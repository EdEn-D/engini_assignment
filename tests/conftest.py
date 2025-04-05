import os
import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ["LOG_LEVEL"] = "ERROR"
os.environ["TEMP_DIR"] = "tests/temp"
