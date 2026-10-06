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

def run_noisy_tests():
    orchestrator = PCAgentOrchestrator()
    print("="*90)
    print(" BẮT ĐẦU CHẠY BỘ STRESS-TEST NÂNG CAO: DỮ LIỆU MƠ HỒ, SAI CHÍNH TẢ, PHẦN CỨNG ẢO, NGUY HIỂM")
    print("="*90 + "\n")

    noisy_cases = [
        {
            "id": "NOISE-01",
            "category": "Lắp bắp, ngập ngừng, lặp từ, sửa lời",
            "query": "À... à ừm... thì... thì là mình... mình có con... con chip ii5... i 5 12400 ép... ép... à nhầm f... nguồn hình như là... là tầm 550 wát... w gì đấy... ví có... có độ tầm 4 triệu rưỡi... kiếm con cạc... cạc màn hình...",
            "expect_cpu": "12400",
            "expect_psu": 550,
            "expect_budget": 4_500_000,
            "validate": lambda r: r and r.contract.current_psu_watt == 550 and r.contract.budget_vnd == 4_500_000
        },
        {
            "id": "NOISE-02",
            "category": "Sai chính tả nặng, Teencode, viết tắt cẩu thả",
            "query": "tui dag sài con chíp rái den 5 5600 nguon 600wats, mun tim kard đồ hoa tầm 5tr5 để redner video capcut vs photoshop, co bi nghen co chai k shop",
            "expect_cpu": "RYZEN",
            "expect_psu": 600,
            "expect_budget": 5_500_000,
            "validate": lambda r: r and "RYZEN" in (r.contract.current_cpu or "") and r.contract.purpose == "Đồ họa & Render"
        },
        {
            "id": "NOISE-03",
            "category": "Nói lan man, kể chuyện đời tư (mèo làm đổ nước, thưởng công ty, vợ cho tiền)",
            "query": "Chào bạn, chả là hôm qua con mèo nhà mình nó nhảy làm đổ ly nước vào cái case cũ hỏng mất con card RX 580 rồi. May mà con chip i5-10400F với cục nguồn Cooler Master 650W không sao hết. Dạo này đi làm công ty mới thưởng cho 5 củ, vợ cho thêm 500k nữa, tính mua con card cũ nào về tối tối rảnh bắn CS2 với anh em cơ quan giải tỏa stress, chứ dạo này sếp dí deadline dữ quá...",
            "expect_cpu": "10400F",
            "expect_psu": 650,
            "expect_budget": 5_500_000,
            "validate": lambda r: r and "10400" in (r.contract.current_cpu or "") and r.contract.budget_vnd == 5_500_000 and r.contract.condition == "used"
        },
        {
            "id": "NOISE-04",
            "category": "Nói cụt ngủn, mơ hồ, thiếu 100% dữ kiện phần cứng",
            "query": "tôi muốn mua máy tính",
            "expect_cpu": None,
            "expect_psu": None,
            "expect_budget": None,
            "validate": lambda r: r is None  # Hệ thống kích hoạt cơ chế yêu cầu bổ sung thông tin
        },
        {
            "id": "NOISE-05",
            "category": "Đảo lộn thuật ngữ (gọi RTX 3060 là nguồn, i5 14400F là card)",
            "query": "em cần nâng cấp nguồn RTX 3060 với card i5 14400F ngân sách 5 triệu để chơi game",
            "expect_cpu": "14400F",
            "expect_psu": None,
            "expect_budget": 5_000_000,
            "validate": lambda r: r and "14400" in (r.contract.current_cpu or "") and r.contract.budget_vnd == 5_000_000
        },
        {
            "id": "NOISE-06",
            "category": "Sai chính tả phiên âm tiếng Việt cực dị (rai dừn, sáu trăm oát, 8 chẹo, kạt màng hình)",
            "query": "dag xài con chíp rai dừn năm 5600x nguồn sáu trăm oát, có 8 chẹo mún lơn kạt màng hình choi game",
            "expect_cpu": "5600X",
            "expect_psu": 600,
            "expect_budget": 8_000_000,
            "validate": lambda r: r and "5600" in (r.contract.current_cpu or "") and r.contract.current_psu_watt == 600 and r.contract.budget_vnd == 8_000_000
        },
        {
            "id": "NOISE-07",
            "category": "Đưa thông tin phần cứng ảo tưởng / Chip lạ không tồn tại trong DB",
            "query": "đang có chip r7 9999x3d nguồn 650w có 12 triệu muốn cắm rtx 4070 ti",
            "expect_cpu": "R7 9999X3D",
            "expect_psu": 650,
            "expect_budget": 12_000_000,
            "validate": lambda r: r and "9999" in (r.contract.current_cpu or "") and r.contract.current_psu_watt == 650
        },
        {
            "id": "NOISE-08",
            "category": "Ngân sách phi lý / Quá thấp so với yêu cầu (500k đòi 4K Max Settings)",
            "query": "em có 500k muốn build pc chơi mượt black myth wukong 4k max setting",
            "expect_cpu": None,
            "expect_psu": None,
            "expect_budget": 500_000,
            "validate": lambda r: r and r.contract.warning_flag is not None and "quá thấp" in r.contract.warning_flag
        },
        {
            "id": "NOISE-09",
            "category": "Linh kiện chéo ngoe / Quá tải cực đoan (Celeron G5905 + Nguồn 250W đòi cắm RTX 5090)",
            "query": "đang có chip celeron g5905 với nguồn cỏ 250w, có 65 triệu tính mua con rtx 5090 về cắm",
            "expect_cpu": "CELERON",
            "expect_psu": 250,
            "expect_budget": 65_000_000,
            "validate": lambda r: r and any("NGUY CƠ CHÁY NỔ" in a for a in r.safety_alerts) and any("NGHẼN CỔ CHAI" in a for a in r.safety_alerts)
        }
    ]

    all_passed = True

    for case in noisy_cases:
        print(f"\n{'='*75}")
        print(f"👉 [{case['id']}] HẠNG MỤC: {case['category']}")
        print(f"🗣️ Đầu vào thực tế: \"{case['query']}\"")
        print(f"{'='*75}")

        report = orchestrator.run(case["query"], show_steps=False)

        # Kiểm tra tính đúng đắn qua hàm validate
        is_ok = case["validate"](report)
        status_text = "✅ ĐẠT (PASS)" if is_ok else "❌ THẤT BẠI (FAIL)"
        if not is_ok:
            all_passed = False

        print(f"\n📌 KẾT QUẢ ĐÁNH GIÁ TỰ ĐỘNG: {status_text}")
        if report and report.contract:
            c = report.contract
            print(f"   • CPU trích xuất: {c.current_cpu} (Kỳ vọng: {case['expect_cpu']})")
            print(f"   • Nguồn (PSU):    {c.current_psu_watt}W (Kỳ vọng: {case['expect_psu']})")
            print(f"   • Ngân sách:      {c.budget_vnd:,} đ (Kỳ vọng: {case['expect_budget']:,} đ)" if c.budget_vnd else f"   • Ngân sách: None")
            print(f"   • Mục đích:       {c.purpose}")
            print(f"   • Cảnh báo:       {c.warning_flag}")

    print("\n" + "="*85)
    if all_passed:
        print("🏆 KẾT LUẬN: TẤT CẢ 9/9 TESTCASE NHIỄU & CỰC ĐOAN ĐỀU ĐẠT CHUẨN XUẤT SẮC!")
    else:
        print("⚠️ CÓ TESTCASE CHƯA ĐẠT CHUẨN.")
    print("="*85)

if __name__ == "__main__":
    run_noisy_tests()
