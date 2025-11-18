# 🎯 Hybrid Resume Screening Pipeline

An intelligent screening assistant that automatically evaluates job applications, saving time and ensuring consistent, fair candidate assessment for recruitment teams.

> **👥 New to this system?** Check out the **[User Guide](USER_GUIDE.md)** - a simple, step-by-step guide for non-technical users!

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [Why Use This System](#-why-use-this-system)
- [Key Capabilities](#-key-capabilities)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
- [Understanding Results](#-understanding-results)
- [Customization](#-customization)
- [Additional Documentation](#-additional-documentation)

## 🔍 What It Does

This system **automatically screens job applications** to help recruitment teams quickly identify qualified candidates. It works like a tireless assistant that:

1. **Checks Eligibility Requirements** - Verifies if candidates meet basic criteria (age, nationality, education, experience)
2. **Reviews Qualitative Information** - Reads and evaluates written responses, experience descriptions, and motivations
3. **Provides Clear Decisions** - Gives each application a PASS or FAIL recommendation with detailed explanations

**Who It's For**: Recruitment teams in public sector organizations (like the Mauritian Public Service Commission) who need to process large volumes of applications fairly and consistently.

**What Problem It Solves**: Manual screening is time-consuming, inconsistent, and prone to human error. This system ensures every application is evaluated against the same standards in seconds, not hours.

## 💡 Why Use This System

### **Save Time**
Screen hundreds of applications in minutes instead of days. Each application is evaluated in seconds with comprehensive results.

### **Ensure Fairness**
Every candidate is judged by the same criteria. No unconscious bias, no fatigue-related errors, no inconsistent standards.

### **Maintain Quality**
Never miss important disqualifying factors. The system checks every requirement, every time, with 100% accuracy.

### **Provide Transparency**
Every decision comes with clear reasoning. Candidates and reviewers can see exactly why an application passed or failed.

### **Reduce Workload**
Focus your team's time on interviewing qualified candidates instead of manually reviewing paperwork.

## ✨ Key Capabilities

### 📝 **Automatic Eligibility Checking**
The system verifies:
- **Age and nationality requirements**
- **Valid contact information** (email, phone numbers)
- **Educational qualifications** (O-Level, A-Level, Degree certificates)
- **Work experience** (years, relevance, positions held)
- **Background clearance** (no investigations, convictions, or disciplinary issues)

### 🤖 **Intelligent Content Review**
Beyond checking boxes, the system reads and understands:
- **Experience descriptions** - Are they relevant and substantial?
- **Motivation statements** - Do they demonstrate genuine interest?
- **Additional qualifications** - What extra value does the candidate bring?
- **Written responses** - Are they complete and appropriate?

### 📊 **Clear, Actionable Results**
For each application, you receive:
- **Overall Decision**: PASS or FAIL
- **Detailed Breakdown**: Which requirements were met or missed
- **Explanations**: Why each decision was made
- **Score Summary**: Quantitative assessment for ranking candidates

### 🖥️ **Easy to Use**
- **Web Interface**: Simple form - paste application data, click evaluate, see results
- **Batch Processing**: Upload multiple applications at once
- **API Access**: Integrate with your existing recruitment systems
- **No Training Required**: Intuitive design anyone can use

## 🔄 How It Works

The system evaluates applications in three simple steps:

### **Step 1: Submit Application**
- Enter candidate information through the web interface, or
- Upload a JSON file with application data, or
- Send data through the API from your recruitment system

### **Step 2: Automatic Evaluation**
The system performs two types of checks:
- **Hard Requirements**: Verifies age, nationality, education, experience against your criteria
- **Soft Assessment**: AI reads and evaluates written content for quality and relevance

### **Step 3: Get Results**
Within seconds, receive:
- ✅ **PASS** or ❌ **FAIL** decision
- Detailed report showing what passed and what failed
- Explanations for each evaluation point
- Overall score for ranking candidates

## 🚀 Quick Start

### What You Need
- Python installed on your computer (version 3.10 or higher)
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Getting Started (3 Simple Steps)

**1. Install the system:**
```bash
poetry install
```

**2. Add your OpenAI API key:**
Create a file called `.env` and add:
```
OPENAI_API_KEY=your_key_here
```

**3. Launch the application:**
```bash
python run_full_stack.py
```

That's it! Open your browser to:
- **Web Interface**: http://127.0.0.1:7860 (for screening applications)
- **API Documentation**: http://localhost:8000/docs (for developers)

## 🛠️ Installation

### Detailed Setup Instructions

**1. Get the code:**
```bash
git clone <repository-url>
cd Hybrid-resume-screening-pipeline
```

**2. Install dependencies:**
```bash
poetry install
```
*Don't have Poetry? Install it first: `pip install poetry`*

**3. Set up your API key:**
```bash
cp .env.example .env
```
Then edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_key_here
```

**4. Test it works:**
```bash
python run_full_stack.py
```
Visit http://127.0.0.1:7860 - you should see the screening interface!

## 📖 How to Use

### Option 1: Web Interface (Easiest)

**For HR teams and non-technical users**

1. **Start the application:**
   ```bash
   python run_full_stack.py
   ```

2. **Open your browser** to http://127.0.0.1:7860

3. **Enter application data:**
   - Paste JSON data directly into the text box, OR
   - Upload a JSON file with candidate information

4. **Click "Evaluate Application"**

5. **Review the results:**
   - See if the candidate PASSED or FAILED
   - Read detailed explanations for each criterion
   - Check the overall score

### Option 2: API Integration (For Developers)

**Integrate with your existing recruitment software**

Send application data to the API and get instant results:

```bash
curl -X POST "http://localhost:8000/evaluate/json" \
  -H "Content-Type: application/json" \
  -d '{
    "post_applied_for": "Administrative Officer",
    "surname": "Smith",
    "other_names": "John",
    "age": 30,
    "nationality": "Mauritian",
    "email": "john.smith@example.com",
    "phone_mobile": "52345678"
  }'
```

**API Documentation:** Visit http://localhost:8000/docs for complete API reference

## 📊 Understanding Results

### What You'll See

Every evaluation provides:

**1. Overall Decision**
```
✅ PASSED - Candidate meets all requirements
❌ FAILED - Candidate does not meet one or more requirements
```

**2. Detailed Breakdown**
- **Eligibility Checks**: Age ✅, Nationality ✅, Education ✅
- **Qualifications**: O-Level ✅, A-Level ✅, Degree ✅
- **Experience**: Years ✅, Relevance ✅
- **Background**: No investigations ✅, No convictions ✅

**3. AI Assessment**
- **Experience Quality**: "Candidate demonstrates 5+ years of relevant experience in..."
- **Motivation**: "Strong alignment with role requirements..."
- **Additional Qualifications**: "Brings valuable skills in..."

**4. Score Summary**
- Overall Score: 85%
- Structured Rules Passed: 28/30
- Qualitative Assessment: PASS

### Example Result

```json
{
  "overall_passed": true,
  "overall_score": 0.85,
  "summary": {
    "structured_passed": true,
    "unstructured_passed": true,
    "failed_rules": ["Age slightly above preferred range"]
  }
}
```

## ⚙️ Customization

### Changing Screening Criteria

You can customize what the system checks for by editing the rules file:

**File to edit:** `src/constants.py`

**Common customizations:**

**1. Change age requirements:**
```python
{"field": "age", "type": "range", "min": 21, "max": 50}
```

**2. Add nationality options:**
```python
{"field": "nationality", "type": "one_of", "values": ["Mauritian", "Permanent Resident"]}
```

**3. Adjust education requirements:**
```python
{"field": "degree_qualifications", "type": "array_length", "min_length": 1}
```

**4. Modify experience requirements:**
```python
{"field": "work_experience_years", "type": "min", "value": 3}
```

### What Can Be Checked?

The system can validate:
- **Exact matches**: "Must be exactly this value"
- **Ranges**: "Must be between X and Y"
- **Lists**: "Must be one of these options"
- **Patterns**: Email format, phone format, ID numbers
- **Existence**: "This field must be filled in"
- **Combinations**: "Must meet A AND B" or "Must meet A OR B"

### Need Help Customizing?

See the **[Technical Documentation](API_README.md)** for detailed rule syntax and examples.

## 📚 Additional Documentation

**For Everyone:**
- **[👥 User Guide](USER_GUIDE.md)** - **START HERE!** Simple guide for non-technical users

**For HR Teams:**
- **[UI Guide](UI_README.md)** - Detailed web interface instructions

**For Developers:**
- **[API Reference](API_README.md)** - Complete API documentation for integration
- **[Technical Details](GRADIO_UI_SUMMARY.md)** - Implementation notes

## ❓ Common Questions

### How long does screening take?
Each application is evaluated in **2-5 seconds**.

### Can I screen multiple applications at once?
Yes! Upload a file with multiple applications or use the API for batch processing.

### What if a candidate doesn't have all the information?
The system will flag missing required fields and mark the application as incomplete.

### Can I change what gets checked?
Yes! You can customize all screening criteria by editing the rules file (see Customization section).

### Is the AI evaluation accurate?
The AI provides assessments based on the content quality. Final hiring decisions should always involve human review.

### What happens to the application data?
Data is processed in real-time and not stored permanently. Only evaluation results are returned.

### Do I need technical skills to use this?
No! The web interface is designed for HR professionals with no technical background. Just paste data and click evaluate.

## 🆘 Troubleshooting

### "API key not configured" error
- Make sure you created a `.env` file
- Check that your OpenAI API key is correct
- Restart the application after adding the key

### Web interface won't load
- Check that port 7860 is not being used by another application
- Try running `python run_ui.py` separately
- Check the console for error messages

### "Application failed" but not sure why
- Look at the detailed breakdown in the results
- Each failed criterion shows an explanation
- Check that all required fields are present in the application data

### Need more help?
Contact: david.adediji@sil.mu

## 📝 License & Credits

**License:** Proprietary software for internal use

**Developed by:** David Adediji (david.adediji@sil.mu)

**Powered by:**
- OpenAI GPT for intelligent content analysis
- FastAPI for robust API infrastructure
- Gradio for user-friendly web interface


