from typing import Optional
import time
from .progressbarmanager import ProgressBarManager
from .api_client import call_ai_api

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