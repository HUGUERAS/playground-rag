from __future__ import annotations

import sys
from pathlib import Path


def bootstrap_shared_types() -> None:
    """Allow local imports from packages/shared-types without installation."""
    current = Path(__file__).resolve()
    repo_root = current.parents[3]
    shared_types_src = repo_root / "packages" / "shared-types" / "src"
    shared_types_path = str(shared_types_src)
    if shared_types_src.exists() and shared_types_path not in sys.path:
        sys.path.insert(0, shared_types_path)
