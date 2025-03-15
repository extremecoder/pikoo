import numpy as np
from braket.circuits import Circuit

# Create a simple Bell state circuit
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)

# Add measurements individually instead of using measure_all()
circuit.measure(0)
circuit.measure(1)