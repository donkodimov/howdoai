import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from howdoai import main, main_cli

class TestHowDoAI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # This will show the full diff for any failures

    @patch('requests.post')
    def test_response_with_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command:\n\n```\ntar -cvf archive.tar file1 file2 directory/\n```\n\nThis will create an archive named 'archive.tar' containing the specified files and directory."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = main("how to create a tar archive")

        expected_output = "<code>\ntar -cvf archive.tar file1 file2 directory/\n</code>"
        self.assertEqual(result, expected_output)

    @patch('requests.post')
    def test_response_without_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The capital of France is Paris."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = main("what is the capital of France")

        expected_output = "<result>The capital of France is Paris.</result>"
        self.assertEqual(result, expected_output)

    @patch('requests.post')
    def test_error_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = main("test query")

        expected_output = "Error: Request failed with status code 500\nResponse: Internal Server Error"
        self.assertEqual(result, expected_output)

class TestHowDoAIIntegration(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # This will show the full diff for any failures

    def test_integration_code_response(self):
        query = "how to create a tar archive"
        result = main(query)
        print(f"\nQuery: {query}")
        print(f"Result:\n{result}")
        self.assertIn("<code>", result)
        self.assertIn("tar", result)
        self.assertIn("</code>", result)

    def test_integration_text_response(self):
        query = "what is the capital of France"
        result = main(query)
        print(f"\nQuery: {query}")
        print(f"Result:\n{result}")
        self.assertIn("<result>", result)
        self.assertIn("Paris", result)
        self.assertIn("</result>", result)

class TestHowDoAIMaxWords(unittest.TestCase):
    @patch('requests.post')
    def test_max_words_limit(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
                    }}
            ]
        }
        mock_post.return_value = mock_response

        result = main("how to create a tar archive", max_words=10)

        word_count = len(result.split())
        self.assertLessEqual(word_count, 10, f"Output exceeded 10 words: {result}")
        self.assertIn("<result>", result)
        self.assertIn("</result>", result)

class TestHowDoAICLI(unittest.TestCase):
    @patch('sys.argv', ['howdoai', '--max-words', '10', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.post')
    def test_cli_max_words(self, mock_post, mock_stdout):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the following command: tar -cvf archive.tar file1 file2 directory/. This will package the specified files and directories into a single archive file."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        main_cli()

        output = mock_stdout.getvalue().strip()
        word_count = len(output.split())
        
        self.assertLessEqual(word_count, 10, f"Output exceeded 10 words: {output}")
        self.assertIn("<result>", output)
        self.assertIn("</result>", output)

    @patch('sys.argv', ['howdoai', 'how to create a tar archive'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.post')
    def test_cli_without_max_words(self, mock_post, mock_stdout):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "To create a tar archive, use the command: tar -cvf archive.tar file1 file2 directory/"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

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

if __name__ == '__main__':
    unittest.main(verbosity=2)