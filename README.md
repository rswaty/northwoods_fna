# Next Gen FNA — Northwoods

Map **what to do where** to reduce wildfire risk across northern MI, WI, and MN Arrowhead.

Strategic screening only — not NEPA, tribal consultation, or stand prescriptions.

## Workflow

```
ArcGIS Pro (local rasters / GDB / .aprx)
        │
        │  run Python from this repo (src/)
        ▼
  scored hex layers
        │
        │  export → push hex GeoJSON / small vectors only
        ▼
  outputs/hex/  →  R Quarto dashboard (GitHub Pages)
```

| Lives where | What |
|-------------|------|
| **This repo** | Python scripts, config, hex outputs, Quarto dashboard, brief |
| **Local / ArcGIS Pro only** | Rasters, file geodatabases, `.aprx` |

**Never commit rasters.** Hexes and small vectors only on GitHub.

## Repo layout

```
config/          # values catalog, weights, EVT rules, path template
src/             # Python for ArcGIS Pro (arcpy)
data/hex/        # WFE hexes (vectors OK to commit once copied)
data/disturbances/
outputs/hex/     # scored hex GeoJSON for the dashboard (commit these)
dashboard/       # R Quarto → GitHub Pages
docs/            # working brief mirrors
```

## Quick start (ArcGIS Pro)

1. Clone this repo.
2. Copy `config/paths.example.yaml` → `config/paths.local.yaml` and set your local layer/raster paths (that file is gitignored).
3. Copy WFE hexes into Pro (or into `data/hex/` and add to the map).
4. Open Pro Python and run scripts under `src/` in order (`01_…`, `02_…`, …).
5. Export scored hexes to `outputs/hex/` (GeoJSON preferred).
6. Commit and push **hex outputs only**; open `dashboard/` in Quarto for the map UI.

Exact input dataset names are not required to start coding — fill them in `paths.local.yaml` when layers are in Pro.

## Prior work (read-only)

- Site: https://rswaty.github.io/northwoods/
- Repo: https://github.com/rswaty/northwoods — **do not edit**

## Brief

See `next_gen_fna.html` (also `.md` / `.txt` / `.odt`).
