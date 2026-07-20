# v1 action assignment

**Default ranking:** people-first (`SCORE_PEOPLE` → Goldilocks 5%/10%).  
**PAD:** GAP 1–3 multiplier only. **Recreation:** deferred. **Resilient lands:** optional later.

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT peat | Yes | → `defer_monitor` (LANDFIRE now; USFS peat later) |
| EVT plantation | Yes | → **always** `protect_from_wildfire` (economic asset) |
| WRTC **Housing Unit Risk** | Yes | → `protect_from_wildfire` when high |
| WFE | Yes | High → `restore_beneficial_fire` (if not peat / already protect) |
| **PAD-US GAP 1–3** | **No** | **Multiplier on priority only**. Status 4 excluded. |
| Disturbances | Later | Calibrate when toggle on |

Plantations may also get a **treatment hint** (silviculture / silviculture-then-fire) = *how* you protect the asset — not a separate action class in v1.

## Action cascade (first match wins)

1. **Peat** → `defer_monitor`
2. **Plantation** → `protect_from_wildfire` (always)
3. **High WRTC Housing Unit Risk** → `protect_from_wildfire`
4. **High WFE** → `restore_beneficial_fire`
5. **Else** → `defer_monitor`

PAD never appears in this list. People + high WFE **outside** PAD still get protect / fire / high base scores.

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
| H | L | 0 | N | Y | **protect_from_wildfire** | silviculture_then_fire |
| L | L | 0.8 | N | Y | **protect_from_wildfire** | silvicultural_treatment |
| H | H | 0 | N | Y | **protect_from_wildfire** | silviculture_then_fire |

### People + WFE outside PAD (still act)
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS | Priority note |
|-----|------|-----|------|------------|----------------|---------------|
| H | H | **0** | N | N | **protect_from_wildfire** | High base score; no PAD boost |
| H | H | **0.7** | N | N | **protect_from_wildfire** | Same action; **higher** score via PAD multiplier |

### Fire need without people
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS |
|-----|------|-----|------|------------|----------------|
| H | L | 0 | N | N | **restore_beneficial_fire** |
| H | L | 0.9 | N | N | **restore_beneficial_fire** (higher priority score) |

### Peat / quiet
| WFE | WRTC | PAD | Peat | Plantation | → ACTION_CLASS |
|-----|------|-----|------|------------|----------------|
| H | H | 0.9 | Y | N | **defer_monitor** |
| L | L | 0.9 | N | N | **defer_monitor** (PAD alone does not create an action) |

## Silviculture action classes in v1

`silvicultural_treatment` and `silviculture_then_fire` are **hints on plantations**, not primary ACTION_CLASS. Broader EVT-based silviculture returns when partners want finer ecosystem rules.
