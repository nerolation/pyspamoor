"""Main entry point for the py_spamoor package."""

import sys
import os

# Add the parent directory to sys.path to allow direct execution
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from py_spamoor.cli import main
except ImportError:
    from cli import main

if __name__ == "__main__":
    sys.exit(main()) 