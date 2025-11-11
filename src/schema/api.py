from pydantic import BaseModel
from typing import Dict, Any

class EvaluationResponse(BaseModel):
    overall_passed: bool
    overall_score: float
    structured_evaluation: Dict[str, Any]
    unstructured_evaluation: Dict[str, Any]
    summary: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


