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
    
    .backup-alert {
        background-color: #FFF3CD; color: #856404; padding: 20px; border-radius: 8px; border: 1px solid #FFEEBA; margin-bottom: 20px; text-align: center; line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧣 KẾT QUẢ GOM KHĂN NINH BÌNH")

# 2. KẾT NỐI DỮ LIỆU
url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"

@st.cache_data(ttl=15) 
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, worksheet="Data App")
    df.columns = df.columns.str.strip()
    
    if 'SDT full' in df.columns:
        df['SDT full'] = df['SDT full'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
    # Tự động map tên cột để tránh lỗi KeyError
    if 'Chuyển khoản thành công' in df.columns and 'Trạng thái chuyển khoản' not in df.columns:
        df = df.rename(columns={'Chuyển khoản thành công': 'Trạng thái chuyển khoản'})
        
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
            
            matched_rows = df[df['Phone_Compare'] == clean_input]
            
            if not matched_rows.empty:
                # 1. Quét tìm tất cả sản phẩm Khách đã chọn (Bóc tách Dự phòng và Chính)
                backup_items = []
                official_items = []
                
                if 'Bạn đăng ký sản phẩm nào?' in df.columns:
                    all_products = []
                    for val in matched_rows['Bạn đăng ký sản phẩm nào?'].astype(str):
                        if val.strip() and val.lower() != 'nan':
                            all_products.extend([x.strip() for x in val.split(',')])
                    
                    for item in all_products:
                        if 'DỰ PHÒNG' in item.upper():
                            clean_name = re.sub(r'[-\s\(]*DỰ PHÒNG[-\s\)]*', '', item, flags=re.IGNORECASE).strip()
                            if clean_name: backup_items.append(clean_name)
                        else:
                            if item: official_items.append(item)
                            
                    backup_items = list(set(backup_items))
                    official_items = list(set(official_items))
                
                is_success = matched_rows['Đăng ký thành công'].astype(str).str.contains('✅').any()

                # ---- TRƯỜNG HỢP 1: 100% LÀ DỰ PHÒNG ----
                if len(backup_items) > 0 and not is_success:
                    backup_str = ", ".join(backup_items)
                    st.markdown(f"""
                    <div class='backup-alert'>
                        <strong>BẠN HIỆN ĐANG TRONG DANH SÁCH DỰ PHÒNG, NẾU NHƯ CÓ SLOT CHÍNH HỦY, MÌNH SẼ LIÊN HỆ DANH SÁCH DỰ PHÒNG THEO THỨ TỰ ƯU TIÊN ĐIỀN FORM.</strong><br><br>
                        <span style='font-size: 15px;'>📦 <i>Sản phẩm bạn đã đăng ký dự phòng:</i> <strong>{backup_str}</strong></span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # ---- TRƯỜNG HỢP 2: CÓ ĐĂNG KÝ THÀNH CÔNG (Chính thức hoặc Mix cả 2) ----
                elif is_success:
                    nicknames = matched_rows['Nickname'].astype(str).replace('nan', '')
                    valid_nicks = nicknames[nicknames.str.strip() != '']
                    nickname = valid_nicks.iloc[0].strip() if len(valid_nicks) > 0 else "BẠN"
                    
                    st.success(f"🎉 CHÚC MỪNG {nickname.upper()} ĐÃ ĐĂNG KÝ THÀNH CÔNG!")
                    
                    table_html = "<div class='section-title'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</div>"
                    table_html += "<table class='custom-table'><thead><tr><th>Sản Phẩm</th><th>Số Lượng</th></tr></thead><tbody>"
                    
                    for p in products:
                        count = matched_rows[p].astype(str).str.contains('✅').sum()
                        val_display = f"<span class='custom-tick'>{count}</span>" if count > 0 else ""
                        table_html += f"<tr><td>{p}</td><td>{val_display}</td></tr>"
                    table_html += "</tbody></table>"
                    
                    st.markdown(table_html, unsafe_allow_html=True)
                    
                    # Hiển thị thông báo phụ cho sản phẩm dự phòng (Nếu khách có mix dự phòng)
                    # Sửa lỗi Markdown, thay bằng thẻ <strong> của HTML
                    if len(backup_items) > 0:
                        backup_str = ", ".join(backup_items)
                        st.markdown(f"<div style='margin-bottom: 20px; font-style: italic; color: #E74C3C; text-align: center;'>💡 Đối với <strong>{backup_str}</strong>, bạn hiện đang trong danh sách dự phòng, mình sẽ liên hệ theo thứ tự ưu tiên đăng ký nếu có slot chính bị hủy.</div>", unsafe_allow_html=True)
                    
                    total_tien = 0
                    for tien_str in matched_rows['Số tiền'].astype(str):
                        tien_str_clean = re.sub(r'\.0$', '', str(tien_str).strip())
                        tien_digits = re.sub(r'[^\d]', '', tien_str_clean)
                        if tien_digits:
                            total_tien += int(tien_digits)
                            
                    tien_format = f"{total_tien:,}".replace(',', '.') + " VNĐ" if total_tien > 0 else "Đang cập nhật"
                    
                    first_success = matched_rows[matched_rows['Đăng ký thành công'].astype(str).str.contains('✅')].iloc[0]
                    han_chot = first_success.get('Hạn chót chuyển khoản', 'Đang cập nhật')
                    tg_con = first_success.get('Thời gian còn lại', 'Đang cập nhật')
                    
                    statuses = matched_rows['Trạng thái chuyển khoản'].astype(str).tolist()
                    if any("ĐANG CẬP NHẬT" in s for s in statuses):
                        ck_status = "ĐANG CẬP NHẬT"
                    elif all("✅ Đã nhận tiền" in s for s in statuses):
                        ck_status = "✅ Đã nhận tiền, CHỐT ĐƠN NHA!"
                    else:
                        ck_status = statuses[0]

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
                    st.warning("🔄 Lưu ý: Sau khi chuyển khoản, bạn vui lòng đợi khoảng 15 phút rồi bấm nút KẾT QUẢ lại một lần nữa để kiểm tra trạng thái chuyển khoản nhé!")

                # ---- TRƯỜNG HỢP 3: TẠCH (Không có dữ liệu hợp lệ) ----
                else:
                    st.warning("Thông tin đăng ký của bạn chưa được xác nhận (Không có slot chính thức hoặc dự phòng). Bạn vui lòng liên hệ admin để kiểm tra nhé!")
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
        mask_p = df_registered[p].astype(str).str.contains('✅', na=False)
        df_p = df_registered[mask_p]
        
        total_raw = len(df_p)
        
        if 'Trạng thái chuyển khoản' in df_p.columns:
            cancelled_p = len(df_p[df_p['Trạng thái chuyển khoản'].astype(str).str.strip().str.upper() == 'HỦY SLOT'])
        else:
            cancelled_p = 0
            
        official_registered = total_raw - cancelled_p
        
        total = total_limits[p]
        rem_count = total - official_registered if (total - official_registered) > 0 else 0
        
        card_html = f"""
        <div class="metric-card">
            <div class="metric-title">{p}</div>
            <div class="metric-value">{official_registered} <span style="font-size:14px; color:#A0B2C6;">/ {total}</span></div>
            <div class="metric-sub" style="color: #E74C3C; margin-top: 8px;">❌ Đã hủy slot: {cancelled_p}</div>
            <div class="metric-sub" style="color: #27AE60; font-weight: bold; font-size: 15px;">🔄 Dự phòng cần gọi: {rem_count} slot</div>
        </div>
        """
        if i % 2 == 0:
            col1.markdown(card_html, unsafe_allow_html=True)
        else:
            col2.markdown(card_html, unsafe_allow_html=True)

# ================= TAB 3 =================
with tab3:
    st.markdown("### 💰 TỔNG HỢP CHỐT ĐƠN")
    
    df_ck = df[df['Trạng thái chuyển khoản'].astype(str).str.contains('✅ Đã nhận tiền, CHỐT ĐƠN NHA!', na=False, regex=False)]
    
    table_data = {
        "Phân loại": ["Tổng cộng", "Nhận tại sự kiện", "Ship về nhà"]
    }
    
    for p in products:
        df_ck_p = df_ck[df_ck[p].astype(str).str.contains('✅', na=False)]
        
        tot = len(df_ck_p)
        event = 0
        ship = 0
        
        if 'Nơi nhận' in df_ck_p.columns:
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
