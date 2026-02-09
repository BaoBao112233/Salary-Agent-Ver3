# 📊 Phân Tích File Excel và Cấu Trúc Output JSON

**Ngày phân tích:** 9 Tháng 2, 2026  
**File nguồn:** `Báo_cáo_công_theo_ph_1770029168127.xlsx`  
**File đầu ra:** `output.json`  
**Môi trường:** salary-ver3-env

---

## 🎯 Tổng Quan

### Mục Đích
Hệ thống đọc và chuyển đổi dữ liệu từ file Excel chấm công sang định dạng JSON có cấu trúc, bao gồm:
- Lưu trữ đầy đủ thông tin ô (cell)
- Phát hiện và lưu trữ công thức Excel (nếu có)
- Lưu trữ cả giá trị đã tính toán
- Hỗ trợ xử lý datetime objects

### Thông Tin File Đầu Vào
- **Tên file:** Báo cáo công theo phân ca
- **Số sheet:** 1 sheet (sheet1)
- **Tổng số dòng:** 30 dòng
- **Tổng số cột:** 17 cột (A-Q)
- **Có công thức:** Không (tất cả các ô đều chứa giá trị tĩnh)

---

## 📁 Cấu Trúc Dữ Liệu Output JSON

### 1. Cấu Trúc Tổng Thể

```json
{
    "sheet_name": {
        "name": "Tên sheet",
        "data": [...],      // Dữ liệu từng ô chi tiết
        "formulas": [...],  // Công thức hoặc giá trị của từng ô
        "values": [...]     // Giá trị đã tính toán
    }
}
```

### 2. Cấu Trúc Chi Tiết Từng Ô (Cell)

Mỗi ô được lưu trữ dưới dạng object với các thuộc tính:

```json
{
    "cell": "A1",           // Địa chỉ ô (A1, B2, C3,...)
    "formula": null,        // Công thức Excel (nếu có) hoặc null
    "value": "Giá trị"      // Giá trị thực tế của ô
}
```

**Các trường hợp giá trị (value):**
- `string`: Văn bản thông thường
- `number`: Số (int hoặc float)
- `datetime`: Ngày giờ ở định dạng ISO 8601 (VD: "2026-02-02T09:00:00")
- `null`: Ô trống

### 3. Cấu Trúc Mảng Data

```javascript
"data": [
    [cell_A1, cell_B1, cell_C1, ...],  // Dòng 1
    [cell_A2, cell_B2, cell_C2, ...],  // Dòng 2
    [cell_A3, cell_B3, cell_C3, ...],  // Dòng 3
    ...
]
```

### 4. Mảng Formulas và Values

```javascript
"formulas": [
    [formula_A1, formula_B1, ...],  // Công thức dòng 1 (hoặc giá trị nếu không có công thức)
    [formula_A2, formula_B2, ...],  // Công thức dòng 2
    ...
]

"values": [
    [value_A1, value_B1, ...],      // Giá trị đã tính toán dòng 1
    [value_A2, value_B2, ...],      // Giá trị đã tính toán dòng 2
    ...
]
```

---

## 📋 Cấu Trúc Nội Dung File Báo Cáo Công

### Dòng 1: Tiêu Đề Chính
```
A1: "Báo cáo công theo phân ca"
B1-Q1: null (các ô trống)
```

### Dòng 2: Dòng Trống
```
A2-Q2: null (toàn bộ dòng trống)
```

### Dòng 3: Headers (Tiêu Đề Cột)

| STT | Cột | Tên Cột | Ý Nghĩa |
|-----|-----|---------|---------|
| 1 | A | Ngày | Ngày làm việc |
| 2 | B | Thứ trong tuần | Thứ 2, Thứ 3,... |
| 3 | C | Ca | Tên ca làm việc |
| 4 | D | Mã nhân viên | Mã định danh NV |
| 5 | E | Tên nhân viên | Họ và tên đầy đủ |
| 6 | F | Yêu cầu bắt đầu | Giờ vào ca theo quy định |
| 7 | G | Yêu cầu kết thúc | Giờ ra ca theo quy định |
| 8 | H | Checkin thực tế | Giờ checkin thực tế |
| 9 | I | Checkout thực tế | Giờ checkout thực tế |
| 10 | J | Thời gian Checkin | Thời điểm checkin hệ thống ghi nhận |
| 11 | K | Thời gian Checkout | Thời điểm checkout hệ thống ghi nhận |
| 12 | L | Tổng thời gian yêu cầu (phút) | Tổng thời gian ca theo quy định |
| 13 | M | Công quy đổi | Hệ số quy đổi công (thường là 1) |
| 14 | N | Tổng thời gian tính công (giờ) | Số giờ thực tế làm việc |
| 15 | O | Tổng số công | Số công đã hoàn thành (0-1) |
| 16 | P | Thời gian hữu ích (phút) | Thời gian làm việc hiệu quả |
| 17 | Q | Thời gian không hữu ích (phút) | Thời gian nghỉ/không làm |

### Dòng 4-30: Dữ Liệu Chi Tiết

Mỗi dòng chứa thông tin chấm công của 1 nhân viên trong 1 ca làm việc.

**Ví dụ dòng 4:**
```json
{
    "Ngày": "2026-02-02T00:00:00",
    "Thứ trong tuần": "Thứ Hai",
    "Ca": "Ca hành chính OXII",
    "Mã nhân viên": "00039",
    "Tên nhân viên": "Nguyễn Bùi Thịnh",
    "Yêu cầu bắt đầu": "2026-02-02T09:00:00",
    "Yêu cầu kết thúc": "2026-02-02T18:48:00",
    "Checkin thực tế": "2026-02-02T08:28:29",
    "Checkout thực tế": "2026-02-02T17:44:32",
    "Thời gian Checkin": "2026-02-02T08:28:29",
    "Thời gian Checkout": "2026-02-02T17:44:32",
    "Tổng thời gian yêu cầu (phút)": 588,
    "Công quy đổi": 1,
    "Tổng thời gian tính công (giờ)": 9.266666666666667,
    "Tổng số công": 0.9456556122448978,
    "Thời gian hữu ích (phút)": 457,
    "Thời gian không hữu ích (phút)": 98
}
```

---

## 🔧 Xử Lý Kỹ Thuật

### 1. Xử Lý Datetime Objects

**Vấn đề:** 
Datetime objects từ Excel không thể serialize trực tiếp sang JSON.

**Giải pháp:**
Sử dụng custom `DateTimeEncoder` class:

```python
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
```

**Kết quả:**
- Datetime được chuyển sang ISO 8601 format
- VD: `datetime(2026, 2, 2, 9, 0, 0)` → `"2026-02-02T09:00:00"`

### 2. Đọc Excel với OpenPyXL

**Kỹ thuật:**
- Load workbook 2 lần:
  - `data_only=False`: Để lấy công thức gốc
  - `data_only=True`: Để lấy giá trị đã tính toán

```python
wb_formula = openpyxl.load_workbook(file_path, data_only=False)
wb_values = openpyxl.load_workbook(file_path, data_only=True)
```

**Lợi ích:**
- Phát hiện được các công thức Excel (=SUM, =VLOOKUP,...)
- Lấy được cả giá trị đã tính và công thức gốc
- Không bị mất thông tin khi chuyển đổi

### 3. Cấu Trúc Cell-Based Storage

**Tại sao lưu từng ô riêng biệt?**
- Giữ nguyên vị trí chính xác của dữ liệu (A1, B2,...)
- Dễ dàng trace back về file Excel gốc
- Hỗ trợ phát hiện công thức và dependencies
- Linh hoạt trong việc xử lý ô trống

---

## 📊 Phân Tích Business Logic

### 1. Tính Toán Công

**Công thức:**
```
Tổng số công = Tổng thời gian tính công (giờ) / Số giờ quy định trong ca
```

**Ví dụ:**
- Ca làm 588 phút = 9.8 giờ
- Thực tế làm 9.27 giờ
- Tổng số công = 9.27 / 9.8 ≈ 0.946 công

### 2. Thời Gian Hữu Ích vs Không Hữu Ích

**Công thức:**
```
Thời gian hữu ích + Thời gian không hữu ích = 
    (Checkout thực tế - Checkin thực tế) tính bằng phút
```

**Ví dụ dòng 4:**
- Checkin: 08:28:29
- Checkout: 17:44:32
- Tổng: ~556 phút
- Hữu ích: 457 phút (82%)
- Không hữu ích: 98 phút (18%)

### 3. Xử Lý Checkin Sớm/Muộn

**Quan sát:**
- Yêu cầu: 09:00:00
- Thực tế: 08:28:29 (sớm 31 phút)
- Hệ thống vẫn tính công từ thời điểm checkin thực tế

**Ý nghĩa:**
- Khuyến khích nhân viên đến sớm
- Tính công đầy đủ cho thời gian làm việc thực tế

---

## 🎯 Ứng Dụng Thực Tế

### 1. AI Agent Salary Calculation

**Input:** File Excel báo cáo công  
**Process:** 
1. Đọc file Excel → JSON structure
2. AI Agent phân tích dữ liệu
3. Tính toán lương, phụ cấp, OT
4. Validation các công thức

**Output:** Báo cáo lương chi tiết

### 2. Các Tính Năng AI Agent Có Thể Làm

```python
# 1. Truy vấn thông tin
"Cho tôi thông tin chấm công của nhân viên 00039 ngày 2/2/2026"

# 2. Tính toán thống kê
"Tính tổng số công của tất cả nhân viên trong tháng 2"

# 3. Phát hiện bất thường
"Những nhân viên nào đi muộn quá 30 phút?"

# 4. Tính lương
"Tính lương cho nhân viên 00039 với công thức: 
 Lương = Số công × Lương cơ bản × Hệ số"

# 5. So sánh hiệu suất
"So sánh thời gian hữu ích giữa các nhân viên"
```

### 3. Formula Validation

**Mục đích:**
Validate các công thức tính công, lương có đúng hay không

**Ví dụ:**
```python
# Kiểm tra công thức tính công
assert (thời_gian_tính_công / thời_gian_yêu_cầu) == tổng_số_công

# Kiểm tra tổng thời gian
assert thời_gian_hữu_ích + thời_gian_không_hữu_ích == 
       (checkout - checkin).total_minutes()
```

---

## 🔍 Điểm Đặc Biệt

### 1. Xử Lý Multiple Data Types

File output.json xử lý được:
- ✅ String: "Thứ Hai", "Nguyễn Bùi Thịnh"
- ✅ Integer: 588, 1, 457
- ✅ Float: 9.266666666666667, 0.9456556122448978
- ✅ Datetime: "2026-02-02T09:00:00"
- ✅ Null: null

### 2. Cấu Trúc 3 Lớp (data, formulas, values)

**Tại sao cần 3 lớp?**

1. **data**: Thông tin đầy đủ nhất (cell address + formula + value)
   - Dùng cho: Debugging, tracing, full analysis
   
2. **formulas**: Công thức hoặc giá trị
   - Dùng cho: Formula validation, dependency analysis
   
3. **values**: Chỉ giá trị đã tính
   - Dùng cho: Quick data processing, calculations

**Lợi ích:**
- Linh hoạt cho nhiều use cases
- Tối ưu performance (chọn lớp phù hợp)
- Đầy đủ thông tin cho audit trail

### 3. Preserve Cell Position

**Ưu điểm:**
```json
"cell": "A4"  // Biết chính xác ô nào trong Excel
```

**Ứng dụng:**
- Sinh báo cáo Excel highlight lỗi
- Tạo link trực tiếp đến ô cụ thể
- Debug dễ dàng khi có vấn đề

---

## 📈 Thống Kê File

### Thống Kê Cơ Bản
- **Tổng số sheets:** 1
- **Tổng số dòng:** 30
- **Tổng số cột:** 17
- **Tổng số ô:** 510 ô (30 × 17)
- **Dòng header:** Dòng 3
- **Dòng dữ liệu:** Dòng 4-30 (27 dòng)

### Thống Kê Dữ Liệu
- **Số nhân viên:** ~27 nhân viên (có thể có duplicate nếu 1 NV làm nhiều ca)
- **Ngày làm việc:** 2026-02-02 (Thứ Hai)
- **Ca làm việc:** Ca hành chính OXII
- **Thời gian ca:** 588 phút (9.8 giờ)

### Thống Kê File JSON
- **Kích thước:** 3760 dòng JSON
- **Có công thức:** Không (tất cả ô đều giá trị tĩnh)
- **Encoding:** UTF-8
- **Format:** Pretty-print với indent 4 spaces

---

## 🛠️ Code Reference

### File Test Excel Reader
**Location:** [tests/test_excel.py](../tests/test_excel.py)

**Chức năng chính:**
```python
def read_excel_complete(file_path):
    """Đọc toàn bộ Excel file bao gồm formulas và values"""
    
def display_sheet_info(sheet_data):
    """Hiển thị thông tin chi tiết của một sheet"""
```

### File Excel Service
**Location:** [template/services/read_excel_xlsx.py](../template/services/read_excel_xlsx.py)

**Các hàm tiện ích:**
```python
def read_excel_with_formulas(file_path, sheet_name)
def get_sheet_names(file_path)
def read_excel_to_array(file_path, sheet_name)
def read_all_sheets_to_dict(file_path)
def read_all_sheets_to_array(file_path)
```

---

## 💡 Best Practices

### 1. Khi Sử Dụng Output JSON

✅ **Nên:**
- Sử dụng lớp `values` cho tính toán nhanh
- Sử dụng lớp `data` cho analysis đầy đủ
- Parse datetime string về datetime object khi cần

❌ **Không nên:**
- Load toàn bộ file JSON vào memory nếu file lớn
- Bỏ qua việc validate datetime format
- Giả định tất cả ô đều có giá trị (có thể null)

### 2. Xử Lý Datetime

```python
from datetime import datetime

# Parse ISO format
date_str = "2026-02-02T09:00:00"
date_obj = datetime.fromisoformat(date_str)

# So sánh thời gian
checkin = datetime.fromisoformat(cell["value"])
checkout = datetime.fromisoformat(cell2["value"])
duration = (checkout - checkin).total_seconds() / 60  # minutes
```

### 3. Truy Cập Dữ Liệu

```python
import json

# Load JSON
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Truy cập sheet
sheet = data["sheet1"]

# Lấy headers (dòng 3, index 2)
headers = [cell["value"] for cell in sheet["data"][2]]

# Lấy dữ liệu (dòng 4 trở đi)
rows = sheet["data"][3:]  # Bỏ qua title, blank, headers

# Xử lý từng dòng
for row in rows:
    employee_id = row[3]["value"]  # Cột D
    employee_name = row[4]["value"]  # Cột E
    total_work_hours = row[13]["value"]  # Cột N
```

---

## 🔮 Hướng Phát Triển

### 1. Tối Ưu Performance
- Streaming parse cho file lớn
- Lazy loading cho từng sheet
- Caching cho frequently accessed data

### 2. Enhanced Features
- Phát hiện và validate công thức Excel
- Tự động detect data types
- Support merged cells
- Handle formulas với external references

### 3. AI Agent Integration
- Natural language query về dữ liệu chấm công
- Tự động tính lương theo công thức phức tạp
- Phát hiện anomaly trong dữ liệu
- Generate báo cáo tự động

---

## 📚 Tài Liệu Tham Khảo

### Libraries Used
- **openpyxl**: Đọc/ghi Excel với công thức
- **pandas**: Xử lý dữ liệu dạng bảng
- **json**: Serialize/deserialize JSON

### Related Files
- [Plan_Cong_viec_tai_tao_repo.md](Plan_Cong_viec_tai_tao_repo.md) - Kế hoạch tổng thể dự án
- [README.md](../README.md) - Tổng quan về project
- [tests/test_excel.py](../tests/test_excel.py) - Code test đọc Excel

---

## ✅ Checklist Validation

Khi làm việc với output.json, cần validate:

- [ ] File JSON valid (không có syntax error)
- [ ] Tất cả datetime đều ở ISO format
- [ ] Không có giá trị undefined (chỉ null là OK)
- [ ] Số lượng cột nhất quán giữa các dòng
- [ ] Headers (dòng 3) có đầy đủ tên cột
- [ ] Các cột số không chứa string
- [ ] Cell address đúng format (A1, B2, ...)

---

**Tạo bởi:** Salary Agent Ver3  
**Cập nhật lần cuối:** 9 Tháng 2, 2026
