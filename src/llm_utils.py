import os
from litellm import completion
from typing import List, Dict

# --- LLM Configuration ---
MODEL_IDENTIFIER = "google/gemma-3-1b"

# Load environment variables (strictly required)
os.environ['OPENAI_API_KEY'] = os.environ["LOCAL_LLM_SERVER_KEY"]
LOCAL_LLM_SERVER_URL = os.environ["LOCAL_LLM_SERVER_URL"]

def call_llm(messages: List[Dict], max_tokens: int = 1024, tools: List[Dict] = None):
    """
    Call the LLM and return the full response object.
    
    Args:
        messages: List of message dictionaries.
        max_tokens: Maximum tokens to generate.
        tools: Optional list of tools for function calling.
        
    Returns:
        The full LiteLLM response object.
    """
    return completion(
        model=f"openai/{MODEL_IDENTIFIER}", 
        messages=messages,
        api_base=f'{LOCAL_LLM_SERVER_URL}/v1',
        max_tokens=max_tokens,
        tools=tools
    )

def generate_response(messages: List[Dict], max_tokens: int = 1024) -> str:
    """
    Call the LLM and return only the text content.
    """
    try:
        response = call_llm(messages, max_tokens)
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n❌ Error calling LLM: {e}")
        return ""