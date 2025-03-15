"""
Run OpenQASM file on Cirq simulator
"""
import cirq
import cirq_google
from cirq.contrib.qasm_import import circuit_from_qasm
import matplotlib.pyplot as plt
import numpy as np
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run OpenQASM on Cirq simulator')
parser.add_argument('--qasm', default='openqasm/sample_cirq.qasm', help='Path to QASM file')
parser.add_argument('--shots', type=int, default=1000, help='Number of shots to run')
args = parser.parse_args()

# Load QASM from file
try:
    with open(args.qasm, 'r') as f:
        qasm_str = f.read()

    print(f"Running {args.qasm} on Cirq simulator...")

    # Create a circuit from QASM
    circuit = circuit_from_qasm(qasm_str)
    print("Loaded QASM circuit on Cirq simulator:")
    print(circuit)

    # Run the circuit on the Cirq simulator
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=args.shots)

    # Get and print the measurement counts
    # For Cirq, we need to handle the measurement results differently

    # Extract all measurement keys
    keys = list(result.measurements.keys())
    print("Measurement keys:", keys)

    # Process the measurement results
    if not keys:
        print("Warning: No measurement results found in the circuit output")
        count_dict = {}
    elif len(keys) == 1 and len(result.measurements[keys[0]][0]) > 1:
        # Case 1: Single measurement gate measuring multiple qubits
        key = keys[0]
        measurements = result.measurements[key]
        
        # Convert each measurement array to a string
        measurement_strings = [''.join(str(bit) for bit in bits) for bits in measurements]
        unique, counts = np.unique(measurement_strings, return_counts=True)
        count_dict = dict(zip(unique, counts))
    elif len(keys) > 1:
        # Case 2: Multiple measurement gates (typically one per qubit)
        # Sort keys to ensure consistent ordering (assuming keys like 'q0', 'q1', etc.)
        try:
            # Try to sort numerically if keys follow a pattern like 'm0_0', 'm0_1'
            sorted_keys = sorted(keys, key=lambda k: int(k.split('_')[-1]) if '_' in k else k)
        except (ValueError, IndexError):
            # Fall back to lexicographical sort
            sorted_keys = sorted(keys)
        
        # Combine measurements from different keys
        combined_measurements = []
        for i in range(len(result.measurements[keys[0]])):
            combined = ''
            for key in sorted_keys:
                # Handle both single-bit and multi-bit measurements
                bits = result.measurements[key][i]
                if len(bits) == 1:
                    combined += str(bits[0])
                else:
                    combined += ''.join(str(bit) for bit in bits)
            combined_measurements.append(combined)
        
        unique, counts = np.unique(combined_measurements, return_counts=True)
        count_dict = dict(zip(unique, counts))
    else:
        # Case 3: Single measurement gate measuring a single qubit
        key = keys[0]
        measurements = result.measurements[key]
        
        # Convert to strings (e.g., '0' or '1')
        measurement_strings = [str(bits[0]) for bits in measurements]
        unique, counts = np.unique(measurement_strings, return_counts=True)
        count_dict = dict(zip(unique, counts))
    print("\nMeasurement counts:", count_dict)

    # Plot histogram
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.bar(count_dict.keys(), count_dict.values())
    ax.set_xlabel('Measurement Outcome')
    ax.set_ylabel('Counts')
    ax.set_title('Quantum Circuit Measurement Results (Cirq Simulator)')
    plt.savefig('cirq_results.png')
    print("Results saved to cirq_results.png")

except Exception as e:
    print(f"Error running QASM file on Cirq simulator: {e}")
