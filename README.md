# Pikoo - Quantum Circuit Simulator

A multi-platform quantum circuit simulator that supports OpenQASM circuits and provides testing capabilities across different quantum computing frameworks.

## Overview

Pikoo allows you to:
1. Convert quantum circuits from different platforms (Qiskit, Cirq, Braket) to OpenQASM format
2. Run OpenQASM circuits on different quantum simulators
3. Generate and run test cases for quantum circuits
4. Visualize measurement results

## Supported Platforms

- [Qiskit](https://qiskit.org/) (IBM)
- [Cirq](https://quantumai.google/cirq) (Google)
- [Braket](https://aws.amazon.com/braket/) (Amazon)

## Project Structure

```
pikoo/
├── openqasm/                  # OpenQASM circuit files
│   ├── sample.qasm            # Sample Bell state circuit
│   └── test_cases.json        # Test cases for the circuit
├── quantum_source/            # Source circuits for different platforms
│   ├── bell_state_qiskit.py   # Bell state circuit in Qiskit
│   ├── bell_state_cirq.py     # Bell state circuit in Cirq
│   └── bell_state_braket.py   # Bell state circuit in Braket
├── quantum_converter.py       # Converts circuits to OpenQASM format
├── run_qasm_qiskit.py         # Run OpenQASM on Qiskit simulator
├── run_qasm_cirq.py           # Run OpenQASM on Cirq simulator
├── run_qasm_braket.py         # Run OpenQASM on Braket simulator
├── test_runner.py             # Run test cases against OpenQASM circuits
└── qasm_test_generator.py     # Generate test cases for OpenQASM circuits
```

## Usage

### Converting Circuits to OpenQASM

```bash
# Set the quantum platform environment variable
export QUANTUM_PLATFORM=qiskit  # or cirq, braket

# Convert the circuit to OpenQASM
python quantum_converter.py
```

### Running OpenQASM Circuits

Run circuits on any platform: python run_qasm.py --platform [qiskit|cirq|braket]
Run test cases: python run_qasm.py --test
Specify custom QASM files: python run_qasm.py --qasm-file path/to/file.qasm


```bash
# Run on Qiskit simulator
python run_qasm_qiskit.py

# Run on Cirq simulator
python run_qasm_cirq.py

# Run on Braket simulator
python run_qasm_braket.py
```

### Running Test Cases

```bash
# Run test cases against the OpenQASM circuit
python test_runner.py
```

### Generating Test Cases

```bash
# Generate test cases for an OpenQASM circuit
python qasm_test_generator.py
```

## Example Circuit

The sample.qasm file contains a Bell state generator circuit:

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

This circuit creates an entangled state (|00⟩ + |11⟩)/√2 when starting with |00⟩ as input.

## Dependencies

- Python 3.8+
- Qiskit
- Cirq
- Amazon Braket SDK
- matplotlib
- numpy

Install dependencies with:

```bash
pip install qiskit qiskit-aer cirq amazon-braket-sdk matplotlib numpy
```

## License

This project is open source and available under the [MIT License](LICENSE).