# Action triggers (quick reference)

See also `ACTION_ASSIGNMENT.md` and `ACTION_MATRIX_REVIEW.csv`.

| Order | Action | Trigger |
|------:|--------|---------|
| 1 | `value_to_protect_from_fire` | Plantation EVT majority |
| 2 | `wetlands_assess_locally` | Peat / wetland EVT majority |
| 3 | `treat_fire_risk_for_people` | `WFE_CAT` High/VH **and** `PEOPLE_CAT` High/VH |
| 4 | `ecosystem_health_focus` | `WFE_CAT` High/VH |
| 5 | `ecosystem_health_focus` | Pine/oak in EVT top 3 **and** `PEOPLE_CAT` Moderate/Low/VL |
| 6 | `defer_monitor` | Else |

**People bins:** AOI quintiles of WRTC HU Risk → Very Low … Very High.  
**Fuel:** Goldilocks score multiplier only (α add = 0.50, β remove = 0.25).
