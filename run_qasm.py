#!/usr/bin/env python3
"""
Unified runner script for OpenQASM circuits across different quantum platforms.
This script serves as an entry point that delegates to platform-specific runners.
"""
import argparse
import os
import sys
import importlib.util
from pathlib import Path

def check_platform_available(platform):
    """Check if the specified platform is available in the environment"""
    if platform == "qiskit":
        try:
            import qiskit
            return True
        except ImportError:
            return False
    elif platform == "cirq":
        try:
            import cirq
            return True
        except ImportError:
            return False
    elif platform == "braket":
        try:
            from braket.circuits import Circuit
            return True
        except ImportError:
            return False
    return False

def main():
    """Main function to parse arguments and run the appropriate platform-specific runner"""
    parser = argparse.ArgumentParser(description="Run OpenQASM circuits on different quantum platforms")
    parser.add_argument(
        "--platform", 
        choices=["qiskit", "cirq", "braket", "auto"],
        default="auto",
        help="Quantum platform to use for simulation (default: auto)"
    )
    parser.add_argument(
        "--qasm-file", 
        default="openqasm/sample.qasm",
        help="Path to the OpenQASM file (default: openqasm/sample.qasm)"
    )
    parser.add_argument(
        "--shots", 
        type=int, 
        default=1000,
        help="Number of shots for the simulation (default: 1000)"
    )
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Run test cases against the circuit"
    )
    
    args = parser.parse_args()
    
    # Determine the platform to use
    platform = args.platform
    
    if platform == "auto":
        # Try platforms in order of preference
        for p in ["qiskit", "cirq", "braket"]:
            if check_platform_available(p):
                platform = p
                print(f"Auto-selected platform: {platform}")
                break
        
        if platform == "auto":
            print("Error: No quantum platform available. Please install qiskit, cirq, or braket.")
            sys.exit(1)
    
    # Check if the selected platform is available
    if not check_platform_available(platform):
        print(f"Error: {platform} is not available. Please install the required package.")
        sys.exit(1)
    
    # Check if the QASM file exists
    qasm_file = Path(args.qasm_file)
    if not qasm_file.exists():
        print(f"Error: QASM file not found: {qasm_file}")
        sys.exit(1)
    
    # Run the appropriate platform-specific runner
    if args.test:
        # Run test cases using test_runner.py
        print(f"Running test cases for {qasm_file} using test_runner.py")
        try:
            from test_runner import QASMTestRunner
            runner = QASMTestRunner(
                qasm_file=str(qasm_file),
                test_cases_file="openqasm/test_cases.json"
            )
            results = runner.run_all_tests()
            
            # Print summary
            print("\nTest Summary:")
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r['result']['success'])
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            
        except Exception as e:
            print(f"Error running tests: {str(e)}")
            sys.exit(1)
    else:
        # Run the platform-specific runner
        runner_file = f"run_qasm_{platform}.py"
        
        if not Path(runner_file).exists():
            print(f"Error: Runner file not found: {runner_file}")
            sys.exit(1)
        
        print(f"Running {qasm_file} on {platform} platform")
        
        # Import and run the platform-specific runner
        try:
            spec = importlib.util.spec_from_file_location("runner", runner_file)
            runner_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner_module)
            
            # If the platform-specific runner has a main function, call it
            if hasattr(runner_module, "main"):
                runner_module.main()
            
        except Exception as e:
            print(f"Error running {platform} runner: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
