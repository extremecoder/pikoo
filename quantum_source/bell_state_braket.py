import numpy as np
from amazon.braket.circuits import Circuit

# Create a simple Bell state circuit
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure_all()