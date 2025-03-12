from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit.quantum_info import state_fidelity
import qiskit_qasm3_import
import json
import numpy as np
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class QuantumBackend(ABC):
    @abstractmethod
    def run_circuit(self, circuit: QuantumCircuit, shots: int = 1000) -> Dict:
        pass

class QiskitBackend(QuantumBackend):
    def __init__(self):
        self.simulator = AerSimulator()
    
    def run_circuit(self, circuit: QuantumCircuit, shots: int = 1000) -> Dict:
        job = self.simulator.run(circuit, shots=shots)
        return job.result().get_counts()

class QASMTestRunner:
    def __init__(self, qasm_file: str, test_cases_file: str, backend: Optional[QuantumBackend] = None):
        self.qasm_file = qasm_file
        self.test_cases_file = test_cases_file
        self.backend = backend or QiskitBackend()
        
    def load_test_cases(self):
        with open(self.test_cases_file, 'r') as f:
            return json.load(f)
            
    def load_qasm_circuit(self):
        circuit = QuantumCircuit.from_qasm_file(self.qasm_file)
        return circuit
        
    def prepare_input_state(self, input_state: str, num_qubits: int) -> QuantumCircuit:
        """Prepare the input state based on the string representation"""
        qc = QuantumCircuit(num_qubits)
        
        # Remove the kets and spaces
        state = input_state.replace('|', '').replace('⟩', '').strip()
        
        # Apply X gates where there are 1s in the input state
        for i, bit in enumerate(reversed(state)):
            if bit == '1':
                qc.x(i)
                
        return qc

    def process_measurement_result(self, state: str) -> str:
        """Extract the relevant qubit states from the full measurement result"""
        # Split the state string into parts if it contains spaces
        parts = state.split()
        # Return just the relevant qubit states (first part if split, or whole string if no spaces)
        return parts[0] if len(parts) > 1 else state
        
    def run_test_case(self, test_case, base_circuit: QuantumCircuit):
        """Run a single test case and return results"""
        num_qubits = base_circuit.num_qubits
        
        # Create circuit with input state preparation
        input_circuit = self.prepare_input_state(test_case['input_state'], num_qubits)
        
        # Combine input preparation with the circuit under test
        complete_circuit = input_circuit.compose(base_circuit)
        
        # Add measurements
        cr = ClassicalRegister(num_qubits)
        complete_circuit.add_register(cr)
        complete_circuit.measure_all()
        
        # Run the circuit using the selected backend
        raw_counts = self.backend.run_circuit(complete_circuit, shots=1000)
        
        # Process the measurement results to match expected format
        counts = {}
        for state, count in raw_counts.items():
            processed_state = self.process_measurement_result(state)
            counts[processed_state] = counts.get(processed_state, 0) + count
        
        # Calculate probabilities
        total_shots = sum(counts.values())
        probabilities = {key: value/total_shots for key, value in counts.items()}
        
        # Compare with expected probabilities
        expected_probs = test_case['measurement_probabilities']
        tolerance = 0.1  # 10% tolerance for statistical fluctuations
        
        matches = all(
            abs(probabilities.get(state, 0) - prob) <= tolerance
            for state, prob in expected_probs.items()
        )
        
        return {
            'success': matches,
            'actual_probabilities': probabilities,
            'expected_probabilities': expected_probs,
            'shots': total_shots
        }

    def run_all_tests(self):
        """Run all test cases and return results"""
        test_cases = self.load_test_cases()
        base_circuit = self.load_qasm_circuit()
        results = []
        
        print(f"\nRunning {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest Case {i+1}: {test_case['description']}")
            print(f"Input State: {test_case['input_state']}")
            print(f"Expected Output: {test_case['expected_output']}")
            
            result = self.run_test_case(test_case, base_circuit)
            
            print("Result:")
            print(f"Success: {'✓' if result['success'] else '✗'}")
            print("Actual Probabilities:")
            for state, prob in result['actual_probabilities'].items():
                print(f"  |{state}⟩: {prob:.3f}")
            print("Expected Probabilities:")
            for state, prob in result['expected_probabilities'].items():
                print(f"  |{state}⟩: {prob:.3f}")
                
            results.append({
                'test_case': test_case,
                'result': result
            })
            
        return results

def main():
    # Initialize the test runner
    runner = QASMTestRunner(
        qasm_file="openqasm/sample.qasm",
        test_cases_file="openqasm/test_cases.json"
    )
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        # Print summary
        print("\nTest Summary:")
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['result']['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        raise

if __name__ == "__main__":
    main()