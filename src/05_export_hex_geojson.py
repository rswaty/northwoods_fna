"""Export scored hexes to outputs/hex/ for the Quarto dashboard (commit these).

Writes GeoJSON + CSV. Prefer GeoJSON for GitHub Pages.
Includes ACTION_CLASS, SCORE_PEOPLE (people-first default), SCORE_PAD, Goldilocks flags.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import ensure_output_dir, load_paths, require_arcpy  # noqa: E402


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    if cfg.get("workspace"):
        arcpy.env.workspace = cfg["workspace"]
    arcpy.env.overwriteOutput = True

    hexes = "hex_wrtc" if arcpy.Exists("hex_wrtc") else cfg["hexes"]
    if not arcpy.Exists(hexes):
        raise SystemExit(f"Working hexes not found: {hexes}")

    out_dir = ensure_output_dir(cfg)
    geojson = Path(cfg.get("output_hex_geojson") or (out_dir / "faa_hex_scores.geojson"))
    csv_path = Path(cfg.get("output_hex_csv") or (out_dir / "faa_hex_scores.csv"))
    geojson.parent.mkdir(parents=True, exist_ok=True)

    # WGS84 for web maps
    tmp = "hex_export_wgs84"
    arcpy.management.Project(hexes, tmp, arcpy.SpatialReference(4326))

    if geojson.exists():
        geojson.unlink()
    arcpy.conversion.FeaturesToJSON(
        tmp,
        str(geojson),
        format_json="FORMATTED",
        include_z="NO_Z_VALUES",
        include_m="NO_M_VALUES",
        geoJSON="GEOJSON",
    )
    print(f"Wrote {geojson}")

    # Attribute CSV
    skip = {"OBJECTID", "Shape", "Shape_Length", "Shape_Area", "SHAPE", "SHAPE@"}
    fields = [
        f.name
        for f in arcpy.ListFields(hexes)
        if f.type not in ("Geometry", "OID") and f.name not in skip
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        with arcpy.da.SearchCursor(hexes, fields) as cur:
            for row in cur:
                writer.writerow(row)
    print(f"Wrote {csv_path}")
    print("Commit outputs/hex/*.geojson (and csv) — not rasters — then refresh the dashboard.")


if __name__ == "__main__":
    main()
