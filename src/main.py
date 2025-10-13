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
