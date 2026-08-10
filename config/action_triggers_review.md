# Action triggers review (FAA cascade)

Partner/review notes for how hexes get an `ACTION_CLASS`. First matching rule wins.

## High WFE and high people (methods)

Cutoffs are AOI-relative (script 04).

| Term | Definition |
|------|------------|
| **High people** | Top **30%** of hexes by WRTC Housing Unit Risk (`WRTC_HU_RISK_MEAN` ≥ 70th percentile). |
| **High WFE** | (1) `WFE_CAT` High or Very High → high; (2) `WFE_CAT` Low or Very Low → **not** high; (3) else (Moderate / missing) → high if hex `MEAN` is in the top **30%** of AOI `MEAN` values. |
| **`MEAN`** | Hex zonal mean of the continuous wildfire-exposure (WFE) surface. |
| Design intent | **Homes alone never imply treat-for-people.** Low/Very Low WFE → defer on the WFE×people path even if people are high. |

| Order | Action | Trigger (summary) | Threshold / notes | Example |
|------:|--------|-------------------|-------------------|---------|
| 1 | `protect_from_fire` — Protect from fire | Plantation EVT majority | `EVT_MAJORITY` in plantation codes (`config/evt_rules_draft.csv`; currently 9312). FDist/WFE/people ignored once matched. | Managed pine plantation (even with insect fuel-add) → protect |
| 2 | `wetlands_assess_locally` — Wetlands assess locally | Peat/wetland EVT majority | Peat codes in `evt_rules_draft.csv`. | Large acidic fen/peat majority → wetlands assess |
| 3 | `treat_fire_risk_for_people` — Treat fire risk for people | High WFE **and** high people | High WFE and high people as in the table above. Not plantation/peat. | Hot jack pine next to lake homes → treat for people |
| 4 | `ecosystem_health_focus` — Ecosystem health focus | High WFE **and not** high people | Same high-WFE rule as row 3. | Hot continuous pine far from housing → ecosystem |
| 5 | `treat_fire_risk_for_people` | High fuel-add **and** high people (WFE not already high) | `FDIST_FUEL_DELTA` ≥ `fdist_fuel_add_min` (default 0.25) and high people. Primary FDist→people path. | Low WFE + ice storm / insect mortality near homes → treat for people |
| 6 | `ecosystem_health_focus` | High fuel-add **and not** high people | Same FDist threshold; WFE not high. | Remote insect/windthrow fuel-add → ecosystem |
| 7 | `ecosystem_health_focus` | Pine/barrens EVT list | `EVT_MAJORITY` in `config/evt_pine_barrens.csv` if not caught above. | Red pine majority, low WFE, quiet FDist → ecosystem |
| 8 | `defer_monitor` — Defer / monitor | Nothing above matched | Excluded from Goldilocks (`GOLDILOCKS_PRIORITY` always 0), as is `wetlands_assess_locally`. | Northern hardwoods, low WFE, FDist 0.1 → defer |

## Context only (not action triggers)

| Field | Role |
|-------|------|
| `PADUS_FRAC` | Map/Leaflet context only — not an action trigger and not in `SCORE_PEOPLE`. |
| `EVT_FIRE` (−1/0/1) | Popup/context. Developed (−1) does not auto-protect; people come from WRTC. FIRE=1 alone does not assign ecosystem. |
| `FIRE_DEP_HEX` | BpS/MFRI fire-dependent flag → `ecosystem_health_focus` if no earlier cascade rule matched. |
| `FDIST_FUEL_DELTA` below 0.25 | Mild/negative fuel change does not trigger action by itself. |

## Goldilocks (priority, not a separate action)

| Field | Role |
|-------|------|
| `GOLDILOCKS_PRIORITY` | 3 = top 5%, 2 = top 10%, 1 = top 15%, 0 = rest; ranked by `SCORE_PEOPLE` among hexes that are **not** `defer_monitor` and **not** `wetlands_assess_locally`. Defers and wetlands always priority 0 (wetlands stay on the action map and as a Goldilocks-map toggle). |
| `SCORE_PEOPLE` | People-first score for Goldilocks (`config/weight_presets.csv`). PAD weight = 0. |

Code source of truth: `src/lib/action_assign.py` (run via `src/04_score_actions.py`).
