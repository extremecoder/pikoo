from qiskit import QuantumCircuit

# Create a Bell state circuit using Qiskit
circuit = QuantumCircuit(2, 2)
circuit.h(0)      # Apply Hadamard to first qubit
circuit.cx(0, 1)  # CNOT with control=first qubit, target=second qubit
circuit.measure_all()