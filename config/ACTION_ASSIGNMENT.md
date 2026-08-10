# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%/15%, actionable hexes only).  
**PAD:** map **context only** (`PADUS_FRAC`). **Recreation:** deferred. **Resilient lands:** optional later.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT plantation | Yes | → **always** `protect_from_fire` (economic asset) |
| EVT peat | Yes | → `wetlands_assess_locally` |
| WFE | Yes | High WFE → people vs ecosystem split |
| WRTC **Housing Unit Risk** | Yes | "High people" routes WFE / fuel-add hexes to the people action |
| FDist `FDIST_FUEL_DELTA` | Yes | High fuel-add (≈ mean ≥ 0.25) → people vs ecosystem even if WFE low |
| EVT pine/barrens list | Yes | Fire-adapted pines away from people → `ecosystem_health_focus` (even if WFE low) |
| **BpS / MFRI (`FIRE_DEP_HEX`)** | Yes | Historic fire-dependent vegetation (short MFRI) → `ecosystem_health_focus` when earlier rules did not already assign an action |
| EVT `FIRE` (−1/0/1) | Context | Popup / review; developed −1 does **not** auto-protect (WRTC handles people) |
| **PAD-US GAP 1–3** | **No** | **Map context only** — not score, not action |

**Treatment hints** (`TREATMENT_HINT`) say *how* to act, not a separate action class:

| Situation | Hint |
|-----------|------|
| Plantation, low WFE | `silvicultural_treatment` |
| Plantation, high WFE | `silviculture_then_fire` |
| `treat_fire_risk_for_people` | `fuels_reduction_home_hardening` |

## Action cascade (first match wins)

1. **Plantation** → `protect_from_fire`
2. **Peat** → `wetlands_assess_locally`
3. **High WFE + high people** → `treat_fire_risk_for_people`
4. **High WFE + not-high people** → `ecosystem_health_focus`
5. **High fuel-add + high people** → `treat_fire_risk_for_people`
6. **High fuel-add + not-high people** → `ecosystem_health_focus`
7. **Pine/barrens (config list)** → `ecosystem_health_focus`
8. **BpS fire-dependent (`FIRE_DEP_HEX=1`)** → `ecosystem_health_focus`
9. **Else** → `defer_monitor`

Notes:
- Fuel-add, pine/barrens, and BpS fire-dependence catch places where today’s WFE is soft but fire still belongs in the conversation.
- Pine/barrens and fire-dep get ecosystem even near people if WFE and fuel-add are not already high (those cases still take the people action first).
- Developed EVT `FIRE=−1` is context; do not auto-protect — people come from WRTC.
- PAD never appears in this list or in `SCORE_PEOPLE`.

## Priority score (Goldilocks)

### PAD-US (GAP Status 1–3 only)

Hex field `PADUS_FRAC` = overlap with PAD features where GAP Status ∈ {1, 2, 3}. Status 4 excluded.

| Role | Detail |
|------|--------|
| Action class? | **No** |
| Priority? | **Yes** — multiplier for management feasibility + conservation/multiple-use mandate |

```text
base   = w_homes×WRTC_HU_Risk + w_plantations×plantation_flag + w_wfe×WFE
score  = base × (1 + w_pad_multiplier × PADUS_FRAC)
```

### Goldilocks bands + priority (people-first)

Ranking is over hexes that are **not** `defer_monitor` and **not** `wetlands_assess_locally`. Wetlands keep their assess-locally action but are not in the people-first 5/10/15% bands (dashboard: optional Goldilocks overlay). Percentages are of that ranked pool across the full AOI.

| Field | Meaning |
|-------|---------|
| `GOLDILOCKS_5` / `_10` / `_15` | Top 5% / 10% / 15% by `SCORE_PEOPLE` (cumulative, nested) |
| `GOLDILOCKS_PRIORITY` | 0–3 ordinal: **3** = top 5% (protect ASAP — high housing + high WFE), **2** = top 10%, **1** = top 15%, **0** = rest (all defers = 0) |

Presets (`config/weight_presets.csv`):

| preset_id | Role |
|-----------|------|
| `people_first` | **Default Goldilocks** |
| `plantation_asset_first` | Boost plantations |
| `pad_first` | Strong PAD GAP 1–3 boost (not a biodiversity model) |
| `balanced` | Even mix |

**TNC Resilient Lands** (optional later) add climate resilience, connectivity, and nature value *off* the protected estate—see `PADUS_AND_RESILIENT.md`. Do not treat PAD 1–3 as a full biodiversity model.

Do **not** require PAD for Protect — WUI and plantations often sit outside PAD.

## Examples

H/L = high/low within AOI; Y/N = flag. PAD = overlap fraction.

### Plantations always protect
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS | Treatment hint |
|-----|------|-----|------|------------|----------------|----------------|
| H | L | 0 | N | Y | **protect_from_fire** | silviculture_then_fire |
| L | L | 0.8 | N | Y | **protect_from_fire** | silvicultural_treatment |
| H | H | 0 | N | Y | **protect_from_fire** | silviculture_then_fire |

### High WFE near people
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS | Priority note |
|-----|------|-----|------|------------|----------------|---------------|
| H | H | **0** | N | N | **treat_fire_risk_for_people** | High base score; no PAD boost |
| H | H | **0.7** | N | N | **treat_fire_risk_for_people** | People-first; PAD only **raises** the score |

### High WFE away from people (ecosystem)
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS |
|-----|------|-----|------|------------|----------------|
| H | L | 0 | N | N | **ecosystem_health_focus** |
| H | L | 0.9 | N | N | **ecosystem_health_focus** (higher priority score via PAD) |

### High people, low WFE
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS |
|-----|------|-----|------|------------|----------------|
| L | H | 0 | N | N | **defer_monitor** (no hazard → no fuels work) |

### Peat / quiet
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS | Note |
|-----|------|-----|------|------------|----------------|------|
| H | H | 0.9 | Y | N | **wetlands_assess_locally** | Still high `SCORE_PEOPLE` → can be Goldilocks priority 3 |
| H | L | 0.9 | Y | N | **wetlands_assess_locally** | Local call on a fire-prone peatland |
| L | L | 0.9 | N | N | **defer_monitor** | PAD alone does not create an action; priority 0 |

## Treatment hints, not action classes

`silvicultural_treatment`, `silviculture_then_fire`, and `fuels_reduction_home_hardening` are **`TREATMENT_HINT`s**, not primary `ACTION_CLASS`. Broader EVT/BpS-based ecosystem rules return when partners want finer logic.
