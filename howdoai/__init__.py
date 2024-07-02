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

def generate_follow_up_questions(initial_query: str, initial_response: str, progress_manager: ProgressBarManager, use_groq: bool = False) -> List[str]:
    try:
        prompt = f"""
        Based on the following question and answer, generate 5 relevant follow-up questions:

        Question: {initial_query}
        Answer: {initial_response}

        Follow-up questions:
        1.
        """
        task = progress_manager.start_progress("[blue]Generating follow-up questions...")
        progress_manager.update_progress(task, 10, "[blue]Preparing follow-up request...")
        response = call_ai_api(prompt, use_groq)
        progress_manager.update_progress(task, 50, "[blue]Processing follow-up response...")
        generated_text = response.content
        questions = [q.strip() for q in generated_text.split('\n') if q.strip().endswith('?')]

        progress_manager.update_progress(task, 20, "[blue]Finalizing follow-up questions...")
        while len(questions) < MIN_FOLLOW_UP_QUESTIONS:
            questions.append(f"Can you elaborate more on {random.choice(['the topic', 'this subject', 'this area', 'this concept'])}?")

        progress_manager.complete_progress(task, "[blue]Follow-up questions generated")
        return questions[:MAX_FOLLOW_UP_QUESTIONS]
    except Exception as e:
        raise AIRequestError(f"Error generating follow-up questions: {str(e)}")
    
def generate_answer(query: str, use_groq: bool, max_tokens: Optional[int], progress_manager: ProgressBarManager) -> str:
    # Logic for generating the answer
    task1 = progress_manager.start_progress("Generating answer...")
    # Simulating steps in API call and response processing
    progress_manager.update_progress(task1, 10, "[green]Preparing API request...")
    time.sleep(0.5)  # Simulating network delay
    progress_manager.update_progress(task1, 20, "[green]Sending request to AI...")
    result = call_ai_api(query, use_groq, max_tokens)
    progress_manager.update_progress(task1, 40, "[green]Processing AI response...")
    answer = result.content.strip()
    return answer, task1
      


def process_answer(answer: str, task_id: int, max_words: Optional[int], progress_manager: ProgressBarManager) -> str:
    # Logic for processing and formatting the answer  
    progress_manager.update_progress(task_id, 10, "[green]Formatting answer...")
    formatted_answer = format_response(answer, max_words)
    progress_manager.complete_progress(task_id, "[green]Answer generated")  
    return formatted_answer
    

def main(query: str, max_words: Optional[int] = None, use_groq: bool = False, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    start_time = time.time()
    
    with ProgressBarManager(console) as progress_manager:
        try:
            questionanswerer = QuestionAnswerer(progress_manager)
            answer, task_id = questionanswerer.generate_answer(query, use_groq, max_tokens)
            formatted_answer = questionanswerer.process_answer(answer, max_words)
            follow_up_questions = generate_follow_up_questions(query, answer, progress_manager, use_groq)
                    
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