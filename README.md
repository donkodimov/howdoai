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

4. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

5. You're ready to use the `howdoai` CLI tool!

## Usage

To use the `howdoai` CLI tool, open your terminal and run the following command:

```
python howdoai.py "your question here"
```

Replace `"your question here"` with the actual question you want to ask. For example:

```
python howdoai.py "howdoai make a tar archive"
```

The `howdoai` tool will query the AI endpoint and provide you with a concise answer to your question. If the answer contains code, it will be wrapped in triple backticks (```).

## Examples

Here are a few examples of using the `howdoai` CLI tool:

1. How to create a tar archive:
   ```
   python howdoai.py "howdoai make a tar archive"
   ```
   Output:
   ```
   <result>To create a tar archive, use the following command:

   ```
   tar -cvf archive.tar file1 file2 directory/
   ```
   </result>
   ```

2. How to find the size of a directory:
   ```
   python howdoai.py "howdoai find the size of a directory"
   ```
   Output:
   ```
   <result>To find the size of a directory, use the `du` command with the `-sh` options:

   ```
   du -sh directory/
   ```
   </result>
   ```

3. How to check the disk space usage:
   ```
   python howdoai.py "howdoai check disk space usage"
   ```
   Output:
   ```
   <result>To check the disk space usage, use the `df` command with the `-h` option:

   ```
   df -h
   ```
   </result>
   ```

Feel free to ask any "how-to" question, and the `howdoai` tool will provide you with a helpful answer!

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

You can change the `model`, `temperature`, `max_tokens`, and other parameters according to your requirements.

## Contributing

If you'd like to contribute to the `howdoai` CLI tool, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.