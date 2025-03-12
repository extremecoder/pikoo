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
        Given the following OpenQASM code:

        {qasm_code}

        Generate a comprehensive set of test cases to verify the circuit's correctness.
        For each test case, provide:
        1. Input state
        2. Expected output state
        3. Explanation of what aspect is being tested
        4. Expected measurement probabilities

        Format the response as a JSON list of test cases.
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
            
            # Parse the response and extract the test cases
            result = response.json()
            test_cases = json.loads(result['choices'][0]['text'])
            return test_cases

        except Exception as e:
            print(f"Error generating test cases: {str(e)}")
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
