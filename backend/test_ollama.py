import requests
import json
import sys

def test_ollama_connection():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3",
        "prompt": "Hello",
        "stream": False
    }
    
    timeout = 30
    
    print(f"Testing connection to Ollama at {url}...")
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            timeout=timeout
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                generated_text = data.get("response", "No response field found in JSON")
                print(f"Generated Response: {generated_text}")
            except json.JSONDecodeError:
                print("Error: Received invalid JSON from Ollama.")
        else:
            print(f"Error: Ollama returned status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Is it running?")
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {timeout} seconds.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_ollama_connection()
