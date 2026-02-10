# 📚 Hướng Dẫn Sử Dụng Read Excel Services

## 🎯 Tổng Quan

Module `read_excel_xlsx.py` cung cấp đầy đủ các functions để đọc, xử lý và convert file Excel trong dự án Salary Agent.

---

## 📦 Installation

Không cần cài đặt thêm, tất cả dependencies đã có trong project:
- `openpyxl` - Đọc/ghi file Excel
- `pandas` - Xử lý dữ liệu (optional)
- `json` - Export/Import JSON

---

## 🚀 Quick Start

### 1. Đọc Excel Đơn Giản

```python
from template.services.read_excel_xlsx import read_excel_to_array

# Đọc sheet đầu tiên
data = read_excel_to_array("file.xlsx")

# Đọc sheet cụ thể
data = read_excel_to_array("file.xlsx", "Sheet1")

# Kết quả: array 2D
# [
#     ["Name", "Age", "Salary"],
#     ["John", 25, 50000],
#     ["Jane", 30, 60000]
# ]
```

### 2. Ghép Dữ Liệu Attendance + Salary

```python
from template.services.read_excel_xlsx import (
    read_excel_to_array, 
    matching_data
)

# Đọc 2 file
attendance = read_excel_to_array("attendance.xlsx")
salary = read_excel_to_array("salary.xlsx")

# Ghép dữ liệu theo ID nhân viên
combined = matching_data(attendance, salary)

# Kết quả: list of dictionaries
# [
#     {
#         "attendance_ID": "NV001",
#         "attendance_Name": "John",
#         "salary_ID": "NV001",
#         "salary_Base Salary": 5000000
#     },
#     ...
# ]
```

### 3. Auto-Detect Headers

```python
from template.services.read_excel_xlsx import parse_excel_with_smart_header

# Tự động tìm header row
headers, data_rows = parse_excel_with_smart_header("file.xlsx", "Sheet1")

# headers = ["ID", "Name", "Age"]
# data_rows = [["1", "John", 25], ["2", "Jane", 30]]
```

### 4. Đọc Tất Cả Sheets

```python
from template.services.read_excel_xlsx import (
    get_sheet_names,
    read_all_sheets_to_dict
)

# Lấy danh sách sheets
sheets = get_sheet_names("file.xlsx")
# ['Sheet1', 'Sheet2', 'Summary']

# Đọc tất cả sheets
all_data = read_all_sheets_to_dict("file.xlsx")
# {
#     'Sheet1': [[...], [...], ...],
#     'Sheet2': [[...], [...], ...]
# }
```

### 5. Đọc Excel Đầy Đủ (với Formulas & Formatting)

```python
from template.services.read_excel_xlsx import read_excel_complete

# Đọc đầy đủ: formulas, values, formatting
full_data = read_excel_complete("file.xlsx")

# Kết quả: dictionary phức tạp với toàn bộ thông tin
# {
#     'Sheet1': {
#         'name': 'Sheet1',
#         'data': [...],           # Cell info với formatting
#         'formulas': [...],       # Công thức gốc
#         'values': [...],         # Giá trị đã tính
#         'merged_cells': [...],   # Các ô merge
#         'column_widths': {...},  # Độ rộng cột
#         'row_heights': {...}     # Chiều cao dòng
#     }
# }
```

### 6. Convert JSON → Excel

```python
from template.services.read_excel_xlsx import (
    read_excel_complete,
    json_to_excel,
    convert_json_file_to_excel
)

# Đọc Excel → JSON
data = read_excel_complete("input.xlsx")

# Save to JSON
import json
with open("output.json", "w") as f:
    json.dump(data, f)

# Convert JSON → Excel
json_to_excel("output.json", "restored.xlsx")

# Hoặc dùng function tiện ích
convert_json_file_to_excel("output.json", "restored.xlsx")
```

---

## 📋 API Reference

### Core Functions

#### `read_excel_to_array(file_path, sheet_name=None)`
Đọc Excel thành array 2D đơn giản.
- **Args:**
  - `file_path` (str): Đường dẫn file Excel
  - `sheet_name` (str, optional): Tên sheet, None = sheet đầu tiên
- **Returns:** `list` - Array 2D
- **Use case:** Đọc nhanh, không cần formulas/formatting

#### `matching_data(attendance_data, salary_data, header_row_index=0, data_start_index=1)`
Ghép dữ liệu theo employee ID.
- **Args:**
  - `attendance_data` (list): Data chấm công
  - `salary_data` (list): Data lương
  - `header_row_index` (int): Index của header row
  - `data_start_index` (int): Index bắt đầu data
- **Returns:** `list` - List of dictionaries
- **Use case:** Merge data từ nhiều nguồn

#### `parse_excel_with_smart_header(file_path, sheet_name=None, skip_rows=0)`
Tự động detect header row.
- **Args:**
  - `file_path` (str): Đường dẫn file
  - `sheet_name` (str, optional): Tên sheet
  - `skip_rows` (int): Số dòng bỏ qua đầu file
- **Returns:** `tuple` - (headers, data_rows)
- **Use case:** File có cấu trúc không chuẩn

#### `get_sheet_names(file_path)`
Lấy danh sách tên sheets.
- **Args:** `file_path` (str)
- **Returns:** `list` - Danh sách tên sheets
- **Use case:** Khám phá cấu trúc file

#### `read_excel_complete(file_path)`
Đọc đầy đủ với formulas & formatting.
- **Args:** `file_path` (str)
- **Returns:** `dict` - Full data structure
- **Use case:** Cần preserve formulas, styles

### Utility Functions

#### `convert_to_dict_with_headers(headers, data_rows)`
Convert array sang list of dicts.

#### `read_all_sheets_to_dict(file_path)`
Đọc tất cả sheets thành dictionary.

#### `json_to_excel(json_data, output_file_path)`
Convert JSON structure sang Excel.

#### `convert_json_file_to_excel(json_file_path, excel_output_path)`
Tiện ích: Convert file JSON → Excel.

---

## 🔥 Use Cases

### Use Case 1: Import File Flow (API Endpoint)

```python
# Trong router/v1/import_file.py
from template.services.read_excel_xlsx import (
    read_excel_to_array,
    matching_data
)

# Đọc files
attendance = read_excel_to_array(attendance_path)
salary = read_excel_to_array(salary_path)

# Ghép dữ liệu
combined = matching_data(attendance, salary)

# Insert vào database
insert_employee_data(combined)
```

### Use Case 2: Backup & Restore

```python
# Backup: Excel → JSON
from template.services.read_excel_xlsx import read_excel_complete
import json

data = read_excel_complete("original.xlsx")
with open("backup.json", "w") as f:
    json.dump(data, f, cls=DateTimeEncoder)

# Restore: JSON → Excel
from template.services.read_excel_xlsx import convert_json_file_to_excel
convert_json_file_to_excel("backup.json", "restored.xlsx")
```

### Use Case 3: Data Analysis

```python
# Phân tích dữ liệu từ nhiều sheets
from template.services.read_excel_xlsx import read_all_sheets_to_dict

all_data = read_all_sheets_to_dict("report.xlsx")

for sheet_name, data in all_data.items():
    print(f"Sheet: {sheet_name}")
    print(f"  Rows: {len(data)}")
    print(f"  Cols: {len(data[0]) if data else 0}")
```

---

## 🧪 Testing

### Run Tests

```bash
# Test imports
python test_imports.py

# Test new functions
python test_new_functions.py

# Test comprehensive
python test_comprehensive.py

# Final integration test
python test_final_integration.py
```

### Tất cả tests đều PASS ✅

---

## ⚠️ Important Notes

### 1. Performance
- `read_excel_to_array()` nhanh nhất (data only)
- `read_excel_complete()` chậm hơn (full info)
- Dùng `read_only=True` khi có thể

### 2. Memory
- File lớn (>10MB): cân nhắc streaming
- Tránh load toàn bộ vào memory
- Close workbook sau khi đọc

### 3. Error Handling
- Luôn check file tồn tại trước
- Validate sheet names
- Handle None values trong data

---

## 📞 Support

Nếu gặp vấn đề:
1. Check [CHANGELOG_ReadExcel_Update.md](CHANGELOG_ReadExcel_Update.md)
2. Xem test files để hiểu cách dùng
3. Review docstrings trong code

---

## 🎓 Best Practices

✅ **DO:**
- Dùng `read_excel_to_array()` cho simple cases
- Close workbook sau khi dùng
- Validate input data
- Use type hints
- Write tests

❌ **DON'T:**
- Load file quá lớn vào memory
- Modify original file
- Assume all cells có value
- Skip error handling

---

**Happy Coding!** 🚀
