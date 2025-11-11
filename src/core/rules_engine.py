import re
from typing import Dict, Any, List

from src.utils.logger import configured_logger


def get_field_value(data: Dict[str, Any], field_path: str) -> Any:
    """
    Enhanced field value extraction with support for:
    - Dot-path access (e.g. 'current_government_employment.post')
    - Array wildcard access (e.g. 'ordinary_level_exams.*.subjects')
    - Array index access (e.g. 'ordinary_level_exams.0.subjects')
    """
    if not field_path:
        return data

    parts = field_path.split(".")
    value = data

    for part in parts:
        if value is None:
            return None

        # Handle array wildcard (*)
        if part == "*":
            if isinstance(value, list):
                # Return all items in the array for further processing
                return value
            else:
                return None

        # Handle array index access
        if part.isdigit():
            if isinstance(value, list):
                idx = int(part)
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return None
            else:
                return None
        # Handle dictionary key access
        elif isinstance(value, dict) and part in value:
            value = value[part]
        # Handle array of dictionaries with wildcard in previous step
        elif isinstance(value, list):
            # This handles cases like 'ordinary_level_exams.*.subjects'
            results = []
            for item in value:
                if isinstance(item, dict) and part in item:
                    results.append(item[part])
            return results if results else None
        else:
            return None

    return value


def evaluate_wildcard_rule(data: Dict[str, Any], rule: Dict[str, Any]) -> (bool, str):
    """
    Handles rules with wildcard field paths like 'ordinary_level_exams.*.subjects'
    """
    field = rule.get("field")
    rule_type = rule.get("type")

    # Handle complex matching rules with wildcards
    if "match_field" in rule and "match_value" in rule and "check_field" in rule:
        match_field = rule.get("match_field")
        match_value = rule.get("match_value")
        check_field = rule.get("check_field")
        allowed_values = rule.get("values", [])

        # Parse the wildcard path
        parts = field.split(".")
        current_data = data

        # Navigate to the array containing the wildcard
        for i, part in enumerate(parts):
            if part == "*":
                # Found wildcard, process the remaining path
                remaining_path = ".".join(parts[i + 1:]) if i + 1 < len(parts) else ""

                if isinstance(current_data, list):
                    # Search through array items
                    for array_item in current_data:
                        if remaining_path:
                            # Get the nested field (e.g., "subjects")
                            nested_value = get_field_value(array_item, remaining_path)
                        else:
                            nested_value = array_item

                        if isinstance(nested_value, list):
                            # Search through subjects array
                            for subject in nested_value:
                                if isinstance(subject, dict) and subject.get(match_field) == match_value:
                                    check_value = subject.get(check_field)
                                    if check_value in allowed_values:
                                        return (True,
                                                f"Found {match_value} with acceptable {check_field}: {check_value}")

                return (False, f"Could not find {match_value} with acceptable {check_field} in {allowed_values}")
            else:
                if isinstance(current_data, dict) and part in current_data:
                    current_data = current_data[part]
                else:
                    return (False, f"Path {field} not found in data")

    # For other rule types with wildcards, use standard evaluation
    value = get_field_value(data, field)
    if value is None:
        return (False, f"Field {field} missing.")

    # Apply the rule type to the resolved value
    temp_rule = rule.copy()
    temp_rule["field"] = "temp"  # Temporary field name
    return evaluate_rule({"temp": value}, temp_rule)


def evaluate_rule(data: Dict[str, Any], rule: Dict[str, Any]) -> (bool, str):
    """Evaluate a single rule with enhanced rule types."""
    rule_type = rule.get("type")

    # Handle optional rules
    if rule.get("optional", False):
        field = rule.get("field")
        if field and get_field_value(data, field) is None:
            return True, f"Optional field '{field}' not present - skipping validation."

    # ---- Logical (composite) rules ----
    if rule_type == "and":
        sub_results = [evaluate_rule(data, r)[0] for r in rule.get("rules", [])]
        return all(sub_results), "All subrules must pass."
    elif rule_type == "or":
        sub_results = [evaluate_rule(data, r)[0] for r in rule.get("rules", [])]
        return (any(sub_results), "At least one subrule must pass.")
    elif rule_type == "optional_and":
        # All rules must pass IF any field exists
        sub_rules = rule.get("rules", [])
        any_field_exists = any(get_field_value(data, r.get("field")) is not None for r in sub_rules if r.get("field"))
        if not any_field_exists:
            return True, "Optional group - no fields present."
        sub_results = [evaluate_rule(data, r)[0] for r in sub_rules]
        return all(sub_results), "All subrules in optional group must pass when present."
    elif rule_type == "not":
        sub = rule.get("rule")
        result, _ = evaluate_rule(data, sub)
        return (not result, "Negated rule result.")

    # ---- Field-based rules ----
    field = rule.get("field")
    value = get_field_value(data, field)

    # Handle wildcard field paths for complex matching
    if field and "*" in field:
        return evaluate_wildcard_rule(data, rule)

    if rule_type == "exists":
        return (value is not None, f"Field '{field}' must exist.")
    elif rule_type == "not_exists":
        return value is None, f"Field '{field}' must not exist."
    elif rule_type == "exact_match":
        return (value == rule.get("value"), f"Expected {rule.get('value')}, got {value}.")
    elif rule_type == "one_of":
        return (value in rule.get("values", []), f"{value} not in allowed set.")
    elif rule_type == "not_in":
        return (value not in rule.get("values", []), f"{value} is disallowed.")
    elif rule_type == "range":
        min_v, max_v = rule.get("min"), rule.get("max")
        if value is None:
            return (False, f"{field} missing.")
        return (min_v <= value <= max_v, f"{field}={value} not in range {min_v}-{max_v}.")
    elif rule_type == "min":
        if value is None:
            return (False, f"{field} missing.")
        return (value >= rule.get("min"), f"{field}={value} < {rule.get('min')}")
    elif rule_type == "max":
        if value is None:
            return (False, f"{field} missing.")
        return (value <= rule.get("max"), f"{field}={value} > {rule.get('max')}")
    elif rule_type == "regex":
        pattern = rule.get("pattern")
        if value is None:
            return (False, f"{field} missing.")
        return (bool(re.match(pattern, str(value))), f"{field} does not match {pattern}.")
    elif rule_type == "boolean":
        return (value is rule.get("value"), f"Expected {rule.get('value')}, got {value}.")
    elif rule_type == "date_before":
        return (str(value) < str(rule.get("before")), f"{value} is not before {rule.get('before')}.")
    elif rule_type == "date_after":
        return (str(value) > str(rule.get("after")), f"{value} is not after {rule.get('after')}.")

    # ---- NEW ENHANCED RULE TYPES ----
    elif rule_type == "string_contains":
        if value is None:
            return (False, f"{field} missing.")
        search_values = rule.get("values", [])
        case_insensitive = rule.get("case_insensitive", False)
        value_str = str(value)
        if case_insensitive:
            value_str = value_str.lower()
            search_values = [v.lower() for v in search_values]
        contains_any = any(search_val in value_str for search_val in search_values)
        return (contains_any, f"{field} must contain one of {rule.get('values')}.")

    elif rule_type == "length_check":
        if value is None:
            return (False, f"{field} missing.")
        value_len = len(str(value))
        min_len = rule.get("min_length", 0)
        max_len = rule.get("max_length", float('inf'))
        valid_length = min_len <= value_len <= max_len
        return (valid_length, f"{field} length {value_len} not in range {min_len}-{max_len}.")

    elif rule_type == "date_range":
        if value is None:
            return (False, f"{field} missing.")
        try:
            date_val = str(value)
            after_date = rule.get("after")
            before_date = rule.get("before")
            valid = True
            reason = ""

            if after_date and date_val <= after_date:
                valid = False
                reason += f"{date_val} not after {after_date}. "
            if before_date and date_val >= before_date:
                valid = False
                reason += f"{date_val} not before {before_date}. "

            return (valid, reason.strip() or f"{field} date is valid.")
        except Exception as e:
            return (False, f"Invalid date format for {field}: {e}")

    elif rule_type == "array_length":
        if value is None:
            return (False, f"{field} missing.")
        if not isinstance(value, list):
            return (False, f"{field} is not an array.")
        array_len = len(value)
        min_len = rule.get("min_length", 0)
        max_len = rule.get("max_length", float('inf'))
        valid_length = min_len <= array_len <= max_len
        return (valid_length, f"{field} array length {array_len} not in range {min_len}-{max_len}.")

    elif rule_type == "nested_field_validation":
        # For complex nested validations
        nested_rules = rule.get("nested_rules", [])
        all_passed = True
        reasons = []

        for nested_rule in nested_rules:
            passed, reason = evaluate_rule(data, nested_rule)
            if not passed:
                all_passed = False
                reasons.append(reason)

        return (all_passed, "; ".join(reasons) if reasons else "All nested validations passed.")

    # Handle complex array matching rules (like the existing ones in the original code)
    elif "match_field" in rule and "match_value" in rule and "check_field" in rule:
        # This handles rules like: find subject "Mathematics" and check if grade is in allowed values
        if value is None:
            return (False, f"{field} missing.")

        match_field = rule.get("match_field")
        match_value = rule.get("match_value")
        check_field = rule.get("check_field")
        allowed_values = rule.get("values", [])

        # Handle array of objects
        if isinstance(value, list):
            for item_list in value:  # Each exam result
                if isinstance(item_list, list):  # subjects array
                    for item in item_list:
                        if isinstance(item, dict) and item.get(match_field) == match_value:
                            check_value = item.get(check_field)
                            if check_value in allowed_values:
                                return (True, f"Found {match_value} with acceptable {check_field}: {check_value}")
                elif isinstance(item_list, dict) and item_list.get(match_field) == match_value:
                    check_value = item_list.get(check_field)
                    if check_value in allowed_values:
                        return (True, f"Found {match_value} with acceptable {check_field}: {check_value}")

            return (False, f"Could not find {match_value} with acceptable {check_field} in {allowed_values}")

        return (False, f"Field {field} is not an array for matching rule.")

    elif rule_type == "unstructured":
        # Skip unstructured rules in structured evaluation - they're handled separately
        return (True, f"Unstructured field '{field}' - handled by LLM evaluation")
    
    else:
        return (False, f"Unknown rule type: {rule_type}")


def evaluate_rules(data: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a list of structured rules against a JSON-like dictionary.

    Args:
        data: The structured JSON object (e.g. PSCApplication as dict)
        rules: List of rule definitions

    Returns:
        {
            "passed": bool,
            "details": [{"rule": rule, "passed": bool, "reason": str}]
        }
    """
    results = []
    all_passed = True

    for rule in rules:
        try:
            passed, reason = evaluate_rule(data, rule)
            results.append({"rule": rule, "passed": passed, "reason": reason})
            if not passed:
                all_passed = False
        except Exception as e:
            configured_logger.error(f"Error evaluating rule {rule}: {e}")
            results.append({"rule": rule, "passed": False, "reason": f"Rule evaluation error: {e}"})
            all_passed = False

    return {"passed": all_passed, "details": results}


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
