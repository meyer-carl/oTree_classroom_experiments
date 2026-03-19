from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIBLING_OTREE = PROJECT_ROOT.parent / "otree"


def main() -> int:
    print(f"python_executable={sys.executable}")
    print(f"project_root={PROJECT_ROOT}")
    print(f"cwd={Path.cwd()}")
    print(f"sibling_otree_exists={SIBLING_OTREE.exists()}")

    if Path.cwd() == PROJECT_ROOT.parent and SIBLING_OTREE.exists():
        print(
            "warning=Running Python from the Teaching directory can shadow the real "
            "oTree package because ./otree exists next to this project."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
