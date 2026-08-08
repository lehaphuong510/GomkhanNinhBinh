import streamlit as st
import pandas as pd
import re
import os
import base64
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(page_title="KẾT QUẢ GOM KHĂN NINH BÌNH", page_icon="🧣", layout="centered")

# Hàm mã hóa ảnh sang Base64 để nhúng thẳng vào HTML (Khắc phục khe hở)
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

qr_base64 = get_image_base64("TTCK.jpg")

# Custom CSS cho theme Nền Trắng, Nhấn Navy & Mustard
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: #0B192C !important; font-weight: bold; }
    
    .stButton>button { 
        background-color: #F4C430; color: #0B192C; 
        font-weight: bold; border-radius: 8px; border: none; width: 100%; 
    }
    .stButton>button:hover { background-color: #0B192C; color: #FFFFFF; border: none; }
    
    .stTextInput>div>div>input { background-color: #F8F9FA; color: #333333; border: 1px solid #0B192C; border-radius: 5px; }
    .stTabs [aria-selected="true"] { border-bottom-color: #0B192C !important; }
    
    /* ================= THIẾT KẾ BẢNG & TEXT CUSTOM ================= */
    .section-title { 
        background: linear-gradient(90deg, #0B192C 0%, #F4C430 100%); 
        color: white; 
        padding: 12px 15px; 
        border-radius: 8px 8px 0 0; 
        font-size: 16px; 
        font-weight: bold; 
        margin-top: 25px;
        text-transform: uppercase;
    }
    
    .custom-table { 
        width: 100%; 
        border-collapse: separate; 
        border-spacing: 0;
        margin-bottom: 20px; 
        border: 1px solid #E0E6ED;
        border-top: none;
        border-radius: 0 0 8px 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        overflow: hidden;
    }
    .custom-table thead tr { background-color: #1A2B4C; } 
    .custom-table th { color: white; padding: 12px 14px; text-align: center; font-size: 15px; border: none; }
    .custom-table th:first-child { text-align: left; }
    .custom-table td { padding: 14px; border-bottom: 1px solid #EEEEEE; border-right: 1px solid #EEEEEE; text-align: center; font-weight: bold; color: #0B192C; background-color: #FFFFFF;}
    .custom-table td:first-child { text-align: left; color: #0B192C; }
    .custom-table td:last-child { border-right: none; }
    .custom-table tr:last-child td { border-bottom: none; }
    
    .custom-tick { 
        font-size: 20px; 
        font-weight: 900; 
        background: -webkit-linear-gradient(45deg, #0B192C, #F4C430); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }
    
    /* ================= KHỐI THANH TOÁN (FLEXBOX) ================= */
    .payment-box {
        display: flex;
        flex-wrap: wrap;
        border: 1px solid #E0E6ED; 
        border-top: none; 
        border-radius: 0 0 8px 8px; 
        padding: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        background-color: #FAFAFA; 
        margin-bottom: 25px;
    }
    .payment-info { flex: 1.3; min-width: 250px; padding-right: 15px; }
    .payment-qr { flex: 1; min-width: 200px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    .payment-qr img { max-width: 100%; border-radius: 8px; border: 1px solid #EEEEEE; }
    .qr-caption { font-size: 13px; color: #888; margin-top: 8px;}
    
    .highlight-val { color: #D4AF37; font-weight: bold; font-size: 16px;} 
    .info-row { margin-bottom: 15px; font-size: 15px; border-bottom: 1px dashed #EEEEEE; padding-bottom: 10px;}
    
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

@st.cache_data(ttl=15) 
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
            
            # Lấy tất cả các dòng khớp với số điện thoại
            matched_rows = df[df['Phone_Compare'] == clean_input]
            
            if not matched_rows.empty:
                # Nếu có BẤT KỲ dòng nào Đăng ký thành công -> Tính là thành công
                is_success = matched_rows['Đăng ký thành công'].astype(str).str.contains('✅').any()
                
                if is_success:
                    # Lấy nickname (ưu tiên dòng đầu tiên có chữ)
                    nicknames = matched_rows['Nickname'].astype(str).replace('nan', '')
                    valid_nicks = nicknames[nicknames.str.strip() != '']
                    nickname = valid_nicks.iloc[0].strip() if len(valid_nicks) > 0 else "BẠN"
                    
                    st.success(f"🎉 CHÚC MỪNG {nickname.upper()} ĐÃ ĐĂNG KÝ THÀNH CÔNG!")
                    
                    # ---- GỘP SẢN PHẨM ----
                    table_html = "<div class='section-title'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</div>"
                    table_html += "<table class='custom-table'><thead><tr><th>Sản Phẩm</th><th>Số Lượng</th></tr></thead><tbody>"
                    
                    for p in products:
                        # Đếm tổng số lượng ✅ của sản phẩm này trong tất cả các dòng của khách
                        count = matched_rows[p].astype(str).str.contains('✅').sum()
                        val_display = f"<span class='custom-tick'>{count}</span>" if count > 0 else ""
                        table_html += f"<tr><td>{p}</td><td>{val_display}</td></tr>"
                    table_html += "</tbody></table>"
                    
                    st.markdown(table_html, unsafe_allow_html=True)
                    
                    # ---- GỘP TỔNG TIỀN ----
                    total_tien = 0
                    for tien_str in matched_rows['Số tiền'].astype(str):
                        tien_digits = re.sub(r'[^\d]', '', tien_str)
                        if tien_digits:
                            total_tien += int(tien_digits)
                            
                    tien_format = f"{total_tien:,}".replace(',', '.') + " VNĐ" if total_tien > 0 else "Đang cập nhật"
                    
                    # Lấy Hạn chót & Thời gian từ dòng thành công đầu tiên
                    first_success = matched_rows[matched_rows['Đăng ký thành công'].astype(str).str.contains('✅')].iloc[0]
                    han_chot = first_success.get('Hạn chót chuyển khoản', 'Đang cập nhật')
                    tg_con = first_success.get('Thời gian còn lại', 'Đang cập nhật')
                    
                    # Xử lý Trạng thái CK: Nếu có 1 bill nào đang nợ thì báo Đang Cập Nhật
                    statuses = matched_rows['Chuyển khoản thành công'].astype(str).tolist()
                    if any("ĐANG CẬP NHẬT" in s for s in statuses):
                        ck_status = "ĐANG CẬP NHẬT"
                    elif all("✅ Đã nhận tiền" in s for s in statuses):
                        ck_status = "✅ Đã nhận tiền, CHỐT ĐƠN NHA!"
                    else:
                        ck_status = statuses[0]

                    # ---- KHỐI THÔNG TIN THANH TOÁN GỘP BẰNG HTML/CSS FLEXBOX ----
                    # Code img xử lý hiển thị linh hoạt
                    img_tag = f"<img src='data:image/jpeg;base64,{qr_base64}' alt='QR Code'><div class='qr-caption'>Quét mã QR để thanh toán</div>" if qr_base64 else "<div style='color:red;'>Đang cập nhật mã QR...</div>"
                    
                    noidung_ck = f"KHAN - {phone_input.strip()[-3:]}"
                    
                    payment_html = f"""
                    <div class='section-title'>THÔNG TIN THANH TOÁN</div>
                    <div class='payment-box'>
                        <div class='payment-info'>
                            <div class='info-row'><strong>💰 Số tiền cần thanh toán:</strong> <span class='highlight-val'>{tien_format}</span></div>
                            <div class='info-row'><strong>⏳ Hạn chót chuyển khoản:</strong> <span class='highlight-val'>{han_chot}</span></div>
                            <div class='info-row'><strong>⏱️ Thời gian còn lại:</strong> <span class='highlight-val'>{tg_con}</span></div>
                            <div class='info-row'><strong>💳 Trạng thái chuyển khoản:</strong> <span class='highlight-val'>{ck_status}</span></div>
                            <div style='margin-top: 20px; margin-bottom: 5px;'><strong>NỘI DUNG CHUYỂN KHOẢN CỦA BẠN:</strong></div>
                            <div style='background-color:#F8F9FA; border:1px solid #E0E6ED; padding:10px; border-radius:5px; font-family:monospace; font-size:16px; color:#D4AF37; font-weight:bold; margin-bottom:10px;'>{noidung_ck}</div>
                            <div style='font-size:14px; color:#155724; background-color:#d4edda; padding:10px; border-radius:5px;'>💡 Vui lòng ghi chính xác nội dung để hệ thống tự động chốt đơn nhé!</div>
                        </div>
                        <div class='payment-qr'>
                            {img_tag}
                        </div>
                    </div>
                    """
                    st.markdown(payment_html, unsafe_allow_html=True)                    
                    st.warning("🔄 Lưu ý: Sau khi chuyển khoản, bạn vui lòng đợi vài phút rồi bấm nút KẾT QUẢ lại một lần nữa để cập nhật trạng thái thành công nhé!")

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
    
    tab3_html = "<table class='custom-table' style='border-top: 1px solid #E0E6ED; border-radius: 8px;'><thead><tr><th>Phân loại</th>"
    
    for p in products:
        tab3_html += f"<th>{p}</th>"
    tab3_html += "</tr></thead><tbody>"
    
    for i in range(3):
        tab3_html += f"<tr><td>{table_data['Phân loại'][i]}</td>"
        for p in products:
            val = table_data[p][i]
            display_val = val if val > 0 else ""
            tab3_html += f"<td>{display_val}</td>"
        tab3_html += "</tr>"
        
    tab3_html += "</tbody></table>"
    
    st.markdown(tab3_html, unsafe_allow_html=True)
