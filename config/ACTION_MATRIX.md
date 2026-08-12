# Action matrix (review - no fuel-add)

Fill `action_your_call` and `goldilocks_eligible_your_call`.  
Code today is in `action_code_now` and `goldilocks_eligible_code_now`.  
Fuel-add / FDist left out on purpose (separate feedback later).

CSV: [`ACTION_MATRIX_REVIEW.csv`](ACTION_MATRIX_REVIEW.csv) (all columns snake_case).

---

## Column dictionary

| Column | Values | Meaning |
|--------|--------|---------|
| `plantation` | Y / N / * | Majority EVT is the plantation type (code 9312). * = any |
| `peat` | Y / N / * | Majority EVT is a listed peat/wetland type |
| `wfe_label` | high / moderate / low / * | Published WFE category: high = High or Very High; moderate = Moderate; low = Low or Very Low |
| `wfe_score_high` | Y / N / * | Continuous hex WFE score (`MEAN`) is among the **highest 30% of hexes** in this AOI (at or above the 70th percentile). Not the category label. |
| `people` | high / low / * | high = housing-unit risk among the highest 30% of hexes; low = below that |
| `on_pine_barrens_list` | Y / N / * | Majority EVT is on the short **pine/barrens list** in `config/evt_pine_barrens.csv` (e.g. jack pine-red pine, pine barrens). Safety net when WFE does not already assign an action. |
| `action_code_now` | action name | What the cascade assigns today |
| `action_your_call` | (blank) | **You fill** - agree or write a different action |
| `goldilocks_eligible_code_now` | Y / N | Y = hex would enter the Goldilocks ranking pool (not defer, not wetlands). Exact priority 1-3 still depends on people-first score rank among that pool. |
| `goldilocks_eligible_your_call` | (blank) | **You fill** - should this situation be eligible for Goldilocks? Y/N |
| `notes` | text | Hints / review flags (ASCII only) |

---

## Plain rules in the code now

1. Plantation -> protect_from_fire  
2. Peat/wetland -> wetlands_assess_locally (not Goldilocks-eligible)  
3. Strict high WFE + high people -> treat_fire_risk_for_people  
4. Elevated WFE for ecosystem -> ecosystem_health_focus  
5. Pine/barrens EVT list (if still unmatched) -> ecosystem_health_focus  
6. Else -> defer_monitor  

**Strict high WFE** (needed for treat_for_people):  
`wfe_label` = high, **or** `wfe_label` = moderate with `wfe_score_high` = Y.  
`wfe_label` = low never qualifies for treat_for_people.

**Elevated WFE for ecosystem**:  
strict high WFE, **or** `wfe_label` = low with `wfe_score_high` = Y.

**Goldilocks:** among eligible actions only, top 5% / 10% / 15% by people-first score (AOI-wide) get priority 3 / 2 / 1.

---

## Matrix

| row | plantation | peat | wfe_label | wfe_score_high | people | on_pine_barrens_list | action_code_now | action_your_call | goldilocks_eligible_code_now | goldilocks_eligible_your_call | notes |
|----:|:----------:|:----:|:---------:|:--------------:|:------:|:--------------------:|-----------------|------------------|:----------------------------:|-------------------------------|-------|
| 1 | Y | * | * | * | * | * | protect_from_fire | | Y | | Always - timber asset |
| 2 | N | Y | * | * | * | * | wetlands_assess_locally | | N | | Always - local peat call; out of Goldilocks |
| 3 | N | N | high | * | high | * | treat_fire_risk_for_people | | Y | | Classic hot exposure + many homes |
| 4 | N | N | high | * | low | * | ecosystem_health_focus | | Y | | Hot exposure + few homes |
| 5 | N | N | moderate | Y | high | * | treat_fire_risk_for_people | | Y | | Moderate label + high continuous WFE + many homes |
| 6 | N | N | moderate | Y | low | * | ecosystem_health_focus | | Y | | Moderate label + high continuous WFE + few homes |
| 7 | N | N | moderate | N | high | * | defer_monitor | | N | | Rare in this AOI |
| 8 | N | N | moderate | N | low | * | defer_monitor | | N | | Rare in this AOI |
| 9 | N | N | low | Y | high | N | ecosystem_health_focus | | Y | | REVIEW: quiet label, high continuous WFE, many homes - ecosystem not treat_for_people |
| 10 | N | N | low | Y | low | N | ecosystem_health_focus | | Y | | Quiet label, high continuous WFE, few homes |
| 11 | N | N | low | Y | high | Y | ecosystem_health_focus | | Y | | Same as row 9; also on pine/barrens list |
| 12 | N | N | low | Y | low | Y | ecosystem_health_focus | | Y | | Same as row 10; also on pine/barrens list |
| 13 | N | N | low | N | high | N | defer_monitor | | N | | Homes alone do not treat |
| 14 | N | N | low | N | low | N | defer_monitor | | N | | Typical quiet hex |
| 15 | N | N | low | N | high | Y | ecosystem_health_focus | | Y | | Pine/barrens list safety net |
| 16 | N | N | low | N | low | Y | ecosystem_health_focus | | Y | | Pine/barrens list safety net |

---

## Questions for you

1. Rows 9 / 11: keep ecosystem, switch to defer, or something else?  
2. Rows 15 / 16: keep pine/barrens list as ecosystem safety net?  
3. Any Goldilocks eligibility changes (especially wetlands = N today)?  
4. Ready for a fuel-add pass after this?
