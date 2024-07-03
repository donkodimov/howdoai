import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .config import config

# Define all constants from the config class
SYSTEM_MESSAGE = config.SYSTEM_MESSAGE
DEFAULT_MAX_TOKENS = config.DEFAULT_MAX_TOKENS
DEFAULT_TEMPERATURE = config.DEFAULT_TEMPERATURE
GROQ_API_KEY = config.GROQ_API_KEY
LOCAL_MODEL = config.LOCAL_MODEL
GROQ_MODEL = config.GROQ_MODEL
LOCAL_API_URL = config.LOCAL_API_URL
GROQ_API_URL = config.GROQ_API_URL

@dataclass
class AIResponse:
    content: str

class AIRequestError(Exception):
    pass

def call_ai_api(query: str, use_groq: bool = False, max_tokens: Optional[int] = None) -> AIResponse:
    """
    Calls the AI API with the given query and returns the AI response.

    Args:
        query (str): The user's query to be sent to the AI API.
        use_groq (bool): Whether to use the Groq API endpoint.
        max_tokens (Optional[int]): Maximum number of tokens for the API request.

    Returns:
        AIResponse: The response from the AI API.

    Raises:
        AIRequestError: If the API request fails.
    """
    if use_groq:
        api_url = GROQ_API_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        model = GROQ_MODEL
    else:
        api_url = LOCAL_API_URL
        headers = {"Content-Type": "application/json"}
        model = LOCAL_MODEL

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query if query else ""}
        ],
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS,
        "stream": False
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return AIResponse(content=result["choices"][0]["message"]["content"])
    except requests.exceptions.RequestException as e:
        raise AIRequestError(f"API request failed: {str(e)}")