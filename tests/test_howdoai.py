import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
import os
import re

# Add the parent directory to sys.path to allow imports from the howdoai package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from howdoai import main, main_cli, format_response, generate_follow_up_questions
from howdoai.api_client import call_ai_api, AIResponse, AIRequestError

def integration_test(func):
    return unittest.skipIf(
        'SKIP_INTEGRATION_TESTS' in os.environ,
        'Skipping integration tests'
    )(func)

def strip_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class TestHowDoAI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch('howdoai.call_ai_api')
    def test_response_with_code(self, mock_call_ai_api):
        """
        Test the response with code for creating a tar archive.

        This test case mocks the call to the AI API and verifies that the response
        contains the expected code snippet for creating a tar archive. It also checks
        that the follow-up questions are returned as a list and that there are at least
        three follow-up questions.

        Mocked AI response:
        The mocked AI response contains a code snippet for creating a tar archive.

        Expected output:
        The expected output is a dictionary with the answer containing the code snippet
        and the follow-up questions.

        """
        mock_call_ai_api.return_value = AIResponse(
            content="To create a tar archive, use the following command:\n\n```\ntar -cvf archive.tar file1 file2 directory/\n```\n\nThis will create an archive named 'archive.tar' containing the specified files and directory."
        )

        result = main("how to create a tar archive")

        expected_output = {
            "answer": "To create a tar archive, use the following command:\n\n\n```\ntar -cvf archive.tar file1 file2 directory/\n\n```\n\nThis will create an archive named 'archive.tar' containing the specified files and directory.",
            "follow_up_questions": result["follow_up_questions"]
        }
        self.assertEqual(result["answer"], expected_output["answer"])
        self.assertIsInstance(result["follow_up_questions"], list)
        self.assertGreaterEqual(len(result["follow_up_questions"]), 3)


    @patch('howdoai.call_ai_api')
    def test_response_without_code(self, mock_call_ai_api):
        mock_call_ai_api.return_value = AIResponse(
            content="The capital of France is Paris."
        )

        result = main("what is the capital of France")

        expected_output = {
            "answer": "The capital of France is Paris.",
            "follow_up_questions": result["follow_up_questions"]
        }
        self.assertEqual(result["answer"], expected_output["answer"])
        self.assertIsInstance(result["follow_up_questions"], list)
        self.assertGreaterEqual(len(result["follow_up_questions"]), 3)         


class TestHowDoAIMaxWords(unittest.TestCase):
    @patch('howdoai.call_ai_api')
    def test_max_words_limit(self, mock_call_ai_api):
        mock_call_ai_api.return_value = AIResponse(
            content="To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
        )

        result = main("how to create a tar archive", max_words=10)

        word_count = len(result["answer"].split())
        self.assertLessEqual(word_count, 10, f"Output exceeded 10 words: {result['answer']}")

class TestHowDoAICLI(unittest.TestCase):
    @patch('sys.argv', ['howdoai', '--max-words', '10', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('howdoai.call_ai_api')
    def test_cli_max_words(self, mock_call_ai_api, mock_stdout):
        """
        Test case for the `main_cli` function with the `--max-words` option.

        This test case verifies that the output of the `main_cli` function does not exceed the specified maximum word count.

        Args:
            self: The test case object.
            mock_call_ai_api: The mock object for the `call_ai_api` function.
            mock_stdout: The mock object for the standard output.

        Returns:
            None
        """
        mock_call_ai_api.return_value = AIResponse(
            content="To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
        )

        main_cli()

        output = mock_stdout.getvalue().strip()
        answer_line = output.split('\n')[0]  # Get the first line, which should be the answer
        word_count = len(answer_line.split())

        self.assertLessEqual(word_count, 10, f"Output exceeded 10 words: {answer_line}")
        self.assertIn("Follow-up questions:", output)

    # @patch('sys.argv', ['howdoai', 'how to create a tar archive'])
    # @patch('sys.stdout', new_callable=StringIO)
    # @patch('howdoai.call_ai_api')
    # def test_cli_without_max_words(self, mock_call_ai_api, mock_stdout):
    #     mock_call_ai_api.return_value = AIResponse(
    #         content="To create a tar archive, use the command: ```tar -cvf archive.tar file1 file2 directory/```"
    #     )
    #     main_cli()
    #     output = mock_stdout.getvalue().strip()
    #     #self.assertIn("n```", output)
    #     #self.assertRegex(output, r'(?s).*```')
    #     self.assertIn("tar -cvf archive.tar file1 file2 directory", output)

        
    @patch('sys.argv', ['howdoai'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_cli_no_query(self, mock_exit, mock_stdout):
        main_cli()

        output = mock_stdout.getvalue()
        self.assertIn("usage:", output)
        self.assertIn("howdoai", output)
        mock_exit.assert_called_once_with(1)

class TestHelperFunctions(unittest.TestCase):
    def test_format_response_with_code(self):
        input_text = "Here's a command:\n```\nls -la\n```\nThis lists files."
        expected_output = "Here's a command:\n\n```\nls -la\n\n```\nThis lists files."
        self.assertEqual(format_response(input_text), expected_output)

    def test_format_response_without_code(self):
        input_text = "The capital of France is Paris."
        expected_output = "The capital of France is Paris."
        self.assertEqual(format_response(input_text), expected_output)

    def test_format_response_with_max_words(self):
        input_text = "This is a long sentence that should be truncated."
        expected_output = "This is a long sentence..."
        self.assertEqual(format_response(input_text, max_words=5), expected_output)

    @patch('howdoai.api_client.requests.post')
    def test_call_ai_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        mock_post.return_value = mock_response

        result = call_ai_api("Test query")
        self.assertEqual(result, AIResponse(content="Test response"))

    @patch('howdoai.api_client.requests.post')
    def test_call_ai_api_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("API error")

        with self.assertRaises(AIRequestError):
            call_ai_api("Test query")

    @patch('howdoai.api_client.requests.post')
    def test_call_ai_api_empty_query(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Empty query response"}}]}
        mock_post.return_value = mock_response

        result = call_ai_api("")
        self.assertEqual(result, AIResponse(content="Empty query response"))

        # Check that the API was called with an empty string, not None
        called_data = mock_post.call_args[1]['json']
        self.assertEqual(called_data['messages'][1]['content'], "")

class TestHowDoAIIntegration(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # This will show the full diff for any failures

    @integration_test
    def test_integration_code_response(self):
        query = "how to create a tar archive"
        result = main(query)
        self.assertIn("tar", result["answer"])
        self.assertGreaterEqual(float(result["execution_time"].split(" ")[0]), 0)


    @integration_test
    def test_integration_text_response(self):
        query = "what is the capital of France"
        result = main(query)
        self.assertIn("Paris", result["answer"])

class TestHowDoAIFollowUpQuestions(unittest.TestCase):
    @patch('howdoai.api_client.call_ai_api')
    def test_generate_follow_up_questions(self, mock_call_ai_api):
        # Mock the initial response
        mock_call_ai_api.side_effect = [
            AIResponse(
                content="Quantum computing is a type of computation that harnesses the collective properties of quantum states, such as superposition, interference, and entanglement, to perform calculations."
            ),
            AIResponse(
                content="1. What are the practical applications of quantum computing?\n2. How does quantum computing differ from classical computing?\n3. What are the current challenges in quantum computing research?\n4. Can you explain the concept of quantum entanglement?\n5. How close are we to achieving practical quantum computers?"
            )
        ]

        # Call the main function with the initial query
        initial_query = "What is quantum computing?"
        result = main(initial_query)

        # Assert that we get a dictionary with 'answer' and 'follow_up_questions' keys
        self.assertIn('answer', result)
        self.assertIn('follow_up_questions', result)

        follow_up_questions = result['follow_up_questions']

        # Assert that we get a list of questions
        self.assertIsInstance(follow_up_questions, list)
        
        # Assert that we get at least 3 follow-up questions
        self.assertGreaterEqual(len(follow_up_questions), 3)

        # Assert that each question is a string and ends with a question mark
        for question in follow_up_questions:
            self.assertIsInstance(question, str)
            self.assertTrue(question.endswith('?'))

        # Assert that the follow-up questions are relevant to quantum computing
        relevant_keywords = ['quantum', 'computing', 'superposition', 'entanglement', 'qubit']
        self.assertTrue(any(any(keyword in question.lower() for keyword in relevant_keywords) for question in follow_up_questions))
        

    @patch('howdoai.call_ai_api')
    def test_generate_follow_up_questions_error(self, mock_call_ai_api):
        mock_call_ai_api.side_effect = [
            AIResponse(content="Quantum computing is ..."),  # First call for the main query
            AIRequestError("API Error")  # Second call for follow-up questions
        ]
        result = main("What is quantum computing?")
        self.assertIn('error', result)
        self.assertIn('Error generating follow-up questions', result['error'])

class TestMainCLI(unittest.TestCase):
    @patch('sys.argv', ['howdoai', '--max-words', '10', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('howdoai.call_ai_api')
    def test_cli_max_words(self, mock_call_ai_api, mock_stdout):
        """
        Test case for the `main_cli` function with the `--max-words` option.

        This test case verifies that the output of the `main_cli` function does not exceed the specified maximum word count.

        Args:
            self: The test case object.
            mock_call_ai_api: The mock object for the `call_ai_api` function.
            mock_stdout: The mock object for the standard output.

        Returns:
            None
        """
        mock_call_ai_api.return_value = AIResponse(
            content="To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
        )
        main_cli()
        output = mock_stdout.getvalue().strip()
        answer_line = output.split('\n')[0]  # Get the first line, which should be the answer
        word_count = len(answer_line.split())
        self.assertLessEqual(word_count, 10, f"Output exceeded 10 words: {answer_line}")
        self.assertIn("Follow-up questions:", output)



    # @patch('sys.argv', ['howdoai', 'how to create a tar archive'])
    # @patch('sys.stdout', new_callable=StringIO)
    # @patch('howdoai.call_ai_api')
    # def test_cli_without_max_words(self, mock_call_ai_api, mock_stdout):
    #     mock_call_ai_api.return_value = AIResponse(
    #         content="To create a tar archive, use the command: ```tar -cvf archive.tar file1 file2 directory/```"
    #     )
    #     main_cli()
    #     output = mock_stdout.getvalue().strip()
    #     # Strip ANSI escape sequences
    #     clean_output = strip_ansi_escape_sequences(output)
    #     print("Cleaned Output:", clean_output)
    #     #output = re.sub(r'\x1b\[[^m]*m', '', output)  # remove ANSI escape codes
    #     self.assertIn("tar -cvf archive", clean_output)
    #     #self.assertIn("tar -cvf archive.tar file1 file2 directory", output)

    @patch('sys.argv', ['howdoai'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_cli_no_query(self, mock_exit, mock_stdout):
        main_cli()
        output = mock_stdout.getvalue()
        self.assertIn("usage:", output)
        self.assertIn("howdoai", output)
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
