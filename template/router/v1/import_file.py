"""
Import File Router
Endpoint để xử lý 2 file đầu vào (attendance + salary info) và tạo file lương kết quả với AI Agent
"""
import os
import uuid
import logging
import math
import json
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from template.agent.agent import Agent
from template.schemas.model import ChatRequest
from template.services.aws_service import S3Service
from template.services.read_excel_xlsx import (
    read_excel_complete,
    get_sheet_names
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Import File"])

# Initialize agent and S3 service
salary_processing_agent = Agent()  # Uses SALARY_AGENT_SYSTEM_PROMPT by default
s3_service = S3Service()


def sanitize_for_json(obj):
    """Làm sạch dữ liệu để tương thích JSON bằng cách thay thế NaN, Infinity bằng None"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj


@router.post("/import_file")
async def import_file(
    session_id: int = Form(..., description="ID phiên làm việc"),
    user_id: int = Form(..., description="ID người dùng"),
    background_tasks: BackgroundTasks = None,
    attendance_file: UploadFile = File(..., description="File chấm công của nhân viên (.xlsx)"),
    template_file: UploadFile = File(..., description="File template tính lương (.xlsx)"),
    
):
    """
    Import và xử lý 2 file để tạo file lương kết quả
    
    ## Mô tả
    Endpoint này nhận 2 file đầu vào:
    - **session_id**: ID phiên làm việc
    - **user_id**: ID người dùng
    - **attendance_file**: File chứa thông tin chấm công của các nhân viên
    - **template_file**: File template dùng để tính lương (có công thức tính toán)
    
    ## Agent sẽ:
    - Phân tích từng file để hiểu cấu trúc và dữ liệu
    - Phân tích đầy đủ các sheet trong mỗi file
    - Kiểm tra xem thiếu thông tin gì để tính được kết quả
    - Sử dụng AI để đánh giá tính đầy đủ của dữ liệu
    - Gộp dữ liệu và tính toán lương
    - Tạo file Excel kết quả
    
    ## Output
    - File Excel chứa kết quả tính lương
    - Thông tin phân tích chi tiết về từng file
    - Cảnh báo về dữ liệu thiếu (nếu có)
    
    ## Ví dụ sử dụng
    ```bash
    curl -X POST "http://localhost:8000/api/v1/import_file" \\
      -F "session_id=your_session_id" \\
      -F "user_id=your_user_id" \\
      -F "attendance_file=@cham_cong.xlsx" \\
      -F "template_file=@template_tinh_luong.xlsx"
    ```
    """
    
    unique_id = str(uuid.uuid4())
    
    # Initialize path variables
    attendance_path = None
    template_path = None
    
    try:
        # Kiểm tra định dạng file
        for file in [attendance_file, template_file]:
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} phải có định dạng Excel (.xlsx hoặc .xls)"
                )
        
        # Lưu các file được upload
        logger.info(f"Đang xử lý các file cho yêu cầu {unique_id}")
        
        # Tạo bảng với logic retry
        try:
            create_table()
            logger.info("✓ Đã tạo/xác minh bảng cơ sở dữ liệu")
        except Exception as e:
            logger.error(f"Kết nối cơ sở dữ liệu thất bại: {str(e)}")
            # Tiếp tục không có database - các file vẫn sẽ được xử lý
            logger.warning("⚠️ Tiếp tục mà không có kết nối cơ sở dữ liệu")

        attendance_path = f"uploads/attendance_{unique_id}.xlsx"
        template_path = f"uploads/template_{unique_id}.xlsx"
        output_path = f"outputs/result_{unique_id}.xlsx"
        
        logger.info("Đang lưu các file đã tải lên...")
        with open(attendance_path, "wb") as f:
            f.write(await attendance_file.read())
        logger.info(f"✓ Đã lưu file chấm công: {attendance_file.filename}")

        with open(template_path, "wb") as f:
            f.write(await template_file.read())
        logger.info(f"✓ Đã lưu file template: {template_file.filename}")
        
        # Tải các file đầu vào lên S3
        try:
            s3_attendance_key = s3_service.upload_file(
                attendance_path, "inputs", f"attendance_{unique_id}.xlsx"
            )
            s3_template_key = s3_service.upload_file(
                template_path, "inputs", f"template_{unique_id}.xlsx"
            )
            logger.info(f"✓ Đã tải các file đầu vào lên S3")
        except Exception as e:
            logger.warning(f"Không thể tải lên S3: {str(e)}")

        # Đọc dữ liệu chấm công và chèn vào cơ sở dữ liệu
        logger.info("Đang đọc các file Excel...")
        attendance_data = read_excel_to_array(attendance_path)
        
        # Bỏ qua dòng đầu tiên nếu chứa header (phát hiện bằng cách kiểm tra giá trị có phải tên cột)
        if combined_data and len(combined_data) > 0:
            first_row = combined_data[0]
            # Kiểm tra nếu dòng đầu tiên chứa dữ liệu giống header (các giá trị khớp với tên cột tiếng Việt phổ biến)
            header_indicators = ['Mã nhân viên', 'Tên nhân viên', 'Họ và tên', 'Ngày']
            is_header_row = any(str(value) in header_indicators for value in first_row.values())
            
            if is_header_row:
                logger.info(f"Đã phát hiện dòng header trong dữ liệu, bỏ qua bản ghi đầu tiên")
                combined_data = combined_data[1:]  # Bỏ qua dòng header
        
        # Debug: Ghi log các key mẫu của nhân viên
        if combined_data:
            sample_keys = list(combined_data[0].keys())
            logger.info(f"Tổng số bản ghi đã ghép: {len(combined_data)}")
            logger.info(f"Các key mẫu của nhân viên (10 đầu tiên): {sample_keys[:10]}")
            logger.info(f"Tất cả các key: {sample_keys}")
        
        # Chuyển đổi dữ liệu để khớp với schema cơ sở dữ liệu
        logger.info("Đang chuyển đổi dữ liệu để chèn vào cơ sở dữ liệu...")
        transformed_data = []
        for idx, employee in enumerate(combined_data):
            # Ghi log nhân viên đầu tiên để debug
            if idx == 0:
                logger.info(f"Mẫu dữ liệu nhân viên đầu tiên: {employee}")
            
            # Trích xuất và ánh xạ các trường vào schema cơ sở dữ liệu
            # Dựa trên cấu trúc Excel thực tế: attendance_col_3 = Mã nhân viên, attendance_col_4 = Tên nhân viên, v.v.
            transformed = {
                'Mã nhân viên': employee.get('attendance_col_3') or employee.get('attendance_Mã nhân viên') or employee.get('salary_Mã NV'),
                'Họ và tên': employee.get('attendance_col_4') or employee.get('attendance_Tên nhân viên') or employee.get('salary_Họ và tên'),
                'Số ngày công thực tế': employee.get('attendance_col_14') or employee.get('attendance_Tổng số công') or 0,
                'Số giờ làm thêm': employee.get('attendance_col_13') or employee.get('attendance_Tổng thời gian tính công (giờ)') or 0,
                'Số ngày nghỉ phép': employee.get('attendance_Số ngày nghỉ phép') or 0,
                'Số ngày nghỉ không lương': employee.get('attendance_Số ngày nghỉ không lương') or 0,
                'Số lần đi muộn': employee.get('attendance_Số lần đi muộn') or 0,
                'Số lần về sớm': employee.get('attendance_Số lần về sớm') or 0,
                'Dự án': employee.get('salary_Dự án') or '',
                'Phòng ban': employee.get('salary_Phòng ban') or '',
                'Hệ số thử việc': employee.get('salary_Hệ số thử việc') or 1.0,
                'Chức danh': employee.get('salary_Chức danh') or '',
                'Lương cơ bản': employee.get('salary_Lương cơ bản') or 0,
                'Lương đóng BHXH': employee.get('salary_Lương đóng BHXH') or 0,
                'Thưởng cố định': employee.get('salary_Thưởng cố định') or 0,
                'Phụ cấp chức vụ': employee.get('salary_Phụ cấp chức vụ') or 0,
                'Phụ cấp xăng xe': employee.get('salary_Phụ cấp xăng xe') or 0,
                'Phụ cấp điện thoại': employee.get('salary_Phụ cấp điện thoại') or 0,
                'Phụ cấp cơm': employee.get('salary_Phụ cấp cơm') or 0,
                'Số người phụ thuộc': employee.get('salary_Số người phụ thuộc') or 0,
            }
            
            # Ghi log bản ghi đã chuyển đổi đầu tiên
            if idx == 0:
                logger.info(f"Nhân viên đã chuyển đổi đầu tiên: {transformed}")
            
            # Chỉ thêm nếu có ít nhất một mã nhân viên
            if transformed['Mã nhân viên']:
                transformed_data.append(transformed)
        
        logger.info(f"Đã chuyển đổi {len(transformed_data)} bản ghi nhân viên")
        
        # Chèn vào cơ sở dữ liệu với xử lý lỗi
        try:
            logger.info(f"Đang chèn {len(transformed_data)} nhân viên vào cơ sở dữ liệu...")
            inserted_count = insert_employee_data(transformed_data)
            logger.info(f"✓ Đã chèn thành công {inserted_count} nhân viên")
            
            return {
                "success": True,
                "message": "Đã xử lý file và chèn dữ liệu thành công",
                "unique_id": unique_id,
                "data": {
                    "total_employees": len(combined_data),
                    "transformed_employees": len(transformed_data),
                    "inserted_count": inserted_count
                }
            }
        except Exception as db_error:
            logger.error(f"Chèn vào cơ sở dữ liệu thất bại: {str(db_error)}")
            # Vẫn trả về thành công vì các file đã được xử lý
            return {
                "success": True,
                "message": "Đã xử lý file nhưng chèn vào cơ sở dữ liệu thất bại",
                "unique_id": unique_id,
                "warning": str(db_error),
                "data": {
                    "total_employees": len(combined_data),
                    "inserted_count": 0
                }
            }
        

        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xử lý file: {str(e)}", exc_info=True)
        
        # Dọn dẹp các file khi có lỗi
        for path in [attendance_path, template_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý file: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_result(filename: str):
    """Download file kết quả"""
    file_path = f"outputs/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
