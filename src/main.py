rules = [
    # =========================
    # BASIC ELIGIBILITY
    # =========================
    {"field": "nationality", "type": "exact_match", "value": "Mauritian"},
    {"field": "age", "type": "range", "min": 18, "max": 45},
    {"field": "date_of_birth", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    {"field": "national_identity_no", "type": "regex", "pattern": r"^[A-Z0-9]{14,20}$"},

    # =========================
    # CONTACT INFORMATION
    # =========================
    {"field": "email", "type": "regex", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
    {"field": "phone_mobile", "type": "regex", "pattern": r"^[0-9]{7,8}$"},
    {"type": "or", "rules": [
        {"field": "phone_office", "type": "exists"},
        {"field": "phone_home", "type": "exists"},
        {"field": "phone_mobile", "type": "exists"}
    ]},

    # =========================
    # APPLICATION INFORMATION
    # =========================
    {"type": "and", "rules": [
        {"field": "post_applied_for", "type": "exists"},
        {"field": "ministry_department", "type": "exists"},
        {"field": "date_of_advertisement", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
    ]},

    # =========================
    # QUALIFICATIONS – ORDINARY LEVEL
    # =========================
    {"type": "and", "rules": [
        {"field": "ordinary_level_exams", "type": "exists"},
        {"field": "ordinary_level_exams.0.subjects", "type": "exists"},
        # Require a pass in English, Maths and another core science or language subject
        {"field": "ordinary_level_exams.*.subjects", "match_field": "subject", "match_value": "Mathematics", "check_field": "grade", "type": "one_of", "values": ['A', 'B', 'C']},
        {"field": "ordinary_level_exams.*.subjects", "match_field": "subject", "match_value": "English Language",
         "check_field": "grade", "type": "one_of", "values": ["1", "2", "3", "A", "B", "C"]}

    ]},


    # =========================
    # QUALIFICATIONS – ADVANCED LEVEL (IF PRESENT)
    # =========================
    {"type": "optional_and", "rules": [
        {"field": "advanced_level_exams", "type": "exists"},
        {"field": "advanced_level_exams.0.subjects", "type": "exists"},
        # Require a pass in English, Maths and another core science or language subject
        {"field": "advanced_level_exams.*.subjects", "match_field": "subject", "match_value": "Mathematics",
         "check_field": "grade", "type": "one_of", "values": ['A', 'B', 'C']},
        {"field": "advanced_level_exams.*.subjects", "match_field": "subject", "match_value": "English Language",
         "check_field": "grade", "type": "one_of", "values": ["1", "2", "3", "A+", "B", "C"]}
    ]},

    # =========================
    # HIGHER QUALIFICATIONS
    # =========================
    {"type": "or", "rules": [
        {"field": "technical_vocational_qualifications", "type": "exists"},
        {"field": "diploma_qualifications", "type": "exists"},
        {"field": "degree_qualifications", "type": "exists"},
        {"field": "degree_qualifications.*.country", "type": "one_of", "values": ["Mauritius", "UK", "USA", "Canada", "Australia", "France"]},
        {"field": "post_degree_qualifications", "type": "exists"}
    ]},

    # =========================
    # EMPLOYMENT HISTORY
    # =========================
    {"type": "or", "rules": [
        {"field": "current_government_employment", "type": "exists"},
        {"field": "previous_government_employment", "type": "exists"},
        {"field": "other_employment", "type": "exists"}
    ]},

    {"field": "current_government_employment.date_of_appointment", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$",
     "optional": True},
    {"field": "previous_government_employment.0.start_date", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$",
     "optional": True},

    # =========================
    # LEGAL / CONDUCT
    # =========================
    {"field": "investigation_enquiry", "type": "boolean", "value": False},
    {"field": "court_conviction", "type": "boolean", "value": False},
    {"field": "resigned_retired_dismissed", "type": "boolean", "value": False},
]

import re
from typing import Any, Dict, List


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
        passed, reason = evaluate_rule(data, rule)
        results.append({"rule": rule, "passed": passed, "reason": reason})
        if not passed:
            all_passed = False

    return {"passed": all_passed, "details": results}


def evaluate_rule(data: Dict[str, Any], rule: Dict[str, Any]) -> (bool, str):
    """Evaluate a single rule."""
    rule_type = rule.get("type")

    # ---- Logical (composite) rules ----
    if rule_type == "and":
        sub_results = [evaluate_rule(data, r)[0] for r in rule.get("rules", [])]
        return all(sub_results), "All subrules must pass."
    elif rule_type == "or":
        sub_results = [evaluate_rule(data, r)[0] for r in rule.get("rules", [])]
        return (any(sub_results), "At least one subrule must pass.")
    elif rule_type == "not":
        sub = rule.get("rule")
        result, _ = evaluate_rule(data, sub)
        return (not result, "Negated rule result.")

    # ---- Field-based rules ----
    field = rule.get("field")
    value = get_field_value(data, field)

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
    else:
        return (False, f"Unknown rule type: {rule_type}")


def get_field_value(data: Dict[str, Any], field_path: str) -> Any:
    """
    Supports dot-path access (e.g. 'current_government_employment.post').
    """
    parts = field_path.split(".")
    value = data
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value
import json
import re

# 1. DEFINING THE CANONICAL MAPPING DICTIONARY

# Keys are common abbreviations (cleaned: lowercase, no periods/spaces),
# Values are the full, canonical degree names.
DEGREE_CANONICAL_MAP = {
    "ba": "Bachelor of Arts", "ab": "Bachelor of Arts",
    "bs": "Bachelor of Science", "bsc": "Bachelor of Science",
    "bacc": "Bachelor of Accounting",
    "bba": "Bachelor of Business Administration",
    "bcom": "Bachelor of Commerce", "bcomm": "Bachelor of Commerce",
    "bed": "Bachelor of Education",
    "beng": "Bachelor of Engineering",
    "bfa": "Bachelor of Fine Arts",
    "bhsc": "Bachelor of Health Science",
    "bla": "Bachelor of Liberal Arts",
    "llb": "Bachelor of Laws",
    "bsw": "Bachelor of Social Work",
    "barch": "Bachelor of Architecture",
    "btech": "Bachelor of Technology",

    "ma": "Master of Arts", "am": "Master of Arts",
    "ms": "Master of Science", "msc": "Master of Science",
    "mba": "Master of Business Administration",
    "med": "Master of Education",
    "mfa": "Master of Fine Arts",
    "mpa": "Master of Public Administration",
    "mph": "Master of Public Health",
    "llm": "Master of Laws",
    "mphil": "Master of Philosophy",
    "mres": "Master of Research",
    "meng": "Master of Engineering",

    "phd": "Doctor of Philosophy", "dphil": "Doctor of Philosophy",
    "edd": "Doctor of Education",
    "dba": "Doctor of Business Administration",
    "jd": "Juris Doctor",
    "md": "Doctor of Medicine",
    "dvm": "Doctor of Veterinary Medicine",
    "psyd": "Doctor of Psychology",
    "pharmd": "Doctor of Pharmacy",
    "dsc": "Doctor of Science",
}

# 2. HELPER FUNCTIONS

def clean_code_for_lookup(code: str) -> str:
    # Cleans a degree code for dictionary lookup (lowercase, no periods/spaces)
    return code.lower().replace('.', '').replace(' ', '').strip()

def normalize_degree_code(code: str) -> str:
    # Looks up and returns the canonical form, or the original code if no match
    cleaned_code = clean_code_for_lookup(code)
    return DEGREE_CANONICAL_MAP.get(cleaned_code, code)


def standardize_qualification_name(qualification_name: str) -> str:

    # Standardizes the degree type within a full qualification name.
    # e.g., "B.Sc. Management Studies" -> "Bachelor of Science in Management Studies"

    if not qualification_name:
        return qualification_name.strip()

    # Regex to find a potential degree code (letters/periods) at the start,
    # followed by a space and the rest of the string (field of study).
    match = re.match(r"^([\w\.]+)\s+(.*)$", qualification_name.strip(), re.IGNORECASE)

    if match:
        degree_code = match.group(1).strip()
        field_of_study = match.group(2).strip()

        standard_degree = normalize_degree_code(degree_code)

        if clean_code_for_lookup(standard_degree) != clean_code_for_lookup(degree_code):
            # If successfully mapped to a canonical degree, reconstruct with "in"
            return f"{standard_degree} in {field_of_study}"
        else:
            # If the code was not in the map (e.g., 'Certificate'), return original
            return qualification_name

    # Handles cases where the qualification is ONLY the code (e.g., "PH. D")
    return normalize_degree_code(qualification_name)


# 3. MAIN PROCESSING FUNCTION

def process_job_application_json(input_filepath: str, output_filepath: str):
    """
    Loads a JSON file, standardizes the qualification names, and saves to a new file.
    """
    print(f"Loading data from: {input_filepath}")

    try:
        with open(input_filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_filepath}. Check file integrity.")
        return

    # Arrays to target for standardization
    qualification_arrays = [
        "ordinary_level_exams",
        "advanced_level_exams",
        "technical_vocational_qualifications",
        "diploma_qualifications",
        "degree_qualifications",
        "post_degree_qualifications"
    ]

    total_changes = 0

    for array_key in qualification_arrays:
        # Check if the array exists and is not null/empty
        if array_key in data and isinstance(data[array_key], list):
            for i, qualification in enumerate(data[array_key]):
                # The field to check is "qualification_name" (or "exam_type" for O/A levels)
                # We prioritize "qualification_name" as it holds the degrees.
                key_to_check = "qualification_name"

                if key_to_check in qualification and qualification[key_to_check]:
                    original_name = qualification[key_to_check]
                    standardized_name = standardize_qualification_name(original_name)

                    if original_name != standardized_name:
                        qualification[key_to_check] = standardized_name
                        total_changes += 1

    print(f"Processing complete. {total_changes} qualification names standardized.")

    # Save the modified data to the new JSON file
    try:
        with open(output_filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved standardized data to: {output_filepath}")
    except Exception as e:
        print(f"Error saving output file: {e}")


if __name__ == "__main__":
    INPUT_FILE = "src/sample.json"
    OUTPUT_FILE = "src/sample_standardized.json"

    process_job_application_json(INPUT_FILE, OUTPUT_FILE)
