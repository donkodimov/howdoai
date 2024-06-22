import requests
import json
import sys
import argparse

def truncate_to_word_limit(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def main(query, max_words=None):
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
                if max_words:
                    answer = truncate_to_word_limit(answer, max_words)
                output = f"<result>{answer}</result>"

            return output

        else:
            return f"Error: Request failed with status code {response.status_code}\nResponse: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error: An unexpected error occurred while making the request\n{str(e)}"

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Error: An unexpected error occurred while parsing the response\n{str(e)}"

def main_cli():
    parser = argparse.ArgumentParser(description='Get concise answers to how-to questions.')
    parser.add_argument('query', nargs='?', help='The question to ask')
    parser.add_argument('--max-words', type=int, help='Maximum number of words in the response')
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    result = main(args.query, args.max_words)
    print(result)

if __name__ == "__main__":
    main_cli()