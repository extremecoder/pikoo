import os
import json
import requests
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv
from pathlib import Path
import yaml

class QASMTestGenerator:
    def __init__(self, together_api_key: Optional[str] = None):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = together_api_key or os.getenv('TOGETHER_API_KEY')
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment variables or constructor")
            
        self.api_url = "https://api.together.xyz/v1/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Load configuration if exists
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """Load configuration from config.yml if it exists"""
        config_path = Path("config.yml")
        default_config = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        if config_path.exists():
            with open(config_path) as f:
                return {**default_config, **yaml.safe_load(f)}
        return default_config

    def read_qasm_file(self, file_path: str) -> str:
        """Read and validate QASM file"""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"QASM file not found: {file_path}")
            
        with open(file_path, 'r') as file:
            content = file.read()
            
        # Basic validation of QASM content
        if not content.strip().startswith("OPENQASM"):
            raise ValueError("Invalid QASM file: Must start with OPENQASM version declaration")
            
        return content

    def generate_test_cases(self, qasm_code: str) -> List[Dict]:
        """Generate test cases using the Together API with improved error handling"""
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
            "model": self.config["model"],
            "prompt": prompt,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
            "top_p": self.config["top_p"],
            "stop": ["</response>"],
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                print(f"Making API request (attempt {attempt + 1}/{max_retries})...")
                response = requests.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if 'choices' not in result or not result['choices']:
                    raise ValueError("No choices in API response")
                    
                response_text = result['choices'][0]['text'].strip()
                
                # Extract and validate JSON
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                
                if start_idx == -1 or end_idx == -1:
                    raise ValueError("Could not find JSON array in response")
                    
                json_str = response_text[start_idx:end_idx + 1]
                test_cases = json.loads(json_str)
                
                if not isinstance(test_cases, list):
                    raise ValueError("Parsed JSON is not an array")
                    
                return test_cases
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Failed to connect to Together API after {max_retries} attempts: {str(e)}")
                print(f"Request failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
            except (json.JSONDecodeError, ValueError) as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to generate valid test cases: {str(e)}")
                print(f"Invalid response: {str(e)}. Retrying...")
                time.sleep(retry_delay)

    def save_test_cases(self, test_cases: List[Dict], output_file: str):
        """Save test cases with proper formatting"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(test_cases, f, indent=2)

def main():
    try:
        generator = QASMTestGenerator()
        
        qasm_file = "openqasm/sample.qasm"
        output_file = "openqasm/test_cases.json"
        
        # Read and validate QASM code
        print(f"\nReading QASM file: {qasm_file}")
        qasm_code = generator.read_qasm_file(qasm_file)
        
        # Generate test cases
        print("\nGenerating test cases...")
        test_cases = generator.generate_test_cases(qasm_code)
        
        # Save test cases
        print(f"\nSaving test cases to {output_file}")
        generator.save_test_cases(test_cases, output_file)
        
        # Print summary
        print(f"\nSuccessfully generated {len(test_cases)} test cases:")
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(json.dumps(test, indent=2))
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
