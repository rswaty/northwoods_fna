# Python scripts (ArcGIS Pro)

Run in order from **ArcGIS Pro Python** (Python window, Notebook, or Pro `python.exe`).

| Script | Purpose |
|--------|---------|
| `01_check_paths.py` | Validate `config/paths.local.yaml` |
| `02_zonal_wrtc.py` | WRTC → hex `WRTC_HU_MEAN` |
| `03_zonal_evt_padus.py` | EVT majority + PAD-US fraction |
| `04_score_actions.py` | Action class + weight preset scores + Goldilocks flags |
| `05_export_hex_geojson.py` | Write `outputs/hex/` for GitHub / Quarto |

## Setup

```text
copy config\paths.example.yaml config\paths.local.yaml
```

Edit `paths.local.yaml` with your GDB / raster paths. You do **not** need final dataset names before scaffolding — fill them when layers are in Pro.

## Notes

- Spatial Analyst required for zonal steps.
- `config/evt_rules_draft.csv` is empty until Randy adds EVT → action rules; until then scoring defaults actions to `defer_monitor`.
- Score fields use raw WRTC/WFE scales initially — normalize after first real run.
- Commit hex GeoJSON only; never rasters or the `.aprx`.
