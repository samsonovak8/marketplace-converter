import json
import requests

def get_by_prompt(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=100000000)
        response.raise_for_status()
        return response.json().get('response', '')
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return ''

def read_file_as_list_of_strings(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]
