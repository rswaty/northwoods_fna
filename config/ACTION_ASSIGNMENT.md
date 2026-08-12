# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%/15%, actionable hexes only, AOI-wide).  
**PAD:** map **context only** (`PADUS_FRAC`). **BpS / EVT_FIRE:** context only. **Recreation:** deferred.

Partner review matrix: `config/ACTION_MATRIX.md` · `config/ACTION_MATRIX_REVIEW.csv`.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT plantation | Yes | → **always** `value_to_protect_from_fire` |
| EVT peat | Yes | → `wetlands_assess_locally` |
| WFE category | Yes | **High / Very High bin only** → people vs ecosystem split |
| People category | Yes | AOI **quintile** bins (`PEOPLE_CAT`, same five labels as WFE). High/VH + High/VH WFE → treat |
| EVT pine/oak list (top 3) | Yes | Safety net → ecosystem when people are **Moderate / Low / Very Low** (tighten) |
| FDist fuel direction | Goldilocks + map | Score multiplier (add > remove) and brown/green layer |
| EVT `FIRE` (−1/0/1) | Context | Popup / review only |
| BpS / MFRI (`FIRE_DEP_HEX`) | Context | Popup / review only |
| PAD-US GAP 1–3 | Context | Map only |

## Action cascade (first match wins)

1. **Plantation** → `value_to_protect_from_fire`  
2. **Peat** → `wetlands_assess_locally`  
3. **High/VH WFE + High/VH people** → `treat_fire_risk_for_people`  
4. **High/VH WFE** → `ecosystem_health_focus`  
5. **Pine/oak in EVT top 3 + people Moderate/Low/VL** → `ecosystem_health_focus`  
6. **Else** → `defer_monitor`  

### Bins

- **WFE:** use product `WFE_CAT` (Very Low … Very High). Actions use High/VH only — no MEAN percentile bypass.  
- **People:** `PEOPLE_CAT` from AOI quintiles of `WRTC_HU_RISK_MEAN` (20/40/60/80th cuts → Very Low … Very High). Treat needs High/VH.  
- **Pine tighten:** High/VH people + pine + not High/VH WFE → **defer** (homes alone never create treat).

## Goldilocks

Base `SCORE_PEOPLE` (homes / plantation / WFE) × asymmetric **fuel multiplier**  
(`1 + 0.50·δ` add, `1 + 0.25·δ` remove). High/VH WFE or high fuel-add hexes are  
lifted to at least the AOI **40th percentile** of scores (hazard floor).  
Dashboard shows white→purple heat on all hexes (percentile stretch).
