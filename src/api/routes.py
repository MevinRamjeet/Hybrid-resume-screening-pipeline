import json
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException, UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
from src.config.system import cfg
from src.schema.api import EvaluationResponse
from src.core.screening import hybrid_evaluate_application, get_structured_rules, get_unstructured_fields
from src.core.rules_manager import get_rules_manager, load_rules_from_file
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

        # Load rules from file
        rules = load_rules_from_file()
        
        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = await hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

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

        # Load rules from file
        rules = load_rules_from_file()
        
        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = await hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

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

        # Load rules from file
        rules = load_rules_from_file()
        
        # Separate structured and unstructured rules
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)

        # Run hybrid evaluation
        results = await hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)

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
        configured_logger.info("Fetching evaluation rules")
        
        # Load rules from file, fallback to constants if file is empty/invalid
        try:
            rules = load_rules_from_file()
            configured_logger.info(f"Loaded {len(rules) if rules else 0} rules from file")
            
            if not rules:
                configured_logger.warning("Rules file is empty, using default rules from constants")
                from src.config.constants import rules as default_rules
                rules = default_rules
        except Exception as load_error:
            configured_logger.error(f"Error loading rules from file: {load_error}, using default rules")
            from src.config.constants import rules as default_rules
            rules = default_rules
        
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)
        
        configured_logger.info(f"Processed {len(structured_rules)} structured rules and {len(unstructured_fields)} unstructured fields")

        # Ensure all data is JSON serializable by converting to dict/list
        response_data = {
            "rules": rules,  # Include full rules for rules_editor.py
            "structured_rules": structured_rules,
            "unstructured_fields": unstructured_fields,
            "total_rules": len(rules),
            "structured_count": len(structured_rules),
            "unstructured_count": len(unstructured_fields)
        }
        
        # Use json.dumps to ensure proper serialization, then return as JSONResponse
        return JSONResponse(content=json.loads(json.dumps(response_data, default=str)))
        
    except Exception as e:
        configured_logger.error(f"Error retrieving rules: {e}", exc_info=True)
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


# ==================== RULES MANAGEMENT ENDPOINTS ====================

@router.put("/rules")
async def update_all_rules(rules: List[Dict[str, Any]]):
    """
    Update all evaluation rules.
    
    Args:
        rules: List of rule dictionaries
        
    Returns:
        Success message with updated rule count
    """
    try:
        rules_manager = get_rules_manager()
        
        # Validate all rules
        for i, rule in enumerate(rules):
            is_valid, error_msg = rules_manager.validate_rule(rule)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid rule at index {i}: {error_msg}")
        
        # Save rules
        success = rules_manager.save_rules(rules, backup=True)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save rules")
        
        configured_logger.info(f"Updated all rules. Total count: {len(rules)}")
        return {
            "message": "Rules updated successfully",
            "total_rules": len(rules),
            "backup_created": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error updating rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update rules: {str(e)}")


@router.post("/rules")
async def add_rule(rule: Dict[str, Any]):
    """
    Add a new evaluation rule.
    
    Args:
        rule: Rule dictionary to add
        
    Returns:
        Success message with new rule index
    """
    try:
        rules_manager = get_rules_manager()
        
        # Validate rule
        is_valid, error_msg = rules_manager.validate_rule(rule)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid rule: {error_msg}")
        
        # Add rule
        success = rules_manager.add_rule(rule)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add rule")
        
        rules = rules_manager.load_rules()
        new_index = len(rules) - 1
        
        configured_logger.info(f"Added new rule at index {new_index}")
        return {
            "message": "Rule added successfully",
            "index": new_index,
            "total_rules": len(rules)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error adding rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add rule: {str(e)}")


@router.put("/rules/{index}")
async def update_rule(index: int, rule: Dict[str, Any]):
    """
    Update a specific rule by index.
    
    Args:
        index: Index of the rule to update
        rule: New rule dictionary
        
    Returns:
        Success message
    """
    try:
        rules_manager = get_rules_manager()
        
        # Validate rule
        is_valid, error_msg = rules_manager.validate_rule(rule)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid rule: {error_msg}")
        
        # Update rule
        success = rules_manager.update_rule(index, rule)
        if not success:
            raise HTTPException(status_code=404, detail=f"Rule at index {index} not found")
        
        configured_logger.info(f"Updated rule at index {index}")
        return {
            "message": "Rule updated successfully",
            "index": index
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error updating rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")


@router.delete("/rules/{index}")
async def delete_rule(index: int):
    """
    Delete a specific rule by index.
    
    Args:
        index: Index of the rule to delete
        
    Returns:
        Success message
    """
    try:
        rules_manager = get_rules_manager()
        
        # Delete rule
        success = rules_manager.delete_rule(index)
        if not success:
            raise HTTPException(status_code=404, detail=f"Rule at index {index} not found")
        
        rules = rules_manager.load_rules()
        configured_logger.info(f"Deleted rule at index {index}")
        return {
            "message": "Rule deleted successfully",
            "total_rules": len(rules)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error deleting rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")


@router.get("/rules/{index}")
async def get_rule(index: int):
    """
    Get a specific rule by index.
    
    Args:
        index: Index of the rule to retrieve
        
    Returns:
        Rule dictionary
    """
    try:
        rules_manager = get_rules_manager()
        rule = rules_manager.get_rule(index)
        
        if rule is None:
            raise HTTPException(status_code=404, detail=f"Rule at index {index} not found")
        
        return {
            "index": index,
            "rule": rule
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error retrieving rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rule: {str(e)}")


@router.post("/rules/reset")
async def reset_rules_to_defaults():
    """
    Reset all rules to default values.
    
    Returns:
        Success message
    """
    try:
        rules_manager = get_rules_manager()
        success = rules_manager.reset_to_defaults()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset rules")
        
        rules = rules_manager.load_rules()
        configured_logger.info("Reset rules to defaults")
        return {
            "message": "Rules reset to defaults successfully",
            "total_rules": len(rules),
            "backup_created": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        configured_logger.error(f"Error resetting rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset rules: {str(e)}")
