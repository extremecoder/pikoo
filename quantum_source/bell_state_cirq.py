import cirq

# Create a Bell state circuit using Cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit()

# Add gates
circuit.append(cirq.H(q0))            # Hadamard on first qubit
circuit.append(cirq.CNOT(q0, q1))     # CNOT between qubits
circuit.append(cirq.measure(q0, q1))   # Measure both qubits