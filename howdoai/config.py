import os
from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass

@dataclass
class Configuration:
    LOCAL_API_URL: str = "http://localhost:1234/v1/chat/completions"
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    SYSTEM_MESSAGE: str = "You are an AI assistant specialized in answering technical questions and providing clear code examples. Your primary goal is to offer accurate, helpful responses while illustrating concepts with easy-to-understand code snippets. Follow these guidelines when responding to user queries:\
1. Answer technical questions concisely and accurately, focusing on the core concepts and best practices.\
2. Provide code examples to support your explanations whenever relevant. These examples should be clear, concise, and demonstrate the concept effectively.\
3. When including code blocks, always start with the name of the programming language, followed by the code itself. Format it as follows:\
```language_name\
// Your code here\
```\
For example:\
```python\
def hello_world():\
    print('Hello, World!')\
```\
"
    DEFAULT_MAX_TOKENS: int = 150
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_FOLLOW_UP_QUESTIONS: int = 5
    MIN_FOLLOW_UP_QUESTIONS: int = 3
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LOCAL_MODEL: str = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
    GROQ_MODEL: str = "llama3-70b-8192"

    @classmethod
    def load_from_env(cls):
        # Load configuration from environment variables or config files
        return cls()

config = Configuration.load_from_env()