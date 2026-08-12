# Action triggers review (FAA cascade)

Partner/review notes. First matching rule wins.  
Fillable matrix (no fuel): `config/ACTION_MATRIX.md` · `ACTION_MATRIX_REVIEW.csv`.

## High WFE and high people

| Term | Definition |
|------|------------|
| **High people** | Top **30%** WRTC Housing Unit Risk. |
| **Strict high WFE** | (1) High/VH category; (2) Low/VL → **never**; (3) Moderate/missing → MEAN in top 30%. Used for **treat-for-people**. |
| **Elevated WFE for ecosystem** | Strict high **or** Low/VL with MEAN in top 30%. |
| Design intent | Homes alone never imply treat-for-people. Quiet labels can still open ecosystem if MEAN is relatively high. |

| Order | Action | Trigger |
|------:|--------|---------|
| 1 | `protect_from_fire` | Plantation EVT majority |
| 2 | `wetlands_assess_locally` | Peat / listed wetland majority |
| 3 | `treat_fire_risk_for_people` | Strict high WFE **and** high people |
| 4 | `ecosystem_health_focus` | Elevated WFE for ecosystem |
| 5–6 | treat / ecosystem via fuel-add | When WFE not elevated — **separate review** |
| 7 | `ecosystem_health_focus` | Pine/barrens EVT list |
| 8 | `defer_monitor` | Nothing above |

## Context only

| Field | Role |
|-------|------|
| `PADUS_FRAC` | Map only |
| `EVT_FIRE` | Popup / your EVT table — not an action trigger |
| `FIRE_DEP_HEX` / BpS | Popup / historic context — not an action trigger |

## Goldilocks

`GOLDILOCKS_PRIORITY` 3/2/1 = top 5/10/15% of `SCORE_PEOPLE` among actionable hexes (**AOI-wide**). Defers and wetlands always 0.
