import streamlit as st
import pandas as pd
import re
import io
from streamlit_gsheets import GSheetsConnection

# ================= CẤU HÌNH CƠ BẢN =================
st.set_page_config(page_title="App Nội Bộ - Lọc Tỉnh Thành", layout="wide")
st.title("📦 HỆ THỐNG LỌC ĐỊA CHỈ SHIP - NỘI BỘ")

# Nút Refresh
col_rf1, col_rf2, col_rf3 = st.columns([1,2,1])
with col_rf2:
    if st.button("🔄 Cập nhật dữ liệu mới nhất từ Biểu Mẫu"):
        st.cache_data.clear()
        st.rerun()
st.divider()

SHEET_ID = '1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU' 
SHEET_NAME = 'Data%20App'

COL_TRANG_THAI = 'Trạng thái chuyển khoản'
COLS_SAN_PHAM = ['Bandana TTB', 'Twilly TTB', 'Bandana ĐMN', 'Twilly ĐMN']
COL_NOI_NHAN = 'Nơi nhận' 
COL_TEN = 'Nickname' 
COL_SDT = 'SDT full' 
COL_DIA_CHI = 'Địa chỉ' 

DICT_TINH = {
    "Hồ Chí Minh": ["hồ chí minh", "hcm", "tp hcm", "tphcm", "sài gòn", "sg"],
    "Hà Nội": ["hà nội", "hn", "ha noi"],
    "Đà Nẵng": ["đà nẵng", "dn", "da nang"],
    "Hải Phòng": ["hải phòng", "hp"],
    "Cần Thơ": ["cần thơ", "ct"],
    "Đồng Nai": ["đồng nai", "biên hòa"],
    "Bình Dương": ["bình dương", "bd"],
    "Bà Rịa - Vũng Tàu": ["bà rịa", "vũng tàu", "brvt"],
    "Thừa Thiên Huế": ["thừa thiên huế", "t.t huế", "tt huế", "huế", "hue"],
    "Khánh Hòa": ["khánh hòa", "nha trang"],
    "Lâm Đồng": ["lâm đồng", "đà lạt"],
    "Quảng Nam": ["quảng nam", "hội an"],
    "Nghệ An": ["nghệ an", "vinh"],
    "Thanh Hóa": ["thanh hóa"],
    "Quảng Ninh": ["quảng ninh", "hạ long"],
    "An Giang": ["an giang"], "Bắc Giang": ["bắc giang"], "Bắc Kạn": ["bắc kạn", "bắc cạn"], 
    "Bạc Liêu": ["bạc liêu"], "Bắc Ninh": ["bắc ninh"], "Bến Tre": ["bến tre"], 
    "Bình Định": ["bình định", "quy nhơn"], "Bình Phước": ["bình phước"], "Bình Thuận": ["bình thuận", "phan thiết"], 
    "Cà Mau": ["cà mau"], "Cao Bằng": ["cao bằng"], "Đắk Lắk": ["đắk lắk", "dak lak", "buôn ma thuột"], 
    "Đắk Nông": ["đắk nông", "dak nong"], "Điện Biên": ["điện biên"], "Đồng Tháp": ["đồng tháp"], 
    "Gia Lai": ["gia lai", "pleiku"], "Hà Giang": ["hà giang"], "Hà Nam": ["hà nam"], 
    "Hà Tĩnh": ["hà tĩnh"], "Hải Dương": ["hải dương", "hd"], "Hậu Giang": ["hậu giang"], 
    "Hòa Bình": ["hòa bình"], "Hưng Yên": ["hưng yên"], "Kiên Giang": ["kiên giang", "phú quốc", "rạch giá"], 
    "Kon Tum": ["kon tum", "kontum"], "Lai Châu": ["lai châu"], "Lạng Sơn": ["lạng sơn"], 
    "Lào Cai": ["lào cai", "sapa"], "Long An": ["long an"], "Nam Định": ["nam định"], 
    "Ninh Bình": ["ninh bình"], "Ninh Thuận": ["ninh thuận"], "Phú Thọ": ["phú thọ"], 
    "Phú Yên": ["phú yên", "tuy hòa"], "Quảng Bình": ["quảng bình", "đồng hới"], "Quảng Ngãi": ["quảng ngãi"], 
    "Quảng Trị": ["quảng trị"], "Sóc Trăng": ["sóc trăng"], "Sơn La": ["sơn la"], 
    "Tây Ninh": ["tây ninh"], "Thái Bình": ["thái bình"], "Thái Nguyên": ["thái nguyên"], 
    "Tiền Giang": ["tiền giang", "mỹ tho"], "Trà Vinh": ["trà vinh"], "Tuyên Quang": ["tuyên quang"], 
    "Vĩnh Long": ["vĩnh long"], "Vĩnh Phúc": ["vĩnh phúc"], "Yên Bái": ["yên bái"]
}
DICT_MIEN = {
    "Miền Bắc": ["Hà Nội", "Hải Phòng", "Quảng Ninh", "Vĩnh Phúc", "Bắc Ninh", "Hải Dương", "Hưng Yên", "Hà Nam", "Nam Định", "Thái Bình", "Ninh Bình", "Hà Giang", "Cao Bằng", "Bắc Kạn", "Tuyên Quang", "Thái Nguyên", "Lạng Sơn", "Bắc Giang", "Phú Thọ", "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình", "Yên Bái", "Lào Cai"],
    "Miền Trung": ["Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế", "Đà Nẵng", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên", "Khánh Hòa", "Ninh Thuận", "Bình Thuận", "Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng"],
    "Miền Nam": ["Hồ Chí Minh", "Bình Dương", "Đồng Nai", "Bà Rịa - Vũng Tàu", "Tây Ninh", "Bình Phước", "Long An", "Tiền Giang", "Bến Tre", "Vĩnh Long", "Trà Vinh", "Đồng Tháp", "Hậu Giang", "Sóc Trăng", "An Giang", "Kiên Giang", "Bạc Liêu", "Cà Mau", "Cần Thơ"]
}

def quet_tinh_thanh(dia_chi):
    if pd.isna(dia_chi) or dia_chi == "": return "Chưa rõ"
    dia_chi_lower = str(dia_chi).lower()
    for tinh, tu_khoa_list in DICT_TINH.items():
        for tu_khoa in tu_khoa_list:
            if re.search(rf"\b{tu_khoa}\b", dia_chi_lower): return tinh
    return "Tỉnh khác (Cần check tay)"

def xac_dinh_mien(tinh):
    for mien, danh_sach in DICT_MIEN.items():
        if tinh in danh_sach: return mien
    return "Khác"

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing"

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
    return df

try:
    df_raw = load_data()
    df_chot_don = df_raw[df_raw[COL_TRANG_THAI].astype(str).str.upper().str.contains('CHỐT ĐƠN', na=False)].copy()
    
    if COL_NOI_NHAN in df_chot_don.columns:
        df_chot_don = df_chot_don[df_chot_don[COL_NOI_NHAN].astype(str).str.upper().str.contains('SHIP', na=False)]
        
    # === ƯU TIÊN LẤY DỮ LIỆU ĐÃ CONFIRM ===
    if 'Checked SDT' in df_chot_don.columns:
        df_chot_don['SDT full'] = df_chot_don['Checked SDT'].replace('', pd.NA).replace('nan', pd.NA).fillna(df_chot_don['SDT full'])
    if 'Checked Địa chỉ' in df_chot_don.columns:
        df_chot_don['Địa chỉ'] = df_chot_don['Checked Địa chỉ'].replace('', pd.NA).replace('nan', pd.NA).fillna(df_chot_don['Địa chỉ'])
        
    if COL_DIA_CHI in df_chot_don.columns:
        df_chot_don['Tỉnh Thành'] = df_chot_don[COL_DIA_CHI].apply(quet_tinh_thanh)
    else:
        st.error(f"❌ Không tìm thấy cột '{COL_DIA_CHI}' trong Sheet!")
        st.stop()
        
    if 'Tỉnh Thành' in df_chot_don.columns:
        df_chot_don['Khu vực'] = df_chot_don['Tỉnh Thành'].apply(xac_dinh_mien)

    # ================= 1. GIAO DIỆN BẢNG THỐNG KÊ =================
    st.subheader("1. 📊 Bảng tổng hợp số lượng theo tỉnh")
    mien_duoc_chon = st.multiselect("📍 Lọc dữ liệu theo Khu vực:", ["Tất cả", "Miền Bắc", "Miền Trung", "Miền Nam", "Khác"], default=["Tất cả"])
    
    if "Tất cả" in mien_duoc_chon or len(mien_duoc_chon) == 0:
        df_loc_mien = df_chot_don.copy()
    else:
        df_loc_mien = df_chot_don[df_chot_don['Khu vực'].isin(mien_duoc_chon)].copy()

    df_tong_hop = df_loc_mien['Tỉnh Thành'].value_counts().reset_index()
    df_tong_hop.columns = ['Tỉnh Thành', 'Số lượng đơn']
    
    for p in COLS_SAN_PHAM:
        if p in df_loc_mien.columns:
            df_mon_nay = df_loc_mien[df_loc_mien[p].astype(str).str.contains('✅', na=False)]
            dem_mon = df_mon_nay['Tỉnh Thành'].value_counts().reset_index()
            dem_mon.columns = ['Tỉnh Thành', p]
            df_tong_hop = pd.merge(df_tong_hop, dem_mon, on='Tỉnh Thành', how='left')
            
    df_tong_hop = df_tong_hop.fillna(0)
    for col in df_tong_hop.columns:
        if col != 'Tỉnh Thành': df_tong_hop[col] = df_tong_hop[col].astype(int)

    if not df_tong_hop.empty:
        tong_dict = {'Tỉnh Thành': '🌟 TỔNG CỘNG'}
        for col in df_tong_hop.columns:
            if col != 'Tỉnh Thành': tong_dict[col] = df_tong_hop[col].sum()
        df_tong_hop = pd.concat([pd.DataFrame([tong_dict]), df_tong_hop], ignore_index=True)

    def to_mau_dong_tong(row):
        if row['Tỉnh Thành'] == '🌟 TỔNG CỘNG':
            return ['background-color: #ffeb3b; color: #d32f2f; font-weight: bold;'] * len(row)
        return [''] * len(row)
        
    st.dataframe(df_tong_hop.style.apply(to_mau_dong_tong, axis=1), use_container_width=True)          
    st.divider()
    
    # ================= 2. BẢNG CHI TIẾT =================
    st.subheader("2. 🔍 Trích xuất danh sách gửi Ship")
    danh_sach_tinh = sorted(df_loc_mien['Tỉnh Thành'].unique().tolist())
    tinh_duoc_chon = st.multiselect("👉 Chọn chi tiết Tỉnh/Thành phố:", ["Tất cả"] + danh_sach_tinh, default=["Tất cả"])
    
    if "Tất cả" in tinh_duoc_chon or len(tinh_duoc_chon) == 0:
        df_hien_thi = df_loc_mien
    else:
        df_hien_thi = df_loc_mien[df_loc_mien['Tỉnh Thành'].isin(tinh_duoc_chon)]
        
    cot_can_xem = [COL_TEN, COL_SDT, COL_DIA_CHI] + COLS_SAN_PHAM
    if 'Lưu ý' in df_hien_thi.columns: cot_can_xem.append('Lưu ý')
    
    cot_thuc_te = [col for col in cot_can_xem if col in df_hien_thi.columns]
    st.dataframe(df_hien_thi[cot_thuc_te], use_container_width=True, hide_index=True)
    st.divider()

    # === THUẬT TOÁN GỘP ĐƠN CHUNG CHO EXCEL VÀ LABEL ===
    df_grouping = df_hien_thi.copy().reset_index(drop=True)
    
    # Đổi ✅ thành 1
    for p in COLS_SAN_PHAM:
        df_grouping[p] = df_grouping[p].astype(str).apply(lambda x: 1 if "✅" in x else 0)
        
    def parse_money(m):
        digits = re.sub(r'[^\d]', '', str(m))
        return int(digits) if digits else 0
    
    if 'Số tiền' in df_grouping.columns:
        df_grouping['Số tiền'] = df_grouping['Số tiền'].apply(parse_money)
    else:
        df_grouping['Số tiền'] = 0
        
    COL_MVD = 'Mã vận đơn'
    if COL_MVD not in df_grouping.columns: df_grouping[COL_MVD] = ""

    agg_dict = {COL_TEN: 'first', COL_DIA_CHI: 'first', 'Số tiền': 'sum', COL_MVD: 'first'}
    for p in COLS_SAN_PHAM: agg_dict[p] = 'sum'
    if 'Phiên lấy hàng' in df_grouping.columns: agg_dict['Phiên lấy hàng'] = 'first'
    
    df_grouped = df_grouping.groupby(COL_SDT, as_index=False).agg(agg_dict)
    
    def tao_sp_gom(row):
        sp_list = []
        for p in COLS_SAN_PHAM:
            if row[p] > 0: sp_list.append(f"{p} (x{row[p]})")
        return ", ".join(sp_list)
        
    df_grouped['Tên SP Gộp'] = df_grouped.apply(tao_sp_gom, axis=1)
    df_grouped['Tổng SL'] = df_grouped.apply(lambda r: sum([r[p] for p in COLS_SAN_PHAM]), axis=1)

    # ================= 3. XUẤT EXCEL GỘP ĐƠN =================
    st.subheader("3. 📊 Xuất File Excel ĐVVC (Tự động Gộp SĐT)")    
    dvvc_choice = st.radio("🚛 Chọn form xuất Đơn vị vận chuyển:", ["GHTK - Giao Hàng Tiết Kiệm", "VTP - Viettel Post"], horizontal=True)

    if st.button(f"Tạo File Excel cho {dvvc_choice.split(' - ')[0]}"):
        df_export = pd.DataFrame()
        if "GHTK" in dvvc_choice:
            prefix = "GHTK"
            df_export['Mã ĐH riêng'] = ""
            df_export['Tên khách hàng'] = df_grouped.get(COL_TEN, '')
            df_export['SĐT'] = df_grouped.get(COL_SDT, '')
            df_export['Địa chỉ chi tiết'] = df_grouped.get(COL_DIA_CHI, '')
            df_export['Tên sản phẩm'] = df_grouped['Tên SP Gộp']
            df_export['Số lượng'] = df_grouped['Tổng SL']
            df_export['KL (kg) KT (cm)'] = "5 x 5 x1 | 0.1"
            df_export['Giá trị hàng'] = df_grouped['Số tiền']
            df_export['Tiền CoD'] = 0
            df_export['Dịch vụ gia tăng'] = ""
            df_export['Hình thức lấy hàng'] = ""
            df_export['Phiên lấy hàng'] = df_grouped.get('Phiên lấy hàng', '')
            df_export['Dịch vụ & Hình thức VC'] = ""
            df_export['Trả ship'] = "Khách trả"

        elif "VTP" in dvvc_choice:
            prefix = "VTP"
            df_export['STT'] = range(1, len(df_grouped) + 1)
            df_export['Mã đơn hàng '] = ""
            df_export['Tên người nhận (*)'] = df_grouped.get(COL_TEN, '')
            df_export['Số ĐT người nhận (*)'] = df_grouped.get(COL_SDT, '')
            df_export['Địa chỉ nhận (*)'] = df_grouped.get(COL_DIA_CHI, '')
            df_export['Tên hàng hóa (*)'] = df_grouped['Tên SP Gộp']
            df_export['Số lượng'] = df_grouped['Tổng SL']
            df_export['Trọng lượng (gram)  (*)'] = 100
            df_export['Giá trị hàng (VND) (*)'] = df_grouped['Số tiền']
            df_export['Tiền thu hộ COD (VND)'] = 0
            df_export['Loại hàng hóa (*)'] = "Khăn"
            df_export['Tính chất hàng hóa đặc biệt'] = ""
            df_export['Dịch vụ  (*)'] = "PHS - Nội tỉnh tiết kiệm thỏa thuận"
            df_export['Dịch vụ cộng thêm '] = ""
            df_export['Thu tiền xem hàng'] = ""
            df_export['Dài (cm)'] = 5
            df_export['Rộng (cm)'] = 5
            df_export['Cao (cm)'] = 1
            df_export['Người trả cước'] = "Người nhận trả"
            df_export['Yêu cầu khác'] = ""
            df_export['Thời gian hẹn lấy'] = ""
            df_export['Thời gian giao'] = ""

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_data = output.getvalue()
        
        if "Tất cả" in tinh_duoc_chon or len(tinh_duoc_chon) == 0:
            ten_file = f"{prefix}_Tat_Ca.xlsx"
        else:
            chuoi_tinh = "_".join(tinh_duoc_chon)
            ten_file = f"{prefix}_{chuoi_tinh if len(chuoi_tinh) <= 40 else 'Nhieu_Tinh_Thanh'}.xlsx"
        
        st.success(f"Đã gộp thành công {len(df_hien_thi)} đơn gốc thành {len(df_grouped)} đơn Ship!")
        st.download_button(
            label=f"📥 TẢI FILE EXCEL {prefix} ĐÃ GỘP ĐƠN (.xlsx)",
            data=excel_data,
            file_name=ten_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # ================= 4. XUẤT LABEL GỘP ĐƠN =================
    st.subheader("4. 🖨️ Xuất File In Label (Dán Decal)")

    if st.button("Tạo File In Label (Đã Gộp Đơn)"):
        html_content = """
        <html><head><meta charset="utf-8">
        <style>
            @page { size: 100mm 150mm; margin: 0; }
            body { font-family: Arial, sans-serif; margin: 0; padding: 2mm; background-color: #f4f4f9; }
            .grid-container { display: flex; flex-direction: column; gap: 2mm; }
            .label-box { width: 96mm; height: 47mm; background: #fff; border: 1px dashed #000; padding: 5px; border-radius: 4px; box-sizing: border-box; page-break-inside: avoid; }
            .title { font-size: 14px; font-weight: bold; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 2px; margin-bottom: 4px; }
            .info { font-size: 13px; margin-bottom: 2px; line-height: 1.5; }
            .products { font-size: 10px; }
        </style></head><body><div class="grid-container">
        """
        
        # In Label dựa trên Data Đã Gộp (df_grouped)
        for index, row in df_grouped.iterrows():
            ten = row.get(COL_TEN, '')
            sdt = str(row.get(COL_SDT, '')).replace('.0', '')
            diachi = row.get(COL_DIA_CHI, '')
            mvd = row.get(COL_MVD, '')
            
            c_p1 = row.get(COLS_SAN_PHAM[0], 0)
            b1 = f"<span style='color: navy;'>✔</span> <b style='color: navy;'>{c_p1} BD Trịnh Thăng Bình</b>" if c_p1 > 0 else "▢ <span style='font-weight:normal; color:#555;'>BD Trịnh Thăng Bình</span>"
            
            c_p2 = row.get(COLS_SAN_PHAM[1], 0)
            b2 = f"<span style='color: navy;'>✔</span> <b style='color: navy;'>{c_p2} TW Trịnh Thăng Bình</b>" if c_p2 > 0 else "▢ <span style='font-weight:normal; color:#555;'>TW Trịnh Thăng Bình</span>"
            
            c_p3 = row.get(COLS_SAN_PHAM[2], 0)
            b3 = f"<span style='color: #D49A00;'>✔</span> <b style='color: #D49A00;'>{c_p3} BD Đinh Mạnh Ninh</b>" if c_p3 > 0 else "▢ <span style='font-weight:normal; color:#555;'>BD Đinh Mạnh Ninh</span>"
            
            c_p4 = row.get(COLS_SAN_PHAM[3], 0)
            b4 = f"<span style='color: #D49A00;'>✔</span> <b style='color: #D49A00;'>{c_p4} TW Đinh Mạnh Ninh</b>" if c_p4 > 0 else "▢ <span style='font-weight:normal; color:#555;'>TW Đinh Mạnh Ninh</span>"

            html_content += f"""
            <div class="label-box">
                <div class="title">📦 MÃ VĐ: {mvd}</div>
                <div class="info">👤 <b>{ten}</b> <br>📞 {sdt}</div>
                <div class="info">🏠 {diachi}</div>
                <div class="products" style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;">
                    <div style="flex: 1; padding-right: 5px;"><div style="margin-bottom: 4px;">{b1}</div><div style="margin-bottom: 4px;">{b2}</div></div>
                    <div style="flex: 1; padding-left: 5px;"><div style="margin-bottom: 4px;">{b3}</div><div style="margin-bottom: 4px;">{b4}</div></div>
                </div>
            </div>
            """
        html_content += "</div></body></html>"
        
        st.success(f"Đã tạo Label thành công cho {len(df_grouped)} đơn (sau khi gộp)!")
        st.download_button(label="📥 TẢI FILE IN LABLE (.html)", data=html_content, file_name="Label_Giao_Hang.html", mime="text/html")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
