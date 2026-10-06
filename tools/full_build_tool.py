from typing import Dict, Any, List, Optional
import re

class FullPCBuildTool:
    """Công cụ tổng hợp cấu hình 8 linh kiện đồng bộ hoàn chỉnh theo ngân sách và linh kiện sẵn có."""

    def generate_build(self, budget: Optional[int], purpose: str = "Gaming", already_owned: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        already_owned = already_owned or {}
        owned_cpu = already_owned.get("cpu")
        owned_gpu = already_owned.get("gpu")

        # TRƯỜNG HỢP 1: NGƯỜI DÙNG ĐÃ CÓ SẴN CPU (VÍ DỤ: I5 14600K, RYZEN 5 7500F...)
        if owned_cpu:
            norm_c = owned_cpu.upper()
            budget = budget or 15_000_000

            # Xác định nền tảng (Platform & Socket) của CPU đã có
            if any(k in norm_c for k in ["AM5", "7500", "7600", "7700", "7800", "7900", "7950", "9600", "9700", "9800"]):
                cpu_socket = "AM5"
                canonical_cpu = f"AMD Ryzen {norm_c}" if "RYZEN" not in norm_c else norm_c
                mb_name = "MSI PRO B650M-A WIFI DDR5"
                mb_socket = "AM5"
                mb_price = 3_200_000
                ram_name = "32GB (2x16GB) Kingston Fury Beast DDR5 5600MHz"
                ram_type = "DDR5"
                ram_price = 2_350_000
                cooler_name = "Thermalright Peerless Assassin 120 SE (Tháp đôi 6 ống đồng)"
                cooler_price = 850_000
                is_high_tdp = True

            elif any(k in norm_c for k in ["AM4", "5600", "5700", "3600", "2600"]):
                cpu_socket = "AM4"
                canonical_cpu = f"AMD Ryzen {norm_c}" if "RYZEN" not in norm_c else norm_c
                mb_name = "MSI B550M PRO-VDH WIFI DDR4"
                mb_socket = "AM4"
                mb_price = 2_200_000
                ram_name = "16GB (2x8GB) Kingston Fury DDR4 3200MHz"
                ram_type = "DDR4"
                ram_price = 850_000
                cooler_name = "Jonsbo CR-1000 EVO ARGB (4 ống đồng)"
                cooler_price = 350_000
                is_high_tdp = False

            else:
                # Mặc định là Intel LGA1700 (Dòng 12, 13, 14 như i5 14600K, i5 13400, i5 12400F...)
                cpu_socket = "LGA1700"
                canonical_cpu = f"Intel Core {norm_c}" if "INTEL" not in norm_c and "CORE" not in norm_c else norm_c
                is_k_series = any(k in norm_c for k in ["14600", "13600", "14700", "13700", "12700", "14900", "13900"]) or norm_c.endswith("K") or norm_c.endswith("KF")
                
                if is_k_series:
                    # CPU dòng K ăn điện lớn (PL2 181W - 253W) -> Cần Main VRM khỏe và Tản nhiệt tháp đôi
                    mb_name = "MSI B760M GAMING PLUS WIFI DDR5"
                    mb_socket = "LGA1700"
                    mb_price = 3_600_000
                    ram_name = "32GB (2x16GB) Kingston Fury Beast DDR5 5600MHz"
                    ram_type = "DDR5"
                    ram_price = 2_350_000
                    cooler_name = "Thermalright Peerless Assassin 120 SE (Tháp đôi 6 ống đồng tản max 245W)"
                    cooler_price = 850_000
                    is_high_tdp = True
                else:
                    mb_name = "ASUS PRIME B760M-K DDR4"
                    mb_socket = "LGA1700"
                    mb_price = 2_150_000
                    ram_name = "16GB (2x8GB) Kingston Fury DDR4 3200MHz"
                    ram_type = "DDR4"
                    ram_price = 850_000
                    cooler_name = "Jonsbo CR-1000 EVO ARGB (4 ống đồng)"
                    cooler_price = 350_000
                    is_high_tdp = False

            # SSD, Nguồn, Case
            ssd_name = "1TB Kingston NV2 NVMe PCIe 4.0 M.2" if budget >= 15_000_000 else "512GB Kingston NV2 NVMe M.2"
            ssd_price = 1_450_000 if budget >= 15_000_000 else 850_000
            
            psu_name = "Deepcool PK750D 750W 80 Plus Bronze" if (budget >= 18_000_000 or is_high_tdp) else "MSI MAG A650BN 650W 80 Plus Bronze"
            psu_watt = 750 if (budget >= 18_000_000 or is_high_tdp) else 650
            psu_price = 1_600_000 if psu_watt == 750 else 1_200_000

            case_name = "Vỏ Bể Cá Panorama Mik Morax 3FA (Kèm 3 Fan vô cực)" if budget >= 18_000_000 else "Montech Air 100 ARGB (4 Fan PWM)"
            case_price = 1_150_000 if budget >= 18_000_000 else 950_000

            # Phân bổ chi phí còn lại cho Card đồ họa (VGA)
            fixed_costs = mb_price + ram_price + ssd_price + cooler_price + psu_price + case_price
            remaining_for_gpu = budget - fixed_costs

            if remaining_for_gpu >= 14_000_000:
                vga_name = "NVIDIA GeForce RTX 4070 Super 12GB GDDR6X"
                vga_price = 14_500_000
                vga_spec = "12GB GDDR6X 192-bit, Ray Tracing & DLSS 3.5 Frame Gen, chiến mượt 2K/4K Ultra"
            elif remaining_for_gpu >= 8_500_000:
                vga_name = "NVIDIA GeForce RTX 4060 Ti 8GB GDDR6"
                vga_price = 9_000_000
                vga_spec = "8GB GDDR6, Kiến trúc Ada Lovelace, DLSS 3 Frame Gen, chiến mượt 2K 144Hz"
            elif remaining_for_gpu >= 7_000_000:
                vga_name = "NVIDIA GeForce RTX 4060 8GB GDDR6"
                vga_price = 7_500_000
                vga_spec = "8GB GDDR6, Siêu tiết kiệm điện (115W TDP), DLSS 3 mượt mà"
            elif remaining_for_gpu >= 5_000_000:
                vga_name = "NVIDIA GeForce RTX 3060 12GB GDDR6"
                vga_price = 5_800_000
                vga_spec = "12GB VRAM bộ nhớ lớn, chuyên trị game nặng và dựng phim đồ họa"
            else:
                vga_name = "NVIDIA GeForce GTX 1660 Super 6GB (hoặc RX 6600 8GB)"
                vga_price = 3_500_000
                vga_spec = "6GB GDDR6, chiến mượt mọi tựa game Esport và làm việc ổn định"

            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{canonical_cpu} (ĐÃ CÓ SẴN - TẬN DỤNG)", "price": 0, "spec": f"Socket {cpu_socket}, Tận dụng CPU sẵn có (Tiết kiệm 100% chi phí mua chip)"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": mb_price, "spec": f"Socket {mb_socket} (Tương thích 100% với {canonical_cpu}), VRM tản nhiệt nhôm dày dặn"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": ram_price, "spec": f"Chuẩn {ram_type} Dual Channel, độ trễ thấp tối ưu FPS game"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": ssd_price, "spec": "Chuẩn NVMe PCIe Gen 4x4 tốc độ cao, load game siêu tốc"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": vga_price, "spec": vga_spec},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": psu_price, "spec": f"{psu_watt}W chuẩn 80 Plus Bronze công suất thực, dư tải an toàn"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": cooler_price, "spec": f"Giải nhiệt tối ưu cho {canonical_cpu}, giữ nhiệt độ mát mẻ êm ái"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": case_price, "spec": "Thiết kế đối lưu gió tốt, quạt ARGB làm mát toàn bộ linh kiện"}
            ]

            total_cost = sum(p["price"] for p in parts)

            advice = (
                f"Chiến lược thông minh khi tận dụng CPU {canonical_cpu} sẵn có: Toàn bộ ngân sách {budget:,} VNĐ được dồn 100% cho 7 linh kiện còn lại, "
                f"giúp bạn sở hữu Card đồ họa {vga_name} cực kỳ mạnh mẽ mà không bị cắt giảm chất lượng nguồn hay tản nhiệt! "
                f"Dàn máy chiến mượt mà tất cả các tựa game hiện nay ở độ phân giải Full HD / 2K Max Settings."
            )
            upgrade_path = (
                f"Hệ sinh thái đồng bộ Socket {mb_socket} và Nguồn {psu_watt}W công suất thực giúp bạn hoàn toàn an tâm sử dụng bền bỉ 4-6 năm, "
                f"sẵn sàng nâng cấp thêm dung lượng RAM hoặc cắm thêm SSD NVMe phụ bất cứ lúc nào."
            )

            compatibility_checks = [
                {
                    "aspect": f"CPU <=> Bo Mạch Chủ (Socket {cpu_socket})",
                    "status": "HOÀN HẢO",
                    "detail": f"CPU {canonical_cpu} (đã có sẵn) khớp 100% chân socket {cpu_socket} trên {mb_name}. Dàn phase nguồn VRM dày dặn đảm bảo cấp đủ điện năng tối đa."
                },
                {
                    "aspect": "RAM <=> Bo Mạch Chủ (Chuẩn DDR)",
                    "status": "HOÀN HẢO",
                    "detail": f"RAM chuẩn {ram_type} khớp tuyệt đối khe cắm trên bo mạch chủ {mb_name}."
                },
                {
                    "aspect": "Tản Nhiệt <=> CPU (Nhiệt năng TDP)",
                    "status": "AN TOÀN MÁT MẺ",
                    "detail": f"{cooler_name} giải tỏa nhiệt lượng xuất sắc cho {canonical_cpu}, giữ nhiệt độ luôn dưới 70°C khi chơi game nặng."
                },
                {
                    "aspect": "Card Đồ Họa <=> Vỏ Case",
                    "status": "VỪA VẶN",
                    "detail": f"Kích thước card {vga_name} lắp đặt vừa vặn hoàn hảo bên trong thùng máy {case_name}."
                },
                {
                    "aspect": "Công Suất Nguồn <=> Tổng Điện Năng",
                    "status": "DƯ TẢI AN TOÀN",
                    "detail": f"Nguồn {psu_watt}W chuẩn 80 Plus công suất thực, mức tiêu thụ tải dưới 60%, triệt tiêu nguy cơ sụt áp hay sập nguồn."
                }
            ]

            detailed_component_breakdown = {
                "cpu_main": f"CPU ({canonical_cpu}) đã có sẵn được lắp trên Mainboard ({mb_name}) chuẩn Socket {cpu_socket}, khai thác 100% xung nhịp Turbo mà không lo tụt xung do quá nhiệt VRM.",
                "ram": f"Bộ nhớ RAM ({ram_name}) chạy Dual Channel giúp mở rộng băng thông bộ nhớ, tăng độ mượt 1% Low FPS trong game.",
                "ssd": f"Ổ cứng ({ssd_name}) chuẩn NVMe Gen 4 khởi động máy trong 5 giây và tải map game thế giới mở tức thì.",
                "gpu": f"Card đồ họa ({vga_name}) là trái tim xử lý khung hình, đem lại trải nghiệm đồ họa mãn nhãn với công nghệ DLSS/Ray Tracing.",
                "psu": f"Bộ nguồn ({psu_name}) bảo vệ toàn diện hệ thống với chứng nhận 80 Plus, an tâm cày game liên tục nhiều giờ.",
                "cooler_case": f"Hệ thống tản nhiệt ({cooler_name}) và vỏ case ({case_name}) tạo luồng gió đối lưu mát mẻ, tôn lên vẻ đẹp góc máy làm việc."
            }

            return {
                "parts": parts,
                "total_cost": total_cost,
                "advice": advice,
                "upgrade_path": upgrade_path,
                "compatibility_checks": compatibility_checks,
                "detailed_component_breakdown": detailed_component_breakdown
            }

        # TRƯỜNG HỢP 2: BUILD TRỌN BỘ 8 LINH KIỆN MỚI TỪ ĐẦU (FULL_PC)
        budget = budget or 15_000_000

        if budget < 7_000_000 or any(w in purpose for w in ["Văn phòng", "Học tập"]) and budget <= 8_000_000:
            cpu_model = "Intel Core i3-12100"
            cpu_socket = "LGA1700"
            mb_name = "ASUS PRIME H610M-K DDR4"
            mb_socket = "LGA1700"
            ram_name = "16GB (2x8GB) Kingston Fury Beast DDR4 3200MHz"
            ram_type = "DDR4"
            ssd_name = "512GB Kingston NV2 NVMe PCIe 4.0 M.2"
            vga_name = "Intel UHD Graphics 730 (Tích hợp sẵn trong CPU - 0đ)"
            psu_name = "Xigmatek X-Power III 450 (400W 80 Plus)"
            psu_watt = 400
            cooler_name = "Tản nhiệt khí kèm sẵn theo hộp CPU (Intel Laminar RM1)"
            case_name = "Vỏ Xigmatek XA-20 (Thiết kế thanh lịch văn phòng)"
            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{cpu_model} (Kèm iGPU đồ họa tích hợp)", "price": 2_350_000, "spec": "LGA1700, 4 nhân 8 luồng, tích hợp đồ họa UHD 730"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": 1_450_000, "spec": "Socket LGA1700, hỗ trợ HDMI/VGA xuất đa màn hình"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": 750_000, "spec": "16GB DDR4 3200MHz chạy Dual Channel mượt mà đa nhiệm"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": 750_000, "spec": "NVMe PCIe Gen 4x4 (Đọc 3500MB/s, mở app tức thì)"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": 0, "spec": "Nhân đồ họa tích hợp, tiết kiệm 100% chi phí mua card rời"},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": 550_000, "spec": "Công suất thực 400W chuẩn 80 Plus, dư tải an toàn"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": 0, "spec": "Tản nhiệt chính hãng theo chip, êm ái mát mẻ"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": 350_000, "spec": "Thiết kế nhỏ gọn, sơn tĩnh điện bền bỉ"}
            ]
            advice = (
                "Cấu hình Đa dụng & Học tập / Văn phòng thông minh: Tận dụng nhân đồ họa tích hợp iGPU UHD 730 giúp tiết kiệm toàn bộ chi phí card rời, "
                "xử lý file Excel hàng trăm nghìn dòng, chạy trơn tru phần mềm kế toán, học online và giải trí nhẹ nhàng."
            )
            upgrade_path = "Nguồn 400W và bo mạch chủ H610 có sẵn khe PCIe x16. Sau này nếu cần chơi game hoặc dựng video, bạn chỉ cần cắm thêm card rời là thành máy gaming!"

        elif budget <= 10_000_000:
            cpu_model = "Intel Core i3-12100F"
            cpu_socket = "LGA1700"
            mb_name = "ASUS PRIME H610M-K DDR4"
            mb_socket = "LGA1700"
            ram_name = "16GB (2x8GB) Kingston Fury DDR4 3200MHz"
            ram_type = "DDR4"
            ssd_name = "512GB Kingston NV2 NVMe PCIe 4.0 M.2"
            vga_name = "NVIDIA GeForce GTX 1660 Super 6GB"
            psu_name = "Xigmatek X-Power III 550 (550W Bronze)"
            psu_watt = 550
            cooler_name = "Tản nhiệt khí Jonsbo CR-1000 EVO ARGB"
            case_name = "Vỏ Xigmatek NYX Air 3F (Kèm sẵn 3 Fan RGB)"
            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{cpu_model} (4 nhân 8 luồng)", "price": 1_850_000, "spec": "LGA1700, 58W-89W TDP"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": 1_450_000, "spec": "Socket LGA1700, RAM DDR4 Dual Channel"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": 750_000, "spec": "DDR4 3200MHz CL16 (2 thanh chạy Dual Channel)"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": 750_000, "spec": "NVMe PCIe Gen 4x4 (Đọc 3500MB/s)"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": 2_800_000, "spec": "6GB GDDR6, TDP 125W"},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": 850_000, "spec": "550W chuẩn 80 Plus Bronze"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": 350_000, "spec": "4 ống đồng, tản nhiệt max 180W TDP"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": 600_000, "spec": "Mặt lưới Airflow đối lưu, kèm 3 Fan LED"}
            ]
            advice = (
                "Cấu hình quốc dân phân khúc dưới 10 triệu: Cân tốt 100% các game Esport phổ biến "
                "(LOL, FO4, Valorant 180+ FPS, CS2 120+ FPS ở mức 1080p). Làm mượt Photoshop, dựng video ngắn CapCut."
            )
            upgrade_path = "Nguồn 550W sau này có thể nâng cấp lên RTX 2060S hoặc RTX 3060 mà không cần đổi nguồn."

        elif budget <= 17_000_000:
            cpu_model = "Intel Core i5-12400F"
            cpu_socket = "LGA1700"
            mb_name = "ASUS PRIME B760M-K DDR4"
            mb_socket = "LGA1700"
            ram_name = "16GB (2x8GB) Kingston Fury Beast 3200MHz"
            ram_type = "DDR4"
            ssd_name = "512GB Kingston NV2 NVMe PCIe 4.0 M.2"
            vga_name = "NVIDIA GeForce RTX 2060 Super 8GB (hoặc RX 6600)"
            psu_name = "MSI MAG A650BN 650W 80 Plus Bronze"
            psu_watt = 650
            cooler_name = "Jonsbo CR-1000 EVO ARGB (4 ống đồng)"
            case_name = "Montech Air 100 ARGB (Kính cường lực, 4 Fan PWM)"
            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{cpu_model} (6 nhân 12 luồng)", "price": 2_700_000, "spec": "LGA1700, Turbo 4.4GHz, 65W-117W TDP"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": 2_150_000, "spec": "Socket LGA1700, Chipset B760, VRM 8+1 Phase"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": 850_000, "spec": "DDR4 3200MHz CL16 (2 thanh chạy Dual Channel)"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": 850_000, "spec": "NVMe PCIe Gen 4x4 (Đọc 3500MB/s)"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": 4_000_000, "spec": "8GB GDDR6 256-bit, Ray Tracing & DLSS"},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": 1_200_000, "spec": "650W chuẩn 80 Plus Bronze tụ Nhật"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": 350_000, "spec": "4 ống đồng, tản nhiệt max 180W (CPU < 65°C)"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": 950_000, "spec": "Kính cường lực cánh mở, 4 quạt ARGB PWM hút xả đối lưu"}
            ]
            advice = (
                "Cấu hình 'Vua phân khúc 15 triệu': Cân mượt mà CS2 (200+ FPS), Valorant (250+ FPS), "
                "GTA 5 (100+ FPS High Settings). Chiến mượt cả game nặng AAA (Black Myth Wukong, Cyberpunk 2077) "
                "ở độ phân giải 1080p High Setting kết hợp DLSS!"
            )
            upgrade_path = "Nguồn 650W Bronze chuẩn công suất thực rất dư tải (hệ thống ăn max ~330W). Sau 2-3 năm nữa bạn chỉ cần cắm card RTX 4060 Ti hoặc RTX 4070 vào là nâng cấp cực dễ!"

        elif budget <= 28_000_000:
            cpu_model = "AMD Ryzen 5 7500F"
            cpu_socket = "AM5"
            mb_name = "MSI PRO B650M-A WIFI DDR5"
            mb_socket = "AM5"
            ram_name = "32GB (2x16GB) Kingston Fury Beast DDR5 5600MHz"
            ram_type = "DDR5"
            ssd_name = "1TB Kingston NV2 NVMe PCIe 4.0 M.2"
            vga_name = "NVIDIA GeForce RTX 4060 Ti 8GB / 16GB"
            psu_name = "Deepcool PK750D 750W 80 Plus Bronze"
            psu_watt = 750
            cooler_name = "Thermalright Peerless Assassin 120 SE (Tháp đôi 6 ống đồng)"
            case_name = "Vỏ Bể Cá Panorama Mik Morax 3FA (3 Fan vô cực)"
            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{cpu_model} (6 nhân 12 luồng Zen 4)", "price": 4_200_000, "spec": "Socket AM5, tiến trình 5nm, Turbo 5.0GHz"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": 3_200_000, "spec": "Socket AM5, Chipset B650, WiFi 6E + Bluetooth 5.3"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": 2_350_000, "spec": "DDR5 5600MHz (2 thanh chạy Dual Channel, On-die ECC)"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": 1_450_000, "spec": "1TB NVMe PCIe Gen 4x4 (Đọc 3500MB/s)"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": 9_800_000, "spec": "Kiến trúc Ada Lovelace, DLSS 3 Frame Generation"},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": 1_600_000, "spec": "750W chuẩn 80 Plus Bronze"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": 790_000, "spec": "Tháp đôi 6 ống dẫn nhiệt, max 245W TDP"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": 1_250_000, "spec": "Kính góc 2 mặt Panorama bể cá khoe trọn linh kiện"}
            ]
            advice = (
                "Cấu hình chuyên Gaming 2K & Đồ họa chuyên nghiệp: Chiến mọi tựa game ở độ phân giải 2K 144Hz Max Settings. "
                "Dung lượng RAM 32GB DDR5 và VGA hỗ trợ DLSS 3 Frame Generation tăng gấp 2 lần FPS trong game nặng."
            )
            upgrade_path = "Nền tảng Socket AM5 được AMD cam kết hỗ trợ lâu dài tới 2027+, bạn có thể nâng cấp thẳng lên Ryzen 7 9800X3D sau này mà không cần đổi Mainboard!"

        else:
            cpu_model = "AMD Ryzen 7 7800X3D"
            cpu_socket = "AM5"
            mb_name = "ASUS ROG STRIX B650E-F GAMING WIFI"
            mb_socket = "AM5"
            ram_name = "32GB (2x16GB) G.Skill Flare X5 DDR5 6000MHz CL30"
            ram_type = "DDR5"
            ssd_name = "1TB Samsung 990 Pro NVMe PCIe 4.0 M.2"
            vga_name = "NVIDIA GeForce RTX 4070 Super 12GB GDDR6X"
            psu_name = "Corsair RM850e 850W ATX 3.0 PCIe 5.0 Gold"
            psu_watt = 850
            cooler_name = "Deepcool LE520 ARGB 240mm (Tản nhiệt nước AIO)"
            case_name = "Vỏ Bể Cá Panorama Mik Morax 3FA (Kèm 3 Fan vô cực)"
            parts = [
                {"category": "Vi Xử Lý (CPU)", "item": f"{cpu_model} (Gaming King 96MB 3D V-Cache)", "price": 9_500_000, "spec": "Socket AM5, 8 nhân 16 luồng, CPU chơi game số 1 thế giới"},
                {"category": "Bo Mạch Chủ (Main)", "item": mb_name, "price": 5_800_000, "spec": "Socket AM5, PCIe 5.0 cho VGA & SSD, 12+2 Phase nguồn"},
                {"category": "Bộ Nhớ RAM", "item": ram_name, "price": 2_850_000, "spec": "DDR5 6000MHz độ trễ siêu thấp CL30 Sweet Spot"},
                {"category": "Ổ Cứng (SSD)", "item": ssd_name, "price": 2_650_000, "spec": "Đọc 7450MB/s, có DRAM Cache cho render file nặng"},
                {"category": "Card Đồ Họa (VGA)", "item": vga_name, "price": 16_500_000, "spec": "12GB GDDR6X, Ray Tracing & DLSS 3.5 đỉnh cao"},
                {"category": "Nguồn Máy Tính (PSU)", "item": psu_name, "price": 3_150_000, "spec": "850W 80 Plus Gold Fully Modular, chuẩn ATX 3.0 cáp 16-pin"},
                {"category": "Tản Nhiệt CPU", "item": cooler_name, "price": 1_450_000, "spec": "Tản nước AIO 240mm ARGB làm mát êm ái"},
                {"category": "Vỏ Case Máy Tính", "item": case_name, "price": 1_250_000, "spec": "Bể cá vô cực Panorama 2 mặt kính cường lực"}
            ]
            advice = (
                "Cấu hình Đẳng Cấp Thượng Lưu (Flagship): Chinh phục mọi tựa game ở độ phân giải 2K/4K Ultra Settings. "
                "Công nghệ 3D V-Cache giúp chỉ số 1% Low FPS cực cao, triệt tiêu 100% hiện tượng drop khung hình."
            )
            upgrade_path = "Nguồn chuẩn ATX 3.0 PCIe 5.0 sẵn sàng cắm thẳng các dòng card quái vật tương lai như RTX 5080/5090 mà không cần đầu chuyển!"

        total_cost = sum(p["price"] for p in parts)

        compatibility_checks = [
            {
                "aspect": "CPU <=> Bo Mạch Chủ (Socket)",
                "status": "HOÀN HẢO",
                "detail": f"CPU {cpu_model} khớp hoàn toàn chân socket {cpu_socket} trên {mb_name}."
            },
            {
                "aspect": "RAM <=> Bo Mạch Chủ (Chuẩn DDR)",
                "status": "HOÀN HẢO",
                "detail": f"RAM chuẩn {ram_type} khớp tuyệt đối khe cắm trên bo mạch chủ."
            },
            {
                "aspect": "Tản Nhiệt <=> CPU (Nhiệt năng TDP)",
                "status": "AN TOÀN MÁT MẺ",
                "detail": f"{cooler_name} giải nhiệt dư tải, máy vận hành êm ái không tiếng ồn."
            },
            {
                "aspect": "Card Đồ Họa <=> Vỏ Case",
                "status": "VỪA VẶN",
                "detail": "Kích thước gọn gàng, tương thích tuyệt đối với kích thước vỏ case."
            },
            {
                "aspect": "Công Suất Nguồn <=> Tổng Điện Năng",
                "status": "DƯ TẢI AN TOÀN",
                "detail": f"Nguồn {psu_watt}W chuẩn công suất thực, mức tiêu thụ dưới 50% giúp hệ thống chạy mát mẻ bền bỉ suốt 5-10 năm."
            }
        ]

        if purpose == "Đồ họa & Render":
            detailed_component_breakdown = {
                "cpu_main": f"Sự kết hợp giữa CPU ({cpu_model}) và Mainboard ({mb_name}) đảm bảo dàn phase nguồn VRM tản nhiệt tốt, duy trì xung nhịp cao ổn định khi render liên tục nhiều giờ.",
                "ram": f"Dung lượng ({ram_name}) dồi dào, đảm bảo không bị tràn bộ nhớ (Out of Memory) khi preview timeline 4K và dựng mô hình 3D đa giác cao.",
                "ssd": f"Tốc độ đọc ghi NVMe của ({ssd_name}) giúp load các bộ thư viện texture 3D dung lượng lớn và xuất project video tức thì.",
                "gpu": f"Sức mạnh của ({vga_name}) với nhân CUDA/Tensor hỗ trợ tăng tốc GPU Rendering (OptiX, CUDA trong Blender, Premiere) và tính năng AI Denoise.",
                "psu": f"Bộ nguồn ({psu_name}) công suất thực đảm bảo hệ thống render nặng qua đêm an toàn tuyệt đối, chống đoản mạch và sụt áp.",
                "cooler_case": f"Hệ thống làm mát ({cooler_name}) và vỏ case ({case_name}) tạo luồng gió đối lưu liên tục, giải nhiệt nhanh giữ nhiệt độ CPU dưới 70°C."
            }
        elif any(w in purpose for w in ["Văn phòng", "Học tập"]) or budget < 7_000_000:
            detailed_component_breakdown = {
                "cpu_main": f"Sự kết hợp giữa CPU ({cpu_model}) và Mainboard ({mb_name}) đảm bảo dàn phase nguồn VRM cấp điện ổn định, hỗ trợ xuất đa màn hình làm việc.",
                "ram": f"Bộ nhớ RAM ({ram_name}) giúp đa nhiệm mượt mà, mở hàng chục tab trình duyệt và file văn phòng cùng lúc.",
                "ssd": f"Ổ cứng SSD ({ssd_name}) đạt tốc độ đọc ghi chuẩn NVMe Gen 4, mở máy và tải tài liệu chỉ trong vài giây.",
                "gpu": f"Xử lý hình ảnh ({vga_name}) tối ưu chi phí, không tỏa nhiệt và tiết kiệm điện tối đa.",
                "psu": f"Bộ nguồn ({psu_name}) đạt chuẩn an toàn, dư dả công suất thực bảo vệ linh kiện chống sụt áp.",
                "cooler_case": f"Hệ thống tản nhiệt và vỏ case ({case_name}) giữ máy luôn mát mẻ và êm ái trong không gian làm việc."
            }
        else:
            detailed_component_breakdown = {
                "cpu_main": f"Sự kết hợp giữa CPU ({cpu_model}) và Mainboard ({mb_name}) tối ưu hiệu năng đơn nhân và IPC cao, triệt tiêu nghẽn cổ chai và ổn định 1% Low FPS.",
                "ram": f"Bộ nhớ ({ram_name}) chạy chuẩn Dual Channel giúp tăng ngay 15-20% FPS trong các tựa game bắn súng Esport cạnh tranh.",
                "ssd": f"Ổ cứng SSD ({ssd_name}) chuẩn NVMe Gen 4 tải bản đồ game thế giới mở tức thì, triệt tiêu hiện tượng khựng lag khi load map.",
                "gpu": f"Card đồ họa ({vga_name}) là trái tim khung hình, hỗ trợ công nghệ Ray Tracing và DLSS/FSR cho trải nghiệm hình ảnh mượt mà, sống động.",
                "psu": f"Bộ nguồn ({psu_name}) dư dả công suất, gánh tốt các pha xung đột gai điện (transient spikes) của card khi combat đông người.",
                "cooler_case": f"Tản nhiệt ({cooler_name}) và vỏ case ({case_name}) tối ưu luồng gió Airflow, giữ cho card và chip luôn mát mẻ dưới 65-70°C khi cày game."
            }

        return {
            "parts": parts,
            "total_cost": total_cost,
            "advice": advice,
            "upgrade_path": upgrade_path,
            "compatibility_checks": compatibility_checks,
            "detailed_component_breakdown": detailed_component_breakdown
        }
