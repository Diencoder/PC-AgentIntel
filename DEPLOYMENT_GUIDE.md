# BỘ TÀI LIỆU HƯỚNG DẪN TRIỂN KHAI HỆ THỐNG MULTI-AGENT
## Đề tài: PC-AgentIntel — Hệ Thống Multi-Agent Tư Vấn Cấu Hình & Kiểm Định Tương Thích Phần Cứng PC
* **Học phần:** Trí Tuệ Nhân Tạo Ứng Dụng (AI Application / AI Agents)
* **Nhiệm vụ:** **Nhiệm vụ 13** — *Xây dựng tối thiểu 2 AI Agents tự chủ cùng thực hiện công việc A (tự chọn) & Soạn tài liệu hướng dẫn triển khai hoàn chỉnh.*
* **Nhóm đề tài:** Hệ Thống Multi-Agent Hỗ Trợ Ra Quyết Định Kỹ Thuật (Multi-Agent Hardware Advisory & Compatibility Audit System).
* **Phiên bản:** v2.5 (Tích hợp Live Gemini 3.5 Flash Model + Hệ Thống Tri Thức Chuyên Gia Fallback).

---

## 1. TỔNG QUAN HỆ THỐNG & ĐẶT VẤN ĐỀ

### 1.1. Bối cảnh & Bài toán cần giải quyết
Tư vấn cấu hình máy tính là một bài toán phức tạp đòi hỏi sự kết hợp giữa:
1. **Khả năng thấu hiểu ngôn ngữ tự nhiên:** Tiếp nhận yêu cầu của người dùng thường bị nhiễu (teencode, viết tắt cẩu thả, nói ngắc ngứ, sai thuật ngữ).
2. **Kiểm định vật lý & An toàn kỹ thuật nghiêm ngặt:** Đảm bảo chân cắm CPU khớp với bo mạch chủ (Socket), chuẩn RAM (DDR4 vs DDR5), công suất nguồn dư tải an toàn (tránh cháy nổ) và triệt tiêu nghẽn cổ chai (Bottleneck).
3. **Cân đối tài chính tối ưu:** Phân bổ ngân sách thông minh vào từng linh kiện theo đúng mục đích sử dụng (Gaming, Đồ họa Render, Văn phòng).

### 1.2. Tại sao là "AI AGENT" mà không phải "Chatbot thông thường"?
Hệ thống này được định nghĩa là **AI Agent System** dựa trên 4 trụ cột khoa học máy tính:
* **Tính Mục Tiêu & Tự Chủ (Goal-Driven & Autonomy):** Agent không chỉ trò chuyện xã giao, mà nhận một mục tiêu cụ thể và tự lập kế hoạch phân rã mục tiêu (Goal Decomposition).
* **Khả Năng Sử Dụng Công Cụ (Tool Calling / Function Calling):** Để khắc phục nhược điểm lớn nhất của mô hình ngôn ngữ lớn (LLM) là bị "ảo giác" (tự bịa thông số, tính nhẩm sai số Watt nguồn), Agent bắt buộc phải gọi 4 công cụ độc lập để tính toán vật lý, đo benchmark và truy vấn cơ sở dữ liệu thật.
* **Hợp Đồng Dữ Liệu Đa Tác Tử (Data Contract Hand-off):** Phân chia rõ ràng trách nhiệm giữa Agent 1 (Tiếp nhận & Chuẩn hóa) và Agent 2 (Kỹ sư trưởng Thẩm định & Ra quyết định).
* **Cơ Chế Kiểm Soát Sai Sót (Guardrails & Reflection):** Tự động phát hiện các xung đột nguy hiểm (CPU Intel cắm Main AMD, nguồn công suất ảo noname) và kích hoạt cảnh báo chặn đứng ngay lập tức.

---

## 2. KIẾN TRÚC HỆ THỐNG MULTI-AGENT

```
                  [ Người Dùng Nhập Ngôn Ngữ Tự Nhiên ]
               (Teencode, viết tắt, "có sẵn chip i5 14600k", v.v.)
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🤖 AGENT 1: Hardware Intent & Spec Analyst (agents/spec_analyst_agent.py)    │
│  • Khử nhiễu văn bản (Teencode, ngắc ngứ, lặp từ, đảo lộn linh kiện).        │
│  • Bóc tách thực thể: CPU, Nguồn (W), Ngân sách (VND), Tình trạng (Mới/Cũ).  │
│  • Nhận diện linh kiện ĐÃ CÓ SẴN (already_owned_parts: CPU / GPU).          │
│  • Phân loại mục tiêu:                                                      │
│    - FULL_PC (Build mới 100% cả 8 món từ đầu)                               │
│    - BUILD_WITH_EXISTING (Lắp ráp case quanh linh kiện có sẵn)             │
│    - GPU (Nâng cấp card rời độc lập)                                        │
│  • Tạo hồ sơ chiến lược bàn giao (Agent 1 Brief).                            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ [HardwareSpecContract] (Pydantic Model)
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚡ AGENT 2: Senior Compatibility Engineer (agents/compatibility_agent.py)    │
│  • Nhận hồ sơ dữ liệu chuẩn hóa từ Agent 1.                                 │
│  • Điều phối và thực thi 4 Công Cụ Kỹ Thuật Chuyên Dụng (Tools):           │
│    ├─ DBLookupTool        : Tra cứu CSDL 8 danh mục linh kiện Việt Nam.    │
│    ├─ PSUCalculatorTool   : Tính tải điện tiêu thụ đỉnh (Peak Wattage).     │
│    ├─ BottleneckTool      : Đo tỷ lệ nghẽn cổ chai IPC giữa CPU & GPU.      │
│    └─ FullPCBuildTool     : Tối ưu 8 linh kiện theo ngân sách & socket.     │
│  • Kiểm định 5 tiêu chuẩn tương thích đồng bộ hệ thống.                      │
│  • Sinh báo cáo tư vấn chuyên sâu (Hỗ trợ Gemini 3.5 Flash + Fallback).     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ [FinalAuditReport]
                       [ Giao Diện CLI / Streamlit Web UI ]
```

### Kiến trúc Dự Phòng Kép (Dual-Engine Resilience):
* **Tầng 1 (Live AI):** Kết nối trực tiếp máy chủ Google qua mô hình **`gemini-3.5-flash`** để viết bài tư vấn tự nhiên, sinh động, dự báo FPS game thực tế (CS2, Valorant, Wukong) và lời khuyên BIOS chuyên sâu.
* **Tầng 2 (Expert Heuristic Fallback):** Nếu mạng gián đoạn hoặc API quá tải/hết token, hệ thống tự động kích hoạt **Bộ máy Tri thức Chuyên gia nội bộ** được nhúng sẵn trong `full_build_tool.py`. Hệ thống cam kết **không bao giờ bị crash, không văng lỗi màn hình đỏ**.

---

## 3. DANH MỤC THÀNH PHẦN MÃ NGUỒN

### 3.1. Các Tác Tử AI (Agents)
1. **`agents/spec_analyst_agent.py` (Agent 1):**
   * Lớp `SpecAnalystAgent`: Xử lý ngôn ngữ tự nhiên, loại bỏ nhiễu, trích xuất thực thể phần cứng và phát hiện linh kiện sẵn có (`already_owned_parts`).
2. **`agents/compatibility_agent.py` (Agent 2):**
   * Lớp `CompatibilityAgent`: Đóng vai Kỹ sư trưởng phần cứng, gọi các công cụ số học, thẩm định độ tương thích 5 sao và soạn bài tư vấn kỹ thuật.

### 3.2. Bộ Công Cụ Ngoại Vi (Agent Tools)
1. **`tools/db_lookup_tool.py` (`DBLookupTool`):**
   * Quản lý CSDL phần cứng [data/pc_parts_db.json](file:///d:/Project/pc_agent_system/data/pc_parts_db.json) (29 GPU, 24 CPU, Mainboard, RAM, SSD, PSU, Tản, Case).
   * Cơ chế **Dynamic Spec Inference**: Tự động suy luận TDP và thế hệ đối với những mã chip lạ/ảo không có trong CSDL.
2. **`tools/psu_calculator_tool.py` (`PSUCalculatorTool`):**
   * Tính toán công suất tiêu thụ tối đa hệ thống: $	ext{Peak Watt} = (	ext{CPU TDP} + 	ext{GPU TDP} + 50	ext{W}) 	imes 1.3$ (hệ số dự phòng an toàn $1.3	imes$).
   * Đánh giá tỷ lệ tải nguồn: `SAFE` ($<80\%$), `WARNING` ($80-95\%$), `DANGER` ($>95\%$).
3. **`tools/bottleneck_tool.py` (`BottleneckTool`):**
   * Đo lường độ lệch hiệu năng CPU - GPU, chia 3 cấp độ: `LOW` ($<15\%$), `MODERATE` ($15-30\%$), `HIGH` ($>30\%$).
4. **`tools/full_build_tool.py` (`FullPCBuildTool`):**
   * Tự động lắp ráp 8 linh kiện cân bằng tuyệt đối từ 5 triệu đến trên 50 triệu VNĐ.
   * Hỗ trợ chế độ **Hybrid Build**: Khóa linh kiện đã có sẵn (CPU/VGA = 0 VNĐ), tự động ghép đúng Socket bo mạch chủ và dồn 100% ngân sách cho các linh kiện còn lại.

### 3.3. Các Thành Phần Điều Phối & Giao Diện
* **`core/schemas.py`:** Định nghĩa Data Contracts (`HardwareSpecContract`, `FinalAuditReport`, `GPUCandidate`...) bằng Pydantic.
* **`core/config.py`:** Quản lý cấu hình biến môi trường (`.env`), ẩn các cảnh báo nội bộ không cần thiết của Google SDK.
* **`orchestrator.py`:** Bộ điều phối liên tác tử Multi-Agent Pipeline.
* **`run_cli.py`:** Giao diện dòng lệnh Terminal hiển thị màu sắc và bảng biểu bằng thư viện Rich.
* **`run_ui.py`:** Giao diện ứng dụng Web Dashboard thương mại hiện đại xây dựng trên Streamlit.

---

## 4. HƯỚNG DẪN CÀI ĐẶT & TRIỂN KHAI CHI TIẾT

### Bước 1: Yêu cầu môi trường
* Hệ điều hành: Windows 10/11, macOS, hoặc Linux.
* Python: Phiên bản **Python 3.10 trở lên** (Đã kiểm thử tối ưu trên Python 3.11).

### Bước 2: Cài đặt các thư viện phụ thuộc
Mở terminal tại thư mục gốc của dự án `pc_agent_system`:
```bash
pip install -r requirements.txt
```
*(Các thư viện chính: `streamlit>=1.30`, `pydantic>=2.0`, `google-genai>=1.0`, `rich>=13.0`, `python-dotenv>=1.0`, `pytest>=7.0`).*

### Bước 3: Cấu hình khóa API Google Gemini (`.env`)
Tạo file `.env` tại thư mục gốc `pc_agent_system/.env` với nội dung:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```
*(Hệ thống đã cấu hình sẵn key miễn phí và tự động kích hoạt chế độ Fallback nếu mất kết nối).*

---

## 5. HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### Cách 1: Khởi chạy Giao diện Web (Streamlit UI) — Khuyên Dùng Cho Thuyết Minh
Chạy lệnh sau trong terminal:
```bash
streamlit run run_ui.py
```
* Trình duyệt sẽ tự động mở giao diện tại địa chỉ: **`http://localhost:8501`**.
* Giao diện được thiết kế thanh lịch, chuyên nghiệp: Thanh bên Sidebar hiển thị cấu trúc Multi-Agent & CSDL phần cứng; màn hình chính là ô nhập yêu cầu và bảng kết quả tư vấn chuẩn xác.

### Cách 2: Khởi chạy Giao diện Dòng Lệnh Tương Tác (Interactive CLI)
Dành cho kiểm thử nhanh trên terminal:
```bash
python run_cli.py
```
* Nhập trực tiếp câu hỏi đời thường bất kỳ và nhấn `Enter` để xem 2 Agent phối hợp phân tích.

---

## 6. CÁC KỊCH BẢN THỰC THI & KIỂM THỬ MẪU (TEST SCENARIOS)

### Kịch bản 1: Ráp trọn bộ PC mới theo ngân sách (Full PC Build)
* **Câu lệnh mẫu:** `"tôi muốn build pc ngân sách 15 triệu chơi game"`
* **Kết quả xử lý:**
  * **Agent 1:** Nhận diện mục đích `Gaming`, ngân sách `15.000.000đ`, loại hình `FULL_PC`.
  * **Agent 2 & Tool:** Đề xuất dàn máy quốc dân 8 món: CPU i5-12400F, Main ASUS B760M-K DDR4, RAM 16GB Dual Channel, SSD 512GB NVMe, VGA RTX 2060 Super 8GB, Nguồn 650W Bronze, Tản CR1000 EVO, Vỏ case Montech Air 100.
  * **Tổng chi phí:** Đúng tròn `14.900.000đ` (Cắm điện là dùng).

### Kịch bản 2: Lắp ráp case khi ĐÃ CÓ SẴN linh kiện (Hybrid Build)
* **Câu lệnh mẫu:** `"tôi muốn build pc 20 triệu nhu cầu gaming đã có sẵn chip i5 14600k"`
* **Kết quả xử lý:**
  * **Agent 1:** Phát hiện từ khóa `"đã có sẵn chip i5 14600k"`. Đặt loại hình `BUILD_WITH_EXISTING`, lập lệnh: khóa CPU = `0 VNĐ`, bảo tồn trọn vẹn 20 triệu cho 7 linh kiện còn lại.
  * **Agent 2 & Tool:** 
    * Khớp đúng chuẩn Socket **LGA1700**: Chọn Bo mạch chủ `MSI B760M GAMING PLUS WIFI DDR5` (VRM 12+1 Phase cực khỏe) thay vì chọn nhầm Main AMD B650 AM5.
    * Nhận diện chip dòng K tỏa nhiệt lớn: Chọn Tản tháp đôi 6 ống đồng `Thermalright Peerless Assassin 120 SE`.
    * Dồn toàn bộ tiền còn lại lên Card đồ họa **RTX 4060 Ti 8GB New**, RAM 32GB DDR5, SSD 1TB NVMe, Nguồn 750W Bronze, Vỏ bể cá Panorama!
  * **Tổng chi phí đầu tư thêm:** Chuẩn xác `20.000.000đ`.

### Kịch bản 3: Nâng cấp linh kiện lẻ & Cảnh báo an toàn (GPU Upgrade)
* **Câu lệnh mẫu:** `"đang có chip celeron g5905 với nguồn cỏ 250w, có 65 triệu tính mua con rtx 5090 về cắm"`
* **Kết quả xử lý:**
  * **Agent 1:** Nhận diện nhu cầu mua riêng card đồ họa cắm vào dàn máy cũ.
  * **Agent 2 & Tool:** Bật ngay 2 còi báo động đỏ:
    * ⛔ `DANGER (377.2% tải nguồn):` Nguồn 250W quá tải cực đoan với RTX 5090 (TDP 575W), nguy cơ cháy nổ nổ tụ lập tức. Yêu cầu nguồn tối thiểu 1000W!
    * ⚠️ `HIGH (Nghẽn cổ chai nặng):` CPU 2 nhân Celeron G5905 gây nghẽn >80% sức mạnh của RTX 5090.

### Kịch bản 4: Đánh chặn xung đột vật lý chết người (Hardware Guardrails)
1. **CPU Intel đòi cắm Mainboard AMD:**
   * *Câu lệnh:* `"mình muốn ráp chip intel i5 12400f với bo mạch chủ b650m am5 của amd có được không"`
   * *Phản ứng:* Chặn đứng ngay: `⛔ LỖI TƯƠNG THÍCH NGHIÊM TRỌNG: Socket LGA1700 và Socket AM5 hoàn toàn khác biệt! Tuyệt đối không thể lắp chung!`
2. **RAM DDR4 đòi cắm khe DDR5:**
   * *Câu lệnh:* `"tôi có sẵn 2 thanh ram ddr4 3200mhz muốn cắm vào main b760 ddr5 mới mua"`
   * *Phản ứng:* Chặn đứng ngay: `⛔ LỖI CHUẨN KHE CẮM RAM: RAM DDR4 khác rãnh khuyết và điện áp với khe DDR5!`
3. **Nguồn văn phòng noname gánh card nặng:**
   * *Câu lệnh:* `"mình có nguồn văn phòng arrow ghi 600w mà nhẹ tênh, có 6 triệu muốn mua rtx 3070"`
   * *Phản ứng:* Chặn đứng ngay: `⛔ CẢNH BÁO NGUỒN CÔNG SUẤT ẢO: Nguồn noname Arrow chỉ đạt công suất thực < 250W, cắm RTX 3070 sẽ nổ tụ hoặc cháy lan!`

---

## 7. BỘ KIỂM THỬ TỰ ĐỘNG (AUTOMATION TESTING)

### 7.1. Kiểm thử đơn vị (Unit Tests) với Pytest
Chạy lệnh:
```bash
pytest tests/ -v
```
* **Kết quả:** `5/5 PASSED` (Kiểm thử độc lập PSU Calculator, Bottleneck Tool, DBLookup Tool, Full Build Engine, và Contract Parser).

### 7.2. Bộ Stress-Test 9 Kịch Bản Nhiễu Thực Tế Cực Đoan
Chạy lệnh:
```bash
python tests/test_noisy_inputs.py
```
* **Kết quả:** `9/9 PASSED (100% ĐẠT CHUẨN XUẤT SẮC)`:
  * `NOISE-01`: Lắp bắp, ngập ngừng, lặp từ, sửa lời.
  * `NOISE-02`: Teencode cẩu thả, viết tắt tiếng lóng (*"rái den"*, *"kard"*).
  * `NOISE-03`: Nói lan man chuyện đời tư (mèo làm đổ nước, thưởng công ty, vợ cho tiền).
  * `NOISE-04`: Nói cụt ngủn, thiếu 100% thông tin (*"tôi muốn mua máy tính"* $
ightarrow$ kích hoạt hỏi bổ sung).
  * `NOISE-05`: Đảo lộn thuật ngữ (gọi RTX 3060 là nguồn, gọi i5 là card).
  * `NOISE-06`: Phiên âm tiếng Việt dị (*"rai dừn sáu trăm oát 8 chẹo"*).
  * `NOISE-07`: Chip lạ/ảo tưởng không có trong CSDL (*"R7 9999X3D"* $
ightarrow$ kích hoạt suy luận động).
  * `NOISE-08`: Ngân sách phi lý (*"500k đòi 4K max setting"*).
  * `NOISE-09`: Cấu hình chéo ngoe (Celeron + 250W đòi cắm RTX 5090).

---

## 8. CÂU HỎI VẤN ĐÁP MẪU & CÂU TRẢ LỜI CHUẨN ĐIỂM 10 (DEFENSE Q&A)

### Câu 1: Tại sao hệ thống này được gọi là AI Agent mà không phải Chatbot thông thường?
> **Trả lời:** *"Thưa thầy, hệ thống có đủ 4 đặc trưng cốt lõi của AI Agent: (1) Tính mục tiêu và tự chủ (Goal-driven); (2) Khả năng sử dụng công cụ (Tool Use) để tính Watt và đo nghẽn vật lý thay vì tự bịa; (3) Kiến trúc Multi-Agent phân chia vai trò rõ ràng với hợp đồng dữ liệu chuẩn Pydantic; và (4) Khả năng tự phản xạ và kiểm soát sai sót kỹ thuật (Self-Reflection Guardrails) trước các xung đột phần cứng chết người."*

### Câu 2: Khi nào hệ thống dùng Gemini và khi nào dùng Heuristic Engine?
> **Trả lời:** *"Thưa thầy, hệ thống được thiết kế theo kiến trúc Chịu lỗi kép (Dual-Engine Resilience): Bình thường khi có mạng và API Key, hệ thống gọi Gemini 3.5 Flash để sinh lời tư vấn tự nhiên, sinh động và phân tích chuyên sâu. Tuy nhiên, nếu mất mạng, timeout hoặc API chạm ngưỡng hạn mức, hệ thống tự động kích hoạt bộ máy Tri thức Chuyên gia nội bộ để tiếp tục phục vụ người dùng trơn tru mà không bao giờ bị sập ứng dụng."*

### Câu 3: Làm thế nào hệ thống đảm bảo cấu hình đề xuất lắp được vào nhau 100% ngoài thực tế?
> **Trả lời:** *"Thưa thầy, hệ thống thực hiện kiểm định đồng bộ theo 5 tiêu chuẩn vàng phần cứng: (1) Socket CPU khớp với Socket Bo mạch chủ; (2) Chuẩn thế hệ RAM khớp khe DDR4/DDR5; (3) TDP Tản nhiệt giải tỏa đủ công suất nhiệt lượng của CPU; (4) Chiều dài Card đồ họa vừa vặn với kích thước vỏ Case; và (5) Công suất nguồn PSU dư tải tối thiểu 30-40% so với điện năng tiêu thụ đỉnh để chống sụt áp và sập nguồn."*
