"""
Utility functions for the Gradio UI interface.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
import httpx


async def call_api_endpoint(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    base_url: str = "http://localhost:8002",
    method: str = "POST"
) -> Dict[str, Any]:
    """
    Call an API endpoint and return the response.
    
    Args:
        endpoint: API endpoint path (e.g., "/api/v1/evaluate")
        data: JSON data to send
        files: Files to upload
        base_url: Base URL of the API server
        method: HTTP method (GET, POST, PUT, DELETE)
        
    Returns:
        Dictionary containing the API response
    """
    url = f"{base_url}{endpoint}"
    method = method.upper()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                if files:
                    response = await client.post(url, files=files)
                elif data:
                    response = await client.post(url, json=data)
                else:
                    response = await client.post(url)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                return {
                    "error": True,
                    "message": f"Unsupported HTTP method: {method}"
                }
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "error": True,
                "message": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Unexpected error: {str(e)}"
            }


def format_evaluation_results(results: Dict[str, Any]) -> str:
    """
    Format evaluation results for display in the UI.
    
    Args:
        results: Evaluation results dictionary
        
    Returns:
        Formatted string for display
    """
    if results.get("error"):
        return f"❌ **Error**: {results.get('message', 'Unknown error')}"
    
    output = []
    
    # Overall result
    overall_passed = results.get("overall_passed", False)
    overall_score = results.get("overall_score", 0)
    
    if overall_passed:
        output.append("# ✅ **APPLICATION PASSED**\n")
    else:
        output.append("# ❌ **APPLICATION FAILED**\n")
    
    output.append(f"**Overall Score**: {overall_score:.2%}\n")
    output.append(f"**Timestamp**: {results.get('timestamp', 'N/A')}\n")
    
    # Summary
    summary = results.get("summary", {})
    output.append("\n## 📊 Summary\n")
    output.append(f"- **Structured Rules Passed**: {summary.get('structured_passed', 'N/A')}")
    output.append(f"- **Structured Score**: {summary.get('structured_score', 0):.2%}")
    output.append(f"- **Failed Structured Rules**: {summary.get('failed_structured_rules', 0)}/{summary.get('total_structured_rules', 0)}")
    output.append(f"- **Unstructured Fields Passed**: {summary.get('unstructured_passed', 'N/A')}")
    output.append(f"- **Unstructured Fields Evaluated**: {summary.get('unstructured_fields_evaluated', 0)}\n")
    
    # Structured evaluation details
    structured_eval = results.get("structured_evaluation", {})
    if structured_eval:
        output.append("\n## 📋 Structured Evaluation Details\n")
        details = structured_eval.get("details", [])
        
        # Failed rules first
        failed_rules = [d for d in details if not d.get("passed", True)]
        if failed_rules:
            output.append("\n### ❌ Failed Rules:\n")
            for detail in failed_rules:
                # Extract information from the rule object
                rule = detail.get("rule", {})
                field = rule.get("field")
                rule_type = rule.get("type", "N/A")
                reason = detail.get("reason", "N/A")
                
                # Format the rule display based on whether it has a field
                if field:
                    output.append(f"- **{field}** ({rule_type})")
                else:
                    # For logical operators (AND/OR) or rules without fields
                    output.append(f"- **{rule_type.upper()} Rule**")
                
                output.append(f"  - {reason}\n")
        
        # Passed rules (collapsed)
        passed_rules = [d for d in details if d.get("passed", False)]
        if passed_rules:
            output.append(f"\n### ✅ Passed Rules: {len(passed_rules)}\n")
    
    # Unstructured evaluation details
    unstructured_eval = results.get("unstructured_evaluation", {})
    if unstructured_eval:
        output.append("\n## 🤖 Unstructured Evaluation (LLM Analysis)\n")
        output.append(f"**Overall Assessment**: {'✅ PASSED' if unstructured_eval.get('passed') else '❌ FAILED'}\n")
        output.append(f"**Reasoning**: {unstructured_eval.get('overall_reasoning', 'N/A')}\n")
        
        field_evals = unstructured_eval.get("field_evaluations", [])
        if field_evals:
            output.append("\n### Field-by-Field Analysis:\n")
            for field_eval in field_evals:
                field_name = field_eval.get("field", "Unknown")
                assessment = field_eval.get("assessment", "N/A")
                reasoning = field_eval.get("reasoning", "N/A")
                
                icon = "✅" if assessment == "PASS" else "❌"
                output.append(f"\n**{icon} {field_name}**")
                output.append(f"- Assessment: {assessment}")
                output.append(f"- Reasoning: {reasoning}\n")
    
    return "\n".join(output)


def format_rules_display(rules_data: Dict[str, Any]) -> str:
    """
    Format rules configuration for display.

    Args:
        rules_data: Rules configuration dictionary

    Returns:
        Formatted string for display
    """
    if rules_data.get("error"):
        return f"❌ **Error**: {rules_data.get('message', 'Unknown error')}"

    output = []
    output.append("# 📜 Evaluation Rules Configuration\n")
    output.append(f"**Total Rules**: {rules_data.get('total_rules', 0)}")
    output.append(f"**Structured Rules**: {rules_data.get('structured_count', 0)}")
    output.append(f"**Unstructured Fields**: {rules_data.get('unstructured_count', 0)}\n")

    # Structured rules
    structured_rules = rules_data.get("structured_rules", [])
    if structured_rules:
        output.append("\n## 📋 Structured Rules\n")
        for i, rule in enumerate(structured_rules, 1):
            rule_type = rule.get("type", "N/A")
            field = rule.get("field", "N/A")
            output.append(f"{i}. **{field}** - Type: `{rule_type}`")

            # Add relevant details based on rule type
            if "value" in rule:
                output.append(f"   - Value: {rule['value']}")
            if "min" in rule or "max" in rule:
                output.append(f"   - Range: {rule.get('min', 'N/A')} to {rule.get('max', 'N/A')}")
            if "pattern" in rule:
                output.append(f"   - Pattern: `{rule['pattern']}`")
            output.append("")

    # Unstructured fields
    unstructured_fields = rules_data.get("unstructured_fields", [])
    if unstructured_fields:
        output.append("\n## 🤖 Unstructured Fields (LLM Evaluated)\n")
        for i, field in enumerate(unstructured_fields, 1):
            field_name = field.get("field", "N/A")
            description = field.get("description", "N/A")
            criteria = field.get("evaluation_criteria", "N/A")

            output.append(f"{i}. **{field_name}**")
            output.append(f"   - Description: {description}")
            output.append(f"   - Criteria: {criteria}")
            output.append("")

    return "\n".join(output)


def validate_json_input(json_str: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate and parse JSON input.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        Tuple of (is_valid, parsed_data, error_message)
    """
    if not json_str or not json_str.strip():
        return False, None, "JSON input is empty"
    
    try:
        data = json.loads(json_str)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"


def create_sample_application() -> str:
    """
    Create a sample application JSON for testing.
    """
    try:
        sample = {
            "post_applied_for": "Software Engineer",
            "ministry_department": "Ministry of Technology",
            "date_of_advertisement": "2024-01-15",
            "national_identity_no": "M1234567890123",
            "surname": "Ramjeet",
            "other_names": "Mevin Kumar",
            "residential_address": "123 Royal Road, Port Louis",
            "date_of_birth": "1995-06-15",
            "age": 29,
            "place_of_birth": "Port Louis",
            "nationality": "Mauritian",
            "phone_mobile": "52345678",
            "email": "mevin.ramjeet@example.com",
            "ordinary_level_exams": [
                {
                    "examination": "Cambridge O-Level",
                    "year": 2011,
                    "subjects": [
                        {"subject": "Mathematics", "grade": "A"},
                        {"subject": "English Language", "grade": "B"},
                        {"subject": "Physics", "grade": "A"},
                        {"subject": "Chemistry", "grade": "B"},
                        {"subject": "Biology", "grade": "C"}
                    ]
                }
            ],
            "degree_qualifications": [
                {
                    "qualification": "BSc Computer Science",
                    "institution": "University of Mauritius",
                    "country": "Mauritius",
                    "year_obtained": 2017
                }
            ],
            "other_employment": [
                {
                    "employer": "Tech Solutions Ltd",
                    "position": "Junior Developer",
                    "start_date": "2017-08-01",
                    "end_date": "2020-12-31",
                    "duties": "Software development and maintenance"
                }
            ],
            "investigation_enquiry": False,
            "court_conviction": False,
            "resigned_retired_dismissed": False
        }

        return json.dumps(sample, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to create sample: {str(e)}"})
