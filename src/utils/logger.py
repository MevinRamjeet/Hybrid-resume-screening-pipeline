import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app_name = os.getenv("APP_NAME", "default_app")
log_filename = os.getenv("LOG_FILE", "app.log")  # Default filename if not set
log_level = os.getenv("LOG_LEVEL", "INFO")
logging_levels = {
"CRITICAL" : 50,
"FATAL" : 50,
"ERROR" : 40,
'WARNING' : 30,
"WARN" : 50,
"INFO" : 20,
"DEBUG" : 10,
"NOTSET" : 0,
}

def setup_logger(name=app_name, log_file=log_filename, level=logging_levels[log_level]):
    """
    Create a comprehensive logger with multiple handlers.

    Features:
    - Console output
    - File logging with rotation
    - Structured logging
    """
    # Get the root project directory
    project_root = Path(__file__).resolve().parent

    # Construct log file path
    log_path = project_root / log_file

    # Ensure log directory exists
    log_dir = log_path.parent  # Extract directory path from log file path
    log_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers (avoid duplicate logs)
    logger.handlers.clear()

    # Console Handler with Line Number
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # File Handler with Rotation
    file_handler = RotatingFileHandler(
        log_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB rotation
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Logger instance
configured_logger = setup_logger()
