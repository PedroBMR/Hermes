import os
import sys

# Ensure the parent directory is on the path so the Hermes package can be imported.
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
