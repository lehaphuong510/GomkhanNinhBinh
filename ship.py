import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection

# ================= CẤU HÌNH CƠ BẢN =================
st.set_page_config(page_title="App Nội Bộ - Lọc Tỉnh Thành", layout="wide")
st.title("📦 HỆ THỐNG LỌC ĐỊA CHỈ SHIP - NỘI BỘ")

# ID Sheet của m (Đã điền sẵn)
SHEET_ID = '1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU' 
SHEET_NAME = 'Data%20App'


# ================= ĐIỀN TÊN CỘT =================
# Mấy cột này t bốc từ code cũ qua, đảm bảo đúng 100%:
COL_TRANG_THAI = 'Trạng thái chuyển khoản'
COLS_SAN_PHAM = [
    'Bandana TTB', 
    'Twilly TTB', 
    'Bandana ĐMN', 
    'Twilly ĐMN'
]
COL_NOI_NHAN = 'Nơi nhận' # M check lại tên cột này trên Sheet cho chuẩn nha

# 👇👇👇 [CHECK LẠI] M ngó vào Sheet xem 3 tên cột này viết chính xác là gì nha:
COL_TEN = 'Nickname' 
COL_SDT = 'SDT full' 
COL_DIA_CHI = 'Địa chỉ' # Cột mà khách thực sự điền số nhà, đường, quận...
# 👆👆👆 

# ================= TỪ ĐIỂN 63 TỈNH THÀNH =================
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

# Hàm bóc tách địa chỉ
def quet_tinh_thanh(dia_chi):
    if pd.isna(dia_chi):
        return "Chưa rõ"
    
    dia_chi_lower = str(dia_chi).lower()
    for tinh, tu_khoa_list in DICT_TINH.items():
        for tu_khoa in tu_khoa_list:
            if re.search(rf"\b{tu_khoa}\b", dia_chi_lower):
                return tinh
    return "Tỉnh khác (Cần check tay)"

# ================= XỬ LÝ DỮ LIỆU =================
url = "https://docs.google.com/spreadsheets/d/1RmfAjOdPwHdCNkI1evcDTj01HM6dyob9Dh-TcuSM5dU/edit?usp=sharing"
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
    df_raw = load_data()
    
    # 1. Lọc bạo lực: Chỉ lấy những đơn có chữ "CHỐT ĐƠN"
    df_chot_don = df_raw[df_raw[COL_TRANG_THAI].astype(str).str.upper().str.contains('CHỐT ĐƠN', na=False)].copy()
    
    
    # 👇👇 CHÈN THÊM DÒNG NÀY ĐỂ LỌC PHỄU 2 (CHỈ LẤY SHIP) 👇👇
    if COL_NOI_NHAN in df_chot_don.columns:
        # Lấy những dòng có chứa chữ "Ship"
        df_chot_don = df_chot_don[df_chot_don[COL_NOI_NHAN].astype(str).str.upper().str.contains('SHIP', na=False)]
    # 👆👆 ------------------------------------------------ 👆👆

       
    # 2. Tạo thêm cột Tỉnh Thành bằng hàm quét Regex
    if COL_DIA_CHI in df_chot_don.columns:
        df_chot_don['Tỉnh Thành'] = df_chot_don[COL_DIA_CHI].apply(quet_tinh_thanh)
    else:
        st.error(f"❌ Không tìm thấy cột '{COL_DIA_CHI}' trong Sheet! M nhớ check lại tên cột nha.")
        st.stop()
    
    
    # ================= GIAO DIỆN HIỂN THỊ =================
    st.subheader("1. 📊 Bảng tổng hợp số lượng theo tỉnh")
    
    # 1. Đếm Số lượng đơn tổng theo từng tỉnh trước
    df_tong_hop = df_chot_don['Tỉnh Thành'].value_counts().reset_index()
    df_tong_hop.columns = ['Tỉnh Thành', 'Số lượng đơn']
    
    # 2. Quét đếm từng món sản phẩm và ghép cột vào bảng
    for p in COLS_SAN_PHAM:
        if p in df_chot_don.columns:
            # Rà xem ở cột sản phẩm này, dòng nào có tick ✅
            df_mon_nay = df_chot_don[df_chot_don[p].astype(str).str.contains('✅', na=False)]
            
            # Đếm số lượng tick ✅ đó theo từng tỉnh
            dem_mon = df_mon_nay['Tỉnh Thành'].value_counts().reset_index()
            dem_mon.columns = ['Tỉnh Thành', p]
            
            # Gắn cái cột mới đếm được vào bảng tổng hợp chung
            df_tong_hop = pd.merge(df_tong_hop, dem_mon, on='Tỉnh Thành', how='left')
            
    # 3. Dọn dẹp số liệu cho đẹp (Trám số 0 vào những ô trống, ép kiểu thành số nguyên)
    df_tong_hop = df_tong_hop.fillna(0)
    for col in df_tong_hop.columns:
        if col != 'Tỉnh Thành':
            df_tong_hop[col] = df_tong_hop[col].astype(int)
            
    # In cái bảng ra màn hình
    st.dataframe(df_tong_hop, use_container_width=True)
    
    st.divider()
    
    st.subheader("2. 🔍 Trích xuất danh sách gửi Ship")
    danh_sach_tinh = sorted(df_chot_don['Tỉnh Thành'].unique().tolist())
    
    tinh_duoc_chon = st.selectbox("👉 Chọn Tỉnh/Thành phố muốn xem:", ["Tất cả"] + danh_sach_tinh)
    
    if tinh_duoc_chon == "Tất cả":
        df_hien_thi = df_chot_don
    else:
        df_hien_thi = df_chot_don[df_chot_don['Tỉnh Thành'] == tinh_duoc_chon]
        
    # Gom các cột cần thiết
    cot_can_xem = [COL_TEN, COL_SDT, COL_DIA_CHI] + COLS_SAN_PHAM
    
    # Kiểm tra xem các cột có tồn tại không trước khi hiển thị
    cot_thuc_te = [col for col in cot_can_xem if col in df_hien_thi.columns]
    
    # Ép kiểu SĐT về chuỗi để không bị hiện số phẩy
    if COL_SDT in df_hien_thi.columns:
        df_hien_thi[COL_SDT] = df_hien_thi[COL_SDT].astype(str).str.replace(r'\.0$', '', regex=True)
    
    st.dataframe(df_hien_thi[cot_thuc_te], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("3. 🖨️ Xuất File In Label (Dán Decal)")
    
    # Check xem sheet đã có cột Mã vận đơn chưa, chưa có thì gán rỗng để không bị lỗi
    COL_MVD = 'Mã vận đơn'
    if COL_MVD not in df_hien_thi.columns:
        df_hien_thi[COL_MVD] = ""

    if st.button("Tạo File In Label cho danh sách trên"):
        # Cấu hình giao diện bản in (CSS)
        html_content = """
        <html><head><meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 10px; }
            .grid-container { 
                display: grid; 
                grid-template-columns: repeat(2, 1fr); /* Chia 2 cột trên giấy A4 */
                gap: 15px; 
            }
            .label-box { 
                border: 2px dashed #000; /* Viền đứt nét để dễ căn cắt */
                padding: 15px; 
                border-radius: 8px; 
                box-sizing: border-box; 
                page-break-inside: avoid; /* Chống cắt nửa cái label khi sang trang mới */
            }
            .title { font-weight: bold; font-size: 18px; margin-bottom: 8px; border-bottom: 1px solid #ccc; padding-bottom: 5px;}
            .info { font-size: 15px; margin-bottom: 5px; line-height: 1.4; }
            .products { margin-top: 10px; font-size: 14px; font-weight: bold;}
            .prod-item { display: inline-block; width: 48%; margin-bottom: 4px; } /* Chia 2 cột cho sp */
        </style></head><body>
        <div class="grid-container">
        """

        # Chạy vòng lặp quét từng đơn để tạo Label
        for index, row in df_hien_thi.iterrows():
            ten = row.get(COL_TEN, '')
            sdt = str(row.get(COL_SDT, '')).replace('.0', '')
            diachi = row.get(COL_DIA_CHI, '')
            mvd = row.get(COL_MVD, '')
            
            # Xử lý logic Tick box (Có ✅ thì in ☑️, không thì in ⬜)
            p1 = "☑️" if "✅" in str(row.get(COLS_SAN_PHAM[0], '')) else "⬜"
            p2 = "☑️" if "✅" in str(row.get(COLS_SAN_PHAM[1], '')) else "⬜"
            p3 = "☑️" if "✅" in str(row.get(COLS_SAN_PHAM[2], '')) else "⬜"
            p4 = "☑️" if "✅" in str(row.get(COLS_SAN_PHAM[3], '')) else "⬜"

            # Gắn data vào khung
            html_content += f"""
            <div class="label-box">
                <div class="title">📦 MÃ VĐ: {mvd}</div>
                <div class="info">👤 <b>{ten}</b> <br>📞 {sdt}</div>
                <div class="info">🏠 {diachi}</div>
                <div class="products">
                    <div class="prod-item">{p1} BD Trịnh Thăng Bình</div>
                    <div class="prod-item">{p2} TW Trịnh Thăng Bình</div>
                    <div class="prod-item">{p3} BD Đinh Mạnh Ninh</div>
                    <div class="prod-item">{p4} TW Đinh Mạnh Ninh</div>
                </div>
            </div>
            """

        html_content += "</div></body></html>"

        # Nút tải file về máy
        st.download_button(
            label="📥 TẢI FILE IN (.html)",
            data=html_content,
            file_name="Label_Giao_Hang.html",
            mime="text/html"
        )

except Exception as e:
    st.error(f"Lỗi rồi m ơi: {e}")
    st.info("Nhớ kiểm tra lại Tên Cột ở phần [CHECK LẠI] xem m gõ đúng 100% chữ cái hoa/thường trên Sheet chưa nha!")
