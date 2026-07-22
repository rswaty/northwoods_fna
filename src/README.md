# Python scripts (ArcGIS Pro)

Run in order from **ArcGIS Pro Python** (Python window, Notebook, or Pro `python.exe`).

| Script | Purpose |
|--------|---------|
| `01_check_paths.py` | Validate `config/paths.local.yaml` |
| `02_zonal_wrtc.py` | WRTC **Housing Unit Risk** (primary) → `WRTC_HU_RISK_MEAN`; optional Exposure / Density |
| `03_zonal_evt_padus.py` | EVT majority; PAD-US **GAP 1–3** → `PADUS_FRAC`; BpS majority + MFRI → `FIRE_DEP_HEX` (context) |
| `04_score_actions.py` | Action cascade + preset scores; **Goldilocks = people-first** |
| `05_export_hex_geojson.py` | Write `outputs/hex/` for GitHub / Quarto |

## Setup

```text
copy config\paths.example.yaml config\paths.local.yaml
```

Point paths at Pro GDB / clipped rasters. See `config/WRTC_DATASETS.md` and `config/PADUS_AND_RESILIENT.md`.

## v1 scoring behavior

**Actions** (`lib/action_assign.py` — first match):

1. Plantation (EVT) → `protect_from_fire` (hint: silviculture)
2. Peat (EVT) → `wetlands_assess_locally`
3. High WFE + high people → `treat_fire_risk_for_people` (hint: `fuels_reduction_home_hardening`)
4. High WFE + not-high people → `ecosystem_health_focus`
5. Else → `defer_monitor`

PAD does **not** pick the action (multiplies priority only, GAP 1–3). BpS/MFRI does **not** pick the action either — `FIRE_DEP_HEX` is context + a check that high WFE ⇒ fire-dependent (script 04 prints the count).

**Scores** (all written on the working hex FC):

| Field | Preset |
|-------|--------|
| `SCORE_PEOPLE` | `people_first` — **default Goldilocks** |
| `SCORE_PLANTATION` | `plantation_asset_first` |
| `SCORE_PAD` | `pad_first` (strong GAP 1–3 boost) |
| `SCORE_BALANCED` | `balanced` |
| `GOLDILOCKS_5` / `_10` / `_15` | Top 5/10/15% by **`SCORE_PEOPLE`**, actionable hexes only |
| `GOLDILOCKS_PRIORITY` | 0–3: 3=top5%, 2=top10%, 1=top15%, 0=rest (defers always 0) |

Goldilocks excludes `defer_monitor` so "don't act" hexes are never flagged. Peat (`wetlands_assess_locally`) **is** ranked. Recreation deferred. TNC Resilient Lands not in the pipeline yet (optional later multiplier).

### When to re-run

| Change | Scripts |
|--------|---------|
| Action names / cascade / Goldilocks only | **04 → 05** |
| First time adding BpS/MFRI context (`FIRE_DEP_HEX`) | **03 → 04 → 05** |
| WRTC / EVT / PAD inputs changed | from the affected zonal step onward |

## Notes

- Spatial Analyst required for zonal steps.
- Until EVT codes are listed in `config/evt_rules_draft.csv`, peat/plantation flags stay off; actions still follow WRTC + WFE.
- Score fields use raw WRTC/WFE scales initially — normalize after the first real run if needed.
- Commit hex GeoJSON only; never rasters or the `.aprx`.
