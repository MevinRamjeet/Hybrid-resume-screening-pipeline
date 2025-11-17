"""
Demo script showing how to use the UI utilities programmatically.

This demonstrates how to integrate the UI utilities into your own applications
without launching the full Gradio interface.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.utils import (
    call_api_endpoint,
    format_evaluation_results,
    create_sample_application,
    validate_json_input
)


async def demo_json_evaluation():
    """Demonstrate evaluating an application via JSON."""
    print("\n" + "="*60)
    print("Demo 1: Evaluate Application via JSON")
    print("="*60)
    
    # Create sample application
    sample_json = create_sample_application()
    print("\n📄 Sample Application Created:")
    print(sample_json[:200] + "...")
    
    # Validate JSON
    is_valid, data, error = validate_json_input(sample_json)
    if not is_valid:
        print(f"❌ Validation Error: {error}")
        return
    
    print("✅ JSON is valid")
    
    # Call API
    print("\n🚀 Calling API endpoint...")
    results = await call_api_endpoint(
        endpoint="/api/v1/evaluate/json",
        data=data,
        base_url="http://localhost:8000"
    )
    
    if results.get("error"):
        print(f"❌ API Error: {results.get('message')}")
        return
    
    # Format and display results
    print("\n📊 Evaluation Results:")
    print("-" * 60)
    formatted = format_evaluation_results(results)
    print(formatted)


async def demo_rules_retrieval():
    """Demonstrate retrieving evaluation rules."""
    print("\n" + "="*60)
    print("Demo 2: Retrieve Evaluation Rules")
    print("="*60)
    
    print("\n🚀 Fetching rules from API...")
    rules_data = await call_api_endpoint(
        endpoint="/api/v1/rules",
        base_url="http://localhost:8000"
    )
    
    if rules_data.get("error"):
        print(f"❌ API Error: {rules_data.get('message')}")
        return
    
    print("\n📜 Rules Summary:")
    print(f"  Total Rules: {rules_data.get('total_rules', 0)}")
    print(f"  Structured Rules: {rules_data.get('structured_count', 0)}")
    print(f"  Unstructured Fields: {rules_data.get('unstructured_count', 0)}")
    
    # Show first few structured rules
    structured_rules = rules_data.get('structured_rules', [])
    if structured_rules:
        print("\n📋 First 3 Structured Rules:")
        for i, rule in enumerate(structured_rules[:3], 1):
            print(f"  {i}. {rule.get('field', 'N/A')} - Type: {rule.get('type', 'N/A')}")


async def demo_schema_retrieval():
    """Demonstrate retrieving application schema."""
    print("\n" + "="*60)
    print("Demo 3: Retrieve Application Schema")
    print("="*60)
    
    print("\n🚀 Fetching schema from API...")
    schema_data = await call_api_endpoint(
        endpoint="/api/v1/schema",
        base_url="http://localhost:8000"
    )
    
    if schema_data.get("error"):
        print(f"❌ API Error: {schema_data.get('message')}")
        return
    
    print("\n📋 Schema Properties:")
    properties = schema_data.get('properties', {})
    print(f"  Total Fields: {len(properties)}")
    print(f"\n  Sample Fields:")
    for i, (field_name, field_info) in enumerate(list(properties.items())[:5], 1):
        field_type = field_info.get('type', 'N/A')
        print(f"    {i}. {field_name}: {field_type}")


async def demo_custom_application():
    """Demonstrate evaluating a custom application."""
    print("\n" + "="*60)
    print("Demo 4: Evaluate Custom Application")
    print("="*60)
    
    # Create a custom application (this one will fail some rules)
    custom_app = {
        "post_applied_for": "Data Scientist",
        "ministry_department": "Ministry of ICT",
        "date_of_advertisement": "2024-01-15",
        "national_identity_no": "M9876543210987",
        "surname": "Smith",
        "other_names": "Jane",
        "residential_address": "456 Main Street, Curepipe",
        "date_of_birth": "1990-03-20",
        "age": 34,
        "nationality": "Mauritian",
        "phone_mobile": "57654321",
        "email": "jane.smith@example.com",
        "ordinary_level_exams": [
            {
                "examination": "Cambridge O-Level",
                "year": 2006,
                "subjects": [
                    {"subject": "Mathematics", "grade": "B"},
                    {"subject": "English Language", "grade": "A"},
                    {"subject": "Physics", "grade": "B"},
                    {"subject": "Chemistry", "grade": "C"},
                    {"subject": "French", "grade": "B"}
                ]
            }
        ],
        "degree_qualifications": [
            {
                "qualification": "MSc Data Science",
                "institution": "University of Mauritius",
                "country": "Mauritius",
                "year_obtained": 2015
            }
        ],
        "other_employment": [
            {
                "employer": "Analytics Corp",
                "position": "Data Analyst",
                "start_date": "2015-09-01",
                "end_date": "2023-12-31",
                "duties": "Data analysis and visualization"
            }
        ],
        "investigation_enquiry": False,
        "court_conviction": False,
        "resigned_retired_dismissed": False
    }
    
    print("\n📄 Custom Application:")
    print(f"  Applicant: {custom_app['surname']} {custom_app['other_names']}")
    print(f"  Position: {custom_app['post_applied_for']}")
    print(f"  Age: {custom_app['age']}")
    
    # Evaluate
    print("\n🚀 Evaluating application...")
    results = await call_api_endpoint(
        endpoint="/api/v1/evaluate/json",
        data=custom_app,
        base_url="http://localhost:8000"
    )
    
    if results.get("error"):
        print(f"❌ API Error: {results.get('message')}")
        return
    
    # Show summary
    print("\n📊 Quick Summary:")
    print(f"  Overall Result: {'✅ PASSED' if results.get('overall_passed') else '❌ FAILED'}")
    print(f"  Overall Score: {results.get('overall_score', 0):.1%}")
    
    summary = results.get('summary', {})
    print(f"  Structured Passed: {summary.get('structured_passed', 'N/A')}")
    print(f"  Unstructured Passed: {summary.get('unstructured_passed', 'N/A')}")
    print(f"  Failed Rules: {summary.get('failed_structured_rules', 0)}")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("🎯 Hybrid Resume Screening Pipeline - UI Utils Demo")
    print("="*60)
    print("\n⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    print("   Start it with: python run_server.py")
    
    input("\nPress Enter to continue...")
    
    try:
        # Run demos
        await demo_json_evaluation()
        input("\nPress Enter for next demo...")
        
        await demo_rules_retrieval()
        input("\nPress Enter for next demo...")
        
        await demo_schema_retrieval()
        input("\nPress Enter for next demo...")
        
        await demo_custom_application()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        print("\n💡 Tip: You can use these utilities in your own Python scripts")
        print("   to integrate with the screening pipeline programmatically.")
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the FastAPI server is running!")


if __name__ == "__main__":
    asyncio.run(main())
