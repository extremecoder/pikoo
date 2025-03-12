import os
import json
import requests
from typing import List, Dict
import time

class QASMTestGenerator:
    def __init__(self, together_api_key: str):
        self.api_key = together_api_key
        self.api_url = "https://api.together.xyz/v1/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def read_qasm_file(self, file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    def generate_test_cases(self, qasm_code: str) -> List[Dict]:
        prompt = f"""
        Generate test cases in JSON format for the following OpenQASM code:

        {qasm_code}

        Return a JSON array where each test case has the following format:
        {{
            "input_state": "e.g., |00⟩",
            "expected_output": "e.g., (|00⟩ + |11⟩)/√2",
            "description": "what aspect is being tested",
            "measurement_probabilities": {{
                "00": 0.5,
                "11": 0.5
            }}
        }}

        Ensure the response is a valid JSON array of test cases.
        """

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Print raw response for debugging
            print("Raw API Response:")
            result = response.json()
            print(result)
            
            # Try to extract and parse the JSON from the response text
            response_text = result['choices'][0]['text'].strip()
            print("\nExtracted Text:")
            print(response_text)
            
            # Try to find JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx + 1]
                test_cases = json.loads(json_str)
                return test_cases
            else:
                print("Error: Could not find JSON array in response")
                return []

        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {str(e)}")
            print("Response text was:", response_text)
            return []
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return []

    def save_test_cases(self, test_cases: List[Dict], output_file: str):
        with open(output_file, 'w') as f:
            json.dump(test_cases, f, indent=2)

def main():
    # Get API key from environment variable
    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        print("Please set the TOGETHER_API_KEY environment variable")
        return

    generator = QASMTestGenerator(api_key)
    
    # Path to your QASM file
    qasm_file = "openqasm/sample.qasm"
    
    # Read QASM code
    qasm_code = generator.read_qasm_file(qasm_file)
    
    # Generate test cases
    print("Generating test cases...")
    test_cases = generator.generate_test_cases(qasm_code)
    
    # Save test cases
    output_file = "openqasm/test_cases.json"
    generator.save_test_cases(test_cases, output_file)
    print(f"Test cases saved to {output_file}")

    # Print summary
    print(f"\nGenerated {len(test_cases)} test cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input State: {test.get('input_state', 'N/A')}")
        print(f"Expected Output: {test.get('expected_output', 'N/A')}")
        print(f"Testing: {test.get('description', 'N/A')}")

if __name__ == "__main__":
    main()
