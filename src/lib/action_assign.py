"""v1 action cascade + priority scoring helpers.

Actions (first match):
  - plantation → protect_from_fire
  - peat → wetlands_assess_locally
  - strict high WFE + high people → treat_fire_risk_for_people
  - elevated WFE for ecosystem (see below) → ecosystem_health_focus
  - high fuel-add + high people → treat_fire_risk_for_people
  - high fuel-add + not-high people → ecosystem_health_focus
  - fire-adapted pine/barrens EVT list → ecosystem_health_focus
  - else → defer_monitor

Strict high WFE (people path):
  High/VH category, or Moderate/missing with MEAN in AOI top 30%.
  Low/VL category never counts — homes alone do not create treat-for-people.

Elevated WFE for ecosystem:
  Strict high WFE, OR Low/VL category with MEAN still in AOI top 30%.
  So a quiet label can still open an ecosystem conversation if continuous
  exposure is relatively high; it cannot open treat-for-people.

BpS / FIRE_DEP_HEX and EVT_FIRE are context only (not cascade inputs).
PAD is context only.

Default Goldilocks: people_first over ranked hexes AOI-wide (defer and wetlands
assess-locally excluded; wetlands stay on the action map / overlay).
"""

from __future__ import annotations

NONACTIONABLE = {"defer_monitor"}
GOLDILOCKS_EXCLUDE = {"defer_monitor", "wetlands_assess_locally"}


def is_high_wfe(wfe: float, wfe_cat: str | None, wfe_p30: float) -> bool:
    """Strict high WFE — used for treat-for-people (and as part of ecosystem).

    1. WFE_CAT High or Very High → high.
    2. WFE_CAT Low or Very Low → not high (category veto).
    3. Moderate or missing → high if MEAN ≥ AOI 70th percentile (top 30%).
    """
    if wfe_cat:
        cat = str(wfe_cat).strip().lower()
        if cat in {"high", "very high", "very_high", "vh", "h"}:
            return True
        if cat in {"low", "very low", "very_low", "l", "vl"}:
            return False
    return wfe >= wfe_p30


def is_elevated_wfe_for_ecosystem(
    wfe: float, wfe_cat: str | None, wfe_p30: float
) -> bool:
    """Exposure high enough to discuss ecosystem fire.

    True if strict high WFE, or Low/VL with MEAN still in the AOI top 30%.
    """
    if is_high_wfe(wfe, wfe_cat, wfe_p30):
        return True
    if wfe_cat:
        cat = str(wfe_cat).strip().lower()
        if cat in {"low", "very low", "very_low", "l", "vl"}:
            return wfe >= wfe_p30
    return False


def is_high_wrtc(homes: float, homes_p30: float) -> bool:
    """High people = top 30% WRTC Housing Unit Risk in the AOI."""
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
    fire_dependent: bool = False,  # unused; BpS is context only
) -> str:
    """First-match cascade. PAD / BpS / EVT_FIRE are not inputs."""
    del fire_dependent  # context only — kept in signature so 04 callers stay stable
    high_wfe = is_high_wfe(wfe, wfe_cat, wfe_p30)
    eco_wfe = is_elevated_wfe_for_ecosystem(wfe, wfe_cat, wfe_p30)
    high_homes = is_high_wrtc(homes, homes_p30)
    high_fuel = is_high_fuel_add(fdist_delta, fuel_add_min)

    if plantation:
        return "protect_from_fire"
    if peat:
        return "wetlands_assess_locally"
    # People treatment requires strict high WFE (Low/VL veto).
    if high_wfe and high_homes:
        return "treat_fire_risk_for_people"
    # Ecosystem: strict high WFE, or Low/VL with elevated MEAN.
    if eco_wfe:
        return "ecosystem_health_focus"
    # Fuel-add bypass when WFE is not elevated for ecosystem either.
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
        return (
            "silviculture_then_fire"
            if is_high_wfe(wfe, wfe_cat, wfe_p30)
            else "silvicultural_treatment"
        )
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
    """People / plantation / WFE / fuel-add urgency. PAD is not used."""
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
