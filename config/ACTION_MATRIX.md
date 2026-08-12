# Action matrix (review — no fuel-add)

Work through the **Your call** column. Code today follows **Code now**. Fuel-add / FDist is left out on purpose (separate feedback later).

## Plain rules in the code now

1. **Plantation** → Protect from fire  
2. **Peat / listed wetland** → Wetlands — assess locally  
3. **Strict high WFE + high people** → Treat fire risk for people  
4. **Elevated WFE for ecosystem** → Ecosystem health focus  
5. **Pine / barrens EVT list** (if still unmatched) → Ecosystem health focus  
6. Else → Defer and Monitor  

**Strict high WFE** (needed for “treat for people”):  
label High or Very High, **or** Moderate with average score in the top 30% of this map.  
**Low / Very Low label never counts** — even with many houses.

**Elevated WFE for ecosystem**:  
strict high WFE, **or** Low/Very Low label **but** average score still in the top 30%.  

**High people**: top 30% housing-unit risk on this map.

**BpS / EVT_FIRE**: context only (not in this matrix).

---

## Factor columns

| Column | Meaning |
|--------|---------|
| plantation | Y = majority plantation EVT |
| peat | Y = majority peat / listed wetland |
| wfe_label | High (= High/VH), Mod (= Moderate), Low (= Low/VL) |
| mean_top30 | Y = hex MEAN in AOI top 30% |
| people | High / Low |
| pine | Y = on pine/barrens EVT list |
| Code now | What the cascade assigns today |
| Your call | **Fill this** — agree, or write a different action |
| notes | Optional |

---

## Matrix

| # | plantation | peat | wfe_label | mean_top30 | people | pine | Code now | Your call | notes |
|--:|:----------:|:----:|:---------:|:----------:|:------:|:----:|----------|-----------|-------|
| 1 | Y | * | * | * | * | * | protect_from_fire | | Always — timber asset |
| 2 | N | Y | * | * | * | * | wetlands_assess_locally | | Always — local peat call |
| 3 | N | N | High | * | High | * | treat_fire_risk_for_people | | Classic people × hot exposure |
| 4 | N | N | High | * | Low | * | ecosystem_health_focus | | Hot exposure, few homes |
| 5 | N | N | Mod | Y | High | * | treat_fire_risk_for_people | | Moderate label, score in top 30%, many homes |
| 6 | N | N | Mod | Y | Low | * | ecosystem_health_focus | | Moderate + elevated score, few homes |
| 7 | N | N | Mod | N | High | * | defer_monitor | | Rare in this AOI (almost all Mod are top 30%) |
| 8 | N | N | Mod | N | Low | * | defer_monitor | | Same |
| 9 | N | N | Low | Y | High | N | ecosystem_health_focus | | **Review:** quiet label, elevated score, many homes — code says ecosystem, **not** treat-for-people |
| 10 | N | N | Low | Y | Low | N | ecosystem_health_focus | | Quiet label, elevated score, few homes |
| 11 | N | N | Low | Y | High | Y | ecosystem_health_focus | | Same as #9; pine also true |
| 12 | N | N | Low | Y | Low | Y | ecosystem_health_focus | | Same as #10; pine also true |
| 13 | N | N | Low | N | High | N | defer_monitor | | Quiet label, score not elevated, many homes — homes alone do not treat |
| 14 | N | N | Low | N | Low | N | defer_monitor | | Typical quiet hex |
| 15 | N | N | Low | N | High | Y | ecosystem_health_focus | | Pine safety net (score not elevated) |
| 16 | N | N | Low | N | Low | Y | ecosystem_health_focus | | Pine safety net |

\* = any / ignored once an earlier row matches.

---

## Questions for you

1. Rows **9 / 11** (Low label + elevated score + **many homes**): keep **ecosystem**, change to **defer**, or something else? (Code will not use treat-for-people while the Low/VL veto stands.)  
2. Rows **15 / 16** (pine list only): keep as ecosystem safety net?  
3. Anything missing before we touch fuel-add?

Editable CSV copy: [`ACTION_MATRIX_REVIEW.csv`](ACTION_MATRIX_REVIEW.csv)
