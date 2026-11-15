"""Rend le dépôt importable par les tests (python -m pytest depuis la racine)."""

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
