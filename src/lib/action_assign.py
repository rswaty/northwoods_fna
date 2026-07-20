"""v1 action cascade + priority scoring helpers.

Actions: peat / plantation / WRTC HU Risk / WFE (PAD is not an action input).
Default Goldilocks ranking: people_first.
PAD GAP 1–3 is a priority multiplier only.
"""

from __future__ import annotations


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

    if peat:
        return "defer_monitor"
    # Plantations are always an asset to protect from wildfire (not a silviculture action class).
    if plantation:
        return "protect_from_wildfire"
    if high_homes:
        return "protect_from_wildfire"
    if high_wfe:
        return "restore_beneficial_fire"
    return "defer_monitor"


def plantation_treatment_hint(
    *,
    plantation: bool,
    wfe: float,
    wfe_cat: str | None,
    wfe_p30: float,
) -> str:
    """How you might protect a plantation — secondary to ACTION_CLASS=protect."""
    if not plantation:
        return ""
    if is_high_wfe(wfe, wfe_cat, wfe_p30):
        return "silviculture_then_fire"
    return "silvicultural_treatment"


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
