# Action matrix (review)

CSV: [`ACTION_MATRIX_REVIEW.csv`](ACTION_MATRIX_REVIEW.csv).

Fuel (FDist) is **not** an action trigger — it is its own map layer (brown = add, green = remove) and a Goldilocks score multiplier.

---

## Column dictionary

| Column | Values | Meaning |
|--------|--------|---------|
| `plantation` | Y / N / * | Majority EVT is plantation |
| `wetland_dominated` | Y / N / * | Majority EVT is listed peat/wetland |
| `wfe_score_very_high_high` | Y / N / Moderate / * | `WFE_CAT` is High or Very High (`Moderate` = that bin exactly) |
| `people_score_very_high_high` | Y / N / Moderate / Very High / * | `PEOPLE_CAT` is High or Very High (AOI quintiles of building density — a proxy for people; `Very High` = that bin only) |
| `on_pine_oak_evt_list` | Y / N / * | Any of EVT top 3 is on `config/evt_pine_barrens.csv` |
| `action_your_call` | action name | Assigned action |
| `goldilocks_eligible_your_call` | Y / N | Enters Goldilocks ranking pool |
| `notes` | text | Hints |

---

## Cascade

1. Plantation → `value_to_protect_from_fire`  
2. Wetland → `wetlands_assess_locally` (not Goldilocks)  
3. High/VH WFE + Moderate/High/VH buildings, or Moderate WFE + Very High buildings → `treat_fire_risk_for_people` ("Treat fire risk near communities")  
4. High/VH WFE → `ecosystem_health_focus`  
5. Pine/oak top 3 + buildings Moderate/Low/VL → `ecosystem_health_focus`  
6. Else → `defer_monitor`  

**Goldilocks:** among eligible actions, top 5% / 10% / 15% by people-first score (dashboard: heat + top-25% start-here outline).
