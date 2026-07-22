"""Summarize LANDFIRE EVT (majority), PAD-US GAP 1–3, and BpS/MFRI onto hexes.

Expects 02_zonal_wrtc.py to have created `hex_wrtc` in the workspace, or falls
back to the source hexes path and creates `hex_scored_work`.

BpS: zonal majority → BPS_MAJORITY, joined to the MFRI table for reference fire
regime (BPS_FRI / BPS_FRG / FIRE_DEP_HEX). This is context/validation only — it
does not gate the action cascade (see src/lib/action_assign.py).

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
    (e.g. GAP_Sts) while the *cell value* is just an internal index — and here
    it is inverse (VALUE 1 = GAP_Sts 4). Comparing the cell value against 1/2/3
    then miscounts the abundant GAP 4 private matrix as "protected".

    Fix: read the raster attribute table to map each cell VALUE to its GAP
    status, then reclassify on the integer VALUE field (the canonical, reliable
    Reclassify usage). Only fall back to treating the cell value as the GAP code
    when the raster has no GAP field / no attribute table.
    """
    print(f"PAD-US raster zonal (GAP in {sorted(include)}): {padus}")
    include_ints = sorted({int(c) for c in include if str(c).strip().isdigit()})
    if not include_ints:
        raise SystemExit("padus_gap_include produced no valid GAP codes")

    rat_fields = [f.name for f in arcpy.ListFields(padus)]
    value_field = next((c for c in ("Value", "VALUE", "value") if c in rat_fields), "Value")

    binary = None
    if gap_field and gap_field in rat_fields:
        # Build VALUE -> 0/1 from the RAT (respects the VALUE/GAP_Sts inversion).
        mapping = []
        with arcpy.da.SearchCursor(padus, [value_field, gap_field]) as cur:
            for val, gap in cur:
                try:
                    g = int(str(gap).strip())
                except (TypeError, ValueError):
                    g = None
                mapping.append([int(val), 1 if g in include_ints else 0])
        if mapping:
            n_prot = sum(1 for _, f in mapping if f == 1)
            print(
                f"  Mapped {len(mapping)} raster values via RAT '{gap_field}' "
                f"({n_prot} -> GAP {include_ints}); reclassifying on '{value_field}'"
            )
            remap = arcpy.sa.RemapValue(mapping)
            binary = arcpy.sa.Reclassify(padus, value_field, remap, "NODATA")

    if binary is None:
        print("  No usable GAP field — treating cell value as the GAP status code")
        pad = arcpy.sa.Raster(padus)
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


def _read_mfri_lut(mfri_csv: str) -> dict[int, tuple[int | None, str]]:
    """BpS raster Value -> (FRI_ALLFIR years, FRG group). -9999 / blanks → invalid."""
    import csv

    lut: dict[int, tuple[int | None, str]] = {}
    with open(mfri_csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                v = int(float(r.get("VALUE", "")))
            except (TypeError, ValueError):
                continue
            try:
                fri = int(float(r.get("FRI_ALLFIR", "")))
            except (TypeError, ValueError):
                fri = None
            lut[v] = (fri, (r.get("FRG_NEW") or "").strip())
    return lut


def _bps_mfri(arcpy, hexes: str, hex_id: str, bps: str, mfri_csv: str, fri_max: int) -> None:
    """Zonal majority of BpS → BPS_MAJORITY; join MFRI → BPS_FRI / BPS_FRG / FIRE_DEP_HEX.

    Context/validation only — does NOT gate the action cascade. FIRE_DEP_HEX = 1
    when the reference all-fire return interval is short (0 < FRI <= fri_max).
    """
    print(f"BpS majority by hex: {bps}")
    out_table = "zonal_bps"
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=hexes,
        zone_field=hex_id,
        in_value_raster=bps,
        out_table=out_table,
        ignore_nodata="DATA",
        statistics_type="MAJORITY",
    )
    lut = _read_mfri_lut(mfri_csv)
    print(f"  MFRI lookup rows: {len(lut)} (from {mfri_csv})")

    existing = [f.name for f in arcpy.ListFields(hexes)]
    for name, ftype, length in (
        ("BPS_MAJORITY", "LONG", None),
        ("BPS_FRI", "LONG", None),
        ("BPS_FRG", "TEXT", 16),
        ("FIRE_DEP_HEX", "SHORT", None),
    ):
        if name not in existing:
            if ftype == "TEXT":
                arcpy.management.AddField(hexes, name, ftype, field_length=length)
            else:
                arcpy.management.AddField(hexes, name, ftype)

    maj: dict = {}
    with arcpy.da.SearchCursor(out_table, [hex_id, "MAJORITY"]) as cur:
        for gid, m in cur:
            maj[gid] = m

    n_fd = 0
    with arcpy.da.UpdateCursor(
        hexes, [hex_id, "BPS_MAJORITY", "BPS_FRI", "BPS_FRG", "FIRE_DEP_HEX"]
    ) as cur:
        for row in cur:
            m = maj.get(row[0])
            if m is None:
                row[1] = row[2] = None
                row[3] = ""
                row[4] = 0
                cur.updateRow(row)
                continue
            mv = int(m)
            fri, frg = lut.get(mv, (None, ""))
            row[1] = mv
            row[2] = fri if (fri is not None and fri > 0) else None
            row[3] = frg
            fd = 1 if (fri is not None and 0 < fri <= fri_max) else 0
            row[4] = fd
            n_fd += fd
            cur.updateRow(row)
    print(f"Added BPS_MAJORITY / BPS_FRI / BPS_FRG / FIRE_DEP_HEX (fire-dependent hexes: {n_fd})")


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    arcpy.env.overwriteOutput = True

    hexes = _working_hexes(arcpy, cfg)
    hex_id = cfg.get("hex_id_field", "GRID_ID")
    evt = cfg.get("landfire_evt", "")
    padus = cfg.get("padus", "")
    bps = cfg.get("landfire_bps", "")

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

    if not bps:
        print(
            "Skipping BpS/MFRI: landfire_bps is empty in paths.local.yaml. "
            "Add e.g. landfire_bps: \"D:/northwoods_faa/MyProject.gdb/nw_aoi_bps\""
        )
    elif not arcpy.Exists(bps):
        print(f"Skipping BpS/MFRI: landfire_bps not found by ArcGIS -> {bps}")
        print("  Check the raster name in Catalog (exact spelling) and that the GDB path is correct.")
    else:
        mfri_csv = cfg.get("mfri_table") or str(
            Path(cfg["_repo_root"]) / "other_outputs" / "mfri_aoi_attributes.csv"
        )
        if not Path(mfri_csv).exists():
            print(f"Skipping BpS/MFRI: MFRI table not found ({mfri_csv})")
        else:
            try:
                fri_max = int(float(cfg.get("fire_dependent_max_fri", "100")))
            except (TypeError, ValueError):
                fri_max = 100
            _bps_mfri(arcpy, hexes, hex_id, bps, mfri_csv, fri_max)

    print(f"Done. Working feature class: {hexes}")
    print("Next: 04_score_actions.py (after filling config/evt_rules_draft.csv)")


if __name__ == "__main__":
    main()
