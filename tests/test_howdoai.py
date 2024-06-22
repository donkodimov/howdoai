import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from howdoai import main

class TestHowDoAI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # This will show the full diff for any failures

    @patch('sys.argv', ['howdoai', 'how to create a tar archive'])
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

        result = main()

        expected_output = "<code>\ntar -cvf archive.tar file1 file2 directory/\n</code>"
        self.assertEqual(result, expected_output)

    @patch('sys.argv', ['howdoai', 'what is the capital of France'])
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

        result = main()

        expected_output = "<result>The capital of France is Paris.</result>"
        self.assertEqual(result, expected_output)

    @patch('sys.argv', ['howdoai', 'test query'])
    @patch('requests.post')
    def test_error_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = main()

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

if __name__ == '__main__':
    unittest.main(verbosity=2)