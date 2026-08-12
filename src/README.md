# Python scripts (ArcGIS Pro)

Run in order from **ArcGIS Pro Python** (Python window, Notebook, or Pro `python.exe`).

| Script | Purpose |
|--------|---------|
| `01_check_paths.py` | Validate `config/paths.local.yaml` |
| `02_zonal_wrtc.py` | WRTC **Housing Unit Risk** (primary) → `WRTC_HU_RISK_MEAN`; optional Exposure / Density |
| `03_zonal_evt_padus.py` | EVT **top 3 by area** (+ majority); PAD → `PADUS_FRAC` (**context**); BpS/MFRI; FDist → `FDIST_FUEL_DELTA` |
| `04_score_actions.py` | Action cascade + `PEOPLE_CAT` + scores; **Goldilocks = people_first × fuel multiplier** |
| `05_export_hex_geojson.py` | Write `outputs/hex/` for GitHub / Quarto |
| `rescore_hex_exports.py` | Offline rescore of exported hex CSV/GeoJSON (no ArcGIS) |

## Setup

```text
copy config\paths.example.yaml config\paths.local.yaml
```

Point paths at Pro GDB / clipped rasters (including **FDist** as `landfire_fdist`). See `config/WRTC_DATASETS.md`.

## v1 scoring behavior

**Actions** (`lib/action_assign.py` — first match):

1. Plantation → `value_to_protect_from_fire`
2. Peat → `wetlands_assess_locally`
3. High/VH WFE + High/VH people → `treat_fire_risk_for_people`
4. High/VH WFE → `ecosystem_health_focus`
5. Pine/oak in EVT top 3 + people Moderate/Low/VL → `ecosystem_health_focus`
6. Else → `defer_monitor`

PAD / BpS / EVT_FIRE do **not** pick the action. Fuel is a Goldilocks multiplier only.

**Scores** (all written on the working hex FC):

| Field | Preset |
|-------|--------|
| `PEOPLE_CAT` | AOI quintiles of WRTC HU Risk (Very Low … Very High) |
| `SCORE_PEOPLE` | `people_first` base × fuel multiplier — **default Goldilocks** |
| `SCORE_PLANTATION` | `plantation_asset_first` × fuel multiplier |
| `SCORE_PAD` | legacy preset label — **PAD weight unused** |
| `SCORE_BALANCED` | `balanced` × fuel multiplier |
| `GOLDILOCKS_5` / `_10` / `_15` | Top 5/10/15% by **`SCORE_PEOPLE`** (defer + wetlands excluded; **AOI-wide**) |
| `GOLDILOCKS_PRIORITY` | 0–3: 3=top5%, 2=top10%, 1=top15%, 0=rest (defers and wetlands always 0) |

Goldilocks excludes `defer_monitor` and `wetlands_assess_locally`.

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
