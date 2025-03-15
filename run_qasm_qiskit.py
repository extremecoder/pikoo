"""
Run OpenQASM file on Qiskit simulator
"""
from qiskit import QuantumCircuit
import qiskit_aer
import matplotlib.pyplot as plt

# Load QASM from file
try:
    with open('openqasm/sample.qasm', 'r') as f:
        qasm_str = f.read()

    # Create a circuit from QASM
    circuit = QuantumCircuit.from_qasm_str(qasm_str)
    print("Loaded QASM circuit on Qiskit simulator:")
    print(circuit)

    # Run the circuit on the QASM simulator
    simulator = qiskit_aer.AerSimulator()
    job = simulator.run(circuit, shots=1000)
    result = job.result()

    # Get and print the measurement counts
    if hasattr(result, 'get_counts'):
        counts = result.get_counts()
        if counts:
            print("\nMeasurement counts:", counts)
            
            # Plot histogram
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            ax.bar(counts.keys(), counts.values())
            ax.set_xlabel('Measurement Outcome')
            ax.set_ylabel('Counts')
            ax.set_title('Quantum Circuit Measurement Results (Qiskit Simulator)')
            plt.savefig('qiskit_results.png')
            print("Results saved to qiskit_results.png")
        else:
            print("\nNo measurement results found in the circuit output")
            # Create an empty plot
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No measurement results available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            ax.set_title('Quantum Circuit Results (Qiskit Simulator)')
            plt.savefig('qiskit_results.png')
            print("Empty results plot saved to qiskit_results.png")
    else:
        print("Error: Result does not have get_counts method")

except Exception as e:
    print(f"Error running QASM file on Qiskit simulator: {e}")
