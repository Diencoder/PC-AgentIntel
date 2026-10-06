import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from orchestrator import PCAgentOrchestrator

def run_complex_tests():
    orchestrator = PCAgentOrchestrator()
    print("="*80)
    print(" BẮT ĐẦU CHẠY BỘ KIỂM THỬ PHỨC TẠP (5 ADVANCED & EDGE TEST CASES)")
    print("="*80 + "\n")

    complex_cases = [
        {
            "id": "COMPLEX-01",
            "name": "AMD Ryzen 5 5600 + Nhu cầu Blender 3D & VRAM lớn",
            "query": "Em dùng chip AMD Ryzen 5 5600, nguồn Corsair 550W Bronze, ngân sách khoảng 6tr5 muốn tìm card làm đồ họa 3D Blender và thỉnh thoảng chơi game 2K, ưu tiên card nhiều VRAM",
            "expect_cpu": "RYZEN",
            "expect_psu": 550,
            "min_budget": 6_000_000,
            "check": lambda report: any(r.gpu.vram_gb >= 12 for r in report.recommendations)
        },
        {
            "id": "COMPLEX-02",
            "name": "RỦI RO KÉP (Double Hazard): Chip cổ đại Core 2 Quad + Nguồn noname 400W đòi mua RTX 3080",
            "query": "Mình đang xài Core 2 Quad Q9650 với nguồn noname 400W, vừa trúng số có 10 triệu muốn mua luôn RTX 3080 để sau này nâng máy dần",
            "expect_cpu": "CORE 2 QUAD",
            "expect_psu": 400,
            "min_budget": 9_000_000,
            "check": lambda report: (
                any("QUÁ TẢI" in a.upper() or "CHÁY NỔ" in a.upper() for a in report.safety_alerts) and
                any("NGHẼN" in a.upper() for a in report.safety_alerts)
            )
        },
        {
            "id": "COMPLEX-03",
            "name": "Tiếng lóng phức tạp: '4 củ rưỡi', 'vga trâu cày', 'hàng 2nd', 'gta 5 roleplay'",
            "query": "e có con i5 12400f nguồn 600w, ví còn tầm 4 củ rưỡi đến 5 củ 2, tính lụm con vga trâu cày hoặc hàng 2nd về cày gta 5 roleplay mượt mượt tí",
            "expect_cpu": "I5 12400F",
            "expect_psu": 600,
            "min_budget": 4_500_000,
            "check": lambda report: report.contract.condition == "used" and len(report.recommendations) > 0
        },
        {
            "id": "COMPLEX-04",
            "name": "Chạm ngưỡng tải cảnh báo nguy cơ (Borderline 95% WARNING)",
            "query": "Máy đang chạy chip i5 10400F nguồn 500W xịn, ngân sách 5 triệu định lấy RTX 2070 Super",
            "expect_cpu": "I5 10400F",
            "expect_psu": 500,
            "min_budget": 4_900_000,
            "check": lambda report: any(r.psu_evaluation.status in ["WARNING", "DANGER"] for r in report.recommendations)
        },
        {
            "id": "COMPLEX-05",
            "name": "Ngân sách khủng (9 triệu) nhưng giấu thông số nguồn",
            "query": "Mình có chip i5 14400F nhưng không rõ nguồn bao nhiêu watt, ngân sách 9 triệu muốn mua card mạnh nhất có thể",
            "expect_cpu": "I5 14400F",
            "expect_psu": None,
            "min_budget": 9_000_000,
            "check": lambda report: (
                "current_psu_watt" in report.contract.missing_fields and
                any("THIẾU THÔNG TIN NGUỒN" in a for a in report.safety_alerts)
            )
        }
    ]

    all_passed = True
    for case in complex_cases:
        print(f"\n▶ [{case['id']}] {case['name']}")
        print(f"  Câu hỏi: \"{case['query']}\"")
        
        report = orchestrator.run(case["query"], show_steps=False)

        # Kiểm tra tính hợp lệ
        passed = True
        notes = []

        if case["expect_cpu"] and (not report.contract.current_cpu or case["expect_cpu"] not in report.contract.current_cpu):
            passed = False
            notes.append(f"Sai CPU: mong đợi {case['expect_cpu']}, thực tế {report.contract.current_cpu}")

        if case["expect_psu"] and report.contract.current_psu_watt != case["expect_psu"]:
            passed = False
            notes.append(f"Sai PSU: mong đợi {case['expect_psu']}, thực tế {report.contract.current_psu_watt}")

        if case["min_budget"] and (not report.contract.budget_vnd or report.contract.budget_vnd < case["min_budget"]):
            passed = False
            notes.append(f"Sai Ngân sách: mong đợi >= {case['min_budget']:,}đ, thực tế {report.contract.budget_vnd}")

        if not case["check"](report):
            passed = False
            notes.append("Không thỏa mãn điều kiện logic nghiệp vụ đặc thù (Check function failed)")

        if passed:
            print(f"  ==> KẾT QUẢ: [SUCCESS] Đạt chuẩn 100%!")
            print(f"      - CPU nhận diện: {report.contract.current_cpu}")
            print(f"      - Nguồn: {report.contract.current_psu_watt}W | Ngân sách: {report.contract.budget_vnd:,}đ")
            print(f"      - Số lượng card đề xuất: {len(report.recommendations)}")
            if report.safety_alerts:
                print(f"      - Cảnh báo an toàn đã kích hoạt ({len(report.safety_alerts)} mục):")
                for a in report.safety_alerts:
                    print(f"        * {a}")
        else:
            all_passed = False
            print(f"  ==> KẾT QUẢ: [FAILED] Lỗi: {'; '.join(notes)}")

    print("\n" + "="*80)
    if all_passed:
        print(" TỔNG KẾT: TẤT CẢ 5/5 TEST CASES PHỨC TẠP ĐÃ VƯỢT QUA XUẤT SẮC!")
    else:
        print(" TỔNG KẾT: CÓ TEST CASE CHƯA ĐẠT, CẦN ĐIỀU CHỈNH!")
    print("="*80 + "\n")
    return all_passed

if __name__ == "__main__":
    success = run_complex_tests()
    sys.exit(0 if success else 1)
