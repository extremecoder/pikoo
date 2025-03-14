import os
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
import sys
import importlib.util

# Import Qiskit
try:
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.qasm2 import dumps
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

# Import Cirq
try:
    import cirq
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False

# Import Braket
try:
    from amazon.braket.circuits import Circuit
    BRAKET_AVAILABLE = True
except ImportError:
    BRAKET_AVAILABLE = False

class QuantumConverter(ABC):
    @abstractmethod
    def to_openqasm(self) -> str:
        pass

class QiskitConverter(QuantumConverter):
    def __init__(self, circuit: 'QuantumCircuit'):
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is not available")
        self.circuit = circuit

    def to_openqasm(self) -> str:
        return dumps(self.circuit)

class CirqConverter(QuantumConverter):
    def __init__(self, circuit: 'cirq.Circuit'):
        if not CIRQ_AVAILABLE:
            raise ImportError("Cirq is not available")
        self.circuit = circuit

    def to_openqasm(self) -> str:
        return self.circuit.to_qasm()

class BraketConverter(QuantumConverter):
    def __init__(self, circuit: 'Circuit'):
        if not BRAKET_AVAILABLE:
            raise ImportError("AWS Braket is not available")
        self.circuit = circuit

    def to_openqasm(self) -> str:
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Braket to OpenQASM conversion")
            
        try:
            print("Converting Braket circuit to OpenQASM via Qiskit...")
            qiskit_circuit = self.circuit.to_ir(
                ir_type='qiskit',
                mapping_family='default'
            )
            return dumps(qiskit_circuit)
        except Exception as e:
            print(f"Error converting Braket circuit to OpenQASM: {str(e)}")
            raise

def load_braket_module(file_path: Path):
    """Load a Python module from file path."""
    try:
        spec = importlib.util.spec_from_file_location("braket_circuit", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module {file_path}: {e}")
        return None

def load_circuit_from_source(source_dir: str = "quantum_source") -> Optional[QuantumConverter]:
    """Load quantum circuit from source files based on platform."""
    platform = os.getenv("QUANTUM_PLATFORM", "qiskit").lower()
    print(f"Loading circuit for platform: {platform}")
    
    Path(source_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        if platform == "qiskit" and QISKIT_AVAILABLE:
            for file in Path(source_dir).glob("*.py"):
                if "QuantumCircuit" in file.read_text():
                    namespace = {}
                    exec(file.read_text(), namespace)
                    for obj in namespace.values():
                        if isinstance(obj, QuantumCircuit):
                            return QiskitConverter(obj)
        
        elif platform == "cirq" and CIRQ_AVAILABLE:
            for file in Path(source_dir).glob("*.py"):
                if "cirq" in file.read_text():
                    namespace = {}
                    exec(file.read_text(), namespace)
                    for obj in namespace.values():
                        if isinstance(obj, cirq.Circuit):
                            return CirqConverter(obj)
        
        elif platform == "braket" and BRAKET_AVAILABLE:
            for file in Path(source_dir).glob("*.py"):
                content = file.read_text()
                if "braket" in content:
                    print(f"Found Braket file: {file}")
                    # Load module directly
                    module = load_braket_module(file)
                    if module and hasattr(module, 'circuit'):
                        circuit = module.circuit
                        if isinstance(circuit, Circuit):
                            print(f"Successfully loaded Braket circuit")
                            return BraketConverter(circuit)
        
        raise ImportError(f"No valid circuit found for platform {platform}")
            
    except Exception as e:
        print(f"Error loading circuit: {str(e)}")
        raise

def main():
    try:
        converter = load_circuit_from_source()
        if not converter:
            raise ValueError("Failed to load quantum circuit")
        
        qasm_code = converter.to_openqasm()
        
        output_path = Path("openqasm/sample.qasm")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(qasm_code)
        
        print(f"Successfully converted circuit to OpenQASM and saved to {output_path}")
        
    except Exception as e:
        print(f"Error converting circuit: {str(e)}")
        raise

if __name__ == "__main__":
    main()