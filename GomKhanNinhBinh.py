import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection
import os

# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX - BẢN NỀN TRẮNG SẠCH SẼ)
st.set_page_config(page_title="KẾT QUẢ GOM KHĂN NINH BÌNH", page_icon="🧣", layout="centered")

# Custom CSS cho theme Nền Trắng, Nhấn Navy & Mustard
st.markdown("""
    <style>
    /* Background tổng thể nền trắng, chữ đen/xám đậm */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* Tiêu đề chính, tiêu đề phụ & text nhấn */
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: #0B192C !important; font-weight: bold; }
    
    /* Nút bấm (Nền Mustard, chữ Navy) */
    .stButton>button { 
        background-color: #F4C430; color: #0B192C; 
        font-weight: bold; border-radius: 8px; border: none; width: 100%; 
    }
    .stButton>button:hover { background-color: #0B192C; color: #FFFFFF; border: none; }
    
    /* Ô nhập liệu */
    .stTextInput>div>div>input { background-color: #F8F9FA; color: #333333; border: 1px solid #0B192C; border-radius: 5px; }
    
    /* Tab active */
    .stTabs [aria-selected="true"] { border-bottom-color: #0B192C !important; }
    
    /* ================= THIẾT KẾ UI CHO KẾT QUẢ ================= */
    
    /* Khối Title Gradient (Navy -> Mustard) */
    .section-title { 
        background: linear-gradient(90deg, #0B192C 0%, #F4C430 100%); 
        color: white; 
        padding: 12px 15px; 
        border-radius: 8px 8px 0 0; 
        font-size: 16px; 
        font-weight: bold; 
        margin-top: 25px;
        margin-bottom: 0px;
        text-transform: uppercase;
    }
    
    /* Bảng HTML Custom nối liền với Title */
    .custom-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-bottom: 20px; 
        border: 1px solid #E0E6ED;
        border-top: none;
        border-radius: 0 0 8px 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .custom-table th { background-color: #1A2B4C; color: white; padding: 12px; text-align: center; font-size: 14px;}
    .custom-table th:first-child { text-align: left; }
    .custom-table td { padding: 12px; border-bottom: 1px solid #E0E6ED; text-align: center; font-weight: bold; color: #0B192C; }
    .custom-table td:first-child { text-align: left; font-weight: normal; color: #333333;}
    .custom-table tr:last-child td { border-bottom: none; }
    
    /* Style cho value phía sau dấu : */
    .highlight-val { color: #D4AF37; font-weight: bold; font-size: 16px;} /* Màu vàng đất đậm */
    .info-row { margin-bottom: 12px; font-size: 15px; border-bottom: 1px dashed #EEEEEE; padding-bottom: 8px;}
    
    /* =========================================================== */
    
    /* Card Thống kê */
    .metric-card { 
        background-color: #FFFFFF; border: 1px solid #E0E6ED; border-top: 5px solid #0B192C; 
        padding: 15px; border-radius: 8px; margin-bottom: 15px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-title { font-size: 16px; color: #0B192C; font-weight: bold; }
    .metric-value { font-size: 26px; font-weight: bold; color: #F4C430; }
    .metric-sub { font-size: 14px; color: #888888; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧣 KẾT QUẢ GOM KHĂN NINH BÌNH")

# 2. KẾT NỐI DỮ LIỆU
url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"

@st.cache_data(ttl=60) 
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip()
    if 'SDT full' in df.columns:
        df['SDT full'] = df['SDT full'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Đang có lỗi kết nối dữ liệu, bạn vui lòng thử lại sau nhé! (Lỗi: {e})")
    st.stop()

products = ["Bandana TTB", "Twilly TTB", "Bandana ĐMN", "Twilly ĐMN"]
total_limits = {"Bandana TTB": 20, "Twilly TTB": 40, "Bandana ĐMN": 20, "Twilly ĐMN": 40}

# 3. TẠO TABS
tab1, tab2, tab3 = st.tabs(["🔍 TRA CỨU KẾT QUẢ", "📊 ĐĂNG KÝ THÀNH CÔNG", "💰 CK THÀNH CÔNG"])

# ================= TAB 1 =================
with tab1:
    st.markdown("### Nhập thông tin để tra cứu")
    phone_input = st.text_input("Nhập số điện thoại của bạn (đã dùng đăng ký):", placeholder="Ví dụ: 0901234567")
    
    if st.button("KẾT QUẢ 🚀"):
        if phone_input:
            clean_input = phone_input.strip().lstrip('0')
            df['Phone_Compare'] = df['SDT full'].astype(str).str.lstrip('0')
            user_row = df[df['Phone_Compare'] == clean_input]
            
            if not user_row.empty:
                user_data = user_row.iloc[0]
                is_success = str(user_data.get('Đăng ký thành công', '')).strip() == '✅'
                
                if is_success:
                    st.success("🎉 CHÚC MỪNG BẠN ĐÃ ĐĂNG KÝ THÀNH CÔNG!")
                    
                    # ---- BẢNG SẢN PHẨM CUSTOM HTML ----
                    table_html = "<div class='section-title'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</div><table class='custom-table'>"
                    table_html += "<tr><th>Sản Phẩm</th><th>Lấy</th></tr>"
                    for p in products:
                        tick = "✅" if "✅" in str(user_data.get(p, "")) else ""
                        table_html += f"<tr><td>{p}</td><td>{tick}</td></tr>"
                    table_html += "</table>"
                    
                    st.markdown(table_html, unsafe_allow_html=True)
                    
                    # ---- XỬ LÝ FORMAT TIỀN TỆ ----
                    raw_tien = str(user_data.get('Số tiền', '0'))
                    tien_digits = re.sub(r'[^\d]', '', raw_tien) 
                    
                    if tien_digits:
                        tien_format = f"{int(tien_digits):,}".replace(',', '.') + " VNĐ"
                    else:
                        tien_format = "Đang cập nhật"
                    # ------------------------------

                    # ---- KHỐI THÔNG TIN THANH TOÁN (GỘP CHUNG QR & TEXT) ----
                    st.markdown("<div class='section-title'>THÔNG TIN THANH TOÁN</div>", unsafe_allow_html=True)
                    st.markdown("<div style='border: 1px solid #E0E6ED; border-top:none; border-radius: 0 0 8px 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); background-color: #FAFAFA;'>", unsafe_allow_html=True)
                    
                    # Chia cột Layout
                    col_info, col_qr = st.columns([1.3, 1])
                    
                    with col_info:
                        st.markdown(f"<div class='info-row'>**💰 Số tiền cần thanh toán:** <span class='highlight-val'>{tien_format}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='info-row'>**⏳ Hạn chót chuyển khoản:** <span class='highlight-val'>{user_data.get('Hạn chót chuyển khoản', 'Đang cập nhật')}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='info-row'>**⏱️ Thời gian còn lại:** <span class='highlight-val'>{user_data.get('Thời gian còn lại', 'Đang cập nhật')}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='info-row'>**💳 Trạng thái chuyển khoản:** <span class='highlight-val'>{user_data.get('Chuyển khoản thành công', 'Đang cập nhật')}</span></div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top: 20px; margin-bottom: 5px;'>**NỘI DUNG CHUYỂN KHOẢN CỦA BẠN:**</div>", unsafe_allow_html=True)
                        st.code(f"KHAN - {phone_input.strip()[-3:]}", language="text")
                        st.info("Vui lòng ghi chính xác nội dung để hệ thống tự động chốt đơn nhé!")

                    with col_qr:
                        if os.path.exists("TTCK.jpg"):
                            st.image("TTCK.jpg", caption="Quét mã QR để thanh toán", use_container_width=True)
                        else:
                            st.warning("Đang cập nhật mã QR...")
                            
                    # Đóng div khối thanh toán
                    st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.error("RẤT TIẾC BÀ HONG CÓ ĐĂNG KÝ THÀNH CÔNG ỜI 😭")
            else:
                st.warning("Không tìm thấy số điện thoại này trong hệ thống. Vui lòng kiểm tra lại!")
        else:
            st.warning("Bạn chưa nhập số điện thoại kìa!")

# ================= TAB 2 =================
with tab2:
    st.markdown("### 📊 TIẾN ĐỘ ĐĂNG KÝ")
    
    df_registered = df[df['Đăng ký thành công'].astype(str).str.contains('✅', na=False)]
    col1, col2 = st.columns(2)
    
    for i, p in enumerate(products):
        reg_count = len(df_registered[df_registered[p].astype(str).str.contains('✅', na=False)])
        total = total_limits[p]
        rem_count = total - reg_count if (total - reg_count) > 0 else 0
        
        card_html = f"""
        <div class="metric-card">
            <div class="metric-title">{p}</div>
            <div class="metric-value">{reg_count} <span style="font-size:14px; color:#A0B2C6;">/ {total}</span></div>
            <div class="metric-sub">Còn lại: {rem_count} slot</div>
        </div>
        """
        if i % 2 == 0:
            col1.markdown(card_html, unsafe_allow_html=True)
        else:
            col2.markdown(card_html, unsafe_allow_html=True)

# ================= TAB 3 =================
with tab3:
    st.markdown("### 💰 TỔNG HỢP CHỐT ĐƠN")
    
    df_ck = df[df['Chuyển khoản thành công'].astype(str).str.contains('✅ Đã nhận tiền, CHỐT ĐƠN NHA!', na=False, regex=False)]
    
    table_data = {
        "Phân loại": ["Tổng cộng", "Nhận tại sự kiện", "Ship về nhà"]
    }
    
    for p in products:
        df_ck_p = df_ck[df_ck[p].astype(str).str.contains('✅', na=False)]
        
        tot = len(df_ck_p)
        event = len(df_ck_p[df_ck_p['Nơi nhận'].astype(str).str.strip() == "Nhận tại Love at first sight 29/8 ở Hà Nội"])
        ship = len(df_ck_p[df_ck_p['Nơi nhận'].astype(str).str.strip() == "Ship về nhà"])
        
        table_data[p] = [tot, event, ship]
    
    df_tab3 = pd.DataFrame(table_data)
    st.dataframe(df_tab3, hide_index=True, use_container_width=True)
