<div align="center">

# 💻 PC-AGENTINTEL — AI MULTI-AGENT HARDWARE ADVISOR & COMPATIBILITY AUDITOR

### Hệ Thống Multi-Agent Tự Chủ Tư Vấn Cấu Hình & Kiểm Định Tương Thích Phần Cứng PC Hàng Đầu
*Tự động bóc tách ngôn ngữ tự nhiên, phân bổ ngân sách 8 linh kiện tối ưu, kiểm định an toàn điện năng, đo nghẽn cổ chai và phát hiện xung đột chân cắm vật lý.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash-orange?logo=google&logoColor=white)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit%20Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pydantic](https://img.shields.io/badge/Data%20Contract-Pydantic%20v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/Unit%20Tests-5%2F5%20Passed-brightgreen?logo=pytest&logoColor=white)](https://pytest.org/)
[![Stress Test](https://img.shields.io/badge/Stress%20Test-9%2F9%20Passed-brightgreen)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📖 1. Giới thiệu tổng quan

**PC-AgentIntel** là giải pháp phần mềm thông minh ứng dụng kiến trúc **Multi-Agent tự chủ (Autonomous Multi-Agent System)** nhằm tự động hóa toàn diện quy trình tư vấn cấu hình máy tính và thẩm định an toàn kỹ thuật phần cứng.

Thay vì dựa vào một Chatbot LLM thông thường dễ gây ra ảo giác thông số (*tự bịa giá, tính nhầm công suất nguồn, tư vấn cắm sai socket*), **PC-AgentIntel** phân tách công việc thành **2 AI Agents độc lập** phối hợp chặt chẽ theo nguyên tắc **Single Responsibility** và **Tool Calling**:

1. **Thấu hiểu ngôn ngữ tự nhiên cực đoan:** Bóc tách chính xác nhu cầu kể cả khi người dùng nói ngắc ngứ, dùng teencode, từ lóng (*"rái den"*, *"sáu trăm oát"*, *"8 chẹo"*, *"kạt màng hình"*).
2. **Kiểm định vật lý & An toàn kỹ thuật 5 sao:** Kiểm tra khớp chân cắm CPU <=> Mainboard (Socket LGA1700 / AM5 / AM4), chuẩn RAM (DDR4 vs DDR5), công suất nguồn dư tải an toàn và đo lường nghẽn cổ chai (Bottleneck).
3. **Chiến lược phân bổ tài chính tối ưu:** 
   * **Ráp mới 100% cả 8 món:** Cân đối ngân sách từ 5 triệu đến 50+ triệu VNĐ.
   * **Hybrid Build (Quanh linh kiện có sẵn):** Khóa CPU/VGA đã có sẵn với giá 0đ, dồn 100% ngân sách cho các món còn lại.
   * **Nâng cấp linh kiện lẻ:** Thẩm định tải nguồn và cảnh báo cháy nổ khi cắm card nặng vào nguồn noname "cỏ".

---

## 🤖 2. Kiến trúc Multi-Agent & Cơ chế phối hợp

Hệ thống vận hành theo quy trình **Perception $ightarrow$ Reasoning $ightarrow$ Tool Action $ightarrow$ Decision Making**:

```
                  [ Người Dùng Nhập Ngôn Ngữ Tự Nhiên ]
               (Teencode, viết tắt, "có sẵn chip i5 14600k", v.v.)
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🤖 AGENT 1: Hardware Intent & Spec Analyst (agents/spec_analyst_agent.py)    │
│  • Khử nhiễu văn bản (Teencode, lặp từ, đảo lộn thuật ngữ phần cứng).        │
│  • Bóc tách thực thể: CPU, Nguồn (W), Ngân sách (VND), Tình trạng (Mới/Cũ).  │
│  • Phát hiện linh kiện ĐÃ CÓ SẴN (already_owned_parts: CPU / GPU).          │
│  • Phân định 3 nhánh nhu cầu: FULL_PC, BUILD_WITH_EXISTING, GPU.            │
│  • Đóng gói hồ sơ chiến lược bàn giao (Agent 1 Brief).                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ [HardwareSpecContract] (Pydantic Schema)
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚡ AGENT 2: Senior Compatibility Engineer (agents/compatibility_agent.py)    │
│  • Tiếp nhận hợp đồng dữ liệu kỹ thuật từ Agent 1.                           │
│  • Điều phối và kích hoạt 4 Python Tools chuyên dụng:                       │
│    ├─ DBLookupTool        : Tra cứu CSDL 8 danh mục linh kiện Việt Nam.    │
│    ├─ PSUCalculatorTool   : Đo đạc công suất tải điện đỉnh (Peak Watt).     │
│    ├─ BottleneckTool      : Đo tỷ lệ nghẽn cổ chai IPC giữa CPU & GPU.      │
│    └─ FullPCBuildTool     : Tối ưu 8 linh kiện trọn bộ theo Socket & Budget.│
│  • Kiểm định 5 tiêu chuẩn tương thích đồng bộ phần cứng.                     │
│  • Sinh báo cáo tư vấn chuyên sâu (Hỗ trợ Live Gemini 3.5 Flash + Fallback).│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ [FinalAuditReport]
                   [ Web UI Dashboard / Interactive Terminal CLI ]
```

---

## 🛠️ 3. Bộ Công cụ Kỹ thuật Ngoại vi (Tools)

Để triệt tiêu 100% hiện tượng "ảo giác AI", Agent 2 bắt buộc phải sử dụng các công cụ số học độc lập:

* **`DBLookupTool` (`tools/db_lookup_tool.py`):** Tra cứu CSDL [data/pc_parts_db.json](file:///d:/Project/pc_agent_system/data/pc_parts_db.json) (29 dòng GPU, 24 dòng CPU, Bo mạch chủ, RAM, SSD, Nguồn, Tản nhiệt, Vỏ Case). Hỗ trợ cơ chế **Dynamic Spec Inference** tự suy luận thông số an toàn cho các dòng chip lạ/ảo không có trong CSDL.
* **`PSUCalculatorTool` (`tools/psu_calculator_tool.py`):** Tính toán điện năng tiêu thụ tối đa hệ thống: $	ext{Peak Watt} = (	ext{CPU TDP} + 	ext{GPU TDP} + 50	ext{W}) 	imes 1.3$ (hệ số dự phòng an toàn $1.3	imes$). Phân loại 3 mức an toàn: `SAFE` ($<80\%$), `WARNING` ($80-95\%$), `DANGER` ($>95\%$).
* **`BottleneckTool` (`tools/bottleneck_tool.py`):** Thuật toán đo lường độ lệch IPC giữa các thế hệ CPU và GPU, phát hiện nghẽn cổ chai phần cứng.
* **`FullPCBuildTool` (`tools/full_build_tool.py`):** Thuật toán cấu hình 8 linh kiện đồng bộ 100%, tự động ghép đúng Socket (LGA1700 / AM5 / AM4), tự động chọn tản tháp đôi cho chip dòng K tỏa nhiệt lớn và cân bằng tài chính.

---

## ⚡ 4. Các Tính Năng Nổi Bật

### 4.1. Lắp ráp trọn bộ 8 linh kiện mới (100% New Full PC)
* Tối ưu hóa từ 5 triệu (dùng iGPU văn phòng tiết kiệm 100% card rời) đến 50+ triệu (Flagship Ryzen 7 7800X3D + RTX 4070 Super).
* Đồng bộ 100% từ bo mạch chủ, RAM Dual Channel, SSD NVMe Gen 4, Tản nhiệt, Nguồn 80 Plus đến Vỏ bể cá Panorama.

### 4.2. Lắp ráp hoàn thiện quanh linh kiện CÓ SẴN (Hybrid Build)
* Người dùng đã có sẵn CPU hoặc GPU (*Ví dụ: "có sẵn chip i5 14600k cần build 20 triệu chơi game"*):
* Hệ thống tự động **khóa linh kiện có sẵn với giá 0 VNĐ**, giữ nguyên nền tảng Socket LGA1700, chọn Mainboard VRM dày dặn, tản nhiệt tháp đôi và **dồn 100% ngân sách 20 triệu lên thẳng Card đồ họa RTX 4060 Ti 8GB New**!

### 4.3. Cảnh báo an toàn & Đánh chặn xung đột (Hardware Guardrails)
* **Xung đột Socket:** Cảnh báo đỏ ngay lập tức nếu người dùng đòi cắm CPU Intel vào Bo mạch chủ AMD AM5.
* **Xung đột chuẩn RAM:** Ngăn chặn việc cắm RAM DDR4 vào khe cắm DDR5 trên bo mạch chủ mới.
* **Cảnh báo nguồn công suất ảo:** Phát hiện các dòng nguồn "cỏ" noname (Arrow, Vision...) thiếu linh kiện bảo vệ, ngăn chặn nguy cơ cháy nổ khi cắm card đồ họa nặng.

---

## 🛡️ 5. Kiến trúc Chịu Lỗi Kép (Dual-Engine Resilience)

Hệ thống được thiết kế theo tiêu chuẩn công nghiệp nhằm đảm bảo độ tin cậy 24/7:
* **Tầng 1 (Live AI Model):** Kết nối trực tiếp máy chủ Google qua mô hình **`gemini-3.5-flash`** thế hệ mới để viết bài luận phân tích FPS thực tế (CS2, Valorant, GTA 5, Black Myth Wukong) và mẹo thiết lập BIOS chuyên sâu.
* **Tầng 2 (Expert Heuristic Fallback):** Khi mất kết nối Internet hoặc API chạm ngưỡng hạn mức quota, hệ thống tự động kích hoạt **Bộ máy Tri thức Kỹ sư Chuyên gia nội bộ**. Toàn bộ dữ liệu kỹ thuật và bài tư vấn vẫn được xuất ra trơn tru mà **không bao giờ bị văng lỗi màu đỏ (Crash)**!

---

## 🚀 6. Hướng dẫn Cài đặt & Khởi chạy

### Bước 1: Yêu cầu môi trường
* Hệ điều hành: Windows 10/11, macOS, hoặc Linux.
* Python: Phiên bản **Python 3.10 trở lên** (Khuyên dùng Python 3.11).

### Bước 2: Cài đặt thư viện dependencies
```bash
git clone <URL_REPO_CUA_BAN>
cd pc_agent_system
pip install -r requirements.txt
```

### Bước 3: Cấu hình biến môi trường (`.env`)
Tạo file `.env` tại thư mục gốc của dự án:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```

### Bước 4: Khởi chạy ứng dụng

#### 🌐 Cách 1: Chạy Giao diện Web (Streamlit UI) — Khuyên Dùng
```bash
streamlit run run_ui.py
```
* Mở trình duyệt tại địa chỉ: **`http://localhost:8501`**.
* Giao diện phong cách thương mại điện tử hiện đại, tích hợp sidebar tra cứu CSDL linh kiện và mô tả kiến trúc Multi-Agent.

#### 💻 Cách 2: Chạy Giao diện Dòng Lệnh Tương Tác (Terminal CLI)
```bash
python run_cli.py
```
* Giao diện dòng lệnh chuẩn kỹ sư với bảng biểu phân màu trực quan của thư viện Rich.

---

## 🧪 7. Bộ Kiểm Thử Tự Động (Automation Testing)

Dự án trang bị bộ kiểm thử toàn diện bảo đảm chất lượng phần mềm:

### 7.1. Chạy Unit Tests bằng Pytest
```bash
pytest tests/ -v
```
```text
============================== test session starts ==============================
collected 5 items
tests/test_scenarios.py::test_psu_calculator PASSED                      [ 20%]
tests/test_scenarios.py::test_bottleneck_detection PASSED                [ 40%]
tests/test_scenarios.py::test_db_lookup PASSED                           [ 60%]
tests/test_scenarios.py::test_full_pc_build PASSED                       [ 80%]
tests/test_scenarios.py::test_spec_contract_parsing PASSED              [100%]
============================== 5 passed in 1.72s ===============================
```

### 7.2. Chạy Stress-Test 9 Kịch Bản Nhiễu Thực Tế Cực Đoan
```bash
python tests/test_noisy_inputs.py
```
```text
=====================================================================================
🏆 KẾT LUẬN: TẤT CẢ 9/9 TESTCASE NHIỄU & CỰC ĐOAN ĐỀU ĐẠT CHUẨN XUẤT SẮC!
=====================================================================================
- NOISE-01: Lắp bắp, ngập ngừng, lặp từ, sửa lời                  --> [PASS]
- NOISE-02: Sai chính tả nặng, Teencode, viết tắt cẩu thả        --> [PASS]
- NOISE-03: Kể chuyện lan man đời tư (mèo làm đổ nước, thưởng)   --> [PASS]
- NOISE-04: Nói cụt ngủn, thiếu 100% dữ kiện                     --> [PASS]
- NOISE-05: Đảo lộn thuật ngữ phần cứng                          --> [PASS]
- NOISE-06: Phiên âm tiếng Việt dị (rai dừn, sáu trăm oát)       --> [PASS]
- NOISE-07: Phần cứng ảo / Chip không có trong CSDL              --> [PASS]
- NOISE-08: Ngân sách phi lý (500k đòi 4K Ultra)                 --> [PASS]
- NOISE-09: Quá tải cực đoan (Celeron 250W đòi cắm RTX 5090)     --> [PASS]
```

---

## 📂 8. Cấu Trúc Thư Mục Dự Án

```text
pc_agent_system/
├── core/
│   ├── config.py                 # Quản lý cấu hình, biến môi trường, ẩn cảnh báo SDK
│   └── schemas.py                # Định nghĩa Pydantic Models & Data Contracts chuẩn hóa
├── data/
│   └── pc_parts_db.json          # Cơ sở dữ liệu phần cứng thực tế (CPU, GPU, Main, RAM, SSD...)
├── tools/                        # Bộ công cụ kỹ thuật độc lập (Agent Tools)
│   ├── db_lookup_tool.py         # Tra cứu CSDL & suy luận thông số động (Dynamic Spec Inference)
│   ├── psu_calculator_tool.py    # Tính toán điện năng đỉnh & tỷ lệ tải nguồn an toàn
│   ├── bottleneck_tool.py        # Đo lường tỷ lệ nghẽn cổ chai IPC
│   └── full_build_tool.py        # Thuật toán tổng hợp cấu hình 8 linh kiện đồng bộ
├── agents/                       # Mã nguồn 2 AI Agents tự chủ
│   ├── spec_analyst_agent.py     # Agent 1: Bóc tách ngôn ngữ tự nhiên, khử nhiễu, lập Brief
│   └── compatibility_agent.py    # Agent 2: Kỹ sư trưởng thẩm định tương thích & viết báo cáo
├── tests/                        # Bộ kiểm thử tự động
│   ├── test_scenarios.py         # 5 Unit Tests kiểm thử độc lập các Tools
│   └── test_noisy_inputs.py      # 9 Stress-Tests kịch bản nhiễu & tình huống cực đoan
├── orchestrator.py               # Bộ điều phối liên tác tử Multi-Agent Pipeline
├── run_cli.py                    # Giao diện dòng lệnh tương tác (Interactive CLI)
├── run_ui.py                     # Giao diện Web trực quan (Streamlit Dashboard)
├── DEPLOYMENT_GUIDE.md           # Bộ tài liệu hướng dẫn triển khai hoàn chỉnh (v2.5)
├── requirements.txt              # Danh sách thư viện phụ thuộc
├── .env.example                  # Mẫu cấu hình biến môi trường
└── README.md                     # Tài liệu giới thiệu dự án chuẩn GitHub
```

---

## 📜 9. Bản Quyền & Thông Tin Đề Tài

* **Đồ án môn học:** Trí Tuệ Nhân Tạo Ứng Dụng (AI Application / AI Agents)
* **Nhiệm vụ:** **Nhiệm vụ 13** — *Xây dựng tối thiểu 2 AI Agents cùng thực hiện công việc A (tự chọn) & Soạn tài liệu hướng dẫn triển khai hoàn chỉnh.*
* **Giấy phép:** [MIT License](LICENSE) — Tự do sử dụng, chỉnh sửa và phát triển cho mục đích học tập và nghiên cứu.
