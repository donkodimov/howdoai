import requests
from typing import Dict, Any
from dataclasses import dataclass
from .config import API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

@dataclass
class AIResponse:
    content: str

class AIRequestError(Exception):
    pass

def call_ai_api(query: str) -> AIResponse:
    """
    Calls the AI API with the given query and returns the AI response.

    Args:
        query (str): The user's query to be sent to the AI API.

    Returns:
        AIResponse: The response from the AI API.

    Raises:
        AIRequestError: If the API request fails.
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query if query else ""}
        ],
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return AIResponse(content=result["choices"][0]["message"]["content"])
    except requests.exceptions.RequestException as e:
        raise AIRequestError(f"API request failed: {str(e)}")