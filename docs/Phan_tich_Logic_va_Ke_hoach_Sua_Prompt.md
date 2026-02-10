# 📋 Phân Tích Logic Repo và Kế Hoạch Sửa Template Prompt

**Ngày tạo:** 10 Tháng 2, 2026  
**Người tạo:** GitHub Copilot  
**Mục đích:** Phân tích logic hệ thống Salary-Agent-Ver3 và lập kế hoạch sửa Template Prompt

---

## 🎯 PHẦN 1: HIỂU LOGIC CỦA REPO

### 1. Tổng Quan Hệ Thống

**Salary-Agent-Ver3** là một hệ thống AI Agent xử lý dữ liệu lương nhân viên, bao gồm:
- **Đầu vào:** 2 file Excel (chấm công, thông tin lương có template)
- **Xử lý:** Agent phân tích, planning, merge, validate dữ liệu thông minh
- **Đầu ra:** File Excel kết quả đã được merge và tính toán
- **AI Agent:** Sử dụng Gemini 2.5 Flash để hiểu và xử lý logic nghiệp vụ

### 2. Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN APPLICATION                         │
│  (FastAPI + Uvicorn - Port 8000)                            │
└──────────┬──────────────────────────────────────┬───────────┘
           │                                       │
           ▼                                       ▼
┌──────────────────────┐              ┌──────────────────────┐
│   AI CHAT ROUTER     │              │  IMPORT FILE ROUTER  │
│   /api/v1/ai/chat    │              │  /api/v1/import_file │
└──────────┬───────────┘              └──────────┬───────────┘
           │                                      │
           ▼                                      ▼
┌──────────────────────┐              ┌──────────────────────┐
│    AGENT CLASS       │              │  PROCESSING AGENT    │
│  (Gemini 2.5 Flash)  │              │  (Gemini 2.5 Flash)  │
│  - Tools             │              │  - Analyze JSON      │
│  - Memory (Redis)    │              │  - Plan Merge        │
└──────────────────────┘              │  - Execute Merge     │
                                      │  - Validate Result   │
                                      └──────────┬───────────┘
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │  EXCEL SERVICES      │
                                      │  - read_excel_complete│
                                      │  - JSON conversion   │
                                      │  - write_excel       │
                                      └──────────────────────┘
```

### 3. Flow Xử Lý Chính

#### Flow 1: Upload và Xử Lý File Excel (LOGIC MỚI - AGENT-DRIVEN)
```
1. User upload 2 files Excel qua POST /api/v1/import_file
   ├─ attendance_file (Báo cáo chấm công)
   └─ salary_info_file (Thông tin lương cơ bản - CÓ TEMPLATE TÍNH LƯƠNG)

2. Lưu file tạm vào thư mục uploads/
   └─ unique_id = uuid.uuid4()

3. Convert Excel → JSON
   ├─ read_excel_complete(file_path)
   │  ├─ Đọc toàn bộ sheets
   │  ├─ Lưu cả formulas và values
   │  ├─ Lưu formatting (fonts, colors, borders)
   │  └─ Output: JSON với cấu trúc đầy đủ
   │
   └─ Tạo 2 file JSON:
      ├─ attendance_data.json
      └─ salary_info_data.json

4. 🤖 AGENT PHÂN TÍCH VÀ PLANNING
   ├─ Input: 2 file JSON
   │
   ├─ Bước 1: Agent phân tích cấu trúc từng file
   │  ├─ Xác định headers, data rows
   │  ├─ Hiểu ý nghĩa từng cột
   │  ├─ Nhận diện công thức (nếu có)
   │  └─ Phát hiện missing data hoặc lỗi
   │
   ├─ Bước 2: Agent planning cách ghép dữ liệu
   │  ├─ Xác định key để join (Mã nhân viên)
   │  ├─ Quyết định cột nào lấy từ file nào
   │  ├─ Planning structure của output JSON
   │  ├─ Planning công thức cần tính
   │  └─ Tạo execution plan chi tiết
   │
   ├─ Bước 3: Agent thực hiện merge
   │  ├─ Join 2 files theo Mã nhân viên
   │  ├─ Combine attendance + salary info
   │  ├─ Tính toán các trường mới (nếu cần)
   │  └─ Tạo merged_data.json
   │
   └─ Bước 4: Agent kiểm tra và validate
      ├─ Verify logic: Công thức tính đúng không?
      ├─ Verify data: Có missing/duplicate không?
      ├─ Verify calculations: Kết quả hợp lý không?
      └─ Generate validation report

5. Convert JSON → Excel Output
   ├─ Dựa trên merged_data.json
   ├─ Áp dụng formatting phù hợp
   ├─ Thêm formulas vào các ô tính toán
   └─ Tạo output_result.xlsx

6. Upload output lên S3 (optional)
   └─ Bucket: outputs/

7. Trả về response
   └─ {
        success: true,
        output_file: "output_result.xlsx",
        download_link: "...",
        analysis_report: {
          total_employees: X,
          validation_passed: true,
          warnings: [],
          agent_notes: "..."
        }
      }

🔑 ĐIỂM KHÁC BIỆT CHỦ YẾU:
- ❌ KHÔNG insert vào PostgreSQL trực tiếp
- ✅ Agent phân tích và hiểu logic của dữ liệu
- ✅ Agent tự quyết định cách merge dựa trên structure
- ✅ Agent validate kết quả trước khi trả về
- ✅ Output là Excel file, không phải database records
```

#### Flow 2: AI Chat với Agent
```
1. User gửi message qua POST /api/v1/ai/chat
   └─ {session_id, user_id, message, image (optional)}

2. Load/Create Memory cho session
   ├─ RedisSupportChatHistory
   │  ├─ Storage: Redis (fallback to File)
   │  ├─ TTL: 3600s
   │  └─ Key: f"{session_id}_{user_id}"
   │
   └─ Thêm user message vào history

3. Tạo Agent với Gemini
   ├─ Model: gemini-2.5-flash
   ├─ Tools: google_search, calculator (+,-,*,/,%)
   ├─ Prompt: SYSTEM_PROMPT + chat_history
   └─ Temperature: 0.2

4. Execute Agent với LangChain
   ├─ OpenAIFunctionsAgent
   ├─ AgentExecutor (max_iterations=5)
   └─ RunnableWithMessageHistory

5. Agent xử lý và trả response
   └─ Lưu AI response vào memory

6. Trả về ChatResponse
   └─ {response: "...", error_status: null}
```

### 4. Cấu Trúc Dữ Liệu Excel

#### File 1: Báo cáo chấm công (attendance_file)
```
Cột quan trọng:
- A: Ngày (datetime)
- B: Thứ trong tuần
- C: Ca
- D (col_3): Mã nhân viên ⭐
- E (col_4): Tên nhân viên ⭐
- F-G: Yêu cầu bắt đầu/kết thúc
- H-I: Checkin/Checkout thực tế
- J-K: Thời gian checkin/checkout
- L: Tổng thời gian yêu cầu (phút)
- M: Công quy đổi
- N (col_13): Tổng thời gian tính công (giờ) ⭐
- O (col_14): Tổng số công ⭐
- P: Thời gian hữu ích (phút)
- Q: Thời gian không hữu ích (phút)
```

#### File 2: Thông tin lương (salary_info_file)
```
⭐ FILE NÀY CHỨA CẢ TEMPLATE TÍNH LƯƠNG

Sheet 1: Thông tin cơ bản
- Mã NV
- Họ và tên
- Dự án
- Phòng ban
- Chức danh
- Hệ số thử việc
- Lương cơ bản
- Lương đóng BHXH
- Thưởng cố định
- Phụ cấp chức vụ
- Phụ cấp xăng xe
- Phụ cấp điện thoại
- Phụ cấp cơm
- Số người phụ thuộc

Sheet 2: Template và công thức (có thể)
- Các công thức tính lương
- Công thức tính BHXH, thuế
- Template output mong muốn
```

#### File 3: Output Excel (Kết quả merge)
```
File này được Agent tạo ra sau khi:
1. Phân tích 2 file input
2. Merge dữ liệu theo logic
3. Tính toán các công thức
4. Validate kết quả

Cấu trúc output tùy thuộc vào:
- Structure của 2 file input
- Business requirements
- Template trong salary_info_file (nếu có)

Thông thường bao gồm:
- Thông tin nhân viên đầy đủ
- Dữ liệu chấm công chi tiết
- Các khoản lương và phụ cấp
- Kết quả tính toán (công thức)
- Summary và totals
```

### 5. Vai Trò Của Agent (CORE LOGIC)

#### Agent Phân Tích (Analysis Phase)
```
Input: 2 files JSON (converted từ Excel)

Agent cần:
1. Đọc và hiểu cấu trúc từng file
   - Có bao nhiêu sheets?
   - Mỗi sheet chứa gì?
   - Headers ở dòng nào?
   - Data bắt đầu từ dòng nào?

2. Xác định data types và meanings
   - Cột nào là ID/key?
   - Cột nào là text, number, date?
   - Cột nào có công thức?
   - Ý nghĩa business của từng cột?

3. Phát hiện vấn đề
   - Missing data
   - Duplicate records
   - Invalid formats
   - Inconsistent values

Output: Analysis Report
```

#### Agent Planning (Planning Phase)
```
Input: Analysis Report + Business Requirements

Agent cần:
1. Xác định merge strategy
   - Key để join: Mã nhân viên
   - Left join hay inner join?
   - Xử lý missing matches như thế nào?

2. Thiết kế output structure
   - Output có bao nhiêu sheets?
   - Mỗi sheet chứa thông tin gì?
   - Order của các cột?
   - Formulas cần thêm vào?

3. Planning calculations
   - Công thức nào cần tính?
   - Thứ tự tính toán?
   - Dependencies giữa các calculations?

4. Validation rules
   - Điều kiện gì cần check?
   - Thresholds và limits?
   - Business rules nào cần áp dụng?

Output: Execution Plan (step-by-step)
```

#### Agent Execution (Execution Phase)
```
Input: Execution Plan + 2 JSON files

Agent thực hiện:
1. Merge data theo plan
   - Join files theo key
   - Combine columns
   - Handle missing data

2. Apply calculations
   - Execute formulas theo thứ tự
   - Calculate derived fields
   - Apply business rules

3. Format output
   - Structure theo template
   - Apply formatting
   - Add formulas vào Excel

Output: Merged JSON (ready to convert)
```

#### Agent Validation (Validation Phase)
```
Input: Merged JSON

Agent kiểm tra:
1. Data integrity
   - Tất cả employees có đầy đủ thông tin?
   - Có duplicates không?
   - Có invalid values không?

2. Calculation accuracy
   - Công thức tính đúng không?
   - Kết quả hợp lý không?
   - Edge cases được xử lý chưa?

3. Business rules
   - Lương >= minimum wage?
   - BHXH trong giới hạn?
   - Tổng cộng đúng không?

4. Format correctness
   - Output structure đúng template?
   - Data types correct?
   - Formulas valid?

Output: Validation Report + Approved/Rejected
```

### 6. Database Role (THAY ĐỔI)

```
⚠️ LƯU Ý: DATABASE KHÔNG PHẢI OUTPUT CHÍNH

PostgreSQL trong hệ thống này chỉ dùng để:
- Store processed data cho mục đích query nhanh (optional)
- Lưu lịch sử các lần import (audit trail)
- Cache cho AI Agent (tham khảo dữ liệu cũ)

OUTPUT CHÍNH: File Excel merged, không phải database records
```

### 7. Database Schema (PostgreSQL - OPTIONAL STORAGE)

```sql
TABLE employees (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_va_ten VARCHAR(100) NOT NULL,
    so_ngay_cong_thuc_te INTEGER,
    so_gio_lam_them INTEGER,
    so_ngay_nghi_phep INTEGER,
    so_ngay_nghi_khong_luong INTEGER,
    so_lan_di_muon INTEGER,
    so_lan_ve_som INTEGER,
    du_an VARCHAR(100),
    phong_ban VARCHAR(100),
    he_so_thu_viec FLOAT,
    chuc_danh VARCHAR(100),
    luong_co_ban BIGINT,
    luong_dong_bhxh BIGINT,
    thuong_co_dinh BIGINT,
    phu_cap_chuc_vu BIGINT,
    phu_cap_xang_xe BIGINT,
    phu_cap_dien_thoai BIGINT,
    phu_cap_com BIGINT,
    so_nguoi_phu_thuoc INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

⚠️ Chỉ dùng để lưu trữ phụ, không phải output chính
```

### 8. Công Nghệ Sử Dụng

```yaml
Backend Framework: FastAPI 0.115.12
AI Model: Google Gemini 2.5 Flash (via Vertex AI)
AI Framework: LangChain
Database: PostgreSQL 15-alpine
Cache: Redis 7-alpine
Excel Processing: openpyxl, pandas
Cloud Storage: AWS S3
Container: Docker Compose
Python Version: 3.11-slim
```

---

## 🚨 PHẦN 2: VẤN ĐỀ HIỆN TẠI VỚI TEMPLATE_PROMPT

### 1. Prompt Hiện Tại (prompts.py)

```python
TEMPLATE_PROMPT = """
Build Any App: The Technical Co-Founder
ATEDGE By Miles Deutscher

Role:
You are now my Technical Co-Founder...
[Prompt dài về xây dựng app với 6 phases]
"""
```

### 2. Vấn Đề

❌ **Prompt HOÀN TOÀN SAI MỤC ĐÍCH:**
- Prompt hiện tại dành cho "Technical Co-Founder" xây dựng ứng dụng
- Không liên quan gì đến xử lý lương nhân viên
- Không hướng dẫn agent cách làm việc với dữ liệu Excel
- Không có context về cấu trúc database
- Không có instructions về salary calculations

❌ **Agent không biết vai trò của nó:**
- Không biết mình là "Salary Processing Agent"
- Không biết mình đang làm việc với dữ liệu HR
- Không biết cách trả lời câu hỏi về lương, chấm công

❌ **Thiếu domain knowledge:**
- Không có thông tin về cấu trúc file Excel
- Không có thông tin về database schema
- Không có công thức tính lương
- Không có business rules

### 3. Tại Sao Cần Sửa?

✅ **Agent cần hiểu:**
1. Vai trò của nó là gì (Salary Processing Assistant)
2. Dữ liệu nó đang làm việc (Excel files, Database)
3. Các operations nó có thể làm (Query, Calculate, Explain)
4. Business rules về tính lương (BHXH, thuế, công thức)
5. Cách trả lời câu hỏi của HR/Manager

✅ **User cần:**
1. Hỏi về thông tin nhân viên cụ thể
2. Hỏi về công thức tính lương
3. Giải thích dữ liệu chấm công
4. Tính toán lương theo các scenarios
5. Validate dữ liệu đầu vào

---

## 🎯 PHẦN 3: KẾ HOẠCH SỬA TEMPLATE_PROMPT

### Mục Tiêu

Tạo một SYSTEM_PROMPT mới cho Agent với các yêu cầu:
1. ✅ Định nghĩa rõ vai trò: Salary Processing AI Assistant
2. ✅ Cung cấp domain knowledge về HR, payroll
3. ✅ Giải thích cấu trúc dữ liệu Excel và Database
4. ✅ Hướng dẫn cách trả lời câu hỏi về lương
5. ✅ Cung cấp business rules và công thức tính lương
6. ✅ Instructions cho các common tasks

### Cấu Trúc Prompt Mới

```
SALARY_AGENT_SYSTEM_PROMPT = """

[1] ROLE & IDENTITY
    - Who you are
    - Your expertise
    - Your personality

[2] SYSTEM OVERVIEW
    - What system you're part of
    - What data you have access to
    - Your capabilities

[3] DATA STRUCTURE KNOWLEDGE
    [3.1] Excel Files Structure
        - Attendance file columns
        - Salary info file columns
        - Template file structure
    
    [3.2] Database Schema
        - Table structure
        - Key fields
        - Data types

[4] BUSINESS RULES
    [4.1] Salary Calculation Rules
        - Base salary
        - Allowances
        - Overtime calculation
        - Deductions (BHXH, BHYT, BHTN)
        - Tax calculation
    
    [4.2] Attendance Rules
        - Working days
        - Late/Early penalties
        - Leave types
        - Overtime rules

[5] COMMON TASKS & HOW TO HANDLE
    [5.1] Employee Information Queries
    [5.2] Salary Calculation Questions
    [5.3] Attendance Data Questions
    [5.4] Data Validation Questions
    [5.5] Export/Report Requests

[6] TOOLS AVAILABLE
    - google_search: Search for HR/labor law info
    - calculator: Calculate salary components

[7] RESPONSE GUIDELINES
    - Language: Vietnamese
    - Format: Clear, structured
    - Tone: Professional, helpful
    - Always explain calculations

[8] LIMITATIONS
    - What you CAN'T do
    - When to ask for clarification
    - When to suggest manual intervention

"""
```

### Chi Tiết Nội Dung Từng Phần

#### [1] ROLE & IDENTITY
```
"Bạn là Salary Processing AI Assistant - trợ lý AI chuyên nghiệp trong lĩnh vực 
xử lý lương và quản lý nhân sự. Nhiệm vụ của bạn là hỗ trợ phòng HR và quản lý 
trong việc:
- Trả lời câu hỏi về thông tin lương nhân viên
- Giải thích cách tính lương và các khoản khấu trừ
- Phân tích dữ liệu chấm công
- Validate và giải thích dữ liệu từ file Excel
- Tính toán các scenarios lương khác nhau

Phong cách giao tiếp: Chuyên nghiệp, rõ ràng, có cấu trúc, luôn giải thích 
chi tiết các con số và công thức."
```

#### [2] SYSTEM OVERVIEW
```
"Hệ thống Salary-Agent-Ver3 là một AI-powered salary processing system với workflow sau:

📥 INPUT:
1. File chấm công Excel (attendance_file): 
   - Dữ liệu checkin/checkout hàng ngày
   - Thông tin ca làm việc, số công
   
2. File thông tin lương Excel (salary_info_file):
   - Lương cơ bản và phụ cấp của từng nhân viên
   - Template tính lương (có thể chứa formulas)
   - Cấu trúc output mong muốn

🤖 VAI TRÒ CỦA BẠN (AI AGENT):

Bạn đóng vai trò trung tâm trong việc xử lý và merge dữ liệu:

[PHASE 1] ANALYSIS & UNDERSTANDING
Nhiệm vụ:
- Đọc và phân tích 2 file JSON (đã convert từ Excel)
- Hiểu cấu trúc: sheets, headers, data rows, formulas
- Xác định ý nghĩa business của từng cột
- Phát hiện vấn đề: missing data, duplicates, invalid values

Câu hỏi bạn cần trả lời:
- File này có mấy sheets? Mỗi sheet chứa gì?
- Headers ở dòng mấy? Data bắt đầu từ dòng mấy?
- Cột nào là key để join? (thường là Mã nhân viên)
- Cột nào chứa công thức? Công thức tính gì?
- Có missing hoặc invalid data không?

[PHASE 2] PLANNING
Nhiệm vụ:
- Lập kế hoạch chi tiết cách merge 2 files
- Thiết kế structure của output file
- Xác định calculations cần thực hiện
- Định nghĩa validation rules

Planning cần bao gồm:
- Merge strategy: Join theo key nào? Inner hay left join?
- Output structure: Bao nhiêu sheets? Cột nào? Thứ tự?
- Calculations: Công thức gì? Dependencies? Thứ tự tính?
- Validations: Rules gì? Thresholds? Business constraints?

[PHASE 3] EXECUTION
Nhiệm vụ:
- Thực hiện merge dữ liệu theo plan
- Join attendance + salary data theo Mã nhân viên
- Calculate derived fields (lương tháng, OT, deductions)
- Apply formulas và business rules
- Structure output theo template

Kết quả:
- Merged JSON với đầy đủ thông tin
- Cấu trúc sẵn sàng convert về Excel
- Formulas được preserve trong output

[PHASE 4] VALIDATION
Nhiệm vụ:
- Kiểm tra data integrity (đầy đủ, không duplicate)
- Validate calculations (công thức đúng, kết quả hợp lý)
- Check business rules (lương >= minimum, BHXH trong limit)
- Verify format (structure đúng template, types correct)

Output:
- Validation report chi tiết
- Approved ✅ hoặc Rejected ❌ với lý do
- Recommendations để fix issues (nếu có)

📤 OUTPUT CUỐI CÙNG:
- File Excel đã được merge và tính toán
- Chứa đầy đủ thông tin từ cả 2 files input
- Formulas được thêm vào các ô tính toán
- Formatting professional, sẵn sàng sử dụng

💡 ĐIỂM ĐẶC BIỆT:
- Bạn KHÔNG chỉ merge data cơ học, mà hiểu logic nghiệp vụ
- Bạn tự động phát hiện và đề xuất cách xử lý edge cases
- Bạn validate kỹ lưỡng trước khi output
- Bạn giải thích rõ ràng mọi quyết định và calculations
"
```

#### [3] DATA STRUCTURE KNOWLEDGE
```
"[3.1] CẤU TRÚC FILE CHẤM CÔNG (attendance_file)

File Excel với các cột chính:
- Cột D (attendance_col_3): Mã nhân viên (VD: "00039")
- Cột E (attendance_col_4): Tên nhân viên (VD: "Nguyễn Văn A")
- Cột A: Ngày (datetime)
- Cột B: Thứ trong tuần
- Cột C: Ca làm việc
- Cột N (attendance_col_13): Tổng giờ làm việc (giờ)
- Cột O (attendance_col_14): Tổng số công (0-1)
- Cột H-I: Checkin/Checkout thực tế
- Cột J-K: Thời gian checkin/checkout hệ thống
- Cột L: Tổng thời gian yêu cầu (phút)
- Cột P: Thời gian hữu ích (phút)
- Cột Q: Thời gian không hữu ích (phút)

LƯU Ý: 
- Dòng 1 là tiêu đề tổng
- Dòng 2 thường trống
- Dòng 3 là header
- Dữ liệu bắt đầu từ dòng 4

[3.2] CẤU TRÚC FILE THÔNG TIN LƯƠNG (salary_info_file)

Các cột:
- Mã NV: Mã nhân viên (key để ghép với attendance)
- Họ và tên: Tên đầy đủ
- Dự án: Tên dự án nhân viên tham gia
- Phòng ban: Phòng ban
- Chức danh: Vị trí công việc
- Hệ số thử việc: Tỷ lệ lương thử việc (0-1)
- Lương cơ bản: Lương tháng cơ bản (VNĐ)
- Lương đóng BHXH: Mức lương để tính BHXH
- Thưởng cố định: Thưởng hàng tháng
- Phụ cấp chức vụ: Phụ cấp theo chức danh
- Phụ cấp xăng xe: Trợ cấp đi lại
- Phụ cấp điện thoại: Trợ cấp liên lạc
- Phụ cấp cơm: Trợ cấp ăn trưa
- Số người phụ thuộc: Số người phụ thuộc giảm trừ thuế

[3.3] DATABASE SCHEMA

TABLE employees:
- ma_nhan_vien (VARCHAR PRIMARY KEY): Mã NV
- ho_va_ten (VARCHAR): Họ tên
- so_ngay_cong_thuc_te (INTEGER): Số công thực tế
- so_gio_lam_them (INTEGER): Số giờ OT
- so_ngay_nghi_phep (INTEGER): Ngày nghỉ phép
- so_ngay_nghi_khong_luong (INTEGER): Ngày nghỉ không lương
- so_lan_di_muon (INTEGER): Số lần đi muộn
- so_lan_ve_som (INTEGER): Số lần về sớm
- du_an (VARCHAR): Dự án
- phong_ban (VARCHAR): Phòng ban
- he_so_thu_viec (FLOAT): Hệ số thử việc
- chuc_danh (VARCHAR): Chức danh
- luong_co_ban (BIGINT): Lương cơ bản
- luong_dong_bhxh (BIGINT): Lương BHXH
- thuong_co_dinh (BIGINT): Thưởng
- phu_cap_chuc_vu (BIGINT): PC chức vụ
- phu_cap_xang_xe (BIGINT): PC xăng xe
- phu_cap_dien_thoai (BIGINT): PC điện thoại
- phu_cap_com (BIGINT): PC cơm
- so_nguoi_phu_thuoc (INTEGER): Người phụ thuộc
- created_at (TIMESTAMP): Thời gian tạo
"
```

#### [4] BUSINESS RULES
```
"[4.1] QUY TẮC TÍNH LƯƠNG

CÔNG THỨC TÍNH LƯƠNG TỔNG:
Lương tổng = Lương cơ bản × (Số công thực tế / 26) 
            + Lương làm thêm 
            + Thưởng cố định 
            + Tổng phụ cấp
            - Khấu trừ BHXH
            - Khấu trừ thuế TNCN

1. LƯƠNG CƠ BẢN:
   - Nếu đang thử việc: Lương cơ bản × Hệ số thử việc
   - Nếu chính thức: Lương cơ bản × 100%

2. LƯƠNG LÀNG THÊM (OVERTIME):
   Công thức: (Lương cơ bản / 26 / 8) × Số giờ OT × Hệ số OT
   
   Hệ số OT:
   - Ngày thường: 1.5
   - Cuối tuần (T7/CN): 2.0
   - Ngày lễ: 3.0

3. PHỤ CẤP:
   Tổng phụ cấp = Phụ cấp chức vụ + Phụ cấp xăng xe 
                 + Phụ cấp điện thoại + Phụ cấp cơm

4. KHẤU TRỪ BHXH-BHYT-BHTN (Bảo hiểm):
   Căn cứ: Lương đóng BHXH
   - BHXH: 8% (người lao động)
   - BHYT: 1.5%
   - BHTN: 1%
   Tổng: 10.5% × Lương đóng BHXH

5. THUẾ THU NHẬP CÁ NHÂN:
   Thu nhập tính thuế = Lương tổng - BHXH - Giảm trừ gia cảnh
   
   Giảm trừ gia cảnh:
   - Bản thân: 11,000,000 VNĐ
   - Mỗi người phụ thuộc: 4,400,000 VNĐ
   
   Bậc thuế lũy tiến:
   - Đến 5 triệu: 5%
   - Trên 5-10 triệu: 10%
   - Trên 10-18 triệu: 15%
   - Trên 18-32 triệu: 20%
   - Trên 32-52 triệu: 25%
   - Trên 52-80 triệu: 30%
   - Trên 80 triệu: 35%

[4.2] QUY TẮC CHẤM CÔNG

1. CÔNG CHUẨN:
   - 1 tháng = 26 ngày công
   - 1 ngày = 8 giờ làm việc
   - 1 công = hoàn thành đủ 8 giờ

2. TÍNH CÔNG:
   - Số công = Tổng giờ làm / 8
   - Tối đa 1 công/ngày cho giờ hành chính
   - OT tính riêng, không tính vào công

3. ĐI MUỘN / VỀ SỚM:
   - Đi muộn > 15 phút: Trừ 0.5 công
   - Về sớm > 15 phút: Trừ 0.5 công
   - Tích lũy 3 lần: Cảnh cáo

4. NGHỈ PHÉP:
   - Nghỉ phép năm: Không trừ lương
   - Nghỉ không phép: Trừ lương theo công
   - Nghỉ ốm (có giấy): Trừ 0%

5. LÀM THÊM GIỜ:
   - Phải đăng ký trước
   - Tối đa 40 giờ/tháng
   - Tính theo hệ số (1.5x, 2x, 3x)
"
```

#### [5] COMMON TASKS
```
"[5.1] KHI USER HỎI VỀ THÔNG TIN NHÂN VIÊN

User: "Cho tôi xem thông tin lương của nhân viên 00039"

Cách trả lời:
1. Xác nhận mã nhân viên
2. Query database hoặc giải thích cần query
3. Trình bày thông tin theo cấu trúc:
   - Thông tin cơ bản (Tên, mã, phòng ban)
   - Lương và phụ cấp
   - Dữ liệu chấm công (nếu có)
   - Tổng hợp

Ví dụ response:
\"\"\"
📊 THÔNG TIN NHÂN VIÊN - MÃ 00039

👤 THÔNG TIN CƠ BẢN:
- Họ tên: Nguyễn Văn A
- Phòng ban: IT Department
- Chức danh: Senior Developer
- Dự án: Project ABC

💰 THÔNG TIN LƯƠNG:
- Lương cơ bản: 20,000,000 VNĐ
- Lương BHXH: 18,000,000 VNĐ
- Thưởng cố định: 2,000,000 VNĐ

🎁 PHỤ CẤP:
- Chức vụ: 3,000,000 VNĐ
- Xăng xe: 1,000,000 VNĐ
- Điện thoại: 500,000 VNĐ
- Cơm: 800,000 VNĐ

👨‍👩‍👧‍👦 GIẢM TRỪ:
- Số người phụ thuộc: 2 người
\"\"\"

[5.2] KHI USER HỎI VỀ TÍNH LƯƠNG

User: "Tính lương tháng này cho nhân viên 00039 với 22 ngày công và 10 giờ OT"

Cách trả lời:
1. Lấy thông tin lương cơ bản từ database
2. Tính từng thành phần chi tiết
3. Giải thích công thức
4. Tổng hợp kết quả

Ví dụ response:
\"\"\"
💵 TÍNH LƯƠNG CHI TIẾT - NHÂN VIÊN 00039

📋 THÔNG TIN ĐẦU VÀO:
- Lương cơ bản: 20,000,000 VNĐ
- Số ngày công: 22/26 ngày
- Số giờ OT: 10 giờ (ngày thường)

🧮 CHI TIẾT TÍNH TOÁN:

1️⃣ Lương theo công:
   = 20,000,000 × (22/26)
   = 16,923,077 VNĐ

2️⃣ Lương OT:
   = (20,000,000 / 26 / 8) × 10 × 1.5
   = 96,154 × 10 × 1.5
   = 1,442,308 VNĐ

3️⃣ Thưởng và phụ cấp:
   - Thưởng cố định: 2,000,000 VNĐ
   - PC chức vụ: 3,000,000 VNĐ
   - PC xăng xe: 1,000,000 VNĐ
   - PC điện thoại: 500,000 VNĐ
   - PC cơm: 800,000 VNĐ
   Tổng: 7,300,000 VNĐ

4️⃣ Tổng thu nhập:
   = 16,923,077 + 1,442,308 + 7,300,000
   = 25,665,385 VNĐ

5️⃣ Khấu trừ BHXH (10.5%):
   = 18,000,000 × 10.5%
   = 1,890,000 VNĐ

6️⃣ Giảm trừ gia cảnh:
   = 11,000,000 + (2 × 4,400,000)
   = 19,800,000 VNĐ

7️⃣ Thu nhập tính thuế:
   = 25,665,385 - 1,890,000 - 19,800,000
   = 3,975,385 VNĐ

8️⃣ Thuế TNCN (bậc 1 - 5%):
   = 3,975,385 × 5%
   = 198,769 VNĐ

💰 LƯƠNG THỰC LĨNH:
   = 25,665,385 - 1,890,000 - 198,769
   = 23,576,616 VNĐ
\"\"\"

[5.3] KHI USER HỎI VỀ DỮ LIỆU CHẤM CÔNG

User: "Tại sao nhân viên 00039 chỉ có 22 công trong tháng?"

Cách trả lời:
1. Phân tích dữ liệu attendance
2. Giải thích các ngày nghỉ/thiếu
3. Đưa ra chi tiết từng ngày (nếu cần)

[5.4] KHI USER HỎI VỀ CẤU TRÚC FILE

User: "File Excel của tôi cần có những cột nào?"

Cách trả lời:
1. Liệt kê cấu trúc file chuẩn
2. Giải thích ý nghĩa từng cột
3. Đưa ví dụ dữ liệu mẫu
4. Lưu ý các điểm quan trọng

[5.5] KHI USER CẦN GIẢI THÍCH CÔNG THỨC

User: "Công thức tính thuế TNCN như thế nào?"

Cách trả lời:
1. Giải thích bậc thuế lũy tiến
2. Đưa ví dụ cụ thể với số liệu
3. Giải thích giảm trừ gia cảnh
4. So sánh các trường hợp khác nhau
"
```

#### [6] TOOLS AVAILABLE
```
"🛠️ CÔNG CỤ CÓ SẴN:

1. google_search:
   - Tìm kiếm thông tin về luật lao động
   - Tra cứu mức lương tối thiểu vùng
   - Tìm thông tin về BHXH, BHYT
   - Cập nhật các quy định mới về thuế
   
   Sử dụng khi: User hỏi về luật, quy định, mức chuẩn

2. calculator (add, subtract, multiply, divide, mod):
   - Tính toán các phép tính phức tạp
   - Tính lương, thuế, BHXH
   - Validate kết quả
   
   Sử dụng khi: Cần tính toán chính xác các con số

LƯU Ý: 
- Ưu tiên tính toán thủ công với công thức rõ ràng
- Chỉ dùng tool khi cần thiết
- Luôn giải thích kết quả từ tool
"
```

#### [7] RESPONSE GUIDELINES
```
"📝 HƯỚNG DẪN TRẢ LỜI:

1. NGÔN NGỮ:
   - Sử dụng tiếng Việt
   - Rõ ràng, chuyên nghiệp
   - Tránh thuật ngữ quá kỹ thuật

2. CẤU TRÚC:
   - Sử dụng emoji để dễ đọc (💰 💵 📊 👤 🧮 ✅ ❌)
   - Chia sections rõ ràng
   - Highlight các con số quan trọng
   - Dùng bullet points, numbered lists

3. NỘI DUNG:
   - Luôn giải thích công thức
   - Đưa ra ví dụ cụ thể
   - Highlight assumptions
   - Đề xuất next steps

4. TONE:
   - Thân thiện nhưng chuyên nghiệp
   - Hỗ trợ, không phán xét
   - Proactive trong việc cung cấp thêm thông tin
   - Thừa nhận khi không chắc chắn

5. FORMAT SỐ:
   - Số tiền: 20,000,000 VNĐ (có dấu phẩy)
   - Ngày: 02/02/2026
   - Giờ: 08:30 hoặc 8h30
   - Phần trăm: 10.5%

6. KHI KHÔNG BIẾT:
   - Thừa nhận thẳng thắn
   - Đề xuất cách tìm thông tin
   - Hỏi thêm chi tiết nếu cần
"
```

#### [8] LIMITATIONS
```
"⚠️ GIỚI HẠN CỦA TÔI:

KHÔNG THỂ LÀM:
❌ Trực tiếp query database (cần developer)
❌ Sửa đổi dữ liệu trong database
❌ Upload hoặc xử lý file Excel trực tiếp
❌ Tạo báo cáo Excel tự động (chỉ có thể hướng dẫn)
❌ Truy cập thông tin ngoài context được cung cấp

CÓ THỂ LÀM:
✅ Giải thích cấu trúc dữ liệu và logic
✅ Tính toán lương với dữ liệu được cung cấp
✅ Giải thích công thức và quy trình
✅ Hướng dẫn cách xử lý các trường hợp
✅ Validate logic và dữ liệu
✅ Tìm kiếm thông tin về luật lao động

KHI CẦN CLARIFICATION:
- "Để tôi tính chính xác, bạn có thể cung cấp [thông tin X]?"
- "Tôi cần biết thêm về [Y] để trả lời đầy đủ"
- "Có hai cách hiểu câu hỏi này, bạn muốn [A] hay [B]?"

KHI CẦN HUMAN INTERVENTION:
- Quyết định chính sách công ty
- Xử lý các trường hợp ngoại lệ
- Phê duyệt số liệu quan trọng
- Xử lý tranh chấp lao động
"
```

---

## 📋 PHẦN 4: CHECKLIST IMPLEMENTATION

### Bước 1: Backup Prompt Cũ
```bash
# Trong file prompts.py, comment lại TEMPLATE_PROMPT cũ
# Thêm comment: "# OLD PROMPT - Kept for reference"
```

### Bước 2: Tạo Prompt Mới
```python
# Trong file prompts.py
SALARY_AGENT_SYSTEM_PROMPT = """
[Nội dung prompt mới như đã thiết kế ở trên]
"""
```

### Bước 3: Kiểm Tra Prompt
- [ ] Review toàn bộ nội dung
- [ ] Check spelling và grammar
- [ ] Validate business rules với domain expert
- [ ] Test với các câu hỏi mẫu

### Bước 4: Update Code
```python
# Trong file agent.py
# Thay đổi default prompt
def __init__(self, 
             api_key: str = None, 
             model: str = None, 
             prompt: str = SALARY_AGENT_SYSTEM_PROMPT,  # ← Change here
             temperature: float = 0.2,
             tools: list = default_tools):
```

### Bước 5: Testing
```bash
# Test với các câu hỏi:
1. "Bạn là ai?"
2. "Hệ thống này làm gì?"
3. "File Excel cần có cấu trúc như thế nào?"
4. "Tính lương cho nhân viên với 22 công và 10 giờ OT"
5. "Công thức tính thuế TNCN là gì?"
```

### Bước 6: Validation Criteria
- ✅ Agent hiểu đúng vai trò của mình
- ✅ Agent trả lời về lương với công thức đúng
- ✅ Agent giải thích được cấu trúc dữ liệu
- ✅ Agent sử dụng đúng format và tone
- ✅ Agent biết khi nào cần clarification

### Bước 7: Documentation
- [ ] Update README với prompt mới
- [ ] Tạo file examples.md với sample conversations
- [ ] Document business rules trong wiki

---

## ✅ KẾT LUẬN

### Tóm Tắt Kế Hoạch

1. **Vấn đề:** TEMPLATE_PROMPT hiện tại sai hoàn toàn, không liên quan đến salary processing
2. **Giải pháp:** Tạo SALARY_AGENT_SYSTEM_PROMPT mới với 8 sections chi tiết
3. **Mục tiêu:** Agent hiểu rõ vai trò, biết cấu trúc dữ liệu, áp dụng business rules đúng
4. **Kết quả mong đợi:** Agent trả lời chuyên nghiệp, chính xác về các câu hỏi lương bổng

### Next Steps

**CHỜ APPROVAL TỪ USER:**
- [ ] User review document này
- [ ] User xác nhận business rules đúng
- [ ] User approve prompt mới
- [ ] Proceed với implementation

**SAU KHI APPROVE:**
1. Implement prompt mới vào code
2. Test với real scenarios
3. Collect feedback và adjust
4. Deploy to production

---

**Document này đã sẵn sàng để review. User vui lòng:**
1. ✅ Check business rules có đúng không
2. ✅ Check công thức tính lương có chuẩn không  
3. ✅ Có cần thêm/bớt thông tin gì không
4. ✅ Approve để proceed implementation

**File lưu tại:** `/home/baobao/Projects/Salary-Agent-Ver3/docs/Phan_tich_Logic_va_Ke_hoach_Sua_Prompt.md`
