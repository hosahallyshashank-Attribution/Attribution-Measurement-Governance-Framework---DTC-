"""
DTC-MAIRF Posture Engine
========================
Assigns one of five governance postures to each channel based on two
observable conditions: budget concentration and evidence tier.

Five governance postures (Table 8, DTC-MAIRF):
  CRITICAL     — Budget >40% + Tier 1 BAC evidence only
  STRATEGIC    — Budget >30% + Tier 3 IDIC causal proof
  SPECULATIVE  — Multiplier Gap >50% at Tier 2 MDIC
  EXPLORATORY  — Budget <20% + Tier 1 BAC evidence
  VERIFIED     — Small budget footprint + Tier 3 IDIC proof

Each posture maps to a governance action and CFO requirement.
"""

from dataclasses import dataclass
from core.multipliers import ChannelOutput

# Concentration thresholds (as proportions)
THRESHOLD_CRITICAL   = 0.40   # >40% → CRITICAL if BAC only
THRESHOLD_STRATEGIC  = 0.30   # >30% → STRATEGIC if IDIC proven
THRESHOLD_CFO_TIER1  = 0.20   # >20% → mandatory CFO approval at Tier 1
THRESHOLD_CFO_TIER3  = 0.30   # >30% → CFO sign-off for Confident Scale
THRESHOLD_SPECULATIVE_GAP = 50.0  # >50% Multiplier Gap → SPECULATIVE

POSTURE_ACTIONS = {
    "CRITICAL":    "MANDATORY HOLD — all scaling paused",
    "STRATEGIC":   "CONFIDENT SCALE — CFO sign-off required",
    "SPECULATIVE": "JUDGEMENT OVERRIDE — joint CMO/CFO review",
    "EXPLORATORY": "AUTONOMOUS TEST — Safe Harbour applies",
    "VERIFIED":    "OPTIMISE / SCALE — quarterly Finance review",
}

CFO_REQUIREMENTS = {
    "CRITICAL":    "Full CFO escalation — IDIC validation within 90 days",
    "STRATEGIC":   "CFO sign-off required — evidence in Ledger of Assumptions",
    "SPECULATIVE": "Joint CMO/CFO review — Causal Multiplier applied",
    "EXPLORATORY": "CMO oversight only — no CFO escalation required",
    "VERIFIED":    "Quarterly Finance review — autonomous scaling permitted",
}


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

    Decision logic follows Table 8 (DTC-MAIRF Decision Matrix):
    1. CRITICAL   — concentration >40% AND Tier 1 BAC only
    2. STRATEGIC  — concentration >30% AND Tier 3 IDIC proven
    3. SPECULATIVE — Multiplier Gap >50% at Tier 2 MDIC
    4. EXPLORATORY — concentration <20% AND Tier 1 BAC
    5. VERIFIED   — small footprint AND Tier 3 IDIC proven
    """
    budget_pct = (channel.spend / total_spend * 100
                  if total_spend > 0 else 0.0)
    tier  = channel.evidence_tier.upper()
    gap   = abs(channel.multiplier_gap_pct)

    # --- Rule application (priority order) ---
    if budget_pct > THRESHOLD_CRITICAL * 100 and tier == "BAC":
        posture = "CRITICAL"
        rationale = (
            f"Budget concentration {budget_pct:.1f}% exceeds 40% threshold "
            f"with Tier 1 BAC evidence only — capital at maximum risk."
        )

    elif budget_pct > THRESHOLD_STRATEGIC * 100 and tier == "IDIC":
        posture = "STRATEGIC"
        rationale = (
            f"Budget concentration {budget_pct:.1f}% exceeds 30% threshold "
            f"with Tier 3 IDIC causal proof — Confident Scale authorised."
        )

    elif gap > THRESHOLD_SPECULATIVE_GAP and tier == "MDIC":
        posture = "SPECULATIVE"
        rationale = (
            f"Multiplier Gap of {gap:.1f}% exceeds 50% at Tier 2 MDIC — "
            f"significant divergence between platform and advanced attribution."
        )

    elif budget_pct < THRESHOLD_CFO_TIER1 * 100 and tier in ("BAC", "MDIC"):
        posture = "EXPLORATORY"
        rationale = (
            f"Budget concentration {budget_pct:.1f}% below 20% threshold — "
            f"Safe Harbour applies; autonomous testing authorised."
        )

    elif tier == "IDIC" and budget_pct <= THRESHOLD_STRATEGIC * 100:
        posture = "VERIFIED"
        rationale = (
            f"Tier 3 IDIC causal proof with small budget footprint "
            f"({budget_pct:.1f}%) — optimise and scale with quarterly review."
        )

    else:
        # Default: treat as SPECULATIVE if none of the above match
        posture = "SPECULATIVE"
        rationale = (
            f"Channel does not meet CRITICAL, STRATEGIC, EXPLORATORY, or "
            f"VERIFIED criteria — classified SPECULATIVE pending further validation."
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
