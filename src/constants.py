# Combined rules for validation (structured and unstructured)
rules = [
    # =========================
    # BASIC ELIGIBILITY
    # =========================
    {"field": "nationality", "type": "exact_match", "value": "Mauritian"},
    {"field": "age", "type": "range", "min": 18, "max": 45},
    {"field": "date_of_birth", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    {"field": "national_identity_no", "type": "regex", "pattern": r"^[A-Z0-9]{14,20}$"},
    {"field": "national_identity_no", "type": "length_check", "min_length": 14, "max_length": 20},

    # =========================
    # CONTACT INFORMATION
    # =========================
    {"field": "email", "type": "regex", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
    {"field": "phone_mobile", "type": "regex", "pattern": r"^[0-9]{7,8}$"},
    {"field": "residential_address", "type": "string_contains", "values": ["Road", "Street", "Avenue", "Lane"], "case_insensitive": True},
    {"field": "residential_address", "type": "length_check", "min_length": 10},
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
        {"field": "date_of_advertisement", "type": "regex", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        {"field": "date_of_advertisement", "type": "date_range", "after": "2020-01-01", "before": "2030-12-31"}
    ]},

    # =========================
    # QUALIFICATIONS – ORDINARY LEVEL
    # =========================
    {"type": "and", "rules": [
        {"field": "ordinary_level_exams", "type": "exists"},
        {"field": "ordinary_level_exams", "type": "array_length", "min_length": 1},
        {"field": "ordinary_level_exams.0.subjects", "type": "exists"},
        {"field": "ordinary_level_exams.0.subjects", "type": "array_length", "min_length": 5},
        # Require a pass in English, Maths and another core science or language subject
        {"field": "ordinary_level_exams.*.subjects", "match_field": "subject", "match_value": "Mathematics", "check_field": "grade", "type": "one_of", "values": ['A', 'B', 'C', '1', '2', '3']},
        {"field": "ordinary_level_exams.*.subjects", "match_field": "subject", "match_value": "English Language",
         "check_field": "grade", "type": "one_of", "values": ["1", "2", "3", "A", "B", "C"]}
    ]},

    # =========================
    # QUALIFICATIONS – ADVANCED LEVEL (IF PRESENT)
    # =========================
    {"type": "optional_and", "rules": [
        {"field": "advanced_level_exams", "type": "exists"},
        {"field": "advanced_level_exams", "type": "array_length", "min_length": 1},
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
    {"field": "current_government_employment.start_date", "type": "date_range", "after": "1990-01-01", "optional": True},

    # =========================
    # LEGAL / CONDUCT
    # =========================
    {"field": "investigation_enquiry", "type": "boolean", "value": False},
    {"field": "court_conviction", "type": "boolean", "value": False},
    {"field": "resigned_retired_dismissed", "type": "boolean", "value": False},

    # =========================
    # NEW ADVANCED RULE TYPES
    # =========================
    {"field": "surname", "type": "length_check", "min_length": 2, "max_length": 50},
    {"field": "other_names", "type": "length_check", "min_length": 2, "max_length": 100},
    {"field": "weight", "type": "range", "min": 30, "max": 200, "optional": True},
    {"field": "height", "type": "range", "min": 120, "max": 220, "optional": True},

    # =========================
    # UNSTRUCTURED FIELDS FOR LLM EVALUATION
    # =========================
    {
        "field": "investigation_details",
        "type": "unstructured",
        "description": "Details about any investigation or enquiry",
        "evaluation_criteria": "Assess if the investigation details indicate any serious misconduct or character issues that would disqualify the candidate"
    },
    {
        "field": "conviction_details",
        "type": "unstructured",
        "description": "Details about any court conviction",
        "evaluation_criteria": "Evaluate if the conviction details show serious criminal activity that would make the candidate unsuitable for government employment"
    },
    {
        "field": "resignation_details",
        "type": "unstructured",
        "description": "Details about resignation, retirement, or dismissal from previous employment",
        "evaluation_criteria": "Determine if the resignation/dismissal details indicate poor performance, misconduct, or other issues that would affect suitability"
    },
    {
        "field": "other_qualifications",
        "type": "unstructured",
        "description": "Additional qualifications not captured in structured fields",
        "evaluation_criteria": "Assess if these additional qualifications are relevant and valuable for the applied position"
    },
    {
        "field": "residential_address",
        "type": "unstructured",
        "description": "Candidate's residential address",
        "evaluation_criteria": "Check if the address appears complete and valid for a Mauritian resident"
    }
]

# Fields marked as unstructured for LLM evaluation
unstructured_fields = [
    {
        "field": "investigation_details",
        "description": "Details about any investigation or enquiry",
        "evaluation_criteria": "Assess if the investigation details indicate any serious misconduct or character issues that would disqualify the candidate"
    },
    {
        "field": "conviction_details",
        "description": "Details about any court conviction",
        "evaluation_criteria": "Evaluate if the conviction details show serious criminal activity that would make the candidate unsuitable for government employment"
    },
    {
        "field": "resignation_details",
        "description": "Details about resignation, retirement, or dismissal from previous employment",
        "evaluation_criteria": "Determine if the resignation/dismissal details indicate poor performance, misconduct, or other issues that would affect suitability"
    },
    {
        "field": "other_qualifications",
        "description": "Additional qualifications not captured in structured fields",
        "evaluation_criteria": "Assess if these additional qualifications are relevant and valuable for the applied position"
    },
    {
        "field": "residential_address",
        "description": "Candidate's residential address",
        "evaluation_criteria": "Check if the address appears complete and valid for a Mauritian resident"
    }
]