# 🔄 CODE LOGIC UPDATE - Salary Agent Ver3

**Ngày cập nhật:** 10 Tháng 2, 2026  
**Thay đổi:** Implement SALARY_AGENT_SYSTEM_PROMPT theo cấu trúc TEMPLATE_PROMPT

---

## ✅ CÁC FILE ĐÃ THAY ĐỔI

### 1. `/template/agent/prompts.py`

**Thay đổi:**
- ✅ Cập nhật `SALARY_AGENT_SYSTEM_PROMPT` hoàn toàn mới
- ✅ Theo cấu trúc của `TEMPLATE_PROMPT` (Role + Framework + Rules)
- ✅ Giữ nguyên `SYSTEM_PROMPT` và `TEMPLATE_PROMPT` cũ

**Nội dung mới:**
```python
SALARY_AGENT_SYSTEM_PROMPT = """
Salary Data Processing Agent - Your AI Co-Processor for Payroll

Role: [Định nghĩa vai trò rõ ràng]

4-Phase Framework:
├─ Phase 1: ANALYSIS & DISCOVERY
├─ Phase 2: PLANNING  
├─ Phase 3: EXECUTION
└─ Phase 4: VALIDATION

Vietnam Salary Rules: [Công thức chi tiết]
Response Standards: [Format chuẩn]
Critical Rules: [Nguyên tắc bắt buộc]
"""
```

### 2. `/template/agent/agent.py`

**Thay đổi:**

#### 2.1 Import Statement (Line ~17)
```python
# CŨ:
from template.agent.prompts import SYSTEM_PROMPT

# MỚI:
from template.agent.prompts import SYSTEM_PROMPT, SALARY_AGENT_SYSTEM_PROMPT
```

#### 2.2 Agent __init__ Default Prompt (Line ~137)
```python
# CŨ:
def __init__(self, 
             api_key: str = None, 
             model: str = None, 
             prompt: str = SYSTEM_PROMPT,  # ← Old default
             temperature: float = 0.2,
             tools: list = default_tools):

# MỚI:
def __init__(self, 
             api_key: str = None, 
             model: str = None, 
             prompt: str = SALARY_AGENT_SYSTEM_PROMPT,  # ← New default
             temperature: float = 0.2,
             tools: list = default_tools):
```

---

## 🎯 LOGIC CỦA PROMPT MỚI

### Cấu Trúc (Giống TEMPLATE_PROMPT)

```
┌─────────────────────────────────────────────┐
│ ROLE DEFINITION                              │
│ - Who you are                               │
│ - Your mission                              │
│ - How you work                              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 4-PHASE FRAMEWORK                            │
│                                              │
│ Phase 1: ANALYSIS & DISCOVERY               │
│ - What you do                               │
│ - What you deliver                          │
│ - Red flags to watch                        │
│                                              │
│ Phase 2: PLANNING                            │
│ - Design output structure                   │
│ - Plan merge strategy                       │
│ - Define calculations                       │
│ - What you deliver                          │
│                                              │
│ Phase 3: EXECUTION                           │
│ - Execute the plan                          │
│ - Progress updates                          │
│ - Check-ins at decision points              │
│                                              │
│ Phase 4: VALIDATION                          │
│ - Verify everything                         │
│ - Quality checks                            │
│ - Final report                              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ HOW TO WORK WITH USER                        │
│ - Communication style                       │
│ - When uncertain                            │
│ - When issues found                         │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ VIETNAM SALARY RULES                         │
│ - Calculation formulas                      │
│ - Validation minimums                       │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ RESPONSE FORMAT STANDARDS                    │
│ - Structure guidelines                      │
│ - Number formats                            │
│ - What to show                              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ CRITICAL RULES                               │
│ - Non-negotiable principles                 │
└─────────────────────────────────────────────┘
```

### Workflow Agent Sẽ Tuân Theo

```
User: "Analyze these 2 Excel files"
       ↓
┌──────────────────────────────────────┐
│ PHASE 1: ANALYSIS                    │
│                                      │
│ Agent reads 2 JSON files             │
│ Agent identifies:                    │
│ - Structure (sheets, headers, data)  │
│ - Key fields (employee ID)           │
│ - Relationships (join key)           │
│ - Issues (missing, duplicates)       │
│                                      │
│ Output: 📊 Analysis Report           │
└──────────────────────────────────────┘
       ↓
Agent: "📊 ANALYSIS COMPLETE
        File 1: 28 employees, key=column D
        File 2: 28 salary records, key=column A
        Join strategy: Inner join on Mã NV
        Issues: 2 employees missing phụ cấp
        
        Ready for Phase 2: Planning?"
       ↓
User: "Yes, continue"
       ↓
┌──────────────────────────────────────┐
│ PHASE 2: PLANNING                    │
│                                      │
│ Agent designs:                       │
│ - Output structure (19 columns)      │
│ - Merge strategy (inner join)        │
│ - Calculations (7 formulas)          │
│ - Validation rules (5 rules)         │
│                                      │
│ Output: 📋 Execution Plan            │
└──────────────────────────────────────┘
       ↓
Agent: "📋 EXECUTION PLAN
        Output: 19 columns including:
        1. Employee info (ID, name, dept)
        2. Attendance (days, OT hours)
        3. Calculated fields (salary, tax, net)
        
        Calculations:
        1. Lương công = Base × (Days/26)
        2. OT = (Base/26/8) × Hours × 1.5
        [...]
        
        Proceed to Phase 3: Execution?"
       ↓
User: "Execute"
       ↓
┌──────────────────────────────────────┐
│ PHASE 3: EXECUTION                   │
│                                      │
│ Agent performs:                      │
│ - Parse JSON files                   │
│ - Extract data                       │
│ - Merge records                      │
│ - Calculate all fields               │
│ - Format output                      │
│                                      │
│ Output: Merged JSON structure        │
└──────────────────────────────────────┘
       ↓
Agent: "⚙️ EXECUTING...
        ✓ Parsed files: 28 + 28 records
        ✓ Merged: 28/28 matches
        ✓ Calculating salaries...
          • Employee 00039: 16.9M ✓
          • Employee 00040: 18.5M ✓
          [...]
        ✓ Execution complete
        
        Proceeding to Phase 4: Validation"
       ↓
┌──────────────────────────────────────┐
│ PHASE 4: VALIDATION                  │
│                                      │
│ Agent verifies:                      │
│ - Data integrity (100% complete)     │
│ - Calculation accuracy (spot checks) │
│ - Business rules (min wage, limits)  │
│ - Format correctness                 │
│                                      │
│ Output: ✅ Validation Report         │
└──────────────────────────────────────┘
       ↓
Agent: "✅ VALIDATION REPORT
        
        📊 DATA: 28/28 records ✓
        🧮 CALCS: Spot-checked 3 employees ✓
        💼 RULES: All comply with min wage ✓
        ⚠️ WARNINGS: 2 employees >40h OT
        
        🎯 VERDICT: APPROVED (98/100)
        Ready to convert to Excel"
       ↓
System converts to Excel
       ↓
User receives output file ✅
```

---

## 🔍 ĐIỂM KHÁC BIỆT SO VỚI PROMPT CŨ

### PROMPT CŨ (`SYSTEM_PROMPT`):
```python
"""
You are a helpful assistant...

TOOLS:
- Google Search
- Calculator
"""
```
- ❌ Quá chung chung
- ❌ Không có structure
- ❌ Không có domain knowledge
- ❌ Không có workflow

### PROMPT MỚI (`SALARY_AGENT_SYSTEM_PROMPT`):
```python
"""
Salary Data Processing Agent - Your AI Co-Processor for Payroll

Role: [Clear definition]

4-PHASE FRAMEWORK:
  Phase 1: ANALYSIS & DISCOVERY
  Phase 2: PLANNING
  Phase 3: EXECUTION
  Phase 4: VALIDATION

[Detailed guidelines for each phase]
[Vietnam salary calculation rules]
[Response format standards]
[Critical rules]
"""
```
- ✅ Specific role definition
- ✅ Structured 4-phase workflow
- ✅ Domain knowledge (Vietnam salary rules)
- ✅ Clear communication guidelines
- ✅ Response format examples
- ✅ Validation requirements

---

## 🧪 TESTING SCENARIOS

### Test 1: Role Understanding
```
User: "Bạn là ai?"

Expected Response:
"Tôi là Salary Data Processing Agent - AI Co-Processor chuyên xử lý 
dữ liệu lương. Tôi giúp bạn:
- Phân tích file Excel attendance và salary
- Merge dữ liệu thông minh
- Tính toán lương theo quy định Việt Nam
- Validate kết quả kỹ lưỡng

Tôi làm việc theo 4 phases: Analysis → Planning → Execution → Validation"
```

### Test 2: Phase Awareness
```
User: "Tôi có 2 file Excel cần xử lý"

Expected Response:
"📊 BẮT ĐẦU PHASE 1: ANALYSIS & DISCOVERY

Để tôi phân tích 2 files của bạn. Tôi sẽ:
1. Đọc cấu trúc của mỗi file
2. Xác định key fields và relationships
3. Phát hiện issues (nếu có)
4. Đưa ra Analysis Report

[Sau đó agent sẽ yêu cầu upload files hoặc đọc JSON]"
```

### Test 3: Calculation Explanation
```
User: "Tính lương cho employee có 22 công, lương cơ bản 20M"

Expected Response:
"🧮 TÍNH LƯƠNG CHI TIẾT

📋 INPUT:
- Lương cơ bản: 20,000,000 VNĐ
- Số công: 22/26 ngày
- Hệ số thử việc: 1.0 (giả sử chính thức)

💰 CALCULATION:
Lương theo công = 20,000,000 × 1.0 × (22/26)
                = 20,000,000 × 0.8462
                = 16,923,077 VNĐ

✓ Kết quả: 16,923,077 VNĐ
"
```

### Test 4: Issue Detection
```
Agent đang xử lý và phát hiện vấn đề:

"🚨 CRITICAL ISSUE DETECTED

Employee 00050 có trong file attendance nhưng KHÔNG có trong 
file salary info.

Cannot calculate salary without salary data.

OPTIONS:
A) Exclude employee 00050 from output
B) Include with NULL values (flag for manual entry)
C) Stop and request updated salary file

💡 RECOMMENDATION: B (include with warning flag)

Your decision?"
```

---

## 📝 CODE CHANGES SUMMARY

### Files Modified: 2

#### 1. `template/agent/prompts.py`
```diff
+ SALARY_AGENT_SYSTEM_PROMPT = """
+ Salary Data Processing Agent - Your AI Co-Processor for Payroll
+ [... 200+ lines of detailed prompt ...]
+ """
```

#### 2. `template/agent/agent.py`
```diff
- from template.agent.prompts import SYSTEM_PROMPT
+ from template.agent.prompts import SYSTEM_PROMPT, SALARY_AGENT_SYSTEM_PROMPT

  def __init__(self, 
-              prompt: str = SYSTEM_PROMPT,
+              prompt: str = SALARY_AGENT_SYSTEM_PROMPT,
```

### Impact:
- ✅ All new Agent instances will use SALARY_AGENT_SYSTEM_PROMPT by default
- ✅ Old SYSTEM_PROMPT still available if needed (backward compatible)
- ✅ Can override prompt when creating Agent: `Agent(prompt=SYSTEM_PROMPT)`
- ✅ No breaking changes to existing code structure

---

## 🚀 NEXT STEPS

### Immediate Testing:
1. ✅ Restart Docker services
   ```bash
   sudo docker compose down
   sudo docker compose up -d --build
   ```

2. ✅ Test Agent initialization
   ```bash
   # Check logs
   sudo docker compose logs -f salary-agent-service
   ```

3. ✅ Test Chat endpoint
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/chat \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": 1,
       "user_id": 100,
       "message": "Bạn là ai và bạn làm gì?"
     }'
   ```

### Expected Response:
Agent should respond with clear explanation of role and 4-phase framework

### Validation Checklist:
- [ ] Agent identifies itself correctly
- [ ] Agent mentions 4 phases when asked about workflow
- [ ] Agent explains salary calculations with formulas
- [ ] Agent uses proper Vietnamese and formatting (✓ ⚠️ 🚨 icons)
- [ ] Agent asks clarifying questions when needed
- [ ] Agent validates before giving answers

---

## 🎯 SUCCESS CRITERIA

Agent behavior should match these examples:

✅ **Good Response:**
```
🔍 PHÂN TÍCH FILE JSON

📁 FILE 1: ATTENDANCE DATA
────────────────────────────
✓ Tổng records: 28 employees
✓ Key field: Column D (Mã nhân viên)
✓ Data rows: 4-31
[detailed analysis...]

Ready for Phase 2: Planning?
```

❌ **Bad Response (Old behavior):**
```
I can help you with that. Let me process the files.
[generic response without structure]
```

---

**Status: CODE UPDATED ✅**  
**Ready for Testing: YES ✅**  
**Breaking Changes: NONE ✅**
