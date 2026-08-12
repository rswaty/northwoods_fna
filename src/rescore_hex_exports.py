"""Rescore exported hex CSV (+ optional GeoJSON) without ArcGIS.

Uses the same cascade / people quintiles / fuel multiplier as 04_score_actions.py.
After Pro runs 04→05, this is only needed for offline iteration.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from lib.action_assign import (  # noqa: E402
    FUEL_ADD_ALPHA,
    FUEL_REMOVE_BETA,
    GOLDILOCKS_EXCLUDE,
    assign_action_v1,
    assign_people_bin,
    is_high_fuel_add,
    is_high_wfe,
    priority_score,
    quintile_edges,
    treatment_hint,
)

CONFIG = REPO / "config"
HEX_CSV = REPO / "outputs" / "hex" / "faa_hex_scores.csv"
HEX_GJ = REPO / "outputs" / "hex" / "faa_hex_scores.geojson"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_pine() -> set[str]:
    return {
        (r.get("evt_code") or "").strip()
        for r in _read_csv(CONFIG / "evt_pine_barrens.csv")
        if (r.get("evt_code") or "").strip().isdigit()
    }


def _load_evt_flags() -> tuple[set[str], set[str]]:
    peat: set[str] = set()
    plant: set[str] = set()
    for r in _read_csv(CONFIG / "evt_rules_draft.csv"):
        raw = (r.get("evt_code") or "").strip()
        if not raw or raw.startswith("#"):
            continue
        codes = [
            t.strip()
            for t in raw.replace("|", ",").split(",")
            if t.strip().isdigit()
        ]
        if r.get("peat_caution", "").strip().lower() == "yes":
            peat.update(codes)
        if r.get("plantation_flag", "").strip().lower() == "yes":
            plant.update(codes)
    return peat, plant


def _evt_key(v) -> str:
    if v is None or v == "":
        return ""
    try:
        return str(int(float(v)))
    except (TypeError, ValueError):
        return ""


def _f(v, default=0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _pine_top3(row: dict, pine: set[str]) -> bool:
    for k in ("EVT_1", "EVT_2", "EVT_3", "EVT_MAJORITY"):
        key = _evt_key(row.get(k))
        if key and key in pine:
            return True
    return False


def _rank_flags(values: list[tuple], top_frac: float) -> set:
    ranked = sorted(values, key=lambda x: x[1], reverse=True)
    if not ranked:
        return set()
    n = max(1, int(len(ranked) * top_frac))
    return {i for i, _ in ranked[:n]}


def rescore_rows(rows: list[dict]) -> list[dict]:
    pine = _load_pine()
    peat_codes, plant_codes = _load_evt_flags()
    presets = {r["preset_id"]: r for r in _read_csv(CONFIG / "weight_presets.csv")}

    homes_list = [_f(r.get("WRTC_HU_RISK_MEAN", r.get("WRTC_HU_MEAN"))) for r in rows]
    edges = quintile_edges(homes_list)

    out = []
    for r in rows:
        evt_key = _evt_key(r.get("EVT_MAJORITY") or r.get("EVT_1"))
        # Prefer existing flags when present; else derive from EVT rules
        if r.get("PLANTATION_HEX") not in (None, ""):
            plantation = str(r.get("PLANTATION_HEX")).strip() in {"1", "1.0"}
        else:
            plantation = evt_key in plant_codes
        if r.get("PEAT_HEX") not in (None, ""):
            peat = str(r.get("PEAT_HEX")).strip() in {"1", "1.0"}
        else:
            peat = evt_key in peat_codes

        pine_flag = _pine_top3(r, pine)
        homes = _f(r.get("WRTC_HU_RISK_MEAN", r.get("WRTC_HU_MEAN")))
        wfe = _f(r.get("MEAN"))
        wfe_cat = (r.get("WFE_CAT") or "").strip() or None
        people_cat = assign_people_bin(homes, edges)
        fdist = _f(r.get("FDIST_FUEL_DELTA"))
        action = assign_action_v1(
            peat=peat,
            plantation=plantation,
            wfe_cat=wfe_cat,
            people_cat=people_cat,
            pine_barrens=pine_flag,
        )
        hint = treatment_hint(
            action=action, plantation=plantation, wfe_cat=wfe_cat
        )
        plant_f = 1.0 if plantation else 0.0

        def score(pid: str) -> float:
            p = presets[pid]
            return priority_score(
                homes=homes,
                plantation=plant_f,
                wfe=wfe,
                fuel_add=fdist,
                w_homes=float(p["w_homes"]),
                w_plantations=float(p["w_plantations"]),
                w_wfe=float(p["w_wfe"]),
                fuel_alpha=FUEL_ADD_ALPHA,
                fuel_beta=FUEL_REMOVE_BETA,
            )

        nr = dict(r)
        nr["PEOPLE_CAT"] = people_cat
        nr["ACTION_CLASS"] = action
        nr["TREATMENT_HINT"] = hint
        nr["PINE_HEX"] = "1" if pine_flag else "0"
        nr["PLANTATION_HEX"] = "1" if plantation else "0"
        nr["PEAT_HEX"] = "1" if peat else "0"
        nr["FDIST_FUEL_ADD"] = "1" if is_high_fuel_add(fdist, 0.25) else "0"
        nr["SCORE_PEOPLE"] = f"{score('people_first'):.10g}"
        nr["SCORE_PLANTATION"] = f"{score('plantation_asset_first'):.10g}"
        nr["SCORE_PAD"] = f"{score('pad_first'):.10g}"
        nr["SCORE_BALANCED"] = f"{score('balanced'):.10g}"
        out.append(nr)

    actionable = [
        (r["GRID_ID"], float(r["SCORE_PEOPLE"]))
        for r in out
        if r["ACTION_CLASS"] not in GOLDILOCKS_EXCLUDE
    ]
    top5 = _rank_flags(actionable, 0.05)
    top10 = _rank_flags(actionable, 0.10)
    top15 = _rank_flags(actionable, 0.15)

    for r in out:
        gid = r["GRID_ID"]
        r["GOLDILOCKS_5"] = "1" if gid in top5 else "0"
        r["GOLDILOCKS_10"] = "1" if gid in top10 else "0"
        r["GOLDILOCKS_15"] = "1" if gid in top15 else "0"
        if gid in top5:
            r["GOLDILOCKS_PRIORITY"] = "3"
        elif gid in top10:
            r["GOLDILOCKS_PRIORITY"] = "2"
        elif gid in top15:
            r["GOLDILOCKS_PRIORITY"] = "1"
        else:
            r["GOLDILOCKS_PRIORITY"] = "0"

    print("ACTION_CLASS", dict(Counter(r["ACTION_CLASS"] for r in out)))
    print("PEOPLE_CAT", dict(Counter(r["PEOPLE_CAT"] for r in out)))
    print(
        "Goldilocks pool",
        len(actionable),
        f"top5={len(top5)} top10={len(top10)} top15={len(top15)}",
    )
    print("People edges", edges)
    print(
        "pine→eco (not High WFE)",
        sum(
            1
            for r in out
            if r["ACTION_CLASS"] == "ecosystem_health_focus"
            and r["PINE_HEX"] == "1"
            and not is_high_wfe(r.get("WFE_CAT"))
        ),
    )
    return out


def main() -> None:
    rows = _read_csv(HEX_CSV)
    out = rescore_rows(rows)
    fieldnames = list(out[0].keys())
    if "PEOPLE_CAT" not in fieldnames:
        # insert after WFE_CAT if possible
        fieldnames = list(rows[0].keys())
        if "WFE_CAT" in fieldnames and "PEOPLE_CAT" not in fieldnames:
            i = fieldnames.index("WFE_CAT") + 1
            fieldnames.insert(i, "PEOPLE_CAT")
        elif "PEOPLE_CAT" not in fieldnames:
            fieldnames.append("PEOPLE_CAT")
    # ensure PEOPLE_CAT present
    if "PEOPLE_CAT" not in fieldnames:
        fieldnames.append("PEOPLE_CAT")
    with HEX_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(f"Wrote {HEX_CSV}")

    if HEX_GJ.exists():
        gj = json.loads(HEX_GJ.read_text(encoding="utf-8"))
        by_id = {r["GRID_ID"]: r for r in out}
        score_keys = [
            "ACTION_CLASS",
            "TREATMENT_HINT",
            "PEOPLE_CAT",
            "PINE_HEX",
            "PLANTATION_HEX",
            "PEAT_HEX",
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
        for feat in gj.get("features", []):
            props = feat.get("properties") or {}
            gid = props.get("GRID_ID")
            r = by_id.get(str(gid)) if gid is not None else None
            if not r:
                continue
            for k in score_keys:
                v = r.get(k)
                if k.startswith("SCORE_"):
                    props[k] = float(v) if v not in (None, "") else None
                elif k.startswith("GOLDILOCKS") or k.endswith("_HEX") or k == "FDIST_FUEL_ADD":
                    props[k] = int(float(v)) if v not in (None, "") else 0
                else:
                    props[k] = v
            feat["properties"] = props
        HEX_GJ.write_text(json.dumps(gj, separators=(",", ":")), encoding="utf-8")
        print(f"Wrote {HEX_GJ}")


if __name__ == "__main__":
    main()
