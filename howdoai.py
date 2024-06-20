import requests
import json
import sys

query = sys.argv[1]

url = "http://localhost:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    "messages": [
        {"role": "system", "content": "You are an AI assistant that provides concise, one-line answers with the best example of how to complete a task. If the answer contains code or commands, wrap it in triple backticks (```)."},
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
            non_code_parts = answer.split("```")
            formatted_answer = non_code_parts[0].strip() + "\n\n```\n" + code + "\n```\n" + non_code_parts[-1].strip()
            #print(f"result\n" + formatted_answer + "\nresult")
            print(f"<code>\n" + code + "\n</code>")
        else:
            print(f"<result>{answer}</result>")

    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print("Error: An unexpected error occurred while making the request")
    print(str(e))

except (KeyError, IndexError, json.JSONDecodeError) as e:
    print("Error: An unexpected error occurred while parsing the response")
    print(str(e))