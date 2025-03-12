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
        Generate test cases for this OpenQASM circuit. Return ONLY a JSON array of test cases with no additional text.
        Each test case should be an object with these exact fields: "input_state", "expected_output", "description", and "measurement_probabilities".

        OpenQASM code:
        {qasm_code}

        Example of expected format:
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
        """

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop": ["\n\n"],
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        try:
            # Print API key length to verify it's set (without revealing it)
            print(f"API Key length: {len(self.api_key)}")
            
            # Make the API request
            print("Making API request...")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            # Print response status and headers
            print(f"Response status: {response.status_code}")
            print("Response headers:", dict(response.headers))
            
            # Print raw response text
            print("Raw response text:", response.text)
            
            # Parse response
            result = response.json()
            if 'choices' not in result or not result['choices']:
                print("Error: No choices in response")
                return []
                
            response_text = result['choices'][0]['text'].strip()
            print("Model output:", response_text)
            
            # Try to parse as JSON
            try:
                test_cases = json.loads(response_text)
                if isinstance(test_cases, list):
                    return test_cases
                else:
                    print("Error: Response is not a JSON array")
                    return []
            except json.JSONDecodeError as je:
                print(f"JSON Parse Error: {str(je)}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            if hasattr(e.response, 'text'):
                print("Error response:", e.response.text)
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
        print("Error: TOGETHER_API_KEY environment variable is not set")
        return
    
    print(f"API key is {'not ' if not api_key else ''}set")
    
    generator = QASMTestGenerator(api_key)
    
    # Path to your QASM file
    qasm_file = "openqasm/sample.qasm"
    
    try:
        # Read QASM code
        qasm_code = generator.read_qasm_file(qasm_file)
        print(f"Successfully read QASM file: {qasm_file}")
        
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
            print(json.dumps(test, indent=2))
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
