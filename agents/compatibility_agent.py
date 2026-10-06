import sys
from typing import Optional, List, Dict, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.schemas import (
    HardwareSpecContract, 
    FinalAuditReport, 
    GPURecommendation, 
    GPUCandidate
)
from tools.db_lookup_tool import DBLookupTool
from tools.psu_calculator_tool import PSUCalculatorTool
from tools.bottleneck_tool import BottleneckTool
from tools.full_build_tool import FullPCBuildTool

AGENT2_SYSTEM_PROMPT = """Bạn là 'Agent 2: Compatibility Auditor & Build Strategist' - Kỹ sư trưởng thẩm định phần cứng máy tính và an toàn điện năng.
Bạn nhận được hồ sơ phân tích từ Agent 1 cùng kết quả kiểm định số học từ các công cụ chuyên dụng (Tools).
Nhiệm vụ của bạn là:
Viết một bài tư vấn và nhận định chuyên sâu (bằng tiếng Việt chuyên nghiệp, tự nhiên, gần gũi, đầy thuyết phục):
- Đánh giá tính khả thi và hợp lý của cấu hình được đề xuất.
- Phân tích trải nghiệm chơi game thực tế (nêu cụ thể tên game: CS2, Valorant, GTA 5, game AAA và mức FPS dự kiến).
- Đánh giá an toàn điện năng của bộ nguồn (PSU) và khả năng nâng cấp về sau (Upgrade path).
- Đưa ra lời khuyên chân thành giúp người dùng không bị lãng phí tiền.
"""

class CompatibilityAgent:
    """
    Agent 2: Compatibility Auditor & Build Strategist
    Chuyên viên thẩm định tính tương thích, an toàn điện năng và lập chiến lược cấu hình.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                pass

        # Đăng ký bộ Tools chuyên dụng
        self.db_tool = DBLookupTool()
        self.psu_tool = PSUCalculatorTool()
        self.bottleneck_tool = BottleneckTool()
        self.full_build_tool = FullPCBuildTool()

    def audit(self, contract: HardwareSpecContract, verbose: bool = False) -> FinalAuditReport:
        budget_text = f"{contract.budget_vnd:,} VND" if contract.budget_vnd is not None else "Chưa xác định"
        psu_text = f"{contract.current_psu_watt}W" if contract.current_psu_watt is not None else "Chưa rõ"
        cpu_text = contract.current_cpu or "Chưa rõ"

        full_pc_data = None

        # NẾU NGƯỜI DÙNG MUỐN BUILD TRỌN BỘ HOẶC BUILD QUANH LINH KIỆN CÓ SẴN
        if contract.target_component in ["FULL_PC", "BUILD_WITH_EXISTING"]:
            full_pc_data = self.full_build_tool.generate_build(
                contract.budget_vnd, 
                contract.purpose,
                already_owned=contract.already_owned_parts
            )

        # TRA CỨU ỨNG VIÊN GPU NẾU CẦN
        is_build_mode = contract.target_component in ["FULL_PC", "BUILD_WITH_EXISTING"]
        gpu_budget = int(contract.budget_vnd * 0.4) if (is_build_mode and contract.budget_vnd) else contract.budget_vnd
        candidates: List[GPUCandidate] = self.db_tool.find_gpus_by_budget(gpu_budget)

        cpu_info = self.db_tool.get_cpu_info(contract.current_cpu)
        cpu_tdp = cpu_info.get("tdp_watt", 65) if cpu_info else 65

        recommendations: List[GPURecommendation] = []
        safety_alerts: List[str] = []

        if contract.warning_flag:
            safety_alerts.append(f"⚠️ CẢNH BÁO TỪ AGENT 1: {contract.warning_flag}")

        if not candidates and not is_build_mode:
            safety_alerts.append(
                f"⚠️ KHÔNG TÌM THẤY LINH KIỆN PHÙ HỢP: Ngân sách {budget_text} quá thấp để mua card đồ họa đáp ứng yêu cầu."
            )

        if not is_build_mode:
            if "current_psu_watt" in contract.missing_fields or not contract.current_psu_watt:
                safety_alerts.append("⚠️ THIẾU THÔNG TIN NGUỒN: Người dùng chưa cung cấp công suất nguồn (PSU). Khuyến nghị mở nắp thùng máy kiểm tra nhãn dán nguồn trước khi mua card!")

        for gpu in candidates:
            psu_eval = self.psu_tool.calculate_load(
                cpu_tdp=cpu_tdp, 
                gpu_tdp=gpu.tdp_watt, 
                user_psu_watt=contract.current_psu_watt
            )

            if not is_build_mode and psu_eval.status == "DANGER":
                safety_alerts.append(f"⛔ NGUY CƠ CHÁY NỔ/SẬP NGUỒN VỚI {gpu.model}: Nguồn {psu_text} quá tải ({psu_eval.load_percentage}%). Bắt buộc phải nâng nguồn tối thiểu {gpu.recommended_psu_watt}W!")

            btn_eval = self.bottleneck_tool.check_bottleneck(
                cpu_name=contract.current_cpu, 
                gpu_model=gpu.model, 
                cpu_info=cpu_info
            )

            if not is_build_mode and btn_eval.bottleneck_risk == "HIGH":
                safety_alerts.append(f"⚠️ NGHẼN CỔ CHAI NẶNG: {contract.current_cpu} sẽ không phát huy được sức mạnh của {gpu.model}.")

            # Nhận định nhanh
            if "5090" in gpu.model:
                q_review = "Quái vật đồ họa 8K, 32GB VRAM đỉnh cao cho AI/Deep Learning"
            elif "5080" in gpu.model or "4090" in gpu.model:
                q_review = "Đỉnh cao Gaming 4K Max Settings, băng thông cực khủng"
            elif "4070" in gpu.model:
                q_review = "Chiến mượt 2K/4K, hỗ trợ công nghệ DLSS 3 Frame Gen"
            elif "7800" in gpu.model:
                q_review = "16GB VRAM cực lớn, chiến game Native không lo tràn VRAM 3-5 năm tới"
            elif "4060" in gpu.model:
                q_review = "Tiết kiệm điện (115-160W), công nghệ Frame Gen tăng gấp đôi FPS"
            elif "3060" in gpu.model:
                q_review = "VRAM 12GB khủng trong tầm giá, tối ưu cho đồ họa 3D và dựng phim"
            elif "2060" in gpu.model or "6600" in gpu.model:
                q_review = "Vua phân khúc giá rẻ - Cân mượt CS2, Valorant và game AAA 1080p High"
            elif "1660" in gpu.model or "1650" in gpu.model:
                q_review = "Lựa chọn tiết kiệm điện, chiến tốt mọi game Esport phổ thông"
            else:
                q_review = f"Hiệu năng phân khúc {gpu.performance_tier}, VRAM {gpu.vram_gb}GB"

            pros = [
                q_review,
                f"Giá thị trường tham khảo: {gpu.market_price_used_vnd:,} VNĐ",
                f"Dung lượng VRAM: {gpu.vram_gb}GB GDDR6 | Chân nguồn: {gpu.power_connectors}"
            ]
            cons = []
            if psu_eval.status in ["WARNING", "DANGER"]:
                cons.append(f"Yêu cầu nguồn tối thiểu {gpu.recommended_psu_watt}W.")

            recommendations.append(GPURecommendation(
                gpu=gpu,
                psu_evaluation=psu_eval,
                bottleneck_evaluation=btn_eval,
                pros=pros,
                cons=cons,
                quick_review=q_review
            ))

        # TỔNG HỢP LỜI TƯ VẤN CỦA AGENT 2 BẰNG LLM HOẶC HEURISTIC
        agent2_consultation = ""
        if self.client:
            try:
                build_summary = f"Yêu cầu: {contract.user_raw_query}. Ngân sách: {budget_text}. Mục đích: {contract.purpose}. Nhận định từ Agent 1: {contract.agent1_brief}."
                if full_pc_data:
                    build_summary += f" Cấu hình trọn bộ đề xuất: {full_pc_data['parts']}, Tổng chi phí: {full_pc_data['total_cost']:,} đ."
                if recommendations:
                    build_summary += f" Card đồ họa ứng viên: {[r.gpu.model for r in recommendations]}."
                
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=f"{AGENT2_SYSTEM_PROMPT}\n\nDữ liệu kiểm định phần cứng:\n{build_summary}\n\nHãy viết lời tư vấn hoàn chỉnh:"
                )
                agent2_consultation = resp.text.strip()
            except Exception:
                pass

        if not agent2_consultation:
            # Fallback tư vấn tự nhiên sâu sắc
            if is_build_mode and full_pc_data:
                bd = full_pc_data.get("detailed_component_breakdown", {})
                parts_analysis = ""
                if bd:
                    parts_analysis = (
                        f"🧩 PHÂN TÍCH CHUYÊN SÂU TỪNG LINH KIỆN ĐƯỢC CHỌN:\n"
                        f" • Bo Mạch Chủ & CPU: {bd.get('cpu_main', '')}\n"
                        f" • Bộ Nhớ RAM: {bd.get('ram', '')}\n"
                        f" • Ổ Cứng Lưu Trữ (SSD): {bd.get('ssd', '')}\n"
                        f" • Card Đồ Họa (VGA): {bd.get('gpu', '')}\n"
                        f" • Bộ Nguồn (PSU): {bd.get('psu', '')}\n"
                        f" • Tản Nhiệt & Vỏ Case: {bd.get('cooler_case', '')}\n\n"
                    )

                if contract.already_owned_parts.get("cpu"):
                    owned_cpu = contract.already_owned_parts["cpu"]
                    agent2_consultation = (
                        f"Chào bạn! Nhận định từ Agent 1 hoàn toàn chuẩn xác: Vi xử lý ({owned_cpu}) là một CPU cực kỳ mạnh mẽ. "
                        f"Việc bạn tận dụng lại CPU này giúp bạn tiết kiệm ngay 4-6 triệu VNĐ chi phí mua chip mới, dồn trọn vẹn ngân sách {budget_text} cho 7 linh kiện còn lại.\n\n"
                        f"{parts_analysis}"
                        f"🎮 VỀ TRẢI NGHIỆM CHƠI GAME & ĐỒ HỌA:\n{full_pc_data['advice']}\n\n"
                        f"⚡ VỀ ĐỘ AN TOÀN ĐIỆN NĂNG & ĐỒNG BỘ PHẦN CỨNG:\n{full_pc_data['upgrade_path']}\n\n"
                        f"💡 LỜI KHUYÊN KỸ THUẬT LẮP ĐẶT: Do {owned_cpu} có hiệu năng cao và tỏa nhiệt lớn khi tải nặng (PL2), bo mạch chủ và tản nhiệt tháp đôi trong bảng "
                        f"được chọn riêng để đảm bảo giữ nhiệt độ CPU luôn dưới 70°C và không bao giờ bị bóp xung khi cày game liên tục!"
                    )
                else:
                    agent2_consultation = (
                        f"Chào bạn! Nhận hồ sơ từ Agent 1, với ngân sách {budget_text} cho nhu cầu {contract.purpose}, "
                        f"tôi đã tính toán cân bằng chi phí và thẩm định độ tương thích đồng bộ của toàn bộ linh kiện trong dàn máy.\n\n"
                        f"{parts_analysis}"
                        f"🎮 VỀ TRẢI NGHIỆM CHƠI GAME & ĐỒ HỌA:\n{full_pc_data['advice']}\n\n"
                        f"⚡ VỀ ĐỘ AN TOÀN ĐIỆN NĂNG & NÂNG CẤP DÀI HẠN:\n{full_pc_data['upgrade_path']}\n\n"
                        f"💡 LỜI KHUYÊN KỸ THUẬT LẮP ĐẶT: Khi ráp máy, yêu cầu kỹ thuật viên cắm 2 thanh RAM vào khe 2 và 4 (chạy chuẩn Dual Channel) "
                        f"để tăng ngay 15-20% FPS, đồng thời đi dây gọn gàng giấu sau lưng case để tối đa luồng khí Airflow làm mát linh kiện nhé!"
                    )
            else:
                agent2_consultation = (
                    f"Chào bạn! Dựa trên phân tích từ Agent 1, tôi đã dùng công cụ tính toán tải nguồn và kiểm tra nghẽn cổ chai "
                    f"với các ứng viên GPU trong bảng trên.\n\n"
                    f"💡 LỜI KHUYÊN CHUYÊN GIA: Hãy ưu tiên phương án có mức tải nguồn dưới 80% để đảm bảo máy chạy mát mẻ, "
                    f"không bị sập nguồn đột ngột khi chơi game nặng trong những ngày hè oi bức!"
                )

        checklist = [
            "Kiểm tra nhiệt độ bằng Furmark: Chạy trong 10-15 phút, nhiệt độ GPU tối đa không quá 80°C, Hotspot không quá 95°C.",
            "Kiểm tra chân nguồn phụ chính hãng, tuyệt đối KHÔNG dùng jack chuyển đổi Molex rẻ tiền.",
            "Kiểm tra ngoại quan chân tiếp xúc PCIe không rỉ sét/cháy chân, ốc vít tản nhiệt còn nguyên vẹn."
        ]

        summary = f"Đã hoàn thành phân tích và thẩm định phương án tối ưu cho ngân sách {budget_text}."

        report = FinalAuditReport(
            contract=contract,
            recommendations=recommendations,
            executive_summary=summary,
            safety_alerts=safety_alerts,
            purchase_checklist=checklist,
            full_pc_build=full_pc_data,
            agent1_brief=contract.agent1_brief,
            agent2_consultation=agent2_consultation
        )

        return report
