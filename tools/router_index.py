# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import config
import knn_router


def main() -> int:
    stale = sorted(config.INDEX_DIR.glob("router-*.npz"))
    path = knn_router.export_index(config.INDEX_DIR)
    for old in stale:
        if old != path:
            old.unlink()
            print(f"removed stale index {old.name}")
    print(f"router index: {path} ({path.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
