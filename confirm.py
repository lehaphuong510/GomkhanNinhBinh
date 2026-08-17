import streamlit as st
import pandas as pd
import re
import os
import base64
import io
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(page_title="XÁC NHẬN THÔNG TIN GIAO HÀNG", page_icon="📦", layout="centered")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_title = get_image_base64("Web confirm.jpg")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, h4, .stTabs [data-baseweb="tab"] p { color: #0B192C !important; font-weight: bold; }
    
    /* CHỈ đổi màu những nút được đánh dấu là type="primary" */
    button[kind="primary"] { background-color: #F4C430 !important; color: #0B192C !important; font-weight: bold !important; border: none; width: 100%; border-radius: 8px;}
    button[kind="primary"]:hover { background-color: #0B192C !important; color: #FFFFFF !important; border: none; }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #F8F9FA; color: #333333; border: 1px solid #0B192C; border-radius: 5px; }
    .stTabs [aria-selected="true"] { border-bottom-color: #0B192C !important; }
    
    .section-title { background: linear-gradient(90deg, #0B192C 0%, #F4C430 100%); color: white; padding: 12px 15px; border-radius: 8px 8px 0 0; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .info-box { background-color: #FAFAFA; border: 1px solid #E0E6ED; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 20px; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); overflow: hidden; }
    .custom-table thead tr { background-color: #1A2B4C; } 
    .custom-table th { color: white; padding: 12px 14px; text-align: center; font-size: 15px; border: none; }
    .custom-table th:first-child { text-align: left; }
    .custom-table td { padding: 14px; border-bottom: 1px solid #EEEEEE; border-right: 1px solid #EEEEEE; text-align: center; font-weight: bold; }
    .custom-table td:first-child { text-align: left; }
    .custom-tick { font-size: 20px; font-weight: 900; background: -webkit-linear-gradient(45deg, #0B192C, #F4C430); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .stMultiSelect [data-baseweb="tag"] { background-color: #0B192C !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Hiển thị Banner Title
if img_title:
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><img src='data:image/jpeg;base64,{img_title}' style='width: 100%; max-width: 800px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'></div>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #0B192C; margin-bottom: 10px;'>📦 XÁC NHẬN THÔNG TIN GIAO HÀNG</h1>", unsafe_allow_html=True)

# Nút Refresh lề trái
col_rf1, col_rf2 = st.columns([1, 3])
with col_rf1:
    if st.button("🔄 Cập nhật dữ liệu"):
        st.cache_data.clear()
        st.rerun()

url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"
ADMIN_PASSWORD = "8994"

LOCK_FILE = "lock_form.txt"
def is_form_locked(): return os.path.exists(LOCK_FILE)
def set_form_lock(locked):
    if locked:
        with open(LOCK_FILE, "w") as f: f.write("locked")
    else:
        if os.path.exists(LOCK_FILE): os.remove(LOCK_FILE)

# HÀM TẨY TRẦN DỮ LIỆU GG SHEET TRƯỚC KHI GHI (Fix lỗi Checkbox 0/1 và Lỗi TypeError)
# HÀM TẨY TRẦN DỮ LIỆU GG SHEET TRƯỚC KHI GHI (Fix lỗi Checkbox 0/1 và Khôi phục số 0)
def clean_df_for_gsheets(df):
    cols_to_ensure = ['Checked SDT', 'Checked Địa chỉ', 'Ngân hàng', 'STK', 'Chủ TK', 'Lưu ý', 'Trạng thái xác nhận', 'Đã hoàn']
    for c in cols_to_ensure:
        if c not in df.columns: df[c] = ""
        df[c] = df[c].astype(object)
    
    if 'Bạn muốn nhận hàng như thế nào?' in df.columns:
        df['Bạn muốn nhận hàng như thế nào?'] = df['Bạn muốn nhận hàng như thế nào?'].astype(object)

    # 1. Chuyển các cột Hộp kiểm bị biến thành 1/0 về dạng Boolean chuẩn
    checkbox_cols = ['Zalo', 'Bao đã nhận tiền', 'Đăng ký thành công', 'Đã hoàn']
    for col in checkbox_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: True if str(x).strip() in ['1', '1.0', 'TRUE', 'True'] else (False if str(x).strip() in ['0', '0.0', 'FALSE', 'False'] else x))
            
    # 2. KHÔI PHỤC VÀ BẢO VỆ SỐ 0 CHO TẤT CẢ CÁC CỘT SĐT VÀ STK
    def restore_phone_zero(x):
        s = str(x).replace('.0', '').replace("'", "").strip()
        if s.lower() in ['nan', 'none', '']: return ""
        # Nếu là toàn số mà mất số 0 ở đầu thì nhả số 0 ra lại
        s_clean = s.replace(" ", "").replace(".", "")
        if s_clean.isdigit() and not s.startswith('0'): 
            s = '0' + s
        return s # Chèn nháy đơn để vĩnh viễn GG Sheet ko nuốt số 0 nữa
        
    def protect_stk(x):
        s = str(x).replace('.0', '').replace("'", "").strip()
        if s.lower() in ['nan', 'none', '']: return ""
        return s # STK ko tự thêm 0 vì có ngân hàng ko bắt đầu bằng 0
        
    # Quét tát cả các cột, hễ thấy SĐT hoặc STK là áp dụng khiên bảo vệ
    for col in df.columns:
        col_upper = col.upper()
        if 'SDT' in col_upper or 'ĐIỆN THOẠI' in col_upper:
            df[col] = df[col].apply(restore_phone_zero)
        elif 'STK' in col_upper or ('TÀI KHOẢN' in col_upper and 'CHỦ' not in col_upper):
            df[col] = df[col].apply(protect_stk)
            
    return df

@st.cache_data(ttl=60)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, worksheet="Data App")
    df.columns = df.columns.str.strip()
    
    if 'SDT full' in df.columns:
        def fix_sdt(x):
            s = str(x).replace('.0', '').strip()
            if s.lower() in ['nan', 'none', '']: return ""
            if s.isdigit() and not s.startswith('0'): return '0' + s
            return s
        df['SDT full'] = df['SDT full'].apply(fix_sdt)
        
    if 'Chuyển khoản thành công' in df.columns and 'Trạng thái chuyển khoản' not in df.columns:
        df = df.rename(columns={'Chuyển khoản thành công': 'Trạng thái chuyển khoản'})

    # Đọc thêm tab Data_DVVC để lấy link tra cứu
    dvvc_dict = {}
    try:
        df_dvvc = conn.read(spreadsheet=url, worksheet="Data_DVVC")
        df_dvvc.columns = df_dvvc.columns.str.strip()
        df_dvvc = df_dvvc.dropna(subset=['DVVC']) # Bỏ qua dòng rỗng
        dvvc_dict = dict(zip(df_dvvc['DVVC'].astype(str).str.strip(), df_dvvc['Link tra cứu'].astype(str).str.strip()))
    except Exception as e:
        pass # Nếu Sheet chưa kịp tạo thì cứ pass nhẹ nhàng, ko làm sập app
        
    return df, dvvc_dict
    

try:
    df_raw, dvvc_dict = load_data()
    # Lấy các đơn ĐÃ CHỐT ĐƠN
    df_chot = df_raw[df_raw['Trạng thái chuyển khoản'].astype(str).str.upper().str.contains('CHỐT ĐƠN', na=False)].copy()
except Exception as e:
    st.error("Đang có lỗi kết nối dữ liệu. Vui lòng thử lại sau!")
    st.stop()
    

tab1, tab2 = st.tabs(["🔍 XÁC NHẬN ĐƠN HÀNG", "🔒 ADMIN"])

# ================= TAB 1: USER CONFIRM =================
with tab1:
    st.markdown("### Nhập SĐT để kiểm tra đơn hàng")
    phone_input = st.text_input("Nhập số điện thoại của bạn:", placeholder="Ví dụ: 0901234567")
    
    if st.button("KIỂM TRA 🚀", type="primary"):
        if phone_input:
            clean_input = phone_input.strip().lstrip('0')
            df_chot['Phone_Compare'] = df_chot['SDT full'].astype(str).str.lstrip('0')
            user_orders = df_chot[df_chot['Phone_Compare'] == clean_input].copy()
            
            if not user_orders.empty:
                st.session_state['verified_phone'] = clean_input 
                st.rerun()
            else:
                st.warning("Không tìm thấy đơn hàng nào đã CHỐT ĐƠN với SĐT này. Bạn kiểm tra lại nhé!")
        else:
            st.warning("Bạn chưa nhập số điện thoại kìa!")

    if 'verified_phone' in st.session_state:
        clean_input = st.session_state['verified_phone']
        df_chot['Phone_Compare'] = df_chot['SDT full'].astype(str).str.lstrip('0')
        user_orders = df_chot[df_chot['Phone_Compare'] == clean_input]
        row_data = user_orders.iloc[0]
        
        nicknames = user_orders['Nickname'].astype(str).replace('nan', '')
        valid_nicks = nicknames[nicknames.str.strip() != '']
        nickname = valid_nicks.iloc[0].strip() if len(valid_nicks) > 0 else "BẠN"
        
        # LẤY THÔNG TIN GỐC
        original_phone = str(row_data.get('SDT full', '')).replace('.0','')
        original_address = str(row_data.get('Địa chỉ', ''))
        noi_nhan_goc = str(row_data.get('Nơi nhận', '')).strip().upper()
        
        tt_xacnhan = str(row_data.get('Trạng thái xác nhận', '')).strip()
        chk_sdt = str(row_data.get('Checked SDT', '')).strip().replace("'", "") # Gọt bỏ nháy đơn nếu có
        chk_dc = str(row_data.get('Checked Địa chỉ', '')).strip()
        
        has_update = (chk_sdt not in ['', 'nan', 'None']) or (chk_dc not in ['', 'nan', 'None'])
        
        # NẾU ĐÃ XÁC NHẬN -> ƯU TIÊN LẤY DỮ LIỆU ĐÃ CẬP NHẬT ĐỂ HIỂN THỊ
        if tt_xacnhan == "Đã xác nhận":
            if chk_sdt not in ['', 'nan', 'None']:
                original_phone = chk_sdt
            if chk_dc not in ['', 'nan', 'None']:
                original_address = chk_dc
            
            # Nếu fan nhận Sự Kiện nhưng đã cập nhật đổi thành Ship
            if str(row_data.get('Bạn muốn nhận hàng như thế nào?', '')).strip() == "Ship về nhà":
                noi_nhan_goc = "SHIP"
                
        # LỜI CHÀO 
        if tt_xacnhan == "Đã xác nhận":
            if has_update:
                st.success(f"🎉 Chào {nickname.upper()} ơi, bạn đã cập nhật thông tin thành công rồi nha, dưới đây là kết quả cuối cùng của bạn!")
            else:
                st.success(f"🎉 Chào {nickname.upper()} ơi, bạn đã xác nhận thông tin thành công rồi nha, dưới đây là kết quả cuối cùng của bạn!")
        else:
            st.info(f"👋 Chào {nickname.upper()} ơi, bạn kiểm tra lại thông tin đơn hàng của mình lần cuối nha!")

        # 0. THÔNG TIN VẬN CHUYỂN (Nằm trên Thông tin sản phẩm)
        st.markdown("<div class='section-title'>🚚 THÔNG TIN VẬN CHUYỂN</div>", unsafe_allow_html=True)
        
        mvd = str(row_data.get('Mã vận đơn', '')).replace('nan', '').strip()
        dvvc = str(row_data.get('DVVC', '')).replace('nan', '').strip()
        phien = str(row_data.get('Phiên lấy hàng', '')).replace('nan', '').strip()
        
        # Check xem có phải nhận sự kiện không (Đã update nếu Fan đổi từ Sự kiện sang Ship)
        is_event_delivery = "LOVE" in noi_nhan_goc or "SỰ KIỆN" in noi_nhan_goc or "HÀ NỘI" in noi_nhan_goc
        
        if mvd == "":
            st.info("📦 Tụi mình sẽ sớm cập nhật Thông tin vận chuyển ngay sau khi book đơn nha ❤️")
        else:
            link_tra_cuu = dvvc_dict.get(dvvc, "")
            
            html_ship = f"""
            <div class='info-box' style='background-color: #F0F8FF; border-left: 5px solid #F4C430;'>
                <div style='margin-bottom: 8px;'><b>Mã vận đơn:</b> <span style='color: #E74C3C; font-weight: bold; font-size: 16px;'>{mvd}</span></div>
                <div style='margin-bottom: 8px;'><b>Đơn vị vận chuyển:</b> {dvvc}</div>
                <div style='margin-bottom: 8px;'><b>Ngày shipper lấy hàng:</b> {phien}</div>
            """
            
            # Chỉ hiện Link tracking nếu có link VÀ KHÔNG PHẢI đơn sự kiện
            if link_tra_cuu != "" and not is_event_delivery:
                html_ship += f"<div style='margin-bottom: 8px;'><b>Link để tracking:</b> <a href='{link_tra_cuu}' target='_blank' style='color: #0066CC; text-decoration: none; font-weight: bold;'>Bấm vào đây để tra cứu hành trình nha 🚀</a></div>"
                
            html_ship += """
                <hr style='border: 0.5px dashed #ccc; margin: 15px 0 10px 0;'>
                <div style='font-size: 14px; font-style: italic; color: #555;'>
                    Nếu mọi người có gì cần hỗ trợ cứ liên hệ với tụi mình như thông tin trong group Zalo nha 😍
                </div>
            </div>
            """
            st.markdown(html_ship, unsafe_allow_html=True)
            
        # 1. THÔNG TIN SẢN PHẨM (Xám mờ nếu = 0, dấu check nếu = 1)
        st.markdown("<div class='section-title'>🛒 THÔNG TIN SẢN PHẨM</div>", unsafe_allow_html=True)
        products = ["Bandana TTB", "Twilly TTB", "Bandana ĐMN", "Twilly ĐMN"]
        
        table_html = "<table class='custom-table'><thead><tr><th>Sản Phẩm</th><th>Số Lượng</th></tr></thead><tbody>"
        total_bandana = 0
        for p in products:
            count = user_orders[p].astype(str).str.contains('✅').sum()
            if count == 0:
                row_style = "color: #B0B0B0;"
                val_display = ""
            elif count == 1:
                row_style = "color: #0B192C; font-weight: bold;"
                val_display = "<span class='custom-tick'>✓</span>"
            else:
                row_style = "color: #0B192C; font-weight: bold;"
                val_display = f"<span class='custom-tick'>{count}</span>"
                
            table_html += f"<tr style='{row_style}'><td>{p}</td><td>{val_display}</td></tr>"
            if "Bandana" in p: total_bandana += count
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        refund_amount = total_bandana * 5000

        # Trạng thái khóa
        is_locked = is_form_locked()
        if is_locked:
            st.error("🔒 ĐÃ HẾT THỜI GIAN CẬP NHẬT THÔNG TIN. Thông tin bên dưới là dữ liệu đã được hệ thống chốt sổ.")

        # 2. THÔNG TIN GIAO HÀNG
        st.markdown("<div class='section-title'>📍 THÔNG TIN GIAO HÀNG</div>", unsafe_allow_html=True)
        
        is_event = "LOVE" in noi_nhan_goc or "SỰ KIỆN" in noi_nhan_goc or "HÀ NỘI" in noi_nhan_goc

        if is_event:
            st.info("📍 Phương thức nhận hàng hiện tại: **Nhận tại sự kiện Love at first sight 29/8 ở Hà Nội**")
        else:
            st.info("📍 Phương thức nhận hàng hiện tại: **Ship về nhà**")

        if not is_locked:
            # Gán key theo SĐT để mỗi lần tra cứu luôn reset về mặc định ĐÃ TICK SẴN
            is_correct = st.checkbox("Thông tin giao hàng bên dưới đã chính xác.", value=True, key=f"chk_correct_{clean_input}")
            st.markdown("<div style='font-size: 13px; font-style: italic; color: #555; margin-top: -10px; margin-bottom: 15px;'>*Trong trường hợp bạn muốn cập nhật, bạn bỏ dấu tick phía đầu nha, và nếu địa chỉ của bạn chưa phải là địa chỉ sau sáp nhập, bạn cũng cập nhật lại giúp mình nha.</div>", unsafe_allow_html=True)
        else:
            is_correct = True

        final_phone = original_phone
        final_address = original_address

        if not is_locked and not is_correct:
            st.markdown("<div style='color: #E74C3C; font-size: 14px; font-weight: bold; margin-bottom: 5px;'>⚠️ CHỈ CẦN ĐIỀN VÀO Ô NÀO CẦN CẬP NHẬT. Ô nào giữ nguyên thì CỨ BỎ TRỐNG nhé!</div>", unsafe_allow_html=True)
            final_phone_input = st.text_input("SĐT Cập Nhật:", placeholder=f"Hiện tại: {original_phone}")
            
            if is_event: holder_add = "Nhập địa chỉ nhà của bạn để tụi mình Ship"
            else: holder_add = f"Hiện tại: {original_address}"
            final_address_input = st.text_area("Địa chỉ Cập Nhật:", placeholder=holder_add)
            
            final_phone = final_phone_input if final_phone_input.strip() != "" else original_phone
            final_address = final_address_input if final_address_input.strip() != "" else original_address
        else:
            if is_event and original_address in ['', 'nan', 'None']:
                st.markdown("<div class='info-box'><b>Trạng thái:</b> Đã xác nhận nhận tại sự kiện</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='info-box'><b>SĐT:</b> {final_phone}<br><b>Địa chỉ:</b> {final_address}</div>", unsafe_allow_html=True)

        # 3. THÔNG TIN HOÀN TIỀN
        final_bank, final_stk, final_chu = "", "", ""
        stk_goc = str(row_data.get('STK', '')).replace('nan','').replace("'", "") # Gọt bỏ nháy đơn
        
        # Bắt trạng thái Đã hoàn tiền
        da_hoan_val = str(row_data.get('Đã hoàn', '')).strip().upper()
        is_refunded = True if da_hoan_val in ['TRUE', '1', '1.0'] else False
        
        if refund_amount > 0:
            st.markdown("<div class='section-title'>💸 THÔNG TIN HOÀN TIỀN</div>", unsafe_allow_html=True)
            st.info(f"🎁 Do giá Bandana giảm, bạn được hoàn lại số tiền là: **{refund_amount:,.0f} VNĐ**.")
            
            if is_refunded:
                st.success("✅ Tụi mình đã hoàn tiền thành công cho bạn rồi nha! Bạn kiểm tra tài khoản giúp tụi mình nhé.")
                st.markdown(f"<div class='info-box'><b>Ngân hàng:</b> {str(row_data.get('Ngân hàng', '')).replace('nan','')}<br><b>STK:</b> {stk_goc}<br><b>Chủ TK:</b> {str(row_data.get('Chủ TK', '')).replace('nan','')}</div>", unsafe_allow_html=True)
            elif not is_locked:
                st.write("Vui lòng điền thông tin để tụi mình chuyển khoản nhé:")
                col_b1, col_b2 = st.columns(2)
                final_bank = col_b1.text_input("Ngân hàng nhận tiền:", value=str(row_data.get('Ngân hàng', '')).replace('nan',''))
                final_stk = col_b2.text_input("Số tài khoản:", value=stk_goc)
                final_chu = st.text_input("Tên chủ tài khoản:", value=str(row_data.get('Chủ TK', '')).replace('nan',''))
            else:
                st.markdown(f"<div class='info-box'><b>Ngân hàng:</b> {str(row_data.get('Ngân hàng', '')).replace('nan','')}<br><b>STK:</b> {stk_goc}<br><b>Chủ TK:</b> {str(row_data.get('Chủ TK', '')).replace('nan','')}</div>", unsafe_allow_html=True)
                
        # 4. LƯU Ý
        st.markdown("<div class='section-title'>📝 LƯU Ý THÊM</div>", unsafe_allow_html=True)
        if not is_locked:
            final_note = st.text_area("Bạn có muốn nhắn nhủ gì cho tụi mình không?", value=str(row_data.get('Lưu ý', '')).replace('nan',''))
        else:
            st.write(str(row_data.get('Lưu ý', '')).replace('nan',''))

        # NÚT CHỐT ĐƠN
        if not is_locked:
            if st.button("🚀 XÁC NHẬN / CẬP NHẬT THÔNG TIN", type="primary"):
                if not is_correct and final_phone_input.strip() == "" and final_address_input.strip() == "":
                    st.warning("⚠️ Bạn quên chưa tick xác nhận thông tin giao hàng hoặc chưa điền thông tin cập nhật rồi. Bạn vui lòng tick hoặc điền thông tin mới nếu cần cập nhật nha.")
                else:
                    with st.spinner("Đang lưu thông tin vào hệ thống..."):
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_form = conn.read(spreadsheet=url, worksheet="Câu trả lời biểu mẫu 1")
                        df_form.columns = df_form.columns.str.strip()
                        
                        # Gọi hàm tẩy trần dọn rác Pandas
                        df_form = clean_df_for_gsheets(df_form)
                        
                        idx_list = user_orders.index
                        
                        if len(idx_list) > 0:
                            for idx in idx_list:
                                if is_event and not is_correct:
                                    df_form.at[idx, 'Bạn muốn nhận hàng như thế nào?'] = "Ship về nhà"
                                
                                # Đã ép định dạng Plain Text trên Sheet nên lưu số trực tiếp luôn
                                sdt_to_save = final_phone.strip() if final_phone.strip() != "" else ""
                                stk_to_save = final_stk.strip() if final_stk.strip() != "" else ""
                                    
                                df_form.at[idx, 'Checked SDT'] = sdt_to_save
                                df_form.at[idx, 'Checked Địa chỉ'] = final_address
                                df_form.at[idx, 'Ngân hàng'] = final_bank
                                df_form.at[idx, 'STK'] = stk_to_save
                                df_form.at[idx, 'Chủ TK'] = final_chu
                                df_form.at[idx, 'Lưu ý'] = final_note
                                df_form.at[idx, 'Trạng thái xác nhận'] = "Đã xác nhận"
                                
                            conn.update(spreadsheet=url, worksheet="Câu trả lời biểu mẫu 1", data=df_form)
                            st.cache_data.clear() 
                            st.success("✅ ĐÃ GHI NHẬN LÊN HỆ THỐNG! Cảm ơn bạn rất nhiều 💖")
                            st.balloons()
                        else:
                            st.error("Có lỗi xảy ra, không lấy được vị trí dòng. Báo admin nhé!")

# ================= TAB 2: ADMIN CONFIRM =================
with tab2:
    st.markdown("### 🔒 CỔNG QUẢN TRỊ NỘI BỘ")
    pass_admin = st.text_input("Nhập mật khẩu Admin:", type="password")
    
    if pass_admin == ADMIN_PASSWORD:
        st.success("Đăng nhập thành công!")
        
        # 1. KHÓA FORM
        is_locked = is_form_locked()
        toggle_lock = st.toggle("🔒 KHÓA CẬP NHẬT (Không cho Fan sửa data nữa)", value=is_locked)
        if toggle_lock != is_locked:
            set_form_lock(toggle_lock)
            st.rerun()
        st.divider()

        # 2. CARD THỐNG KÊ XÁC NHẬN (TÍNH TẤT CẢ ĐƠN)
        total_orders = len(df_chot)
        
        confirmed_total = 0
        updated_count = 0
        
        if 'Trạng thái xác nhận' in df_chot.columns:
            df_confirmed = df_chot[df_chot['Trạng thái xác nhận'].astype(str).str.strip() == 'Đã xác nhận']
            confirmed_total = len(df_confirmed)
            
            
            # Đếm số người CÓ CẬP NHẬT THÔNG TIN (Cách 2: So sánh Đối chiếu)
            def has_update(row):
                # 1. Lấy và dọn dẹp data gốc
                orig_sdt = str(row.get('SDT full', '')).replace('.0', '').replace("'", "").strip()
                if orig_sdt.isdigit() and not orig_sdt.startswith('0'):
                    orig_sdt = '0' + orig_sdt
                orig_dc = str(row.get('Địa chỉ', '')).strip()
                
                noi_goc = str(row.get('Nơi nhận', '')).strip().upper()
                is_event_goc = "LOVE" in noi_goc or "SỰ KIỆN" in noi_goc or "HÀ NỘI" in noi_goc

                # 2. Lấy và dọn dẹp data Checked
                chk_sdt = str(row.get('Checked SDT', '')).replace("'", "").strip().replace('nan', '').replace('None', '')
                chk_dc = str(row.get('Checked Địa chỉ', '')).strip().replace('nan', '').replace('None', '')
                chk_noi = str(row.get('Bạn muốn nhận hàng như thế nào?', '')).strip()

                # 3. Mở phiên tòa xét xử: So sánh gốc và mới
                # TH1: Khách nhận sự kiện nhưng quyết định "quay xe" chọn Ship
                if is_event_goc and chk_noi == 'Ship về nhà':
                    return True
                
                # TH2: Cột Checked SDT có dữ liệu VÀ KHÁC với SDT gốc
                if chk_sdt != '' and chk_sdt != orig_sdt:
                    return True
                
                # TH3: Cột Checked Địa chỉ có dữ liệu VÀ KHÁC với Địa chỉ gốc
                if chk_dc != '' and chk_dc != orig_dc:
                    return True

                return False
                
            if confirmed_total > 0:
                updated_count = df_confirmed.apply(has_update, axis=1).sum()

        just_confirmed_count = confirmed_total - updated_count
        not_confirmed = total_orders - confirmed_total
        
        st.markdown("#### 📦 TIẾN ĐỘ XÁC NHẬN THÔNG TIN TỔNG")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Tổng đơn", total_orders)
        col2.metric("👌 Chỉ Xác Nhận", just_confirmed_count, help="Giữ nguyên thông tin gốc")
        col3.metric("✍️ Có Cập Nhật", updated_count, help="Đổi SĐT, Địa chỉ hoặc Đổi sang Ship")
        col4.metric("⏳ Đang chờ", not_confirmed)

        st.divider()
        
        # 3. QUẢN LÝ HOÀN TIỀN
        st.markdown("### 💸 QUẢN LÝ HOÀN TIỀN BANDANA")
        refund_list = []
        for index, row in df_chot.iterrows():
            b_ttb = 1 if "✅" in str(row.get('Bandana TTB', '')) else 0
            b_dmn = 1 if "✅" in str(row.get('Bandana ĐMN', '')) else 0
            tong_ban = b_ttb + b_dmn
            tien_hoan = tong_ban * 5000
            
            if tien_hoan > 0:
                bank = str(row.get('Ngân hàng', '')).replace('nan','').strip()
                stk = str(row.get('STK', '')).replace('nan','').replace("'", "").strip() # Lột vỏ nháy đơn
                chu = str(row.get('Chủ TK', '')).replace('nan','').strip()
                status = "✅ Đã điền" if bank and stk else "⏳ Chưa điền"
                
                # Bắt chuẩn trạng thái Đã hoàn
                da_hoan_val = str(row.get('Đã hoàn', '')).strip().upper()
                is_done = True if da_hoan_val in ['TRUE', '1', '1.0'] else False
                
                refund_list.append({
                    "Index": index, 
                    "Đã hoàn": is_done,
                    "Tên khách hàng": row.get('Nickname', ''),
                    "SĐT": str(row.get('SDT full', '')).replace('.0',''),
                    "SL": tong_ban,
                    "Số tiền hoàn": tien_hoan,
                    "Ngân hàng": bank,
                    "STK": stk,
                    "Chủ TK": chu,
                    "Trạng thái STK": status
                })
                
        df_refund = pd.DataFrame(refund_list)
        
        if not df_refund.empty:
            # BỘ LỌC
            col_f1, col_f2 = st.columns(2)
            unique_tien = df_refund['Số tiền hoàn'].unique().tolist()
            loc_tien = col_f1.multiselect("Lọc theo Số tiền hoàn:", unique_tien, default=[])
            loc_trangthai = col_f2.multiselect("Lọc theo Trạng thái điền form:", ["✅ Đã điền", "⏳ Chưa điền"], default=[])
            
            if len(loc_tien) == 0 and len(loc_trangthai) == 0: df_filtered = df_refund.copy()
            elif len(loc_tien) == 0: df_filtered = df_refund[df_refund['Trạng thái STK'].isin(loc_trangthai)]
            elif len(loc_trangthai) == 0: df_filtered = df_refund[df_refund['Số tiền hoàn'].isin(loc_tien)]
            else: df_filtered = df_refund[(df_refund['Số tiền hoàn'].isin(loc_tien)) & (df_refund['Trạng thái STK'].isin(loc_trangthai))]
            
            df_display = df_filtered.copy()
            df_display['Số tiền hoàn'] = df_display['Số tiền hoàn'].apply(lambda x: f"{x:,.0f}")
            
            st.markdown("<p style='font-weight:bold; color:#0B192C;'>Check trực tiếp vào ô 'Đã hoàn' bên dưới, sau đó bấm Lưu:</p>", unsafe_allow_html=True)
            
            # DATA EDITOR SỐNG
            edited_df = st.data_editor(
                df_display.drop(columns=['Index']),
                column_config={"Đã hoàn": st.column_config.CheckboxColumn("Đã hoàn", default=False)},
                disabled=["Tên khách hàng", "SĐT", "SL", "Số tiền hoàn", "Ngân hàng", "STK", "Chủ TK", "Trạng thái STK"],
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("LƯU TRẠNG THÁI HOÀN TIỀN LÊN GOOGLE SHEET", type="primary"):
                with st.spinner("Đang cập nhật lên Sheet..."):
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_form = conn.read(spreadsheet=url, worksheet="Câu trả lời biểu mẫu 1")
                    df_form.columns = df_form.columns.str.strip()
                    
                    # Gọi hàm tẩy trần dọn rác Pandas
                    df_form = clean_df_for_gsheets(df_form)
                    
                    for i in range(len(edited_df)):
                        origin_idx = df_filtered.iloc[i]['Index']
                        new_val = edited_df.iloc[i]['Đã hoàn']
                        # Gán thẳng True/False để GG Sheet hiện đúng hộp kiểm
                        df_form.at[origin_idx, 'Đã hoàn'] = bool(new_val)
                        
                    conn.update(spreadsheet=url, worksheet="Câu trả lời biểu mẫu 1", data=df_form)
                    st.cache_data.clear()
                    st.success("✅ Đã lưu trạng thái hoàn tiền thành công!")
            
            # Xuất Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_dl = df_filtered.drop(columns=['Index']).copy()
                df_dl['SĐT'] = df_dl['SĐT'].apply(lambda x: f"'{x}") 
                df_dl['STK'] = df_dl['STK'].apply(lambda x: f"'{x}" if str(x).strip() != "" else "") 
                df_dl.to_excel(writer, index=False, sheet_name='HoanTien')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 TẢI FILE EXCEL DANH SÁCH NÀY (.xlsx)",
                data=excel_data,
                file_name="Danh_Sach_Hoan_Tien.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Hiện chưa có ai thuộc diện hoàn tiền.")
            
        st.divider()
        
        # 4. TỔNG HỢP CHỐT ĐƠN (3 DÒNG)
        st.markdown("### 💰 TỔNG HỢP CHỐT ĐƠN")
        products_table = ["Bandana TTB", "Twilly TTB", "Bandana ĐMN", "Twilly ĐMN"]
        table_data = {"Phân loại": ["Tổng cộng", "Nhận tại sự kiện", "Ship về nhà"]}
        for p in products_table:
            tot, event, ship = 0, 0, 0
            for index, row in df_chot.iterrows():
                if "✅" in str(row.get(p, '')):
                    tot += 1
                    noi = str(row.get('Nơi nhận', '')).strip().upper()
                    if "LOVE" in noi or "SỰ KIỆN" in noi or "HÀ NỘI" in noi: event += 1
                    elif "SHIP" in noi: ship += 1
            table_data[p] = [tot, event, ship]
            
        tab3_html = "<table class='custom-table'><thead><tr><th>Phân loại</th>"
        for p in products_table: tab3_html += f"<th>{p}</th>"
        tab3_html += "</tr></thead><tbody>"
        for i in range(3):
            is_ev = "Sự kiện" in table_data['Phân loại'][i]
            td_style = "background-color: #FFF3CD !important; color: #856404 !important; font-weight: bold;" if is_ev else ""
            
            tab3_html += f"<tr><td style='{td_style}'>{table_data['Phân loại'][i]}</td>"
            for p in products_table:
                val = table_data[p][i]
                tab3_html += f"<td style='{td_style}'>{val if val > 0 else ''}</td>"
            tab3_html += "</tr>"
        tab3_html += "</tbody></table>"
        st.markdown(tab3_html, unsafe_allow_html=True)

        # 6. TỔNG HỢP LỜI CHÚC / LƯU Ý TỪ FAN
        st.divider()
        st.markdown("### 💌 LỜI NHẮN NHỦ TỪ FAN")

        if 'Lưu ý' in df_chot.columns:
            # Lọc ra những người có điền Lưu ý (khác rỗng, nan, None)
            df_notes = df_chot[df_chot['Lưu ý'].astype(str).str.strip().replace(['nan', 'None', ''], pd.NA).notna()]
            
            # Bỏ qua những bạn chỉ nhập khoảng trắng
            df_notes = df_notes[df_notes['Lưu ý'].astype(str).str.strip() != '']
            
            if not df_notes.empty:
                st.write(f"🥰 Đang có **{len(df_notes)}** lời nhắn siêu dễ thương từ các bạn Fan nè:")
                
                # Chia làm 2 cột cho đẹp và đỡ bị dài trang
                cols = st.columns(2)
                
                for idx, row in enumerate(df_notes.iterrows()):
                    row_data = row[1]
                    note = str(row_data['Lưu ý']).strip()
                    sdt = str(row_data.get('SDT full', '')).replace('.0', '').replace("'", "")
                    name = str(row_data.get('Nickname', '')).replace('nan', '').strip()
                    if name == "": name = "Fan Giấu Tên"
                    
                    # HTML template cho 1 card lời nhắn (màu vàng nhạt, viền vàng đậm)
                    card_html = f"""
                    <div style="background-color: #FFF9E6; border-left: 5px solid #F4C430; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <div style="font-size: 13px; font-weight: bold; color: #0B192C; margin-bottom: 8px;">
                            👤 {name} <span style="color: #666; font-weight: normal;">({sdt})</span>
                        </div>
                        <div style="font-size: 14px; color: #333; font-style: italic; line-height: 1.5;">
                            "{note}"
                        </div>
                    </div>
                    """
                    # Rải đều thẻ vào 2 cột (0 thì cột trái, 1 thì cột phải)
                    cols[idx % 2].markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("Hiện tại chưa có bạn nào để lại lời nhắn.")
        else:
            st.error("Chưa có cột 'Lưu ý' trong dữ liệu.")
        
    elif pass_admin != "":
        st.error("Sai mật khẩu!")
