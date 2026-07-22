# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%/15%, actionable hexes only).  
**PAD:** GAP 1–3 multiplier only. **Recreation:** deferred. **Resilient lands:** optional later.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT plantation | Yes | → **always** `protect_from_fire` (economic asset) |
| EVT peat | Yes | → `wetlands_assess_locally` (fire-dependent *and* ground-fire hazard; screening can't decide) |
| WFE | Yes | High WFE is the treatment trigger; **people** split it (below) |
| WRTC **Housing Unit Risk** | Yes | "High people" routes a high-WFE hex to the people action |
| **BpS / MFRI (`FIRE_DEP_HEX`)** | **No** | **Context/validation only.** WFE already encodes fire-behavior/return-interval, so high WFE ⇒ fire-dependent; used to check that premise, not to gate. |
| **PAD-US GAP 1–3** | **No** | **Multiplier on priority only**. Status 4 excluded. |
| Disturbances | Later | Calibrate when toggle on |

**Treatment hints** (`TREATMENT_HINT`) say *how* to act, not a separate action class:

| Situation | Hint |
|-----------|------|
| Plantation, low WFE | `silvicultural_treatment` |
| Plantation, high WFE | `silviculture_then_fire` |
| `treat_fire_risk_for_people` | `fuels_reduction_home_hardening` — mechanical fuels reduction + home hardening / defensible-space inspections (near homes + fire-excluded → not beneficial fire) |

## Action cascade (first match wins)

1. **Plantation** → `protect_from_fire` (always; economic asset)
2. **Peat** → `wetlands_assess_locally`
3. **High WFE + high people** → `treat_fire_risk_for_people`
4. **High WFE + not-high people** → `ecosystem_health_focus`
5. **Else** → `defer_monitor`

Notes:
- **No "high WFE but not fire-dependent" case.** WFE is built from fire behavior / return interval, so high WFE means fire-carrying, fire-adapted fuels. BpS/MFRI is folded in only as context and to validate this (script 04 prints how many high-WFE hexes come back long-interval; expect ~0).
- **People-first:** a high-WFE hex that is *both* near people and on PAD goes to `treat_fire_risk_for_people`; PAD then just raises its priority score.
- **High people but low WFE → `defer_monitor`** (no hazard, no fuels work). Peat no longer blanket-defers — high stakes on those hexes still surface via the priority ranking.

PAD never appears in this list. People + high WFE **outside** PAD still get treated and score high.

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

Ranking is over **actionable hexes only** — `defer_monitor` is excluded, so a "don't act" hex can never be flagged Goldilocks. Percentages are of the actionable pool.

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
