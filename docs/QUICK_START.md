# ⚡ Quick Start Guide

**Get screening in 3 minutes!**

---

## 🚀 Start the System

Open your command window and type:

```bash
python run_full_stack.py
```

Wait for this message:
```
✓ API running on http://localhost:8000
✓ UI running on http://127.0.0.1:7860
```

---

## 🌐 Open the Screening Tool

Open your web browser and go to:

```
http://127.0.0.1:7860
```

---

## 📝 Screen an Application

### Method 1: Use Sample Data (Easiest!)

1. Click **"📋 Load Sample"**
2. Click **"🚀 Evaluate"**
3. See the results!

### Method 2: Enter Your Own Data

1. Replace the sample with your candidate's information
2. Click **"🚀 Evaluate"**
3. Review the PASS/FAIL decision

### Method 3: Upload a File

1. Click **"File Upload"** tab
2. Select your JSON file
3. Click **"🚀 Evaluate File"**

---

## ✅ Read the Results

### Passed Application
```
✅ APPLICATION PASSED
Overall Score: 92%
```
→ Candidate meets all requirements!

### Failed Application
```
❌ APPLICATION FAILED
Overall Score: 68%

Failed Rules:
- age: 47 not in range 18-45
- nationality: Expected Mauritian, got Zimbabwean
```
→ Candidate doesn't meet requirements (see reasons)

---

## 🛑 Stop the System

In the command window, press:
```
Ctrl + C
```

---

## 🆘 Having Problems?

| Problem | Solution |
|---------|----------|
| Can't connect | Make sure you ran `python run_full_stack.py` |
| Invalid JSON | Click "Load Sample" to see correct format |
| Wrong results | Check your data matches the sample format |

---

## 📞 Need Help?

**Read the full guide:** [USER_GUIDE.md](USER_GUIDE.md)

**Contact:** david.adediji@sil.mu

---

## 📋 Sample Application Format

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
  "national_identity_no": "M1234567890123",
  "investigation_enquiry": false,
  "court_conviction": false
}
```

**Copy this format and fill in your candidate's details!**

---

## ⏱️ That's It!

You're now ready to screen applications automatically.

**Remember:**
- ✅ Each screening takes 2-5 seconds
- ✅ Results show exactly why candidates passed or failed
- ✅ You can screen hundreds of applications quickly
- ✅ Final hiring decisions are still yours to make!

---

**Happy Screening! 🎯**
