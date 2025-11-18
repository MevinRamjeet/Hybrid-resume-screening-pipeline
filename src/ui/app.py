"""
Main Gradio application for the Hybrid Resume Screening Pipeline.
"""
import gradio as gr
from .components import (
    create_header,
    create_footer,
    create_evaluation_tab,
    create_rules_tab,
    create_schema_tab,
    create_settings_tab
)
from .rules_editor import create_rules_editor_tab


def create_app() -> gr.Blocks:
    """
    Create and configure the Gradio application.
    
    Returns:
        Configured Gradio Blocks interface
    """
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    
    .tab-nav button {
        font-size: 1.1em;
        padding: 10px 20px;
    }
    
    .markdown-text h1 {
        color: #667eea;
    }
    
    .markdown-text h2 {
        color: #764ba2;
        border-bottom: 2px solid #764ba2;
        padding-bottom: 5px;
    }
    
    .markdown-text h3 {
        color: #667eea;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    
    .success-text {
        color: #10b981;
        font-weight: bold;
    }
    
    .error-text {
        color: #ef4444;
        font-weight: bold;
    }
    """
    
    # Create the main interface
    with gr.Blocks(
        title="Hybrid Resume Screening Pipeline",
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="blue",
        ),
        css=custom_css
    ) as app:
        # State for API URL
        api_url_state = gr.State(value="http://localhost:8002")
        
        # Header
        create_header()
        
        # Main content tabs
        with gr.Tabs():
            create_evaluation_tab(api_url_state)
            create_rules_tab(api_url_state)
            create_rules_editor_tab(api_url_state)
            create_schema_tab(api_url_state)
            create_settings_tab(api_url_state)
        
        # Footer
        create_footer()
    
    return app


def launch_app(
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    share: bool = False,
    debug: bool = False
) -> None:
    """
    Launch the Gradio application.
    
    Args:
        server_name: Server hostname (default: 127.0.0.1)
        server_port: Server port (default: 7860)
        share: Whether to create a public link (default: False)
        debug: Enable debug mode (default: False)
    """
    app = create_app()
    
    print("\n" + "="*60)
    print("🚀 Launching Hybrid Resume Screening Pipeline UI")
    print("="*60)
    print(f"📍 Local URL: http://{server_name}:{server_port}")
    if share:
        print("🌐 Public URL will be generated...")
    print("\n💡 Make sure the FastAPI server is running on http://localhost:8000")
    print("="*60 + "\n")
    
    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    launch_app()
