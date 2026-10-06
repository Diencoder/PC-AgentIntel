import json
from typing import List, Optional, Dict, Any
from core.config import HARDWARE_DB_PATH
from core.schemas import GPUCandidate

class DBLookupTool:
    """Tool tra cứu và truy vấn thông số phần cứng từ cơ sở dữ liệu."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or HARDWARE_DB_PATH
        self._load_db()

    def _load_db(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"[Error] Không thể tải database phần cứng: {e}")
            self.data = {"gpus": [], "cpus": []}

    def find_gpus_by_budget(self, budget_vnd: Optional[int], tolerance_pct: float = 0.15) -> List[GPUCandidate]:
        """
        Lọc danh sách GPU phù hợp với ngân sách người dùng.
        Cho phép vượt nhẹ ngân sách (tolerance_pct = 15%) để đề xuất phương án cố thêm tí được card vượt trội.
        """
        all_gpus = self.data.get("gpus", [])
        if not budget_vnd:
            # Nếu người dùng không nhập ngân sách, trả về top 3 card phổ biến nhất
            candidates = all_gpus[:3]
        else:
            max_allowed = budget_vnd * (1 + tolerance_pct)
            candidates = [
                gpu for gpu in all_gpus 
                if gpu.get("market_price_used_vnd", 0) <= max_allowed
            ]

        # Sắp xếp theo giá giảm dần (tiệm cận ngân sách nhất sẽ cho hiệu năng cao nhất)
        candidates.sort(key=lambda x: x.get("market_price_used_vnd", 0), reverse=True)

        return [GPUCandidate(**item) for item in candidates[:3]]

    def get_cpu_info(self, cpu_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Tra cứu thông số chi tiết CPU (TDP, thế hệ)."""
        if not cpu_name:
            return None
        
        cpu_name_clean = cpu_name.lower().replace("-", " ").replace("intel", "").replace("core", "").strip()
        cpus = self.data.get("cpus", [])
        
        for cpu in cpus:
            model_clean = cpu.get("model", "").lower().replace("-", " ").replace("intel", "").replace("core", "").strip()
            if cpu_name_clean in model_clean or model_clean in cpu_name_clean:
                return cpu

        # Nếu không tìm thấy chính xác trong DB, trả về ước lượng mặc định an toàn cho chip phổ thông
                # Khong tim thay trong DB -> Uoc tinh dong thong minh theo dong chip (Dynamic Spec Inference)
        cpu_lower = cpu_name.lower()
        if any(w in cpu_lower for w in ["i9", "r9", "ryzen 9", "ultra 9", "threadripper", "xeon"]):
            tdp = 150
            peak = 260
            tier = "High-End / Workstation (Uoc tinh)"
        elif any(w in cpu_lower for w in ["i7", "r7", "ryzen 7", "ultra 7", "13600k", "14600k"]):
            tdp = 125
            peak = 200
            tier = "Upper Mid-Range (Uoc tinh)"
        elif any(w in cpu_lower for w in ["i3", "r3", "ryzen 3", "pentium", "celeron", "athlon"]):
            tdp = 55
            peak = 75
            tier = "Entry Level (Uoc tinh)"
        else:
            tdp = 65
            peak = 130
            tier = "Mainstream Modern (Uoc tinh)"

        return {
            "model": f"{cpu_name} [Thong so uoc tinh]",
            "tdp_watt": tdp,
            "peak_power_watt": peak,
            "generation_tier": tier
        }
