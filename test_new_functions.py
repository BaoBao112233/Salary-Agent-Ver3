#!/usr/bin/env python3
"""Test các hàm mới trong read_excel_xlsx module"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/home/baobao/Projects/Salary-Agent-Ver3')

from template.services.read_excel_xlsx import (
    read_excel_complete, 
    json_to_excel, 
    convert_json_file_to_excel, 
    display_sheet_info,
    read_excel_to_array,
    read_all_sheets_to_dict,
    matching_data,
    get_sheet_names,
    DateTimeEncoder
)

def test_all_functions():
    """Test tất cả các functions"""
    
    print("="*80)
    print("TEST: Import các hàm")
    print("="*80)
    
    functions = [
        "read_excel_complete",
        "json_to_excel", 
        "convert_json_file_to_excel",
        "display_sheet_info",
        "read_excel_to_array",
        "read_all_sheets_to_dict",
        "matching_data",
        "get_sheet_names",
        "DateTimeEncoder"
    ]
    
    print("✅ Đã import thành công các hàm:")
    for func in functions:
        print(f"   - {func}")
    
    # Test với file thực nếu tồn tại
    test_file = "/home/baobao/Projects/Salary-Agent-Ver3/tests/data/test_RDU_Salary.xlsx"
    
    if os.path.exists(test_file):
        print("\n" + "="*80)
        print("TEST: Đọc file Excel thực tế")
        print("="*80)
        
        # Test get_sheet_names
        print(f"\n1. Test get_sheet_names():")
        sheet_names = get_sheet_names(test_file)
        print(f"   Số sheets: {len(sheet_names)}")
        print(f"   Tên sheets: {sheet_names}")
        
        # Test read_excel_to_array
        print(f"\n2. Test read_excel_to_array():")
        if sheet_names:
            first_sheet = sheet_names[0]
            data = read_excel_to_array(test_file, first_sheet)
            print(f"   Sheet: {first_sheet}")
            print(f"   Số dòng: {len(data)}")
            print(f"   Số cột: {len(data[0]) if data else 0}")
            if data and len(data) > 0:
                print(f"   Dòng đầu tiên: {data[0][:5]}...")  # 5 ô đầu
        
        # Test read_all_sheets_to_dict
        print(f"\n3. Test read_all_sheets_to_dict():")
        all_data = read_all_sheets_to_dict(test_file)
        print(f"   Số sheets: {len(all_data)}")
        for sheet_name, sheet_data in all_data.items():
            print(f"   - {sheet_name}: {len(sheet_data)} dòng")
        
        # Test matching_data với dữ liệu giả
        print(f"\n4. Test matching_data():")
        attendance = [
            ["ID", "Name", "Days"],
            ["E001", "John Doe", 22],
            ["E002", "Jane Smith", 20]
        ]
        salary = [
            ["ID", "Base Salary", "Position"],
            ["E001", 5000000, "Developer"],
            ["E002", 6000000, "Manager"]
        ]
        combined = matching_data(attendance, salary)
        print(f"   Số nhân viên: {len(combined)}")
        if combined:
            print(f"   Nhân viên đầu tiên: {combined[0]}")
        
        print("\n" + "="*80)
        print("✅ TẤT CẢ TESTS THÀNH CÔNG!")
        print("="*80)
    else:
        print(f"\n⚠️ File test không tồn tại: {test_file}")
        print("   Chỉ test được imports")

if __name__ == "__main__":
    try:
        test_all_functions()
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
