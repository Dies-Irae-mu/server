#!/usr/bin/env python3
"""
Test runner for movement bug fix tests.

Usage:
    python run_movement_tests.py

This script runs the movement bug fix verification tests using pytest.
"""

import os
import sys
import subprocess


def run_tests():
    """Run the movement bug fix tests using pytest."""
    print("Running Movement Bug Fix Tests with pytest")
    print("=" * 50)
    
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, "tests", "test_movement_simple.py")
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest", 
        test_file,
        "-v",  # verbose output
        "--tb=short",  # shorter traceback format
        "--no-header",  # cleaner output
    ]
    
    try:
        result = subprocess.run(cmd, cwd=script_dir, check=False)
        
        # Print summary
        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("✅ All tests passed! The movement bug fix is working.")
        else:
            print("❌ Some tests failed. Please check the output above.")
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest:")
        print("   pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_simple_tests():
    """Run the simple verification tests directly."""
    print("Running Simple Movement Bug Fix Verification")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, "tests", "test_movement_simple.py")
    
    try:
        result = subprocess.run([sys.executable, test_file], cwd=script_dir, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running simple tests: {e}")
        return False


if __name__ == "__main__":
    # Try pytest first, fall back to simple tests
    success = run_tests()
    if not success:
        print("\nFalling back to simple test runner...")
        success = run_simple_tests()
    
    sys.exit(0 if success else 1) 