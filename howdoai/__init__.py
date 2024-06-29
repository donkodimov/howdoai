import sys
import argparse
from typing import Optional, Dict, Any, List
import random
import time
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .api_client import call_ai_api, AIResponse, AIRequestError
from .config import LOCAL_API_URL, GROQ_API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

# Constants
MAX_FOLLOW_UP_QUESTIONS = 5
MIN_FOLLOW_UP_QUESTIONS = 3
start_time = time.time()

# Initialize Rich console
console = Console()

def truncate_to_word_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = ' '.join(words[:max_words])
    if len(truncated) < len(text):
        truncated += '...'
    return truncated

def format_response(answer: str, max_words: Optional[int] = None) -> str:
    if max_words:
        answer = truncate_to_word_limit(answer, max_words)
    
    # Ensure code blocks start on a new line
    answer = answer.replace("```", "\n```")
    
    return answer

def generate_follow_up_questions(initial_query: str, initial_response: str, use_groq: bool = False) -> List[str]:
    try:
        prompt = f"""
        Based on the following question and answer, generate 5 relevant follow-up questions:

        Question: {initial_query}
        Answer: {initial_response}

        Follow-up questions:
        1.
        """

        response = call_ai_api(prompt, use_groq)
        generated_text = response.content
        questions = [q.strip() for q in generated_text.split('\n') if q.strip().endswith('?')]

        while len(questions) < MIN_FOLLOW_UP_QUESTIONS:
            questions.append(f"Can you elaborate more on {random.choice(['the topic', 'this subject', 'this area', 'this concept'])}?")

        return questions[:MAX_FOLLOW_UP_QUESTIONS]
    except Exception as e:
        raise AIRequestError(f"Error generating follow-up questions: {str(e)}")

def main(query: str, max_words: Optional[int] = None, use_groq: bool = False, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    try:
        result = call_ai_api(query, use_groq, max_tokens)
        answer = result.content.strip()
        
        formatted_answer = format_response(answer, max_words)
        
        try:
            follow_up_questions = generate_follow_up_questions(query, answer, use_groq)
        except AIRequestError as e:
            return {"error": f"Error generating follow-up questions: {str(e)}"}
        
        return {
            "answer": formatted_answer,
            "follow_up_questions": follow_up_questions,
            "execution_time": f"{time.time() - start_time:.2f} seconds",
            "max_tokens": max_tokens if max_tokens else "DEFAULT_MAX_TOKENS"
        }
    except AIRequestError as e:
        return {"error": f"Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main_cli() -> None:
    parser = argparse.ArgumentParser(description='Get concise answers to how-to questions.')
    parser.add_argument('query', nargs='?', help='The question to ask')
    parser.add_argument('--max-words', type=int, help='Maximum number of words in the response')
    parser.add_argument('--groq', '-g', action='store_true', help='Use Groq API endpoint')
    parser.add_argument('--max-tokens', '-t', type=int, help='Maximum number of tokens for the API request')
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    result = main(args.query, args.max_words, args.groq, args.max_tokens)
    if "error" in result:
        console.print(Panel(result["error"], title="Error", border_style="red"))
    else:
        console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))
        
        if result["follow_up_questions"]:
            console.print("\n[bold]Follow-up questions:[/bold]")
            for i, question in enumerate(result["follow_up_questions"], 1):
                console.print(f"{question}")
        console.print(f"\n[italic]Execution time: {result['execution_time']}[/italic]")
        
        if args.groq:
            console.print("[bold blue]Using Groq API endpoint[/bold blue]")
        else:
            console.print("[bold green]Using local API endpoint[/bold green]")

if __name__ == "__main__":
    main_cli()