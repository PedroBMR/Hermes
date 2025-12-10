import os
import sys

# Ensure the ``src`` directory is on the path so the hermes package can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

# Provide a lightweight ``apscheduler`` stub so importing ``hermes.services``
# doesn't require the real dependency during tests.
import tests.apscheduler_stub  # noqa: F401
