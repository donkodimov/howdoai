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

# Constants
MAX_FOLLOW_UP_QUESTIONS = 5
MIN_FOLLOW_UP_QUESTIONS = 3

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

def generate_follow_up_questions(initial_query: str, initial_response: str, progress: Progress, task: int, use_groq: bool = False) -> List[str]:
    try:
        prompt = f"""
        Based on the following question and answer, generate 5 relevant follow-up questions:

        Question: {initial_query}
        Answer: {initial_response}

        Follow-up questions:
        1.
        """

        progress.update(task, advance=10, description="[blue]Preparing follow-up request...")
        response = call_ai_api(prompt, use_groq)
        progress.update(task, advance=50, description="[blue]Processing follow-up response...")
        generated_text = response.content
        questions = [q.strip() for q in generated_text.split('\n') if q.strip().endswith('?')]

        progress.update(task, advance=20, description="[blue]Finalizing follow-up questions...")
        while len(questions) < MIN_FOLLOW_UP_QUESTIONS:
            questions.append(f"Can you elaborate more on {random.choice(['the topic', 'this subject', 'this area', 'this concept'])}?")

        progress.update(task, advance=20, description="[blue]Follow-up questions generated")
        return questions[:MAX_FOLLOW_UP_QUESTIONS]
    except Exception as e:
        raise AIRequestError(f"Error generating follow-up questions: {str(e)}")

def main(query: str, max_words: Optional[int] = None, use_groq: bool = False, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        try:
            task1 = progress.add_task("[green]Generating answer...", total=100)
            
            # Simulating steps in API call and response processing
            progress.update(task1, advance=10, description="[green]Preparing API request...")
            time.sleep(0.5)  # Simulating network delay
            progress.update(task1, advance=20, description="[green]Sending request to AI...")
            result = call_ai_api(query, use_groq, max_tokens)
            progress.update(task1, advance=40, description="[green]Processing AI response...")
            answer = result.content.strip()
            progress.update(task1, advance=20, description="[green]Formatting answer...")
            formatted_answer = format_response(answer, max_words)
            progress.update(task1, completed=100, description="[green]Answer generated")
            
            task2 = progress.add_task("[blue]Generating follow-up questions...", total=100)
            try:
                follow_up_questions = generate_follow_up_questions(query, answer, progress, task2, use_groq)
            except AIRequestError as e:
                progress.update(task2, completed=100, description="[blue]Error in follow-up questions")
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