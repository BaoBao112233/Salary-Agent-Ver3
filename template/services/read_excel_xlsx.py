import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.styles import Font, Fill, Border, Alignment, PatternFill
from copy import copy
import pandas as pd
import json
from datetime import datetime, date
import re


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def read_excel_complete(file_path):
    """
    Đọc file Excel xlsx bao gồm tất cả sheets, công thức, giá trị và formatting
    
    Args:
        file_path: Đường dẫn đến file Excel
    
    Returns:
        Dictionary chứa thông tin của tất cả các sheets
    """
    # Load workbook với data_only=False để giữ công thức
    wb_formula = openpyxl.load_workbook(file_path, data_only=False)
    # Load workbook với data_only=True để lấy giá trị đã tính
    wb_values = openpyxl.load_workbook(file_path, data_only=True)
    
    all_sheets_data = {}
    
    # Duyệt qua tất cả các sheets
    for sheet_name in wb_formula.sheetnames:
        print(f"\n=== Đang đọc sheet: {sheet_name} ===")
        
        sheet_formula = wb_formula[sheet_name]
        sheet_values = wb_values[sheet_name]
        
        sheet_data = {
            'name': sheet_name,
            'data': [],
            'formulas': [],
            'values': [],
            'merged_cells': [],
            'column_widths': {},
            'row_heights': {}
        }
        
        # Lưu merged cells
        for merged_range in sheet_formula.merged_cells.ranges:
            sheet_data['merged_cells'].append(str(merged_range))
        
        # Lưu column widths
        for col_letter in range(1, sheet_formula.max_column + 1):
            col = get_column_letter(col_letter)
            if sheet_formula.column_dimensions[col].width:
                sheet_data['column_widths'][col] = sheet_formula.column_dimensions[col].width
        
        # Lưu row heights
        for row_num in range(1, sheet_formula.max_row + 1):
            if sheet_formula.row_dimensions[row_num].height:
                sheet_data['row_heights'][row_num] = sheet_formula.row_dimensions[row_num].height
        
        # Đọc dữ liệu từng dòng
        for row_idx, (row_formula, row_values) in enumerate(zip(sheet_formula.iter_rows(), 
                                                                 sheet_values.iter_rows()), 
                                                             start=1):
            row_data = []
            row_formula_data = []
            row_value_data = []
            
            for col_idx, (cell_formula, cell_value) in enumerate(zip(row_formula, row_values), start=1):
                cell_address = f"{get_column_letter(col_idx)}{row_idx}"
                
                # Lấy công thức (nếu có)
                formula = cell_formula.value if isinstance(cell_formula.value, str) and cell_formula.value.startswith('=') else None
                
                # Lấy giá trị đã tính toán
                value = cell_value.value
                
                # Lưu formatting
                cell_format = {}
                if cell_formula.font:
                    font_info = {
                        'name': cell_formula.font.name,
                        'size': cell_formula.font.size,
                        'bold': cell_formula.font.bold,
                        'italic': cell_formula.font.italic
                    }
                    if cell_formula.font.color:
                        try:
                            # Try RGB first
                            rgb_val = cell_formula.font.color.rgb
                            if rgb_val and isinstance(rgb_val, str) and len(rgb_val) in [6, 8]:
                                font_info['color'] = rgb_val
                            else:
                                # Try theme via private attribute
                                theme_val = getattr(cell_formula.font.color, '_theme', None)
                                if theme_val is not None and isinstance(theme_val, int):
                                    font_info['theme'] = theme_val
                                    font_info['tint'] = getattr(cell_formula.font.color, '_tint', 0.0)
                        except:
                            # Fallback to theme via private attribute
                            try:
                                theme_val = getattr(cell_formula.font.color, '_theme', None)
                                if theme_val is not None and isinstance(theme_val, int):
                                    font_info['theme'] = theme_val
                                    font_info['tint'] = getattr(cell_formula.font.color, '_tint', 0.0)
                            except:
                                pass
                    cell_format['font'] = font_info
                
                if cell_formula.fill and cell_formula.fill.patternType:
                    fill_info = {
                        'patternType': cell_formula.fill.patternType
                    }
                    if cell_formula.fill.fgColor:
                        try:
                            # Try RGB first
                            rgb_val = cell_formula.fill.fgColor.rgb
                            if rgb_val and isinstance(rgb_val, str) and len(rgb_val) in [6, 8]:
                                fill_info['fgColor'] = rgb_val
                            else:
                                # Try theme
                                theme_val = getattr(cell_formula.fill.fgColor, '_theme', None)
                                if theme_val is not None and isinstance(theme_val, int):
                                    fill_info['fgTheme'] = theme_val
                                    fill_info['fgTint'] = getattr(cell_formula.fill.fgColor, '_tint', 0.0)
                        except:
                            # Fallback to theme via private attribute
                            try:
                                theme_val = getattr(cell_formula.fill.fgColor, '_theme', None)
                                if theme_val is not None and isinstance(theme_val, int):
                                    fill_info['fgTheme'] = theme_val
                                    fill_info['fgTint'] = getattr(cell_formula.fill.fgColor, '_tint', 0.0)
                            except:
                                pass
                    cell_format['fill'] = fill_info
                
                if cell_formula.border:
                    cell_format['border'] = {
                        'left': {'style': cell_formula.border.left.style} if cell_formula.border.left else None,
                        'right': {'style': cell_formula.border.right.style} if cell_formula.border.right else None,
                        'top': {'style': cell_formula.border.top.style} if cell_formula.border.top else None,
                        'bottom': {'style': cell_formula.border.bottom.style} if cell_formula.border.bottom else None
                    }
                
                if cell_formula.alignment:
                    cell_format['alignment'] = {
                        'horizontal': cell_formula.alignment.horizontal,
                        'vertical': cell_formula.alignment.vertical,
                        'wrap_text': cell_formula.alignment.wrap_text
                    }
                
                # Lưu thông tin
                cell_info = {
                    'cell': cell_address,
                    'formula': formula,
                    'value': value
                }
                
                if cell_format:
                    cell_info['format'] = cell_format
                
                row_data.append(cell_info)
                row_formula_data.append(formula)
                row_value_data.append(value)
            
            sheet_data['data'].append(row_data)
            sheet_data['formulas'].append(row_formula_data)
            sheet_data['values'].append(row_value_data)
        
        all_sheets_data[sheet_name] = sheet_data
    
    wb_formula.close()
    wb_values.close()
    
    return all_sheets_data


def json_to_excel(json_data, output_file_path):
    """
    Convert từ JSON structure sang file Excel với formatting
    
    Args:
        json_data: Dictionary hoặc đường dẫn đến file JSON
        output_file_path: Đường dẫn file Excel đầu ra
    
    Returns:
        bool: True nếu thành công, False nếu có lỗi
    
    Example:
        # Từ dictionary
        json_to_excel(data_dict, "output.xlsx")
        
        # Từ file JSON
        json_to_excel("input.json", "output.xlsx")
    """
    try:
        # Nếu json_data là string (đường dẫn file), đọc file
        if isinstance(json_data, str):
            with open(json_data, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        
        # Tạo workbook mới
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Xóa sheet mặc định
        
        # Xử lý từng sheet
        for sheet_name, sheet_data in json_data.items():
            # Tạo sheet mới
            ws = wb.create_sheet(title=sheet_data['name'])
            
            # Áp dụng column widths
            if 'column_widths' in sheet_data:
                for col, width in sheet_data['column_widths'].items():
                    ws.column_dimensions[col].width = width
            
            # Áp dụng row heights
            if 'row_heights' in sheet_data:
                for row_num, height in sheet_data['row_heights'].items():
                    ws.row_dimensions[int(row_num)].height = height
            
            # Duyệt qua từng dòng trong data
            for row_data in sheet_data['data']:
                for cell_info in row_data:
                    # Parse cell address (VD: "A1" -> row=1, col=1)
                    cell_address = cell_info['cell']
                    
                    # Lấy cell từ worksheet
                    cell = ws[cell_address]
                    
                    # Xử lý giá trị
                    value = cell_info['value']
                    formula = cell_info['formula']
                    
                    # Nếu có công thức, ghi công thức
                    if formula:
                        cell.value = formula
                    else:
                        # Chuyển đổi datetime string về datetime object
                        if isinstance(value, str) and _is_datetime_string(value):
                            try:
                                cell.value = datetime.fromisoformat(value)
                            except:
                                cell.value = value
                        else:
                            cell.value = value
                    
                    # Áp dụng formatting nếu có
                    if 'format' in cell_info:
                        fmt = cell_info['format']
                        
                        # Font
                        if 'font' in fmt:
                            from openpyxl.styles.colors import Color
                            f = fmt['font']
                            font_args = {
                                'name': f.get('name'),
                                'size': f.get('size'),
                                'bold': f.get('bold'),
                                'italic': f.get('italic')
                            }
                            if f.get('color'):
                                try:
                                    font_args['color'] = Color(rgb=f.get('color'))
                                except:
                                    pass
                            elif f.get('theme') is not None:
                                font_args['color'] = Color(theme=f.get('theme'), tint=f.get('tint', 0.0))
                            cell.font = Font(**font_args)
                        
                        # Fill (background color)
                        if 'fill' in fmt:
                            from openpyxl.styles.colors import Color
                            fill_args = {
                                'patternType': fmt['fill'].get('patternType', 'solid')
                            }
                            
                            # Xử lý foreground color
                            if fmt['fill'].get('fgColor'):
                                fill_args['fgColor'] = Color(rgb=fmt['fill'].get('fgColor'))
                            elif fmt['fill'].get('fgTheme') is not None:
                                fill_args['fgColor'] = Color(
                                    theme=fmt['fill'].get('fgTheme'), 
                                    tint=fmt['fill'].get('fgTint', 0.0)
                                )
                            
                            if 'fgColor' in fill_args:
                                cell.fill = PatternFill(**fill_args)
                        
                        # Alignment
                        if 'alignment' in fmt:
                            a = fmt['alignment']
                            cell.alignment = Alignment(
                                horizontal=a.get('horizontal'),
                                vertical=a.get('vertical'),
                                wrap_text=a.get('wrap_text')
                            )
                        
                        # Border
                        if 'border' in fmt:
                            from openpyxl.styles import Side
                            b = fmt['border']
                            sides = {}
                            if b.get('left'):
                                sides['left'] = Side(style=b['left']['style'])
                            if b.get('right'):
                                sides['right'] = Side(style=b['right']['style'])
                            if b.get('top'):
                                sides['top'] = Side(style=b['top']['style'])
                            if b.get('bottom'):
                                sides['bottom'] = Side(style=b['bottom']['style'])
                            if sides:
                                cell.border = Border(**sides)
            
            # Áp dụng merged cells
            if 'merged_cells' in sheet_data:
                for merged_range in sheet_data['merged_cells']:
                    ws.merge_cells(merged_range)
        
        # Lưu file
        wb.save(output_file_path)
        wb.close()
        
        return True
        
    except Exception as e:
        print(f"Lỗi khi convert JSON sang Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def _is_datetime_string(value):
    """
    Kiểm tra xem string có phải là datetime ISO format không
    
    Args:
        value: String cần kiểm tra
    
    Returns:
        bool: True nếu là datetime string
    """
    if not isinstance(value, str):
        return False
    
    # Pattern cho ISO 8601: YYYY-MM-DDTHH:MM:SS hoặc YYYY-MM-DD
    datetime_pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$'
    return bool(re.match(datetime_pattern, value))

def display_sheet_info(sheet_data):
    """
    Hiển thị thông tin chi tiết của một sheet
    """
    print(f"\nSheet: {sheet_data['name']}")
    print("-" * 80)
    
    for row_idx, row in enumerate(sheet_data['data'], start=1):
        for cell_info in row:
            if cell_info['formula']:
                print(f"Ô {cell_info['cell']}: "
                      f"Công thức = {cell_info['formula']}, "
                      f"Giá trị = {cell_info['value']}")


def convert_json_file_to_excel(json_file_path, excel_output_path):
    """
    Hàm tiện ích: Convert trực tiếp từ file JSON sang file Excel
    
    Args:
        json_file_path (str): Đường dẫn đến file JSON input
        excel_output_path (str): Đường dẫn file Excel output
    
    Returns:
        bool: True nếu thành công
    
    Example:
        convert_json_file_to_excel("output.json", "restored.xlsx")
    """
    return json_to_excel(json_file_path, excel_output_path)

def display_sheet_info(sheet_data):
    """
    Hiển thị thông tin chi tiết của một sheet
    """
    print(f"\nSheet: {sheet_data['name']}")
    print("-" * 80)
    
    for row_idx, row in enumerate(sheet_data['data'], start=1):
        for cell_info in row:
            if cell_info['formula']:
                print(f"Ô {cell_info['cell']}: "
                      f"Công thức = {cell_info['formula']}, "
                      f"Giá trị = {cell_info['value']}")


def convert_json_file_to_excel(json_file_path, excel_output_path):
    """
    Hàm tiện ích: Convert trực tiếp từ file JSON sang file Excel
    
    Args:
        json_file_path (str): Đường dẫn đến file JSON input
        excel_output_path (str): Đường dẫn file Excel output
    
    Returns:
        bool: True nếu thành công
    
    Example:
        convert_json_file_to_excel("output.json", "restored.xlsx")
    """
    return json_to_excel(json_file_path, excel_output_path)


def read_excel_to_array(file_path, sheet_name=None):
    """
    Đọc file Excel và trả về dữ liệu dưới dạng array đơn giản
    Phù hợp cho việc xử lý dữ liệu thông thường (không cần formula/formatting)
    
    Args:
        file_path (str): Đường dẫn đến file Excel
        sheet_name (str, optional): Tên sheet cần đọc. Nếu None, đọc sheet đầu tiên
    
    Returns:
        list: Mảng 2 chiều chứa giá trị các ô (chỉ value, không có formula/format)
        
    Example:
        data = read_excel_to_array("file.xlsx", "Sheet1")
        # data = [
        #     ["Name", "Age", "Salary"],
        #     ["John", 25, 50000],
        #     ["Jane", 30, 60000]
        # ]
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    # Lấy sheet
    if sheet_name:
        if sheet_name not in wb.sheetnames:
            wb.close()
            raise ValueError(f"Sheet '{sheet_name}' không tồn tại. Available sheets: {wb.sheetnames}")
        ws = wb[sheet_name]
    else:
        ws = wb.active
    
    # Đọc dữ liệu thành array
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(list(row))
    
    wb.close()
    return data


def read_all_sheets_to_dict(file_path):
    """
    Đọc tất cả sheets trong file Excel và trả về dictionary
    
    Args:
        file_path (str): Đường dẫn đến file Excel
    
    Returns:
        dict: Dictionary với key là tên sheet, value là array 2 chiều
        
    Example:
        all_data = read_all_sheets_to_dict("file.xlsx")
        # all_data = {
        #     "Sheet1": [[...], [...], ...],
        #     "Sheet2": [[...], [...], ...]
        # }
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    all_sheets = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        data = []
        for row in ws.iter_rows(values_only=True):
            data.append(list(row))
        all_sheets[sheet_name] = data
    
    wb.close()
    return all_sheets


def matching_data(attendance_data, salary_data, header_row_index=0, data_start_index=1):
    """
    Ghép dữ liệu chấm công với dữ liệu lương theo mã nhân viên
    
    Args:
        attendance_data (list): Dữ liệu chấm công (array 2D)
        salary_data (list): Dữ liệu lương (array 2D)
        header_row_index (int): Index của dòng header (mặc định 0)
        data_start_index (int): Index bắt đầu của dữ liệu (mặc định 1)
    
    Returns:
        list: Danh sách dictionary chứa thông tin đầy đủ của mỗi nhân viên
        
    Example:
        attendance = [
            ["ID", "Name", "Days"],
            ["E001", "John", 22],
            ["E002", "Jane", 20]
        ]
        salary = [
            ["ID", "Base Salary"],
            ["E001", 5000000],
            ["E002", 6000000]
        ]
        result = matching_data(attendance, salary)
        # result = [
        #     {"id": "E001", "name": "John", "days": 22, "base_salary": 5000000},
        #     {"id": "E002", "name": "Jane", "days": 20, "base_salary": 6000000}
        # ]
    """
    if not attendance_data or not salary_data:
        return []
    
    # Lấy header rows
    attendance_headers = attendance_data[header_row_index] if len(attendance_data) > header_row_index else []
    salary_headers = salary_data[header_row_index] if len(salary_data) > header_row_index else []
    
    # Convert None headers thành string
    attendance_headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(attendance_headers)]
    salary_headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(salary_headers)]
    
    # Convert salary data thành dictionary để lookup nhanh
    salary_dict = {}
    for row in salary_data[data_start_index:]:  # Bỏ qua header
        if row and len(row) > 0 and row[0]:  # Có employee ID
            employee_id = str(row[0]).strip()
            salary_dict[employee_id] = row
    
    # Combine data
    combined = []
    for row in attendance_data[data_start_index:]:  # Bỏ qua header
        if not row or len(row) == 0 or not row[0]:
            continue
            
        employee_id = str(row[0]).strip()
        
        # Tạo dictionary cho nhân viên này
        employee_data = {}
        
        # Thêm dữ liệu từ attendance
        for i, header in enumerate(attendance_headers):
            if i < len(row):
                employee_data[f"attendance_{header}"] = row[i]
        
        # Thêm dữ liệu từ salary (nếu tìm thấy)
        if employee_id in salary_dict:
            salary_row = salary_dict[employee_id]
            for i, header in enumerate(salary_headers):
                if i < len(salary_row):
                    employee_data[f"salary_{header}"] = salary_row[i]
        
        combined.append(employee_data)
    
    return combined


def parse_excel_with_smart_header(file_path, sheet_name=None, skip_rows=0):
    """
    Đọc file Excel với khả năng tự động tìm header row
    
    Args:
        file_path (str): Đường dẫn đến file Excel
        sheet_name (str, optional): Tên sheet cần đọc
        skip_rows (int): Số dòng bỏ qua từ đầu (mặc định 0)
    
    Returns:
        tuple: (headers, data_rows)
            - headers: List các tên cột
            - data_rows: List các dòng dữ liệu (không bao gồm header)
    """
    raw_data = read_excel_to_array(file_path, sheet_name)
    
    if not raw_data or len(raw_data) <= skip_rows:
        return [], []
    
    # Bỏ qua các dòng đầu
    data = raw_data[skip_rows:]
    
    # Tìm header row (dòng đầu tiên có nhiều giá trị không None)
    header_row_idx = 0
    max_non_none = 0
    
    for i, row in enumerate(data[:10]):  # Chỉ kiểm tra 10 dòng đầu
        non_none_count = sum(1 for cell in row if cell is not None and str(cell).strip())
        if non_none_count > max_non_none:
            max_non_none = non_none_count
            header_row_idx = i
    
    headers = data[header_row_idx] if len(data) > header_row_idx else []
    data_rows = data[header_row_idx + 1:] if len(data) > header_row_idx + 1 else []
    
    # Convert None headers thành string
    headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(headers)]
    
    return headers, data_rows


def convert_to_dict_with_headers(headers, data_rows):
    """
    Convert data rows thành list of dictionaries với headers
    
    Args:
        headers (list): Danh sách tên cột
        data_rows (list): Danh sách các dòng dữ liệu
    
    Returns:
        list: Danh sách dictionary
    """
    result = []
    for row in data_rows:
        if not row or all(cell is None for cell in row):
            continue
        
        row_dict = {}
        for i, header in enumerate(headers):
            if i < len(row):
                row_dict[header] = row[i]
            else:
                row_dict[header] = None
        
        result.append(row_dict)
    
    return result


def get_sheet_names(file_path):
    """
    Lấy danh sách tên các sheets trong file Excel
    
    Args:
        file_path (str): Đường dẫn đến file Excel
    
    Returns:
        list: Danh sách tên các sheets
    """
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet_names = wb.sheetnames
    wb.close()
    return sheet_names


# Ví dụ sử dụng
if __name__ == "__main__":
    file_path = "/home/baobao/Projects/Salary-Agent-Ver3/tests/data/test_RDU_Salary.xlsx"  # Thay đổi đường dẫn file của bạn
    
    try:
        # Đọc toàn bộ file Excel
        all_data = read_excel_complete(file_path)
        
        # Hiển thị thông tin tổng quan
        print(f"Tổng số sheets: {len(all_data)}")
        print(f"Danh sách sheets: {list(all_data.keys())}")
        
        # Hiển thị chi tiết từng sheet
        for sheet_name, sheet_data in all_data.items():
            display_sheet_info(sheet_data)
        
        # Hoặc truy cập dữ liệu của một sheet cụ thể
        # if all_data:
        #     first_sheet = list(all_data.values())[0]
        #     print(f"\n\nDữ liệu sheet đầu tiên:")
        #     print(f"Số dòng: {len(first_sheet['data'])}")
            
        print(f"\nĐã hoàn thành việc đọc file Excel.")
        # print(json.dumps(all_data, ensure_ascii=False, indent=4))

        # Lưu dữ liệu ra file JSON để kiểm tra
        output_path = "/home/baobao/Projects/Salary-Agent-Ver3/tests/data/output_test_RDU_Salary.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

        print(f"Dữ liệu đã được lưu vào {output_path}")
        
        # Test convert ngược lại từ JSON sang Excel
        print("\n" + "="*80)
        print("Test convert JSON -> Excel")
        print("="*80)
        
        output_excel = "/home/baobao/Projects/Salary-Agent-Ver3/tests/data/output_from_json.xlsx"
        success = json_to_excel(all_data, output_excel)
        
        if success:
            print(f"✅ Đã convert thành công JSON -> Excel: {output_excel}")
            
            # Verify bằng cách đọc lại file Excel vừa tạo
            print("\nVerifying file Excel vừa tạo...")
            wb_verify = openpyxl.load_workbook(output_excel)
            print(f"   - Số sheets: {len(wb_verify.sheetnames)}")
            print(f"   - Tên sheets: {wb_verify.sheetnames}")
            
            # Kiểm tra vài ô để verify
            ws_verify = wb_verify[wb_verify.sheetnames[0]]
            print(f"   - Ô A1: {ws_verify['A1'].value}")
            print(f"   - Ô D4: {ws_verify['D4'].value}")
            print(f"   - Ô N4: {ws_verify['N4'].value}")
            
            wb_verify.close()
        else:
            print("❌ Có lỗi khi convert JSON -> Excel")

    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_path}")
    except Exception as e:
        print(f"Lỗi: {str(e)}")