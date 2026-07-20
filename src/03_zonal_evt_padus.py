"""Summarize LANDFIRE EVT (majority) and PAD-US overlap onto working hexes.

Expects 02_zonal_wrtc.py to have created `hex_wrtc` in the workspace, or falls
back to the source hexes path and creates `hex_scored_work`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import load_paths, require_arcpy  # noqa: E402


def _working_hexes(arcpy, cfg: dict) -> str:
    workspace = cfg.get("workspace", "")
    if workspace:
        arcpy.env.workspace = workspace
    candidate = "hex_wrtc"
    if arcpy.Exists(candidate):
        return candidate
    src = cfg["hexes"]
    out = "hex_scored_work"
    print(f"{candidate} not found; copying {src} → {out}")
    arcpy.management.CopyFeatures(src, out)
    return out


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    arcpy.env.overwriteOutput = True

    hexes = _working_hexes(arcpy, cfg)
    hex_id = cfg.get("hex_id_field", "GRID_ID")
    evt = cfg.get("landfire_evt", "")
    padus = cfg.get("padus", "")

    if evt and arcpy.Exists(evt):
        print(f"EVT majority by hex: {evt}")
        # Majority via Zonal Statistics AS TABLE with MAJORITY (Spatial Analyst)
        out_table = "zonal_evt"
        arcpy.sa.ZonalStatisticsAsTable(
            in_zone_data=hexes,
            zone_field=hex_id,
            in_value_raster=evt,
            out_table=out_table,
            ignore_nodata="DATA",
            statistics_type="MAJORITY",
        )
        if "EVT_MAJORITY" not in [f.name for f in arcpy.ListFields(hexes)]:
            arcpy.management.AddField(hexes, "EVT_MAJORITY", "LONG")
        zonal = {}
        with arcpy.da.SearchCursor(out_table, [hex_id, "MAJORITY"]) as cur:
            for gid, maj in cur:
                zonal[gid] = maj
        with arcpy.da.UpdateCursor(hexes, [hex_id, "EVT_MAJORITY"]) as cur:
            for row in cur:
                row[1] = zonal.get(row[0])
                cur.updateRow(row)
        print("Added EVT_MAJORITY")
    else:
        print("Skipping EVT (landfire_evt empty or not found)")

    if padus and arcpy.Exists(padus):
        print(f"PAD-US overlap fraction: {padus}")
        # Intersect then summarize area / hex area → PADUS_FRAC
        inter = "hex_padus_inter"
        arcpy.analysis.Intersect([hexes, padus], inter, "ALL", None, "INPUT")
        if "PADUS_FRAC" not in [f.name for f in arcpy.ListFields(hexes)]:
            arcpy.management.AddField(hexes, "PADUS_FRAC", "DOUBLE")

        # Sum intersect area by hex_id
        from collections import defaultdict

        inter_area: dict = defaultdict(float)
        shape_field = arcpy.Describe(inter).shapeFieldName
        with arcpy.da.SearchCursor(inter, [hex_id, shape_field]) as cur:
            for gid, geom in cur:
                if geom:
                    inter_area[gid] += geom.area

        hex_area: dict = {}
        shape_field_h = arcpy.Describe(hexes).shapeFieldName
        with arcpy.da.SearchCursor(hexes, [hex_id, shape_field_h]) as cur:
            for gid, geom in cur:
                hex_area[gid] = geom.area if geom else 0.0

        with arcpy.da.UpdateCursor(hexes, [hex_id, "PADUS_FRAC"]) as cur:
            for row in cur:
                ha = hex_area.get(row[0]) or 0.0
                row[1] = (inter_area.get(row[0], 0.0) / ha) if ha else 0.0
                cur.updateRow(row)
        print("Added PADUS_FRAC")
    else:
        print("Skipping PAD-US (padus empty or not found)")

    print(f"Done. Working feature class: {hexes}")
    print("Next: 04_score_actions.py (after filling config/evt_rules_draft.csv)")


if __name__ == "__main__":
    main()
