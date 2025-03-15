"""
Standardized quantum result format for cross-platform compatibility.
"""
import matplotlib.pyplot as plt
import numpy as np

class QuantumResult:
    """
    A platform-independent quantum result representation.
    """
    
    def __init__(self, counts, metadata=None):
        """
        Initialize a quantum result.
        
        Args:
            counts (dict): Dictionary mapping bitstrings to counts
            metadata (dict, optional): Additional metadata about the result
        """
        self.counts = counts  # Dictionary of bitstring:count
        self.metadata = metadata or {}
        self._normalize_counts()
    
    def _normalize_counts(self):
        """Ensure counts are in a consistent format"""
        # Ensure all keys are strings
        self.counts = {str(k): v for k, v in self.counts.items()}
    
    @property
    def total_shots(self):
        """Get the total number of shots"""
        return sum(self.counts.values())
    
    @property
    def probabilities(self):
        """Get the probabilities for each outcome"""
        total = self.total_shots
        return {k: v / total for k, v in self.counts.items()} if total > 0 else {}
    
    def plot(self, filename=None, title='Quantum Circuit Results', figsize=(8, 6)):
        """
        Plot results in a standard format.
        
        Args:
            filename (str, optional): Filename to save the plot
            title (str): Title for the plot
            figsize (tuple): Figure dimensions (width, height)
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        # Sort keys for consistent display
        sorted_keys = sorted(self.counts.keys())
        values = [self.counts[k] for k in sorted_keys]
        
        ax.bar(sorted_keys, values)
        ax.set_xlabel('Measurement Outcome')
        ax.set_ylabel('Counts')
        ax.set_title(title)
        
        # If too many outcomes, rotate labels
        if len(sorted_keys) > 5:
            plt.xticks(rotation=45, ha='right')
            
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename)
            
        return fig
    
    @classmethod
    def from_qiskit_result(cls, result, metadata=None):
        """
        Create a QuantumResult from a Qiskit result.
        
        Args:
            result: Qiskit Result object
            metadata (dict, optional): Additional metadata
            
        Returns:
            QuantumResult: Standardized result
        """
        if hasattr(result, 'get_counts'):
            counts = result.get_counts()
            # Convert format if needed (Qiskit sometimes uses different formats)
            if isinstance(counts, list) and len(counts) > 0:
                counts = counts[0]
        else:
            counts = {}
            
        return cls(counts, metadata)
    
    @classmethod
    def from_cirq_result(cls, result, metadata=None):
        """
        Create a QuantumResult from a Cirq result.
        
        Args:
            result: Cirq Result object
            metadata (dict, optional): Additional metadata
            
        Returns:
            QuantumResult: Standardized result
        """
        keys = list(result.measurements.keys())
        count_dict = {}
        
        if not keys:
            return cls({}, metadata)
            
        if len(keys) == 1 and len(result.measurements[keys[0]][0]) > 1:
            # Single measurement gate with multiple qubits
            key = keys[0]
            measurements = result.measurements[key]
            measurement_strings = [''.join(str(bit) for bit in bits) for bits in measurements]
            unique, counts = np.unique(measurement_strings, return_counts=True)
            count_dict = dict(zip(unique, counts))
        elif len(keys) > 1:
            # Multiple measurement gates
            try:
                sorted_keys = sorted(keys, key=lambda k: int(k.split('_')[-1]) if '_' in k else k)
            except (ValueError, IndexError):
                sorted_keys = sorted(keys)
                
            combined_measurements = []
            for i in range(len(result.measurements[keys[0]])):
                combined = ''
                for key in sorted_keys:
                    bits = result.measurements[key][i]
                    if len(bits) == 1:
                        combined += str(bits[0])
                    else:
                        combined += ''.join(str(bit) for bit in bits)
                combined_measurements.append(combined)
                
            unique, counts = np.unique(combined_measurements, return_counts=True)
            count_dict = dict(zip(unique, counts))
        else:
            # Single measurement gate with single qubit
            key = keys[0]
            measurements = result.measurements[key]
            measurement_strings = [str(bits[0]) for bits in measurements]
            unique, counts = np.unique(measurement_strings, return_counts=True)
            count_dict = dict(zip(unique, counts))
            
        return cls(count_dict, metadata)
    
    @classmethod
    def from_braket_result(cls, result, metadata=None):
        """
        Create a QuantumResult from a Braket result.
        
        Args:
            result: Braket Result object
            metadata (dict, optional): Additional metadata
            
        Returns:
            QuantumResult: Standardized result
        """
        if hasattr(result, 'measurement_counts') and result.measurement_counts:
            counts = result.measurement_counts
            # Braket returns Counter objects, convert to dict
            if hasattr(counts, 'items'):
                counts = dict(counts)
        else:
            counts = {}
            
        return cls(counts, metadata) 