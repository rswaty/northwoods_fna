# Partner notes — next threads (thinking only)

Captured 2026-07-30. **No implementation yet.** These sit beside FAA (strategic “what to do where”) and the existing Northwoods Fire Assessment site ([recent fires page](https://rswaty.github.io/northwoods/recent.html)).

Keep the split clear:

| Track | Question | Cadence |
|-------|----------|---------|
| **FAA (this repo)** | What kind of work, where, for planning conversations? | Seasonal–annual screen on ~10k-acre hexes |
| **Recent / ops support** | What is happening *now*, and who can respond? | Days–weeks; stations, seasonal risk, fresh fire stats |

Do not force every operational layer into the FAA action cascade. Many belong as **context, feasibility, or a companion map**.

---

## 1. Map fire response capacity (stations)

**Ask:** Where are volunteer fire departments, state DNR / natural-resources fire stations, USFS (and other federal) fire stations, and related dispatch/response points?

**Why it matters**

- FAA can rank a hex “treat for people” or Priority 3 with **no nearby engine**. That is still a valid planning signal — but partners need to see the **response gap**.
- Complements **feasibility** (already listed as a limitation): capacity to *suppress* or *support Rx* is different from mills or ownership.
- Supports rapid-response positioning (thread 2): teams and pre-positioning care about distance to stations + current risk, not only strategic Goldilocks.

**How to think about folding it in (later)**

| Role | Recommendation |
|------|----------------|
| Action picker? | **No** — “far from a station” should not invent a new action class by itself. |
| Hex field? | Yes eventually: e.g. distance to nearest VFD / DNR / USFS, or count within X miles → `RESPONSE_DIST` or similar. |
| Score / Goldilocks? | Optional **soft** feasibility filter or dashboard flag (“high people priority + long response time”). |
| Map product? | Strong as a **standalone or overlay** layer for partners — valuable even before hex joins. |

**Data hunt (partners / open layers)**

- State GIS: fire station / VFD / emergency-service points (MI, WI, MN — schemas will differ).
- USFS / federal facility layers; NIFC or regional dispatch directories if usable.
- NFIRS / local address lists are messy; prefer official point layers with agency type.
- Attribute carefully: **volunteer vs career**, **agency**, **year of record** — capacity is not equal across points.

**Design caution:** Response time ≠ ignition risk ≠ treatment need. Keep stations in the **feasibility / ops** family next to mills and current projects — not inside “protect vs ecosystem” rules.

---

## 2. Current / seasonal fire risk for rapid response

**Ask:** Gather the best *current* fire-risk information (especially **seasonal**), summarize it, and see whether it can help **position rapid response teams**.

**Why it matters**

- FAA’s WFE + WRTC screen is **structural** (fuels, housing, ecology). It does not say “this week is extreme in the Arrowhead.”
- Seasonal products (NFDRS / ERC / BI, NWS fire weather, state burn bans, drought, green-up / curing) drive **when** capacity should surge.
- Historic seasonality on the Northwoods [recent fires](https://rswaty.github.io/northwoods/recent.html) page already shows **April peaks** and strong monthly structure — that is strategic context for *when* starts cluster; live indices answer *this season’s* anomaly.

**How to think about the product**

1. **Do not merge into FAA v1 scoring.** Mixing “April climatology” or “today’s ERC” into Goldilocks would make the strategic map twitchy and hard to explain.
2. **Companion operational brief** (weekly/seasonal): map or dashboard strip — where is risk elevated *now* relative to normal, overlaid with stations (1) and optional FAA priority hexes (“strategic need × current danger”).
3. **Summarize for non-modelers:** one page — “typical Northwoods season,” “this year vs normal,” “watch districts,” link to official forecasts (do not replace NWS/state duty officers).

**Data to gather (illustrative)**

- State / interagency daily or weekly fire danger; NFDRS station network.
- Seasonal outlooks (NICC / GACC).
- Fuel moisture / greenness if partners already use them.
- Tie back to Short-based seasonality (thread 3) so “normal April busy-ness” is visible next to “this April.”

**Link to FAA:** Use FAA to answer *where investment conversations should focus*; use seasonal risk + stations to answer *where to put people and engines this month*. Same geography, different question.

---

## 3. Refresh [northwoods recent fires](https://rswaty.github.io/northwoods/recent.html)

**Current page (as of check):** Internal draft. Short (2022) occurrences **1992–2020** clipped to Northwoods (+10 km). Covers count/trends, seasonality (April peak), size distribution, spatial map with human vs natural cause. Mean ~2,550 fires/year in the AOI framing used there.

**Ask:** Add the **latest** data so the page is not stuck ending in 2020.

**Why it matters for FAA + partners**

- Fresh occurrence supports **ignition / start patterns** (FAA limitation) without overloading the action cascade.
- Updated seasonality and hotspots feed rapid-response storytelling (thread 2).
- Keeps the public/partner Northwoods site aligned with the FAA conversation (“we are not only building hex actions; we also track what actually ignited”).

**Thinking for the update**

| Task | Note |
|------|------|
| Extend years past 2020 | Prefer same Short family or successor / state occurrence compilations; document source break if schema changes. |
| Keep cause (human vs natural) | Feeds ignition discussion and prevention vs lightning narratives. |
| Preserve seasonality + size + map | Don’t drop what managers already understand; add years and a clear “data through YYYY” banner. |
| Optional extras later | Large-fire perimeters, link to FDist fuel-add story, or “starts near FAA Priority 3 hexes” as a crosswalk — only after core refresh. |

**Repo note:** That site is [rswaty/northwoods](https://github.com/rswaty/northwoods) (separate from this FAA repo). FAA should **link** to it; occurrence ETL need not live here unless we deliberately share pipelines.

---

## 4. Think through “protections” in FAA

“Protect” is doing a lot of work in partner language. Split it deliberately so FAA stays accurate.

### 4a. Three different meanings of “protect”

| Meaning | In FAA today | Risk if confused |
|---------|----------------|------------------|
| **A. Action class `value_to_protect_from_fire`** | Keep damaging fire *out* of a listed **asset** (v1: mainly plantations; people path is now `treat_fire_risk_for_people`) | Calling everything “protect” sounds like land-protection (PAD) or suppression-only. |
| **B. Values to protect (catalog)** | Homes/communities, plantations; infrastructure placeholder; PAD/resilient as context or multipliers — see `config/values_to_protect.csv` | Catalog grows; each value needs a spatial rule and whether it **picks action** or only **raises score**. |
| **C. Protected lands (PAD-US)** | Ownership/mandate context; GAP 1–3 was a score multiplier — partners already worry it skews away from private industrial timber | PAD ≠ “must protect from fire”; wilderness may want fire *in*. |

**Recommendation for partner talk:** Say **protect assets / values from damaging fire**, not “protect the landscape.” Ecosystem work is **ecosystem health focus**, not “unprotected.”

### 4b. What should be in the protection / values catalog next?

| Candidate | Action vs score? | Notes |
|-----------|------------------|--------|
| Homes / communities | Already drives people action + people-first score | Keep primary. |
| Plantations / industrial timber | Action: value_to_protect_from_fire | Improve map beyond EVT; adjacency to “risky” fuels (limitation). |
| Critical infrastructure | Placeholder | Power, water, telecom — partner layers; likely protect or people-adjacent hint. |
| Valuable timber *beside* risky timber | Not solved | May need neighbor rules or nested hexes — protection of asset + treatment of adjacent fuels in one conversation. |
| Municipal watersheds / water | Not in v1 | Often “protect” in agency language; decide action vs score with partners. |
| Cultural / tribal values | Not mapped here | Must stay consultation-led; do not invent a silent GIS proxy. |
| Biodiversity / resilient lands | Limitation — context later | Do not equate PAD with biodiversity protection. |

### 4c. Protections vs response capacity

- **Protect (values)** = *what we care about if fire runs.*  
- **Stations (thread 1)** = *who can get there.*  
- High-value + long response time = priority for **prevention, hardening, and pre-positioning conversations** — still may stay `treat_fire_risk_for_people` or `value_to_protect_from_fire`, with a feasibility flag, not a new vague “protect more” class.

### 4d. Open design questions (answer with partners before coding)

1. Should **any** new value (infrastructure, watersheds) **force** `value_to_protect_from_fire`, or only boost score under an existing action?
2. Do we **remove PAD from scoring** and keep it as context only (earlier feedback)? That changes what “protected land” means in the product.
3. Is **suppression response gap** a dashboard overlay only, or a Goldilocks demotion/promotion?
4. How do we name actions so “protect” never sounds like “no fire ever on this hex” when the hex is fire-adapted and away from assets?

---

## 5. Meet with Krystina Hird — project + mill locations

**To-do (you):** Schedule / hold a working meeting with **Krystina Hird** to walk the FAA concept and dig into **mill locations** (and related wood-utilization geography).

**Why this meeting**

- Mills are already on the design horizon as **feasibility** (where low-value / treatment wood can go) — not as an action picker.
- Partner trust: industry and agency staff often know mill status (open/closed, species accepted, haul distance) better than a static GIS layer.
- Ties to **protections** (valuable timber) and **plantations** (4 / 8): what is economically worth protecting, and where treated material can move.

**Agenda prompts (suggested)**

1. Two-minute FAA pitch: actions + Goldilocks, not prescriptions.  
2. What mill / concentration-yard layers does she trust for MI / WI / MN Arrowhead? Year? Public vs ask-industry?  
3. Haul distance that still “counts” as feasible for fuels/thinning byproducts?  
4. Does mill proximity change **priority** only, or also **treatment hint** (e.g. commercial thin more realistic)?  
5. Any conflict with “protect plantation / industrial timber” — mills as demand signal vs asset map?  
6. Who else should review mill and timber-value layers?

**After the meeting:** Capture agreed sources and rules in this file (or `values_to_protect` / a future mills note). Do not code until sources and “score vs hint only” are clear.

---

## 6. LANDFIRE disturbances as fuel-add / fuel-remove (document prior design)

**Status:** Discussed for FAA; **not coded yet.** Needed for Arrowhead insects and lower-Michigan wind/ice — cases where **WFE undersells** current fuel concern.

### Intent

Classify LANDFIRE **FDist** (or equivalent disturbance) codes into a simple fuel-direction lookup, then summarize to hexes:

| Code meaning | Lookup value | Examples (illustrative — finalize from AOI RAT / attribute table) |
|--------------|--------------|---------------------------------------------------------------------|
| Fuel **remove** | **−1** | Fire (and some harvest types, if partners agree) |
| Neutral / unknown | **0** | No disturbance, or types that don’t clearly change fine/ladder fuels |
| Fuel **add** | **+1** | Insects/disease, wind/ice, blowdown, etc. |

**Hex field (proposed):** `FDIST_FUEL_DELTA` = **area-weighted mean** of −1 / 0 / +1 over the hex → roughly in **[−1, +1]**.

**Time window:** **Last 10 years** (agreed). Older events should not dominate “current concern.”

### Why this is in FAA (not only a pretty map)

- High WFE ≠ recent fuel add; low WFE + high fuel-add is a **first-class** situation (ice/wind near homes; insect-killed fuels).  
- Proposed cascade idea (for when matrix + CSV are ready): after plantation/peat, allow **low WFE + fuel-add** to still reach `treat_fire_risk_for_people` or an ecosystem / disturbance-fuels path — see `ACTION_MATRIX_DRAFT.csv`.  
- Also feed **priority** so Goldilocks can surface fuel-add hexes even when WFE is soft.

### Design rules (keep elegant)

| Role | Recommendation |
|------|----------------|
| Action picker? | **Yes, carefully** — only via explicit matrix rows (esp. low WFE + fuel-add); not a silent rewrite of WFE. |
| Score term? | **Yes** — small weight so fuel-add can enter people-first ranking. |
| Undisturbed pixels | Treat as **0**, not NoData dropped from the mean (same lesson as WRTC NoData). |
| Magnitude | Start with −1/0/+1; severity bands later if needed. |
| Partner CSV | You will supply FDist code → −1/0/+1 table; build from the **clipped raster’s** attribute table so codes match. |

### Open before coding

1. Exact FDist year filter (calendar years vs LANDFIRE vintage).  
2. Is harvest always −1, 0, or partner-specific?  
3. Cutoff for “high fuel-add” (draft ~**δ ≥ 0.25**).  
4. Away-from-people + fuel-add: new action vs reuse `ecosystem_health_focus`?

---

## 7. Highlight high-value (economic) forests near high-risk areas

**Ask:** Can we show where **economically valuable** forests sit **next to** (or in) **high wildfire risk**?

**Why it matters**

- Classic Northwoods tension: timber you do not want to burn / lose, adjacent to fuels that will carry fire (jack pine, insect-killed stands, untreated WUI edge).  
- Already listed as a limitation (“valuable timber next to risky timber”); partners will ask for a **map they can point at in a meeting**, not only a hex action label.  
- Different from “plantation = protect”: high-value may be natural-origin red pine, selective industrial land, or mature sawtimber — **EVT plantation flag will miss most of it.**

### Ways to think about it (no code yet)

| Approach | Pros | Cons |
|----------|------|------|
| **A. Same-hex coincidence** | Simple: high timber-value flag × high WFE (or fuel-add) inside one hex | 10k-acre hex averages; “near” is weak |
| **B. Neighbor / adjacency** | Flag hexes where value is high and a **neighbor** hex is high risk (or shared edge with high-risk pixels) | Clearer “beside”; needs rules for queen vs rook neighbors, thresholds |
| **C. Pixel / fine overlay first** | Map product: value layer ∩ buffered high-WFE or FDist-add | Best for conversation; may not need to change FAA actions in v1 |
| **D. Nested finer hexes later** | Designed-in path for FAA | More work; don’t block a simple overlay |

**Recommended path:** Start with a **companion highlight map** (C or simple A), using whatever timber-value layer Krystina / industry trust. Use it to **raise score or flag** (`TIMBER_VALUE_NEAR_RISK`) before inventing a new action. Action remains protect / people / ecosystem as today; the highlight answers “*why this conversation is awkward.*”

**Depends on:** Better value map (meeting 5 + plantations 8). “High risk” can be WFE high, fuel-add high, or FAA Priority ≥ 1 — pick one definition with partners so the map is explainable.

### Open questions

1. Is “high value” stumpage class, forest type, ownership (industrial), or mill-shed sawtimber?  
2. Distance that counts as “near” — shared hex, 1 neighbor, or X meters?  
3. Does adjacency ever **force** `value_to_protect_from_fire`, or only a dashboard/priority flag?

---

## 8. Better plantation map (beyond LANDFIRE EVT) — satellite?

**Ask:** Replace or supplement EVT plantation (e.g. code 9312) with a **better plantation / managed tree-farm** layer. Satellite or other remote sensing?

**Why it matters**

- EVT undercounts / mislabels managed plantations → `value_to_protect_from_fire` and plantation score terms are incomplete.  
- Design already assumed a later **swap** into the same `PLANTATION_HEX` flag without rebuilding the cascade — keep that pattern.

### Options to evaluate (thinking)

| Source family | Notes |
|---------------|--------|
| **State / industry GIS** | Best if it exists (forest inventory, industry shapefiles) — ask in Hird meeting. |
| **LANDFIRE / TreeMap / imputation** | May improve structure; still not always “plantation” as ownership intent. |
| **Satellite / ML land cover** | Possible: texture, planting rows, spectral age classes; needs training labels and accuracy assessment for Northwoods. High effort; partner-facing accuracy claims matter. |
| **Manual / partner digitize priority zones** | Pragmatic interim for Goldilocks corridors. |

**Recommendation:** Do **not** lead with a custom satellite model unless industry layers fail. Meeting (5) first → existing vector layers → only then scope RS. Whatever wins still writes **`PLANTATION_HEX` (or successor)** and keeps action = value_to_protect_from_fire.

**Link to (7):** Plantation map is one slice of economic value; industrial natural stands may need a separate “timber value” layer so adjacency highlights aren’t plantation-only.

---

## Suggested sequencing (still no code)

1. **Meet Krystina Hird** (5) — mills, timber value, plantation/industry layers.  
2. **FDist + EVT `FIRE` → actions** — design locked below (§9–10); fill matrix critical rows, then implement.  
3. **PAD = context only** — decision locked (§9); drop from score when coding next; keep on Leaflet.  
4. **Refresh** occurrence on [recent.html](https://rswaty.github.io/northwoods/recent.html) (3).  
5. **Companion maps:** stations (1); high-value near high-risk highlight (7) once value layer exists.  
6. **Plantation layer upgrade** (8) when a trusted source beats EVT.  
7. **Seasonal risk brief** (2) as ops companion.  

---

## 9. Decision log (2026-08-04)

| Decision | Choice | Implication |
|----------|--------|-------------|
| **PAD-US** | **Context only** — not a score multiplier, not an action input | Keep `PADUS_FRAC` on hexes for Leaflet/symbology/popups; set `w_pad_multiplier` effect to unused / 0 in scoring when next coded. Partners still *see* protected-land share. |
| **FDist `FUEL_DIRECTION_1`** | −1 remove / 0 neutral / +1 add; Mechanical Add = −1 (chipping etc.) | Hex `FDIST_FUEL_DELTA` = area-weighted mean; “high fuel-add” ≈ δ ≥ ~0.25 (tune after first map). |
| **EVT `FIRE`** | 1 = fire-dependent; 0 = not; −1 = bad if burned (developed, plantation, ruderal) | **Not** the same scale as FDist. Use for ecology / protect signals — see §10. |
| **Action matrix** | Fill after reviewing this design | Critical rows: plantation, peat, WFE×people, low-WFE+fuel-add, fire-adapted without high WFE. |
| **Fuel-add, not-high people** | **`ecosystem_health_focus`** | Confirmed 2026-08-04. |
| **Fire-adapted pines (incl. low WFE)** | **`ecosystem_health_focus`** | Confirmed — pine/barrens list; near people still ecosystem unless higher cascade steps (high WFE / fuel-add → people) already matched. |
| **Developed EVT `FIRE=−1`** | Context only; people via WRTC | Not an auto-protect trigger. |

---

## 10. How FDist + EVT `FIRE` fit the cascade (review before matrix)

### Two different signals

| Input | Hex idea | Answers |
|-------|----------|---------|
| **WFE** | already on hex | How hot can fire run *today*? |
| **FDist delta** | mean of `FUEL_DIRECTION_1` | Did recent disturbance **add** fuels WFE may miss? |
| **EVT `FIRE`** | join on `EVT_MAJORITY` | Is this **fire-adapted** (1), not (0), or **bad to burn** (−1)? |
| **PAD** | `PADUS_FRAC` | Context on the map only. |
| **People** | WRTC | Near homes? |

### Goal
Flag **red pine / fire-adapted** and **fuel-add–heavy** hexes with a real action — **without** turning half the AOI into “do something” (EVT `FIRE=1` alone includes huge swamp/fen acres).

### Proposed cascade (first match) — for matrix review

1. **Plantation** (EVT rules only) → **`value_to_protect_from_fire`**  
   - EVT `FIRE = −1` includes developed/ruderal **and** plantation. **Do not** auto-protect every `FIRE=−1` hex.  
   - **Developed as `FIRE=−1`:** marks “don’t burn / development present” for context. Those places should already surface in **WRTC people** layers when housing risk is present — people actions come from **high people × (high WFE or high fuel-add)**, not from the −1 flag alone. Avoid double-counting development in both EVT and the cascade.  
   - Other non-plantation `FIRE=−1` (ruderal, etc.) → usually fall through to **defer** unless people/WFE/fuel-add rules catch them.  
2. **Peat** (existing EVT peat list) → **`wetlands_assess_locally`** (catches most acidic peat/fen; runs before fire-dep).  
3. **High WFE + high people** → **`treat_fire_risk_for_people`**  
4. **High WFE + not-high people** → **`ecosystem_health_focus`**  
5. **High fuel-add + high people** (WFE any, including low) → **`treat_fire_risk_for_people`**  
   - Arrowhead insects / MI ice–wind near homes.  
6. **High fuel-add + not-high people** → **`ecosystem_health_focus`** (confirmed).  
7. **Fire-adapted pines/barrens** (when not already caught above) → **`ecosystem_health_focus`** (including near people if WFE/fuel-add not high):  
   - **Include:** pine/barrens EVT list (`config/evt_pine_barrens.csv`).  
   - **Exclude:** peat (already step 2); other `FIRE=1` wetlands/swamps not on the pine list.  
8. **Else** → **`defer_monitor`**

**Goldilocks unchanged in spirit:** only actionable hexes; top 5/10/15% by people-first score. More actions ≠ everyone is Priority 3 — the short list stays small.

### What you should see on Leaflet (eventually)

| Layer / field | Role on map |
|---------------|-------------|
| `ACTION_CLASS` | Fill / legend (primary) |
| `GOLDILOCKS_PRIORITY` | Emphasis / filter |
| `PADUS_FRAC` | **Context** (opacity, second symbology, or popup) — not driving color of action |
| `FDIST_FUEL_DELTA` | Popup + optional overlay (“fuel-add heavy”) |
| EVT-based fire flag | Popup (“fire-adapted / not / bad if burned”) |

### Rough size control (mental model)

| Rule | Effect on map volume |
|------|----------------------|
| Fuel-add high | Relatively few hexes — good action flags |
| High WFE | Already ~183 actionable (91+92) in last run |
| All EVT `FIRE=1` | **Too big** — includes massive swamp/fen |
| `FIRE=1` ∩ pine/barrens-type only | Targets red/jack pine story without flooding |
| Peat first | Wetlands stay `wetlands_assess_locally`, not ecosystem |

### Locked for matrix / coding (2026-08-04)

Cascade steps 5–7 confirmed. Next: fill `ACTION_MATRIX_DRAFT.csv` to match, then implement (PAD out of score; FDist zonal; EVT `FIRE` + pine list join; Leaflet context for PAD).

Optional later: publish the exact pine/barrens EVT code list in `config/` (can draft from `evt_aoi_attributes.csv` where `FIRE=1` and pine/barrens in the name/GP).
