#!/usr/bin/env python
"""
Test runner script to run all tests in the project.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run only unit tests
    python run_tests.py integration  # Run only integration tests
    python run_tests.py -v           # Verbose output
    python run_tests.py -k test_name # Run specific test pattern
"""

import sys
import subprocess
import os

def main():
    """Run all tests using pytest."""
    # Change to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Set PYTHONPATH to include the current directory
    env = os.environ.copy()
    env['PYTHONPATH'] = script_dir
    
    # Build pytest command
    pytest_args = ['python', '-m', 'pytest', 'app/test']
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'unit':
            pytest_args.append('app/test/unit')
        elif sys.argv[1] == 'integration':
            pytest_args.append('app/test/integration')
        else:
            # Pass through other arguments (like -v, -k, etc.)
            pytest_args.extend(sys.argv[1:])
    
    # Run pytest
    result = subprocess.run(pytest_args, env=env)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()

