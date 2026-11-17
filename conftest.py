"""Enable automatic function profiles for all repository pytest commands.

Ported from Gana cf8f0cd850209db676ee5c04184963de8ab06e2a.
Vaelchi-specific adaptations retain the shared checking and profiling policy.
"""

import sys
from pathlib import Path

# The existing quality tools use flat imports from this directory. Loading the
# plugin by name keeps pytest and mypy consistent without an installed package.
_TOOLS = str(Path(__file__).resolve().parent / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
pytest_plugins = ["pytest_profile"]
