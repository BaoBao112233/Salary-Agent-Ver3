"""
Import File Router - AI Agent Version
Endpoint để xử lý 2 file Excel (attendance + salary info) với AI Agent
Agent sẽ analyze, plan, merge và validate dữ liệu
"""
import os
import uuid
import logging
import json
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from template.agent.agent import Agent
from template.schemas.model import ChatRequest
from template.services.aws_service import S3Service
from template.services.read_excel_xlsx import read_excel_complete, json_to_excel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Import File AI"])

# Initialize AI Agent with Salary Processing prompt
salary_agent = Agent()  # Uses SALARY_AGENT_SYSTEM_PROMPT by default
s3_service = S3Service()


@router.post("/import_file_ai")
async def import_file_ai(
    session_id: int = Form(..., description="ID phiên làm việc"),
    user_id: int = Form(..., description="ID người dùng"),
    attendance_file: UploadFile = File(..., description="File chấm công (.xlsx)"),
    salary_info_file: UploadFile = File(..., description="File thông tin lương + template (.xlsx)"),
):
    """
    🤖 AI-Powered Salary Processing Endpoint
    
    ## Flow:
    1. Upload 2 Excel files
    2. Convert Excel → JSON
    3. AI Agent analyzes structure
    4. AI Agent plans merge strategy
    5. AI Agent executes merge + calculations
    6. AI Agent validates results
    7. Return analysis report + merged data
    
    ## Input:
    - attendance_file: File chấm công (Mã NV, Số công, Giờ OT)
    - salary_info_file: File lương + template (Lương cơ bản, Phụ cấp, Công thức)
    
    ## Output:
    - Analysis report from Agent
    - Processing status
    - Validation results
    - Download link (if successful)
    """
    
    unique_id = str(uuid.uuid4())
    
    # Paths
    attendance_path = None
    salary_info_path = None
    
    try:
        # === STEP 1: Validate file formats ===
        logger.info(f"🚀 Starting AI processing for request {unique_id}")
        
        for file in [attendance_file, salary_info_file]:
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} phải có định dạng Excel (.xlsx hoặc .xls)"
                )
        
        # === STEP 2: Save uploaded files ===
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)
        
        attendance_path = f"uploads/attendance_{unique_id}.xlsx"
        salary_info_path = f"uploads/salary_{unique_id}.xlsx"
        
        logger.info("📥 Đang lưu files...")
        with open(attendance_path, "wb") as f:
            f.write(await attendance_file.read())
        logger.info(f"✓ Saved: {attendance_file.filename}")
        
        with open(salary_info_path, "wb") as f:
            f.write(await salary_info_file.read())
        logger.info(f"✓ Saved: {salary_info_file.filename}")
        
        # === STEP 3: Convert Excel to JSON ===
        logger.info("📊 Converting Excel to JSON...")
        
        attendance_json = read_excel_complete(attendance_path)
        salary_json = read_excel_complete(salary_info_path)
        
        logger.info(f"✓ Attendance: {len(attendance_json)} sheets")
        logger.info(f"✓ Salary Info: {len(salary_json)} sheets")
        
        # Save JSON for debugging
        attendance_json_path = f"uploads/attendance_{unique_id}.json"
        salary_json_path = f"uploads/salary_{unique_id}.json"
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            """Convert datetime objects to ISO format strings"""
            from datetime import datetime, date
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            return obj
        
        attendance_json_clean = convert_datetime(attendance_json)
        salary_json_clean = convert_datetime(salary_json)
        
        with open(attendance_json_path, 'w', encoding='utf-8') as f:
            json.dump(attendance_json_clean, f, ensure_ascii=False, indent=2)
        
        with open(salary_json_path, 'w', encoding='utf-8') as f:
            json.dump(salary_json_clean, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ JSON files saved for debugging")
        
        # === STEP 4: Prepare message for AI Agent ===
        logger.info("🤖 Calling AI Agent for analysis...")
        
        # Create a comprehensive prompt for the agent with actual JSON content
        agent_message = f"""
🔍 PHASE 1: ANALYZE THESE 2 FILES

FILE 1: ATTENDANCE DATA
File name: {attendance_file.filename}
JSON Content:
```json
{json.dumps(attendance_json_clean, ensure_ascii=False, indent=2)}
```

FILE 2: SALARY INFO + TEMPLATE
File name: {salary_info_file.filename}
JSON Content:
```json
{json.dumps(salary_json_clean, ensure_ascii=False, indent=2)}
```

TASK:
1. Analyze cấu trúc của mỗi file (sheets, headers, data rows)
2. Xác định key fields để join (Mã nhân viên)
3. Phát hiện issues (missing data, duplicates, invalid values)
4. Đưa ra Analysis Report chi tiết

Hãy bắt đầu PHASE 1: ANALYSIS & DISCOVERY
"""
        
        # Call AI Agent
        chat_request = ChatRequest(
            session_id=session_id,
            user_id=user_id,
            message=agent_message
        )
        
        agent_response = salary_agent.chat(chat_request)
        
        logger.info("✓ Agent analysis completed")
        logger.info(f"Agent response preview: {agent_response.response[:200]}...")
        
        # === STEP 5: Convert merged JSON back to Excel ===
        logger.info("📤 Converting merged JSON to Excel...")
        
        output_excel_path = f"outputs/merged_{unique_id}.xlsx"
        
        # Merge 2 JSON files into one (simple merge - keep both sheets)
        merged_json = {
            **attendance_json_clean,
            **salary_json_clean
        }
        
        # Convert merged JSON to Excel
        try:
            success = json_to_excel(merged_json, output_excel_path)
            if success:
                logger.info(f"✓ Excel output created: {output_excel_path}")
            else:
                logger.warning("⚠️ Excel conversion completed with warnings")
        except Exception as excel_error:
            logger.error(f"❌ Excel conversion failed: {excel_error}")
            output_excel_path = None
        
        # === STEP 6: Return response ===
        return {
            "success": True,
            "request_id": unique_id,
            "message": "AI Agent analysis completed and Excel generated",
            "agent_analysis": agent_response.response,
            "files_processed": {
                "attendance": attendance_file.filename,
                "salary_info": salary_info_file.filename
            },
            "json_files": {
                "attendance_json": attendance_json_path,
                "salary_json": salary_json_path
            },
            "output_excel": output_excel_path,
            "download_url": f"/api/v1/download_merged/{unique_id}" if output_excel_path else None,
            "next_steps": [
                "Review analysis report",
                "Download merged Excel file",
                "Proceed to Phase 2: Planning (if needed)",
                "Execute calculations",
                "Validate results"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing files: {str(e)}", exc_info=True)
        
        # Cleanup on error
        for path in [attendance_path, salary_info_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý file: {str(e)}"
        )


@router.post("/import_file_continue")
async def import_file_continue(
    session_id: int = Form(..., description="ID phiên làm việc"),
    user_id: int = Form(..., description="ID người dùng"),
    request_id: str = Form(..., description="Request ID từ bước trước"),
    phase: str = Form(..., description="Phase: planning, execution, validation"),
):
    """
    Continue processing với AI Agent
    
    Phases:
    - planning: Agent lập kế hoạch merge
    - execution: Agent thực hiện merge + tính toán
    - validation: Agent validate kết quả
    """
    
    try:
        logger.info(f"🔄 Continuing phase: {phase} for request {request_id}")
        
        # Load JSON files
        attendance_json_path = f"uploads/attendance_{request_id}.json"
        salary_json_path = f"uploads/salary_{request_id}.json"
        
        if not os.path.exists(attendance_json_path) or not os.path.exists(salary_json_path):
            raise HTTPException(
                status_code=404,
                detail="JSON files not found. Please upload files first."
            )
        
        # Prepare message based on phase
        if phase == "planning":
            agent_message = f"""
📋 PHASE 2: PLANNING

Based on your analysis, now create a detailed execution plan:

1. Design output structure (columns list)
2. Define merge strategy (join type, key, handling missing)
3. List all calculations needed (formulas)
4. Set validation rules

Provide a step-by-step execution plan.
"""
        elif phase == "execution":
            agent_message = f"""
⚙️ PHASE 3: EXECUTION

Execute the plan you created:

1. Parse JSON files
2. Merge data according to plan
3. Calculate all derived fields
4. Format output structure

Show progress and results.
"""
        elif phase == "validation":
            agent_message = f"""
✅ PHASE 4: VALIDATION

Validate the merged results:

1. Check data integrity
2. Verify calculations (spot check 3 employees)
3. Apply business rules validation
4. Generate validation report

Final verdict: APPROVED or REJECTED?
"""
        else:
            raise HTTPException(status_code=400, detail="Invalid phase")
        
        # Call Agent
        chat_request = ChatRequest(
            session_id=session_id,
            user_id=user_id,
            message=agent_message
        )
        
        agent_response = salary_agent.chat(chat_request)
        
        return {
            "success": True,
            "request_id": request_id,
            "phase": phase,
            "agent_response": agent_response.response,
            "next_phase": {
                "planning": "execution",
                "execution": "validation",
                "validation": "complete"
            }.get(phase)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in phase {phase}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi trong phase {phase}: {str(e)}"
        )


@router.get("/download_merged/{request_id}")
async def download_result(request_id: str):
    """
    📥 Download merged Excel file
    
    Returns the merged Excel file created from JSON data.
    """
    try:
        # Use absolute path or ensure correct relative path
        output_path = os.path.abspath(f"outputs/merged_{request_id}.xlsx")
        
        logger.info(f"📥 Download request for: {output_path}")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"File exists: {os.path.exists(output_path)}")
        
        if not os.path.exists(output_path):
            logger.error(f"❌ File not found: {output_path}")
            logger.error(f"Files in outputs/: {os.listdir('outputs') if os.path.exists('outputs') else 'outputs/ not found'}")
            raise HTTPException(
                status_code=404,
                detail=f"File không tồn tại. Request ID: {request_id}"
            )
        
        file_size = os.path.getsize(output_path)
        logger.info(f"✓ Found file: {output_path} ({file_size} bytes)")
        
        return FileResponse(
            path=output_path,
            filename=f"salary_merged_{request_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
