import sys
import argparse
from typing import Optional, Dict, Any, List
import random
import time
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .api_client import call_ai_api, AIResponse, AIRequestError
from .config import LOCAL_API_URL, GROQ_API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from .progressbarmanager import ProgressBarManager
from .questionanswerer import QuestionAnswerer

# Constants
MAX_FOLLOW_UP_QUESTIONS = 5
MIN_FOLLOW_UP_QUESTIONS = 3

# Initialize Rich console
console = Console()    

def main(query: str, max_words: Optional[int] = None, use_groq: bool = False, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    start_time = time.time()
    
    with ProgressBarManager(console) as progress_manager:
        try:
            questionanswerer = QuestionAnswerer(progress_manager)
            answer, task_id = questionanswerer.generate_answer(query, use_groq, max_tokens)
            formatted_answer = questionanswerer.process_answer(answer, max_words)
            follow_up_questions = questionanswerer.generate_follow_up_questions(query, answer, use_groq, max_tokens)
                    
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