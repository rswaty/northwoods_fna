# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%/15%, actionable hexes only, AOI-wide).  
**PAD:** map **context only** (`PADUS_FRAC`). **BpS / EVT_FIRE:** context only. **Recreation:** deferred.

Partner review matrix: `config/ACTION_MATRIX.md` · `config/ACTION_MATRIX_REVIEW.csv`.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT plantation | Yes | → **always** `value_to_protect_from_fire` |
| EVT peat | Yes | → `wetlands_assess_locally` |
| WFE category | Yes | **High / Very High** → people vs ecosystem split; **Moderate** → treat only with Very High buildings |
| Building category (people proxy) | Yes | AOI **quintile** bins of building density (`PEOPLE_CAT`, same five labels as WFE). Moderate/High/VH + High/VH WFE, or Very High + Moderate WFE → treat |
| EVT pine/oak list (top 3) | Yes | Safety net → ecosystem when buildings are **Moderate / Low / Very Low** (tighten) |
| FDist fuel direction | Goldilocks + map | Score multiplier (add > remove) and brown/green layer |
| EVT `FIRE` (−1/0/1) | Context | Popup / review only |
| BpS / MFRI (`FIRE_DEP_HEX`) | Context | Popup / review only |
| PAD-US GAP 1–3 | Context | Map only |

## Action cascade (first match wins)

1. **Plantation** → `value_to_protect_from_fire` (label: "Protect plantations from fire"; other mapped values can join later)  
2. **Peat** → `wetlands_assess_locally`  
3. **High/VH WFE + Moderate/High/VH buildings**, or **Moderate WFE + Very High buildings** → `treat_fire_risk_for_people` (label: "Treat fire risk near communities")  
4. **High/VH WFE** → `ecosystem_health_focus`  
5. **Pine/oak in EVT top 3 + buildings Moderate/Low/VL** → `ecosystem_health_focus`  
6. **Else** → `defer_monitor`  

### Bins

- **WFE:** use product `WFE_CAT` (Very Low … Very High). Actions use High/VH, plus Moderate for the Very High building rule — no MEAN percentile bypass.  
- **Buildings (people proxy):** `PEOPLE_CAT` from AOI quintiles of `WRTC_BLDG_DENSITY_MEAN` (20/40/60/80th cuts → Very Low … Very High). Buildings show where structures are, not a population count; the field keeps its `PEOPLE_CAT` name for the role it plays.  
  Housing Unit Risk is **not** used (embeds wildfire; double-counts with WFE).  
- **Pine tighten:** High/VH buildings + pine + not High/VH WFE → **defer** (buildings alone never create treat).

## Goldilocks

Base `SCORE_PEOPLE` = `0.50·people_pct + 0.15·plantation + 0.25·wfe_pct`, where  
`people_pct` / `wfe_pct` are 0–1 AOI percentile ranks of `WRTC_BLDG_DENSITY_MEAN` / WFE `MEAN`  
(plantation 0/1; weights from `weight_presets.csv`), × asymmetric **fuel multiplier**  
(`1 + 0.50·δ` add, `1 + 0.25·δ` remove). High/VH WFE or high fuel-add hexes are  
lifted to at least the AOI **40th percentile** of scores (hazard floor).  
Dashboard shows white→purple heat on all hexes (percentile stretch).
