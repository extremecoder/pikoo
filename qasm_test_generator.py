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
        prompt = f"""<instruction>Given an OpenQASM circuit, generate test cases in JSON format. Return only valid JSON.</instruction>

<context>
The circuit is:
{qasm_code}

You should return a JSON array of test cases. Each test case should have:
- input_state: The initial quantum state
- expected_output: The expected final state
- description: What aspect is being tested
- measurement_probabilities: Expected measurement probabilities
</context>

<example_output>
[
    {{
        "input_state": "|00⟩",
        "expected_output": "(|00⟩ + |11⟩)/√2",
        "description": "Bell state generation test",
        "measurement_probabilities": {{
            "00": 0.5,
            "11": 0.5
        }}
    }}
]
</example_output>

<response>"""

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop": ["</response>"],
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        try:
            print("Making API request...")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                return []

            result = response.json()
            print("Raw API response:", json.dumps(result, indent=2))
            
            if 'choices' not in result or not result['choices']:
                print("Error: No choices in response")
                return []
                
            response_text = result['choices'][0]['text'].strip()
            print("\nModel output:", response_text)
            
            # Try to find JSON array in the response
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx + 1]
                    test_cases = json.loads(json_str)
                    if not isinstance(test_cases, list):
                        print("Error: Parsed JSON is not an array")
                        return []
                    return test_cases
                else:
                    print("Error: Could not find JSON array in response")
                    return []
            except json.JSONDecodeError as je:
                print(f"JSON Parse Error: {str(je)}")
                print("Failed to parse:", json_str)
                return []
                
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
        print("Error: TOGETHER_API_KEY environment variable is not set")
        return
    
    print(f"API key is {'not ' if not api_key else ''}set")
    
    generator = QASMTestGenerator(api_key)
    
    try:
        # Read QASM code
        qasm_file = "openqasm/sample.qasm"
        qasm_code = generator.read_qasm_file(qasm_file)
        print(f"Successfully read QASM file: {qasm_file}")
        print("\nQASM Code:")
        print(qasm_code)
        
        # Generate test cases
        print("\nGenerating test cases...")
        test_cases = generator.generate_test_cases(qasm_code)
        
        # Save test cases
        output_file = "openqasm/test_cases.json"
        generator.save_test_cases(test_cases, output_file)
        print(f"\nTest cases saved to {output_file}")

        # Print summary
        print(f"\nGenerated {len(test_cases)} test cases:")
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(json.dumps(test, indent=2))
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
