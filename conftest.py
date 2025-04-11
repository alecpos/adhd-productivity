"""Root level conftest to help with imports."""

import os
import sys
from pathlib import Path

# Get the root directory of the project
root_dir = Path(__file__).parent

# Add the root directory to Python path
sys.path.insert(0, str(root_dir)) 