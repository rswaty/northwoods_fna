# EVT rules (v1) — peat and plantations only

| EVT role | Effect on ACTION_CLASS |
|----------|------------------------|
| Peat / wetland | `defer_monitor` |
| Plantation | **always** `protect_from_wildfire` |
| All other EVTs | Ignored |

**Peat source (v1):** LANDFIRE EVT is good enough for screening.  
**Later:** substitute **USFS peatlands** data for the same `PEAT_HEX` / defer rule—no cascade redesign; only the peat mask input changes.

Plantation silviculture needs are recorded as `TREATMENT_HINT`, not the action class.

PAD-US is **not** an EVT job and **not** an action picker — see `ACTION_ASSIGNMENT.md` (priority multiplier; ES layers may split out later).
