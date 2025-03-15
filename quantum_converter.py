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
    from braket.circuits import Circuit
    BRAKET_AVAILABLE = True
    print("Successfully imported Braket")
except ImportError:
    BRAKET_AVAILABLE = False
    print("Failed to import Braket: package not available")

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
    """Converter for Amazon Braket quantum circuits to OpenQASM format.
    
    This converter uses the qiskit-braket-provider package to convert Braket circuits
    to Qiskit circuits, which can then be converted to OpenQASM format.
    
    Attributes:
        circuit: The Braket quantum circuit to convert.
    """
    def __init__(self, circuit: 'Circuit'):
        if not BRAKET_AVAILABLE:
            raise ImportError("AWS Braket is not available. Please install the amazon-braket-sdk package.")
        self.circuit = circuit

    def to_openqasm(self) -> str:
        """Convert the Braket circuit to OpenQASM format.
        
        Returns:
            str: The OpenQASM representation of the circuit.
            
        Raises:
            ImportError: If required packages are not available.
            RuntimeError: If the conversion fails.
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Braket to OpenQASM conversion. Please install the qiskit package.")
        
        # Check if qiskit-braket-provider is available
        try:
            import importlib
            qbp_spec = importlib.util.find_spec("qiskit_braket_provider")
            if qbp_spec is None:
                raise ImportError("qiskit-braket-provider package is required for Braket to OpenQASM conversion.")
        except ImportError:
            raise ImportError("qiskit-braket-provider package is required for Braket to OpenQASM conversion. " 
                              "Please install it with: pip install qiskit-braket-provider")
        
        print("Converting Braket circuit to OpenQASM...")
        
        try:
            # Use the to_qiskit function from qiskit_braket_provider.providers
            from qiskit_braket_provider.providers import to_qiskit
            qiskit_circuit = to_qiskit(self.circuit)
            print("Successfully converted Braket circuit to Qiskit format")
            return dumps(qiskit_circuit)
        except Exception as e:
            # If the primary method fails, try the adapter module directly
            try:
                from qiskit_braket_provider.providers import adapter
                qiskit_circuit = adapter.to_qiskit(self.circuit)
                print("Successfully converted Braket circuit using adapter module")
                return dumps(qiskit_circuit)
            except Exception:
                # If both methods fail, raise a clear error message
                raise RuntimeError(f"Failed to convert Braket circuit to OpenQASM: {str(e)}")



def load_circuit_from_source(source_dir: str = "quantum_source") -> Optional[QuantumConverter]:
    """Load quantum circuit from source files based on platform.
    
    Args:
        source_dir: Directory containing quantum circuit source files
        
    Returns:
        QuantumConverter: A converter for the loaded circuit
        
    Raises:
        ImportError: If no valid circuit is found or required packages are missing
    """
    platform = os.getenv("QUANTUM_PLATFORM", "qiskit").lower()
    print(f"Loading circuit for platform: {platform}")
    
    # Ensure source directory exists
    Path(source_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if the requested platform is available
    if platform == "qiskit" and not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is not available. Please install the qiskit package.")
    elif platform == "cirq" and not CIRQ_AVAILABLE:
        raise ImportError("Cirq is not available. Please install the cirq package.")
    elif platform == "braket" and not BRAKET_AVAILABLE:
        raise ImportError("AWS Braket SDK is not available. Please install the amazon-braket-sdk package.")
    
    # Load circuit based on platform
    try:
        for file in Path(source_dir).glob("*.py"):
            content = file.read_text()
            
            if platform == "qiskit" and "QuantumCircuit" in content:
                print(f"Found Qiskit file: {file}")
                namespace = {}
                exec(content, namespace)
                for obj in namespace.values():
                    if isinstance(obj, QuantumCircuit):
                        print("Successfully loaded Qiskit circuit")
                        return QiskitConverter(obj)
            
            elif platform == "cirq" and "cirq" in content:
                print(f"Found Cirq file: {file}")
                namespace = {}
                exec(content, namespace)
                for obj in namespace.values():
                    if isinstance(obj, cirq.Circuit):
                        print("Successfully loaded Cirq circuit")
                        return CirqConverter(obj)
            
            elif platform == "braket" and "braket" in content and "circuit" in content:
                print(f"Found Braket file: {file}")
                namespace = {}
                exec(content, namespace)
                for obj_name, obj in namespace.items():
                    if obj_name == 'circuit' and isinstance(obj, Circuit):
                        print("Successfully loaded Braket circuit")
                        return BraketConverter(obj)
        
        # If we get here, no valid circuit was found
        raise ImportError(f"No valid circuit found for platform {platform} in {source_dir}")
            
    except Exception as e:
        if isinstance(e, ImportError):
            raise
        print(f"Error loading circuit: {str(e)}")
        raise ImportError(f"Failed to load circuit: {str(e)}")

def main():
    """Main function to load a quantum circuit and convert it to OpenQASM format."""
    try:
        converter = load_circuit_from_source()
        qasm_code = converter.to_openqasm()
        
        output_path = Path("openqasm/sample.qasm")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(qasm_code)
        
        print(f"Successfully converted circuit to OpenQASM and saved to {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()