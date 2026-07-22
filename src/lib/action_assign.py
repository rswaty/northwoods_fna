"""v1 action cascade + priority scoring helpers.

Actions (first match): plantation / peat / high WFE (split by people).
  - plantation → protect_from_fire (economic asset)
  - peat → wetlands_assess_locally (fire-dependent AND the hardest ground fire to
    control; screening can't decide, so flag for local assessment)
  - high WFE + high people → treat_fire_risk_for_people
  - high WFE + not-high people → ecosystem_health_focus
  - else → defer_monitor

WFE is built from fire-behavior / return-interval inputs, so high WFE already
implies fire-carrying, fire-dependent fuels — there is no "high WFE but not
fire-dependent" case. BpS/MFRI is folded in as context only (it does not gate
actions; it lets us validate that premise per hex via FIRE_DEP_HEX).

Default Goldilocks ranking: people_first, over ACTIONABLE hexes only
(defer_monitor excluded). PAD GAP 1–3 is a priority multiplier only.
"""

from __future__ import annotations

# Actions treated as "do nothing now" — excluded from Goldilocks ranking.
NONACTIONABLE = {"defer_monitor"}


def is_high_wfe(wfe: float, wfe_cat: str | None, wfe_p30: float) -> bool:
    if wfe_cat:
        cat = str(wfe_cat).strip().lower()
        if cat in {"high", "very high", "very_high", "vh", "h"}:
            return True
        if cat in {"low", "very low", "moderate", "medium", "l", "m"}:
            return False
    return wfe >= wfe_p30


def is_high_wrtc(homes: float, homes_p30: float) -> bool:
    return homes >= homes_p30


def assign_action_v1(
    *,
    peat: bool,
    plantation: bool,
    wfe: float,
    wfe_cat: str | None,
    homes: float,
    wfe_p30: float,
    homes_p30: float,
) -> str:
    """First-match cascade. PAD is not an input. See config/ACTION_ASSIGNMENT.md."""
    high_wfe = is_high_wfe(wfe, wfe_cat, wfe_p30)
    high_homes = is_high_wrtc(homes, homes_p30)

    # Plantations are always an asset to protect from wildfire.
    if plantation:
        return "protect_from_fire"
    # Peat/wetlands: don't silently defer — needs local judgement.
    if peat:
        return "wetlands_assess_locally"
    # High WFE is the only treatment trigger; people-first split.
    if high_wfe:
        if high_homes:
            return "treat_fire_risk_for_people"
        return "ecosystem_health_focus"
    return "defer_monitor"


def treatment_hint(
    *,
    action: str,
    plantation: bool,
    wfe: float,
    wfe_cat: str | None,
    wfe_p30: float,
) -> str:
    """How to carry out the action — secondary to ACTION_CLASS.

    - Plantation protect: silviculture (then fire if hot).
    - treat_fire_risk_for_people: near homes and fire-excluded, so mechanical
      fuels reduction plus home hardening / defensible-space inspections — not
      beneficial fire.
    """
    if plantation:
        return "silviculture_then_fire" if is_high_wfe(wfe, wfe_cat, wfe_p30) else "silvicultural_treatment"
    if action == "treat_fire_risk_for_people":
        return "fuels_reduction_home_hardening"
    return ""


def priority_score(
    *,
    homes: float,
    plantation: float,
    wfe: float,
    pad_frac: float,
    w_homes: float,
    w_plantations: float,
    w_wfe: float,
    w_pad_multiplier: float,
) -> float:
    """Base urgency × PAD multiplier (feasibility + conservation/multiple-use mandate).

    High WRTC × high WFE outside PAD still scores from the base terms.
    PAD only boosts; it never zeroes out a hex.
    """
    base = w_homes * homes + w_plantations * plantation + w_wfe * wfe
    # pad_frac in [0, 1] → multiplier in [1.0, 1.0 + w_pad_multiplier]
    mult = 1.0 + w_pad_multiplier * max(0.0, min(1.0, pad_frac))
    return base * mult


def percentile_threshold(values: list[float], pct: float = 0.70) -> float:
    """Value at percentile (0.70 ≈ top 30% cutoff)."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return 0.0
    idx = min(len(vals) - 1, max(0, int(len(vals) * pct)))
    return vals[idx]
