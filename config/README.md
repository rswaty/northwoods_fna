# Config index

| File | Role |
|------|------|
| `paths.example.yaml` | Copy → `paths.local.yaml` (gitignored) for Pro paths |
| `weight_presets.csv` | Score weights (people_first default) |
| `action_classes.csv` | Action labels / short descriptions |
| `action_triggers_review.md` | Cascade + thresholds (partner-facing) |
| `ACTION_ASSIGNMENT.md` | Design write-up for the cascade |
| `ACTION_MATRIX.md` / `ACTION_MATRIX_DRAFT.csv` | Optional factor×action worksheet |
| `evt_rules_draft.csv` | Peat / plantation EVT codes |
| `evt_pine_barrens.csv` | Pine/barrens EVT → ecosystem path |
| `EVT_RULES_LOGIC.md` | How EVT flags are meant to work |
| `WRTC_DATASETS.md` | Which WRTC layers we use |
| `PADUS_AND_RESILIENT.md` | PAD context (not score) |
| `values_to_protect.csv` | Value list (plantations, etc.) |
| `next_steps_partner_notes.md` | Longer partner / next-step notes |
| `week_action_plan.md` | Near-term checklist |

Pipeline code lives in `src/`; scored hexes in `outputs/hex/`.
