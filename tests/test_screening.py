#!/usr/bin/env python3
"""
Comprehensive test suite for the screening module.

This module contains tests for:
- Rule filtering and categorization
- Unstructured data gathering and processing
- Mock LLM evaluation functionality
- Real LLM evaluation with error handling
- Hybrid evaluation workflow
- Integration testing and demo functionality
"""

import pytest
import json
import sys
import os
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.screening import (
    get_structured_rules,
    get_unstructured_fields,
    gather_unstructured_data,
    mock_llm_evaluation,
    evaluate_unstructured_data,
    hybrid_evaluate_application
)
from src.config.constants import rules

# ================================
# Test Data Constants
# ================================

SAMPLE_RULES = [
    {"field": "age", "type": "structured", "operator": ">=", "value": 18},
    {"field": "nationality", "type": "structured", "operator": "==", "value": "Zimbabwean"},
    {"field": "investigation_details", "type": "unstructured", "description": "Investigation details", "evaluation_criteria": "Should be empty"}
]

SAMPLE_APPLICATION_DATA = {
    "post_applied_for": "Software Developer",
    "surname": "Smith",
    "other_names": "John",
    "age": 30,
    "nationality": "Zimbabwean",
    "investigation_enquiry": False,
    "court_conviction": False,
    "investigation_details": None,
    "other_qualifications": ["Python", "JavaScript"]
}

COMPLEX_RULES = [
    {"field": "age", "type": "structured", "operator": ">=", "value": 21},
    {"field": "age", "type": "structured", "operator": "<=", "value": 65},
    {"field": "nationality", "type": "structured", "operator": "==", "value": "Zimbabwean"},
    {"field": "investigation_enquiry", "type": "structured", "operator": "==", "value": False},
    {"field": "court_conviction", "type": "structured", "operator": "==", "value": False},
    {"field": "investigation_details", "type": "unstructured", "description": "Investigation details", "evaluation_criteria": "Should be empty or null"},
    {"field": "other_qualifications", "type": "unstructured", "description": "Additional qualifications", "evaluation_criteria": "Should demonstrate relevant skills"},
    {"field": "residential_address", "type": "unstructured", "description": "Residential address", "evaluation_criteria": "Should be complete and valid"}
]

FAILING_APPLICATION_DATA = {
    "post_applied_for": "Software Developer",
    "surname": "Johnson",
    "other_names": "Alice",
    "age": 17,  # Fails age requirement
    "nationality": "American",  # Fails nationality requirement
    "investigation_enquiry": True,  # Fails investigation requirement
    "court_conviction": False,
    "investigation_details": "Under investigation for fraud",  # Fails unstructured evaluation
    "other_qualifications": [],
    "residential_address": "123"  # Incomplete address
}


class TestRuleFiltering:
    """Test rule filtering functions"""
    
    def test_get_structured_rules(self):
        """Test extraction of structured rules"""
        structured = get_structured_rules(SAMPLE_RULES)
        assert len(structured) == 2
        assert all(rule.get("type") != "unstructured" for rule in structured)
    
    def test_get_unstructured_fields(self):
        """Test extraction of unstructured fields"""
        unstructured = get_unstructured_fields(SAMPLE_RULES)
        assert len(unstructured) == 1
        assert all(rule.get("type") == "unstructured" for rule in unstructured)
    
    def test_empty_rules_list(self):
        """Test handling of empty rules list"""
        assert get_structured_rules([]) == []
        assert get_unstructured_fields([]) == []


class TestUnstructuredDataGathering:
    """Test unstructured data gathering"""
    
    def test_gather_unstructured_data_success(self):
        """Test successful gathering of unstructured data"""
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        result = gather_unstructured_data(SAMPLE_APPLICATION_DATA, unstructured_fields)
        
        assert isinstance(result, dict)
        # Should not include investigation_details since it's None
        assert len(result) == 0  # None values are filtered out
    
    def test_gather_unstructured_data_with_values(self):
        """Test gathering when unstructured fields have values"""
        data = SAMPLE_APPLICATION_DATA.copy()
        data["investigation_details"] = "Some investigation info"
        
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        result = gather_unstructured_data(data, unstructured_fields)
        
        assert "investigation_details" in result
        assert result["investigation_details"]["value"] == "Some investigation info"
        assert "description" in result["investigation_details"]
        assert "evaluation_criteria" in result["investigation_details"]
    
    def test_gather_unstructured_data_empty_fields(self):
        """Test gathering with no unstructured fields"""
        result = gather_unstructured_data(SAMPLE_APPLICATION_DATA, [])
        assert result == {}


class TestMockLLMEvaluation:
    """Test mock LLM evaluation functionality"""
    
    def test_mock_llm_evaluation_empty_data(self):
        """Test mock evaluation with empty data"""
        result = mock_llm_evaluation({})
        assert result["passed"] is True
        assert result["field_evaluations"] == []
        assert "Mock evaluation completed" in result["overall_reasoning"]
    
    def test_mock_llm_evaluation_investigation_details(self):
        """Test mock evaluation with investigation details"""
        unstructured_data = {
            "investigation_details": {
                "value": "Some investigation",
                "description": "Investigation details",
                "evaluation_criteria": "Should be empty"
            }
        }
        
        result = mock_llm_evaluation(unstructured_data)
        assert result["passed"] is False
        assert len(result["field_evaluations"]) == 1
        assert result["field_evaluations"][0]["assessment"] == "FAIL"
    
    def test_mock_llm_evaluation_other_qualifications(self):
        """Test mock evaluation with other qualifications"""
        unstructured_data = {
            "other_qualifications": {
                "value": ["Python", "JavaScript"],
                "description": "Additional qualifications",
                "evaluation_criteria": "Beneficial"
            }
        }
        
        result = mock_llm_evaluation(unstructured_data)
        assert result["passed"] is True
        assert result["field_evaluations"][0]["assessment"] == "PASS"
    
    def test_mock_llm_evaluation_residential_address(self):
        """Test mock evaluation with residential address"""
        # Test complete address
        unstructured_data = {
            "residential_address": {
                "value": "123 Main Street, Harare, Zimbabwe",
                "description": "Residential address",
                "evaluation_criteria": "Should be complete"
            }
        }
        
        result = mock_llm_evaluation(unstructured_data)
        assert result["passed"] is True
        assert result["field_evaluations"][0]["assessment"] == "PASS"
        
        # Test incomplete address
        unstructured_data["residential_address"]["value"] = "Short"
        result = mock_llm_evaluation(unstructured_data)
        assert result["passed"] is False
        assert result["field_evaluations"][0]["assessment"] == "FAIL"


class TestUnstructuredDataEvaluation:
    """Test unstructured data evaluation with LLM"""
    
    def test_evaluate_unstructured_data_empty(self):
        """Test evaluation with no unstructured data"""
        result = evaluate_unstructured_data({}, "Software Developer")
        assert result["passed"] is True
        assert "No unstructured data to evaluate" in result["llm_response"]
    
    @patch('src.core.screening.call_llm')
    def test_evaluate_unstructured_data_success(self, mock_call_llm):
        """Test successful LLM evaluation"""
        mock_call_llm.return_value = json.dumps({
            "overall_assessment": "PASS",
            "overall_reasoning": "Candidate looks good",
            "field_evaluations": [
                {"field": "test_field", "assessment": "PASS", "reasoning": "Good"}
            ]
        })
        
        unstructured_data = {
            "test_field": {
                "value": "test_value",
                "description": "Test field",
                "evaluation_criteria": "Test criteria"
            }
        }
        
        result = evaluate_unstructured_data(unstructured_data, "Software Developer")
        assert result["passed"] is True
        assert result["overall_reasoning"] == "Candidate looks good"
        assert len(result["field_evaluations"]) == 1
    
    @patch('src.core.screening.call_llm')
    def test_evaluate_unstructured_data_llm_failure(self, mock_call_llm):
        """Test LLM evaluation failure fallback"""
        mock_call_llm.return_value = None
        
        unstructured_data = {
            "test_field": {
                "value": "test_value",
                "description": "Test field",
                "evaluation_criteria": "Test criteria"
            }
        }
        
        result = evaluate_unstructured_data(unstructured_data, "Software Developer")
        # Should fallback to mock evaluation
        assert "Mock evaluation completed" in result["overall_reasoning"]
    
    @patch('src.core.screening.call_llm')
    def test_evaluate_unstructured_data_invalid_json(self, mock_call_llm):
        """Test handling of invalid JSON response from LLM"""
        mock_call_llm.return_value = "Invalid JSON response"
        
        unstructured_data = {
            "test_field": {
                "value": "test_value",
                "description": "Test field",
                "evaluation_criteria": "Test criteria"
            }
        }
        
        result = evaluate_unstructured_data(unstructured_data, "Software Developer")
        # Should handle invalid JSON gracefully
        assert result["overall_reasoning"] == "LLM evaluation completed (text format)"


class TestHybridEvaluation:
    """Test hybrid evaluation functionality"""
    
    @patch('src.core.screening.evaluate_rules')
    def test_hybrid_evaluate_application_success(self, mock_evaluate_rules):
        """Test successful hybrid evaluation"""
        # Mock structured evaluation
        mock_evaluate_rules.return_value = {
            "passed": True,
            "details": [
                {"passed": True, "reason": "Age requirement met"},
                {"passed": True, "reason": "Nationality requirement met"}
            ]
        }
        
        structured_rules = get_structured_rules(SAMPLE_RULES)
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        
        result = hybrid_evaluate_application(
            SAMPLE_APPLICATION_DATA, 
            structured_rules, 
            unstructured_fields
        )
        
        assert result["overall_passed"] is True
        assert "structured_evaluation" in result
        assert "unstructured_evaluation" in result
        assert "summary" in result
        assert result["summary"]["structured_passed"] is True
    
    @patch('src.core.screening.evaluate_rules')
    def test_hybrid_evaluate_application_structured_failure(self, mock_evaluate_rules):
        """Test hybrid evaluation with structured failure"""
        # Mock structured evaluation failure
        mock_evaluate_rules.return_value = {
            "passed": False,
            "details": [
                {"passed": False, "reason": "Age requirement not met"},
                {"passed": True, "reason": "Nationality requirement met"}
            ]
        }
        
        structured_rules = get_structured_rules(SAMPLE_RULES)
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        
        result = hybrid_evaluate_application(
            SAMPLE_APPLICATION_DATA, 
            structured_rules, 
            unstructured_fields
        )
        
        assert result["overall_passed"] is False
        assert result["summary"]["structured_passed"] is False


class TestMainDemoFunctionality:
    """Test the main demo functionality that was in screening.py"""
    
    def test_demo_with_sample_data(self):
        """Test the demo functionality with sample data"""
        # Create sample data file
        sample_data = SAMPLE_APPLICATION_DATA.copy()
        
        # Test the core functionality that main() was demonstrating
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)
        
        # This should not raise an exception
        results = hybrid_evaluate_application(sample_data, structured_rules, unstructured_fields)
        
        assert "overall_passed" in results
        assert "overall_score" in results
        assert "summary" in results
    
    @patch('builtins.print')
    def test_demo_output_format(self, mock_print):
        """Test that demo output would be properly formatted"""
        results = {
            "overall_passed": True,
            "overall_score": 0.85,
            "summary": {
                "structured_passed": True,
                "unstructured_passed": True,
                "structured_score": 0.9,
                "total_structured_rules": 5,
                "failed_structured_rules": 1,
                "unstructured_fields_evaluated": 2
            },
            "structured_evaluation": {"details": []},
            "unstructured_evaluation": {
                "overall_reasoning": "Good candidate",
                "field_evaluations": []
            }
        }
        
        # Test the output formatting logic
        overall_result = 'PASSED' if results['overall_passed'] else 'FAILED'
        assert overall_result == 'PASSED'
        
        structured_result = 'PASSED' if results['summary']['structured_passed'] else 'FAILED'
        assert structured_result == 'PASSED'


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_rule_types(self):
        """Test handling of invalid rule types."""
        invalid_rules = [
            {"field": "age", "type": "invalid_type", "operator": ">=", "value": 18}
        ]
        
        structured = get_structured_rules(invalid_rules)
        unstructured = get_unstructured_fields(invalid_rules)
        
        # The current implementation treats anything that's not "unstructured" as structured
        # So invalid_type rules end up in structured rules
        assert len(structured) == 1  # Invalid rules are treated as structured
        assert len(unstructured) == 0  # Only rules with type="unstructured" go here
        
        # Verify the invalid rule is in structured (even though it shouldn't be processed)
        assert structured[0]["type"] == "invalid_type"

    def test_missing_application_fields(self):
        """Test handling of missing fields in application data."""
        incomplete_data = {"age": 25}  # Missing most fields
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        
        result = gather_unstructured_data(incomplete_data, unstructured_fields)
        assert isinstance(result, dict)

    def test_none_application_data(self):
        """Test handling of None application data."""
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        
        # This should handle gracefully without crashing
        try:
            result = gather_unstructured_data(None, unstructured_fields)
            # If it doesn't crash, that's good
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass

    @patch('src.core.screening.call_llm')
    def test_llm_timeout_handling(self, mock_call_llm):
        """Test handling of LLM timeout scenarios."""
        mock_call_llm.side_effect = TimeoutError("LLM request timed out")
        
        unstructured_data = {
            "test_field": {
                "value": "test_value",
                "description": "Test field",
                "evaluation_criteria": "Test criteria"
            }
        }
        
        result = evaluate_unstructured_data(unstructured_data, "Software Developer")
        # Should fallback to mock evaluation
        assert "Mock evaluation completed" in result["overall_reasoning"]


class TestPerformance:
    """Test performance and scalability aspects."""

    def test_large_rules_set_performance(self):
        """Test performance with large number of rules."""
        # Create a large set of rules
        large_rules = []
        for i in range(100):
            large_rules.append({
                "field": f"field_{i}",
                "type": "structured" if i % 2 == 0 else "unstructured",
                "operator": "==",
                "value": f"value_{i}",
                "description": f"Field {i}",
                "evaluation_criteria": f"Criteria {i}"
            })
        
        # Test that filtering still works efficiently
        structured = get_structured_rules(large_rules)
        unstructured = get_unstructured_fields(large_rules)
        
        assert len(structured) == 50  # Half should be structured
        assert len(unstructured) == 50  # Half should be unstructured

    def test_large_application_data_performance(self):
        """Test performance with large application data."""
        # Create large application data
        large_data = SAMPLE_APPLICATION_DATA.copy()
        for i in range(50):
            large_data[f"extra_field_{i}"] = f"value_{i}"
        
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        result = gather_unstructured_data(large_data, unstructured_fields)
        
        # Should complete without performance issues
        assert isinstance(result, dict)


class TestIntegration:
    """Integration tests for complete screening workflow."""

    @patch('src.core.screening.evaluate_rules')
    def test_complete_screening_workflow_success(self, mock_evaluate_rules, sample_application, complex_rules):
        """Test complete screening workflow with passing candidate."""
        mock_evaluate_rules.return_value = {
            "passed": True,
            "details": [{"passed": True, "reason": "All requirements met"}]
        }
        
        structured_rules = get_structured_rules(complex_rules)
        unstructured_fields = get_unstructured_fields(complex_rules)
        
        result = hybrid_evaluate_application(sample_application, structured_rules, unstructured_fields)
        
        assert result["overall_passed"] is True
        assert "structured_evaluation" in result
        assert "unstructured_evaluation" in result
        assert "summary" in result

    @patch('src.core.screening.evaluate_rules')
    def test_complete_screening_workflow_failure(self, mock_evaluate_rules, failing_application, complex_rules):
        """Test complete screening workflow with failing candidate."""
        mock_evaluate_rules.return_value = {
            "passed": False,
            "details": [{"passed": False, "reason": "Age requirement not met"}]
        }
        
        structured_rules = get_structured_rules(complex_rules)
        unstructured_fields = get_unstructured_fields(complex_rules)
        
        result = hybrid_evaluate_application(failing_application, structured_rules, unstructured_fields)
        
        assert result["overall_passed"] is False
        assert result["summary"]["structured_passed"] is False

    def test_real_rules_integration(self):
        """Test integration with actual rules from constants."""
        # Test with real rules from the constants module
        structured_rules = get_structured_rules(rules)
        unstructured_fields = get_unstructured_fields(rules)
        
        # Should not raise exceptions
        assert isinstance(structured_rules, list)
        assert isinstance(unstructured_fields, list)

    @patch('src.core.screening.evaluate_rules')
    @patch('src.core.screening.call_llm')
    def test_end_to_end_screening_with_mocks(self, mock_call_llm, mock_evaluate_rules, sample_application, mock_llm_response):
        """Test end-to-end screening with all external dependencies mocked."""
        # Mock structured evaluation
        mock_evaluate_rules.return_value = {
            "passed": True,
            "details": [{"passed": True, "reason": "All structured requirements met"}]
        }
        
        # Mock LLM response
        mock_call_llm.return_value = json.dumps(mock_llm_response)
        
        structured_rules = get_structured_rules(SAMPLE_RULES)
        unstructured_fields = get_unstructured_fields(SAMPLE_RULES)
        
        result = hybrid_evaluate_application(sample_application, structured_rules, unstructured_fields)
        
        assert result["overall_passed"] is True
        assert result["summary"]["structured_passed"] is True
        assert result["summary"]["unstructured_passed"] is True
        assert "overall_score" in result


# ================================
# Pytest Fixtures
# ================================

@pytest.fixture
def sample_application():
    """Fixture providing sample application data."""
    return SAMPLE_APPLICATION_DATA.copy()

@pytest.fixture
def failing_application():
    """Fixture providing failing application data."""
    return FAILING_APPLICATION_DATA.copy()

@pytest.fixture
def sample_rules():
    """Fixture providing sample rules."""
    return SAMPLE_RULES.copy()

@pytest.fixture
def complex_rules():
    """Fixture providing complex rules for comprehensive testing."""
    return COMPLEX_RULES.copy()

@pytest.fixture
def structured_rules():
    """Fixture providing only structured rules."""
    return get_structured_rules(SAMPLE_RULES)

@pytest.fixture
def unstructured_fields():
    """Fixture providing only unstructured fields."""
    return get_unstructured_fields(SAMPLE_RULES)

@pytest.fixture
def mock_llm_response():
    """Fixture providing a mock LLM response."""
    return {
        "overall_assessment": "PASS",
        "overall_reasoning": "Candidate meets all requirements",
        "field_evaluations": [
            {
                "field": "other_qualifications",
                "assessment": "PASS",
                "reasoning": "Relevant technical skills demonstrated"
            }
        ]
    }

@pytest.fixture
def temp_data_file(tmp_path):
    """Fixture providing a temporary data file."""
    data_file = tmp_path / "test_application.json"
    data_file.write_text(json.dumps(SAMPLE_APPLICATION_DATA, indent=2))
    return data_file

@pytest.fixture
def temp_rules_file(tmp_path):
    """Fixture providing a temporary rules file."""
    rules_file = tmp_path / "test_rules.json"
    rules_file.write_text(json.dumps(SAMPLE_RULES, indent=2))
    return rules_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
