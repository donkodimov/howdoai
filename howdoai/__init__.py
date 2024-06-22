import requests
import json
import sys
import argparse
from typing import Optional, Dict, Any

# Constants
API_URL = "http://localhost:1234/v1/chat/completions"
SYSTEM_MESSAGE = "You are an AI assistant that provides concise, one-line answers with the best example of how to complete a task. If the answer contains code or commands, wrap it in triple backticks (```)."


def truncate_to_word_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = ' '.join(words[:max_words])
    if len(truncated) < len(text):
        truncated += '...'
    return truncated

def call_ai_api(query: str) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query if query else ""}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")

def format_response(answer: str, max_words: Optional[int] = None) -> str:
    if "```" in answer:
        code_start = answer.find("```") + 3
        code_end = answer.find("```", code_start)
        code = answer[code_start:code_end].strip()
        return f"<code>\n{code}\n</code>"
    else:
        if max_words:
            answer = truncate_to_word_limit(answer, max_words)
        return f"<result>{answer}</result>"

def main(query: str, max_words: Optional[int] = None) -> str:
    try:
        result = call_ai_api(query)
        answer = result["choices"][0]["message"]["content"].strip()
        return format_response(answer, max_words)
    except Exception as e:
        return f"Error: {str(e)}"

def main_cli() -> None:
    parser = argparse.ArgumentParser(description='Get concise answers to how-to questions.')
    parser.add_argument('query', nargs='?', help='The question to ask')
    parser.add_argument('--max-words', type=int, help='Maximum number of words in the response')
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    result = main(args.query, args.max_words)
    print(result)

if __name__ == "__main__":
    main_cli()