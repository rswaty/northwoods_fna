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
    "wrtc_building_density",
    "wrtc_housing_unit_density",
    "wrtc_housing_unit_risk",
    "wrtc_housing_unit_exposure",
    "landfire_evt",
    "landfire_bps",
    "landfire_fdist",
    "padus",
]


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    print("Repo:", cfg["_repo_root"])
    print(
        "v1: people = Building Density; WFE = hazard; "
        "PAD GAP 1-3 context; EVT = peat + plantations"
    )
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

    # Primary people raster = Building Density
    building = cfg.get("wrtc_building_density", "")
    if building:
        exists = arcpy.Exists(building)
        print(
            f"  {'OK' if exists else 'NOT FOUND'}: "
            f"wrtc_building_density (PRIMARY people) -> {building}"
        )
        ok = ok and exists
    else:
        print(
            "  empty: wrtc_building_density "
            "(PRIMARY — set before 02_zonal_wrtc.py)"
        )
        ok = False

    print("Recommended (fill when ready):")
    for key in RECOMMENDED:
        if key == "wrtc_building_density":
            continue  # already reported as primary
        val = cfg.get(key, "")
        if not val:
            print(f"  empty: {key}")
            continue
        print(f"  {'OK' if arcpy.Exists(val) else 'NOT FOUND'}: {key} -> {val}")

    if cfg.get("padus"):
        print(
            f"  PAD note: zonal step keeps GAP_Sts in "
            f"{{{cfg.get('padus_gap_include', '1,2,3')}}} only"
        )

    if not ok:
        raise SystemExit(1)
    print("Required paths look good.")


if __name__ == "__main__":
    main()
