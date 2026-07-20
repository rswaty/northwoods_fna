# v1 action assignment

## Roles of each input

| Input | Picks **action class**? | Role |
|-------|-------------------------|------|
| EVT peat | Yes | → `defer_monitor` |
| EVT plantation | Yes | → **always** `protect_from_wildfire` (economic asset) |
| WRTC (homes) | Yes | → `protect_from_wildfire` |
| WFE | Yes | High → `restore_beneficial_fire` (if not peat / already protect) |
| **PAD-US** | **No** | **Multiplier on priority score only** (management feasibility + high biodiversity/recreation value) |
| Disturbances | Later | Calibrate when toggle on |

Plantations may also get a **treatment hint** (silviculture / silviculture-then-fire) = *how* you protect the asset — not a separate action class in v1.

## Action cascade (first match wins)

1. **Peat** → `defer_monitor`
2. **Plantation** → `protect_from_wildfire` (always)
3. **High WRTC** → `protect_from_wildfire`
4. **High WFE** → `restore_beneficial_fire`
5. **Else** → `defer_monitor`

PAD never appears in this list. People + high WFE **outside** PAD still get protect / fire / high base scores.

## Priority score (Goldilocks)

```text
base   = w_homes×WRTC + w_plantations×plantation_flag + w_wfe×WFE
score  = base × (1 + w_pad_multiplier × PADUS_FRAC)
```

- Outside PAD (`PADUS_FRAC ≈ 0`): multiplier = 1.0 — homes×WFE still rank high.
- Inside PAD: score is boosted (easier management context + conservation/recreation value).
- Preset `biodiversity_recreation_first` uses a larger `w_pad_multiplier`.

### PAD categories (think-through; refine later)

v1 uses **any PAD overlap fraction** as the multiplier. Later, differentiate by PAD attributes:

| PAD flavor | Why it matters | Suggested later weight |
|------------|----------------|------------------------|
| Fee / federal / state / county | Higher ops feasibility (not small private) | Stronger multiplier |
| Easement / private conserved | High value, variable access/ops | Medium |
| Local parks / recreation | Value + some ops | Medium |
| Unknown / other | Weak signal | Low |

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
