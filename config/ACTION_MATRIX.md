# Action matrix (review)

CSV: [`ACTION_MATRIX_REVIEW.csv`](ACTION_MATRIX_REVIEW.csv).

Fuel (FDist) is **not** an action trigger — it only multiplies Goldilocks scores.

---

## Column dictionary

| Column | Values | Meaning |
|--------|--------|---------|
| `plantation` | Y / N / * | Majority EVT is plantation |
| `wetland_dominated` | Y / N / * | Majority EVT is listed peat/wetland |
| `wfe_score_very_high_high` | Y / N / * | `WFE_CAT` is High or Very High |
| `people_score_very_high_high` | Y / N / * | `PEOPLE_CAT` is High or Very High (AOI quintiles) |
| `on_pine_oak_evt_list` | Y / N / * | Any of EVT top 3 is on `config/evt_pine_barrens.csv` |
| `action_your_call` | action name | Assigned action |
| `goldilocks_eligible_your_call` | Y / N | Enters Goldilocks ranking pool |
| `notes` | text | Hints |

---

## Cascade

1. Plantation → `value_to_protect_from_fire`  
2. Wetland → `wetlands_assess_locally` (not Goldilocks)  
3. High/VH WFE + High/VH people → `treat_fire_risk_for_people`  
4. High/VH WFE → `ecosystem_health_focus`  
5. Pine/oak top 3 + people Moderate/Low/VL → `ecosystem_health_focus`  
6. Else → `defer_monitor`  

**Goldilocks:** among eligible actions, top 5% / 10% / 15% by people-first score × fuel multiplier.
