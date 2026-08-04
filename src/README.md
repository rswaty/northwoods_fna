# Python scripts (ArcGIS Pro)

Run in order from **ArcGIS Pro Python** (Python window, Notebook, or Pro `python.exe`).

| Script | Purpose |
|--------|---------|
| `01_check_paths.py` | Validate `config/paths.local.yaml` |
| `02_zonal_wrtc.py` | WRTC **Housing Unit Risk** (primary) → `WRTC_HU_RISK_MEAN`; optional Exposure / Density |
| `03_zonal_evt_padus.py` | EVT majority; PAD → `PADUS_FRAC` (**context**); BpS/MFRI; FDist → `FDIST_FUEL_DELTA` |
| `04_score_actions.py` | Action cascade + scores; **Goldilocks = people_first**; EVT FIRE / pine flags |
| `05_export_hex_geojson.py` | Write `outputs/hex/` for GitHub / Quarto |

## Setup

```text
copy config\paths.example.yaml config\paths.local.yaml
```

Point paths at Pro GDB / clipped rasters (including **FDist** as `landfire_fdist`). See `config/WRTC_DATASETS.md`.

## v1 scoring behavior

**Actions** (`lib/action_assign.py` — first match):

1. Plantation → `protect_from_fire`
2. Peat → `wetlands_assess_locally`
3. High WFE + high people → `treat_fire_risk_for_people`
4. High WFE + not-high people → `ecosystem_health_focus`
5. High fuel-add + high people → `treat_fire_risk_for_people`
6. High fuel-add + not-high people → `ecosystem_health_focus`
7. Pine/barrens (`config/evt_pine_barrens.csv`) → `ecosystem_health_focus`
8. Else → `defer_monitor`

PAD does **not** pick the action or score. Fuel-add uses `FDIST_FUEL_DELTA` ≥ `fdist_fuel_add_min` (default 0.25).

**Scores** (all written on the working hex FC):

| Field | Preset |
|-------|--------|
| `SCORE_PEOPLE` | `people_first` — **default Goldilocks** (homes + WFE + fuel-add; no PAD) |
| `SCORE_PLANTATION` | `plantation_asset_first` |
| `SCORE_PAD` | legacy preset label — **PAD weight unused** |
| `SCORE_BALANCED` | `balanced` |
| `GOLDILOCKS_5` / `_10` / `_15` | Top 5/10/15% by **`SCORE_PEOPLE`**, actionable hexes only |
| `GOLDILOCKS_PRIORITY` | 0–3: 3=top5%, 2=top10%, 1=top15%, 0=rest (defers always 0) |

Goldilocks excludes `defer_monitor`. Peat and new fuel-add / pine actions **are** ranked.

### When to re-run

| Change | Scripts |
|--------|---------|
| Action / score / Goldilocks only | **04 → 05** |
| First FDist path or EVT/PAD/BpS inputs | **03 → 04 → 05** |
| WRTC inputs changed | from 02 onward |

## Notes

- Spatial Analyst required for zonal steps.
- Until EVT codes are listed in `config/evt_rules_draft.csv`, peat/plantation flags stay off; actions still follow WRTC + WFE.
- Score fields use raw WRTC/WFE scales initially — normalize after the first real run if needed.
- Commit hex GeoJSON only; never rasters or the `.aprx`.
