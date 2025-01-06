import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
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
    """
    Represents the response from the AI API.

    Attributes:
        content (str): The content of the response.
    """
    content: str
    follow_up_questions: List[str] = field(default_factory=list)
    task_id: Optional[str] = None
    execution_time: Optional[float] = None

class AIRequestError(Exception):
    """
    Exception raised for errors that occur during AI requests.

    Attributes:
        message -- explanation of the error
        error_type -- type of error (connection, timeout, rate_limit, etc.)
        status_code -- HTTP status code if available
        suggestion -- suggested resolution for the error
    """
    def __init__(self, message, error_type="api_error", status_code=None, suggestion=None):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.suggestion = suggestion
        super().__init__(self.message)

def call_ai_api(query: str, use_groq: bool = False, max_tokens: Optional[int] = None, retries: int = 3) -> AIResponse:
    """
    Calls the AI API with the given query and returns the AI response.

    Args:
        query (str): The user's query to be sent to the AI API.
        use_groq (bool): Whether to use the Groq API endpoint.
        max_tokens (Optional[int]): Maximum number of tokens for the API request.
        retries (int): Number of retry attempts for transient failures.

    Returns:
        AIResponse: The response from the AI API.

    Raises:
        AIRequestError: If the API request fails.
    """
    if use_groq:
        if not GROQ_API_KEY:
            raise AIRequestError(
                "Groq API key is required but not found",
                error_type="configuration_error",
                suggestion="Please set the GROQ_API_KEY environment variable"
            )
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

    last_exception = None
    for attempt in range(retries):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=(3.05, 30)  # Connect timeout, read timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            result = response.json()
            return AIResponse(content=result["choices"][0]["message"]["content"])
            
        except requests.exceptions.Timeout as e:
            last_exception = AIRequestError(
                "Request timed out",
                error_type="timeout",
                suggestion="Please check your internet connection and try again"
            )
        except requests.exceptions.ConnectionError as e:
            last_exception = AIRequestError(
                "Connection error occurred",
                error_type="connection_error",
                suggestion="Please check your internet connection and API endpoint availability"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            error_message = str(e)
            
            if status_code == 401:
                error_message = "Invalid API key"
                suggestion = "Please verify your API key is correct"
            elif status_code == 403:
                error_message = "Access denied"
                suggestion = "Please check your API permissions"
            elif status_code == 429:
                error_message = "Rate limit exceeded"
                suggestion = "Please wait before making more requests"
            elif status_code >= 500:
                error_message = "Server error occurred"
                suggestion = "Please try again later"
                
            last_exception = AIRequestError(
                f"API request failed: {error_message}",
                error_type="http_error",
                status_code=status_code,
                suggestion=suggestion
            )
        except ValueError as e:  # JSON decode error
            last_exception = AIRequestError(
                "Invalid response from API",
                error_type="invalid_response",
                suggestion="Please check the API endpoint configuration"
            )
        except Exception as e:
            last_exception = AIRequestError(
                f"Unexpected error: {str(e)}",
                error_type="unexpected_error"
            )
            
        # Exponential backoff before retry
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    
    # If we've exhausted all retries, raise the last exception
    raise last_exception