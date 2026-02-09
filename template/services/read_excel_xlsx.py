import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.styles import Font, Fill, Border, Alignment, PatternFill
from copy import copy
import pandas as pd
import json
from datetime import datetime, date
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        logger.info(f"\n=== Đang đọc sheet: {sheet_name} ===")
        
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