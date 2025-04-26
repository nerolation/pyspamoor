#!/usr/bin/env python3
"""
Wrapper script to run py_spamoor CLI directly.
"""
import sys
import os

# When running from repository root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from py_spamoor.cli import main
except ImportError:
    # Try relative import
    try:
        from cli import main
    except ImportError:
        # Try with full path
        from py_spamoor.cli import main

if __name__ == "__main__":
    sys.exit(main()) 