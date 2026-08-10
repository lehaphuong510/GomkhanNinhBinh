import streamlit as st
import pandas as pd
import re
import os
import base64
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(page_title="KẾT QUẢ GOM KHĂN NINH BÌNH", page_icon="🧣", layout="centered")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

qr_base64 = get_image_base64("TTCK.jpg")

prod_map = {
    "Bandana TTB": {"full": "Bandana Trịnh Thăng Bình", "img": "Bandana TTB.jpg"},
    "Twilly TTB": {"full": "Twilly Trịnh Thăng Bình", "img": "Twilly TTB.jpg"},
    "Bandana ĐMN": {"full": "Bandana Đinh Mạnh Ninh", "img": "Bandana ĐMN.jpg"},
    "Twilly ĐMN": {"full": "Twilly Đinh Mạnh Ninh", "img": "Twilly ĐMN.jpg"}
}

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, h4, .stTabs [data-baseweb="tab"] p { color: #0B192C !important; font-weight: bold; }
    
    .stButton>button { background-color: #F4C430; color: #0B192C; font-weight: bold; border-radius: 8px; border: none; width: 100%; }
    .stButton>button:hover { background-color: #0B192C; color: #FFFFFF; border: none; }
    .stTextInput>div>div>input { background-color: #F8F9FA; color: #333333; border: 1px solid #0B192C; border-radius: 5px; }
    .stTabs [aria-selected="true"] { border-bottom-color: #0B192C !important; }
    
    .section-title { background: linear-gradient(90deg, #0B192C 0%, #F4C430 100%); color: white; padding: 12px 15px; border-radius: 8px 8px 0 0; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 20px; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); overflow: hidden; }
    .custom-table thead tr { background-color: #1A2B4C; } 
    .custom-table th { color: white; padding: 12px 14px; text-align: center; font-size: 15px; border: none; }
    .custom-table th:first-child { text-align: left; }
    .custom-table td { padding: 14px; border-bottom: 1px solid #EEEEEE; border-right: 1px solid #EEEEEE; text-align: center; font-weight: bold; color: #0B192C; background-color: #FFFFFF;}
    .custom-table td:first-child { text-align: left; color: #0B192C; }
    .custom-table td:last-child { border-right: none; }
    .custom-table tr:last-child td { border-bottom: none; }
    
    .custom-tick { font-size: 20px; font-weight: 900; background: -webkit-linear-gradient(45deg, #0B192C, #F4C430); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .payment-box { display: flex; flex-wrap: wrap; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); background-color: #FAFAFA; margin-bottom: 25px; }
    .payment-info { flex: 1.3; min-width: 250px; padding-right: 15px; }
    .payment-qr { flex: 1; min-width: 200px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    .payment-qr img { max-width: 100%; border-radius: 8px; border: 1px solid #EEEEEE; }
    .qr-caption { font-size: 13px; color: #888; margin-top: 8px;}
    
    .highlight-val { color: #D4AF37; font-weight: bold; font-size: 16px;} 
    .info-row { margin-bottom: 15px; font-size: 15px; border-bottom: 1px dashed #EEEEEE; padding-bottom: 10px;}
    
    .metric-card { background-color: #FFFFFF; border: 1px solid #E0E6ED; border-top: 5px solid #0B192C; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .metric-title { font-size: 15px; color: #0B192C; font-weight: bold; text-transform: uppercase; margin-bottom: 10px;}
    .metric-sub { font-size: 14px; margin-top: 5px; color: #333333; }
    
    .backup-alert { background-color: #FFF3CD; color: #856404; padding: 20px; border-radius: 8px; border: 1px solid #FFEEBA; margin-bottom: 20px; text-align: center; line-height: 1.6; }
    .cancel-alert { background-color: #F8D7DA; color: #721C24; padding: 20px; border-radius: 8px; border: 1px solid #F5C6CB; margin-bottom: 20px; text-align: center; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# Khắc phục triệt để lỗi Title bị mất do CSS
st.markdown("<h1 style='text-align: center; color: #0B192C; margin-bottom: 30px;'>🧣 KẾT QUẢ GOM KHĂN NINH BÌNH</h1>", unsafe_allow_html=True)

url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"

@st.cache_data(ttl=15) 
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, worksheet="Data App")
    df.columns = df.columns.str.strip()
    
    if 'SDT full' in df.columns:
        df['SDT full'] = df['SDT full'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
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

tab1, tab2, tab3 = st.tabs(["🔍 TRA CỨU KẾT QUẢ", "📊 THỐNG KÊ ĐĂNG KÝ", "💰 CK THÀNH CÔNG"])

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
                # Lấy nickname chung cho SĐT
                nicknames = matched_rows['Nickname'].astype(str).replace('nan', '')
                valid_nicks = nicknames[nicknames.str.strip() != '']
                nickname = valid_nicks.iloc[0].strip() if len(valid_nicks) > 0 else "BẠN"
                
                # --- PHÂN LỌC ĐƠN THÀNH CÁC KHỐI (BLOCKS) ---
                order_blocks = []
                
                # 1. Quét dòng HỦY SLOT
                canceled_rows = matched_rows[matched_rows['Trạng thái chuyển khoản'].astype(str).str.upper().str.contains('HỦY SLOT', na=False)]
                if not canceled_rows.empty:
                    canceled_items = []
                    for ans in canceled_rows['Bạn đăng ký sản phẩm nào?'].astype(str):
                        if ans.strip() and ans.lower() != 'nan':
                            canceled_items.extend([x.strip() for x in ans.split(',') if x.strip()])
                    canceled_items = list(set(canceled_items))
                    if canceled_items:
                        order_blocks.append({"type": "CANCEL", "items": canceled_items, "title": "HỦY SLOT"})

                # 2. Quét dòng ACTIVE
                active_rows = matched_rows[~matched_rows['Trạng thái chuyển khoản'].astype(str).str.upper().str.contains('HỦY SLOT', na=False)]
                if not active_rows.empty:
                    success_rows = active_rows[active_rows['Đăng ký thành công'].astype(str).str.contains('✅', na=False)]
                    if not success_rows.empty:
                        unique_statuses = success_rows['Trạng thái chuyển khoản'].astype(str).unique()
                        for status in unique_statuses:
                            group_rows = success_rows[success_rows['Trạng thái chuyển khoản'].astype(str) == status]
                            if "✅ Đã nhận tiền" in status:
                                btitle = "CHỐT ĐƠN"
                            elif "ĐANG CẬP NHẬT" in status:
                                btitle = "ĐANG CHỜ CHUYỂN KHOẢN"
                            else:
                                btitle = status
                            order_blocks.append({"type": "ACTIVE", "status": status, "rows": group_rows, "title": btitle})
                            
                    # 3. Quét dòng CHỈ CÓ DỰ PHÒNG
                    backup_only_rows = active_rows[~active_rows['Đăng ký thành công'].astype(str).str.contains('✅', na=False)]
                    if not backup_only_rows.empty:
                        backup_items_only = []
                        for ans in backup_only_rows['Bạn đăng ký sản phẩm nào?'].astype(str):
                            if ans.strip() and ans.lower() != 'nan':
                                items = [x.strip() for x in ans.split(',')]
                                for item in items:
                                    if 'DỰ PHÒNG' in item.upper():
                                        clean_name = re.sub(r'[-\s\(]*DỰ PHÒNG[-\s\)]*', '', item, flags=re.IGNORECASE).strip()
                                        if clean_name: backup_items_only.append(clean_name)
                        backup_items_only = list(set(backup_items_only))
                        if backup_items_only:
                            order_blocks.append({"type": "BACKUP", "items": backup_items_only, "title": "DỰ PHÒNG"})

                # --- RENDER GIAO DIỆN TỪ CÁC KHỐI ĐÃ PHÂN LỌC ---
                total_blocks = len(order_blocks)
                
                if total_blocks > 0:
                    for idx, block in enumerate(order_blocks, 1):
                        # Tiêu đề chia đơn rõ ràng
                        if total_blocks > 1:
                            st.markdown(f"<h4 style='color:#0B192C; margin-top:25px; margin-bottom:15px; border-bottom: 2px solid #F4C430; padding-bottom: 8px;'>📦 KẾT QUẢ ĐƠN {idx}/{total_blocks} ({block['title']})</h4>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h4 style='color:#0B192C; margin-top:25px; margin-bottom:15px; border-bottom: 2px solid #F4C430; padding-bottom: 8px;'>📦 KẾT QUẢ ĐƠN CỦA BẠN ({block['title']})</h4>", unsafe_allow_html=True)
                        
                        # Khối Hủy
                        if block["type"] == "CANCEL":
                            cancel_str = ", ".join(block["items"])
                            # Đưa thẳng HTML sát lề trái để Streamlit ko nhận nhầm là Code Block
                            html_str = f"""<div class='cancel-alert'>
<strong>SLOT CỦA BẠN BỊ HỦY DO HẾT HẠN THANH TOÁN MÀ MÌNH VẪN CHƯA NHẬN ĐƯỢC CHUYỂN KHOẢN 😭</strong><br><br>
<span style='font-size: 15px;'>💔 <i>Sản phẩm đã bị hủy:</i> <strong>{cancel_str}</strong></span>
</div>"""
                            st.markdown(html_str, unsafe_allow_html=True)
                            
                        # Khối Dự phòng
                        elif block["type"] == "BACKUP":
                            backup_str = ", ".join(block["items"])
                            html_str = f"""<div class='backup-alert'>
<strong>BẠN HIỆN ĐANG TRONG DANH SÁCH DỰ PHÒNG, NẾU NHƯ CÓ SLOT CHÍNH HỦY, MÌNH SẼ LIÊN HỆ DANH SÁCH DỰ PHÒNG THEO THỨ TỰ ƯU TIÊN ĐIỀN FORM.</strong><br><br>
<span style='font-size: 15px;'>📦 <i>Sản phẩm bạn đã đăng ký dự phòng:</i> <strong>{backup_str}</strong></span>
</div>"""
                            st.markdown(html_str, unsafe_allow_html=True)
                            
                        # Khối Active (Thành công / Chờ CK)
                        elif block["type"] == "ACTIVE":
                            group_rows = block["rows"]
                            status = block["status"]
                            is_chot_don = "✅ Đã nhận tiền" in status
                            
                            if is_chot_don:
                                st.success(f"🎉 CHÚC MỪNG {nickname.upper()} ĐÃ CHỐT ĐƠN THÀNH CÔNG!")
                                ck_status = "✅ Đã nhận tiền, CHỐT ĐƠN NHA!"
                            else:
                                st.success(f"🎉 CHÚC MỪNG {nickname.upper()} ĐÃ ĐĂNG KÝ THÀNH CÔNG!")
                                ck_status = "ĐANG CẬP NHẬT"
                                
                            table_html = "<div class='section-title'>SẢN PHẨM ĐĂNG KÝ THÀNH CÔNG</div><table class='custom-table'><thead><tr><th>Sản Phẩm</th><th>Số Lượng</th></tr></thead><tbody>"
                            for p in products:
                                count = group_rows[p].astype(str).str.contains('✅').sum()
                                val_display = f"<span class='custom-tick'>{count}</span>" if count > 0 else ""
                                table_html += f"<tr><td>{p}</td><td>{val_display}</td></tr>"
                            table_html += "</tbody></table>"
                            st.markdown(table_html, unsafe_allow_html=True)
                            
                            backup_items = []
                            for ans in group_rows['Bạn đăng ký sản phẩm nào?'].astype(str):
                                if ans.strip() and ans.lower() != 'nan':
                                    items = [x.strip() for x in ans.split(',')]
                                    for item in items:
                                        if 'DỰ PHÒNG' in item.upper():
                                            clean_name = re.sub(r'[-\s\(]*DỰ PHÒNG[-\s\)]*', '', item, flags=re.IGNORECASE).strip()
                                            if clean_name: backup_items.append(clean_name)
                            backup_items = list(set(backup_items))
                            if backup_items:
                                backup_str = ", ".join(backup_items)
                                st.markdown(f"<div style='margin-bottom: 20px; font-style: italic; color: #E74C3C; text-align: center;'>💡 Đối với <strong>{backup_str}</strong>, bạn hiện đang trong danh sách dự phòng, mình sẽ liên hệ theo thứ tự ưu tiên đăng ký nếu có slot chính bị hủy.</div>", unsafe_allow_html=True)
                            
                            total_tien = 0
                            for tien_str in group_rows['Số tiền'].astype(str):
                                tien_str_clean = re.sub(r'\.0$', '', str(tien_str).strip())
                                tien_digits = re.sub(r'[^\d]', '', tien_str_clean)
                                if tien_digits:
                                    total_tien += int(tien_digits)
                            tien_format = f"{total_tien:,}".replace(',', '.') + " VNĐ" if total_tien > 0 else "Đang cập nhật"
                            
                            latest_row = group_rows.iloc[-1]
                            han_chot = latest_row.get('Hạn chót chuyển khoản', 'Đang cập nhật')
                            tg_con = latest_row.get('Thời gian còn lại', 'Đang cập nhật')
                            noidung_ck = f"KHAN - {phone_input.strip()[-3:]}"
                            
                            if is_chot_don:
                                payment_html = f"""<div class='section-title'>THÔNG TIN CHỐT ĐƠN</div>
<div class='payment-box' style='display:block;'>
<div class='payment-info' style='padding-right:0;'>
<div class='info-row'><strong>💰 Tổng tiền đã thanh toán:</strong> <span class='highlight-val'>{tien_format}</span></div>
<div class='info-row'><strong>💳 Trạng thái:</strong> <span class='highlight-val'>{ck_status}</span></div>
<div style='margin-top: 15px; font-size: 15px; color: #0052FF; background-color: #E5F0FF; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center;'>
💬 BẠN ƠI NHỚ VÀO GROUP ZALO ĐỂ TIỆN THEO DÕI NHA:<br>
<a href='https://zalo.me/g/4cfzit6xrp7y7m8clbar' target='_blank' style='color: #0052FF; text-decoration: underline;'>https://zalo.me/g/4cfzit6xrp7y7m8clbar</a>
</div>
</div>
</div>"""
                                st.markdown(payment_html, unsafe_allow_html=True)
                            else:
                                img_tag = f"<img src='data:image/jpeg;base64,{qr_base64}' alt='QR Code' style='max-width: 100%; border-radius: 8px; border: 1px solid #EEEEEE;'><div class='qr-caption'>Quét mã QR để thanh toán</div>" if qr_base64 else "<div style='color:red;'>Đang cập nhật mã QR...</div>"
                                payment_html = f"""<div class='section-title'>THÔNG TIN THANH TOÁN</div>
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
</div>"""
                                st.markdown(payment_html, unsafe_allow_html=True)                   
                                st.warning("🔄 Lưu ý: Sau khi chuyển khoản, bạn vui lòng đợi khoảng 15 phút rồi bấm nút KẾT QUẢ lại một lần nữa để kiểm tra trạng thái nhé!")
                else:
                    st.warning("Thông tin đăng ký của bạn chưa được xác nhận. Bạn vui lòng liên hệ admin để kiểm tra nhé!")
                    
            else:
                st.warning("Không tìm thấy số điện thoại này trong hệ thống. Vui lòng kiểm tra lại!")
        else:
            st.warning("Bạn chưa nhập số điện thoại kìa!")

# CÁI CÔNG TẮC ẨN/HIỆN THỐNG KÊ NẰM Ở ĐÂY NHA M:
# Đổi thành False nếu muốn ẨN (hiện chữ Hệ thống đang cập nhật)
# Đổi thành True nếu muốn HIỆN toàn bộ bảng thống kê
HIENTHI_THONGKE = True 

# ================= TAB 2 =================
with tab2:
    st.markdown("### 📊 THỐNG KÊ ĐĂNG KÝ")
    
    if HIENTHI_THONGKE:
        col1, col2 = st.columns(2)
        
        for i, p in enumerate(products):
            full_name = prod_map[p]["full"]
            img_name = prod_map[p]["img"]
            img_b64 = get_image_base64(img_name)
            
            limit_main = total_limits[p]
            limit_backup = 5
            
            main_success = df[p].astype(str).str.contains('✅').sum()
            main_remaining = max(0, limit_main - main_success)
            
            cancelled_main = 0
            backup_active = 0
            
            if 'Bạn đăng ký sản phẩm nào?' in df.columns:
                for index, row in df.iterrows():
                    ans = str(row.get('Bạn đăng ký sản phẩm nào?', ''))
                    status = str(row.get('Trạng thái chuyển khoản', '')).strip().upper()
                    has_tick = '✅' in str(row.get(p, '')) # Đã bổ sung lại dòng check tick xanh
                    
                    if ans.strip() and ans.lower() != 'nan': # Đã ép kiểu chữ chống lỗi ô trống
                        items = [x.strip() for x in ans.split(',')]
                        for item in items:
                            is_backup = 'DỰ PHÒNG' in item.upper()
                            clean_name = re.sub(r'[-\s\(]*DỰ PHÒNG[-\s\)]*', '', item, flags=re.IGNORECASE).strip()
                            
                            if clean_name == full_name:
                                if not is_backup and status == 'HỦY SLOT':
                                    cancelled_main += 1
                                elif is_backup and status != 'HỦY SLOT' and not has_tick:
                                    backup_active += 1
                                    
            backup_remaining = max(0, limit_backup - backup_active)
            call_backup = min(cancelled_main, 5)
            need_new = cancelled_main - 5 if cancelled_main > 5 else 0
            
            img_html = f"<img src='data:image/jpeg;base64,{img_b64}' style='width:100%; border-radius:8px; border:1px solid #EEEEEE;'>" if img_b64 else ""
            
            # Đã nén HTML lại thành 1 dòng để chống lỗi lòi thẻ </div> của Streamlit
            card_html = f"""<div class="metric-card" style="display: flex; align-items: center; justify-content: space-between;"><div style="flex: 1; max-width: 100px;">{img_html}</div><div style="flex: 2.5; padding-left: 15px;"><div class="metric-title">{full_name}</div><div class="metric-sub"><strong>✅ Chính thức:</strong> {main_success} / {limit_main} (Còn {main_remaining})</div><div class="metric-sub"><strong>📦 Dự phòng:</strong> {backup_active} / {limit_backup} (Còn {backup_remaining})</div><div class="metric-sub" style="color: #E74C3C; margin-top: 5px;"><strong>❌ Hủy slot do không CK:</strong> {cancelled_main}</div><div class="metric-sub" style="color: #27AE60;"><strong>🔄 Gọi thêm từ dự phòng:</strong> {call_backup}</div>{f'<div class="metric-sub" style="color: #C0392B; font-weight: bold; background-color: #FADBD8; padding: 5px; border-radius: 4px; display: inline-block; margin-top: 5px;">🚨 Cần gọi ĐK mới: {need_new} slot</div>' if need_new > 0 else ''}</div></div>"""
            if i % 2 == 0:
                col1.markdown(card_html, unsafe_allow_html=True)
            else:
                col2.markdown(card_html, unsafe_allow_html=True)
    else:
        # Giao diện hiển thị lúc đang đóng công tắc
        st.info("🔄 Hệ thống đang cập nhật số liệu. Bạn vui lòng quay lại sau nhé!")

# ================= TAB 3 =================
with tab3:
    st.markdown("### 💰 TỔNG HỢP CHỐT ĐƠN")
    
    if HIENTHI_THONGKE:
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
        
        st.markdown(tab3_html.replace('\n', ''), unsafe_allow_html=True)
    else:
        # Giao diện hiển thị lúc đang đóng công tắc
        st.info("🔄 Hệ thống đang cập nhật số liệu. Bạn vui lòng chờ thêm một chút nhé!")
