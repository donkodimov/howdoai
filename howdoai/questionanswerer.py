from typing import Optional
import time
import random
from .progressbarmanager import ProgressBarManager
from .api_client import call_ai_api, AIRequestError

from .config import config


# Constants
MAX_FOLLOW_UP_QUESTIONS = config.MAX_FOLLOW_UP_QUESTIONS
MIN_FOLLOW_UP_QUESTIONS = config.MIN_FOLLOW_UP_QUESTIONS

class QuestionAnswerer:
    """
    A class that generates answers to questions and generates follow-up questions based on a given question and answer.

    Args:
        progress_manager (ProgressBarManager): An instance of the ProgressBarManager class.

    Attributes:
        progress_manager (ProgressBarManager): An instance of the ProgressBarManager class.
        task_id (Optional[int]): The ID of the current task.

    Methods:
        generate_answer: Generates an answer to a given question.
        process_answer: Processes the generated answer.
        format_response: Formats the answer.
        truncate_to_word_limit: Truncates the text to a specified word limit.
        generate_follow_up_questions: Generates follow-up questions based on a given question and answer.
    """

    def __init__(self, progress_manager: ProgressBarManager):
        self.progress_manager = progress_manager
        self.task_id = None

    def generate_answer(self, query: str, use_groq: bool, max_tokens: Optional[int]) -> str:
        """
        Generates an answer to a given question.

        Args:
            query (str): The question to generate an answer for.
            use_groq (bool): Flag indicating whether to use GROQ for generating the answer.
            max_tokens (Optional[int]): The maximum number of tokens for the generated answer.

        Returns:
            str: The generated answer.
        """
        self.task_id = self.progress_manager.start_progress("Generating answer...")
        # Logic for generating the answer
        self.progress_manager.update_progress(self.task_id, 30, "[green]Sending request to AI...")
        result = call_ai_api(query, use_groq, max_tokens)
        self.progress_manager.update_progress(self.task_id, 40, "[green]Processing AI response...")
        answer = result.content.strip()
        return answer, self.task_id

    def process_answer(self, answer: str, max_words: Optional[int]) -> str:
        """
        Processes the generated answer.

        Args:
            answer (str): The generated answer.
            max_words (Optional[int]): The maximum number of words for the formatted answer.

        Returns:
            str: The formatted answer.
        """
        self.progress_manager.update_progress(self.task_id, 10, "[green]Formatting answer...")
        formatted_answer = self.format_response(answer, max_words)
        self.progress_manager.complete_progress(self.task_id, "[green]Answer generated")
        return formatted_answer
    
    def format_response(self, answer: str, max_words: Optional[int] = None) -> str:
        """
        Formats the answer.

        Args:
            answer (str): The answer to format.
            max_words (Optional[int]): The maximum number of words for the formatted answer.

        Returns:
            str: The formatted answer.
        """
        if max_words:
            answer = self.truncate_to_word_limit(answer, max_words)
        
        # Ensure code blocks start on a new line
        answer = answer.replace("```", "\n```")
        
        return answer
    
    def truncate_to_word_limit(self, text: str, max_words: int) -> str:
        """
        Truncates the text to a specified word limit.

        Args:
            text (str): The text to truncate.
            max_words (int): The maximum number of words.

        Returns:
            str: The truncated text.
        """
        # First, check if the text needs truncation
        if len(text.split()) <= max_words:
            return text

        # If truncation is needed, split the text into words
        words = text.split()
        truncated = ' '.join(words[:max_words])

        # Add ellipsis if the text was truncated
        if len(truncated) < len(text):
            truncated += '...'

        return truncated
    
    def generate_follow_up_questions(self, initial_query: str, initial_response: str, use_groq: bool, max_tokens: Optional[int]) -> str:
        """
        Generates follow-up questions based on a given question and answer.

        Args:
            initial_query (str): The initial question.
            initial_response (str): The initial answer.
            use_groq (bool): Flag indicating whether to use GROQ for generating the follow-up questions.
            max_tokens (Optional[int]): The maximum number of tokens for the generated follow-up questions.

        Returns:
            str: The generated follow-up questions.
        """
        try:
            prompt = f"""
            Based on the following question and answer, generate 5 relevant follow-up questions:

            Question: {initial_query}
            Answer: {initial_response}

            Follow-up questions:
            1.
            """
            task = self.progress_manager.start_progress("[blue]Generating follow-up questions...")
            self.progress_manager.update_progress(task, 10, "[blue]Preparing follow-up request...")
            response = call_ai_api(prompt, use_groq, max_tokens)
            self.progress_manager.update_progress(task, 50, "[blue]Processing follow-up response...")
            generated_text = response.content
            questions = [q.strip() for q in generated_text.split('\n') if q.strip().endswith('?')]

            self.progress_manager.update_progress(task, 20, "[blue]Finalizing follow-up questions...")
            while len(questions) < MIN_FOLLOW_UP_QUESTIONS:
                questions.append(f"Can you elaborate more on {random.choice(['the topic', 'this subject', 'this area', 'this concept'])}?")

            self.progress_manager.complete_progress(task, "[blue]Follow-up questions generated")
            return questions[:MAX_FOLLOW_UP_QUESTIONS]
        except Exception as e:
            raise AIRequestError(f"Error generating follow-up questions: {str(e)}")