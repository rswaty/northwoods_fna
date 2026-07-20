"""Zonal statistics: WRTC housing exposure → hex mean (and optional sum).

Requires Spatial Analyst. Writes a table joined back onto a working hex copy
in the workspace GDB (does not overwrite the source hex feature class).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import load_paths, require_arcpy  # noqa: E402


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()

    hexes = cfg["hexes"]
    raster = cfg.get("wrtc_housing_exposure", "")
    workspace = cfg.get("workspace", "")
    hex_id = cfg.get("hex_id_field", "GRID_ID")

    if not raster:
        raise SystemExit("Set wrtc_housing_exposure in config/paths.local.yaml")
    if not arcpy.Exists(hexes):
        raise SystemExit(f"Hexes not found: {hexes}")
    if not arcpy.Exists(raster):
        raise SystemExit(f"WRTC raster not found: {raster}")

    if workspace:
        arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    out_fc = "hex_wrtc"
    out_table = "zonal_wrtc"

    print(f"Copying hexes → {out_fc}")
    arcpy.management.CopyFeatures(hexes, out_fc)

    print(f"Zonal statistics as table: {raster} → {out_table}")
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=out_fc,
        zone_field=hex_id,
        in_value_raster=raster,
        out_table=out_table,
        ignore_nodata="DATA",
        statistics_type="MEAN",
    )

    # Join MEAN onto working hexes as WRTC_HU_MEAN
    fields = [f.name for f in arcpy.ListFields(out_fc)]
    if "WRTC_HU_MEAN" not in fields:
        arcpy.management.AddField(out_fc, "WRTC_HU_MEAN", "DOUBLE")

    zonal = {}
    with arcpy.da.SearchCursor(out_table, [hex_id, "MEAN"]) as cur:
        for gid, mean in cur:
            zonal[gid] = mean
    with arcpy.da.UpdateCursor(out_fc, [hex_id, "WRTC_HU_MEAN"]) as cur:
        for row in cur:
            row[1] = zonal.get(row[0])
            cur.updateRow(row)

    print(f"Done. Working feature class: {out_fc} (field WRTC_HU_MEAN)")
    print("Next: 03_zonal_evt_padus.py")


if __name__ == "__main__":
    main()
