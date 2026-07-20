# Python scripts (ArcGIS Pro)

Run in order from **ArcGIS Pro Python** (Python window, Notebook, or Pro `python.exe`).

| Script | Purpose |
|--------|---------|
| `01_check_paths.py` | Validate `config/paths.local.yaml` |
| `02_zonal_wrtc.py` | WRTC **Housing Unit Risk** (primary) → `WRTC_HU_RISK_MEAN`; optional Exposure / Density |
| `03_zonal_evt_padus.py` | EVT majority; PAD-US **GAP 1–3** → `PADUS_FRAC` (raster or polygon) |
| `04_score_actions.py` | Action cascade + preset scores; **Goldilocks = people-first** |
| `05_export_hex_geojson.py` | Write `outputs/hex/` for GitHub / Quarto |

## Setup

```text
copy config\paths.example.yaml config\paths.local.yaml
```

Point paths at Pro GDB / clipped rasters. See `config/WRTC_DATASETS.md` and `config/PADUS_AND_RESILIENT.md`.

## v1 scoring behavior

**Actions** (`lib/action_assign.py` — first match):

1. Peat (EVT) → `defer_monitor`
2. Plantation (EVT) → `protect_from_wildfire` (+ `TREATMENT_HINT`)
3. High WRTC HU Risk → `protect_from_wildfire`
4. High WFE → `restore_beneficial_fire`
5. Else → `defer_monitor`

PAD does **not** pick the action. It multiplies priority only (GAP 1–3).

**Scores** (all written on the working hex FC):

| Field | Preset |
|-------|--------|
| `SCORE_PEOPLE` | `people_first` — **default Goldilocks** |
| `SCORE_PLANTATION` | `plantation_asset_first` |
| `SCORE_PAD` | `pad_first` (strong GAP 1–3 boost) |
| `SCORE_BALANCED` | `balanced` |
| `GOLDILOCKS_5` / `_10` | Top 5% / 10% by **`SCORE_PEOPLE`** |

Recreation deferred. TNC Resilient Lands not in the pipeline yet (optional later multiplier).

## Notes

- Spatial Analyst required for zonal steps.
- Until EVT codes are listed in `config/evt_rules_draft.csv`, peat/plantation flags stay off; actions still follow WRTC + WFE.
- Score fields use raw WRTC/WFE scales initially — normalize after the first real run if needed.
- Commit hex GeoJSON only; never rasters or the `.aprx`.
