import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from howdoai import main, main_cli, call_ai_api, format_response
import requests
import os

def integration_test(func):
    return unittest.skipIf(
        'SKIP_INTEGRATION_TESTS' in os.environ,
        'Skipping integration tests'
    )(func)

class TestHowDoAI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch('howdoai.call_ai_api')
    def test_response_with_code(self, mock_call_ai_api):
        mock_call_ai_api.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command:\n\n```\ntar -cvf archive.tar file1 file2 directory/\n```\n\nThis will create an archive named 'archive.tar' containing the specified files and directory."
                    }
                }
            ]
        }

        result = main("how to create a tar archive")

        expected_output = "<code>\ntar -cvf archive.tar file1 file2 directory/\n</code>"
        self.assertEqual(result, expected_output)

    @patch('howdoai.call_ai_api')
    def test_response_without_code(self, mock_call_ai_api):
        mock_call_ai_api.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The capital of France is Paris."
                    }
                }
            ]
        }

        result = main("what is the capital of France")

        expected_output = "<result>The capital of France is Paris.</result>"
        self.assertEqual(result, expected_output)

    @patch('howdoai.call_ai_api')
    def test_error_response(self, mock_call_ai_api):
        mock_call_ai_api.side_effect = RuntimeError(
            "API request failed: Internal Server Error")

        result = main("test query")

        expected_output = "Error: API request failed: Internal Server Error"
        self.assertEqual(result, expected_output)


class TestHowDoAIMaxWords(unittest.TestCase):
    @patch('howdoai.call_ai_api')
    def test_max_words_limit(self, mock_call_ai_api):
        mock_call_ai_api.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
                    }
                }
            ]
        }

        result = main("how to create a tar archive", max_words=10)

        word_count = len(result.split())
        self.assertLessEqual(
            word_count, 10, f"Output exceeded 10 words: {result}")
        self.assertIn("<result>", result)
        self.assertIn("</result>", result)


class TestHowDoAICLI(unittest.TestCase):
    @patch('sys.argv', ['howdoai', '--max-words', '10', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('howdoai.call_ai_api')
    def test_cli_max_words(self, mock_call_ai_api, mock_stdout):
        mock_call_ai_api.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
                    }
                }
            ]
        }

        main_cli()

        output = mock_stdout.getvalue().strip()
        word_count = len(output.split())

        self.assertLessEqual(
            word_count, 10, f"Output exceeded 10 words: {output}")
        self.assertIn("<result>", output)
        self.assertIn("</result>", output)

    @patch('sys.argv', ['howdoai', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('howdoai.call_ai_api')
    def test_cli_without_max_words(self, mock_call_ai_api, mock_stdout):
        mock_call_ai_api.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the command: tar -cvf archive.tar file1 file2 directory/"
                    }
                }
            ]
        }

        main_cli()

        output = mock_stdout.getvalue().strip()
        self.assertIn("<result>", output)
        self.assertIn("tar -cvf archive.tar", output)
        self.assertIn("</result>", output)

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
        expected_output = "<code>\nls -la\n</code>"
        self.assertEqual(format_response(input_text), expected_output)

    def test_format_response_without_code(self):
        input_text = "The capital of France is Paris."
        expected_output = "<result>The capital of France is Paris.</result>"
        self.assertEqual(format_response(input_text), expected_output)

    def test_format_response_with_max_words(self):
        input_text = "This is a long sentence that should be truncated."
        expected_output = "<result>This is a long sentence...</result>"
        self.assertEqual(format_response(
            input_text, max_words=5), expected_output)

    @patch('requests.post')
    def test_call_ai_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [
            {"message": {"content": "Test response"}}]}
        mock_post.return_value = mock_response

        result = call_ai_api("Test query")
        self.assertEqual(
            result, {"choices": [{"message": {"content": "Test response"}}]})

    @patch('requests.post')
    def test_call_ai_api_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException(
            "API error")

        with self.assertRaises(RuntimeError):
            call_ai_api("Test query")

    @patch('requests.post')
    def test_call_ai_api_empty_query(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [
            {"message": {"content": "Empty query response"}}]}
        mock_post.return_value = mock_response

        result = call_ai_api("")
        self.assertEqual(
            result, {"choices": [{"message": {"content": "Empty query response"}}]})

        # Check that the API was called with an empty string, not None
        called_data = mock_post.call_args[1]['json']
        self.assertEqual(called_data['messages'][1]['content'], "")

# Add this after the TestHowDoAICLI class and before the TestHelperFunctions class

class TestHowDoAIIntegration(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # This will show the full diff for any failures

    @integration_test
    def test_integration_code_response(self):
        query = "how to create a tar archive"
        result = main(query)
        print(f"\nQuery: {query}")
        print(f"Result:\n{result}")
        self.assertIn("<code>", result)
        self.assertIn("tar", result)
        self.assertIn("</code>", result)

    @integration_test
    def test_integration_text_response(self):
        query = "what is the capital of France"
        result = main(query)
        print(f"\nQuery: {query}")
        print(f"Result:\n{result}")
        self.assertIn("<result>", result)
        self.assertIn("Paris", result)
        self.assertIn("</result>", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
