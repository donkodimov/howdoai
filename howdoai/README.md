# howdoai CLI Tool

`howdoai` is a command-line tool that allows you to quickly get answers to your "how-to" questions by querying an AI endpoint. It provides concise, one-line answers with the best example of how to complete a task, making it easy for you to find solutions to your problems.

## Installation

To install the `howdoai` CLI tool, follow these steps:

1. Make sure you have Python installed on your system. `howdoai` requires Python 3.6 or higher.

2. Clone the `howdoai` repository from GitHub:
   ```
   git clone https://github.com/donkodimov/howdoai.git
   ```

3. Navigate to the `howdoai` directory:
   ```
   cd howdoai
   ```

4. Install the package in editable mode:
   ```
   pip install -e .
   ```

5. You're ready to use the `howdoai` CLI tool!

## Usage

You can use `howdoai` in two ways:

1. As a command-line tool:
   ```
   howdoai "your question here"
   ```
   For example:
   ```
   howdoai "how to create a tar archive"
   ```

2. As a Python module:
   ```python
   from howdoai import main
   
   result = main("your question here")
   print(result)
   ```

The `howdoai` tool will query the AI endpoint and provide you with a concise answer to your question. If the answer contains code, it will be wrapped in triple backticks (```).

## Examples

Here are a few examples of using the `howdoai` CLI tool:

1. How to create a tar archive:
   ```
   howdoai "howdoai make a tar archive"
   ```
   Output:
   ```
   <code>
   tar -czf myarchive.tar.gz /path/to/directory
   </code>
   ```

2. How to find the size of a directory:
   ```
   howdoai "howdoai find the size of a directory"
   ```
   Output:
   ```
   <code>
   du -sh /path/to/directory
   </code>
   ```

3. How to check the disk space usage:
   ```
   howdoai "howdoai check disk space usage"
   ```
   Output:
   ```
   <result>To check disk space usage on Windows, use the command `wmic diskdrive get size,freespace` or `fsutil volume get freespace` and on Linux/macOS, use `df -h` or `du -sh /`.
   </result>
   ```

Feel free to ask any "how-to" question, and the `howdoai` tool will provide you with a helpful answer!

## Features

- Provides concise, one-line answers to "how-to" questions
- Includes code snippets or commands when relevant, wrapped in `<code>` tags
- Non-code answers are wrapped in `<result>` tags
- Uses an AI-powered backend for generating responses

## Configuration

The `howdoai` CLI tool uses a pre-configured AI endpoint to generate answers. If you want to modify the endpoint or adjust the AI model settings, you can update the `data` dictionary in the `howdoai.py` script:

```python
data = {
    "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    "messages": [
        {"role": "system", "content": "You are an AI assistant that provides concise, one-line answers with the best example of how to complete a task. If the answer contains code, wrap it in triple backticks (```)."},
        {"role": "user", "content": query}
    ],
    "temperature": 0.7,
    "max_tokens": 100,
    "stream": True
}
```
## Testing

To run the tests, use the following command from the root directory of the project:

```
python -m unittest discover tests
```

You can change the `model`, `temperature`, `max_tokens`, and other parameters according to your requirements.

## Contributing

If you'd like to contribute to the `howdoai` CLI tool, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.