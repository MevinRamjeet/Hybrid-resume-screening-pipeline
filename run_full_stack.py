"""
Launch both FastAPI server and Gradio UI together.

This script starts both the backend API server and the frontend UI interface
in separate processes for a complete full-stack experience.

Usage:
    python run_full_stack.py
"""
import subprocess
import sys
import time
import signal
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(message: str, color: str = Colors.OKGREEN):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")


def print_banner():
    """Print startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🎯 Hybrid Resume Screening Pipeline - Full Stack Launcher  ║
    ║                                                               ║
    ║   Starting both FastAPI Backend and Gradio Frontend...       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, Colors.HEADER)


def main():
    """Main entry point."""
    print_banner()
    
    # Store process references
    processes = []
    
    try:
        # Start FastAPI server
        print_colored("\n[1/2] 🚀 Starting FastAPI Server...", Colors.OKCYAN)
        print_colored("      URL: http://localhost:8002", Colors.OKBLUE)
        print_colored("      Docs: http://localhost:8002/docs\n", Colors.OKBLUE)
        
        api_process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(("FastAPI Server", api_process))
        
        # Wait for API to start
        print_colored("      Waiting for API to initialize...", Colors.WARNING)
        time.sleep(3)
        
        # Check if API process is still running
        if api_process.poll() is not None:
            print_colored("      ❌ FastAPI server failed to start!", Colors.FAIL)
            stderr = api_process.stderr.read()
            if stderr:
                print_colored(f"      Error: {stderr}", Colors.FAIL)
            return 1
        
        print_colored("      ✅ FastAPI server started successfully!\n", Colors.OKGREEN)
        
        # Start Gradio UI
        print_colored("[2/2] 🎨 Starting Gradio UI...", Colors.OKCYAN)
        print_colored("      URL: http://127.0.0.1:7860\n", Colors.OKBLUE)
        
        ui_process = subprocess.Popen(
            [sys.executable, "run_ui.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(("Gradio UI", ui_process))
        
        # Wait for UI to start
        time.sleep(2)
        
        # Check if UI process is still running
        if ui_process.poll() is not None:
            print_colored("      ❌ Gradio UI failed to start!", Colors.FAIL)
            stderr = ui_process.stderr.read()
            if stderr:
                print_colored(f"      Error: {stderr}", Colors.FAIL)
            return 1
        
        print_colored("      ✅ Gradio UI started successfully!\n", Colors.OKGREEN)
        
        # Print success message
        success_message = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ✅ Full Stack Successfully Launched!                        ║
    ║                                                               ║
    ║   📍 FastAPI Backend:  http://localhost:8002                  ║
    ║   📍 API Docs:         http://localhost:8002/docs             ║
    ║   📍 Gradio Frontend:  http://127.0.0.1:7860                  ║
    ║                                                               ║
    ║   Press Ctrl+C to stop both servers                          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """
        print_colored(success_message, Colors.OKGREEN)
        
        # Keep running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print_colored(f"\n⚠️  {name} has stopped unexpectedly!", Colors.WARNING)
                    return 1
    
    except KeyboardInterrupt:
        print_colored("\n\n🛑 Shutting down servers...", Colors.WARNING)
    
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", Colors.FAIL)
        return 1
    
    finally:
        # Cleanup: terminate all processes
        for name, process in processes:
            if process.poll() is None:  # Process is still running
                print_colored(f"   Stopping {name}...", Colors.OKCYAN)
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print_colored(f"   Force killing {name}...", Colors.WARNING)
                    process.kill()
        
        print_colored("\n👋 All servers stopped. Goodbye!\n", Colors.OKGREEN)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
