"""
DTC-MAIRF Ledger of Assumptions (LoA) Generator
================================================
Generates a structured Ledger of Assumptions entry for each channel,
documenting the evidence tier, scepticism factor, AA source, multiplier
version, and uncertainty caveat — creating an audit trail equivalent to
financial reporting schedules (Horngren et al., 2015).

The Ledger of Assumptions is the paper's Pillar 3 instrument:
it anchors governance decisions to an auditable record that Finance
can verify against the internal system of record.
"""

from dataclasses import dataclass
from datetime import datetime
from core.multipliers import ChannelOutput
from core.posture import PostureOutput

AA_SOURCE_LABELS = {
    "BAC":  "Industry benchmark multiplier (BAC) — M² / Measured.com or equivalent. "
            "Population-level correction only. Not brand-specific aaROAS.",
    "MDIC": "MMM-Derived Incrementality Coefficient (MDIC) — brand-specific "
            "statistical regression from historical spend/revenue data. "
            "aaROAS produced at Tier 2.",
    "IDIC": "Incrementality-Derived Causal Inference (IDIC) — geo-test, RCT, "
            "or conversion lift study providing causal proof net of organic "
            "baseline demand. aaROAS produced at Tier 3.",
}

UNCERTAINTY_CAVEATS = {
    "BAC":  "HIGH uncertainty — population-level multiplier may be systematically "
            "wrong for this brand. Governance decision uses lower bound of "
            "10–40% scepticism range. Brand-specific MDIC or IDIC required "
            "before scaling authority is granted.",
    "MDIC": "MEDIUM uncertainty — brand-specific MMM estimate subject to model "
            "specification and data quality constraints. Governance decision "
            "uses lower bound of 5–15% scepticism range. IDIC validation "
            "required before Confident Scale is authorised.",
    "IDIC": "LOW residual uncertainty — causal proof established through "
            "controlled experiment. Governance decision uses lower bound of "
            "0–5% scepticism range reflecting residual methodological uncertainty only.",
}


@dataclass
class LoAEntry:
    """A single Ledger of Assumptions entry for one channel."""
    channel_name: str
    period: str
    evidence_tier: str
    aa_source: str
    multiplier: float
    multiplier_version: str
    lt_roas: float
    aa_roas: float
    aa_roas_governance: float         # Lower bound used for decision
    scepticism_range: str
    posture: str
    governance_action: str
    uncertainty_caveat: str
    cfo_acknowledged: bool
    analyst: str
    timestamp: str
    notes: str


def generate_loa_entry(
    channel_out: ChannelOutput,
    posture_out: PostureOutput,
    period: str = "Not specified",
    multiplier_version: str = "v1.0",
    cfo_acknowledged: bool = False,
    analyst: str = "Not specified",
    notes: str = "",
) -> LoAEntry:
    """Generate a Ledger of Assumptions entry for a single channel."""
    tier = channel_out.evidence_tier.upper()
    s_low, s_high = {
        "BAC":  (0.10, 0.40),
        "MDIC": (0.05, 0.15),
        "IDIC": (0.00, 0.05),
    }.get(tier, (0.10, 0.40))

    return LoAEntry(
        channel_name=channel_out.channel_name,
        period=period,
        evidence_tier=tier,
        aa_source=AA_SOURCE_LABELS.get(tier, "Unknown"),
        multiplier=channel_out.multiplier,
        multiplier_version=multiplier_version,
        lt_roas=channel_out.lt_roas,
        aa_roas=channel_out.aa_roas,
        aa_roas_governance=channel_out.aa_roas_lower,
        scepticism_range=f"{int(s_low*100)}–{int(s_high*100)}%",
        posture=posture_out.posture,
        governance_action=posture_out.governance_action,
        uncertainty_caveat=UNCERTAINTY_CAVEATS.get(tier, ""),
        cfo_acknowledged=cfo_acknowledged,
        analyst=analyst,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        notes=notes,
    )


def generate_portfolio_loa(
    channel_outputs: list[ChannelOutput],
    posture_outputs: list[PostureOutput],
    period: str = "Not specified",
    multiplier_version: str = "v1.0",
    analyst: str = "Not specified",
) -> list[LoAEntry]:
    """Generate LoA entries for an entire portfolio."""
    posture_map = {p.channel_name: p for p in posture_outputs}
    entries = []
    for ch in channel_outputs:
        posture = posture_map.get(ch.channel_name)
        if posture:
            # Auto-flag CFO acknowledgement required for CRITICAL/SPECULATIVE
            cfo_ack = posture.posture not in ("CRITICAL", "SPECULATIVE")
            entries.append(generate_loa_entry(
                ch, posture,
                period=period,
                multiplier_version=multiplier_version,
                cfo_acknowledged=cfo_ack,
                analyst=analyst,
            ))
    return entries
