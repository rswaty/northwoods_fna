# WRTC / Wildfire Risk to Communities — datasets for Next Gen FNA

Source: [wildfirerisk.org/download](https://wildfirerisk.org/download/) · GIS by state via Forest Service Research Data Archive (May 2024 update).  
Download **MI, WI, MN** (and clip to AOI in Pro). **Never commit rasters.**

Official family name is **Wildfire Risk to Communities (WRC/WRTC)**.

## Proposed stack (use multiple)

| Priority | Dataset | What it is | Use in FNA |
|----------|---------|------------|------------|
| **1 — primary people risk** | **Housing Unit Risk** (`HURisk`) | Likelihood + intensity + home susceptibility + housing density; only where housing exists | Main `w_homes` term; drives “high WRTC → protect_from_wildfire” |
| **2 — exposure companion** | **Housing Unit Exposure** (`HUExposure`) | Expected housing units exposed per year (likelihood × housing density) | Second people metric / dashboard toggle; “homes in the fire pathway” without full consequence |
| **3 — where homes are** | **Housing Unit Density** (or **Count**) | Where occupied housing exists | Mask / presence; optional sum of count per hex for “how many homes” |
| **4 — optional context** | **Community Wildfire Risk Reduction Zones** (`CWiRRZ`) | Minimal / Indirect / Direct / Transmission zones | Dashboard label & partner talk track—not v1 action cascade |
| **5 — optional landscape** | **Risk to Potential Structures** (Risk to Homes) | Wall-to-wall: risk *if* a home were there | Triangulation / planning context; **not** primary for protect (paints risk with no homes) |

## Not primary for v1 people scoring

| Dataset | Why skip as primary |
|---------|---------------------|
| Housing Unit Impact | Intensity × susceptibility × density, **no** likelihood — incomplete risk |
| Burn Probability alone | Hazard only; we already use **WFE** for exposure/hazard on hexes |
| Wildfire Hazard Potential (WRTC copy) | Triangulation only; WFE is the project hazard surface |
| Building Count/Density (all buildings) | Prefer **Housing Unit** layers (occupied housing) |
| Population Count/Density | Useful later for equity; not v1 protect trigger |
| Flame length exceedance | Intensity detail later if needed |

## How they enter the hex pipeline

Zonal to ~10k-acre hexes (mean unless noted):

| Hex field | From |
|-----------|------|
| `WRTC_HU_RISK_MEAN` | Housing Unit Risk (primary) |
| `WRTC_HU_EXPOSURE_MEAN` | Housing Unit Exposure |
| `WRTC_HU_DENSITY_MEAN` or `WRTC_HU_COUNT_SUM` | Housing Unit Density / Count |
| `WRTC_RRZONE_MAJORITY` | CWiRRZ (optional categorical) |

**v1 decision rule:** “high homes” uses **Housing Unit Risk** hex mean (top ~30%). Exposure can be shown alongside. Count/density prevents treating empty high-RPS landscape as “communities.”

**Default Goldilocks ranking** uses the people-first preset (`SCORE_PEOPLE`), which weights Housing Unit Risk most heavily.

## Relation to WFE

- **WFE** = landscape wildfire exposure / transmission (your existing hex product).  
- **HURisk / HUExposure** = that hazard intersecting **housing**.  
- Do not double-count BP/WHP from WRTC as a second hazard driver; keep WFE as the hazard leg.

## Download tips

- Prefer state GIS packages for MI, WI, MN from the Research Data Archive links on the download page.  
- Mosaic/clip in the local ArcGIS Pro project; point `config/paths.local.yaml` at the clipped rasters.
