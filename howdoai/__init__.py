import requests
import json
import sys

def main(query=None):
    if query is None:
        query = sys.argv[1] if len(sys.argv) > 1 else ""

    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "messages": [
            {"role": "system",
                "content": "You are an AI assistant that provides concise, one-line answers with the best example of how to complete a task. If the answer contains code or commands, wrap it in triple backticks (```)."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()

            if "```" in answer:
                code_start = answer.find("```") + 3
                code_end = answer.find("```", code_start)
                code = answer[code_start:code_end].strip()
                output = f"<code>\n{code}\n</code>"
            else:
                output = f"<result>{answer}</result>"

            return output  # Only return the output, don't print it here

        else:
            error_message = f"Error: Request failed with status code {response.status_code}\nResponse: {response.text}"
            return error_message

    except requests.exceptions.RequestException as e:
        error_message = f"Error: An unexpected error occurred while making the request\n{str(e)}"
        return error_message

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        error_message = f"Error: An unexpected error occurred while parsing the response\n{str(e)}"
        return error_message
    
def main_cli():
    result = main()
    print(result)

if __name__ == "__main__":
    result = main()
    print(result)  # Print the result only when run as a script