import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import configured_logger
except ImportError:
    import logging
    configured_logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
TEXT_GENERATION_MODEL = "gpt-4o-mini"
openai_api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")

openai_client = OpenAI(api_key=openai_api_key)


def call_llm(messages, temperature=0.0):
    try:
        r = openai_client.chat.completions.create(
            model=TEXT_GENERATION_MODEL,
            temperature=temperature,
            messages=messages
        )
        return r.choices[0].message.content
    except Exception as e:
        configured_logger.error(f"Error calling LLM: {e}")
        return None
