import requests
from typing import Dict, Any
from dataclasses import dataclass
from .config import LOCAL_API_URL, GROQ_API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, GROQ_API_KEY, LOCAL_MODEL, GROQ_MODEL

@dataclass
class AIResponse:
    content: str

class AIRequestError(Exception):
    pass

def call_ai_api(query: str, use_groq: bool = False) -> AIResponse:
    """
    Calls the AI API with the given query and returns the AI response.

    Args:
        query (str): The user's query to be sent to the AI API.
        use_groq (bool): Whether to use the Groq API endpoint.

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
        "max_tokens": DEFAULT_MAX_TOKENS,
        "stream": False
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return AIResponse(content=result["choices"][0]["message"]["content"])
    except requests.exceptions.RequestException as e:
        raise AIRequestError(f"API request failed: {str(e)}")