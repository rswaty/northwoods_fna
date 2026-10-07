# WRTC / Wildfire Risk to Communities — datasets for Next Gen FAA

Source: [wildfirerisk.org/download](https://wildfirerisk.org/download/) · GIS by state via Forest Service Research Data Archive (May 2024 update).  
Download **MI, WI, MN** (and clip to AOI in Pro). **Never commit rasters.**

Official family name is **Wildfire Risk to Communities (WRC/WRTC)**.

## Proposed stack (use multiple)

| Priority | Dataset | What it is | Use in FAA |
|----------|---------|------------|------------|
| **1 — primary people proxy** | **Building Density** | Qualifying footprints ≥40 m² (homes, cabins, camps, commercial, industrial) — where structures are, not a population count | Main `w_homes` term; AOI quintiles → `PEOPLE_CAT`; High/VH buildings × High/VH WFE (or Very High buildings × Moderate WFE) → `treat_fire_risk_for_people` |
| **2 — Context companion** | **Housing Unit Density** (or **Count**) | Where occupied / vacant Census housing exists (includes seasonal homes) | Context map only; **not** scored |
| **3 — optional companion** | **Housing Unit Risk** (`HURisk`) | Likelihood + intensity + home susceptibility + housing density | Context only — **not** people scoring (embeds wildfire; double-counts with WFE) |
| **4 — optional companion** | **Housing Unit Exposure** (`HUExposure`) | Expected housing units exposed per year (likelihood × housing density) | Dashboard / triangulation; also hazard×homes, not a second people driver |
| **5 — optional context** | **Community Wildfire Risk Reduction Zones** (`CWiRRZ`) | Minimal / Indirect / Direct / Transmission zones | Dashboard label & partner talk track—not v1 action cascade |
| **6 — optional landscape** | **Risk to Potential Structures** (Risk to Homes) | Wall-to-wall: risk *if* a home were there | Triangulation / planning context; **not** primary for protect (paints risk with no homes) |

## Not primary for v1 people scoring

| Dataset | Why skip as primary |
|---------|---------------------|
| Housing Unit Risk / Exposure | Pack wildfire into the people term; WFE is already the hazard leg |
| Housing Unit Impact | Intensity × susceptibility × density, **no** likelihood — incomplete risk |
| Burn Probability alone | Hazard only; we already use **WFE** for exposure/hazard on hexes |
| Wildfire Hazard Potential (WRTC copy) | Triangulation only; WFE is the project hazard surface |
| Housing Unit Density / Count | Census housing undersells cabins, camps and other structures; shown as **Context** only |
| Building Count | Building **Density** is used instead (smoothed, comparable across hexes) |
| Population Count/Density | Useful later for equity; not v1 protect trigger |
| Flame length exceedance | Intensity detail later if needed |

## How they enter the hex pipeline

Zonal to ~10k-acre hexes (mean unless noted):

| Hex field | From |
|-----------|------|
| `WRTC_BLDG_DENSITY_MEAN` | Building Density (**primary people**) |
| `WRTC_HU_DENSITY_MEAN` | Housing Unit Density (Context map only) |
| `WRTC_HU_RISK_MEAN` | Housing Unit Risk (optional companion) |
| `WRTC_HU_EXPOSURE_MEAN` | Housing Unit Exposure (optional) |
| `WRTC_HU_COUNT_SUM` | Housing Unit Count (optional; not coded yet) |
| `WRTC_RRZONE_MAJORITY` | CWiRRZ (optional categorical) |

**v1 decision rule:** “high people” uses **Building Density** hex mean → AOI quintiles (`PEOPLE_CAT`). Housing Unit Density / Risk / Exposure can be shown alongside as context only.

**Default Goldilocks ranking** uses the people-first preset (`SCORE_PEOPLE`), which weights Building Density most heavily (`w_homes`), then WFE and plantations.

## NoData / NULL hexes

Housing Unit **Risk** and **Exposure** only have pixel values **where housing units exist**; hexes with no homes come back NoData from zonal stats. Building Density and Housing Unit **Density** are spatially smoothed, so they usually have a (tiny) value even in empty hexes.

For these housing layers, NoData genuinely means **no homes = 0**, so `02_zonal_wrtc.py` fills NULL with **0** by default (it prints how many hexes were filled). Set `wrtc_fill_nodata_zero: "false"` in `paths.local.yaml` to keep NULLs instead. Do **not** apply this logic to hazard rasters like WFE, where NoData is missing data, not zero hazard.

## Relation to WFE

- **WFE** = landscape wildfire exposure / transmission (your existing hex product).  
- **Building Density** = where structures are (homes, cabins, camps, commercial) — the people term.  
- **HU Density** = where Census housing is (occupied + vacant / seasonal) — context only.  
- **HURisk / HUExposure** = hazard intersecting housing — useful context, **not** a second people score.  
- Do not double-count BP/WHP (or HU Risk) from WRTC as a second hazard driver; keep WFE as the hazard leg.

## Download tips

- Prefer state GIS packages for MI, WI, MN from the Research Data Archive links on the download page.  
- Mosaic/clip in the local ArcGIS Pro project; point `config/paths.local.yaml` at the clipped rasters.
