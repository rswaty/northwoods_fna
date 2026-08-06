"""v1 action cascade + priority scoring helpers.

Actions (first match):
  - plantation → protect_from_fire
  - peat → wetlands_assess_locally
  - high WFE + high people → treat_fire_risk_for_people
  - high WFE + not-high people → ecosystem_health_focus
  - high fuel-add + high people → treat_fire_risk_for_people
  - high fuel-add + not-high people → ecosystem_health_focus
  - fire-adapted pine/barrens → ecosystem_health_focus
  - else → defer_monitor

PAD is context only (not an action or score input). Developed EVT FIRE=-1 is
context; people risk comes from WRTC.

Default Goldilocks: people_first over ACTIONABLE hexes only (defer excluded).
"""

from __future__ import annotations

# Actions treated as "do nothing now" — excluded from Goldilocks ranking.
NONACTIONABLE = {"defer_monitor"}


def is_high_wfe(wfe: float, wfe_cat: str | None, wfe_p30: float) -> bool:
    """High WFE = top ~30% of hex MEAN (same idea as high people / WRTC).

    WFE_CAT High / Very High still counts as high. Low / Moderate / Very Low do
    **not** veto the percentile — otherwise AOI-hot N WI hexes labeled Moderate
    or Low stayed on defer_monitor.
    """
    if wfe_cat:
        cat = str(wfe_cat).strip().lower()
        if cat in {"high", "very high", "very_high", "vh", "h"}:
            return True
    return wfe >= wfe_p30


def is_high_wrtc(homes: float, homes_p30: float) -> bool:
    """High people = top ~30% of WRTC Housing Unit Risk on hexes."""
    return homes >= homes_p30


def is_high_fuel_add(fdist_delta: float, fuel_add_min: float) -> bool:
    """Area-weighted FDist fuel direction; positive = net fuel add."""
    return fdist_delta >= fuel_add_min


def assign_action_v1(
    *,
    peat: bool,
    plantation: bool,
    wfe: float,
    wfe_cat: str | None,
    homes: float,
    wfe_p30: float,
    homes_p30: float,
    fdist_delta: float = 0.0,
    fuel_add_min: float = 0.25,
    pine_barrens: bool = False,
) -> str:
    """First-match cascade. PAD is not an input. See config/ACTION_ASSIGNMENT.md."""
    high_wfe = is_high_wfe(wfe, wfe_cat, wfe_p30)
    high_homes = is_high_wrtc(homes, homes_p30)
    high_fuel = is_high_fuel_add(fdist_delta, fuel_add_min)

    if plantation:
        return "protect_from_fire"
    if peat:
        return "wetlands_assess_locally"
    if high_wfe:
        if high_homes:
            return "treat_fire_risk_for_people"
        return "ecosystem_health_focus"
    # Low/mid WFE: recent fuel-add and fire-adapted pines still get actions.
    if high_fuel:
        if high_homes:
            return "treat_fire_risk_for_people"
        return "ecosystem_health_focus"
    if pine_barrens:
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
    """How to carry out the action — secondary to ACTION_CLASS."""
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
    fuel_add: float = 0.0,
    w_homes: float,
    w_plantations: float,
    w_wfe: float,
    w_fuel_add: float = 0.0,
) -> float:
    """People / plantation / WFE / fuel-add urgency. PAD is not used (context only)."""
    fuel = max(0.0, fuel_add)
    return (
        w_homes * homes
        + w_plantations * plantation
        + w_wfe * wfe
        + w_fuel_add * fuel
    )


def percentile_threshold(values: list[float], pct: float = 0.70) -> float:
    """Value at percentile (0.70 ≈ top 30% cutoff)."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return 0.0
    idx = min(len(vals) - 1, max(0, int(len(vals) * pct)))
    return vals[idx]
