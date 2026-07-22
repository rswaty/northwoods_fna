# EVT rules (v1) — peat and plantations only

| EVT role | Effect on ACTION_CLASS |
|----------|------------------------|
| Plantation | **always** `protect_from_fire` |
| Peat / wetland | `wetlands_assess_locally` (not a blanket defer — peat can be fire-dependent *and* is the hardest ground fire to control) |
| All other EVTs | Ignored |

**Peat source (v1):** LANDFIRE EVT is good enough for screening.  
**Later:** substitute **USFS peatlands** data for the same `PEAT_HEX` / defer rule—no cascade redesign; only the peat mask input changes.

Plantation silviculture needs are recorded as `TREATMENT_HINT`, not the action class.

PAD-US is **not** an EVT job and **not** an action picker — see `ACTION_ASSIGNMENT.md` (priority multiplier; ES layers may split out later).
