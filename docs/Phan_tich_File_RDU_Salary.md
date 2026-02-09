# 📊 Phân Tích Chi Tiết File RDU Salary

**Ngày phân tích:** 9 Tháng 2, 2026  
**File nguồn:** `test_RDU_Salary.xlsx`  
**File JSON:** `output_test_RDU_Salary.json`  
**Môi trường:** salary-ver3-env

---

## 🎯 Tổng Quan

### Thông Tin File

| Thuộc tính | Giá trị |
|------------|---------|
| **Tổng số sheets** | 11 sheets |
| **Tổng số dòng JSON** | 183,000 dòng |
| **Tổng số công thức** | 2,603 công thức Excel |
| **Kích thước file** | ~20-30 MB (JSON) |
| **Mục đích** | Hệ thống tính lương tổng hợp RDU tháng 11/2025 |

### Mô Tả Hệ Thống

Đây là file Excel lương tổng hợp của công ty RDU (Robotics Development Unit), bao gồm:
- Bảng lương chính với đầy đủ các khoản thu nhập
- Các bảng phụ: Chấm công, gửi xe, hỗ trợ cơm, thưởng/phạt
- Phiếu lương cá nhân
- Bảng hạch toán cho kế toán
- Đề nghị thanh toán (ĐNTT)

---

## 📑 Cấu Trúc 11 Sheets

### Tổng Quan Các Sheet

| STT | Tên Sheet | Số Dòng | Số Cột | Mô Tả | Số Formulas |
|-----|-----------|---------|--------|-------|-------------|
| 1 | **0.Bang luong T11** | 136 | 110 | 🌟 Bảng lương chính | 1,037 |
| 2 | **RDU T11** | 26 | 108 | Bảng tổng hợp lương RDU | 959 |
| 3 | **1.BCC** | 40 | 107 | Bảng chấm công (BCC) | 319 |
| 4 | **2.Gui xe** | 32 | 31 | Hỗ trợ gửi xe | 42 |
| 5 | **3.Ho tro com** | 6 | 39 | Hỗ trợ tiền cơm | 7 |
| 6 | **4.Hach toan luong** | 34 | 39 | Hạch toán kế toán | 122 |
| 7 | **5. ĐNTT** | 25 | 22 | Đề nghị thanh toán | 3 |
| 8 | **4. Tru thuong vi pham** | 19 | 10 | Trừ thưởng vi phạm | 52 |
| 9 | **NPT** | 19 | 10 | Nhân viên NPT | 16 |
| 10 | **Phieuluong** | 2 | 50 | Template phiếu lương | 46 |
| 11 | **Sheet2** | 112 | 1 | Dữ liệu phụ/tạm | 0 |

---

## 📋 Chi Tiết Từng Sheet

### 1. 🌟 Sheet: "0.Bang luong T11" (Bảng Lương Chính)

**Mô tả:** Sheet quan trọng nhất, chứa toàn bộ thông tin lương của nhân viên

**Thông tin:**
- **Số dòng:** 136 dòng
- **Số cột:** 110 cột (A-DH)
- **Header row:** Dòng 10
- **Data rows:** Dòng 13-136
- **Công thức:** 1,037 công thức Excel

#### Cấu Trúc Cột (Top 30 cột quan trọng)

| STT | Cột | Tên Cột | Ý Nghĩa | Data Type |
|-----|-----|---------|---------|-----------|
| 1 | A | STT | Số thứ tự | Formula |
| 2 | B | Mã nhân viên | Mã NV (RDU-XXX) | String |
| 3 | C | Họ và tên | Họ tên đầy đủ | String |
| 4 | D | Chức danh | Vị trí công việc | String |
| 5 | E | Phòng ban | Phòng ban/Bộ phận | String |
| 6 | F | Dự án (nếu có) | Tên dự án | String |
| 7 | G | Tình trạng hợp đồng | Chính thức/Thử việc | String |
| 8 | H | Tình trạng BHXH | Có/Không | String |
| 9 | I | Ngày bắt đầu | Ngày vào làm | Date |
| 10 | J | Ngày ký HDLD | Ngày ký hợp đồng | Date |
| 11 | K | Ngày kết thúc HĐ | Ngày hết hạn HĐ | Date |
| 12 | L | Hệ số thử việc | Hệ số nếu đang thử việc | Number |
| 13 | M | Thu nhập thỏa thuận | Lương cơ bản tháng | Number |
| 14 | N | Phụ cấp ăn trưa | Tiền cơm trưa | Number |
| 15 | O | Tổng thu nhập | =M+N | Formula |
| 16-30 | P-AD | Các khoản khác | Lương thực tế, BHXH, BHYT, thuế... | Mixed |

#### Các Nhóm Cột Chính

**A. Thông tin cá nhân (Cột A-K):**
- Mã NV, Họ tên, Chức danh, Phòng ban
- Thông tin hợp đồng, BHXH
- Ngày tháng quan trọng

**B. Thu nhập cơ bản (Cột M-O):**
- Thu nhập thỏa thuận (lương cơ bản)
- Phụ cấp ăn trưa
- Tổng thu nhập

**C. Chấm công & tính lương (Cột P-Z ước tính):**
- Số ngày công chuẩn
- Số ngày công thực tế
- Các loại ngày nghỉ (phép, lễ, ốm...)
- Lương thực tế theo công

**D. Các khoản phụ cấp & thưởng (Cột AA-AM ước tính):**
- Phụ cấp chức vụ
- Phụ cấp độc hại
- Thưởng hiệu suất
- Thưởng đánh giá
- OT (làm thêm giờ)

**E. Các khoản trừ (Cột AN-AX ước tính):**
- BHXH (8%)
- BHYT (1.5%)
- BHTN (1%)
- Thuế TNCN
- Các khoản trừ khác (vi phạm, tạm ứng...)

**F. Thực lãnh (Cột AY-BD ước tính):**
- Tổng thu nhập
- Tổng các khoản trừ
- Thực lãnh = Thu nhập - Trừ

#### Sample Data (Dòng 13)

```json
{
    "row": 13,
    "STT": 1,
    "Mã_nhân_viên": "RDU-001",
    "Họ_và_tên": "Lê Đình Dũng",
    "Chức_danh": "Giám đốc",
    "Phòng_ban": "BOD",
    "Thu_nhập_thỏa_thuận": 5592000,
    "Phụ_cấp_ăn_trưa": 11688000,
    "Tổng_thu_nhập": 17280000  // =SUM(M13:N13)
}
```

#### Các Công Thức Quan Trọng

```excel
# STT tự động
A13: =IF(C13="","",SUBTOTAL(3,$C$13:C13))

# Tổng thu nhập
O13: =SUM(M13:N13)

# Tổng cộng (summary row)
M15: =SUM(M13:M14)
N15: =SUM(N13:N14)
O15: =SUM(O13:O14)
```

---

### 2. Sheet: "RDU T11"

**Mô tả:** Bảng tổng hợp lương RDU tháng 11

**Thông tin:**
- **Số dòng:** 26 dòng
- **Số cột:** 108 cột
- **Công thức:** 959 công thức
- **Mục đích:** Tổng hợp và kiểm tra số liệu từ bảng lương chính

**Đặc điểm:**
- Có nhiều công thức VLOOKUP tham chiếu đến "0.Bang luong T11"
- Tính toán tổng, trung bình theo phòng ban
- Summary report cho management

---

### 3. Sheet: "1.BCC" (Bảng Chấm Công)

**Mô tả:** Bảng chấm công chi tiết theo ngày trong tháng

**Thông tin:**
- **Số dòng:** 40 dòng
- **Số cột:** 107 cột
- **Header row:** Dòng 3
- **Công thức:** 319 công thức

#### Cấu Trúc Cột

| Cột | Tên | Mô Tả |
|-----|-----|-------|
| A | STT | Số thứ tự |
| B | ID | Mã nhân viên |
| C | HỌ TÊN | Tên nhân viên |
| D | CHỨC DANH | Vị trí |
| E | PHÒNG BAN | Bộ phận |
| F | Ngày tính công tháng 11/2025 | Số ngày công chuẩn |
| G-CZ | Ngày 1-31 | Chấm công từng ngày (X, P, L, O...) |
| CA-CG | Tổng hợp | Tổng các loại công (đi làm, phép, lễ...) |

**Ký hiệu chấm công:**
- `X`: Đi làm
- `P`: Nghỉ phép
- `L`: Nghỉ lễ
- `O`: Nghỉ ốm
- `K`: Nghỉ không lương
- `1/2`: Nửa ngày
- Trống: Không dữ liệu

**Ví dụ:**
```
RDU-001 | Lê Đình Dũng | 1: X | 2: X | 3: P | 4: X | ... | Tổng: 22 công
```

---

### 4. Sheet: "2.Gui xe" (Hỗ Trợ Gửi Xe)

**Mô tả:** Tính toán hỗ trợ phí gửi xe cho nhân viên

**Thông tin:**
- **Số dòng:** 32 dòng
- **Số cột:** 31 cột
- **Header row:** Dòng 3
- **Công thức:** 42 công thức

#### Cấu Trúc Cột

| Cột | Tên | Ý Nghĩa |
|-----|-----|---------|
| A | STT | Số thứ tự |
| B | Mã nhân viên | ID nhân viên |
| C | Họ và tên | Tên đầy đủ |
| D | Chức danh | Vị trí công việc |
| E | Phòng ban | Bộ phận |
| F | Cấp bậc | Cấp bậc trong công ty |
| G | Nhóm cấp bậc | A, B, C, D... |
| H | Loại xe đăng ký | Xe máy/Xe đạp/Ô tô |
| I | Định mức hỗ trợ | Số tiền hỗ trợ theo cấp bậc |
| J | Số ngày đi làm | Số ngày công thực tế |
| K | Số tiền hỗ trợ gửi xe | =I × J / 26 |

**Định mức hỗ trợ (ví dụ):**
- Cấp A: 300,000 vnđ/tháng
- Cấp B: 250,000 vnđ/tháng
- Cấp C: 200,000 vnđ/tháng
- Cấp D: 150,000 vnđ/tháng

**Công thức tính:**
```
Hỗ trợ gửi xe = Định mức × (Số ngày đi làm / 26)
```

---

### 5. Sheet: "3.Ho tro com" (Hỗ Trợ Tiền Cơm)

**Mô tả:** Tính tiền hỗ trợ ăn trưa cho nhân viên

**Thông tin:**
- **Số dòng:** 6 dòng (nhỏ - có thể là summary)
- **Số cột:** 39 cột
- **Header row:** Dòng 2
- **Công thức:** 7 công thức

#### Cấu Trúc Cột

| Cột | Tên | Ý Nghĩa |
|-----|-----|---------|
| A | STT | Số thứ tự |
| B | Mã nhân viên | ID |
| C | Họ và tên | Tên NV |
| D | Số ngày công thực tế | Ngày đi làm |
| E | Số ngày cơm nhà máy | Ăn tại công ty |
| F | Số ngày cơm chi vào lương | Nhận tiền thay vì ăn |
| G | Định mức hỗ trợ cơm | VD: 40,000 vnđ/suất |
| H | Thành tiền | =G × (D hoặc F) |
| I-AK | Ngày T4-T12 | Chi tiết theo ngày tuần |

**Công thức tính:**
```
Tiền hỗ trợ cơm = Định mức × Số ngày được hỗ trợ
```

**Lưu ý:**
- Nhân viên có thể chọn ăn tại công ty HOẶC nhận tiền
- Nếu nghỉ thì không được hỗ trợ ngày đó

---

### 6. Sheet: "4.Hach toan luong" (Hạch Toán Kế Toán)

**Mô tả:** Bảng tổng hợp cho phòng kế toán hạch toán lương

**Thông tin:**
- **Số dòng:** 34 dòng
- **Số cột:** 39 cột
- **Header row:** Dòng 8
- **Công thức:** 122 công thức

#### Cấu Trúc Cột

| Cột | Tên | Ý Nghĩa |
|-----|-----|---------|
| A | STT | Số thứ tự |
| B | Bộ phận | Phòng ban/Cost center |
| C | Thu nhập tháng Q1 | Lương cơ bản |
| D | Phụ cấp cơm trưa | Tiền cơm |
| E | OT | Tiền làm thêm giờ |
| F | Trợ cấp khác | Xăng xe, điện thoại, di chuyển... |
| G | Thu nhập khác | Thưởng sáng kiến, thưởng... |
| H | Tổng lương (1) | Tổng thu nhập |
| I | Khoản trích công ty (2) | BHXH, BHYT do công ty chịu |
| J-AM | Chi tiết hạch toán | Các TK kế toán 334, 338, 642... |

**Mục đích:**
- Tổng hợp lương theo bộ phận
- Phân bổ chi phí lương vào các tài khoản kế toán
- Tính tổng chi phí nhân sự công ty phải trả

**Công thức:**
```
Tổng chi phí nhân sự = Lương trả NV + BHXH/BHYT công ty đóng
```

---

### 7. Sheet: "5. ĐNTT" (Đề Nghị Thanh Toán)

**Mô tả:** Phiếu đề nghị thanh toán lương cho từng nhân viên

**Thông tin:**
- **Số dòng:** 25 dòng
- **Số cột:** 22 cột
- **Header row:** Dòng 6
- **Công thức:** 3 công thức

**Mục đích:**
- Template phiếu đề nghị thanh toán cá nhân
- Dùng để xin phê duyệt trước khi chuyển lương
- In ra và ký duyệt

**Cấu trúc:**
```
Họ tên: [Tên NV]
Mã nhân viên: [Mã]
Bộ phận: [Phòng ban]

Chi tiết:
- Lương cơ bản: XXX
- Phụ cấp: XXX
- Thưởng: XXX
- Trừ: XXX
--------------
Thực lãnh: XXX

Người đề nghị: [Ký]
Người phê duyệt: [Ký]
```

---

### 8. Sheet: "4. Tru thuong vi pham" (Trừ Thưởng Vi Phạm)

**Mô tả:** Bảng tính trừ lương do vi phạm nội quy

**Thông tin:**
- **Số dòng:** 19 dòng
- **Số cột:** 10 cột
- **Header rows:** Dòng 3-4 (merged header)
- **Công thức:** 52 công thức

#### Cấu Trúc Cột

| Cột | Tên | Ý Nghĩa |
|-----|-----|---------|
| A | STT | Số thứ tự |
| B | Mã nhân viên | ID |
| C | Họ và tên | Tên NV |
| D | Chức danh | Vị trí |
| E | Phòng ban | Bộ phận |
| F | Thưởng đánh giá tháng | Thưởng gốc |
| G | Trừ vi phạm - Chấm công | Trừ do đi muộn, về sớm |
| H | Trừ vi phạm - Tuân thủ | Trừ do vi phạm nội quy |
| I | Tổng trừ | =G+H |
| J | Thưởng thực tế | =F-I |

**Công thức:**
```excel
# STT tự động
A5: =IF(B5="","",SUBTOTAL(3,$B$5:B5))

# Lookup thưởng từ bảng lương chính
F5: =VLOOKUP(B5,'0.Bang luong T11'!$B$13:$AH$13,33,0)

# Tổng trừ
I5: =SUM(G5:H5)

# Thưởng còn lại
J5: =F5-I5
```

**Các loại vi phạm:**
- Đi muộn/về sớm
- Không tuân thủ 6S
- Vi phạm quy trình
- Không đeo thẻ
- Vi phạm an toàn

---

### 9. Sheet: "NPT"

**Mô tả:** Bảng lương nhân viên NPT (có thể là bộ phận riêng hoặc nhân viên part-time)

**Thông tin:**
- **Số dòng:** 19 dòng
- **Số cột:** 10 cột
- **Công thức:** 16 công thức

**Cấu trúc tương tự sheet "4. Tru thuong vi pham"**

---

### 10. Sheet: "Phieuluong" (Template Phiếu Lương)

**Mô tả:** Template mẫu phiếu lương in ra cho nhân viên

**Thông tin:**
- **Số dòng:** 2 dòng (template)
- **Số cột:** 50 cột
- **Công thức:** 46 công thức

**Mục đích:**
- Template để in phiếu lương cho từng nhân viên
- Chứa công thức VLOOKUP để lấy dữ liệu từ bảng chính
- In ra và phát cho nhân viên cuối tháng

**Cấu trúc phiếu lương:**
```
CÔNG TY TNHH RDU
PHIẾU LƯƠNG THÁNG 11/2025

Họ tên: [=VLOOKUP...]
Mã NV: [=VLOOKUP...]
Chức danh: [=VLOOKUP...]

THU NHẬP:
  Lương cơ bản:        [số tiền]
  Phụ cấp:            [số tiền]
  Thưởng:             [số tiền]
  OT:                 [số tiền]
  Tổng thu nhập:      [số tiền]

CÁC KHOẢN TRỪ:
  BHXH (8%):          [số tiền]
  BHYT (1.5%):        [số tiền]
  BHTN (1%):          [số tiền]
  Thuế TNCN:          [số tiền]
  Khác:               [số tiền]
  Tổng trừ:           [số tiền]

THỰC LÃNH:            [số tiền]

Ngày in: [DATE]
```

---

### 11. Sheet: "Sheet2"

**Mô tả:** Sheet dữ liệu phụ/tạm thời

**Thông tin:**
- **Số dòng:** 112 dòng
- **Số cột:** 1 cột
- **Công thức:** 0 công thức

**Đặc điểm:**
- Có thể là dữ liệu import tạm
- Hoặc lookup table
- Hoặc notes/ghi chú

---

## 🔧 Công Thức Excel Quan Trọng

### 1. Công Thức VLOOKUP

**Mục đích:** Tìm kiếm dữ liệu từ bảng khác

```excel
# Lookup thưởng từ bảng lương chính
=VLOOKUP(B5,'0.Bang luong T11'!$B$13:$AH$13,33,0)

# Tham số:
# - B5: Mã nhân viên cần tìm
# - '0.Bang luong T11'!$B$13:$AH$13: Vùng dữ liệu
# - 33: Lấy cột thứ 33 (cột AG)
# - 0: Tìm kiếm chính xác
```

### 2. Công Thức SUBTOTAL

**Mục đích:** Đếm số thứ tự tự động (bỏ qua ô ẩn)

```excel
=IF(B5="","",SUBTOTAL(3,$B$5:B5))

# SUBTOTAL(3, range): Đếm số ô không rỗng
# Nếu B5 rỗng → STT = rỗng
# Nếu B5 có giá trị → STT = số lượng từ B5 đến hàng hiện tại
```

### 3. Công Thức SUM

**Mục đích:** Tính tổng

```excel
# Tổng thu nhập
=SUM(M13:N13)

# Tổng trừ
=SUM(G5:H5)

# Tổng dọc
=SUM(M13:M136)
```

### 4. Công Thức IF

**Mục đích:** Điều kiện

```excel
=IF(B5="","",VLOOKUP(...))

# Nếu B5 rỗng → trả về rỗng
# Nếu B5 có giá trị → thực hiện VLOOKUP
```

### 5. Các Công Thức Tính Lương

```excel
# Lương thực tế theo công
=Thu_nhập_thỏa_thuận × (Số_công_thực_tế / Số_công_chuẩn)

# BHXH (8%)
=Lương_đóng_BHXH × 8%

# BHYT (1.5%)
=Lương_đóng_BHXH × 1.5%

# BHTN (1%)
=Lương_đóng_BHXH × 1%

# Thuế TNCN (bậc thang)
=IF(Thu_nhập_tính_thuế <= 5000000, 0,
   IF(Thu_nhập_tính_thuế <= 10000000, 
      (Thu_nhập_tính_thuế - 5000000) × 5%,
      ...))

# Thực lãnh
=Tổng_thu_nhập - (BHXH + BHYT + BHTN + Thuế_TNCN + Các_khoản_trừ_khác)
```

---

## 📊 Data Flow (Luồng Dữ Liệu)

### Sơ Đồ Luồng

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT DATA SOURCES                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌──────────┐  ┌──────────┐
        │  1.BCC    │  │ 2.Gui xe │  │ 3.Cơm    │
        │ (Chấm công│  │(Gửi xe)  │  │(Ăn trưa) │
        └───────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │ 0.Bang luong T11 │ ◄─── VLOOKUP ───┐
                    │  (Bảng lương)    │                  │
                    └──────────────────┘                  │
                              │                           │
                ┌─────────────┼─────────────┐            │
                │             │             │             │
                ▼             ▼             ▼             │
        ┌───────────┐  ┌──────────┐  ┌──────────┐       │
        │  RDU T11  │  │4.Tru/phạt│  │   NPT    │───────┘
        │ (Summary) │  │(Vi phạm) │  │(Nhân viên│
        └───────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │ 4.Hach toan luong│
                    │   (Kế toán)      │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌──────────┐  ┌──────────┐
        │Phieuluong │  │ 5.ĐNTT   │  │Print/Pay │
        │(In phiếu) │  │(Thanh toán│  │(Chuyển $)│
        └───────────┘  └──────────┘  └──────────┘
```

### Giải Thích Luồng

**1. Input (Thu thập dữ liệu):**
- Chấm công từ máy chấm công → Sheet "1.BCC"
- Đăng ký gửi xe → Sheet "2.Gui xe"
- Đăng ký ăn cơm → Sheet "3.Ho tro com"

**2. Processing (Xử lý):**
- Dữ liệu được tổng hợp vào "0.Bang luong T11"
- Tính toán lương, phụ cấp, BHXH, thuế
- Áp dụng công thức phức tạp

**3. Cross-reference (Tham chiếu chéo):**
- Sheet "4.Tru thuong vi pham" dùng VLOOKUP lấy dữ liệu từ "0.Bang luong T11"
- Sheet "NPT" tương tự
- Sheet "RDU T11" tổng hợp lại

**4. Output (Kết quả):**
- "4.Hach toan luong": Cho kế toán hạch toán
- "Phieuluong": In phát cho nhân viên
- "5.ĐNTT": Đề nghị thanh toán, phê duyệt
- Cuối cùng: Chuyển lương vào tài khoản

---

## 🎯 Use Cases cho AI Agent

### 1. Query Thông Tin

```python
# Truy vấn lương của 1 nhân viên
"Cho tôi thông tin lương của nhân viên RDU-001"

# Truy vấn theo phòng ban
"Tổng lương phòng Phát triển SP là bao nhiêu?"

# Truy vấn chấm công
"Nhân viên RDU-007 có bao nhiêu ngày công tháng 11?"
```

### 2. Tính Toán & Phân Tích

```python
# Tính tổng chi phí nhân sự
"Tính tổng chi phí nhân sự tháng 11 (bao gồm BHXH công ty đóng)"

# So sánh
"So sánh lương trung bình giữa các phòng ban"

# Phân tích xu hướng
"Những nhân viên nào có số công thấp?"
```

### 3. Validation

```python
# Kiểm tra công thức
"Kiểm tra xem công thức tính BHXH có đúng không?"

# Kiểm tra dữ liệu
"Có nhân viên nào có lương âm không?"

# Kiểm tra consistency
"So sánh tổng lương trong bảng chính với bảng hạch toán"
```

### 4. Generate Reports

```python
# Tạo báo cáo
"Tạo báo cáo tổng hợp lương tháng 11 theo phòng ban"

# Export
"Export danh sách nhân viên bị trừ lương do vi phạm"

# Tạo phiếu lương
"Tạo phiếu lương cho nhân viên RDU-001"
```

### 5. Anomaly Detection

```python
# Phát hiện bất thường
"Tìm các nhân viên có lương thực lãnh > 50 triệu"

# Phát hiện lỗi
"Tìm các ô có lỗi #N/A hoặc #VALUE"

# Kiểm tra hợp lý
"Nhân viên nào có BHXH > 20% lương?"
```

---

## 📈 Thống Kê Tổng Hợp

### Thống Kê Cơ Bản

```python
{
    "total_sheets": 11,
    "total_rows": 451,
    "total_columns": 535,
    "total_cells": ~47,000,
    "total_formulas": 2603,
    "json_file_size": "~25 MB",
    "json_lines": 183000
}
```

### Phân Bố Công Thức

| Sheet | Số Formulas | % |
|-------|-------------|---|
| 0.Bang luong T11 | 1,037 | 39.8% |
| RDU T11 | 959 | 36.8% |
| 1.BCC | 319 | 12.3% |
| 4.Hach toan luong | 122 | 4.7% |
| Khác | 166 | 6.4% |
| **Tổng** | **2,603** | **100%** |

### Complexity Score

```python
Complexity = (Sheets × Formulas × Cross_references) / 1000

= (11 × 2603 × 5) / 1000
= 143 điểm

→ Độ phức tạp: VERY HIGH ⚠️
```

**Các yếu tố phức tạp:**
- ✅ 11 sheets liên kết với nhau
- ✅ 2,603 công thức Excel
- ✅ Nhiều VLOOKUP cross-sheet
- ✅ Formulas phức tạp (nested IF, SUBTOTAL...)
- ✅ 110 cột trong bảng chính

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Lỗi #N/A

**Nguyên nhân:**
```excel
F5: =VLOOKUP(B5,'0.Bang luong T11'!$B$13:$AH$13,33,0)
→ Value: "#N/A"
```

**Lý do:**
- Mã nhân viên trong sheet "4.Tru thuong vi pham" không tìm thấy trong bảng chính
- Hoặc vùng lookup sai (dòng 13 thay vì 13:136)
- Hoặc cột 33 nằm ngoài range $B$13:$AH$13

**Giải pháp:**
```excel
# Sửa range
=VLOOKUP(B5,'0.Bang luong T11'!$B$13:$AH$136,33,0)

# Hoặc dùng IFERROR
=IFERROR(VLOOKUP(B5,'0.Bang luong T11'!$B$13:$AH$13,33,0), 0)
```

### 2. Performance Issues

**Vấn đề:**
- File 183,000 dòng JSON → Load chậm
- 2,603 formulas → Recalculate chậm

**Giải pháp:**
```python
# Streaming parse thay vì load toàn bộ
import ijson

with open('output_test_RDU_Salary.json', 'rb') as f:
    for sheet_name, sheet_data in ijson.kvitems(f, ''):
        # Process từng sheet
        process_sheet(sheet_name, sheet_data)
```

### 3. Datetime Handling

**Lưu ý:**
- Ngày tháng đã được convert sang ISO format
- VD: "2025-11-01T00:00:00"

**Parse:**
```python
from datetime import datetime

date_str = "2025-11-01T00:00:00"
date_obj = datetime.fromisoformat(date_str)
```

### 4. Cross-Sheet References

**Vấn đề:**
- Nhiều sheet tham chiếu lẫn nhau
- Nếu sửa 1 sheet → ảnh hưởng các sheet khác

**Giải pháp:**
- Validate toàn bộ file trước khi modify
- Backup before making changes
- Test trên copy trước

---

## 🛠️ Code Examples

### 1. Load và Parse JSON

```python
import json
from datetime import datetime

# Load file
with open('output_test_RDU_Salary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access sheet
bang_luong = data['0.Bang luong T11']

# Get headers (dòng 10, index 9)
headers = [cell['value'] for cell in bang_luong['data'][9]]

# Get employee data (dòng 13+, index 12+)
employees = []
for row in bang_luong['data'][12:]:  # Bỏ qua header và summary
    if row[1]['value']:  # Có mã nhân viên
        emp = {
            'ma_nv': row[1]['value'],
            'ho_ten': row[2]['value'],
            'chuc_danh': row[3]['value'],
            'phong_ban': row[4]['value'],
            'thu_nhap': row[12]['value']  # Cột M
        }
        employees.append(emp)

print(f"Tổng số nhân viên: {len(employees)}")
```

### 2. Truy Vấn Thông Tin

```python
def get_employee_info(data, ma_nv):
    """Lấy thông tin lương của 1 nhân viên"""
    bang_luong = data['0.Bang luong T11']
    
    for row in bang_luong['data'][12:]:
        if row[1]['value'] == ma_nv:
            return {
                'Mã NV': row[1]['value'],
                'Họ tên': row[2]['value'],
                'Chức danh': row[3]['value'],
                'Phòng ban': row[4]['value'],
                'Thu nhập TT': row[12]['value'],
                'Phụ cấp cơm': row[13]['value'],
                'Tổng thu nhập': row[14]['value']
            }
    return None

# Sử dụng
info = get_employee_info(data, 'RDU-001')
print(info)
```

### 3. Tính Tổng Lương Theo Phòng Ban

```python
from collections import defaultdict

def salary_by_department(data):
    """Tổng lương theo phòng ban"""
    bang_luong = data['0.Bang luong T11']
    dept_salary = defaultdict(float)
    
    for row in bang_luong['data'][12:]:
        ma_nv = row[1]['value']
        if ma_nv:
            phong_ban = row[4]['value']
            thu_nhap = row[14]['value']  # Tổng thu nhập
            
            if isinstance(thu_nhap, (int, float)):
                dept_salary[phong_ban] += thu_nhap
    
    return dict(dept_salary)

# Sử dụng
summary = salary_by_department(data)
for dept, total in sorted(summary.items(), key=lambda x: x[1], reverse=True):
    print(f"{dept:30s}: {total:>15,.0f} VNĐ")
```

### 4. Tìm Lỗi #N/A

```python
def find_na_errors(data):
    """Tìm tất cả các ô có lỗi #N/A"""
    errors = []
    
    for sheet_name, sheet_data in data.items():
        for i, row in enumerate(sheet_data['data']):
            for cell in row:
                if cell['value'] == '#N/A':
                    errors.append({
                        'sheet': sheet_name,
                        'cell': cell['cell'],
                        'formula': cell['formula']
                    })
    
    return errors

# Sử dụng
na_errors = find_na_errors(data)
print(f"Tìm thấy {len(na_errors)} lỗi #N/A:")
for err in na_errors[:10]:  # Show first 10
    print(f"  {err['sheet']} - {err['cell']}: {err['formula']}")
```

### 5. Export Sang CSV

```python
import csv

def export_to_csv(data, sheet_name, output_file):
    """Export 1 sheet sang CSV"""
    sheet = data[sheet_name]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        for row in sheet['data']:
            row_values = [cell['value'] for cell in row]
            writer.writerow(row_values)
    
    print(f"Đã export {sheet_name} → {output_file}")

# Sử dụng
export_to_csv(data, '0.Bang luong T11', 'bang_luong_T11.csv')
```

---

## 🔐 Security & Privacy

### Dữ Liệu Nhạy Cảm

File này chứa thông tin cá nhân và tài chính:
- ✅ Họ tên, mã nhân viên
- ✅ Lương, thu nhập
- ✅ CMND/CCCD (nếu có)
- ✅ Số tài khoản ngân hàng (nếu có)

### Best Practices

**1. Access Control:**
```python
# Chỉ cho phép HR và kế toán truy cập
ALLOWED_USERS = ['hr_manager', 'accountant', 'cfo']

def check_permission(user):
    if user not in ALLOWED_USERS:
        raise PermissionError("Không có quyền truy cập")
```

**2. Data Masking:**
```python
def mask_sensitive_data(data):
    """Che dữ liệu nhạy cảm khi demo"""
    for row in data['0.Bang luong T11']['data'][12:]:
        # Mask tên
        ho_ten = row[2]['value']
        if ho_ten:
            row[2]['value'] = ho_ten[0] + '*' * (len(ho_ten)-1)
        
        # Mask lương (chỉ hiện 2 số đầu)
        thu_nhap = row[12]['value']
        if isinstance(thu_nhap, (int, float)):
            row[12]['value'] = f"{str(int(thu_nhap))[:2]}***"
    
    return data
```

**3. Audit Log:**
```python
import logging

logging.info(f"User {username} accessed salary data at {datetime.now()}")
```

---

## 📚 Tài Liệu Liên Quan

### Files trong Project

- [test_excel.py](../tests/test_excel.py) - Hàm đọc/ghi Excel ↔️ JSON
- [test_RDU_Salary.xlsx](../tests/data/test_RDU_Salary.xlsx) - File Excel gốc
- [output_test_RDU_Salary.json](../tests/data/output_test_RDU_Salary.json) - File JSON output
- [Phan_tich_file_Excel_va_Output_JSON.md](Phan_tich_file_Excel_va_Output_JSON.md) - Phân tích cấu trúc chung
- [Huong_dan_Convert_JSON_Excel.md](Huong_dan_Convert_JSON_Excel.md) - Hướng dẫn convert

### External Resources

- [OpenPyXL Documentation](https://openpyxl.readthedocs.io/)
- [Pandas Excel I/O](https://pandas.pydata.org/docs/reference/io.html#excel)
- [Excel Formula Reference](https://support.microsoft.com/en-us/office/excel-functions-alphabetical-b3944572-255d-4efb-bb96-c6d90033e188)

---

## ✅ Checklist Xử Lý

Khi làm việc với file RDU Salary JSON:

### Pre-processing
- [ ] Validate JSON structure
- [ ] Check file size và memory requirements
- [ ] Backup file gốc
- [ ] Check quyền truy cập

### Processing
- [ ] Parse JSON đúng encoding (UTF-8)
- [ ] Handle datetime format
- [ ] Handle #N/A errors
- [ ] Validate cross-sheet references

### Post-processing
- [ ] Verify output data
- [ ] Check tổng cộng matches
- [ ] Test formulas nếu convert về Excel
- [ ] Audit log

### Security
- [ ] Mask sensitive data nếu demo
- [ ] Encrypt file nếu cần
- [ ] Xóa temporary files
- [ ] Log access

---

## 🎓 Kết Luận

### Điểm Mạnh

✅ **Cấu trúc rõ ràng:**
- 11 sheets phân chia theo chức năng
- Headers và metadata đầy đủ
- Formulas được preserve

✅ **Dữ liệu đầy đủ:**
- 2,603 công thức Excel được lưu
- Cell-level granularity
- Datetime được format chuẩn

✅ **Dễ xử lý:**
- JSON structure well-formed
- Consistent naming
- Easy to parse

### Điểm Cần Cải Thiện

⚠️ **Performance:**
- File quá lớn (183K lines)
- Nên optimize cho large file

⚠️ **Errors:**
- Có lỗi #N/A trong formulas
- Cần fix VLOOKUP ranges

⚠️ **Documentation:**
- Thiếu data dictionary
- Cần document business logic

### Khuyến Nghị

**1. Tối ưu file:**
```python
# Nén JSON
import gzip
with gzip.open('output.json.gz', 'wt', encoding='utf-8') as f:
    json.dump(data, f)
```

**2. Fix errors:**
```python
# Fix VLOOKUP ranges
# Sửa từ $B$13:$AH$13 → $B$13:$AH$136
```

**3. Add validation:**
```python
# Validate tổng lương
assert sum(all_salaries) == expected_total
```

---

**Tạo bởi:** Salary Agent Ver3  
**Phân tích:** File test_RDU_Salary.xlsx → output_test_RDU_Salary.json  
**Cập nhật:** 9 Tháng 2, 2026  
**Version:** 1.0
