"""Assign action class + weighted priority scores from config tables.

v1:
  - Actions: plantation→protect; peat→wetlands; high WFE or high fuel-add
    (split by people); fire-adapted pine/barrens away from people→ecosystem;
    else defer
  - PAD is map context only (PADUS_FRAC kept; not in score)
  - Goldilocks = people_first over ranked hexes (defer + wetlands excluded);
    bands 5/10/15% + priority 0-3; wetlands remain a dashboard overlay
  - EVT FIRE / PINE_HEX from evt attributes + pine list; FDIST_FUEL_DELTA from 03

See config/ACTION_ASSIGNMENT.md and config/next_steps_partner_notes.md §10.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.action_assign import (  # noqa: E402
    GOLDILOCKS_EXCLUDE,
    assign_action_v1,
    is_high_fuel_add,
    is_high_wfe,
    percentile_threshold,
    priority_score,
    treatment_hint,
)
from lib.paths import CONFIG_DIR, REPO_ROOT, load_paths, require_arcpy  # noqa: E402


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


def _load_pine_codes(path: Path) -> set[str]:
    codes: set[str] = set()
    if not path.exists():
        return codes
    for r in _read_csv(path):
        c = (r.get("evt_code") or "").strip()
        if c.isdigit():
            codes.add(c)
    return codes


def _load_evt_fire(path: Path) -> dict[str, int]:
    """EVT VALUE → FIRE (−1 / 0 / 1)."""
    out: dict[str, int] = {}
    if not path.exists():
        return out
    for r in _read_csv(path):
        try:
            key = str(int(float(r["VALUE"])))
            out[key] = int(float(r["FIRE"]))
        except (TypeError, ValueError, KeyError):
            continue
    return out


def _load_evt_names(path: Path) -> dict[str, str]:
    """EVT VALUE → EVT_NAME (majority vegetation label)."""
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for r in _read_csv(path):
        try:
            key = str(int(float(r["VALUE"])))
        except (TypeError, ValueError, KeyError):
            continue
        name = (r.get("EVT_NAME") or "").strip()
        if name:
            out[key] = name
    return out


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
    try:
        fuel_add_min = float(cfg.get("fdist_fuel_add_min", "0.25"))
    except (TypeError, ValueError):
        fuel_add_min = 0.25

    peat_codes, plant_codes = _load_evt_flags(CONFIG_DIR / "evt_rules_draft.csv")
    pine_codes = _load_pine_codes(CONFIG_DIR / "evt_pine_barrens.csv")
    evt_attr = Path(
        cfg.get("evt_attributes")
        or (REPO_ROOT / "other_outputs" / "evt_aoi_attributes.csv")
    )
    evt_fire = _load_evt_fire(evt_attr)
    evt_names = _load_evt_names(evt_attr)
    presets = {r["preset_id"]: r for r in _read_csv(CONFIG_DIR / "weight_presets.csv")}

    new_fields = [
        ("ACTION_CLASS", "TEXT", 40),
        ("TREATMENT_HINT", "TEXT", 40),
        ("SCORE_PEOPLE", "DOUBLE", None),
        ("SCORE_PLANTATION", "DOUBLE", None),
        ("SCORE_PAD", "DOUBLE", None),
        ("SCORE_BALANCED", "DOUBLE", None),
        ("GOLDILOCKS_5", "SHORT", None),
        ("GOLDILOCKS_10", "SHORT", None),
        ("GOLDILOCKS_15", "SHORT", None),
        ("GOLDILOCKS_PRIORITY", "SHORT", None),
        ("PLANTATION_HEX", "SHORT", None),
        ("PEAT_HEX", "SHORT", None),
        ("PINE_HEX", "SHORT", None),
        ("EVT_NAME", "TEXT", 80),
        ("EVT_FIRE", "SHORT", None),
        ("FDIST_FUEL_ADD", "SHORT", None),
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
    homes_field = None
    for candidate in ("WRTC_HU_RISK_MEAN", "WRTC_HU_MEAN"):
        if candidate in field_names:
            homes_field = candidate
            break

    read_fields = [hex_id, wfe_field]
    for optional in (
        "EVT_MAJORITY",
        homes_field,
        "PADUS_FRAC",
        wfe_cat_field,
        "FIRE_DEP_HEX",
        "FDIST_FUEL_DELTA",
    ):
        if optional and optional in field_names and optional not in read_fields:
            read_fields.append(optional)

    records = []
    with arcpy.da.SearchCursor(hexes, read_fields) as cur:
        for row in cur:
            rec = dict(zip(read_fields, row))
            evt = rec.get("EVT_MAJORITY")
            evt_key = str(int(evt)) if evt is not None else ""
            fire_lab = evt_fire.get(evt_key)
            evt_name = evt_names.get(evt_key, "")
            pine = evt_key in pine_codes
            fdist = _norm(rec.get("FDIST_FUEL_DELTA")) or 0.0
            records.append(
                {
                    "id": rec[hex_id],
                    "evt_key": evt_key,
                    "wfe": _norm(rec.get(wfe_field)) or 0.0,
                    "wfe_cat": rec.get(wfe_cat_field) if wfe_cat_field in read_fields else None,
                    "homes": (_norm(rec.get(homes_field)) or 0.0) if homes_field else 0.0,
                    "pad": _norm(rec.get("PADUS_FRAC")) or 0.0,
                    "peat": evt_key in peat_codes,
                    "plantation": evt_key in plant_codes,
                    "pine": pine,
                    "evt_name": evt_name,
                    "evt_fire": fire_lab,
                    "fdist": fdist,
                    "fire_dep": rec.get("FIRE_DEP_HEX") if "FIRE_DEP_HEX" in read_fields else None,
                }
            )

    wfe_p30 = percentile_threshold([r["wfe"] for r in records], 0.70)
    homes_p30 = percentile_threshold([r["homes"] for r in records], 0.70)

    rows_out = []
    n_fuel = n_pine_act = 0
    for rec in records:
        plant = 1.0 if rec["plantation"] else 0.0
        wfe_cat = str(rec["wfe_cat"]) if rec["wfe_cat"] is not None else None
        fuel_flag = is_high_fuel_add(rec["fdist"], fuel_add_min)
        if fuel_flag:
            n_fuel += 1
        action = assign_action_v1(
            peat=rec["peat"],
            plantation=rec["plantation"],
            wfe=rec["wfe"],
            wfe_cat=wfe_cat,
            homes=rec["homes"],
            wfe_p30=wfe_p30,
            homes_p30=homes_p30,
            fdist_delta=rec["fdist"],
            fuel_add_min=fuel_add_min,
            pine_barrens=rec["pine"],
        )
        if action == "ecosystem_health_focus" and rec["pine"] and not is_high_wfe(
            rec["wfe"], wfe_cat, wfe_p30
        ):
            n_pine_act += 1
        hint = treatment_hint(
            action=action,
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
                fuel_add=rec["fdist"],
                w_homes=float(p["w_homes"]),
                w_plantations=float(p["w_plantations"]),
                w_wfe=float(p["w_wfe"]),
                w_fuel_add=float(p.get("w_fuel_add") or 0.0),
            )

        rows_out.append(
            {
                "id": rec["id"],
                "ACTION_CLASS": action,
                "TREATMENT_HINT": hint,
                "PLANTATION_HEX": 1 if rec["plantation"] else 0,
                "PEAT_HEX": 1 if rec["peat"] else 0,
                "PINE_HEX": 1 if rec["pine"] else 0,
                "EVT_NAME": rec["evt_name"] or None,
                "EVT_FIRE": rec["evt_fire"],
                "FDIST_FUEL_ADD": 1 if fuel_flag else 0,
                "SCORE_PEOPLE": score("people_first"),
                "SCORE_PLANTATION": score("plantation_asset_first"),
                "SCORE_PAD": score("pad_first"),
                "SCORE_BALANCED": score("balanced"),
            }
        )

    actionable = [
        (r["id"], r["SCORE_PEOPLE"])
        for r in rows_out
        if r["ACTION_CLASS"] not in GOLDILOCKS_EXCLUDE
    ]
    top5 = _rank_flags(actionable, 0.05)
    top10 = _rank_flags(actionable, 0.10)
    top15 = _rank_flags(actionable, 0.15)
    by_id = {r["id"]: r for r in rows_out}

    def _priority(gid) -> int:
        if gid in top5:
            return 3
        if gid in top10:
            return 2
        if gid in top15:
            return 1
        return 0

    update_fields = [
        hex_id,
        "ACTION_CLASS",
        "TREATMENT_HINT",
        "PLANTATION_HEX",
        "PEAT_HEX",
        "PINE_HEX",
        "EVT_NAME",
        "EVT_FIRE",
        "FDIST_FUEL_ADD",
        "SCORE_PEOPLE",
        "SCORE_PLANTATION",
        "SCORE_PAD",
        "SCORE_BALANCED",
        "GOLDILOCKS_5",
        "GOLDILOCKS_10",
        "GOLDILOCKS_15",
        "GOLDILOCKS_PRIORITY",
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
            row[5] = r["PINE_HEX"]
            row[6] = r["EVT_NAME"]
            row[7] = r["EVT_FIRE"]
            row[8] = r["FDIST_FUEL_ADD"]
            row[9] = r["SCORE_PEOPLE"]
            row[10] = r["SCORE_PLANTATION"]
            row[11] = r["SCORE_PAD"]
            row[12] = r["SCORE_BALANCED"]
            row[13] = 1 if row[0] in top5 else 0
            row[14] = 1 if row[0] in top10 else 0
            row[15] = 1 if row[0] in top15 else 0
            row[16] = _priority(row[0])
            cur.updateRow(row)

    from collections import Counter

    counts = Counter(r["ACTION_CLASS"] for r in rows_out)
    print("ACTION_CLASS counts:", dict(counts))
    print(
        f"Fuel-add hexes (FDIST_FUEL_DELTA>={fuel_add_min}): {n_fuel}; "
        f"pine/barrens→ecosystem (low/mid WFE path): ~{n_pine_act}"
    )
    n_named = sum(1 for r in records if r.get("evt_name"))
    print(
        f"Pine list codes: {len(pine_codes)}; EVT FIRE lookup rows: {len(evt_fire)}; "
        f"EVT_NAME matched: {n_named}/{len(records)}"
    )
    print("PAD: context only (not in score). SCORE_PAD preset label is legacy.")

    if not peat_codes and not plant_codes:
        print(
            "NOTE: No EVT codes in config/evt_rules_draft.csv yet — "
            "peat/plantation flags stay off."
        )
    if "FDIST_FUEL_DELTA" not in field_names:
        print(
            "NOTE: FDIST_FUEL_DELTA missing — run 03 with landfire_fdist set. "
            "Fuel-add actions stay off until then."
        )

    if any(r.get("fire_dep") is not None for r in records):
        high_wfe_recs = [
            r
            for r in records
            if is_high_wfe(
                r["wfe"],
                str(r["wfe_cat"]) if r["wfe_cat"] is not None else None,
                wfe_p30,
            )
        ]
        non_fd = sum(1 for r in high_wfe_recs if (r.get("fire_dep") or 0) == 0)
        n_hw = len(high_wfe_recs)
        pct = (100.0 * non_fd / n_hw) if n_hw else 0.0
        print(
            f"Premise check (BpS/MFRI): {non_fd}/{n_hw} high-WFE hexes are NOT "
            f"fire-dependent ({pct:.1f}%)."
        )

    print(f"WFE top-30% cutoff={wfe_p30:.4g}; WRTC top-30% cutoff={homes_p30:.4g}")
    print(
        f"Goldilocks (people_first) over {len(actionable)} ranked hexes "
        f"(defer + wetlands_assess_locally excluded): "
        f"top5={len(top5)} top10={len(top10)} top15={len(top15)}"
    )
    print(
        "GOLDILOCKS_PRIORITY: 3=top5%, 2=top10%, 1=top15%, 0=rest "
        "(defers and wetlands assess-locally always 0)."
    )
    print(f"Scored {len(rows_out)} hexes on {hexes}")
    print("Next: 05_export_hex_geojson.py")


if __name__ == "__main__":
    main()
