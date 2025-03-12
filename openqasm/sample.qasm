OPENQASM 2.0;
include "qelib1.inc";

// Initialize quantum and classical registers
qreg q[2];
creg c[2];

// Create a Bell state
h q[0];      // Hadamard on first qubit
cx q[0],q[1];  // CNOT with first qubit as control, second as target

// Measure both qubits
measure q[0] -> c[0];
measure q[1] -> c[1];
