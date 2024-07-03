import sys
import argparse
from typing import Optional, Dict, Any, List
import time
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .api_client import AIRequestError, call_ai_api
from .config import config
from .progressbarmanager import ProgressBarManager
from .questionanswerer import QuestionAnswerer

# Constants
MAX_FOLLOW_UP_QUESTIONS = config.MAX_FOLLOW_UP_QUESTIONS
MIN_FOLLOW_UP_QUESTIONS = config.MIN_FOLLOW_UP_QUESTIONS

# Initialize Rich console
console = Console()    

def main(query: str, max_words: Optional[int] = None, use_groq: bool = False, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    """
    Executes the main logic of the program.

    Args:
        query (str): The query string to be processed.
        max_words (Optional[int], optional): The maximum number of words in the formatted answer. Defaults to None.
        use_groq (bool, optional): Flag indicating whether to use GROQ for answer generation. Defaults to False.
        max_tokens (Optional[int], optional): The maximum number of tokens for answer generation. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing the answer, follow-up questions, execution time, and max tokens used (if applicable).
            - answer (str): The formatted answer.
            - follow_up_questions (List[str]): A list of follow-up questions.
            - execution_time (str): The execution time in seconds.
            - max_tokens (Union[int, str]): The max tokens used or "DEFAULT_MAX_TOKENS" if not specified.
            - error (str): An error message if an exception occurs during execution.
    """
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
    """
    Command-line interface for getting concise answers to how-to questions.
    
    This function parses command-line arguments, calls the main function with the provided arguments,
    and prints the result to the console.
    """
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