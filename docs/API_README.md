# Hybrid Resume Screening Pipeline - FastAPI Server

This FastAPI server provides a web API interface for the hybrid resume screening pipeline, allowing you to evaluate job applications through HTTP endpoints.

## Setup and Installation

### 1. Install Dependencies

Make sure you have the required dependencies installed:

```bash
pip install fastapi uvicorn python-multipart
```

Or if using the project's dependency management:

```bash
pip install -e .
```

### 2. Environment Setup

Ensure your `.env` file is configured with the necessary API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
HF_TOKEN=your_huggingface_token_here
```

## Running the Server

### Option 1: Using the startup script
```bash
python run_server.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check

### Application Evaluation
- **POST** `/evaluate` - Evaluate using Pydantic model (PSCApplication)
- **POST** `/evaluate/json` - Evaluate using raw JSON data
- **POST** `/evaluate/file` - Evaluate by uploading a JSON file

### Configuration
- **GET** `/rules` - Get current evaluation rules
- **GET** `/schema` - Get PSCApplication schema

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)

## Example Usage

### 1. Using the Example Client

Run the provided example client to test all endpoints:

```bash
python example_client.py
```

### 2. Using curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Evaluate Application (JSON):**
```bash
curl -X POST "http://localhost:8000/evaluate/json" \
     -H "Content-Type: application/json" \
     -d '{
       "post_applied_for": "Software Developer",
       "surname": "Smith",
       "other_names": "John",
       "age": 30,
       "nationality": "Zimbabwean",
       "degree_qualifications": [
         {
           "level": "degree",
           "qualification_name": "Bachelor of Computer Science",
           "institution": "University of Zimbabwe"
         }
       ],
       "investigation_enquiry": false,
       "court_conviction": false
     }'
```

**Upload File:**
```bash
curl -X POST "http://localhost:8000/evaluate/file" \
     -F "file=@sample.json"
```

### 3. Using Python requests

```python
import requests

# Evaluate application
response = requests.post(
    "http://localhost:8000/evaluate/json",
    json={
        "post_applied_for": "Data Analyst",
        "surname": "Johnson",
        "other_names": "Alice",
        "age": 28,
        "nationality": "Zimbabwean",
        "investigation_enquiry": False,
        "court_conviction": False
    }
)

result = response.json()
print(f"Result: {'PASSED' if result['overall_passed'] else 'FAILED'}")
print(f"Score: {result['overall_score']:.2%}")
```

## Response Format

All evaluation endpoints return a JSON response with the following structure:

```json
{
  "overall_passed": true,
  "overall_score": 0.85,
  "structured_evaluation": {
    "passed": true,
    "details": [...]
  },
  "unstructured_evaluation": {
    "passed": true,
    "overall_reasoning": "...",
    "field_evaluations": [...]
  },
  "summary": {
    "structured_passed": true,
    "unstructured_passed": true,
    "structured_score": 0.9,
    "total_structured_rules": 10,
    "failed_structured_rules": 1,
    "unstructured_fields_evaluated": 3
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **422**: Validation Error
- **500**: Internal Server Error

Error responses include detailed error messages:

```json
{
  "detail": "Evaluation failed: Missing required field 'surname'"
}
```

## Development

### Adding New Endpoints

To add new endpoints, modify `src/api/app.py` and follow the existing patterns.

### Testing

Use the provided `example_client.py` to test all endpoints, or write your own tests using the FastAPI test client.

## Production Deployment

For production deployment:

1. Set `allow_origins` in CORS middleware to specific domains
2. Use a production WSGI server like Gunicorn
3. Set up proper logging and monitoring
4. Configure environment variables securely
5. Use HTTPS

Example production command:
```bash
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
