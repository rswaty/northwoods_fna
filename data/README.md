# Local data notes

Put **rasters and bulky downloads** under `data/rasters/` or in your ArcGIS Pro file geodatabase.
Those paths are gitignored — never commit them.

## v1 inputs (local / Pro)

| Input | Notes |
|-------|--------|
| WFE hexes | Vectors — may also live in `data/hex/` (OK to commit) |
| WRTC Housing Unit Density | **Primary** people layer (MI/WI/MN). See `config/WRTC_DATASETS.md` |
| WRTC Building Density | **Context map** companion (cabins / other ≥40 m²); not scored |
| WRTC HU Risk / Exposure | Optional companions (not scored — avoid double-counting WFE) |
| LANDFIRE EVT | Peat + plantation flags only |
| PAD-US | Filter to **GAP Status 1–3** in zonal step |
| TNC Resilient Lands | Optional later — not required for v1 |
| Recreation | Deferred |

Point `config/paths.local.yaml` at clipped layers in the Pro project.
