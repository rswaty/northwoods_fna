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
| **PAD-US** | GAP Status **1–3 only** → priority **multiplier** (feasibility / mandate). Not an action picker. Status 4 out. Raster or polygon OK. |
| **Ranking default** | **People-first** Goldilocks over actionable hexes (top 5/10/15%; `GOLDILOCKS_PRIORITY` 0–3). Also: plantation-asset-first, **PAD-first**, balanced |
| **Recreation** | Deferred |
| **TNC Resilient Lands** | Optional later second multiplier — does not change actions; re-orders priority (including off PAD). See `config/PADUS_AND_RESILIENT.md` |

### Action cascade (first match)

1. Plantation → protect_from_fire  
2. Peat → wetlands_assess_locally  
3. High WFE + high people → treat_fire_risk_for_people (mechanical fuels reduction + home hardening)  
4. High WFE + not-high people → ecosystem_health_focus (beneficial fire)  
5. Else → defer_monitor  

High WFE ⇒ fire-dependent (WFE is fire-behavior based), so there's no "hot but not fire-adapted" case. **BpS/MFRI** is folded in as ecological context (`FIRE_DEP_HEX`) and to validate that premise — it does not pick actions.

Details: `config/ACTION_ASSIGNMENT.md` · brief: `next_gen_faa.html`

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
config/          # values, weights, EVT/PAD/WRTC notes, paths.example.yaml
src/             # ArcGIS Pro Python (arcpy) pipeline
data/hex/        # WFE hexes (vectors OK to commit once copied)
data/disturbances/
outputs/hex/     # scored hex GeoJSON for the dashboard (commit these)
dashboard/       # R Quarto → GitHub Pages
docs/            # Pages output folder (optional)
next_gen_faa.*   # working brief
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

See `next_gen_faa.html` (also `.md` / `.txt` / `.odt`).
