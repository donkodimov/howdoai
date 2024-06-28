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
   ```bash
   howdoai "your question here"
   ```
   For example:
   ```bash
   howdoai "how to create a tar archive"
   ```

2. As a Python module:
   ```python
   from howdoai import main
   
   result = main("your question here")
   print(result)
   ```

You can also limit the number of words in the response using the `--max-words` option:

```bash
howdoai --max-words 20 "how to create a tar archive"
```

The `howdoai` tool will query the AI endpoint and provide you with a concise answer to your question. If the answer contains code, it will be wrapped in triple backticks (```).

To use the Groq API with `howdoai`, simply append the `--groq` option to your command. Here's an example:

```bash
howdoai --groq "Your query here"
```

This command sends your query to the Groq API and displays the response in your terminal.


## Examples

Here are a few examples of using the `howdoai` CLI tool:

1. How to create a tar archive:
   ```bash
   howdoai "howdoai make a tar archive"
   ```
   Output:
   ```
   <code>
   tar -czf myarchive.tar.gz /path/to/directory
   </code>
   ```

2. How to find the size of a directory:
   ```bash
   howdoai "howdoai find the size of a directory"
   ```
   Output:
   ```
   <code>
   du -sh /path/to/directory
   </code>
   ```

3. How to check the disk space usage:
   ```bash
   howdoai "howdoai check disk space usage"
   ```
   Output:
   ```
   <result>To check disk space usage on Windows, use the command `wmic diskdrive get size,freespace` or `fsutil volume get freespace` and on Linux/macOS, use `df -h` or `du -sh /`.
   </result>
   ```

4. How to use the `howdoai`CLI tool with groq api:
   ```bash
   howdoai --groq "how to create tar archive"
   ```
   

Feel free to ask any "how-to" question, and the `howdoai` tool will provide you with a helpful answer!

## Features

- Provides concise, one-line answers to "how-to" questions
- Includes code snippets or commands when relevant
- Uses an local and remote AI-powered backend for generating responses

## Configuration

The `howdoai` CLI tool uses a pre-configured AI local or remote endpoint to generate answers. If you want to modify the endpoint or adjust the AI model settings, you can update the `LOCAL_API_URL` and `call_ai_api` function in the `api_client.py` file:

```python
API_URL = "http://localhost:1234/v1/chat/completions"

def call_ai_api(query: str) -> Dict[str, Any]:
    if use_groq:
        api_url = GROQ_API_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        model = GROQ_MODEL
    else:
        api_url = LOCAL_API_URL
        headers = {"Content-Type": "application/json"}
        model = LOCAL_MODEL

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query if query else ""}
        ],
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "stream": False
    }
    ...
```

## Testing

To run the tests, use the following command from the root directory of the project:

```bash
python -m unittest discover tests
```

You can change the `model`, `temperature`, `max_tokens`, and other parameters according to your requirements.

Note: The test suite includes integration tests that make actual API calls. To skip these tests, set the `SKIP_INTEGRATION_TESTS` environment variable:

```bash
export SKIP_INTEGRATION_TESTS=1
python -m unittest discover tests
```

### Environment Configuration

Before using the `--groq` option, ensure you have set up the necessary environment variables:

- `GROQ_API_KEY`: Your API key for accessing the Groq API.
- `GROQ_ENDPOINT`: The endpoint URL for the Groq API.

Example:

```bash
export GROQ_API_KEY="your_api_key_here"
export GROQ_ENDPOINT="https://api.groq.com/v1"
```

## Troubleshooting

If you encounter any issues while using `howdoai`, try the following:

1. Ensure you're using Python 3.6 or higher.
2. Check your internet connection, as the tool requires access to the AI endpoint.
3. If you receive an error about the AI endpoint, make sure it's running and accessible.
4. For any other issues, please open an issue on the GitHub repository.

If you encounter any issues while using the `--groq` option:

1. Ensure your `GROQ_API_KEY` and `GROQ_ENDPOINT` environment variables are correctly set.
2. Verify that the Groq API is currently accessible and operational.
3. Check if your query is correctly formatted and adheres to the Groq API's requirements.
4. For detailed error messages, use the `--verbose` option with your command.


## Error Handling

`howdoai` is designed to handle various error scenarios gracefully. If an error occurs during the API call or response processing, the tool will display an error message explaining what went wrong.


## Contributing

If you'd like to contribute to the `howdoai` CLI tool, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## Git Branching Strategy

This project follows a Git branching model inspired by [Vincent Driessen's branching model](https://nvie.com/posts/a-successful-git-branching-model/). This strategy helps us manage releases, feature development, and hotfixes in a structured manner.

### Main Branches

- `main`: This branch contains production-ready code. All releases are merged into and tagged on this branch.
- `develop`: This is the main branch for development, where features are integrated.

### Supporting Branches

- `feature/*`: Used for developing new features or improvements. These branch off from and merge back into `develop`.
- `release/*`: Used for preparing releases. These branch off from `develop` and merge into both `main` and `develop`.
- `hotfix/*`: Used for quick fixes to production code. These branch off from `main` and merge into both `main` and `develop`.

### Workflow

1. **Feature Development**
   - Create a new branch from `develop`: `git checkout -b feature/my-new-feature develop`
   - Develop and commit changes
   - Open a pull request to merge back into `develop`

2. **Preparing a Release**
   - Create a release branch from `develop`: `git checkout -b release/v1.2.0 develop`
   - Make minor bug fixes and prepare release metadata
   - Merge into `main` and `develop` when ready
   - Tag the release on `main`: `git tag -a v1.2.0 -m "Release version 1.2.0"`

3. **Hotfixes**
   - Create a hotfix branch from `main`: `git checkout -b hotfix/critical-bug main`
   - Fix the issue and commit changes
   - Merge into both `main` and `develop`
   - Tag the hotfix on `main`: `git tag -a v1.2.1 -m "Hotfix version 1.2.1"`

### Branch Naming Conventions

- Feature branches: `feature/add-max-words-option`
- Release branches: `release/v1.2.0`
- Hotfix branches: `hotfix/fix-api-connection-issue`

### Tagging

We use semantic versioning (e.g., v1.2.3) for release tags.

### Pull Requests and Code Reviews

All merges to `develop` and `main` branches must go through a pull request and code review process.

### Continuous Integration

Our CI pipeline runs tests on all feature branches and the `develop` branch. Successful builds on `main` are automatically deployed to production.

For more detailed information about this branching strategy, please refer to [Vincent Driessen's article](https://nvie.com/posts/a-successful-git-branching-model/).