#!/usr/bin/env python3
"""
Universal runner for OpenQASM circuits across different quantum platforms.
"""
import argparse
import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import importlib.util

# Import our compatibility utilities
from platform_compatibility import to_platform_compatible_qasm, validate_cross_platform
from quantum_result import QuantumResult

def check_platform_available(platform):
    """
    Check if the specified platform is available in the environment.
    
    Args:
        platform (str): Name of the platform to check ('qiskit', 'cirq', 'braket')
        
    Returns:
        bool: True if available, False otherwise
    """
    if platform == "qiskit":
        try:
            import qiskit
            return True
        except ImportError:
            return False
    elif platform == "cirq":
        try:
            import cirq
            return True
        except ImportError:
            return False
    elif platform == "braket":
        try:
            from braket.circuits import Circuit
            return True
        except ImportError:
            return False
    return False

def run_on_qiskit(qasm_file, shots):
    """
    Run the given QASM file on Qiskit simulator.
    
    Args:
        qasm_file (str): Path to the QASM file
        shots (int): Number of shots to run
        
    Returns:
        QuantumResult: Standardized result object
    """
    from qiskit import QuantumCircuit
    import qiskit_aer
    
    # Create a circuit from QASM
    circuit = QuantumCircuit.from_qasm_file(qasm_file)
    print(f"Loaded QASM circuit on Qiskit simulator:")
    print(circuit)
    
    # Run the circuit on the QASM simulator
    simulator = qiskit_aer.AerSimulator()
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    
    # Convert to standardized result format
    return QuantumResult.from_qiskit_result(result, {'platform': 'qiskit'})

def run_on_cirq(qasm_file, shots):
    """
    Run the given QASM file on Cirq simulator.
    
    Args:
        qasm_file (str): Path to the QASM file
        shots (int): Number of shots to run
        
    Returns:
        QuantumResult: Standardized result object
    """
    import cirq
    from cirq.contrib.qasm_import import circuit_from_qasm
    
    # Load QASM file
    with open(qasm_file, 'r') as f:
        qasm_str = f.read()
    
    # Create a circuit from QASM
    circuit = circuit_from_qasm(qasm_str)
    print(f"Loaded QASM circuit on Cirq simulator:")
    print(circuit)
    
    # Run the circuit on the Cirq simulator
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=shots)
    
    # Convert to standardized result format
    return QuantumResult.from_cirq_result(result, {'platform': 'cirq'})

def run_on_braket(qasm_file, shots):
    """
    Run the given QASM file on AWS Braket simulator.
    
    Args:
        qasm_file (str): Path to the QASM file
        shots (int): Number of shots to run
        
    Returns:
        QuantumResult: Standardized result object
    """
    from braket.circuits import Circuit
    from braket.devices import LocalSimulator
    import re
    
    with open(qasm_file, 'r') as f:
        qasm_str = f.read()
    
    try:
        # Method 1: Use Braket's native OpenQASM support via Program class
        from braket.ir.openqasm import Program
        
        print("Using native Braket OpenQASM support...")
        
        # Process the QASM for Braket compatibility
        lines = qasm_str.split('\n')
        processed_lines = []
        version_updated = False
        include_removed = False
        
        # Gate mappings from common representations to Braket's preferred names
        gate_mappings = {
            'cx': 'cnot',
            'ccx': 'ccnot',
            'id': 'i',  # identity gate
        }
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                processed_lines.append(line)
                continue
                
            # Update version declaration
            if 'OPENQASM 2.0' in line and not version_updated:
                line = 'OPENQASM 3;'
                version_updated = True
            
            # Skip include statements for qelib1.inc
            elif re.search(r'include\s+["\']qelib1.inc["\'];', line):
                include_removed = True
                continue
            
            # Process gate names using more robust pattern matching
            else:
                for old_gate, new_gate in gate_mappings.items():
                    pattern = r'\b' + old_gate + r'\s+([^;]+);'
                    replacement = new_gate + r' \1;'
                    line = re.sub(pattern, replacement, line)
            
            processed_lines.append(line)
        
        # Combine the processed lines back into a string
        processed_qasm = '\n'.join(processed_lines)
        
        print("Processed QASM for Braket compatibility:")
        print(processed_qasm.strip())
        print(f"Version updated: {version_updated}, Include removed: {include_removed}")
        
        # Create a program from the processed QASM
        qasm_program = Program(source=processed_qasm)
        
        # Run the program on the local simulator
        simulator = LocalSimulator()
        print("Running the OpenQASM program directly with Braket native support...")
        task = simulator.run(qasm_program, shots=shots)
        result = task.result()
        
        # Convert to standardized result format
        return QuantumResult.from_braket_result(result, {'platform': 'braket'})
            
    except Exception as e:
        print(f"Native OpenQASM parsing failed: {e}")
        
        # Method 2: Fallback to qiskit-braket-provider
        try:
            print("Falling back to qiskit-braket-provider...")
            from qiskit import QuantumCircuit
            from qiskit_braket_provider.providers import to_braket
            
            # First convert QASM to Qiskit circuit
            qiskit_circuit = QuantumCircuit.from_qasm_file(qasm_file)
            
            # Then convert Qiskit circuit to Braket circuit
            circuit = to_braket(qiskit_circuit)
            print("Loaded QASM circuit on Braket simulator using qiskit-braket-provider:")
            print(circuit)
            
            # Run the circuit on the Braket local simulator
            simulator = LocalSimulator()
            result = simulator.run(circuit, shots=shots).result()
            
            # Convert to standardized result format
            return QuantumResult.from_braket_result(result, {'platform': 'braket'})
                
        except Exception as e2:
            raise RuntimeError(f"All Braket methods failed: {e} / {e2}")

def main():
    parser = argparse.ArgumentParser(description='Run OpenQASM circuits on different quantum platforms')
    parser.add_argument('--qasm', default='openqasm/sample.qasm', help='Path to the OpenQASM file')
    parser.add_argument('--platform', choices=['qiskit', 'cirq', 'braket', 'auto'], default='auto',
                        help='Quantum platform to use for simulation')
    parser.add_argument('--shots', type=int, default=1000, help='Number of shots to run')
    parser.add_argument('--validate', action='store_true', help='Validate the QASM for cross-platform compatibility')
    parser.add_argument('--output', default=None, help='Output file for the result plot (default: platform_results.png)')
    args = parser.parse_args()
    
    # Check if QASM file exists
    if not os.path.exists(args.qasm):
        print(f"Error: QASM file '{args.qasm}' not found.")
        sys.exit(1)
    
    # Load the QASM file
    with open(args.qasm, 'r') as f:
        qasm_str = f.read()
    
    # Validate if requested
    if args.validate:
        issues = validate_cross_platform(qasm_str)
        if issues:
            print("Cross-platform compatibility issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No cross-platform compatibility issues found.")
    
    # If platform is 'auto', select first available platform
    if args.platform == 'auto':
        for platform in ['qiskit', 'braket', 'cirq']:
            if check_platform_available(platform):
                args.platform = platform
                print(f"Auto-selected platform: {platform}")
                break
        else:
            print("Error: No quantum platform available. Please install Qiskit, Cirq, or Braket.")
            sys.exit(1)
    
    # Check if selected platform is available
    if not check_platform_available(args.platform):
        print(f"Error: Selected platform '{args.platform}' is not available.")
        sys.exit(1)
    
    # Create a platform-compatible version of the QASM code
    compatible_qasm = to_platform_compatible_qasm(qasm_str, args.platform)
    
    # Write to a temporary file if needed
    if qasm_str != compatible_qasm:
        print(f"Adapting QASM for {args.platform} compatibility...")
        temp_qasm_file = f"openqasm/temp_{args.platform}.qasm"
        with open(temp_qasm_file, 'w') as f:
            f.write(compatible_qasm)
        qasm_file = temp_qasm_file
    else:
        qasm_file = args.qasm
    
    # Run on the selected platform
    print(f"Running {qasm_file} on {args.platform} platform with {args.shots} shots...")
    
    if args.platform == 'qiskit':
        result = run_on_qiskit(qasm_file, args.shots)
    elif args.platform == 'cirq':
        result = run_on_cirq(qasm_file, args.shots)
    elif args.platform == 'braket':
        result = run_on_braket(qasm_file, args.shots)
    
    # Show the results
    print("\nMeasurement counts:", result.counts)
    print("Probabilities:", result.probabilities)
    
    # Plot and save the results
    output_file = args.output or f"{args.platform}_results.png"
    result.plot(filename=output_file, title=f'Quantum Circuit Results ({args.platform.capitalize()})')
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main() 