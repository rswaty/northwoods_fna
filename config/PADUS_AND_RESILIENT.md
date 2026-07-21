# PAD-US and optional TNC Resilient Lands

## PAD-US v1 rule

Use **GAP Status Codes 1–3 only** (exclude Status 4).

| GAP Status | Meaning (short) | In v1 multiplier? |
|------------|-----------------|-------------------|
| 1 | Permanent protection; natural state; natural disturbance allowed/mimicked (e.g. wilderness, some parks) | Yes |
| 2 | Permanent protection; primarily natural; some management that may interfere with natural processes | Yes |
| 3 | Permanent protection from conversion; multiple use allowed (e.g. many National Forests, state forests) | Yes |
| 4 | No known mandate against conversion / unknown | **No** |

Hex field: `PADUS_FRAC` = fraction of hex that is GAP Status 1–3.

**Input format:** raster *or* polygons.

| Format | How `03_zonal_evt_padus.py` works |
|--------|-----------------------------------|
| **Raster** (preferred here) | Reclassify GAP status → binary (1 where ∈ {1,2,3}, else 0); zonal **MEAN** = `PADUS_FRAC`. Set `padus_type: raster`. **If GAP status is in a RAT field (e.g. `GAP_Sts`) and the cell value is only an index, set `padus_gap_field` so the reclass reads that field — not the raw cell value.** Reading the raw index makes the GAP 4 private matrix (often index 1) read as protected → `PADUS_FRAC≈1` almost everywhere. |
| **Polygons** | Select `GAP_Sts` in 1–3, intersect, area fraction. Set `padus_type: polygon`. |

**Role:** priority **multiplier** for (a) management feasibility on non-small-ownership lands and (b) lands with a conservation/multiple-use mandate. Does **not** pick action class. High WRTC × high WFE outside PAD still ranks.

Weight presets: **people_first** (default Goldilocks), plantation_asset_first, **pad_first** (strong PAD 1–3 boost), balanced.

## What TNC Resilient Lands would do *in this analysis*

People-first FAA question: where should limited work go to reduce wildfire risk to homes (and plantations), with sensible ecosystem deferrals?

PAD 1–3 already answers: “boost places where agencies/partners can act and land has a conservation/multiple-use mandate.”

[TNC Resilient & Connected Lands](https://www.maps.tnc.org/resilientland/) would add a **second multiplier** for “where nature is more likely to persist under climate change,” including lands **outside** PAD:

| In this analysis | Effect |
|------------------|--------|
| Does **not** change action class | Still peat→defer, homes/plantations→protect, high WFE→beneficial fire |
| **Raises priority** on resilient hexes | Same people×WFE story ranks higher if the hex is in the resilient network |
| **Surfaces unprotected resilient land** | High WRTC or high WFE on resilient private land gets a bump PAD alone would miss |
| **Connectivity / climate flow** | Optional later nuance: prefer hexes that keep resilient networks linked |

**Concrete example:** two hexes with similar Housing Unit Risk and WFE—one is GAP 3 National Forest (PAD boost), one is resilient private timberland (no PAD). With PAD only, the NF ranks higher. With resilient lands added, the private resilient hex can catch up when partners care about climate-smart biodiversity *and* people risk.

**What it is not:** a species list, a recreation layer, or a reason to treat away from homes. Under people-first, resilient lands only **re-order** among already-urgent hexes (or pull in a few resilient high-WFE areas partners care about).

### If / when added

```text
score = base × (1 + w_pad × PADUS_1to3_FRAC) × (1 + w_resilient × RESILIENT_FRAC)
```

- People-first stays default Goldilocks; resilient weight stays modest unless a partner asks for a “resilient-lands” view.
- Do **not** replace PAD—stack them.
- Recreation remains deferred.

v1 ships with **PAD 1–3 only**.
