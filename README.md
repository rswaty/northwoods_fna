# Next Gen FAA — Northwoods

**FAA = Fire Action Assessment** — map **what to do where** to reduce wildfire risk across northern MI, WI, and MN Arrowhead.

Strategic screening only — not NEPA, tribal consultation, or stand prescriptions.

## v1 design (locked)

| Piece | Rule |
|-------|------|
| **Hazard** | Existing **WFE** on ~10k-acre hexes (`MEAN` / `WFE_CAT`) |
| **People** | WRTC **Housing Unit Risk** (primary); Exposure + Density/Count as companions — see `config/WRTC_DATASETS.md` |
| **Plantations** | EVT flag → always **Protect from fire** (silviculture = `TREATMENT_HINT` only) |
| **Peat** | LANDFIRE EVT → **`wetlands_assess_locally`** (fire-dependent *and* ground-fire hazard; swap to USFS peatlands later, same flag) |
| **PAD-US** | GAP 1–3 → `PADUS_FRAC` on hexes for **map context only** (Leaflet). Not a score multiplier or action picker. |
| **Ranking default** | **People-first** Goldilocks over actionable hexes (top 5/10/15%; `GOLDILOCKS_PRIORITY` 0–3). Also: plantation-asset-first, **PAD-first**, balanced |
| **Recreation** | Deferred |
| **TNC Resilient Lands** | Optional later second multiplier — does not change actions; re-orders priority (including off PAD). See `config/PADUS_AND_RESILIENT.md` |

### Action cascade (first match)

1. Plantation → protect_from_fire  
2. Peat → wetlands_assess_locally  
3. High WFE + high people → treat_fire_risk_for_people  
4. High WFE + not-high people → ecosystem_health_focus  
5. High fuel-add (FDist) + high people → treat_fire_risk_for_people  
6. High fuel-add + not-high people → ecosystem_health_focus  
7. Fire-adapted pine/barrens (EVT list) → ecosystem_health_focus  
8. Else → defer_monitor  

**PAD** is map context only (not score / not action). Developed EVT `FIRE=−1` is context; people come from WRTC.

Details: `config/ACTION_ASSIGNMENT.md` · notes: `config/next_steps_partner_notes.md` · brief: `faa_overview.qmd`

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
config/          # weights, EVT rules, path example — see config/README.md
src/             # ArcGIS Pro Python (01–05)
outputs/hex/     # scored hex GeoJSON (+ CSV) for the dashboard
dashboard/       # Quarto map (render → docs/dashboard for Pages)
docs/            # Pages notes; dashboard build output gitignored
faa_overview.qmd / faa_how_it_works.qmd / next_gen_faa.md
```

## Quick start (ArcGIS Pro)

1. Clone this repo.
2. Copy `config/paths.example.yaml` → `config/paths.local.yaml` and set local paths (gitignored).
3. Stage in Pro: WFE hexes, WRTC HU Risk (+ optional Exposure/Density), LANDFIRE EVT, PAD-US (raster OK).
4. Add peat/plantation EVT codes to `config/evt_rules_draft.csv` when classified.
5. Run `src/01` → `05` in Pro Python (see `src/README.md`).
6. Push `outputs/hex/faa_hex_scores.geojson`; render `dashboard/` in Quarto.

## Prior work (read-only)

- Site: https://rswaty.github.io/northwoods/
- Repo: https://github.com/rswaty/northwoods — **do not edit**

## Brief

See `next_gen_faa.md` and `faa_overview.qmd`.
