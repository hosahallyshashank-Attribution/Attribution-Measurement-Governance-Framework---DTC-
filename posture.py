"""
DTC-MAIRF Posture Engine
========================
Assigns one of five governance postures to each channel based on two
observable conditions: budget concentration and evidence tier.

Five governance postures (Table 8, DTC-MAIRF):
  CRITICAL     - Budget >40% + Tier 1 BAC evidence only
  STRATEGIC    - Budget >30% + Tier 3 IDIC causal proof
  SPECULATIVE  - Multiplier Gap >50% at Tier 2 MDIC AND budget >=5%
  EXPLORATORY  - Budget <5% regardless of tier OR budget <20% with BAC/MDIC
  VERIFIED     - Small budget footprint + Tier 3 IDIC proof

Decision priority:
  1. CRITICAL   checked first (highest risk)
  2. STRATEGIC  checked second (high concentration + proven)
  3. EXPLORATORY checked third (small footprint - protects small channels
     from SPECULATIVE escalation when budget concentration is low)
  4. SPECULATIVE checked fourth (large Multiplier Gap + material budget)
  5. VERIFIED   checked fifth
  6. Default SPECULATIVE if none match

Multiplier Gap sign convention:
  Positive = overvaluation (Value Trap) - aaROAS < LT ROAS
  Negative = undervaluation (Hidden Driver) - aaROAS > LT ROAS
"""

from dataclasses import dataclass
from core.multipliers import ChannelOutput

# Concentration thresholds (as percentages)
THRESHOLD_CRITICAL        = 40.0   # >40% budget + BAC only = CRITICAL
THRESHOLD_STRATEGIC       = 30.0   # >30% budget + IDIC proof = STRATEGIC
THRESHOLD_CFO_TIER1       = 20.0   # >20% budget = CFO approval at Tier 1
THRESHOLD_EXPLORATORY_MIN =  5.0   # <5% budget = EXPLORATORY regardless
THRESHOLD_SPECULATIVE_GAP = 50.0   # >50% Multiplier Gap = SPECULATIVE
THRESHOLD_SPECULATIVE_MIN =  5.0   # Must have >=5% budget for SPECULATIVE

POSTURE_ACTIONS = {
    "CRITICAL":    "MANDATORY HOLD - Capital frozen. All scaling paused pending IDIC causal validation within 90 days.",
    "STRATEGIC":   "CONFIDENT SCALE - Causal proof established. CFO sign-off required before full capital release.",
    "SPECULATIVE": "JUDGEMENT OVERRIDE - Significant signal divergence. Joint CMO/CFO review required before scaling proceeds.",
    "EXPLORATORY": "AUTONOMOUS TEST - Small budget footprint. Safe Harbour applies. CMO oversight only.",
    "VERIFIED":    "OPTIMISE/SCALE - Multiple sources confirmed within variance tolerance. Quarterly Finance review.",
}

CFO_REQUIREMENTS = {
    "CRITICAL":    "Full CFO escalation required. IDIC validation mandatory within 90 days before any budget release.",
    "STRATEGIC":   "CFO sign-off required. Evidence documented in Ledger of Assumptions before capital release.",
    "SPECULATIVE": "Joint CMO/CFO review triggered. Causal Multiplier applied. Tier 3 validation before aggressive scaling.",
    "EXPLORATORY": "CMO oversight only. No CFO escalation required. Ring-fenced Safe Harbour budget applies.",
    "VERIFIED":    "Quarterly Finance review. Autonomous scaling permitted within evidence-validated parameters.",
}

MULTIPLIER_GAP_NOTE = (
    "Multiplier Gap sign convention: "
    "POSITIVE = platform overvalues channel (Value Trap, aaROAS < LT ROAS); "
    "NEGATIVE = platform undervalues channel (Hidden Driver, aaROAS > LT ROAS)."
)

AATOES_NOTE = (
    "aaROAS (governance) = lower bound of scepticism range applied to aaROAS. "
    "Used for capital allocation decisions per precautionary principle "
    "(Kahneman & Tversky, 1979). "
    "BAC: 10-40% scepticism. MDIC: 5-15%. IDIC: 0-5%."
)


@dataclass
class PostureOutput:
    """Governance posture assignment for a single channel."""
    channel_name: str
    budget_pct: float
    evidence_tier: str
    multiplier_gap_pct: float
    posture: str
    governance_action: str
    cfo_requirement: str
    cfо_escalation_required: bool
    rationale: str


def assign_posture(channel: ChannelOutput, total_spend: float) -> PostureOutput:
    """
    Assign a governance posture to a channel based on budget concentration
    and evidence tier.

    Decision logic follows Table 8 (DTC-MAIRF Decision Matrix).
    Priority order matters — EXPLORATORY is checked before SPECULATIVE
    to prevent small-footprint channels from triggering CFO escalation
    purely on Multiplier Gap when their budget concentration is immaterial.
    """
    budget_pct = (channel.spend / total_spend * 100
                  if total_spend > 0 else 0.0)
    tier = channel.evidence_tier.upper()
    gap  = abs(channel.multiplier_gap_pct)

    # ── 1. CRITICAL: highest risk — large budget + weakest evidence ──────
    if budget_pct > THRESHOLD_CRITICAL and tier == "BAC":
        posture = "CRITICAL"
        rationale = (
            f"Budget {budget_pct:.1f}% exceeds 40% with Tier 1 BAC only. "
            f"Capital at maximum risk — mandatory Hold."
        )

    # ── 2. STRATEGIC: large budget + causal proof earned ─────────────────
    elif budget_pct > THRESHOLD_STRATEGIC and tier == "IDIC":
        posture = "STRATEGIC"
        rationale = (
            f"Budget {budget_pct:.1f}% exceeds 30% with Tier 3 IDIC causal proof. "
            f"Confident Scale authorised — CFO sign-off required."
        )

    # ── 3. EXPLORATORY: small footprint — checked BEFORE SPECULATIVE ─────
    #    Channels below 5% budget are EXPLORATORY regardless of Multiplier Gap.
    #    Channels below 20% budget with BAC/MDIC are EXPLORATORY.
    #    This prevents immaterial channels from triggering CFO escalation.
    elif budget_pct < THRESHOLD_EXPLORATORY_MIN:
        posture = "EXPLORATORY"
        rationale = (
            f"Budget {budget_pct:.1f}% below 5% minimum threshold. "
            f"Safe Harbour applies regardless of Multiplier Gap — "
            f"immaterial concentration does not warrant CFO escalation."
        )

    elif budget_pct < THRESHOLD_CFO_TIER1 and tier in ("BAC", "MDIC"):
        posture = "EXPLORATORY"
        rationale = (
            f"Budget {budget_pct:.1f}% below 20% threshold at {tier} evidence. "
            f"Safe Harbour applies — autonomous testing authorised."
        )

    # ── 4. SPECULATIVE: material budget + large Multiplier Gap ───────────
    #    Only triggered when budget is >= 5% — prevents over-escalation
    #    of small channels with high multiplier variation.
    elif (gap > THRESHOLD_SPECULATIVE_GAP
          and tier == "MDIC"
          and budget_pct >= THRESHOLD_SPECULATIVE_MIN):
        posture = "SPECULATIVE"
        rationale = (
            f"Multiplier Gap {gap:.1f}% exceeds 50% at Tier 2 MDIC "
            f"with material budget concentration {budget_pct:.1f}%. "
            f"Significant divergence between platform and advanced attribution."
        )

    # ── 5. VERIFIED: causal proof + small footprint ───────────────────────
    elif tier == "IDIC" and budget_pct <= THRESHOLD_STRATEGIC:
        posture = "VERIFIED"
        rationale = (
            f"Tier 3 IDIC causal proof with budget {budget_pct:.1f}%. "
            f"Optimise and scale with quarterly Finance review."
        )

    # ── 6. Default SPECULATIVE ─────────────────────────────────────────────
    else:
        posture = "SPECULATIVE"
        rationale = (
            f"Channel ({budget_pct:.1f}% budget, {tier}) does not meet "
            f"CRITICAL, STRATEGIC, EXPLORATORY, or VERIFIED criteria. "
            f"Classified SPECULATIVE pending further validation."
        )

    cfo_required = posture in ("CRITICAL", "STRATEGIC", "SPECULATIVE")

    return PostureOutput(
        channel_name=channel.channel_name,
        budget_pct=budget_pct,
        evidence_tier=tier,
        multiplier_gap_pct=channel.multiplier_gap_pct,
        posture=posture,
        governance_action=POSTURE_ACTIONS[posture],
        cfo_requirement=CFO_REQUIREMENTS[posture],
        cfо_escalation_required=cfo_required,
        rationale=rationale,
    )


def assign_portfolio_postures(
    channels: list[ChannelOutput],
) -> list[PostureOutput]:
    """Assign governance postures to an entire portfolio."""
    total_spend = sum(c.spend for c in channels)
    return [assign_posture(c, total_spend) for c in channels]
