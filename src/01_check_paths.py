"""Validate that paths.local.yaml points at layers that exist in ArcGIS Pro."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import load_paths, require_arcpy  # noqa: E402

REQUIRED = [
    "hexes",
    "hex_id_field",
    "wfe_mean_field",
]

RECOMMENDED = [
    "aoi",
    "wrtc_housing_exposure",
    "landfire_evt",
    "padus",
]


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    print("Repo:", cfg["_repo_root"])
    print("Checking required inputs…")
    ok = True
    for key in REQUIRED:
        val = cfg.get(key, "")
        if not val:
            print(f"  MISSING config: {key}")
            ok = False
            continue
        if key.endswith("_field"):
            print(f"  OK config: {key} = {val}")
            continue
        exists = arcpy.Exists(val)
        print(f"  {'OK' if exists else 'NOT FOUND'}: {key} -> {val}")
        ok = ok and exists

    print("Recommended (fill when ready):")
    for key in RECOMMENDED:
        val = cfg.get(key, "")
        if not val:
            print(f"  empty: {key}")
            continue
        print(f"  {'OK' if arcpy.Exists(val) else 'NOT FOUND'}: {key} -> {val}")

    if not ok:
        raise SystemExit(1)
    print("Required paths look good.")


if __name__ == "__main__":
    main()
