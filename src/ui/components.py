"""
UI components for the Gradio interface.
"""
import gradio as gr
from typing import Dict, Any, Optional
import json
from .utils import (
    call_api_endpoint,
    format_evaluation_results,
    format_rules_display,
    validate_json_input,
    create_sample_application
)


def create_header() -> gr.HTML:
    """Create the header component."""
    header_html = """
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em;">🎯 Hybrid Resume Screening Pipeline</h1>
        <p style="color: #f0f0f0; margin-top: 10px; font-size: 1.2em;">
            AI-Powered Application Evaluation System
        </p>
        <p style="color: #e0e0e0; margin-top: 5px;">
            Combines structured rule validation with intelligent LLM analysis
        </p>
    </div>
    """
    return gr.HTML(header_html)


def create_footer() -> gr.HTML:
    """Create the footer component."""
    footer_html = """
    <div style="text-align: center; padding: 15px; margin-top: 30px; border-top: 1px solid #ddd;">
        <p style="color: #666; font-size: 0.9em;">
            💡 <strong>Tip:</strong> Make sure the FastAPI server is running on <code>http://localhost:8000</code>
        </p>
        <p style="color: #888; font-size: 0.8em; margin-top: 5px;">
            Hybrid Resume Screening Pipeline v1.0.0 | Built with FastAPI & Gradio
        </p>
    </div>
    """
    return gr.HTML(footer_html)


async def evaluate_json_application(json_input: str, api_url: str) -> tuple[str, str]:
    """
    Evaluate an application from JSON input.
    
    Args:
        json_input: JSON string containing application data
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (formatted_results, raw_json)
    """
    # Validate JSON
    is_valid, data, error_msg = validate_json_input(json_input)
    if not is_valid:
        return f"❌ **Validation Error**: {error_msg}", ""
    
    # Call API
    results = await call_api_endpoint(
        endpoint="/api/v1/evaluate/json",
        data=data,
        base_url=api_url
    )
    
    # Format results
    formatted = format_evaluation_results(results)
    raw_json = json.dumps(results, indent=2)
    
    return formatted, raw_json


async def evaluate_file_application(file, api_url: str) -> tuple[str, str]:
    """
    Evaluate an application from an uploaded file.
    
    Args:
        file: Uploaded file object
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (formatted_results, raw_json)
    """
    if file is None:
        return "❌ **Error**: No file uploaded", ""
    
    try:
        # Read file content
        with open(file.name, 'rb') as f:
            files = {"file": (file.name.split('/')[-1], f, "application/json")}
            
            # Call API
            results = await call_api_endpoint(
                endpoint="/api/v1/evaluate/file",
                files=files,
                base_url=api_url
            )
        
        # Format results
        formatted = format_evaluation_results(results)
        raw_json = json.dumps(results, indent=2)
        
        return formatted, raw_json
    except Exception as e:
        return f"❌ **Error**: {str(e)}", ""


async def get_evaluation_rules(api_url: str) -> str:
    """
    Fetch and display evaluation rules.
    
    Args:
        api_url: Base URL of the API server
        
    Returns:
        Formatted rules display
    """
    rules_data = await call_api_endpoint(
        endpoint="/api/v1/rules",
        base_url=api_url,
        method="GET"
    )
    
    return format_rules_display(rules_data)


async def get_application_schema(api_url: str) -> str:
    """
    Fetch and display application schema.
    
    Args:
        api_url: Base URL of the API server
        
    Returns:
        Formatted schema JSON
    """
    schema_data = await call_api_endpoint(
        endpoint="/api/v1/schema",
        base_url=api_url,
        method="GET"
    )
    
    if schema_data.get("error"):
        return f"❌ **Error**: {schema_data.get('message', 'Unknown error')}"
    
    return json.dumps(schema_data, indent=2)


def load_sample_application() -> str:
    """Load a sample application for testing."""
    return create_sample_application()


def create_evaluation_tab(api_url_state: gr.State) -> gr.Tab:
    """
    Create the evaluation tab.
    
    Args:
        api_url_state: Gradio state for API URL
        
    Returns:
        Gradio Tab component
    """
    with gr.Tab("📝 Evaluate Application") as tab:
        gr.Markdown("""
        ### Evaluate Job Applications
        Submit application data in JSON format to evaluate against the screening rules.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("#### Input Options")
                
                with gr.Tabs():
                    with gr.Tab("JSON Input"):
                        json_input = gr.Code(
                            label="Application JSON",
                            language="json",
                            lines=20,
                            value=""
                        )
                        
                        with gr.Row():
                            load_sample_btn = gr.Button("📋 Load Sample", variant="secondary", size="sm")
                            clear_btn = gr.Button("🗑️ Clear", variant="secondary", size="sm")
                            evaluate_json_btn = gr.Button("🚀 Evaluate", variant="primary", size="lg")
                    
                    with gr.Tab("File Upload"):
                        file_input = gr.File(
                            label="Upload JSON File",
                            file_types=[".json"],
                            type="filepath"
                        )
                        evaluate_file_btn = gr.Button("🚀 Evaluate File", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("#### Evaluation Results")
                
                with gr.Tabs():
                    with gr.Tab("Formatted Results"):
                        results_output = gr.Markdown(
                            label="Results",
                            value="Results will appear here after evaluation..."
                        )
                    
                    with gr.Tab("Raw JSON"):
                        raw_json_output = gr.Code(
                            label="Raw JSON Response",
                            language="json",
                            lines=20
                        )
        
        # Event handlers
        load_sample_btn.click(
            fn=load_sample_application,
            outputs=json_input
        )
        
        clear_btn.click(
            fn=lambda: "",
            outputs=json_input
        )
        
        evaluate_json_btn.click(
            fn=evaluate_json_application,
            inputs=[json_input, api_url_state],
            outputs=[results_output, raw_json_output]
        )
        
        evaluate_file_btn.click(
            fn=evaluate_file_application,
            inputs=[file_input, api_url_state],
            outputs=[results_output, raw_json_output]
        )
    
    return tab


def create_rules_tab(api_url_state: gr.State) -> gr.Tab:
    """
    Create the rules configuration tab.
    
    Args:
        api_url_state: Gradio state for API URL
        
    Returns:
        Gradio Tab component
    """
    with gr.Tab("📜 Evaluation Rules") as tab:
        gr.Markdown("""
        ### Current Evaluation Rules
        View the structured and unstructured rules used for application screening.
        """)
        
        refresh_rules_btn = gr.Button("🔄 Refresh Rules", variant="primary")
        
        rules_display = gr.Markdown(
            label="Rules Configuration",
            value="Click 'Refresh Rules' to load the current configuration..."
        )
        
        # Event handler
        refresh_rules_btn.click(
            fn=get_evaluation_rules,
            inputs=[api_url_state],
            outputs=rules_display
        )
    
    return tab


def create_schema_tab(api_url_state: gr.State) -> gr.Tab:
    """
    Create the schema reference tab.
    
    Args:
        api_url_state: Gradio state for API URL
        
    Returns:
        Gradio Tab component
    """
    with gr.Tab("📋 Application Schema") as tab:
        gr.Markdown("""
        ### PSCApplication Schema
        View the complete schema for job applications, including all required and optional fields.
        """)
        
        refresh_schema_btn = gr.Button("🔄 Load Schema", variant="primary")
        
        schema_display = gr.Code(
            label="Application Schema (JSON)",
            language="json",
            lines=25,
            value="Click 'Load Schema' to view the application data structure..."
        )
        
        # Event handler
        refresh_schema_btn.click(
            fn=get_application_schema,
            inputs=[api_url_state],
            outputs=schema_display
        )
    
    return tab


def create_settings_tab(api_url_state: gr.State) -> gr.Tab:
    """
    Create the settings tab.
    
    Args:
        api_url_state: Gradio state for API URL
        
    Returns:
        Gradio Tab component
    """
    with gr.Tab("⚙️ Settings") as tab:
        gr.Markdown("""
        ### API Configuration
        Configure the connection to the FastAPI backend server.
        """)
        
        with gr.Row():
            with gr.Column():
                api_url_input = gr.Textbox(
                    label="API Base URL",
                    value="http://localhost:8002",
                    placeholder="http://localhost:8002",
                    info="Base URL of the FastAPI server"
                )
                
                update_url_btn = gr.Button("💾 Update URL", variant="primary")
                status_output = gr.Markdown("Current URL: `http://localhost:8000`")
                
                gr.Markdown("""
                ---
                ### 📖 Quick Start Guide
                
                1. **Start the FastAPI Server**:
                   ```bash
                   python run_server.py
                   ```
                
                2. **Load Sample Data**: Use the "Load Sample" button in the Evaluate tab
                
                3. **Evaluate**: Click "Evaluate" to process the application
                
                4. **View Results**: Check both formatted and raw JSON results
                
                ---
                ### 🔧 Troubleshooting
                
                - **Connection Error**: Ensure the FastAPI server is running
                - **Invalid JSON**: Check your JSON syntax using the sample as reference
                - **Evaluation Failed**: Review the error message in the results panel
                """)
        
        # Event handler
        def update_api_url(new_url: str) -> tuple[str, str]:
            return new_url, f"✅ URL updated to: `{new_url}`"
        
        update_url_btn.click(
            fn=update_api_url,
            inputs=[api_url_input],
            outputs=[api_url_state, status_output]
        )
    
    return tab
