import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
from src.config.system import cfg
from src.schema.api import EvaluationResponse
from src.core.screening import hybrid_evaluate_application, get_structured_rules, get_unstructured_fields
from src.constants import rules
from src.utils.logger import configured_logger
from src.schema.extraction import PSCApplication

router = APIRouter(prefix=f"/api/{cfg.api_version}")


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_application(application: PSCApplication):
    """
    Evaluate a job application using the hybrid screening pipeline.
    
    Args:
        application: PSCApplication object containing all application data
        
    Returns:
        EvaluationResponse with detailed evaluation results
    """
    try:
        configured_logger.info(f"Starting evaluation for application: {application.surname} {application.other_names}")

        # Convert Pydantic model to dictionary
        application_data = application.model_dump(exclude_none=True)

        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

        # Create response
        response = EvaluationResponse(
            overall_passed=results["overall_passed"],
            overall_score=results["overall_score"],
            structured_evaluation=results["structured_evaluation"],
            unstructured_evaluation=results["unstructured_evaluation"],
            summary=results["summary"],
            timestamp=datetime.now().isoformat()
        )

        configured_logger.info(f"Evaluation completed. Result: {'PASSED' if results['overall_passed'] else 'FAILED'}")
        return response

    except Exception as e:
        configured_logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate/json")
async def evaluate_application_json(application_data: Dict[str, Any]):
    """
    Evaluate a job application using raw JSON data.
    
    Args:
        application_data: Dictionary containing application data
        
    Returns:
        Evaluation results as JSON
    """
    try:
        configured_logger.info("Starting evaluation for JSON application data")

        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

        # Add timestamp
        results["timestamp"] = datetime.now().isoformat()

        configured_logger.info(f"Evaluation completed. Result: {'PASSED' if results['overall_passed'] else 'FAILED'}")
        return JSONResponse(content=results)

    except Exception as e:
        configured_logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate/file")
async def evaluate_application_file(file: UploadFile = File(...)):
    """
    Evaluate a job application from an uploaded JSON file.
    
    Args:
        file: JSON file containing application data
        
    Returns:
        Evaluation results as JSON
    """
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON file")

        # Read and parse JSON file
        content = await file.read()
        try:
            application_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

        configured_logger.info(f"Starting evaluation for uploaded file: {file.filename}")

        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

        # Add metadata
        results["timestamp"] = datetime.now().isoformat()
        results["source_file"] = file.filename

        configured_logger.info(
            f"Evaluation completed for {file.filename}. Result: {'PASSED' if results['overall_passed'] else 'FAILED'}")
        return JSONResponse(content=results)

    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error during file evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"File evaluation failed: {str(e)}")


@router.get("/rules")
async def get_evaluation_rules():
    """
    Get the current evaluation rules configuration.
    
    Returns:
        Dictionary containing structured and unstructured rules
    """
    try:
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        return {
            "structured_rules": structured_rules,
            "unstructured_fields": unstructured_fields,
            "total_rules": len(rules),
            "structured_count": len(structured_rules),
            "unstructured_count": len(unstructured_fields)
        }
    except Exception as e:
        configured_logger.error(f"Error retrieving rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rules: {str(e)}")


@router.get("/schema")
async def get_application_schema():
    """
    Get the PSCApplication schema for reference.
    
    Returns:
        JSON schema for PSCApplication
    """
    try:
        return PSCApplication.model_json_schema()
    except Exception as e:
        configured_logger.error(f"Error retrieving schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve schema: {str(e)}")
