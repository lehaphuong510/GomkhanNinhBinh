import streamlit as st
import pandas as pd
import re
import os
import base64
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(page_title="XÁC NHẬN THÔNG TIN GIAO HÀNG", page_icon="📦", layout="centered")

# ================= CSS VÀ GIAO DIỆN =================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, h4, .stTabs [data-baseweb="tab"] p { color: #0B192C !important; font-weight: bold; }
    .stButton>button { background-color: #F4C430; color: #0B192C; font-weight: bold; border-radius: 8px; border: none; width: 100%; }
    .stButton>button:hover { background-color: #0B192C; color: #FFFFFF; border: none; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #F8F9FA; color: #333333; border: 1px solid #0B192C; border-radius: 5px; }
    .stTabs [aria-selected="true"] { border-bottom-color: #0B192C !important; }
    
    .section-title { background: linear-gradient(90deg, #0B192C 0%, #F4C430 100%); color: white; padding: 12px 15px; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 20px; text-transform: uppercase; margin-bottom: 15px;}
    .info-box { background-color: #FAFAFA; border: 1px solid #E0E6ED; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .custom-tick { font-size: 18px; font-weight: bold; color: #D4AF37; }
    .note-alert { background-color: #E5F0FF; border-left: 4px solid #0052FF; padding: 15px; border-radius: 4px; font-size: 14px; color: #0B192C; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #0B192C; margin-bottom: 10px;'>📦 XÁC NHẬN THÔNG TIN GIAO HÀNG</h1>", unsafe_allow_html=True)

# Nút Refresh
col_rf1, col_rf2, col_rf3 = st.columns([1,2,1])
with col_rf2:
    if st.button("🔄 Cập nhật dữ liệu mới nhất"):
        st.cache_data.clear()
        st.rerun()

url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"
ADMIN_PASSWORD = "8994"

@st.cache_data(ttl=60)
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
    st.error("Đang có lỗi kết nối dữ liệu. Vui lòng thử lại sau!")
    st.stop()

# Lọc data chỉ lấy những đơn SHIP và CHỐT ĐƠN
if 'Nơi nhận' in df.columns:
    df_ship = df[df['Nơi nhận'].astype(str).str.upper().str.contains('SHIP', na=False)]
    df_ship = df_ship[df_ship['Trạng thái chuyển khoản'].astype(str).str.upper().str.contains('CHỐT ĐƠN', na=False)]
else:
    df_ship = df.copy()

tab1, tab2 = st.tabs(["🔍 XÁC NHẬN ĐƠN HÀNG", "🔒 ADMIN"])

# ================= TAB 1: USER CONFIRM =================
with tab1:
    st.markdown("### Nhập SĐT để kiểm tra đơn hàng")
    phone_input = st.text_input("Nhập số điện thoại của bạn:", placeholder="Ví dụ: 0901234567")
    
    if st.button("KIỂM TRA 🚀"):
        if phone_input:
            clean_input = phone_input.strip().lstrip('0')
            df_ship['Phone_Compare'] = df_ship['SDT full'].astype(str).str.lstrip('0')
            user_orders = df_ship[df_ship['Phone_Compare'] == clean_input].copy()
            
            if not user_orders.empty:
                st.session_state['verified_phone'] = clean_input 
                st.rerun()
            else:
                st.warning("Không tìm thấy đơn hàng giao tận nơi (SHIP) nào đã CHỐT ĐƠN với SĐT này. Bạn kiểm tra lại nhé!")
        else:
            st.warning("Bạn chưa nhập số điện thoại kìa!")

    if 'verified_phone' in st.session_state:
        clean_input = st.session_state['verified_phone']
        df_ship['Phone_Compare'] = df_ship['SDT full'].astype(str).str.lstrip('0')
        user_orders = df_ship[df_ship['Phone_Compare'] == clean_input]
        
        nicknames = user_orders['Nickname'].astype(str).replace('nan', '')
        valid_nicks = nicknames[nicknames.str.strip() != '']
        nickname = valid_nicks.iloc[0].strip() if len(valid_nicks) > 0 else "BẠN"
        
        original_phone = user_orders.iloc[0].get('SDT full', '')
        original_address = user_orders.iloc[0].get('Địa chỉ', '')
        
        st.success(f"🎉 Chào {nickname.upper()} ơi, bạn kiểm tra lại thông tin đơn hàng của mình lần cuối nha!")
        
        is_confirmed = False
        if 'Checked SDT' in user_orders.columns:
            if str(user_orders.iloc[0].get('Checked SDT', '')).strip() not in ['', 'nan', 'None']:
                is_confirmed = True
                st.info("✅ Bạn đã xác nhận thông tin trước đó rồi! Tuy nhiên bạn vẫn có thể cập nhật lại bên dưới nếu muốn thay đổi.")

        # 1. THÔNG TIN SẢN PHẨM
        st.markdown("<div class='section-title'>🛒 THÔNG TIN SẢN PHẨM</div>", unsafe_allow_html=True)
        products = ["Bandana TTB", "Twilly TTB", "Bandana ĐMN", "Twilly ĐMN"]
        
        prod_html = "<div class='info-box'><ul>"
        total_bandana = 0
        for p in products:
            count = user_orders[p].astype(str).str.contains('✅').sum()
            if count > 0:
                prod_html += f"<li><span style='font-size:16px;'>{p}: <b class='custom-tick'>{count} chiếc</b></span></li>"
                if "Bandana" in p: total_bandana += count
        prod_html += "</ul></div>"
        st.markdown(prod_html, unsafe_allow_html=True)
        
        refund_amount = total_bandana * 5000

        # 2. FORM ĐIỀN THÔNG TIN
        st.markdown("<div class='section-title'>📍 THÔNG TIN GIAO HÀNG</div>", unsafe_allow_html=True)
        is_correct = st.checkbox("Thông tin giao hàng bên dưới đã chính xác (Không cần sửa) ✅", value=True)
        
        if is_correct:
            final_phone = original_phone
            final_address = original_address
            st.markdown(f"<div class='info-box'><b>SĐT:</b> {final_phone}<br><b>Địa chỉ:</b> {final_address}</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='note-alert'>
            <b>💡 LƯU Ý DÀNH CHO BẠN:</b><br>
            - Nếu khu vực của bạn vừa được sáp nhập/thay đổi tên hành chính, bạn vui lòng cập nhật lại địa chỉ mới nhất để shipper dễ tìm nha.<br>
            - Bạn <b>CHỈ CẦN ĐIỀN</b> vào ô nào cần cập nhật. Nếu thông tin nào vẫn giữ nguyên thì cứ <b>BỎ TRỐNG</b> nhé!
            </div>
            """, unsafe_allow_html=True)
            
            final_phone_input = st.text_input("SĐT Cập Nhật:", placeholder=f"Hiện tại: {original_phone}")
            final_address_input = st.text_area("Địa chỉ Cập Nhật:", placeholder=f"Hiện tại: {original_address}")
            
            # Logic: Bỏ trống thì lấy cái cũ
            final_phone = final_phone_input if final_phone_input.strip() != "" else original_phone
            final_address = final_address_input if final_address_input.strip() != "" else original_address
            
        final_bank, final_stk, final_chu = "", "", ""
        if refund_amount > 0:
            st.markdown("<div class='section-title'>💸 THÔNG TIN HOÀN TIỀN</div>", unsafe_allow_html=True)
            st.info(f"🎁 Do giá Bandana giảm, bạn được hoàn lại số tiền là: **{refund_amount:,.0f} VNĐ**. Vui lòng điền thông tin để tụi mình chuyển khoản nhé!")
            col_b1, col_b2 = st.columns(2)
            final_bank = col_b1.text_input("Ngân hàng nhận tiền:")
            final_stk = col_b2.text_input("Số tài khoản:")
            final_chu = st.text_input("Tên chủ tài khoản:")
            
        st.markdown("<div class='section-title'>📝 LƯU Ý THÊM</div>", unsafe_allow_html=True)
        final_note = st.text_area("Bạn có muốn nhắn nhủ gì cho tụi mình không?", placeholder="Ghi chú về đơn hàng, thời gian nhận...")
        
        if st.button("🚀 CẬP NHẬT & CHỐT ĐƠN"):
            with st.spinner("Đang lưu thông tin vào hệ thống..."):
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_form = conn.read(spreadsheet=url, worksheet="Câu trả lời biểu mẫu 1")
                df_form.columns = df_form.columns.str.strip()
                
                cols_to_add = ['Checked SDT', 'Checked Địa chỉ', 'Ngân hàng', 'STK', 'Chủ TK', 'Lưu ý']
                for c in cols_to_add:
                    if c not in df_form.columns: df_form[c] = ""
                
                df_form['Phone_Compare'] = df_form['SDT full'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0')
                idx_list = df_form[df_form['Phone_Compare'] == clean_input].index
                
                if len(idx_list) > 0:
                    for idx in idx_list:
                        df_form.at[idx, 'Checked SDT'] = final_phone
                        df_form.at[idx, 'Checked Địa chỉ'] = final_address
                        df_form.at[idx, 'Ngân hàng'] = final_bank
                        df_form.at[idx, 'STK'] = final_stk
                        df_form.at[idx, 'Chủ TK'] = final_chu
                        df_form.at[idx, 'Lưu ý'] = final_note
                        
                    df_form = df_form.drop(columns=['Phone_Compare'])
                    conn.update(worksheet="Câu trả lời biểu mẫu 1", data=df_form)
                    
                    st.cache_data.clear() 
                    st.success("✅ Cập nhật thông tin thành công! Cảm ơn bạn rất nhiều 💖")
                    st.balloons()
                else:
                    st.error("Có lỗi xảy ra, không tìm thấy data gốc trong Biểu mẫu. Báo admin nhé!")

# ================= TAB 2: ADMIN CONFIRM =================
with tab2:
    st.markdown("### 🔒 CỔNG QUẢN TRỊ NỘI BỘ")
    pass_admin = st.text_input("Nhập mật khẩu Admin:", type="password")
    
    if pass_admin == ADMIN_PASSWORD:
        st.success("Đăng nhập thành công!")
        total_ship = len(df_ship)
        
        confirmed_count = 0
        if 'Checked Địa chỉ' in df_ship.columns:
            confirmed_count = df_ship[~df_ship['Checked Địa chỉ'].isna() & (df_ship['Checked Địa chỉ'].astype(str).str.strip() != '') & (df_ship['Checked Địa chỉ'].astype(str).str.strip() != 'nan')].shape[0]

        not_confirmed = total_ship - confirmed_count
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Tổng đơn SHIP", total_ship)
        col2.metric("✅ Đã Xác Nhận", confirmed_count)
        col3.metric("⏳ Đang chờ Xác Nhận", not_confirmed)
        
        st.divider()
        st.markdown("### 💸 DANH SÁCH HOÀN TIỀN BANDANA")
        
        refund_list = []
        for index, row in df_ship.iterrows():
            b_ttb = 1 if "✅" in str(row.get('Bandana TTB', '')) else 0
            b_dmn = 1 if "✅" in str(row.get('Bandana ĐMN', '')) else 0
            tong_ban = b_ttb + b_dmn
            tien_hoan = tong_ban * 5000
            
            if tien_hoan > 0:
                bank = str(row.get('Ngân hàng', '')).replace('nan','')
                stk = str(row.get('STK', '')).replace('nan','')
                chu = str(row.get('Chủ TK', '')).replace('nan','')
                status = "✅ Đã điền" if bank and stk else "⏳ Chưa điền"
                
                refund_list.append({
                    "Tên khách hàng": row.get('Nickname', ''),
                    "SĐT": str(row.get('SDT full', '')).replace('.0',''),
                    "Số lượng Bandana": tong_ban,
                    "Số tiền hoàn": tien_hoan,
                    "Ngân hàng": bank,
                    "STK": stk,
                    "Chủ TK": chu,
                    "Trạng thái STK": status
                })
                
        df_refund = pd.DataFrame(refund_list)
        if not df_refund.empty:
            st.dataframe(df_refund, use_container_width=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_refund.to_excel(writer, index=False, sheet_name='HoanTien')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 TẢI FILE EXCEL KẾ TOÁN (.xlsx)",
                data=excel_data,
                file_name="Danh_Sach_Hoan_Tien.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Hiện chưa có ai thuộc diện hoàn tiền.")
    elif pass_admin != "":
        st.error("Sai mật khẩu!")
