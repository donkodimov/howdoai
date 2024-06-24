import sys
import argparse
from typing import Optional, Dict, Any, List
import random
from dataclasses import dataclass

from .api_client import call_ai_api
from .config import API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

# Constants
MAX_FOLLOW_UP_QUESTIONS = 5
MIN_FOLLOW_UP_QUESTIONS = 3


@dataclass
class AIResponse:
    content: str


class AIRequestError(Exception):
    pass


def truncate_to_word_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = ' '.join(words[:max_words])
    if len(truncated) < len(text):
        truncated += '...'
    return truncated


def format_response(answer: str, max_words: Optional[int] = None) -> str:
    if "```" in answer:
        code_start = answer.find("```") + 3
        code_end = answer.rfind("```")
        if code_end > code_start:
            code = answer[code_start:code_end].strip()
            return f"<code>\n{code}\n</code>"
    if max_words:
        answer = truncate_to_word_limit(answer, max_words)
    return f"<result>{answer}</result>"



def generate_follow_up_questions(initial_query: str, initial_response: str) -> List[str]:
    try:
        prompt = f"""
        Based on the following question and answer, generate 5 relevant follow-up questions:

        Question: {initial_query}
        Answer: {initial_response}

        Follow-up questions:
        1.
        """

        response = call_ai_api(prompt)
        generated_text = response.content
        questions = [q.strip() for q in generated_text.split('\n') if q.strip().endswith('?')]

        while len(questions) < MIN_FOLLOW_UP_QUESTIONS:
            questions.append(f"Can you elaborate more on {random.choice(['the topic', 'this subject', 'this area', 'this concept'])}?")

        return questions[:MAX_FOLLOW_UP_QUESTIONS]
    except Exception as e:
        raise AIRequestError(f"Error generating follow-up questions: {str(e)}")



def main(query: str, max_words: Optional[int] = None) -> Dict[str, Any]:

    try:
        result = call_ai_api(query)
        answer = result.content.strip()
        formatted_answer = format_response(answer, max_words)
        
        try:
            follow_up_questions = generate_follow_up_questions(query, answer)
        except AIRequestError as e:
            return {"error": f"Error generating follow-up questions: {str(e)}"}
        
        return {
            "answer": formatted_answer,
            "follow_up_questions": follow_up_questions
        }
    except AIRequestError as e:
        return {"error": f"Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main_cli() -> None:
    """
    Command-line interface for getting concise answers to how-to questions.

    Usage:
        python __init__.py [query] [--max-words MAX_WORDS]

    Arguments:
        query (str, optional): The question to ask.
        --max-words (int, optional): Maximum number of words in the response.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Get concise answers to how-to questions.')
    parser.add_argument('query', nargs='?', help='The question to ask')
    parser.add_argument('--max-words', type=int, help='Maximum number of words in the response')
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    result = main(args.query, args.max_words)
    if "error" in result:
        print(result["error"])
    else:
        print(result["answer"])
        
        if result["follow_up_questions"]:
            print("\nFollow-up questions:")
            for i, question in enumerate(result["follow_up_questions"], 1):
                print(f"{i}. {question}")


if __name__ == "__main__":
    main_cli()
