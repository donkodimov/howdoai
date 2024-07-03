from typing import Optional
import time
import random
from .progressbarmanager import ProgressBarManager
from .api_client import call_ai_api, AIRequestError

from .config import LOCAL_API_URL, GROQ_API_URL, SYSTEM_MESSAGE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


# Constants
MAX_FOLLOW_UP_QUESTIONS = 5
MIN_FOLLOW_UP_QUESTIONS = 3

class QuestionAnswerer:
    def __init__(self, progress_manager: ProgressBarManager):
        self.progress_manager = progress_manager
        self.task_id = None

    def generate_answer(self, query: str, use_groq: bool, max_tokens: Optional[int]) -> str:
        self.task_id = self.progress_manager.start_progress("Generating answer...")
        # Logic for generating the answer
        #task1 = progress_manager.start_progress("Generating answer...")
        # Simulating steps in API call and response processing
        self.progress_manager.update_progress(self.task_id, 10, "[green]Preparing API request...")
        time.sleep(0.5)  # Simulating network delay
        self.progress_manager.update_progress(self.task_id, 20, "[green]Sending request to AI...")
        result = call_ai_api(query, use_groq, max_tokens)
        self.progress_manager.update_progress(self.task_id, 40, "[green]Processing AI response...")
        answer = result.content.strip()
        return answer, self.task_id

    def process_answer(self, answer: str, max_words: Optional[int]) -> str:
        self.progress_manager.update_progress(self.task_id, 10, "[green]Formatting answer...")
        formatted_answer = self.format_response(answer, max_words)
        self.progress_manager.complete_progress(self.task_id, "[green]Answer generated")
        return formatted_answer
    
    def format_response(self, answer: str, max_words: Optional[int] = None) -> str:
        if max_words:
            answer = self.truncate_to_word_limit(answer, max_words)
        
        # Ensure code blocks start on a new line
        answer = answer.replace("```", "\n```")
        
        return answer
    
    def truncate_to_word_limit(self, text: str, max_words: int) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text
        truncated = ' '.join(words[:max_words])
        if len(truncated) < len(text):
            truncated += '...'
        return truncated
    
    def generate_follow_up_questions(self, initial_query: str, initial_response: str, use_groq: bool, max_tokens: Optional[int]) -> str:
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