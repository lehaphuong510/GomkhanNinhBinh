import streamlit as st
import pandas as pd
import re
import io
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
        def fix_sdt(x):
            # 1. Ép về kiểu chữ, cắt đuôi .0 và xóa khoảng trắng thừa
            s = str(x).replace('.0', '').strip()
            # 2. Nếu là ô trống thì trả về ô trống, không xử lý thêm
            if s.lower() == 'nan' or s.lower() == 'none' or s == '':
                return ""
            # 3. Nếu toàn là số và thiếu số 0 ở đầu -> Bơm số 0 vào
            if s.isdigit() and not s.startswith('0'):
                return '0' + s
            return s
            
        df['SDT full'] = df['SDT full'].apply(fix_sdt)
        
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
    
    # Đổi thành multiselect cho phép chọn nhiều tỉnh cùng lúc
    tinh_duoc_chon = st.multiselect(
        "👉 Chọn Tỉnh/Thành phố muốn xem (Có thể chọn nhiều):", 
        ["Tất cả"] + danh_sach_tinh, 
        default=["Tất cả"]
    )
    
    # Xử lý logic lọc nhiều tỉnh
    if "Tất cả" in tinh_duoc_chon or len(tinh_duoc_chon) == 0:
        df_hien_thi = df_chot_don
    else:
        # Lọc ra những đơn có tỉnh nằm trong danh sách đã chọn
        df_hien_thi = df_chot_don[df_chot_don['Tỉnh Thành'].isin(tinh_duoc_chon)]
        
    # Gom các cột cần thiết
    cot_can_xem = [COL_TEN, COL_SDT, COL_DIA_CHI] + COLS_SAN_PHAM
    
    # Kiểm tra xem các cột có tồn tại không trước khi hiển thị
    cot_thuc_te = [col for col in cot_can_xem if col in df_hien_thi.columns]
    
    # Ép kiểu SĐT về chuỗi để không bị hiện số phẩy
    if COL_SDT in df_hien_thi.columns:
        df_hien_thi[COL_SDT] = df_hien_thi[COL_SDT].astype(str).str.replace(r'\.0$', '', regex=True)
    
    st.dataframe(df_hien_thi[cot_thuc_te], use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("3. 📊 Xuất File Excel (Mẫu GHTK)")    
    if st.button("Tạo File Excel GHTK cho danh sách trên"):
        # 1. Tạo một DataFrame mới tinh để đóng gói theo đúng chuẩn ĐVVC
        df_export = pd.DataFrame()
        
        # Hàm đếm số lượng: Quét 4 cột sản phẩm xem có bao nhiêu tick ✅
        def dem_so_luong(row):
            count = 0
            for p in COLS_SAN_PHAM:
                if "✅" in str(row.get(p, '')):
                    count += 1
            return count if count > 0 else 1 # Tránh ra 0 nếu data có lỗi
            
        # 2. Lắp ráp từng cột theo đúng thứ tự m dặn
        df_export['Mã ĐH riêng'] = ""
        df_export['Tên khách hàng'] = df_hien_thi.get(COL_TEN, '')
        df_export['SĐT'] = df_hien_thi.get(COL_SDT, '')
        df_export['Địa chỉ chi tiết'] = df_hien_thi.get(COL_DIA_CHI, '')
        
        # Mấy cột mới này nếu trên Sheet m chưa có thì nó sẽ tự để trống không báo lỗi
        df_export['Tên sản phẩm'] = df_hien_thi.get('Sản phẩm đăng ký thành công', '')
        df_export['Số lượng'] = df_hien_thi.apply(dem_so_luong, axis=1)
        df_export['KL (kg) KT (cm)'] = "5 x 5 x1 | 0.1"
        df_export['Giá trị hàng'] = df_hien_thi.get('Số tiền', '')
        df_export['Tiền CoD'] = ""
        df_export['Dịch vụ gia tăng'] = ""
        df_export['Hình thức lấy hàng'] = ""
        df_export['Phiên lấy hàng'] = df_hien_thi.get('Phiên lấy hàng', '')
        df_export['Dịch vụ & Hình thức VC'] = ""
        df_export['Trả ship'] = "Khách trả"
        
        # 3. Đóng gói thành file Excel (lưu vào bộ nhớ đệm)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_data = output.getvalue()
        
        # TẠO TÊN FILE THÔNG MINH
        if "Tất cả" in tinh_duoc_chon or len(tinh_duoc_chon) == 0:
            ten_file = "GHTK_Tat_Ca.xlsx"
        else:
            # Nối tên các tỉnh m đã chọn lại (ví dụ: Hồ Chí Minh_Hà Nội)
            chuoi_tinh = "_".join(tinh_duoc_chon)
            # Nếu tên dài quá (do chọn nhiều tỉnh) thì gộp chung cho an toàn
            if len(chuoi_tinh) > 40:
                chuoi_tinh = "Nhieu_Tinh_Thanh"
            ten_file = f"GHTK_{chuoi_tinh}.xlsx"
        
        # 4. Hiện nút Download file về máy
        st.download_button(
            label="📥 TẢI FILE EXCEL (.xlsx)",
            data=excel_data,
            file_name=ten_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.subheader("4. 🖨️ Xuất File In Label (Dán Decal)")
    
    # Check xem sheet đã có cột Mã vận đơn chưa, chưa có thì gán rỗng để không bị lỗi
    COL_MVD = 'Mã vận đơn'
    if COL_MVD not in df_hien_thi.columns:
        df_hien_thi[COL_MVD] = ""

    if st.button("Tạo File In Label cho danh sách trên"):
        # Cấu hình giao diện bản in (CSS)
        html_content = """
        <html><head><meta charset="utf-8">
        <style>
            @page { 
                size: 100mm 150mm; /* Khổ A6 chuẩn */
                margin: 0; 
            }
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 2mm; 
                background-color: #f4f4f9; 
            }
            .grid-container { 
                display: flex; 
                flex-direction: column; /* Xếp dọc từ trên xuống */
                gap: 2mm; /* Khoảng cách giữa 3 tem */
            }
            .label-box { 
                width: 96mm; 
                height: 47mm; /* 47x3 = 141mm, vừa khít 150mm A6 */
                background: #fff; 
                border: 1px dashed #000; 
                padding: 5px; 
                border-radius: 4px; 
                box-sizing: border-box; 
                page-break-inside: avoid; /* Chống cắt nửa tem khi sang trang */
            }
            .title { 
                font-size: 14px; 
                font-weight: bold; 
                color: #333; 
                border-bottom: 1px solid #ccc; 
                padding-bottom: 2px; 
                margin-bottom: 4px; 
            }
            .info { 
                font-size: 13px; /* Thu nhỏ chữ lại để vừa khung */
                margin-bottom: 2px; 
                line-height: 1.2; 
            }
            .products {
                font-size: 10px; /* Font sản phẩm nhỏ gọn */
            }
        </style></head><body>
        <div class="grid-container">
        """

        # Chạy vòng lặp quét từng đơn để tạo Label
        # Chạy vòng lặp quét từng đơn để tạo Label
        for index, row in df_hien_thi.iterrows():
            ten = row.get(COL_TEN, '')
            sdt = str(row.get(COL_SDT, '')).replace('.0', '')
            diachi = row.get(COL_DIA_CHI, '')
            mvd = row.get(COL_MVD, '')
            
            # Xử lý logic Tick box và In đậm (Có tick = đậm, không tick = mỏng)
            # Xử lý logic Tick box và In đậm, Tô màu
            has_p1 = "✅" in str(row.get(COLS_SAN_PHAM[0], ''))
            b1 = "<span style='color: navy;'>✔</span> <b style='color: navy;'>BD Trịnh Thăng Bình</b>" if has_p1 else "▢ <span style='font-weight:normal; color:#555;'>BD Trịnh Thăng Bình</span>"
            
            has_p2 = "✅" in str(row.get(COLS_SAN_PHAM[1], ''))
            b2 = "<span style='color: navy;'>✔</span> <b style='color: navy;'>TW Trịnh Thăng Bình</b>" if has_p2 else "▢ <span style='font-weight:normal; color:#555;'>TW Trịnh Thăng Bình</span>"
            
            has_p3 = "✅" in str(row.get(COLS_SAN_PHAM[2], ''))
            b3 = "<span style='color: #D49A00;'>✔</span> <b style='color: #D49A00;'>BD Đinh Mạnh Ninh</b>" if has_p3 else "▢ <span style='font-weight:normal; color:#555;'>BD Đinh Mạnh Ninh</span>"
            
            has_p4 = "✅" in str(row.get(COLS_SAN_PHAM[3], ''))
            b4 = "<span style='color: #D49A00;'>✔</span> <b style='color: #D49A00;'>TW Đinh Mạnh Ninh</b>" if has_p4 else "▢ <span style='font-weight:normal; color:#555;'>TW Đinh Mạnh Ninh</span>"

            # Gắn data vào khung (Dùng Flexbox chia 2 bên trái/phải)
            html_content += f"""
            <div class="label-box">
                <div class="title">📦 MÃ VĐ: {mvd}</div>
                <div class="info">👤 <b>{ten}</b> <br>📞 {sdt}</div>
                <div class="info">🏠 {diachi}</div>
                
                <!-- Bố cục chia 2 cột -->
                <div class="products" style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;">
                    <div style="flex: 1; padding-right: 5px;">
                        <div style="margin-bottom: 4px;">{b1}</div>
                        <div style="margin-bottom: 4px;">{b2}</div>
                    </div>
                    <div style="flex: 1; padding-left: 5px;">
                        <div style="margin-bottom: 4px;">{b3}</div>
                        <div style="margin-bottom: 4px;">{b4}</div>
                    </div>
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
