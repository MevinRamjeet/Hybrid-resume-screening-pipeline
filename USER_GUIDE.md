# 📖 User Guide: Resume Screening System

**A Simple Guide for HR Teams and Recruitment Staff**

---

## What Is This?

This is an **automatic screening tool** that reads job applications and tells you if candidates meet your requirements. Think of it as a smart assistant that:

- ✅ Checks if candidates are qualified
- ✅ Reads their experience and qualifications
- ✅ Gives you a clear PASS or FAIL decision
- ✅ Explains why each decision was made

**No technical knowledge needed!**

---

## Why Should I Use This?

### Before (Manual Screening):
- 😓 Spend hours reading every application
- 😕 Easy to miss important details when tired
- 😰 Hard to be consistent across hundreds of applications
- 📚 Mountains of paperwork to review

### After (Automatic Screening):
- ⚡ Screen hundreds of applications in minutes
- ✅ Never miss disqualifying factors
- 🎯 Every candidate judged by the same standards
- 😊 Focus your time on interviewing, not paperwork

---

## How Do I Use It?

### Step 1: Start the Program

1. Open your computer's command window
2. Type this command:
   ```
   python run_full_stack.py
   ```
3. Press Enter
4. Wait a few seconds for it to start

**You'll see a message saying the system is ready!**

### Step 2: Open the Screening Tool

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to this address: **http://127.0.0.1:7860**
3. You'll see the screening interface

### Step 3: Submit an Application

**Option A: Paste Application Data**
1. Click on the "JSON Input" tab
2. Click "📋 Load Sample" to see an example
3. Replace the sample with your candidate's information
4. Click "🚀 Evaluate"

**Option B: Upload a File**
1. Click on the "File Upload" tab
2. Click "Upload JSON File"
3. Select your candidate's application file
4. Click "🚀 Evaluate File"

### Step 4: Read the Results

Within seconds, you'll see:

**✅ PASSED** - Candidate meets all requirements
- You'll see which requirements they passed
- You'll see their overall score
- You'll see AI analysis of their experience

**❌ FAILED** - Candidate doesn't meet requirements
- You'll see exactly which requirements they failed
- You'll see clear explanations for each failure
- You can use this to provide feedback to candidates

---

## Understanding the Results

### Example: Passed Application

```
✅ APPLICATION PASSED

Overall Score: 92%

Summary:
- Structured Rules Passed: ✅
- Unstructured Fields Passed: ✅
- Failed Rules: 0/25

📋 Structured Evaluation Details
✅ Passed Rules: 25

🤖 AI Analysis
✅ PASSED
Reasoning: Candidate demonstrates strong relevant experience 
with 8 years in administrative roles. Qualifications align 
well with position requirements.
```

### Example: Failed Application

```
❌ APPLICATION FAILED

Overall Score: 68%

Summary:
- Structured Rules Passed: ❌
- Failed Rules: 3/25

📋 Structured Evaluation Details
❌ Failed Rules:
- age (range)
  - age=47 not in range 18-45.
  
- nationality (exact_match)
  - Expected Mauritian, got Zimbabwean.
  
- email (regex)
  - email does not match required format.

✅ Passed Rules: 22
```

---

## Common Questions

### Q: How long does it take to screen one application?
**A:** About 2-5 seconds per application.

### Q: Can I screen multiple applications at once?
**A:** Yes! You can upload a file with multiple applications or run them one after another.

### Q: What if some information is missing?
**A:** The system will flag missing required fields and mark the application as incomplete.

### Q: Can I trust the AI's judgment?
**A:** The AI helps evaluate written content, but final hiring decisions should always involve human review. Use it as a helpful assistant, not a replacement for human judgment.

### Q: What information does the system check?

The system automatically checks:

**Basic Information:**
- ✓ Age (must be within required range)
- ✓ Nationality (must match requirements)
- ✓ Contact details (valid email, phone numbers)
- ✓ National ID number format

**Education:**
- ✓ O-Level certificates (minimum 5 subjects with passes)
- ✓ A-Level certificates (if required)
- ✓ Degree qualifications (if required)
- ✓ Required subjects and grades

**Experience:**
- ✓ Years of experience (meets minimum)
- ✓ Relevant work history
- ✓ Job positions held

**Background:**
- ✓ No ongoing investigations
- ✓ No criminal convictions
- ✓ No disciplinary issues

**Written Content (AI Reviews):**
- ✓ Quality of experience descriptions
- ✓ Relevance of qualifications
- ✓ Completeness of responses

---

## What If Something Goes Wrong?

### Problem: "Cannot connect to server"
**Solution:**
1. Make sure you started the program (Step 1)
2. Check that you typed the web address correctly
3. Try closing and reopening your browser

### Problem: "Invalid JSON format"
**Solution:**
1. Click "📋 Load Sample" to see the correct format
2. Make sure all brackets { } and quotes " " match
3. Use the sample as a template

### Problem: "Application failed but I don't know why"
**Solution:**
1. Look at the "Failed Rules" section
2. Each failed rule has an explanation
3. Check that all required information is included

### Problem: Results look wrong
**Solution:**
1. Double-check the application data you entered
2. Make sure all fields are filled in correctly
3. Verify dates are in the format: YYYY-MM-DD (e.g., 1990-05-15)

---

## Tips for Best Results

### ✅ DO:
- Use the sample application as a template
- Fill in all required fields
- Use correct date formats (YYYY-MM-DD)
- Double-check spelling and formatting
- Keep a copy of the results for your records

### ❌ DON'T:
- Skip required fields
- Use incorrect date formats
- Mix up field names
- Forget to start the program first
- Rely solely on automated screening for final decisions

---

## Need Help?

### For Technical Issues:
Contact: **david.adediji@sil.mu**

### For Questions About Results:
- Review the detailed explanations in the results
- Check the "Evaluation Rules" tab to see all requirements
- Consult with your recruitment team lead

---

## Quick Reference Card

**To Start:**
```
python run_full_stack.py
```

**Web Address:**
```
http://127.0.0.1:7860
```

**To Stop:**
Press `Ctrl+C` in the command window

**Sample Application Format:**
```json
{
  "post_applied_for": "Administrative Officer",
  "surname": "Smith",
  "other_names": "John",
  "age": 30,
  "nationality": "Mauritian",
  "email": "john.smith@example.com",
  "phone_mobile": "52345678",
  "date_of_birth": "1993-05-15",
  "national_identity_no": "M1234567890123"
}
```

---

## Remember

This tool is designed to **help** you, not replace you. It:
- ✅ Saves you time on initial screening
- ✅ Ensures consistency and fairness
- ✅ Catches missing requirements
- ✅ Provides clear documentation

But **YOU** still make the final hiring decisions!

---

**Version 1.0.0** | Last Updated: November 2025
