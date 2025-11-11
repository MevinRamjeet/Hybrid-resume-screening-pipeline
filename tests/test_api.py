#!/usr/bin/env python3
"""
Example client for the Hybrid Resume Screening Pipeline API

This script demonstrates how to interact with the FastAPI server.
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✓ Health check passed")
        print(f"  Response: {response.json()}")
    else:
        print("✗ Health check failed")
        print(f"  Status: {response.status_code}")
    print()


def test_get_rules():
    """Test getting evaluation rules"""
    print("Getting evaluation rules...")
    response = requests.get(f"{BASE_URL}/rules")
    if response.status_code == 200:
        rules_data = response.json()
        print("✓ Rules retrieved successfully")
        print(f"  Total rules: {rules_data['total_rules']}")
        print(f"  Structured rules: {rules_data['structured_count']}")
        print(f"  Unstructured fields: {rules_data['unstructured_count']}")
    else:
        print("✗ Failed to get rules")
        print(f"  Status: {response.status_code}")
    print()


def test_evaluate_sample_application():
    """Test evaluating a sample application"""
    print("Testing application evaluation...")

    # Sample application data
    sample_application = {
        "post_applied_for": "Software Developer",
        "ministry_department": "Ministry of Technology",
        "date_of_advertisement": "2024-01-15",
        "national_identity_no": "12345678901234",
        "surname": "Smith",
        "other_names": "John Michael",
        "residential_address": "123 Main Street, Harare, Zimbabwe",
        "date_of_birth": "1990-05-15",
        "age": 34,
        "place_of_birth": "Harare",
        "nationality": "Zimbabwean",
        "phone_mobile": "+263771234567",
        "email": "john.smith@email.com",
        "degree_qualifications": [
            {
                "level": "degree",
                "institution": "University of Zimbabwe",
                "country": "Zimbabwe",
                "qualification_name": "Bachelor of Science in Computer Science",
                "class_division_level": "Upper Second Class",
                "date_of_result": "2012-11-30",
                "course_type": "full_time",
                "duration_from": "2009-09-01",
                "duration_to": "2012-11-30"
            }
        ],
        "ordinary_level_exams": [
            {
                "exam_type": "Cambridge G.C.E.",
                "month_year": "November 2005",
                "subjects": [
                    {"subject": "Mathematics", "grade": "A"},
                    {"subject": "English Language", "grade": "B"},
                    {"subject": "Physics", "grade": "A"},
                    {"subject": "Chemistry", "grade": "B"},
                    {"subject": "Computer Science", "grade": "A"}
                ],
                "result": "Pass"
            }
        ],
        "investigation_enquiry": False,
        "court_conviction": False,
        "resigned_retired_dismissed": False,
        "other_qualifications": [
            "Certified Scrum Master",
            "AWS Cloud Practitioner"
        ]
    }

    # Send evaluation request
    response = requests.post(
        f"{BASE_URL}/evaluate/json",
        json=sample_application,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print("✓ Application evaluation completed")
        print(f"  Overall Result: {'PASSED' if result['overall_passed'] else 'FAILED'}")
        print(f"  Overall Score: {result['overall_score']:.2%}")
        print(f"  Structured Evaluation: {'PASSED' if result['summary']['structured_passed'] else 'FAILED'}")
        print(f"  Unstructured Evaluation: {'PASSED' if result['summary']['unstructured_passed'] else 'FAILED'}")
        print(f"  Timestamp: {result['timestamp']}")
    else:
        print("✗ Application evaluation failed")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
    print()


def test_file_upload():
    """Test file upload evaluation"""
    print("Testing file upload evaluation...")

    # Create a sample JSON file
    sample_data = {
        "post_applied_for": "Data Analyst",
        "surname": "Johnson",
        "other_names": "Alice",
        "age": 28,
        "nationality": "Zimbabwean",
        "degree_qualifications": [
            {
                "level": "degree",
                "qualification_name": "Bachelor of Mathematics",
                "institution": "University of Cape Town"
            }
        ],
        "investigation_enquiry": False,
        "court_conviction": False
    }

    # Save to temporary file
    with open("temp_application.json", "w") as f:
        json.dump(sample_data, f, indent=2)

    try:
        # Upload file
        with open("temp_application.json", "rb") as f:
            files = {"file": ("temp_application.json", f, "application/json")}
            response = requests.post(f"{BASE_URL}/evaluate/file", files=files)

        if response.status_code == 200:
            result = response.json()
            print("✓ File upload evaluation completed")
            print(f"  Overall Result: {'PASSED' if result['overall_passed'] else 'FAILED'}")
            print(f"  Source File: {result.get('source_file', 'Unknown')}")
        else:
            print("✗ File upload evaluation failed")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")

    finally:
        # Clean up temporary file
        import os
        if os.path.exists("temp_application.json"):
            os.remove("temp_application.json")

    print()


def main():
    """Run all API tests"""
    print("=" * 60)
    print("HYBRID RESUME SCREENING PIPELINE - API CLIENT TEST")
    print("=" * 60)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with: python run_server.py")
    print("=" * 60)
    print()

    try:
        test_health_check()
        test_get_rules()
        test_evaluate_sample_application()
        test_file_upload()

        print("=" * 60)
        print("API testing completed!")
        print("Visit http://localhost:8000/docs for interactive API documentation")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the API server")
        print("  Make sure the server is running: python run_server.py")
    except Exception as e:
        print(f"✗ Error during testing: {e}")


if __name__ == "__main__":
    main()
