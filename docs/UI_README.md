# 🎯 Hybrid Resume Screening Pipeline - UI Documentation

A modern, user-friendly Gradio interface for the Hybrid Resume Screening Pipeline that combines structured rule validation with intelligent LLM analysis.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [API Configuration](#api-configuration)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🚀 Core Capabilities

- **Interactive Application Evaluation**: Submit job applications via JSON input or file upload
- **Real-time Results**: Get instant feedback with detailed evaluation reports
- **Dual Evaluation System**:
  - **Structured Rules**: Validates against predefined business rules
  - **Unstructured Analysis**: AI-powered evaluation of qualitative fields
- **Rules Explorer**: View and understand all evaluation criteria
- **Schema Reference**: Complete application data structure documentation
- **Sample Data**: Pre-loaded examples for quick testing

### 🎨 User Interface

- **Modern Design**: Clean, intuitive interface with gradient styling
- **Tabbed Navigation**: Organized workflow across multiple sections
- **Formatted Results**: Easy-to-read evaluation reports with icons and formatting
- **Raw JSON View**: Access complete API responses for debugging
- **Responsive Layout**: Works seamlessly on different screen sizes

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- FastAPI server running (see main README)

### Install Dependencies

```bash
# Install all dependencies including Gradio
poetry install

# Or update existing installation
poetry update
```

The UI requires the following additional packages:
- `gradio>=4.0.0`
- `httpx>=0.25.0`

## 🚀 Quick Start

### 1. Start the FastAPI Server

First, ensure the backend API is running:

```bash
python run_server.py
```

The API should be accessible at `http://localhost:8000`

### 2. Launch the UI

In a new terminal, start the Gradio interface:

```bash
python run_ui.py
```

The UI will be available at `http://127.0.0.1:7860`

### 3. Evaluate an Application

1. Navigate to the **"Evaluate Application"** tab
2. Click **"Load Sample"** to populate with example data
3. Click **"Evaluate"** to process the application
4. View results in both formatted and raw JSON formats

## 📖 Usage Guide

### Evaluate Application Tab

#### JSON Input Method

1. **Manual Entry**:
   - Type or paste JSON directly into the code editor
   - Ensure proper JSON syntax (use the sample as reference)
   - Click **"Evaluate"** to submit

2. **Load Sample**:
   - Click **"Load Sample"** to populate with a valid example
   - Modify fields as needed for testing
   - Click **"Evaluate"** to submit

3. **Clear Input**:
   - Click **"Clear"** to reset the input field

#### File Upload Method

1. Click the **"File Upload"** tab
2. Click **"Upload JSON File"** and select a `.json` file
3. Click **"Evaluate File"** to process

#### Understanding Results

**Formatted Results Tab**:
- ✅/❌ Overall pass/fail status
- Overall score percentage
- Summary statistics
- Detailed breakdown of:
  - Failed structured rules (with reasons)
  - Passed structured rules count
  - LLM analysis of unstructured fields

**Raw JSON Tab**:
- Complete API response
- Useful for debugging and integration
- Can be saved for record-keeping

### Evaluation Rules Tab

View the complete set of evaluation criteria:

1. Click the **"Evaluation Rules"** tab
2. Click **"Refresh Rules"** to load current configuration
3. Review:
   - **Structured Rules**: Field validations, ranges, patterns
   - **Unstructured Fields**: LLM-evaluated criteria

### Application Schema Tab

Reference the complete data structure:

1. Click the **"Application Schema"** tab
2. Click **"Load Schema"** to view the PSCApplication model
3. Use this to understand:
   - Required vs optional fields
   - Field types and formats
   - Nested object structures

### Settings Tab

Configure the API connection:

1. Click the **"Settings"** tab
2. Update the **API Base URL** if needed (default: `http://localhost:8000`)
3. Click **"Update URL"** to apply changes
4. Review the Quick Start Guide and Troubleshooting tips

## ⚙️ API Configuration

### Default Configuration

```python
API_BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
```

### Custom Configuration

If your FastAPI server runs on a different host/port:

1. Go to **Settings** tab
2. Enter new URL (e.g., `http://192.168.1.100:8080`)
3. Click **"Update URL"**

### Advanced Launch Options

```bash
# Custom port
python run_ui.py --port 7861

# Listen on all interfaces
python run_ui.py --host 0.0.0.0

# Create public shareable link
python run_ui.py --share

# Enable debug mode
python run_ui.py --debug

# Combine options
python run_ui.py --host 0.0.0.0 --port 8080 --share
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Error

**Symptom**: "API request failed" error message

**Solutions**:
- Verify FastAPI server is running: `python run_server.py`
- Check server URL in Settings tab
- Ensure no firewall blocking port 8000
- Test API directly: `curl http://localhost:8000/api/v1/rules`

#### 2. Invalid JSON Error

**Symptom**: "Invalid JSON" validation error

**Solutions**:
- Use the "Load Sample" button to get valid JSON
- Check for:
  - Missing commas between fields
  - Unclosed brackets or braces
  - Unquoted string values
  - Trailing commas
- Use a JSON validator online

#### 3. Module Import Error

**Symptom**: `ModuleNotFoundError: No module named 'gradio'`

**Solutions**:
```bash
# Reinstall dependencies
poetry install

# Or install gradio directly
pip install gradio>=4.0.0 httpx>=0.25.0
```

#### 4. Port Already in Use

**Symptom**: "Address already in use" error

**Solutions**:
```bash
# Use a different port
python run_ui.py --port 7861

# Or find and kill the process using port 7860
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:7860 | xargs kill -9
```

#### 5. Evaluation Takes Too Long

**Symptom**: Request times out or takes very long

**Solutions**:
- Check OpenAI API key configuration in `.env`
- Verify internet connection for LLM calls
- Review application data size (very large arrays may slow processing)
- Check FastAPI server logs for errors

### Debug Mode

Enable debug mode for detailed error messages:

```bash
python run_ui.py --debug
```

This will show:
- Detailed stack traces
- API request/response details
- Gradio internal logs

## 📝 Sample Application Structure

```json
{
  "post_applied_for": "Software Engineer",
  "ministry_department": "Ministry of Technology",
  "date_of_advertisement": "2024-01-15",
  "national_identity_no": "M1234567890123",
  "surname": "Ramjeet",
  "other_names": "Mevin Kumar",
  "residential_address": "123 Royal Road, Port Louis",
  "date_of_birth": "1995-06-15",
  "age": 29,
  "nationality": "Mauritian",
  "phone_mobile": "52345678",
  "email": "mevin.ramjeet@example.com",
  "ordinary_level_exams": [...],
  "degree_qualifications": [...],
  "other_employment": [...],
  "investigation_enquiry": false,
  "court_conviction": false,
  "resigned_retired_dismissed": false
}
```

## 🎨 UI Architecture

```
src/ui/
├── __init__.py          # Package initialization
├── app.py               # Main Gradio application
├── components.py        # UI component definitions
└── utils.py             # Utility functions

run_ui.py                # Launcher script
```

### Key Components

- **app.py**: Main application setup, theme configuration, and launch logic
- **components.py**: Individual UI tabs and interactive elements
- **utils.py**: API communication, data formatting, and validation

## 🔗 Integration

### Embedding in Other Applications

```python
from src.ui import create_app

# Create the Gradio app
app = create_app()

# Mount in FastAPI (optional)
from fastapi import FastAPI
fastapi_app = FastAPI()
fastapi_app = gr.mount_gradio_app(fastapi_app, app, path="/ui")
```

### Programmatic Usage

```python
from src.ui.utils import call_api_endpoint, format_evaluation_results

# Evaluate application
results = await call_api_endpoint(
    endpoint="/api/v1/evaluate/json",
    data=application_data,
    base_url="http://localhost:8000"
)

# Format results
formatted = format_evaluation_results(results)
print(formatted)
```

## 📊 Performance Tips

1. **Batch Processing**: For multiple applications, use the API directly
2. **Caching**: Results are not cached; re-evaluation will call the API again
3. **Network**: Local deployment (localhost) is fastest
4. **File Size**: Keep JSON files under 1MB for optimal performance

## 🛡️ Security Considerations

- **Local Deployment**: Default configuration is localhost-only
- **Public Sharing**: Use `--share` flag cautiously; creates public URL
- **API Keys**: Never include API keys in application JSON
- **Data Privacy**: Application data is sent to the FastAPI server and potentially to OpenAI

## 📚 Additional Resources

- [Main API Documentation](API_README.md)
- [Project README](../README.md)
- [Gradio Documentation](https://gradio.app/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## 🤝 Contributing

To enhance the UI:

1. Modify components in `src/ui/components.py`
2. Update utilities in `src/ui/utils.py`
3. Adjust styling in `src/ui/app.py` (custom_css)
4. Test thoroughly with `python run_ui.py --debug`

## 📄 License

Same as the main project.

---

**Need Help?** Check the troubleshooting section or review the FastAPI server logs for detailed error messages.
