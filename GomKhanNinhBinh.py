import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX)
st.set_page_config(page_title="KẾT QUẢ GOM KHĂN NINH BÌNH", page_icon="🧣", layout="centered")

# Custom CSS cho theme Navy & Mustard
st.markdown("""
    <style>
    /* Background tổng thể */
    .stApp { background-color: #0B192C; color: #E0E6ED; }
    
    /* Tiêu đề & text nhấn */
    h1, h2, h3, .stTabs [data-baseweb="tab"] p, .highlight { color: #F4C430 !important; font-weight: bold; }
    
    /* Nút bấm */
    .stButton>button { 
        background-color: #F4C430; color: #0B192C; 
        font-weight: bold; border-radius: 8px; border: none; width: 100%; 
    }
    .stButton>button:hover { background-color: #FFD700; color: #000000; border: none; }
    
    /* Ô nhập liệu */
    .stTextInput>div>div>input { background-color: #1A2B4C; color: #FFF; border: 1px solid #F4C430; }
    
    /* Tab active */
    .stTabs [aria-selected="true"] { border-bottom-color: #F4C430 !important; }
    
    /* Card Thống kê */
    .metric-card { 
        background-color: #1A2B4C; border-left: 5px solid #F4C430; 
        padding: 15px; border-radius: 8px; margin-bottom: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-title { font-size: 16px; color: #A0B2C6; }
    .metric-value { font-size: 24px; font-weight: bold; color: #F4C430; }
    .metric-sub { font-size: 14px; color: #4CAF50; margin-top: 5px; }
    
    /* Bảng */
    [data-testid="stDataFrame"] { background-color: #1A2B4C; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧣 KẾT QUẢ GOM KHĂN NINH BÌNH")

# 2. KẾT NỐI DỮ LIỆU
url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"

@st.cache_data(ttl=60) # Tự động làm mới mỗi 60 giây để tránh lag/quá tải API
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)
    # Ép kiểu SĐT thành chuỗi để giữ nguyên số 0
    if 'SDT full' in df.columns:
        df['SDT full'] = df['SDT full'].astype(str).str.replace(".0", "", regex=False).str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Đang có lỗi kết nối dữ liệu, bạn vui lòng thử lại sau nhé!")
    st.stop()

# Danh sách các cột sản phẩm
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
            phone_input = phone_input.strip()
            # Lọc data theo sdt
            user_row = df[df['SDT full'] == phone_input]
            
            if not user_row.empty:
                user_data = user_row.iloc[0] # Lấy dòng đầu tiên khớp
                
                # Kiểm tra ✅ Đăng ký thành công
                is_success = str(user_data.get('Đăng ký thành công', '')).strip() == '✅'
                
                if is_success:
                    st.success("🎉 CHÚC MỪNG BẠN ĐÃ ĐĂNG KÝ THÀNH CÔNG!")
                    st.markdown("---")
                    
                    # Bảng Sản phẩm
                    st.markdown("<h4 class='highlight'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</h4>", unsafe_allow_html=True)
                    user_products = {p: ["✅" if "✅" in str(user_data.get(p, "")) else ""] for p in products}
                    df_user_prod = pd.DataFrame(user_products)
                    st.dataframe(df_user_prod, hide_index=True, use_container_width=True)
                    
                    # Thông tin thanh toán
                    st.markdown("<h4 class='highlight'>THÔNG TIN THANH TOÁN</h4>", unsafe_allow_html=True)
                    st.markdown(f"**💰 Số tiền cần thanh toán:** {user_data.get('Số tiền', 'Đang cập nhật')}")
                    st.markdown(f"**⏳ Hạn chót chuyển khoản:** {user_data.get('Hạn chót chuyển khoản', 'Đang cập nhật')}")
                    st.markdown(f"**⏱️ Thời gian chuyển khoản còn lại:** {user_data.get('Thời gian còn lại', 'Đang cập nhật')}")
                    st.markdown(f"**💳 Trạng thái chuyển khoản:** {user_data.get('Chuyển khoản thành công', 'Đang cập nhật')}")
                    
                    st.markdown("---")
                    
                    # Hướng dẫn & QR Code
                    st.markdown("<h4 class='highlight'>THÔNG TIN CHUYỂN KHOẢN</h4>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image("TTCK.jpg", caption="Quét mã QR để thanh toán", use_column_width=True)
                    with col2:
                        st.markdown("**NỘI DUNG CHUYỂN KHOẢN:**")
                        st.code(f"KHAN - {phone_input[-3:]}", language="text")
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
    
    # Chỉ tính những người có chữ ✅ ở cột Đăng ký thành công
    df_registered = df[df['Đăng ký thành công'].astype(str).str.contains('✅', na=False)]
    
    # Chia làm 2 cột để hiện Card cho đẹp
    col1, col2 = st.columns(2)
    
    for i, p in enumerate(products):
        # Đếm số lượng ✅ của từng cột sản phẩm trong tập df_registered
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
    
    # Lọc những người đã CK thành công
    df_ck = df[df['Chuyển khoản thành công'].astype(str).str.contains('✅ Đã nhận tiền, CHỐT ĐƠN NHA!', na=False, regex=False)]
    
    # Khởi tạo data cho bảng
    table_data = {
        "Phân loại": ["Tổng cộng", "Nhận tại sự kiện", "Ship về nhà"]
    }
    
    for p in products:
        # Lọc những ai trong df_ck có mua sản phẩm p
        df_ck_p = df_ck[df_ck[p].astype(str).str.contains('✅', na=False)]
        
        # Đếm
        tot = len(df_ck_p)
        event = len(df_ck_p[df_ck_p['Nơi nhận'].astype(str).str.strip() == "Nhận tại Love at first sight 29/8 ở Hà Nội"])
        ship = len(df_ck_p[df_ck_p['Nơi nhận'].astype(str).str.strip() == "Ship về nhà"])
        
        table_data[p] = [tot, event, ship]
    
    df_tab3 = pd.DataFrame(table_data)
    st.dataframe(df_tab3, hide_index=True, use_container_width=True)
