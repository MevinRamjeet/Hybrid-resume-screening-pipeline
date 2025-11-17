"""
Launcher script for the Gradio UI interface.

Usage:
    python run_ui.py [--host HOST] [--port PORT] [--share] [--debug]

Examples:
    python run_ui.py
    python run_ui.py --port 7861
    python run_ui.py --share
    python run_ui.py --host 0.0.0.0 --port 8080
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui import launch_app


def main():
    """Main entry point for the UI launcher."""
    parser = argparse.ArgumentParser(
        description="Launch the Hybrid Resume Screening Pipeline UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ui.py                          # Launch with default settings
  python run_ui.py --port 7861              # Launch on custom port
  python run_ui.py --share                  # Create public link
  python run_ui.py --host 0.0.0.0           # Listen on all interfaces
  python run_ui.py --debug                  # Enable debug mode
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Server hostname (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Server port (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public shareable link"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Launch the app
    try:
        launch_app(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down UI server...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error launching UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
