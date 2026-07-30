# FAA — next week action plan

Short plan based on current repo state, partner notes, and open design. Detail lives in `config/next_steps_partner_notes.md` and `faa_overview.qmd`.

## Where we are (30 seconds)

**Built and runnable in Pro:** path check → WRTC zonal → EVT/PAD/(BpS) zonal → score/actions → hex export. Cascade is plantation → peat/wetlands → high WFE×people vs ecosystem → defer. Goldilocks = people-first over actionable hexes (peat included). PAD is a score multiplier (partners already doubt that).

**Documented, not coded yet:** FDist fuel-add/remove (−1/0/+1, 10 yr); fire-adapted via EVT+MFRI; action matrix (mostly blank); mills/stations/seasonal risk/ignitions as companions; protections vocabulary; value-near-risk; better plantations.

**Partner-facing:** `faa_overview.qmd` (plain-language overview). Pitch: strategic “what to do where” for conversation — not prescriptions.

---

## Next week — do these (in order)

### 1. Close the loop on what you already ran
- [ ] Confirm Pro has latest `git pull` (action names, Goldilocks, BpS path in `paths.local.yaml`, FRI max **100**).
- [ ] If not already: **03 → 04 → 05**; skim action counts + premise check; push hex GeoJSON if it looks sane.
- [ ] Commit/push local docs still sitting out (`faa_overview.*`, `next_steps_partner_notes.md`) when ready.

### 2. One partner meeting (highest leverage)
- [ ] **Meet Krystina Hird** — 30–45 min: FAA pitch + **mill locations** + what she trusts for **timber value / plantations**.
- [ ] Capture afterward: data sources, haul-distance rule of thumb, score vs hint only (notes file §5).

### 3. Finish the two tables that unlock the next model bump
- [ ] **Fill `config/ACTION_MATRIX_DRAFT.csv`** at least for: plantation, peat, high WFE splits, and the **KEY** low-WFE + fuel-add rows. Collapse Med→Low/High if three levels feel like too much.
- [ ] **FDist lookup CSV** (−1 / 0 / +1) from your LANDFIRE FDist attributes, **last 10 years** — even a draft. (Repo already has an fdist-related commit; align that file with the −1/0/+1 design.)

### 4. One design decision (don’t code all of it yet)
- [ ] **PAD in scoring:** keep multiplier, or context-only? Write the decision in the notes file so scoring changes wait on purpose.
- [ ] Optional same day: agree “high-value near high-risk” = **map flag first**, not a new action (notes §7).

### 5. Light companion work (only if 1–4 are moving)
- [ ] Start **station** layer hunt (VFD / DNR / USFS) — map bookmark list, not hex join.
- [ ] Scope **recent.html** refresh (Short past 2020) as a separate northwoods-repo task — don’t block FAA.

---

## Explicitly park until later

| Park | Why |
|------|-----|
| Satellite plantation ML | Ask for industry GIS first |
| LandScan, ignitions in cascade | Secondary; document only |
| Seasonal ERC inside Goldilocks | Ops companion, not FAA score |
| Wiring FDist/MFRI into code | After matrix + FDist CSV are filled |
| Nested hexes / full biodiversity | Phase later |

---

## Success check Friday

You’re in good shape if:

1. Hird meeting happened (or firmly scheduled) with mill/timber notes written down.  
2. Action matrix has real actions on the critical rows.  
3. Draft FDist −1/0/+1 table exists.  
4. PAD decision recorded.  
5. Latest hex export (or a clear “blocked on X”) matches the current cascade story.

Then the following week is mostly **implement FDist + matrix rules + optional de-PAD score** — not more brainstorming.
