import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX - BẢN NỀN TRẮNG SẠCH SẼ)
st.set_page_config(page_title="KẾT QUẢ GOM KHĂN NINH BÌNH", page_icon="🧣", layout="centered")

# Custom CSS cho theme Nền Trắng, Nhấn Navy & Mustard
st.markdown("""
    <style>
    /* Background tổng thể nền trắng, chữ đen/xám đậm */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* Tiêu đề chính, tiêu đề phụ & text nhấn */
    h1, h2, h3, .stTabs [data-baseweb="tab"] p, .highlight { color: #0B192C !important; font-weight: bold; }
    
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
    
    /* Card Thống kê (Giống phong cách Dashboard) */
    .metric-card { 
        background-color: #FFFFFF; border: 1px solid #E0E6ED; border-top: 5px solid #0B192C; 
        padding: 15px; border-radius: 8px; margin-bottom: 15px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-title { font-size: 16px; color: #0B192C; font-weight: bold; }
    .metric-value { font-size: 26px; font-weight: bold; color: #F4C430; }
    .metric-sub { font-size: 14px; color: #888888; margin-top: 5px; }
    
    /* Bảng */
    [data-testid="stDataFrame"] { background-color: #FFFFFF; }
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
    
    # Ép kiểu SĐT thành chuỗi, gọt số .0
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
                    st.markdown("---")
                    
                    st.markdown("<h4 class='highlight'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</h4>", unsafe_allow_html=True)
                    user_products = {p: ["✅" if "✅" in str(user_data.get(p, "")) else ""] for p in products}
                    df_user_prod = pd.DataFrame(user_products)
                    st.dataframe(df_user_prod, hide_index=True, use_container_width=True)
                    
                    # ---- XỬ LÝ FORMAT TIỀN TỆ ----
                    raw_tien = str(user_data.get('Số tiền', '0'))
                    tien_digits = re.sub(r'[^\d]', '', raw_tien) # Chỉ lấy số, bỏ hết chữ và ký tự đặc biệt
                    
                    if tien_digits:
                        tien_int = int(tien_digits)
                        tien_format = f"{tien_int:,}".replace(',', '.') + " VNĐ"
                    else:
                        tien_format = "Đang cập nhật"
                    # ------------------------------

                    st.markdown("<h4 class='highlight'>THÔNG TIN THANH TOÁN</h4>", unsafe_allow_html=True)
                    st.markdown(f"**💰 Số tiền cần thanh toán:** <span style='color:#F4C430; font-size:18px; font-weight:bold;'>{tien_format}</span>", unsafe_allow_html=True)
                    st.markdown(f"**⏳ Hạn chót chuyển khoản:** {user_data.get('Hạn chót chuyển khoản', 'Đang cập nhật')}")
                    st.markdown(f"**⏱️ Thời gian chuyển khoản còn lại:** {user_data.get('Thời gian còn lại', 'Đang cập nhật')}")
                    st.markdown(f"**💳 Trạng thái chuyển khoản:** {user_data.get('Chuyển khoản thành công', 'Đang cập nhật')}")
                    
                    st.markdown("---")
                    
                    st.markdown("<h4 class='highlight'>THÔNG TIN CHUYỂN KHOẢN</h4>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        import os
                        if os.path.exists("TTCK.jpg"):
                            # Đã fix lỗi TypeError bằng cách xài use_container_width thay cho use_column_width
                            st.image("TTCK.jpg", caption="Quét mã QR để thanh toán", use_container_width=True)
                        else:
                            st.warning("Đang cập nhật mã QR...")
                    with col2:
                        st.markdown("**NỘI DUNG CHUYỂN KHOẢN:**")
                        st.code(f"KHAN - {phone_input.strip()[-3:]}", language="text")
                        st.info("Vui lòng ghi chính xác nội dung để hệ thống tự động chốt đơn nhé!")
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
