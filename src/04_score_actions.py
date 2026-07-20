"""Assign action class + weighted priority scores from config tables.

v1: plantations always protect; PAD multiplies priority only.
See config/ACTION_ASSIGNMENT.md.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.action_assign import (  # noqa: E402
    assign_action_v1,
    percentile_threshold,
    plantation_treatment_hint,
    priority_score,
)
from lib.paths import CONFIG_DIR, load_paths, require_arcpy  # noqa: E402


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _norm(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _rank_flags(values: list[tuple], top_frac: float) -> set:
    ranked = sorted(
        [(i, s) for i, s in values if s is not None],
        key=lambda x: x[1],
        reverse=True,
    )
    if not ranked:
        return set()
    n = max(1, int(len(ranked) * top_frac))
    return {i for i, _ in ranked[:n]}


def _load_evt_flags(rules_path: Path) -> tuple[set[str], set[str]]:
    peat: set[str] = set()
    plant: set[str] = set()
    for r in _read_csv(rules_path):
        raw = (r.get("evt_code") or "").strip()
        if not raw or raw.startswith("#"):
            continue
        codes = [t.strip() for t in raw.replace("|", ",").split(",") if t.strip().isdigit()]
        if r.get("peat_caution", "").strip().lower() == "yes":
            peat.update(codes)
        if r.get("plantation_flag", "").strip().lower() == "yes":
            plant.update(codes)
    return peat, plant


def main() -> None:
    arcpy = require_arcpy()
    cfg = load_paths()
    arcpy.env.overwriteOutput = True
    if cfg.get("workspace"):
        arcpy.env.workspace = cfg["workspace"]

    hexes = "hex_wrtc" if arcpy.Exists("hex_wrtc") else cfg["hexes"]
    if not arcpy.Exists(hexes):
        raise SystemExit(f"Working hexes not found: {hexes}")

    hex_id = cfg.get("hex_id_field", "GRID_ID")
    wfe_field = cfg.get("wfe_mean_field", "MEAN")
    wfe_cat_field = cfg.get("wfe_cat_field", "WFE_CAT")

    peat_codes, plant_codes = _load_evt_flags(CONFIG_DIR / "evt_rules_draft.csv")
    presets = {r["preset_id"]: r for r in _read_csv(CONFIG_DIR / "weight_presets.csv")}

    new_fields = [
        ("ACTION_CLASS", "TEXT", 40),
        ("TREATMENT_HINT", "TEXT", 40),
        ("SCORE_PEOPLE", "DOUBLE", None),
        ("SCORE_PLANTATION", "DOUBLE", None),
        ("SCORE_BIODIV", "DOUBLE", None),
        ("SCORE_BALANCED", "DOUBLE", None),
        ("GOLDILOCKS_5", "SHORT", None),
        ("GOLDILOCKS_10", "SHORT", None),
        ("PLANTATION_HEX", "SHORT", None),
        ("PEAT_HEX", "SHORT", None),
    ]
    existing = {f.name for f in arcpy.ListFields(hexes)}
    for name, ftype, length in new_fields:
        if name in existing:
            continue
        if ftype == "TEXT":
            arcpy.management.AddField(hexes, name, ftype, field_length=length)
        else:
            arcpy.management.AddField(hexes, name, ftype)

    field_names = [f.name for f in arcpy.ListFields(hexes)]
    read_fields = [hex_id, wfe_field]
    for optional in ("EVT_MAJORITY", "WRTC_HU_MEAN", "PADUS_FRAC", wfe_cat_field):
        if optional in field_names and optional not in read_fields:
            read_fields.append(optional)

    records = []
    with arcpy.da.SearchCursor(hexes, read_fields) as cur:
        for row in cur:
            rec = dict(zip(read_fields, row))
            evt = rec.get("EVT_MAJORITY")
            evt_key = str(int(evt)) if evt is not None else ""
            records.append(
                {
                    "id": rec[hex_id],
                    "evt_key": evt_key,
                    "wfe": _norm(rec.get(wfe_field)) or 0.0,
                    "wfe_cat": rec.get(wfe_cat_field) if wfe_cat_field in read_fields else None,
                    "homes": _norm(rec.get("WRTC_HU_MEAN")) or 0.0,
                    "pad": _norm(rec.get("PADUS_FRAC")) or 0.0,
                    "peat": evt_key in peat_codes,
                    "plantation": evt_key in plant_codes,
                }
            )

    wfe_p30 = percentile_threshold([r["wfe"] for r in records], 0.70)
    homes_p30 = percentile_threshold([r["homes"] for r in records], 0.70)

    rows_out = []
    for rec in records:
        plant = 1.0 if rec["plantation"] else 0.0
        wfe_cat = str(rec["wfe_cat"]) if rec["wfe_cat"] is not None else None
        action = assign_action_v1(
            peat=rec["peat"],
            plantation=rec["plantation"],
            wfe=rec["wfe"],
            wfe_cat=wfe_cat,
            homes=rec["homes"],
            wfe_p30=wfe_p30,
            homes_p30=homes_p30,
        )
        hint = plantation_treatment_hint(
            plantation=rec["plantation"],
            wfe=rec["wfe"],
            wfe_cat=wfe_cat,
            wfe_p30=wfe_p30,
        )

        def score(pid: str) -> float:
            p = presets[pid]
            return priority_score(
                homes=rec["homes"],
                plantation=plant,
                wfe=rec["wfe"],
                pad_frac=rec["pad"],
                w_homes=float(p["w_homes"]),
                w_plantations=float(p["w_plantations"]),
                w_wfe=float(p["w_wfe"]),
                w_pad_multiplier=float(p["w_pad_multiplier"]),
            )

        rows_out.append(
            {
                "id": rec["id"],
                "ACTION_CLASS": action,
                "TREATMENT_HINT": hint,
                "PLANTATION_HEX": 1 if rec["plantation"] else 0,
                "PEAT_HEX": 1 if rec["peat"] else 0,
                "SCORE_PEOPLE": score("people_first"),
                "SCORE_PLANTATION": score("plantation_asset_first"),
                "SCORE_BIODIV": score("biodiversity_recreation_first"),
                "SCORE_BALANCED": score("balanced"),
            }
        )

    top5 = _rank_flags([(r["id"], r["SCORE_BALANCED"]) for r in rows_out], 0.05)
    top10 = _rank_flags([(r["id"], r["SCORE_BALANCED"]) for r in rows_out], 0.10)
    by_id = {r["id"]: r for r in rows_out}

    update_fields = [
        hex_id,
        "ACTION_CLASS",
        "TREATMENT_HINT",
        "PLANTATION_HEX",
        "PEAT_HEX",
        "SCORE_PEOPLE",
        "SCORE_PLANTATION",
        "SCORE_BIODIV",
        "SCORE_BALANCED",
        "GOLDILOCKS_5",
        "GOLDILOCKS_10",
    ]
    with arcpy.da.UpdateCursor(hexes, update_fields) as cur:
        for row in cur:
            r = by_id.get(row[0])
            if not r:
                continue
            row[1] = r["ACTION_CLASS"]
            row[2] = r["TREATMENT_HINT"]
            row[3] = r["PLANTATION_HEX"]
            row[4] = r["PEAT_HEX"]
            row[5] = r["SCORE_PEOPLE"]
            row[6] = r["SCORE_PLANTATION"]
            row[7] = r["SCORE_BIODIV"]
            row[8] = r["SCORE_BALANCED"]
            row[9] = 1 if row[0] in top5 else 0
            row[10] = 1 if row[0] in top10 else 0
            cur.updateRow(row)

    if not peat_codes and not plant_codes:
        print(
            "NOTE: No EVT codes in config/evt_rules_draft.csv yet — "
            "peat/plantation flags stay off. See config/ACTION_ASSIGNMENT.md."
        )
    print(f"WFE top-30% cutoff={wfe_p30:.4g}; WRTC top-30% cutoff={homes_p30:.4g}")
    print(f"Scored {len(rows_out)} hexes on {hexes}")
    print("Next: 05_export_hex_geojson.py")


if __name__ == "__main__":
    main()
