# Action decision matrix (draft)

Fill **`ACTION_CLASS`** / **`TREATMENT_HINT`** in [`ACTION_MATRIX_DRAFT.csv`](ACTION_MATRIX_DRAFT.csv) (Excel-friendly). Rows are situations; columns are input factors.

## Factor bins (proposed)

| Factor | Low | Med | High |
|--------|-----|-----|------|
| **WFE** | Below top-30% (not cat-high) | Mid (optional; today’s code is only high vs not) | Top 30% or `WFE_CAT` high |
| **PEOPLE** (WRTC HU Risk) | Below top-30% | Mid (optional) | Top 30% |
| **FDIST_FUEL** (last **10** yr, area-weighted −1/0/+1) | Fuel **remove** (δ ≲ −0.25) | Neutral (\|δ\| < 0.25) | Fuel **add** (δ ≳ +0.25) |
| **PAD** (GAP 1–3 frac) | < 0.33 | 0.33–0.67 | > 0.67 — *score only today* |
| **PEAT** / **PLANTATION** | — | — | Use **Y/N** (first two matrix rows) |
| **FIRE_DEP** | FRI > 100 | — | FRI ≤ 100 — *context only* |

## How to use

1. Open the CSV; fill `ACTION_CLASS` (and optional hint/notes).
2. Rows marked **KEY** are the low-WFE + fuel-add cases (MI ice/wind, Arrowhead insects).
3. Plantation / peat rows are overrides (`*` = other factors ignored).
4. If **Med** is too fine, collapse Med→Low or Med→High in your fills and we will match code to that.

FDist code→(−1/0/+1) CSV still to come from you.
