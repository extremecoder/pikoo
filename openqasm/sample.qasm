// Generated from Cirq v1.4.1

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(0), q(1)]
qreg q[2];
creg m0[2];  // Measurement: q(0),q(1)


h q[0];
cx q[0],q[1];

// Gate: cirq.MeasurementGate(2, cirq.MeasurementKey(name='q(0),q(1)'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
