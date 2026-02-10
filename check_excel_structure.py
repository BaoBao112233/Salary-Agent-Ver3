#!/usr/bin/env python3
"""Script để xem cấu trúc file Excel test"""

import sys
sys.path.insert(0, '/home/baobao/Projects/Salary-Agent-Ver3')

from template.services.read_excel_xlsx import read_excel_to_array, get_sheet_names

# File test
test_file = "/home/baobao/Projects/Salary-Agent-Ver3/tests/data/test_RDU_Salary.xlsx"

print("="*80)
print("CẤU TRÚC FILE EXCEL")
print("="*80)

# Xem tất cả sheets
sheet_names = get_sheet_names(test_file)
print(f"\nTổng số sheets: {len(sheet_names)}")
print(f"Danh sách sheets:")
for i, name in enumerate(sheet_names, 1):
    print(f"  {i}. {name}")

# Xem dữ liệu chi tiết của một vài sheets quan trọng
important_sheets = ["RDU T11", "0.Bang luong T11", "1.BCC"]

for sheet_name in important_sheets:
    if sheet_name in sheet_names:
        print(f"\n{'='*80}")
        print(f"SHEET: {sheet_name}")
        print(f"{'='*80}")
        
        data = read_excel_to_array(test_file, sheet_name)
        
        # Hiển thị 5 dòng đầu
        print(f"\n5 dòng đầu tiên:")
        for i, row in enumerate(data[:5], 1):
            print(f"  Dòng {i}: {row[:10] if len(row) > 10 else row}")  # 10 cột đầu
        
        # Tìm header (dòng không None)
        for i, row in enumerate(data):
            non_none = [cell for cell in row if cell is not None]
            if len(non_none) > 5:  # Dòng có ít nhất 5 cột có giá trị
                print(f"\nHeader (dòng {i+1}):")
                print(f"  {row[:15]}")  # 15 cột đầu
                break
