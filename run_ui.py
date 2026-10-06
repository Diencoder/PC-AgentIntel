import streamlit as st
import json
from orchestrator import PCAgentOrchestrator

st.set_page_config(
    page_title="PC-AgentIntel | Tư Vấn Phần Cứng PC",
    page_icon="💻",
    layout="wide"
)

# Tối giản hóa CSS chuẩn phong cách trang công nghệ thương mại hiện đại
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    .header-sub {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 24px;
    }
    
    .badge-safe { background-color: #10B981; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .badge-warn { background-color: #F59E0B; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .badge-danger { background-color: #EF4444; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        transition: background-color 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Tiêu đề sản phẩm thương mại thanh lịch
st.markdown('<div class="header-title">💻 PC-AgentIntel</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Hệ thống Tư Vấn Cấu Hình & Kiểm Định Tương Thích Phần Cứng Máy Tính</div>', unsafe_allow_html=True)

# SIDEBAR: Nơi dành riêng cho Thầy giáo xem thông tin kỹ thuật 2 Agent & CSDL
st.sidebar.markdown("### 🤖 Kiến Trúc Multi-Agent")
st.sidebar.markdown("""
Hệ thống vận hành bởi **2 AI Agents tự chủ**:
- **Agent 1 (Spec & Intent Analyst):** Bóc tách ngôn ngữ tự nhiên, teencode, nhận diện ngân sách & mục đích, lập hồ sơ Data Contract.
- **Agent 2 (Compatibility Engineer):** Tra cứu CSDL linh kiện, chạy Tools tính công suất điện & nghẽn cổ chai, kiểm định tương thích 5 sao.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Cơ Sở Dữ Liệu Thực Tế (CSDL)")
st.sidebar.markdown("""
- **Card đồ họa (VGA):** 29 dòng (GTX 1050 Ti $\\rightarrow$ RTX 5090)
- **Vi xử lý (CPU):** 24 dòng (Core 2 Quad $\\rightarrow$ Ultra 9 / 9800X3D)
- **Bo mạch chủ:** H610, B760, Z790, B650, X670
- **Bộ nhớ RAM:** DDR4 3200 $\\rightarrow$ DDR5 6000 CL30
- **Ổ cứng SSD:** NVMe PCIe Gen 4x4 (3500MB/s - 7450MB/s)
- **Bộ nguồn (PSU):** 450W $\\rightarrow$ 1000W ATX 3.0 PCIe 5.0
- **Tản nhiệt & Vỏ Case:** Tản khí CR1000, AIO 240/360 LCD, Case Bể Cá
""")

# Ô nhập liệu duy nhất
user_query = st.text_area(
    "Nhập yêu cầu cấu hình của bạn:",
    value="",
    height=100,
    placeholder="Ví dụ: 'tôi muốn build pc ngân sách 15 triệu chơi game' hoặc 'tôi có chip i5 12400f nguồn 550w, có 5 triệu tìm card cũ'..."
)

btn_run = st.button("🚀 Gửi Yêu Cầu Tư Vấn", type="primary")

if btn_run and user_query.strip():
    orchestrator = PCAgentOrchestrator()
    
    with st.spinner("Đang tính toán và thẩm định cấu hình tối ưu..."):
        contract = orchestrator.agent1.analyze(user_query)
        
        # 1. KIỂM TRA LỖI XUNG ĐỘT PHẦN CỨNG (GUARDRAILS)
        if contract.warning_flag and any(w in contract.warning_flag for w in ["LỖI TƯƠNG THÍCH", "LỖI CHUẨN", "CẢNH BÁO NGUỒN CÔNG SUẤT ẢO"]):
            st.error(f"### ⛔ CẢNH BÁO XUNG ĐỘT LINH KIỆN\n\n{contract.warning_flag}")
            if "LỖI CHUẨN KHE CẮM RAM" in contract.warning_flag:
                st.warning("💡 **Giải pháp:** Mua RAM chuẩn DDR5 hoặc đổi bo mạch chủ sang phiên bản hỗ trợ DDR4 (Ví dụ: B760M DDR4) để tận dụng lại RAM cũ.")
            elif "LỖI TƯƠNG THÍCH NGHIÊM TRỌNG" in contract.warning_flag:
                st.warning("💡 **Giải pháp:** CPU Intel bắt buộc đi cùng Main Intel (H610, B760). Bo mạch chủ AMD bắt buộc gắn CPU AMD Ryzen (AM4/AM5).")
            else:
                st.warning("💡 **Khuyến nghị:** Cần nâng cấp bộ nguồn chuẩn công suất thực 80 Plus trước khi cắm card đồ họa rời công suất cao.")
        
        # 2. KIỂM TRA THIẾU THÔNG TIN
        elif (not contract.current_cpu and not contract.current_psu_watt and not contract.budget_vnd):
            st.warning("""
            👋 **Yêu cầu còn thiếu thông tin để tư vấn.**
            
            Vui lòng bổ sung thêm:
            1. 💰 **Ngân sách** dự kiến (Ví dụ: *5 triệu, 15 triệu...*)
            2. ⚡ **Linh kiện đang có sẵn** nếu có (Ví dụ: *nguồn 550W, chip i5 12400f* hoặc *ráp nguyên dàn mới*)
            3. 🎯 **Mục đích chính** (Ví dụ: *chơi CS2, Valorant*, *làm đồ họa 3D*...)
            """)
            
        else:
            report = orchestrator.agent2.audit(contract, verbose=False)
            budget_disp = f"{contract.budget_vnd:,} đ" if contract.budget_vnd else "Chưa xác định"

            st.markdown("---")
            
            # PHẦN 1: BÁO CÁO PHÂN TÍCH NHU CẦU & CHIẾN LƯỢC
            st.markdown("### 🎯 Phân Tích Nhu Cầu & Chiến Lược Cấu Hình")
            if contract.target_component == 'BUILD_WITH_EXISTING':
                owned_desc = ', '.join([f"{k.upper()}: {v}" for k, v in contract.already_owned_parts.items()])
                loai_hinh_str = f"Lắp ráp hoàn thiện quanh linh kiện có sẵn ({owned_desc})"
            elif contract.target_component == 'FULL_PC':
                loai_hinh_str = "Ráp trọn bộ PC mới (8 linh kiện)"
            else:
                loai_hinh_str = "Nâng cấp Card đồ họa (GPU)"
            st.markdown(f"- **Mục đích:** `{contract.purpose}` | **Loại hình:** `{loai_hinh_str}` | **Ngân sách:** `{budget_disp}`")
            st.info(f"**Định hướng kỹ thuật:**\n\n{report.agent1_brief}")

            st.markdown("---")
            
            # PHẦN 2: KẾT QUẢ ĐỀ XUẤT CẤU HÌNH & THẨM ĐỊNH TƯƠNG THÍCH
            is_build_mode = contract.target_component in ["FULL_PC", "BUILD_WITH_EXISTING"]
            if is_build_mode and report.full_pc_build:
                build = report.full_pc_build
                title_desc = f"### 💻 Cấu Hình Đề Xuất (Đã Khấu Trừ Linh Kiện Có Sẵn | Ngân Sách Đầu Tư {budget_disp})" if contract.target_component == "BUILD_WITH_EXISTING" else f"### 💻 Cấu Hình 8 Linh Kiện Đề Xuất (Tối Ưu Ngân Sách {budget_disp})"
                st.markdown(title_desc)
                
                # Bảng linh kiện
                parts_data = [
                    {
                        "Hạng Mục Linh Kiện": p["category"],
                        "Tên Linh Kiện Đề Xuất": p["item"],
                        "Thông Số Kỹ Thuật": p.get("spec", "Đồng bộ hệ thống"),
                        "Giá Tham Khảo": f"{p['price']:,} đ" if p['price'] > 0 else "0 đ (Đã có sẵn)"
                    }
                    for p in build["parts"]
                ]
                st.dataframe(parts_data, use_container_width=True, hide_index=True)
                if contract.target_component == "BUILD_WITH_EXISTING":
                    st.markdown(f"### 👉 Tổng Chi Phí Đầu Tư Thêm: `{build['total_cost']:,} VNĐ` *(Đã trừ chi phí linh kiện có sẵn 0đ, dồn 100% ngân sách cho các linh kiện còn lại)*")
                else:
                    st.markdown(f"### 👉 Tổng Chi Phí Dự Kiến: `{build['total_cost']:,} VNĐ` *(Trọn bộ đầy đủ 8 món, cắm điện là dùng)*")
                
                # Bảng kiểm định tương thích
                comp_checks = build.get("compatibility_checks", [])
                if comp_checks:
                    st.markdown("#### 🛡️ Bảng Kiểm Định Tương Thích Đồng Bộ Toàn Hệ Thống")
                    comp_data = [
                        {
                            "Hạng Mục Kiểm Định": c["aspect"],
                            "Trạng Thái": f"✔ {c['status']}",
                            "Chi Tiết Kỹ Thuật": c["detail"]
                        }
                        for c in comp_checks
                    ]
                    st.dataframe(comp_data, use_container_width=True, hide_index=True)
                    
                # Lời tư vấn chuyên sâu
                st.markdown("#### 💡 Bài Tư Vấn & Đánh Giá Kỹ Thuật Chuyên Sâu")
                st.success(report.agent2_consultation)
                
            else:
                # Nâng cấp card đồ họa
                st.markdown(f"### 🎮 Bảng So Sánh Card Đồ Họa Tối Ưu")
                
                if report.safety_alerts:
                    for alert in report.safety_alerts:
                        st.error(alert)

                for rec in report.recommendations:
                    with st.container(border=True):
                        r_col1, r_col2, r_col3 = st.columns([3, 2, 2])
                        with r_col1:
                            st.subheader(f"🎮 {rec.gpu.model}")
                            st.markdown(f"**Giá tham khảo:** `{rec.gpu.market_price_used_vnd:,} VNĐ`")
                            st.caption(f"💡 {rec.quick_review}")
                        
                        with r_col2:
                            st.markdown("**Tải Nguồn (PSU):**")
                            if rec.psu_evaluation.status == "SAFE":
                                st.markdown(f"<span class='badge-safe'>AN TOÀN ({rec.psu_evaluation.load_percentage}%)</span>", unsafe_allow_html=True)
                            elif rec.psu_evaluation.status == "WARNING":
                                st.markdown(f"<span class='badge-warn'>CẢNH BÁO ({rec.psu_evaluation.load_percentage}%)</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span class='badge-danger'>NGUY HIỂM ({rec.psu_evaluation.load_percentage}%)</span>", unsafe_allow_html=True)
                            st.caption(rec.psu_evaluation.message)

                        with r_col3:
                            st.markdown("**Nghẽn Cổ Chai CPU:**")
                            if rec.bottleneck_evaluation.bottleneck_risk == "LOW":
                                st.markdown("<span class='badge-safe'>LÝ TƯỞNG (<8% nghẽn)</span>", unsafe_allow_html=True)
                            elif rec.bottleneck_evaluation.bottleneck_risk == "MODERATE":
                                st.markdown("<span class='badge-warn'>NGHẼN NHẸ (15-20%)</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("<span class='badge-danger'>NGHẼN NẶNG (>40%)</span>", unsafe_allow_html=True)
                            st.caption(rec.bottleneck_evaluation.explanation)

                st.markdown("#### 💡 Lời Khuyên & Đánh Giá Kỹ Thuật Chuyên Sâu")
                st.success(report.agent2_consultation)
