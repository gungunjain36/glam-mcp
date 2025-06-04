import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def configure_gemini():
    """Configure Gemini API with environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file")
    genai.configure(api_key=api_key)

def parse_natural_language(prompt: str) -> str:
    """
    Use Gemini API to convert natural language prompt into MCP-compatible prompt.
    Args:
        prompt: Natural language input (e.g., "Cut from 10 to 20 seconds and apply sepia filter")
    Returns:
        MCP prompt (e.g., "trim 10 20; filter sepia")
    """
    configure_gemini()
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Define the instruction for Gemini
    instruction = """
    Convert the following natural language video editing prompt into a structured MCP-compatible prompt.
    Supported operations:
    - trim start end (e.g., trim 10 20 for 10 to 20 seconds)
    - crop w h x y (e.g., crop 300 200 100 50 for width=300, height=200, x=100, y=50)
    - filter name (e.g., filter sepia or filter grayscale)
    Operations are separated by semicolons. Only one trim is allowed.
    Example:
    Input: "Cut from 10 to 20 seconds and apply sepia filter"
    Output: "trim 10 20; filter sepia"
    If the prompt is invalid or unclear, return an empty string.
    Input: {prompt}
    """

    try:
        response = model.generate_content(instruction.format(prompt=prompt))
        mcp_prompt = response.text.strip()
        # Validate the prompt
        if not mcp_prompt or not any(op in mcp_prompt for op in ["trim", "crop", "filter"]):
            raise ValueError("Invalid or empty MCP prompt returned by Gemini")
        return mcp_prompt
    except Exception as e:
        raise ValueError(f"Failed to parse prompt with Gemini: {str(e)}")