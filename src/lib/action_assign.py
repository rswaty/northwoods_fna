"""v1 action cascade + priority scoring helpers.

Actions (first match):
  - plantation → value_to_protect_from_fire
  - peat / wetland → wetlands_assess_locally
  - High/VH WFE bin + High/VH people bin → treat_fire_risk_for_people
  - High/VH WFE bin (any other people bin) → ecosystem_health_focus
  - pine/oak in EVT top 3 + people Moderate/Low/Very Low → ecosystem_health_focus
  - else → defer_monitor

WFE gate: category bins only (High / Very High). No MEAN percentile bypass.
People gate: five AOI quintile bins (Very Low … Very High), same label set as WFE.
  Treat-for-people needs High or Very High people.
Pine safety net (tighten): top-3 EVT list match only when people are not High/VH.
  High/VH people + pine + not High/VH WFE → defer (homes alone do not create treat).

Fuel (FDist / ``FDIST_FUEL_DELTA``) is not an action trigger. It multiplies the
Goldilocks urgency score (add raises more than remove lowers) and stays on the
map as its own layer. High/VH WFE or high fuel-add hexes also get a score
**floor** (AOI percentile) so remote hot places are not near-zero on Goldilocks.

BpS / FIRE_DEP_HEX / EVT_FIRE / PAD are context only.
"""

from __future__ import annotations

NONACTIONABLE = {"defer_monitor"}
GOLDILOCKS_EXCLUDE = {"defer_monitor", "wetlands_assess_locally"}

PEOPLE_BIN_LABELS = (
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High",
)

# Goldilocks fuel multiplier: score *= 1 + α·δ⁺  or  1 + β·δ⁻  (α > β).
FUEL_ADD_ALPHA = 0.50
FUEL_REMOVE_BETA = 0.25

# After scoring: High/VH WFE or high fuel-add hexes get at least this AOI
# percentile of SCORE_PEOPLE (keeps remote hot hexes from ranking near zero).
HAZARD_SCORE_FLOOR_PCT = 0.40
FUEL_ADD_FLOOR_MIN = 0.25


def _norm_cat(cat: str | None) -> str:
    if not cat:
        return ""
    return str(cat).strip().lower().replace("_", " ")


def is_high_or_very_high_bin(cat: str | None) -> bool:
    """True for High / Very High category labels (WFE or people)."""
    c = _norm_cat(cat)
    return c in {"high", "very high", "vh", "h"}


def is_high_wfe(wfe_cat: str | None) -> bool:
    """WFE action gate: High or Very High bin only."""
    return is_high_or_very_high_bin(wfe_cat)


def is_high_people(people_cat: str | None) -> bool:
    """People action gate: High or Very High bin only."""
    return is_high_or_very_high_bin(people_cat)


def people_bin_allows_pine_ecosystem(people_cat: str | None) -> bool:
    """Tighten: pine → ecosystem only for Moderate / Low / Very Low people."""
    c = _norm_cat(people_cat)
    return c in {"moderate", "low", "very low", "m", "l", "vl"}


def quintile_edges(values: list[float]) -> list[float]:
    """Return four cut points (20/40/60/80th) for five equal-count bins."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return [0.0, 0.0, 0.0, 0.0]
    n = len(vals)

    def at_frac(frac: float) -> float:
        idx = min(n - 1, max(0, int(n * frac)))
        return vals[idx]

    return [at_frac(0.20), at_frac(0.40), at_frac(0.60), at_frac(0.80)]


def assign_people_bin(homes: float, edges: list[float]) -> str:
    """Map WRTC homes/risk to Very Low … Very High using AOI quintile edges."""
    if len(edges) < 4:
        edges = quintile_edges([homes])
    e0, e1, e2, e3 = edges[0], edges[1], edges[2], edges[3]
    if homes < e0:
        return "Very Low"
    if homes < e1:
        return "Low"
    if homes < e2:
        return "Moderate"
    if homes < e3:
        return "High"
    return "Very High"


def is_high_fuel_add(fdist_delta: float, fuel_add_min: float) -> bool:
    """Area-weighted FDist fuel direction; positive = net fuel add (map flag)."""
    return fdist_delta >= fuel_add_min


def fuel_goldilocks_multiplier(
    fdist_delta: float,
    *,
    alpha: float = FUEL_ADD_ALPHA,
    beta: float = FUEL_REMOVE_BETA,
) -> float:
    """Asymmetric score multiplier from FDist (−1 … +1). Add > remove in strength."""
    d = float(fdist_delta or 0.0)
    if d >= 0:
        return 1.0 + alpha * d
    return 1.0 + beta * d


def assign_action_v1(
    *,
    peat: bool,
    plantation: bool,
    wfe_cat: str | None,
    people_cat: str | None,
    pine_barrens: bool = False,
    # Legacy kwargs kept so older callers fail soft during transition
    wfe: float = 0.0,
    homes: float = 0.0,
    wfe_p30: float = 0.0,
    homes_p30: float = 0.0,
    fdist_delta: float = 0.0,
    fuel_add_min: float = 0.25,
    fire_dependent: bool = False,
) -> str:
    """First-match cascade. PAD / BpS / EVT_FIRE / fuel are not action inputs."""
    del wfe, homes, wfe_p30, homes_p30, fdist_delta, fuel_add_min, fire_dependent

    if plantation:
        return "value_to_protect_from_fire"
    if peat:
        return "wetlands_assess_locally"

    high_wfe = is_high_wfe(wfe_cat)
    high_people = is_high_people(people_cat)

    if high_wfe and high_people:
        return "treat_fire_risk_for_people"
    if high_wfe:
        return "ecosystem_health_focus"
    # Tighten: pine top-3 only when people are Moderate or lower.
    if pine_barrens and people_bin_allows_pine_ecosystem(people_cat):
        return "ecosystem_health_focus"
    return "defer_monitor"


def treatment_hint(
    *,
    action: str,
    plantation: bool,
    wfe_cat: str | None,
    wfe: float = 0.0,
    wfe_p30: float = 0.0,
) -> str:
    """How to carry out the action — secondary to ACTION_CLASS."""
    del wfe, wfe_p30
    if plantation:
        return (
            "silviculture_then_fire"
            if is_high_wfe(wfe_cat)
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
    fuel_alpha: float = FUEL_ADD_ALPHA,
    fuel_beta: float = FUEL_REMOVE_BETA,
) -> float:
    """Homes / plantation / WFE base × asymmetric FDist fuel multiplier."""
    del w_fuel_add
    base = w_homes * homes + w_plantations * plantation + w_wfe * wfe
    return base * fuel_goldilocks_multiplier(
        fuel_add, alpha=fuel_alpha, beta=fuel_beta
    )


def needs_hazard_score_floor(
    wfe_cat: str | None,
    fdist_delta: float,
    *,
    fuel_add_min: float = FUEL_ADD_FLOOR_MIN,
) -> bool:
    """True when hex should get the Goldilocks hazard floor."""
    return is_high_wfe(wfe_cat) or is_high_fuel_add(fdist_delta, fuel_add_min)


def apply_hazard_score_floor(
    scores: list[float],
    apply_flags: list[bool],
    *,
    floor_pct: float = HAZARD_SCORE_FLOOR_PCT,
) -> tuple[list[float], float, int]:
    """Lift flagged scores up to an AOI percentile floor.

    Returns (new_scores, floor_value, n_lifted).
    """
    if not scores or len(scores) != len(apply_flags):
        return list(scores), 0.0, 0
    floor = percentile_threshold(list(scores), floor_pct)
    out: list[float] = []
    n_lifted = 0
    for score, flag in zip(scores, apply_flags):
        if flag and score < floor:
            out.append(floor)
            n_lifted += 1
        else:
            out.append(score)
    return out, floor, n_lifted


def percentile_threshold(values: list[float], pct: float = 0.70) -> float:
    """Value at percentile (legacy helper; action gates no longer use this)."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return 0.0
    idx = min(len(vals) - 1, max(0, int(len(vals) * pct)))
    return vals[idx]


# Back-compat aliases used by older docs / exploratory code
def is_elevated_wfe_for_ecosystem(
    wfe: float, wfe_cat: str | None, wfe_p30: float
) -> bool:
    del wfe, wfe_p30
    return is_high_wfe(wfe_cat)


def is_high_wrtc(homes: float, homes_p30: float) -> bool:
    """Deprecated: prefer PEOPLE_CAT High/VH. Kept for any external callers."""
    return homes >= homes_p30
