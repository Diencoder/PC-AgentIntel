import re
import streamlit as st
import json
from orchestrator import PCAgentOrchestrator

st.set_page_config(
    page_title="PC-AgentIntel | Trí Tuệ Nhân Tạo Tư Vấn Phần Cứng PC",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Thiết kế giao diện hiện đại phong cách AI Tech Portal
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Ẩn hoàn toàn Sidebar */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    .block-container {
        max-width: 1040px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        margin: 0 auto !important;
    }
    
    /* Hero Header */
    .hero-container {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(99, 102, 241, 0.08));
        color: #2563EB;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(37, 99, 235, 0.2);
        margin-bottom: 12px;
    }
    
    .badge-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 10px #10B981;
        display: inline-block;
    }
    
    .hero-title-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    
    .hero-icon {
        font-size: 2.7rem;
        line-height: 1;
        display: inline-block;
    }
    
    .hero-title-text {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0F172A 0%, #1E40AF 50%, #4338CA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    .hero-sub {
        font-size: 1.08rem;
        color: #475569;
        max-width: 720px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.6;
    }
    
    /* Stats Row */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
        box-shadow: 0 8px 18px rgba(37,99,235,0.08);
    }
    
    .stat-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }
    
    .stat-label {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 2px;
    }
    
    /* Bento Grid */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-top: 2rem;
    }
    
    .bento-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    
    .bento-card:hover {
        transform: translateY(-3px);
        border-color: #60A5FA;
        box-shadow: 0 12px 24px rgba(37,99,235,0.08);
    }
    
    .bento-icon {
        font-size: 2rem;
        margin-bottom: 12px;
        display: inline-block;
    }
    
    .bento-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }
    
    .bento-desc {
        font-size: 0.88rem;
        color: #64748B;
        line-height: 1.55;
    }
    
    .badge-safe { background-color: #10B981; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .badge-warn { background-color: #F59E0B; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .badge-danger { background-color: #EF4444; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    
    /* Button primary */
    .main-btn div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        font-weight: 600;
        font-size: 1.05rem;
        border-radius: 10px;
        border: none;
        padding: 14px 28px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37,99,235,0.25);
        transition: all 0.2s ease;
    }
    .main-btn div.stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 18px rgba(37,99,235,0.35);
        transform: translateY(-1px);
    }
    
    /* Quick chip buttons */
    .chip-btn div.stButton > button {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9999px !important;
        padding: 6px 12px !important;
        transition: all 0.2s ease !important;
    }
    .chip-btn div.stButton > button:hover {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border-color: #93C5FD !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">
        <span class="badge-dot"></span>
        <span>✨ NEXT-GEN AI HARDWARE ARCHITECT • GEMINI 3.5 FLASH</span>
    </div>
    <div class="hero-title-wrapper">
        <span class="hero-icon">💻</span>
        <span class="hero-title-text">PC-AgentIntel</span>
    </div>
    <div class="hero-sub">
        Chuyên gia AI đa tác tử phân tích nhu cầu phần cứng, tính công suất tải nguồn thực tế, đo nghẽn cổ chai và tối ưu cấu hình 8 món bám sát giá thị trường Việt Nam.
    </div>
</div>
""", unsafe_allow_html=True)

# Stat Cards Row
st.markdown("""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-value">🚀 29+ Dòng VGA</div>
        <div class="stat-label">GTX 1050 Ti ➔ RTX 5090</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">🧠 24+ Dòng CPU</div>
        <div class="stat-label">Intel Gen 12-14 • AM4/AM5</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">⚡ Headroom ≥ 20%</div>
        <div class="stat-label">Chống quá tải & sập nguồn</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">🛡️ Zero-Conflict</div>
        <div class="stat-label">Khóa Socket & DDR4/DDR5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Ô nhập liệu duy nhất
user_query = st.text_area(
    "Nhập yêu cầu cấu hình của bạn:",
    value="",
    height=85,
    placeholder="Ví dụ: 'tôi muốn build pc ngân sách 15 triệu chơi game' hoặc 'tôi có chip i5 12400f nguồn 550w, có 5 triệu tìm card cũ'..."
)

st.markdown('<div class="main-btn">', unsafe_allow_html=True)
btn_run = st.button("🚀 Gửi Yêu Cầu Tư Vấn AI", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

if btn_run and user_query.strip():
    
    orchestrator = PCAgentOrchestrator()
    
    with st.spinner("🤖 Đang điều phối Multi-Agent & 4 Tools tính toán tương thích tối ưu..."):
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
                st.table(parts_data)
                
                # Tổng kết tài chính & kỹ thuật
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    cost_val = build.get('actual_cost_vnd', build.get('total_cost', 0))
                    st.metric("Tổng Chi Phí Cần Chi", f"{cost_val:,} đ")
                with m_col2:
                    st.metric("Độ Tương Thích Socket/RAM", "100% Hoàn Hảo", delta="Đạt chuẩn")
                with m_col3:
                    # Xác định công suất nguồn an toàn từ linh kiện
                    psu_watt_val = build.get('min_psu_watt')
                    if not psu_watt_val:
                        for p in build.get("parts", []):
                            if "Nguồn" in p.get("category", "") or "PSU" in p.get("category", ""):
                                m = re.search(r'(\d+)\s*W', p.get("item", ""), re.IGNORECASE) or re.search(r'(\d+)', p.get("item", ""))
                                if m:
                                    psu_watt_val = m.group(1)
                                    break
                    psu_disp = f"{psu_watt_val}W" if psu_watt_val else "Chuẩn 80 Plus"
                    st.metric("Tải Nguồn Đề Xuất", psu_disp, delta="Headroom an toàn")
                    
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

else:
    # HIỂN THỊ KHI CHƯA SUBMIT: Bento Grid Tính Năng Nổi Bật (Tạo sự sống động, hấp dẫn)
    st.markdown("""
    <div class="bento-grid">
        <div class="bento-card">
            <div class="bento-icon">⚡</div>
            <div class="bento-title">Đo Tải Nguồn Chuẩn Xác (PSU)</div>
            <div class="bento-desc">
                Tính toán tổng TDP điện áp thực tế giữa CPU, GPU và linh kiện ngoại vi, tự động dự phòng Headroom ≥ 20% chống quá tải sập nguồn.
            </div>
        </div>
        <div class="bento-card">
            <div class="bento-icon">⚖️</div>
            <div class="bento-title">Kiểm Soát Nghẽn Cổ Chai</div>
            <div class="bento-desc">
                Đánh giá độ cân bằng hiệu năng vi xử lý và card đồ họa. Đảm bảo GPU khai thác 100% công suất trong game mà không bị CPU kìm hãm.
            </div>
        </div>
        <div class="bento-card">
            <div class="bento-icon">🔄</div>
            <div class="bento-title">Hybrid Build Thông Minh</div>
            <div class="bento-desc">
                Tận dụng linh kiện bạn đang có sẵn (gán giá 0đ), chỉ dồn ngân sách vào các món còn thiếu và khóa chặt Socket LGA1700 / AM5.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
