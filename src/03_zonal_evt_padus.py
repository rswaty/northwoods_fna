"""Summarize LANDFIRE EVT (majority) and PAD-US GAP Status 1–3 onto hexes.

Expects 02_zonal_wrtc.py to have created `hex_wrtc` in the workspace, or falls
back to the source hexes path and creates `hex_scored_work`.

PAD may be a **raster** or a **polygon** layer.
Raster path (default): reclassify GAP status → binary (1 where GAP in {1,2,3},
else 0) → zonal MEAN = PADUS_FRAC. If the raster stores GAP status in an
attribute field (padus_gap_field, e.g. GAP_Sts) with the cell value being only
an index, the reclass runs on that field — NOT the raw cell value.
See config/PADUS_AND_RESILIENT.md.
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


def _is_raster(arcpy, path: str) -> bool:
    try:
        desc = arcpy.Describe(path)
        return getattr(desc, "dataType", "") in {
            "RasterDataset",
            "RasterLayer",
            "MosaicDataset",
            "RasterBand",
        } or hasattr(desc, "meanCellWidth")
    except Exception:
        return False


def _padus_frac_from_raster(
    arcpy, hexes: str, hex_id: str, padus: str, include: set[str], gap_field: str = ""
) -> None:
    """MEAN of a 0/1 raster (1 = GAP in include) per hex = PADUS_FRAC.

    IMPORTANT: many PAD-US rasters store GAP status in an attribute-table field
    (e.g. GAP_Sts) while the *cell value* is just an internal index. Comparing
    the cell value against 1/2/3 then miscounts (the abundant GAP 4 private
    matrix often gets a low index and reads as "protected"). So if the raster
    has the GAP field, reclassify on THAT field; only fall back to treating the
    cell value as the GAP code when no such field exists.
    """
    print(f"PAD-US raster zonal (GAP in {sorted(include)}): {padus}")
    include_ints = sorted({int(c) for c in include if str(c).strip().isdigit()})
    if not include_ints:
        raise SystemExit("padus_gap_include produced no valid GAP codes")

    rat_fields = {f.name: f.type for f in arcpy.ListFields(padus)}
    if gap_field and gap_field in rat_fields:
        print(f"  Reclassifying on RAT field '{gap_field}' (cell value is an index, not the GAP code)")
        is_text = rat_fields[gap_field] in ("String", "Text")
        pairs = []
        for g in (1, 2, 3, 4):
            v = 1 if g in include_ints else 0
            pairs.append([str(g) if is_text else g, v])
        remap = arcpy.sa.RemapValue(pairs)
        binary = arcpy.sa.Reclassify(padus, gap_field, remap, "NODATA")
    else:
        print("  No GAP field found — treating cell value as the GAP status code")
        pad = arcpy.sa.Raster(padus)
        binary = None
        for c in include_ints:
            piece = arcpy.sa.Con(pad == c, 1, 0)
            binary = piece if binary is None else arcpy.sa.Con(binary == 1, 1, piece)
        binary = arcpy.sa.Con(arcpy.sa.IsNull(pad), 0, binary)

    out_raster = "padus_gap13_binary"
    binary.save(out_raster)

    out_table = "zonal_padus"
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=hexes,
        zone_field=hex_id,
        in_value_raster=out_raster,
        out_table=out_table,
        ignore_nodata="DATA",
        statistics_type="MEAN",
    )
    if "PADUS_FRAC" not in [f.name for f in arcpy.ListFields(hexes)]:
        arcpy.management.AddField(hexes, "PADUS_FRAC", "DOUBLE")
    zonal = {}
    with arcpy.da.SearchCursor(out_table, [hex_id, "MEAN"]) as cur:
        for gid, mean in cur:
            zonal[gid] = mean
    with arcpy.da.UpdateCursor(hexes, [hex_id, "PADUS_FRAC"]) as cur:
        for row in cur:
            row[1] = zonal.get(row[0])
            cur.updateRow(row)
    print("Added PADUS_FRAC from PAD raster (GAP 1-3 cell fraction)")


def _padus_frac_from_polygons(arcpy, hexes: str, hex_id: str, padus: str, gap_field: str) -> None:
    print(f"PAD-US polygon overlap (GAP Status 1-3): {padus}")
    arcpy.management.MakeFeatureLayer(padus, "padus_lyr")
    where = f"{gap_field} IN (1, 2, 3, '1', '2', '3')"
    arcpy.management.SelectLayerByAttribute("padus_lyr", "NEW_SELECTION", where)
    n_sel = int(arcpy.management.GetCount("padus_lyr")[0])
    print(f"  Selected {n_sel} PAD features with {gap_field} in 1-3")

    inter = "hex_padus_inter"
    arcpy.analysis.Intersect([hexes, "padus_lyr"], inter, "ALL", None, "INPUT")
    if "PADUS_FRAC" not in [f.name for f in arcpy.ListFields(hexes)]:
        arcpy.management.AddField(hexes, "PADUS_FRAC", "DOUBLE")

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
    print("Added PADUS_FRAC (GAP 1-3 polygon overlap)")


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
        include = {
            t.strip()
            for t in (cfg.get("padus_gap_include") or "1,2,3").split(",")
            if t.strip()
        }
        gap_field = cfg.get("padus_gap_field", "GAP_Sts")
        forced = (cfg.get("padus_type") or "").strip().lower()
        use_raster = forced == "raster" or (
            forced != "polygon" and _is_raster(arcpy, padus)
        )
        if use_raster:
            _padus_frac_from_raster(arcpy, hexes, hex_id, padus, include, gap_field)
        else:
            _padus_frac_from_polygons(arcpy, hexes, hex_id, padus, gap_field)
    else:
        print("Skipping PAD-US (padus empty or not found)")

    print(f"Done. Working feature class: {hexes}")
    print("Next: 04_score_actions.py (after filling config/evt_rules_draft.csv)")


if __name__ == "__main__":
    main()
