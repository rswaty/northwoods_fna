"""Zonal statistics: WRTC people layers → hex means.

Primary: Housing Unit Risk → WRTC_HU_RISK_MEAN (drives people-first scoring).
Optional companions: Housing Unit Exposure, Housing Unit Density.

Requires Spatial Analyst. Writes onto a working hex copy in the workspace GDB
(does not overwrite the source hex feature class).

See config/WRTC_DATASETS.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import load_paths, require_arcpy  # noqa: E402


def _zonal_mean(
    arcpy,
    zones: str,
    zone_field: str,
    raster: str,
    out_table: str,
    out_field: str,
    fill_zero: bool = True,
) -> None:
    """Zonal MEAN of `raster` per hex → `out_field`.

    WRTC Housing Unit Risk/Exposure only have pixels where housing exists, so
    hexes with no housing are absent from the zonal table (NoData). For these
    housing-risk layers, NoData means "no homes here" = 0 risk, so fill_zero
    replaces NULL with 0. Count how many were filled for transparency.
    """
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=zones,
        zone_field=zone_field,
        in_value_raster=raster,
        out_table=out_table,
        ignore_nodata="DATA",
        statistics_type="MEAN",
    )
    fields = [f.name for f in arcpy.ListFields(zones)]
    if out_field not in fields:
        arcpy.management.AddField(zones, out_field, "DOUBLE")
    zonal = {}
    with arcpy.da.SearchCursor(out_table, [zone_field, "MEAN"]) as cur:
        for gid, mean in cur:
            zonal[gid] = mean
    n_filled = 0
    with arcpy.da.UpdateCursor(zones, [zone_field, out_field]) as cur:
        for row in cur:
            val = zonal.get(row[0])
            if val is None and fill_zero:
                val = 0.0
                n_filled += 1
            row[1] = val
            cur.updateRow(row)
    note = f" ({n_filled} NoData hexes set to 0 = no homes)" if fill_zero and n_filled else ""
    print(f"  Added {out_field}{note}")


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()

    hexes = cfg["hexes"]
    workspace = cfg.get("workspace", "")
    hex_id = cfg.get("hex_id_field", "GRID_ID")

    # Primary = Housing Unit Risk (legacy key wrtc_housing_exposure still accepted)
    risk = cfg.get("wrtc_housing_unit_risk") or cfg.get("wrtc_housing_exposure", "")
    exposure = cfg.get("wrtc_housing_unit_exposure", "")
    density = cfg.get("wrtc_housing_unit_density", "")

    # NoData in WRTC housing layers = no homes = 0 risk. Fill by default.
    # Set wrtc_fill_nodata_zero: "false" in paths.local.yaml to keep NULLs.
    fill_zero = str(cfg.get("wrtc_fill_nodata_zero", "true")).strip().lower() != "false"

    if not risk:
        raise SystemExit(
            "Set wrtc_housing_unit_risk (Housing Unit Risk) in config/paths.local.yaml"
        )
    if not arcpy.Exists(hexes):
        raise SystemExit(f"Hexes not found: {hexes}")
    if not arcpy.Exists(risk):
        raise SystemExit(f"WRTC Housing Unit Risk raster not found: {risk}")

    if workspace:
        arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    out_fc = "hex_wrtc"
    print(f"Copying hexes → {out_fc}")
    arcpy.management.CopyFeatures(hexes, out_fc)

    print(f"Primary zonal: Housing Unit Risk → WRTC_HU_RISK_MEAN")
    _zonal_mean(arcpy, out_fc, hex_id, risk, "zonal_wrtc_risk", "WRTC_HU_RISK_MEAN", fill_zero)

    # Keep legacy alias for older scoring field name
    fields = [f.name for f in arcpy.ListFields(out_fc)]
    if "WRTC_HU_MEAN" not in fields:
        arcpy.management.AddField(out_fc, "WRTC_HU_MEAN", "DOUBLE")
    with arcpy.da.UpdateCursor(out_fc, ["WRTC_HU_RISK_MEAN", "WRTC_HU_MEAN"]) as cur:
        for row in cur:
            row[1] = row[0]
            cur.updateRow(row)

    if exposure and arcpy.Exists(exposure):
        print("Companion zonal: Housing Unit Exposure")
        _zonal_mean(arcpy, out_fc, hex_id, exposure, "zonal_wrtc_exp", "WRTC_HU_EXPOSURE_MEAN", fill_zero)
    else:
        print("Skipping Housing Unit Exposure (path empty or not found)")

    if density and arcpy.Exists(density):
        print("Companion zonal: Housing Unit Density")
        _zonal_mean(arcpy, out_fc, hex_id, density, "zonal_wrtc_den", "WRTC_HU_DENSITY_MEAN", fill_zero)
    else:
        print("Skipping Housing Unit Density (path empty or not found)")

    print(f"Done. Working feature class: {out_fc}")
    print("Next: 03_zonal_evt_padus.py")


if __name__ == "__main__":
    main()
