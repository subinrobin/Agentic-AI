import os
from litellm import completion
from typing import List, Dict

# --- LLM Configuration ---
MODEL_IDENTIFIER = "google/gemma-3-1b"

# Load environment variables (strictly required)
os.environ['OPENAI_API_KEY'] = os.environ["LOCAL_LLM_SERVER_KEY"]
LOCAL_LLM_SERVER_URL = os.environ["LOCAL_LLM_SERVER_URL"]

def generate_response(messages: List[Dict], max_tokens: int = 1024) -> str:
    """
    Call the LLM to get a response using the shared configuration.
    
    Args:
        messages: List of message dictionaries (role, content).
        max_tokens: Maximum number of tokens to generate.
        
    Returns:
        The text content of the assistant's response.
    """
    try:
        response = completion(
            model=f"openai/{MODEL_IDENTIFIER}", 
            messages=messages,
            api_base=f'{LOCAL_LLM_SERVER_URL}/v1',
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n❌ Error calling LLM: {e}")
        return ""
