# conftest.py
# -----------
# Tells pytest to add the project root to sys.path so that
# `from cyberproof.models import ...` works without installing the package.

import sys
from pathlib import Path

# Insert the project root (the directory containing this file) at the
# front of sys.path.  This lets pytest find the cyberproof/ package.
sys.path.insert(0, str(Path(__file__).parent))
