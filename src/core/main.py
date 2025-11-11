

import re
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.rules_engine import get_field_value, evaluate_rules
from src.utils.call_llm import call_llm
from src.constants import structured_rules, unstructured_fields
from src.utils.logger import configured_logger

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



def gather_unstructured_data(data: Dict[str, Any], unstructured_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gathers unstructured data from the application based on the defined unstructured fields.

    Args:
        data: The application data dictionary
        unstructured_fields: List of unstructured field definitions

    Returns:
        Dictionary containing gathered unstructured data
    """
    unstructured_data = {}

    for field_def in unstructured_fields:
        field_name = field_def["field"]
        field_value = get_field_value(data, field_name)

        if field_value is not None:
            unstructured_data[field_name] = {
                "value": field_value,
                "description": field_def["description"],
                "evaluation_criteria": field_def["evaluation_criteria"]
            }

    return unstructured_data


def mock_llm_evaluation(unstructured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock LLM evaluation for testing when API key is not available.
    """
    field_evaluations = []
    overall_passed = True
    
    for field_name, field_info in unstructured_data.items():
        value = field_info['value']
        
        # Simple heuristic evaluation
        if field_name in ['investigation_details', 'conviction_details', 'resignation_details']:
            # These should be None/empty for a passing candidate
            assessment = "PASS" if not value else "FAIL"
            reasoning = f"No concerning {field_name.replace('_', ' ')}" if not value else f"Has {field_name.replace('_', ' ')} that needs review"
        elif field_name == 'other_qualifications':
            # Additional qualifications are generally positive
            assessment = "PASS"
            reasoning = "Additional qualifications are beneficial"
        elif field_name == 'residential_address':
            # Check if address seems complete
            assessment = "PASS" if value and len(str(value)) > 10 else "FAIL"
            reasoning = "Address appears complete" if assessment == "PASS" else "Address appears incomplete"
        else:
            assessment = "PASS"
            reasoning = "No issues identified"
        
        field_evaluations.append({
            "field": field_name,
            "assessment": assessment,
            "reasoning": reasoning
        })
        
        if assessment == "FAIL":
            overall_passed = False
    
    return {
        "passed": overall_passed,
        "overall_reasoning": "Mock evaluation completed - replace with actual LLM when API key is configured",
        "field_evaluations": field_evaluations,
        "llm_response": "Mock response"
    }


def evaluate_unstructured_data(unstructured_data: Dict[str, Any], post_applied_for: str = "") -> Dict[str, Any]:
    """
    Evaluates unstructured data using LLM.
    
    Args:
        unstructured_data: Dictionary of unstructured data to evaluate
        post_applied_for: The position being applied for (for context)
        
    Returns:
        Dictionary containing LLM evaluation results
    """
    if not unstructured_data:
        return {"passed": True, "details": [], "llm_response": "No unstructured data to evaluate"}
    
    # Prepare the prompt for LLM evaluation
    prompt_parts = [
        f"You are evaluating a job application for the position: {post_applied_for or 'Government Position'}",
        "Please evaluate the following unstructured data fields and determine if they indicate any issues that would disqualify the candidate.",
        "For each field, provide a score (PASS/FAIL) and brief reasoning.",
        "\nUnstructured Data to Evaluate:"
    ]
    
    field_evaluations = []
    for field_name, field_info in unstructured_data.items():
        prompt_parts.append(f"\n{field_name.upper()}:")
        prompt_parts.append(f"Description: {field_info['description']}")
        prompt_parts.append(f"Value: {field_info['value']}")
        prompt_parts.append(f"Evaluation Criteria: {field_info['evaluation_criteria']}")
        prompt_parts.append("---")
    
    prompt_parts.append("\nPlease provide your evaluation in the following JSON format:")
    prompt_parts.append("""{
  "overall_assessment": "PASS" or "FAIL",
  "overall_reasoning": "Brief explanation of overall decision",
  "field_evaluations": [
    {
      "field": "field_name",
      "assessment": "PASS" or "FAIL",
      "reasoning": "Brief explanation"
    }
  ]
}""")
    
    full_prompt = "\n".join(prompt_parts)
    
    try:
        messages = [
            {"role": "system", "content": "You are an expert HR evaluator for government positions. Evaluate applications objectively and fairly."},
            {"role": "user", "content": full_prompt}
        ]
        
        llm_response = call_llm(messages, temperature=0.1)
        
        if llm_response:
            try:
                # Try to parse JSON response
                evaluation_result = json.loads(llm_response)
                
                overall_passed = evaluation_result.get("overall_assessment", "FAIL").upper() == "PASS"
                
                return {
                    "passed": overall_passed,
                    "overall_reasoning": evaluation_result.get("overall_reasoning", ""),
                    "field_evaluations": evaluation_result.get("field_evaluations", []),
                    "llm_response": llm_response
                }
            except json.JSONDecodeError:
                configured_logger.warning(f"Could not parse LLM response as JSON: {llm_response}")
                # Fallback: simple text analysis
                overall_passed = "PASS" in llm_response.upper() and "FAIL" not in llm_response.upper()
                return {
                    "passed": overall_passed,
                    "overall_reasoning": "LLM evaluation completed (text format)",
                    "field_evaluations": [],
                    "llm_response": llm_response
                }
        else:
            configured_logger.warning("No response from LLM - using mock evaluation")
            return mock_llm_evaluation(unstructured_data)
            
    except Exception as e:
        configured_logger.error(f"Error in LLM evaluation: {e} - using mock evaluation")
        return mock_llm_evaluation(unstructured_data)


def hybrid_evaluate_application(data: Dict[str, Any], structured_rules: List[Dict[str, Any]], 
                               unstructured_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs hybrid evaluation combining structured rules and LLM-based unstructured evaluation.
    
    Args:
        data: The application data dictionary
        structured_rules: List of structured rule definitions
        unstructured_fields: List of unstructured field definitions
        
    Returns:
        Dictionary containing comprehensive evaluation results
    """
    configured_logger.info("Starting hybrid evaluation")
    
    # Step 1: Evaluate structured rules
    structured_results = evaluate_rules(data, structured_rules)
    configured_logger.info(f"Structured evaluation completed: {structured_results['passed']}")
    
    # Step 2: Gather and evaluate unstructured data
    unstructured_data = gather_unstructured_data(data, unstructured_fields)
    configured_logger.info(f"Gathered {len(unstructured_data)} unstructured fields")
    
    post_applied_for = data.get("post_applied_for", "")
    unstructured_results = evaluate_unstructured_data(unstructured_data, post_applied_for)
    configured_logger.info(f"Unstructured evaluation completed: {unstructured_results['passed']}")
    
    # Step 3: Combine results
    overall_passed = structured_results["passed"] and unstructured_results["passed"]
    
    # Calculate scores
    structured_score = sum(1 for detail in structured_results["details"] if detail["passed"]) / len(structured_results["details"]) if structured_results["details"] else 0
    
    return {
        "overall_passed": overall_passed,
        "overall_score": (structured_score + (1 if unstructured_results["passed"] else 0)) / 2,
        "structured_evaluation": structured_results,
        "unstructured_evaluation": unstructured_results,
        "unstructured_data_found": unstructured_data,
        "summary": {
            "structured_passed": structured_results["passed"],
            "unstructured_passed": unstructured_results["passed"],
            "structured_score": structured_score,
            "total_structured_rules": len(structured_results["details"]),
            "failed_structured_rules": len([d for d in structured_results["details"] if not d["passed"]]),
            "unstructured_fields_evaluated": len(unstructured_data)
        }
    }




def main():
    """Main function to demonstrate the hybrid screening pipeline."""
    INPUT_FILE = "sample.json"
    
    print("=" * 60)
    print("HYBRID RESUME SCREENING PIPELINE")
    print("=" * 60)
    
    try:
        # Load sample data
        with open(INPUT_FILE, 'r') as f:
            application_data = json.load(f)
        
        print(f"\nLoaded application for: {application_data.get('surname', 'Unknown')} {application_data.get('other_names', '')}")
        print(f"Position applied for: {application_data.get('post_applied_for', 'Unknown')}")
        
        # Run hybrid evaluation
        results = hybrid_evaluate_application(application_data, structured_rules, unstructured_fields)
        
        # Display results
        print("\n" + "=" * 40)
        print("EVALUATION RESULTS")
        print("=" * 40)
        
        print(f"\nOVERALL RESULT: {'PASSED' if results['overall_passed'] else 'FAILED'}")
        print(f"Overall Score: {results['overall_score']:.2%}")
        
        print("\nSTRUCTURED EVALUATION:")
        print(f"  Result: {'PASSED' if results['summary']['structured_passed'] else 'FAILED'}")
        print(f"  Score: {results['summary']['structured_score']:.2%}")
        print(f"  Rules Passed: {results['summary']['total_structured_rules'] - results['summary']['failed_structured_rules']}/{results['summary']['total_structured_rules']}")
        
        if results['summary']['failed_structured_rules'] > 0:
            print("\n  Failed Rules:")
            for detail in results['structured_evaluation']['details']:
                if not detail['passed']:
                    print(f"    X {detail['reason']}")
        
        print("\nUNSTRUCTURED EVALUATION (LLM):")
        print(f"  Result: {'PASSED' if results['summary']['unstructured_passed'] else 'FAILED'}")
        print(f"  Fields Evaluated: {results['summary']['unstructured_fields_evaluated']}")
        
        if results['unstructured_evaluation']['overall_reasoning']:
            print(f"  LLM Reasoning: {results['unstructured_evaluation']['overall_reasoning']}")
        
        if results['unstructured_evaluation']['field_evaluations']:
            print("\n  Field-by-field LLM Assessment:")
            for field_eval in results['unstructured_evaluation']['field_evaluations']:
                status = "PASS" if field_eval.get('assessment', '').upper() == 'PASS' else "FAIL"
                print(f"    {status}: {field_eval.get('field', 'Unknown')}: {field_eval.get('reasoning', 'No reasoning provided')}")
        
        # Save detailed results
        output_file = "evaluation_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{INPUT_FILE}'")
        print("Please ensure the sample.json file exists in the current directory.")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        configured_logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
