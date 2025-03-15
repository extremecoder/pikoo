"""
Standard gate definitions and translations for cross-platform quantum computing.
"""

class GateTranslator:
    """
    Translates gates between different quantum computing platforms.
    """
    
    # Standard gates supported across platforms
    STANDARD_GATES = {
        'x', 'y', 'z',           # Pauli gates
        'h',                      # Hadamard gate
        'cx', 'cnot',             # CNOT gate (different names in different platforms)
        's', 'sdg',               # S and S-dagger gates
        't', 'tdg',               # T and T-dagger gates
        'rx', 'ry', 'rz',         # Rotation gates
        'u1', 'u2', 'u3',         # Universal gates
        'swap',                   # SWAP gate
        'ccx', 'toffoli',         # Toffoli gate
        'measure'                 # Measurement operation
    }
    
    # Gate mappings between platforms (from: {to_platform: to_name})
    GATE_MAPPINGS = {
        'cx': {
            'braket': 'cnot',
            'qiskit': 'cx',
            'cirq': 'cx'
        },
        'ccx': {
            'braket': 'ccnot',
            'qiskit': 'ccx',
            'cirq': 'ccx'
        },
        'barrier': {
            'qiskit': 'barrier',
            'braket': 'barrier',
            'cirq': None  # Not supported in Cirq
        },
        'id': {
            'braket': 'i',
            'qiskit': 'id',
            'cirq': 'i'  
        }
    }
    
    @staticmethod
    def translate_gate(gate_name, source_platform, target_platform):
        """
        Translate a gate from source platform to target platform.
        
        Args:
            gate_name (str): Gate name in the source platform
            source_platform (str): Source platform ('qiskit', 'cirq', 'braket')
            target_platform (str): Target platform ('qiskit', 'cirq', 'braket')
            
        Returns:
            str or None: Gate name in the target platform, or None if not supported
        """
        # Check if gate is in our mapping
        if gate_name in GateTranslator.GATE_MAPPINGS:
            mapping = GateTranslator.GATE_MAPPINGS[gate_name]
            if target_platform in mapping:
                return mapping[target_platform]
        
        # Standard gates that have the same name across platforms
        if gate_name in GateTranslator.STANDARD_GATES:
            return gate_name
            
        # Unknown gate - return as is and hope for the best
        return gate_name
    
    @staticmethod
    def is_supported(gate_name, platform):
        """
        Check if a gate is supported on a given platform.
        
        Args:
            gate_name (str): Gate name
            platform (str): Platform name ('qiskit', 'cirq', 'braket')
            
        Returns:
            bool: True if supported, False otherwise
        """
        # Check if gate is in our mapping
        if gate_name in GateTranslator.GATE_MAPPINGS:
            mapping = GateTranslator.GATE_MAPPINGS[gate_name]
            if platform in mapping:
                return mapping[platform] is not None
        
        # Standard gates are assumed to be supported
        return gate_name in GateTranslator.STANDARD_GATES

def get_platform_gate_set(platform):
    """
    Get the set of gates supported by a platform.
    
    Args:
        platform (str): Platform name ('qiskit', 'cirq', 'braket')
        
    Returns:
        set: Set of supported gate names
    """
    supported_gates = set()
    
    # Add all standard gates
    for gate in GateTranslator.STANDARD_GATES:
        if GateTranslator.is_supported(gate, platform):
            supported_gates.add(gate)
    
    # Add platform-specific gates from mappings
    for gate, mappings in GateTranslator.GATE_MAPPINGS.items():
        if platform in mappings and mappings[platform] is not None:
            supported_gates.add(gate)
    
    return supported_gates 