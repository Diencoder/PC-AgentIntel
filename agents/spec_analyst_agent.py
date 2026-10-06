import json
import re
import sys
from typing import Optional, Dict

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.schemas import HardwareSpecContract

SYSTEM_PROMPT = """Bạn là 'Agent 1: Spec & Intent Analyst' trong hệ thống Multi-Agent tư vấn phần cứng máy tính.
Nhiệm vụ của bạn là:
1. Lắng nghe yêu cầu tự nhiên của người dùng, phân tích sâu về tâm lý ngân sách, mục đích (Gaming, Đồ họa, hay Văn phòng).
2. Xác định xem người dùng muốn:
   - 'BUILD TRỌN BỘ PC MỚI' (FULL_PC)
   - 'BUILD HOÀN THIỆN DÀN PC QUANH LINH KIỆN CÓ SẴN' (BUILD_WITH_EXISTING) khi người dùng nói 'đã có sẵn chip...', 'có sẵn card...'
   - 'NÂNG CẤP MỘT LINH KIỆN' (GPU).
3. Đóng gói thành JSON chuẩn với các trường:
   - current_cpu, current_psu_watt, budget_vnd, target_component ('FULL_PC', 'BUILD_WITH_EXISTING' hoặc 'GPU'), condition, purpose, missing_fields, warning_flag, already_owned_parts.
   - agent1_brief: Một đoạn văn ngắn (2-3 câu) nhận định sâu sắc của bạn về bài toán này để chuyển giao cho Agent 2 (Kỹ sư trưởng).

ĐỊNH DẠNG TRẢ VỀ: DUY NHẤT một chuỗi JSON hợp lệ, không bọc markdown.
"""

class SpecAnalystAgent:
    """Agent 1: Bóc tách ngôn ngữ tự nhiên, phân tích bối cảnh và tạo hồ sơ chuyển giao."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                pass

    def _normalize_text(self, text: str) -> str:
        t = text.lower()
        t = re.sub(r"\b(?:à|ừm|thì|là|con|cái|kiểu|đấy)\s*\.{2,}\s*", " ", t)
        t = re.sub(r"\b(\w+)\s*\.{2,}\s*\1\b", r"\1", t)

        replacements = [
            (r"\brái\s*den\b", "ryzen"),
            (r"\brai\s*den\b", "ryzen"),
            (r"\brai\s*d[ừửu]n\b", "ryzen"),
            (r"\brysen\b", "ryzen"),
            (r"\bnăm\s+(\d{4})", r"5 \1"),
            (r"\bsáu\s*trăm\s*(?:oát|wát|wat|w|oat)\b", "600w"),
            (r"\bnăm\s*trăm\s*(?:oát|wát|wat|w|oat)\b", "500w"),
            (r"\bbảy\s*trăm\s*(?:oát|wát|wat|w|oat)\b", "700w"),
            (r"\bbốn\s*trăm\s*(?:oát|wát|wat|w|oat)\b", "400w"),
            (r"\bchẹo\b", "triệu"),
            (r"\bmún\s*lơn\b", "muốn lên"),
            (r"\bmún\b", "muốn"),
            (r"\blơn\b", "lên"),
            (r"\bkạt(?:\s*màng\s*hình)?\b", "card"),
            (r"\bmàng\s*hình\b", "màn hình"),
            (r"\bchoi\b", "chơi"),
            (r"\b(i[3579]\s*\d{4,5})\s*ép\b", r"\1f"),
            (r"\b(i\s*([3579]))\b", r"i\2"),
            (r"\b(?:kard|cạc|cac)\b", "card"),
            (r"\b(?:wats|wat|wát)\b", "w"),
            (r"\b(?:redner|ren đồ)\b", "render"),
            (r"\bdag\b", "đang"),
            (r"\bnghen\s*co\s*chai\b", "nghẽn cổ chai"),
        ]
        for pattern, repl in replacements:
            t = re.sub(pattern, repl, t)
        return t

    def analyze(self, query: str) -> HardwareSpecContract:
        if self.client:
            models_to_try = [self.model_name, "gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
            seen = set()
            models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]
            
            prompt = f"{SYSTEM_PROMPT}\n\nYêu cầu của người dùng: '{query}'"
            for m in models_to_try:
                try:
                    resp = self.client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    text = resp.text.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    data = json.loads(text)
                    data["user_raw_query"] = query
                    return HardwareSpecContract(**data)
                except Exception:
                    continue

        return self._fallback_heuristic_parse(query)

    def _fallback_heuristic_parse(self, query: str) -> HardwareSpecContract:
        norm_q = self._normalize_text(query)

        # 1. CPU Detection
        cpu = None
        cpu_patterns = [
            r"((?:core\s+)?ultra\s*[579]\s*[a-z0-9]+)",
            r"(i[3579][ -]?(?:\d{4,5}[a-z]?|\d{3,4}))",
            r"(core 2 quad\s*[a-z0-9]*)",
            r"(core 2 duo\s*[a-z0-9]*)",
            r"((?:ryzen|r)\s*[3579]\s*\d{4,5}[a-z0-9]*)",
            r"(xeon\s*[a-z0-9-]+)",
            r"(celeron\s*[a-z0-9]+)",
            r"(pentium\s*[a-z0-9]+)"
        ]
        for pattern in cpu_patterns:
            match = re.search(pattern, norm_q)
            if match:
                cpu = re.sub(r"\s+", " ", match.group(1).upper()).strip()
                break

        # 2. PSU Detection
        psu = None
        psu_match = re.search(r"(\d{3,4})\s*w(?:att)?", norm_q)
        if psu_match:
            psu = int(psu_match.group(1))

        # 3. Budget Detection
        budget = None
        # Tạm thời loại bỏ các mã CPU có đuôi K/KF (ví dụ 14600k, 13700k...) để không bị nhầm ký tự 'k' thành tiền nghìn đồng
        q_budget = re.sub(r"\b(?:i[3579]|core|ultra|ryzen|r[3579])\s*[-]?\s*\d{4,5}[a-z]*\b", " ", norm_q)
        q_budget = re.sub(r"\b\d{4,5}[kK][fF]?\b", " ", q_budget)

        # Kiểm tra cộng dồn: ví dụ '5 củ, vợ cho thêm 500k'
        sum_match = re.search(r"(\d+)\s*(?:củ|cu|tr|triệu|trieu)\b[\s\S]*?(\d{2,4})\s*k\b", q_budget)
        if sum_match:
            budget = int(sum_match.group(1)) * 1_000_000 + int(sum_match.group(2)) * 1_000

        # Kiểm tra 'triệu rưỡi / củ rưỡi'
        if not budget:
            ruoi_match = re.search(r"(\d+)\s*(?:triệu|trieu|tr|củ|cu)\s*r(?:ưỡ|uo)i\b", q_budget)
            if ruoi_match:
                budget = int(ruoi_match.group(1)) * 1_000_000 + 500_000

        if not budget:
            combo_match = re.search(r"(?<![a-z0-9])(\d+)\s*(?:tr|củ|cu|triệu|trieu)\s*(\d{1,3})\b", q_budget)
            if combo_match:
                digits2 = combo_match.group(2)
                if len(digits2) == 1:
                    budget = int(combo_match.group(1)) * 1_000_000 + int(digits2) * 100_000
                elif len(digits2) == 2:
                    budget = int(combo_match.group(1)) * 1_000_000 + int(digits2) * 10_000
                else:
                    budget = int(combo_match.group(1)) * 1_000_000 + int(combo_match.group(2)) * 1_000

        if not budget:
            xy_match = re.search(r"(?<![a-z0-9])(\d+)\s*(?:tr|củ|cu)\s*(\d)\b", q_budget)
            if xy_match:
                budget = int(xy_match.group(1)) * 1_000_000 + int(xy_match.group(2)) * 100_000

        if not budget:
            budget_match_tr = re.search(r"(?<![a-z0-9])(\d+(?:[.,]\d+)?)\s*(?:triệu|trieu|tr|củ|cu)\b", q_budget)
            budget_match_k = re.search(r"(?<![a-z0-9])(\d{3,5})\s*k\b", q_budget)
            if budget_match_tr:
                val_str = budget_match_tr.group(1).replace(",", ".")
                budget = int(float(val_str) * 1_000_000)
            elif budget_match_k:
                budget = int(budget_match_k.group(1)) * 1_000

        # 4. Tình trạng
        condition = "any"
        if any(w in norm_q for w in ["cũ", "cu", "2nd", "second hand", "used", "lướt", "trâu cày"]):
            condition = "used"
        elif any(w in norm_q for w in ["mới", "moi", "new", "đập hộp", "chính hãng"]):
            condition = "new"

        # 5. Mục đích sử dụng thực tế
        if any(w in norm_q for w in ["đồ họa", "render", "thiết kế", "photoshop", "premiere", "blender", "capcut", "3d", "autocad", "revit", "dựng phim"]):
            purpose = "Đồ họa & Render"
        elif any(w in norm_q for w in ["văn phòng", "office", "kế toán", "lướt web", "xem phim", "học tập", "word", "excel", "học online"]):
            purpose = "Văn phòng & Học tập"
        elif any(w in norm_q for w in ["game", "gaming", "chơi", "fps", "cs2", "valorant", "lol", "fo4", "gta", "wukong", "pubg"]):
            purpose = "Gaming"
        else:
            if budget and budget <= 8_000_000:
                purpose = "Học tập & Văn phòng phổ thông"
            else:
                purpose = "Đa dụng (Học tập, Làm việc & Giải trí)"

        # 6. PHÁT HIỆN LINH KIỆN CÓ SẴN (PRE-OWNED PARTS)
        already_owned_parts: Dict[str, str] = {}
        has_owned_keywords = any(w in norm_q for w in [
            "đã có", "da co", "có sẵn", "co san", "đang có", "dang co", 
            "sẵn có", "san co", "sẵn chip", "san chip", "sẵn cpu", "san cpu", 
            "sẵn vga", "sẵn card", "san card", "tận dụng", "tan dung", "xài lại", "đã mua"
        ])

        if cpu and has_owned_keywords:
            already_owned_parts["cpu"] = cpu

        # Phát hiện VGA có sẵn nếu có
        gpu_patterns = [
            r"((?:rtx|gtx|gt)\s*\d{3,4}(?:\s*ti|\s*super|\s*s)?)",
            r"(rx\s*\d{3,4}(?:\s*xt)?)",
        ]
        for gp in gpu_patterns:
            gm = re.search(gp, norm_q)
            if gm and has_owned_keywords:
                already_owned_parts["gpu"] = gm.group(1).upper()
                break

        # 7. PHÂN ĐỊNH MỤC TIÊU LINH KIỆN (TARGET COMPONENT)
        is_build_request = any(w in norm_q for w in ["build", "ráp", "rap", "mua mới", "trọn bộ", "dàn máy", "case", "thùng"])
        is_gpu_upgrade = any(w in norm_q for w in [
            "nâng card", "nang card", "mua card", "tim card", "tìm card", "thay card", 
            "lên card", "len card", "card cũ", "card mới", "mua vga", "nâng vga", 
            "thay vga", "tìm gpu", "mua gpu", "card rời", "tìm vga", "kiếm card"
        ])

        has_plug_only = any(w in norm_q for w in ["về cắm", "ve cam", "cắm vào", "cam vao", "gắn vào", "gan vao", "cắm card", "lắp card"])
        if already_owned_parts and is_build_request and not is_gpu_upgrade and not has_plug_only:
            target_comp = "BUILD_WITH_EXISTING"
        elif is_gpu_upgrade or has_plug_only or ((cpu is not None or psu is not None) and not is_build_request):
            target_comp = "GPU"
        else:
            target_comp = "FULL_PC"

        missing = []
        if target_comp == "GPU":
            if not cpu:
                missing.append("current_cpu")
            if not psu:
                missing.append("current_psu_watt")
        if not budget:
            missing.append("budget_vnd")

        # 8. KIỂM TRA LỖI XUNG ĐỘT (GUARDRAILS)
        warning = None
        has_intel_cpu = any(w in norm_q for w in ["intel", "i3", "i5", "i7", "i9", "core ultra", "12400", "13400", "14400"])
        has_amd_mb = any(w in norm_q for w in ["b650", "b550", "x670", "am5", "am4", "a520", "a620"])
        has_amd_cpu = any(w in norm_q for w in ["amd", "ryzen", "r5", "r7", "r9", "5600", "7500f", "7800x3d", "9800x3d"])
        has_intel_mb = any(w in norm_q for w in ["h610", "b760", "z790", "lga1700", "lga1200", "b660"])

        if has_intel_cpu and has_amd_mb:
            warning = "LỖI TƯƠNG THÍCH NGHIÊM TRỌNG: CPU Intel (Socket LGA1700) và Bo mạch chủ AMD (Socket AM5/AM4) HOÀN TOÀN KHÁC BIỆT về chân cắm vật lý! Tuyệt đối không thể lắp chung!"
        elif has_amd_cpu and has_intel_mb:
            warning = "LỖI TƯƠNG THÍCH NGHIÊM TRỌNG: CPU AMD Ryzen và Bo mạch chủ Intel (Socket LGA1700) HOÀN TOÀN KHÁC BIỆT về chân cắm vật lý! Tuyệt đối không thể lắp chung!"

        if ("ddr4" in norm_q and "ddr5" in norm_q) and ("main" in norm_q or "bo mach" in norm_q or "khe" in norm_q):
            warning = "LỖI CHUẨN KHE CẮM RAM: RAM DDR4 và khe DDR5 trên bo mạch chủ có vị trí rãnh khuyết (notch) và điện thế (1.2V vs 1.1V) khác nhau! Không thể cắm chung!"

        if any(w in norm_q for w in ["arrow", "vision", "cong suat ao", "công suất ảo"]) or (any(w in norm_q for w in ["nguon co", "nguồn cỏ", "nguon van phong", "nguồn văn phòng"]) and not psu):
            warning = "CẢNH BÁO NGUỒN CÔNG SUẤT ẢO: Nguồn văn phòng noname (như Arrow, Vision...) chỉ có công suất thực khoảng 200-250W, thiếu linh kiện lọc nguồn và mạch bảo vệ. Tuyệt đối không cắm card đồ họa rời công suất cao vì sẽ nổ tụ hoặc cháy lan!"

        if budget and budget < 1_000_000:
            warning = "Ngân sách dưới 1 triệu quá thấp cho phần cứng hiện nay."

        # 9. SINH BRIEF CỦA AGENT 1
        b_str = f"{budget:,} VNĐ" if budget else "chưa xác định"
        
        if target_comp == "BUILD_WITH_EXISTING":
            if "cpu" in already_owned_parts:
                owned_cpu = already_owned_parts["cpu"]
                brief = (
                    f"Người dùng ĐÃ CÓ SẴN vi xử lý ({owned_cpu}) và muốn đầu tư ngân sách {b_str} để hoàn thiện trọn bộ case PC cho mục đích {purpose}. "
                    f"Chiến lược kỹ thuật cốt lõi từ Agent 1: Tận dụng hoàn toàn CPU sẵn có (chi phí 0 VNĐ, tuyệt đối KHÔNG đề xuất mua thêm CPU khác). "
                    f"Dồn 100% ngân sách {b_str} vào 7 linh kiện còn lại, trong đó bắt buộc chọn Bo mạch chủ có chân Socket tương thích 100% với {owned_cpu}, "
                    f"trang bị bộ tản nhiệt đủ công suất giải tỏa nhiệt lượng và dồn tối đa ngân sách để nâng cấp Card đồ họa (VGA) mạnh nhất có thể."
                )
            else:
                owned_gpu = already_owned_parts.get("gpu", "Card rời")
                brief = (
                    f"Người dùng ĐÃ CÓ SẴN card đồ họa ({owned_gpu}) và có ngân sách {b_str} để ráp các linh kiện còn lại cho mục đích {purpose}. "
                    f"Chiến lược đề xuất: Tận dụng card màn hình sẵn có (chi phí 0 VNĐ), dồn toàn bộ {b_str} để trang bị CPU thế hệ mới, RAM và Nguồn chuẩn công suất thực."
                )
        elif target_comp == "FULL_PC":
            if any(w in purpose for w in ["Văn phòng", "Học tập"]):
                brief = (
                    f"Người dùng có ngân sách khoảng {b_str} cho nhu cầu {purpose}. "
                    f"Chiến lược tối ưu từ Agent 1: Ở tầm ngân sách này, giải pháp thông minh và kinh tế nhất là cấu hình Đa dụng phổ thông dùng CPU có nhân đồ họa tích hợp iGPU "
                    f"(tiết kiệm 100% chi phí mua card rời, máy chạy mát và êm). Tập trung ngân sách cho 16GB RAM và SSD NVMe tốc độ cao để lướt web, học tập và làm việc mượt mà."
                )
            elif purpose == "Đồ họa & Render":
                brief = (
                    f"Người dùng có nhu cầu ráp trọn bộ máy tính phục vụ {purpose} với ngân sách khoảng {b_str}. "
                    f"Chiến lược đề xuất: Ưu tiên dung lượng RAM dồi dào (32GB) và card đồ họa có nhiều VRAM/CUDA để tránh tràn bộ nhớ khi dựng hình."
                )
            else:
                brief = (
                    f"Người dùng có nhu cầu ráp trọn bộ case PC mới với ngân sách khoảng {b_str} cho mục đích {purpose}. "
                    f"Chiến lược đề xuất: Cần phân bổ ngân sách hài hòa (khoảng 35-40% cho GPU, 25% cho CPU+Main, phần còn lại cho RAM, SSD, Nguồn chuẩn) "
                    f"để đảm bảo hiệu năng cao nhất, không bị nghẽn cổ chai và sẵn sàng nâng cấp."
                )
        else:
            brief = (
                f"Người dùng đang có sẵn cấu hình (CPU: {cpu or 'Chưa rõ'}, Nguồn: {psu or 'Chưa rõ'}W) "
                f"và muốn tìm mua/nâng cấp card màn hình trong tầm giá {b_str} để phục vụ {purpose}. "
                f"Cần thẩm định kỹ công suất nguồn điện và đo lường nghẽn cổ chai trước khi khuyến nghị."
            )

        return HardwareSpecContract(
            user_raw_query=query,
            current_cpu=cpu,
            current_psu_watt=psu,
            budget_vnd=budget,
            target_component=target_comp,
            condition=condition,
            purpose=purpose,
            missing_fields=missing,
            warning_flag=warning,
            already_owned_parts=already_owned_parts,
            agent1_brief=brief
        )
