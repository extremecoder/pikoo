"""
Platform compatibility utilities for adapting OpenQASM code across quantum platforms.
"""

def to_platform_compatible_qasm(original_qasm, target_platform):
    """
    Convert OpenQASM to be compatible with specific platforms.
    
    Args:
        original_qasm (str): The original OpenQASM code
        target_platform (str): Target platform ('qiskit', 'cirq', 'braket')
        
    Returns:
        str: OpenQASM code compatible with the target platform
    """
    lines = original_qasm.split('\n')
    compatible_lines = []
    
    # Track whether version and includes have been processed
    version_updated = False
    include_processed = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            compatible_lines.append(line)
            continue
            
        # Handle platform-specific gate adaptations
        if 'barrier' in line and target_platform == 'cirq':
            compatible_lines.append(f"// {line}  # skipped for Cirq compatibility")
            continue
        
        # Handle OpenQASM version differences
        if 'OPENQASM 2.0' in line:
            if target_platform == 'braket':
                compatible_lines.append('OPENQASM 3;')
                version_updated = True
            else:
                compatible_lines.append(line)
                version_updated = True
            continue
            
        # Handle include statements
        if 'include' in line and 'qelib1.inc' in line:
            if target_platform == 'braket':
                # Skip qelib1.inc for Braket as it uses native gates
                compatible_lines.append(f"// {line}  # skipped for Braket compatibility")
                include_processed = True
            else:
                compatible_lines.append(line)
                include_processed = True
            continue
            
        # Handle gate name differences
        if target_platform == 'braket':
            # Replace cx with cnot for Braket
            if ' cx ' in line or line.startswith('cx '):
                line = line.replace('cx ', 'cnot ')
                
        # Add the line to the compatible lines
        compatible_lines.append(line)
    
    # Ensure version and include are present
    if not version_updated:
        if target_platform == 'braket':
            compatible_lines.insert(0, 'OPENQASM 3;')
        else:
            compatible_lines.insert(0, 'OPENQASM 2.0;')
            
    if not include_processed and target_platform != 'braket':
        if target_platform in ['qiskit', 'cirq']:
            compatible_lines.insert(1, 'include "qelib1.inc";')
    
    return '\n'.join(compatible_lines)

def validate_cross_platform(qasm_str):
    """
    Check if QASM code is compatible with all platforms.
    
    Args:
        qasm_str (str): The OpenQASM code to validate
        
    Returns:
        list: List of compatibility issues
    """
    issues = []
    
    # Check for Cirq-incompatible gates
    if 'barrier' in qasm_str:
        issues.append("Warning: 'barrier' gate is not supported in Cirq")
    
    # Check for OpenQASM version
    if 'OPENQASM 3' in qasm_str:
        issues.append("Warning: OpenQASM 3.0 is not fully supported by all platforms")
    
    # Check for custom gates which might not be cross-platform
    if 'gate ' in qasm_str:
        issues.append("Warning: Custom gate definitions may not be portable across platforms")
    
    return issues 