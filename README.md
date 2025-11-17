# 🎯 Hybrid Resume Screening Pipeline

A sophisticated AI-powered system that combines structured rule validation with intelligent LLM analysis for comprehensive job application screening.

## 🚀 Quick Start

### Option 1: Full Stack (Recommended)
Launch both API and UI together:
```bash
python run_full_stack.py
```
- **API**: http://localhost:8000
- **UI**: http://127.0.0.1:7860

### Option 2: API Only
```bash
python run_server.py
```

### Option 3: UI Only
```bash
python run_ui.py
```

## 📚 Documentation

- **[API Documentation](API_README.md)** - Complete API reference and usage
- **[UI Documentation](UI_README.md)** - Gradio interface guide and troubleshooting

## ✨ Features

- **🎨 Modern Web UI**: Interactive Gradio interface for easy application evaluation
- **📋 Structured Validation**: Rule-based screening with 30+ validation rules
- **🤖 AI Analysis**: LLM-powered evaluation of qualitative fields
- **📊 Detailed Reports**: Comprehensive pass/fail analysis with reasoning
- **🔌 REST API**: Full-featured FastAPI backend
- **📁 Multiple Input Methods**: JSON, file upload, or direct API calls

## 🛠️ Installation

```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## 📖 Rules Reference

| Type          | Description                         | Example                                                      |
| ------------- | ----------------------------------- | ------------------------------------------------------------ |
| `exact_match` | Field must match value exactly      | `{"type": "exact_match", "value": "Administrative Officer"}` |
| `one_of`      | Field must be one of allowed values | `["Mauritian", "Permanent Resident"]`                        |
| `not_in`      | Value must not appear in list       | `["Suspended", "Dismissed"]`                                 |
| `regex`       | Validate using regex pattern        | Email, phone number                                          |
| `range`       | Numeric range constraint            | `{"min": 25, "max": 40}`                                     |
| `min` / `max` | Minimum or maximum only             | `{"min": 2}` years experience                                |
| `boolean`     | Must be true or false               | `{"type": "boolean", "value": false}`                        |
| `exists`      | Field must be present/non-null      | `{"type": "exists"}`                                         |
| `not_exists`  | Field must be null/missing          | For fields like `court_conviction`                           |


