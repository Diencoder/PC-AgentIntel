import sys
from typing import Optional, Dict, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.schemas import HardwareSpecContract, FinalAuditReport
from agents.spec_analyst_agent import SpecAnalystAgent
from agents.compatibility_agent import CompatibilityAgent

console = Console()

class PCAgentOrchestrator:
    """
    Bộ điều phối hệ thống Multi-Agent PC-AgentIntel.
    Thể hiện rõ rệt sự phối hợp giữa Agent 1 (Spec Analyst) và Agent 2 (Build Strategist & Compatibility Auditor).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.agent1 = SpecAnalystAgent(api_key=api_key)
        self.agent2 = CompatibilityAgent(api_key=api_key)

    def run(self, user_query: str, show_steps: bool = False) -> Optional[FinalAuditReport]:
        # BƯỚC 1: AGENT 1 BÓC TÁCH & PHÂN TÍCH BỐI CẢNH
        contract: HardwareSpecContract = self.agent1.analyze(user_query)

        # Kiểm tra nếu phát hiện lỗi xung đột tương thích phần cứng trực tiếp
        if contract.warning_flag and any(w in contract.warning_flag for w in ["LỖI TƯƠNG THÍCH", "LỖI CHUẨN", "CẢNH BÁO NGUỒN CÔNG SUẤT ẢO"]):
            if "LỖI CHUẨN KHE CẮM RAM" in contract.warning_flag:
                sol = " • Giải pháp 1: Mua RAM chuẩn DDR5 để tương thích với bo mạch chủ mới.\n • Giải pháp 2: Hoặc đổi bo mạch chủ sang phiên bản hỗ trợ DDR4 (Ví dụ: B760M-K DDR4) để tận dụng lại 2 thanh RAM cũ."
            elif "LỖI TƯƠNG THÍCH NGHIÊM TRỌNG" in contract.warning_flag:
                sol = " • Đối với CPU Intel (LGA1700): Bắt buộc phải đi cùng Bo mạch chủ Intel (H610, B760, Z790).\n • Đối với Bo mạch chủ AMD (AM5/AM4): Bắt buộc phải gắn CPU AMD Ryzen (Ryzen 5 7500F, Ryzen 7 7800X3D...)."
            else:
                sol = " • Khuyến nghị: Thay thế ngay bằng bộ nguồn công suất thực có chứng chỉ 80 Plus (MSI MAG A650BN, Corsair, Deepcool...) trước khi lắp card đồ họa rời."

            warn_panel = f"[bold red]⛔ {contract.warning_flag}[/bold red]\n\n[bold yellow]💡 GIẢI PHÁP TỪ KỸ SƯ TRƯỞNG:[/bold yellow]\n{sol}"
            console.print(Panel(warn_panel, title="[bold red]PHÁT HIỆN XUNG ĐỘT LINH KIỆN & CẢNH BÁO AN TOÀN[/bold red]", border_style="red"))
            return None

        # Kiểm tra nếu câu hỏi hoàn toàn thiếu thông tin
        is_empty = (not contract.current_cpu and not contract.current_psu_watt and not contract.budget_vnd)
        if is_empty:
            msg = (
                f"[bold yellow]Chào bạn! Yêu cầu của bạn còn thiếu thông tin để tư vấn.[/bold yellow]\n\n"
                f"Vui lòng bổ sung thêm:\n"
                f" • 💰 [cyan]Ngân sách[/cyan] (Ví dụ: [green]'5 triệu'[/green], [green]'15 triệu'[/green]...)\n"
                f" • ⚡ [cyan]Nguồn hoặc CPU sẵn có[/cyan] (Ví dụ: [green]'nguồn 550W'[/green], [green]'chip i5 12400f'[/green]...)\n"
                f" • 🎯 [cyan]Mục đích[/cyan] (Ví dụ: [green]'chơi game CS2'[/green], [green]'làm đồ họa'[/green]...)"
            )
            console.print(Panel(msg, title="[bold yellow]CẦN THÊM THÔNG TIN[/bold yellow]", border_style="yellow"))
            return None

        # BƯỚC 2: CHUYỂN GIAO CHO AGENT 2 THẨM ĐỊNH & VIẾT BÁO CÁO TƯ VẤN
        report: FinalAuditReport = self.agent2.audit(contract, verbose=False)

        budget_disp = f"{contract.budget_vnd:,} đ" if contract.budget_vnd else "Chưa xác định"

        # HIỂN THỊ PHẦN 1: NHẬN ĐỊNH BÀN GIAO TỪ AGENT 1
        a1_panel = (
            f"[bold cyan]🎯 Nhu cầu nhận diện:[/bold cyan] {contract.purpose} ({'Build trọn bộ PC mới' if contract.target_component == 'FULL_PC' else 'Nâng cấp card đồ họa'})\n"
            f"[bold cyan]💰 Ngân sách:[/bold cyan] {budget_disp}\n"
            f"[bold yellow]📝 Nhận định chiến lược của Agent 1:[/bold yellow]\n{report.agent1_brief}"
        )
        console.print(Panel(a1_panel, title="[bold cyan]🤖 [AGENT 1 - SPEC ANALYST]: PHÂN TÍCH NHU CẦU & BÀN GIAO[/bold cyan]", border_style="cyan"))

        # HIỂN THỊ PHẦN 2: BẢNG KỸ THUẬT & TƯ VẤN TỪ AGENT 2
        if contract.target_component in ["FULL_PC", "BUILD_WITH_EXISTING"] and report.full_pc_build:
            build = report.full_pc_build
            parts = build["parts"]
            
            # 1. BẢNG CHI TIẾT 8 LINH KIỆN
            table = Table(
                title=f"💻 CẤU HÌNH TRỌN BỘ PC ĐỀ XUẤT (Ngân sách: {budget_disp} | Nhu cầu: {contract.purpose})",
                border_style="green", 
                header_style="bold green"
            )
            table.add_column("Linh Kiện", style="bold yellow", width=20)
            table.add_column("Tên Linh Kiện Chi Tiết", style="bold white", width=42)
            table.add_column("Thông Số Kỹ Thuật", style="cyan", width=34)
            table.add_column("Giá Tham Khảo", justify="right", width=16)

            for p in parts:
                spec_str = p.get("spec", "Chuẩn đồng bộ hệ thống")
                table.add_row(p["category"], p["item"], spec_str, f"{p['price']:,} đ")

            table.add_section()
            table.add_row(
                "[bold green]TỔNG CHI PHÍ DỰ KIẾN[/bold green]", 
                "[bold green]Trọn bộ đầy đủ 8 linh kiện (Cắm điện là dùng)[/bold green]", 
                "[bold green]Đồng bộ 100%[/bold green]",
                f"[bold green]{build['total_cost']:,} đ[/bold green]"
            )
            console.print(table)

            # 2. BẢNG KIỂM ĐỊNH TƯƠNG THÍCH ĐỒNG BỘ TOÀN BỘ HỆ THỐNG
            comp_checks = build.get("compatibility_checks", [])
            if comp_checks:
                comp_table = Table(
                    title="🛡️ BẢNG KIỂM ĐỊNH TƯƠNG THÍCH ĐỒNG BỘ TOÀN BỘ LINH KIỆN (AGENT 2 AUDIT)",
                    border_style="blue",
                    header_style="bold blue"
                )
                comp_table.add_column("Hạng Mục Kiểm Định", style="bold white", width=32)
                comp_table.add_column("Trạng Thái", justify="center", width=20)
                comp_table.add_column("Chi Tiết Đánh Giá Kỹ Thuật", width=58)

                for c in comp_checks:
                    st = c["status"]
                    st_colored = f"[bold green]✔ {st}[/bold green]" if "HOÀN HẢO" in st or "AN TOÀN" in st or "VỪA VẶN" in st else f"[bold yellow]⚠️ {st}[/bold yellow]"
                    comp_table.add_row(c["aspect"], st_colored, c["detail"])

                console.print(comp_table)

        else:
            table = Table(
                title=f"🎮 BẢNG SO SÁNH CARD ĐỒ HỌA TỐI ƯU (Ngân sách: {budget_disp} | Nhu cầu: {contract.purpose})", 
                border_style="green", 
                header_style="bold green"
            )
            table.add_column("Card Đồ Họa (GPU)", style="bold white", width=28)
            table.add_column("Giá Tham Khảo", justify="right", width=16)
            table.add_column("Tải Nguồn (PSU)", width=16)
            table.add_column("Nghẽn Cổ Chai", width=14)
            table.add_column("Đánh Giá Nhanh", width=38)

            for rec in report.recommendations:
                psu_color = "green" if rec.psu_evaluation.status == "SAFE" else ("yellow" if rec.psu_evaluation.status == "WARNING" else "red")
                btn_color = "green" if rec.bottleneck_evaluation.bottleneck_risk == "LOW" else ("yellow" if rec.bottleneck_evaluation.bottleneck_risk == "MODERATE" else "red")
                
                table.add_row(
                    rec.gpu.model,
                    f"{rec.gpu.market_price_used_vnd:,} đ",
                    f"[{psu_color}]{rec.psu_evaluation.status} ({rec.psu_evaluation.load_percentage}%)[/{psu_color}]",
                    f"[{btn_color}]{rec.bottleneck_evaluation.bottleneck_risk}[/{btn_color}]",
                    rec.quick_review
                )
            console.print(table)

        # HIỂN THỊ PHẦN 3: BÀI TƯ VẤN & LỜI KHUYÊN CHUYÊN GIA TỪ AGENT 2
        console.print(Panel(report.agent2_consultation, title="[bold green]⚡ [AGENT 2 - KỸ SƯ TRƯỞNG]: BÀI TƯ VẤN & ĐÁNH GIÁ CHUYÊN SÂU[/bold green]", border_style="green"))

        if report.safety_alerts:
            alert_text = "\n".join([f"• {a}" for a in report.safety_alerts])
            console.print(Panel(alert_text, title="[bold red]LƯU Ý AN TOÀN KỸ THUẬT QUAN TRỌNG[/bold red]", border_style="red"))

        return report

if __name__ == "__main__":
    orchestrator = PCAgentOrchestrator()
    orchestrator.run("tôi muốn build pc ngân sách 15 triệu chơi game")
