Next Gen FNA — Northwoods

# Next Gen FNA — Northwoods

Internal working brief. Region: northern Michigan, Wisconsin, and Minnesota Arrowhead.

**Goal:** Map *what to do where* to reduce wildfire risk to people, ecosystems, and services (water, carbon, recreation)—code-driven, customizable, multi-state, with a manageable (“Goldilocks”) treatment footprint.

Strategic screening only—not NEPA, tribal consultation, or stand prescriptions.

## 1. Design intent

Building blocks are standard (hexes, WRTC, LANDFIRE, PAD-US, dashboards). The product is defined by how they are combined:

  - **Action classes** on every hex—not only a risk heat map

  - **Values to protect from wildfire** as an extensible catalog (homes, plantations as assets, infrastructure); separate from PAD-US

  - **Plantations always Protect from wildfire**; silviculture is a treatment hint, not the action class

  - **EVT (v1)** flags peat (defer) and plantations only—not a full ecosystem→action table

  - **PAD-US as priority multiplier** (management feasibility + biodiversity/recreation value)—does not gate action; high people × high WFE outside PAD still count

  - **Disturbance overlays** that calibrate recommended actions (toggleable)

  - **Mill / utilization feasibility** for low-value wood

  - **Carbon** not a v1 ranking driver; smoke framing consistent with [PNAS on Rx fire and PM2.5](https://www.pnas.org/doi/10.1073/pnas.2613722123)

  - **Nested hexes** designed in (10k-acre parents now; finer children later)

  - **ArcGIS Pro + Python + R Quarto** — GIS/rasters in a local Pro project; Python in this repo (run in Pro); hex outputs pushed here for the R dashboard on GitHub Pages

  - **No rasters on GitHub** — hexes and small vectors only

Method and code should transfer to other regions by swapping AOI, hexes, values list, rules, mills, and disturbance sources—not by copying Northwoods biases blindly.

> v1 succeeds when hexes show action class, value context, peat/plantation flags, and disturbance-aware updates—not only “high exposure × high housing = red.”

## 2. Action classes

Required on every hex. Avoid bare “protect” (conservation land-protection meaning).

  - **Protect from wildfire** — reduce wildfire damage to listed values (homes, plantations, infrastructure, others as added)

  - **Silvicultural treatment** — non-commercial thinning through commercial harvest (v1: plantation *treatment hint*, not primary action class)

  - **Restore with beneficial fire** — prescribed, managed, or cultural fire as the main tool

  - **Silviculture then fire** — thin/harvest first when needed (v1: plantation treatment hint when exposure is high)

  - **Defer / monitor** — peat caution, quiet hexes, active/recent burn, or no feasible outlet

ICO / variable-density thinning is one example for some dense red pine plantations—not a regional template. [Larson & Churchill 2012](https://doi.org/10.1016/j.foreco.2012.02.033); [Hanna et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11082040/).

### v1 action cascade (first match wins)

  - Peat (EVT) → **Defer / monitor**

  - Plantation (EVT) → **Protect from wildfire** (always)

  - High WRTC Housing Unit Risk → **Protect from wildfire**

  - High WFE → **Restore with beneficial fire**

  - Else → **Defer / monitor**

PAD-US does not appear in the cascade. Full examples: `config/ACTION_ASSIGNMENT.md`.

## 3. Analysis approach

  - **Region first** on existing WFE hexes (~6,895 × ~10,000 acres). Prior work: [site](https://rswaty.github.io/northwoods/), [repo](https://github.com/rswaty/northwoods) (read-only; do not edit).

  - **Per hex:** WFE; WRTC people layers; PAD-US multiplier; EVT peat/plantation flags; later mills and disturbances.

  - **Goldilocks:** top 5% / 10% (or capacity caps) under weight presets. Priority score = (homes + plantations + WFE) × (1 + PAD multiplier).

  - **Later:** case studies (Arrowhead, Two Hearted, northern LP ice storm); nested hexes; PAD category weights; optional partner EVT workshop; stand-condition overlays.

## 4. Values to protect from wildfire

Extensible catalog. Plantations are an **economic asset** always assigned Protect from wildfire; silviculture may appear as a treatment hint.

  | value_id | Value | Map with 

  | homes_communities | Homes and communities | WRTC (see §5) 

  | plantations | Timber plantations | LANDFIRE EVT / local layers; always Protect 

  | infrastructure | Critical infrastructure | Partner layers when available 

  | future_value | Additional values | New row + layer 

**PAD-US** is not a values-to-protect action. It is a **priority multiplier** (easier management on non-small-ownership lands + biodiversity/recreation value). High people × high WFE *outside* PAD still ranks and can get Protect. v1 uses overlap fraction; later weight by PAD category (fee/federal/state vs easement).

**Add a value:** Propose → Spatialize → Register in `config/values_to_protect.csv` → Score per hex → Weight in dashboard → Link to Protect from wildfire.

## 5. Wildfire Risk to Communities (WRTC) datasets

Source: [wildfirerisk.org/download](https://wildfirerisk.org/download/) (May 2024 GIS by state: MI, WI, MN). Rasters stay local. Details: `config/WRTC_DATASETS.md`.

  | Role | Dataset | Use 

  | **Primary** | **Housing Unit Risk** | Main people term; drives high-WRTC → Protect. Integrates likelihood, intensity, home susceptibility, and housing density where housing exists. 

  | Companion | **Housing Unit Exposure** | Expected housing units exposed per year (likelihood × density). Dashboard / alternate people view. 

  | Where homes are | **Housing Unit Density** or **Count** | Presence and magnitude of housing per hex. 

  | Optional label | **Community Wildfire Risk Reduction Zones** | Minimal / Indirect / Direct / Transmission—dashboard context, not v1 action cascade. 

  | Optional triangulation | **Risk to Potential Structures** (“Risk to Homes”) | Wall-to-wall risk *if* a home were there. Not primary for Protect (no homes required). 

**Not primary for v1 people scoring:** Housing Unit Impact (no likelihood); WRTC burn probability / WHP as a second hazard (project hazard is **WFE**); Building Count (prefer Housing Unit); Population (equity later).

[SILVIS WUI](https://silvis.forest.wisc.edu/data/wui-change/) remains an optional label only (2020).

## 6. Ecosystem logic (EVT) and WFE

**WFE** (existing hex `MEAN` / `WFE_CAT`) is the landscape exposure / transmission surface—priority and, when high and not already Protect/peat, the trigger for Restore with beneficial fire.

**LANDFIRE EVT (v1):** only two jobs—flag **peat** → Defer; flag **plantations** → Protect. No full EVT-name → action table (condition within an EVT, e.g. thinned vs dense pine–oak, needs overlays later). See `config/EVT_RULES_LOGIC.md`.

## 7. Dashboard and disturbances

  - First draft from Randy’s scoring rules, weights, and value list

  - **Built in R / Quarto**, hosted on GitHub Pages; consumes hex outputs pushed from ArcGIS Pro

  - Presets: People-first | Plantation-asset-first | Biodiversity/recreation-first (stronger PAD multiplier) | Balanced

  - Toggle disturbance polygons (ice storm, fire); when on, calibrate actions; when off, show baseline

  - Versioned files in `data/disturbances/`; optional later GitHub Actions ingest

## 8. Mills and low-value wood

Utilization is part of feasibility (distance to buyers; opportunity vs constrained).

Sources: [MI](https://www2.dnr.state.mi.us/mfid/) · [WI](https://dnr.wisconsin.gov/topic/forestbusinesses/industries) · [MN](https://www.dnr.state.mn.us/forestry/um/index.html) · [Primary Forest Products mill map](https://primary.forestproductslocator.org/mill-map). USFS [TPO](https://research.fs.usda.gov/programs/nrum) = aggregates only (mill points confidential).

## 9. Carbon, smoke, FIA

  - **Carbon:** not a v1 ranking driver

  - **Smoke:** [PNAS](https://www.pnas.org/doi/10.1073/pnas.2613722123)—Rx fire often increases net PM2.5 under current conditions; still essential for ecology and hazard where logic supports it

  - **FIA:** no for v1 hex scoring. Optional later via [TreeMap](https://research.fs.usda.gov/firelab/products/dataandtools/treemap-tree-level-model-united-states-forests) on priority hexes only

## 10. Example relevant efforts from around the region

Not exhaustive. Prefer priorities that can hand off to existing work.

  - **MN:** [Arrowhead Landscape Pilot](https://www.fs.usda.gov/r09/superior/natural-resources/forest-management/arrowhead-landscape-pilot-project); Superior NF co-stewardship (Bois Forte, Fond du Lac, Grand Portage); [MN Fire Adapted Communities](https://www.minnesotafac.org/)

  - **WI:** [CNNF Good Neighbor Authority](https://dnr.wisconsin.gov/topic/forestmanagement/gnaGeneralInfo); northern CWPPs; [Wisconsin Point fire restoration](https://www.superiorwi.gov/DocumentCenter/View/16070/Wisconsin_Point_Fire_Restoration_Fact_Sheet_2025)

  - **MI:** [2025 ice storm recovery](https://www.michigan.gov/dnr/about/newsroom/storm-recovery); Hiawatha/Ottawa Rx fire; CWPPs; Two Hearted / TNC UP

  - **Regional:** [Great Lakes Forest Fire Compact](https://compacts.csg.org/compact/great-lakes-forest-fire-compact/); [EACC](https://gacc.nifc.gov/eacc/); [TNC Great Lakes Northwoods](https://www.nature.org/en-us/about-us/where-we-work/priority-landscapes/great-lakes/stories-in-the-great-lakes/great-lakes-northwoods/)

## 11. Implementation

**Stack:**

  - **ArcGIS Pro** — primary GIS workspace (partner preference). Rasters, geodatabases, and the `.aprx` stay local.

  - **Python** — scoring and zonals in this repo’s `src/` (arcpy / Pro Python).

  - **R / Quarto** — draft dashboard only; reads pushed hex GeoJSON/CSV; does not reimplement scoring.

  - Do not modify [rswaty/northwoods](https://github.com/rswaty/northwoods) (read-only prior work).

> **Workflow:** edit Python here → run in ArcGIS Pro on local rasters → push *hexes and small vectors only* → update R dashboard. **Never commit rasters** (LANDFIRE, WRTC, WHP, etc.), raster zips, file geodatabases, or the Pro project.

**Division of labor:** Pro + Python write the truth tables; R draws the map.

**Phases:** (1) regional hex scores + action classes in Pro → (2) push hex outputs; Quarto dashboard + disturbance toggles → (3) mills + case studies → (4) nested hexes; PAD categories; optional TreeMap / EVT workshop.

**Near term:** download WRTC state GIS (HU Risk, Exposure, Density/Count); copy WFE hexes into Pro; join WRTC + PAD-US + EVT flags; export Goldilocks hex GeoJSON; push; refresh Quarto sketch.

## 12. Open items

  - Numeric thresholds for “high” WRTC / WFE (v1 uses top ~30% within AOI)

  - Goldilocks capacity caps; case-study boundaries

  - PAD category weighting scheme

  - Disturbance automation sources

  - Timing of any multi-partner EVT workshop / condition overlays

## 13. Key links

  - [Existing Northwoods assessment](https://rswaty.github.io/northwoods/) · [repo](https://github.com/rswaty/northwoods)

  - [Wildfire Risk to Communities](https://wildfirerisk.org/) · [download](https://wildfirerisk.org/download/) · repo note `config/WRTC_DATASETS.md`

  - [Wildfire Hazard Potential](https://research.fs.usda.gov/firelab/products/dataandtools/wildfire-hazard-potential) (triangulation only)

  - [LANDFIRE](https://landfire.gov/) · [EVT](https://landfire.gov/vegetation/evt)

  - [PAD-US](https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download) · [SILVIS WUI](https://silvis.forest.wisc.edu/data/wui-change/)

  - [PNAS — Rx fire and PM2.5](https://www.pnas.org/doi/10.1073/pnas.2613722123)

  - [CUP WFE methods](https://conservation-data-lab.github.io/cup_assessment/fire.html)

  - [Bailey ecoregions (AOI)](https://doi.org/10.2737/RDS-2016-0003)

  - [TreeMap](https://data.fs.usda.gov/geodata/rastergateway/treemap/) · [FIA](https://research.fs.usda.gov/programs/fia)

  - Repo logic: `config/ACTION_ASSIGNMENT.md` · `config/EVT_RULES_LOGIC.md`
