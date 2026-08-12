# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%/15%, actionable hexes only, AOI-wide).  
**PAD:** map **context only** (`PADUS_FRAC`). **BpS / EVT_FIRE:** context only. **Recreation:** deferred.

Partner review matrix (no fuel): `config/ACTION_MATRIX.md` · `config/ACTION_MATRIX_REVIEW.csv`.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT plantation | Yes | → **always** `protect_from_fire` |
| EVT peat | Yes | → `wetlands_assess_locally` |
| WFE (strict) | Yes | High/VH, or Moderate with MEAN in top 30% → people vs ecosystem split. **Low/VL never** opens treat-for-people. |
| WFE (ecosystem elevated) | Yes | Strict high **or** Low/VL with MEAN still in top 30% → `ecosystem_health_focus` |
| WRTC Housing Unit Risk | Yes | "High people" with **strict** high WFE → treat-for-people |
| FDist fuel-add | Yes | Separate path (not in current review matrix) |
| EVT pine/barrens list | Yes | Safety net → ecosystem when earlier rules did not match |
| EVT `FIRE` (−1/0/1) | Context | Popup / review only |
| BpS / MFRI (`FIRE_DEP_HEX`) | Context | Popup / review only |
| PAD-US GAP 1–3 | Context | Map only |

## Action cascade (first match wins)

1. **Plantation** → `protect_from_fire`  
2. **Peat** → `wetlands_assess_locally`  
3. **Strict high WFE + high people** → `treat_fire_risk_for_people`  
4. **Elevated WFE for ecosystem** → `ecosystem_health_focus`  
5. **High fuel-add + high people** → `treat_fire_risk_for_people`  
6. **High fuel-add + not-high people** → `ecosystem_health_focus`  
7. **Pine/barrens list** → `ecosystem_health_focus`  
8. **Else** → `defer_monitor`  

### What “high / elevated WFE” means

- **Strict (people path):** High/VH category; or Moderate/missing with MEAN ≥ AOI 70th percentile. Low/VL → never.  
- **Ecosystem elevated:** strict **or** Low/VL with MEAN ≥ AOI 70th percentile.  

So a Low label can still get an ecosystem conversation if the continuous score is relatively high; it cannot get treat-for-people from that alone.

## Goldilocks

Rank `SCORE_PEOPLE` over hexes that are not `defer_monitor` and not `wetlands_assess_locally` (full AOI). Priority 3/2/1 = top 5/10/15% of that pool.
