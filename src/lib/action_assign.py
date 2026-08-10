"""v1 action cascade + priority scoring helpers.

Actions (first match):
  - plantation → protect_from_fire
  - peat → wetlands_assess_locally
  - high WFE + high people → treat_fire_risk_for_people
  - high WFE + not-high people → ecosystem_health_focus
  - high fuel-add + high people → treat_fire_risk_for_people
  - high fuel-add + not-high people → ecosystem_health_focus
  - fire-adapted pine/barrens → ecosystem_health_focus
  - fire-dependent BpS (MFRI) → ecosystem_health_focus
  - else → defer_monitor

PAD is context only (not an action or score input). Developed EVT FIRE=-1 is
context; people risk comes from WRTC.

Default Goldilocks: people_first over ranked hexes only (defer and wetlands
assess-locally excluded from the priority bands; wetlands stay on the action map
and as a Goldilocks-map toggle overlay).
"""

from __future__ import annotations

# Excluded from Goldilocks 5/10/15% ranking (priority always 0).
# defer = no near-term treatment conversation; wetlands = assess locally but
# fire-adaptation is not classified, so they are not in the people-first queue.
NONACTIONABLE = {"defer_monitor"}
GOLDILOCKS_EXCLUDE = {"defer_monitor", "wetlands_assess_locally"}


def is_high_wfe(wfe: float, wfe_cat: str | None, wfe_p30: float) -> bool:
    """Return True if the hex has high wildfire exposure (WFE).

    Methods rule (AOI-relative):
      1. If WFE_CAT is High or Very High → high.
      2. If WFE_CAT is Low or Very Low → not high
         (category wins; homes nearby do not create fire risk).
      3. Otherwise (Moderate or missing category) → high if hex MEAN
         is in the top 30% of MEAN values across the analysis AOI
         (i.e. MEAN ≥ 70th percentile of hexes).

    ``wfe`` is the hex zonal mean of the WFE surface (field MEAN).
    ``wfe_p30`` is that 70th-percentile cutoff computed in script 04.
    """
    if wfe_cat:
        cat = str(wfe_cat).strip().lower()
        if cat in {"high", "very high", "very_high", "vh", "h"}:
            return True
        if cat in {"low", "very low", "very_low", "l", "vl"}:
            return False
    return wfe >= wfe_p30


def is_high_wrtc(homes: float, homes_p30: float) -> bool:
    """Return True if the hex has high people / community wildfire risk.

    High = top 30% of WRTC Housing Unit Risk among hexes in the AOI
    (WRTC_HU_RISK_MEAN ≥ 70th percentile). Independent of WFE.
    """
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
    fire_dependent: bool = False,
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
    # Low/mid WFE: fuel-add, pine list, then BpS fire-dependent still get actions.
    if high_fuel:
        if high_homes:
            return "treat_fire_risk_for_people"
        return "ecosystem_health_focus"
    if pine_barrens:
        return "ecosystem_health_focus"
    if fire_dependent:
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
