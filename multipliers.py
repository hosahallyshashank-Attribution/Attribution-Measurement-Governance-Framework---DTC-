"""
DTC-MAIRF Multiplier Engine
===========================
Applies BAC / MDIC / IDIC multipliers to platform-reported ROAS figures,
producing aaROAS (Advanced Attribution ROAS) calibrated to evidence quality.

Evidence tiers:
  Tier 1 — BAC  (Benchmark Average Coefficient):  industry-average multiplier
  Tier 2 — MDIC (MMM-Derived Incrementality Coefficient): brand-specific MMM
  Tier 3 — IDIC (Incrementality-Derived Causal Inference): geo-test / RCT

Scepticism factor ranges (applied to produce lower-bound governance figure):
  Tier 1 BAC  — 10–40%
  Tier 2 MDIC —  5–15%
  Tier 3 IDIC —  0–5%

Reference: Hosahally, Sukumar & Bharadwaj (2025). Attribution Risk:
Formalising a Governance Framework for Marketing Capital Allocation
under Measurement Uncertainty.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

SCEPTICISM_RANGES = {
    "BAC":  (0.10, 0.40),
    "MDIC": (0.05, 0.15),
    "IDIC": (0.00, 0.05),
}


@dataclass
class ChannelInput:
    """Input data for a single channel."""
    channel_name: str
    spend: float
    lt_roas: float                        # Platform last-touch ROAS
    evidence_tier: str                    # "BAC", "MDIC", or "IDIC"
    multiplier: Optional[float] = None   # AA multiplier (aaRev / LT Rev)
    scepticism_override: Optional[float] = None  # Override default range midpoint


@dataclass
class ChannelOutput:
    """Output from the multiplier engine for a single channel."""
    channel_name: str
    spend: float
    lt_roas: float
    evidence_tier: str
    multiplier: float
    aa_roas: float                  # aaROAS = LT ROAS * multiplier
    scepticism_factor: float        # Applied scepticism factor (lower bound)
    aa_roas_adjusted: float         # aaROAS after scepticism factor applied
    aa_roas_lower: float            # Lower bound (governance decision point)
    aa_roas_upper: float            # Upper bound
    multiplier_gap_pct: float       # (LT ROAS - aaROAS) / LT ROAS * 100


def apply_multiplier(channel: ChannelInput, total_spend: float) -> ChannelOutput:
    """
    Apply the appropriate multiplier and scepticism factor to a channel.

    The governance decision always uses aa_roas_lower (lower bound of the
    scepticism range) — reflecting the precautionary principle that the cost
    of over-scaling a non-incremental channel exceeds the cost of under-scaling
    a genuinely incremental one (Kahneman & Tversky, 1979).
    """
    tier = channel.evidence_tier.upper()
    if tier not in SCEPTICISM_RANGES:
        raise ValueError(
            f"evidence_tier must be one of {list(SCEPTICISM_RANGES.keys())}, "
            f"got '{channel.evidence_tier}'"
        )

    # Default multiplier to 1.0 if not provided (no correction available)
    multiplier = channel.multiplier if channel.multiplier is not None else 1.0

    # Calculate aaROAS
    aa_roas = channel.lt_roas * multiplier

    # Apply scepticism factor — use lower bound for governance decisions
    s_low, s_high = SCEPTICISM_RANGES[tier]
    if channel.scepticism_override is not None:
        s_low = s_high = channel.scepticism_override

    aa_roas_lower = aa_roas * (1 - s_high)  # Most conservative
    aa_roas_upper = aa_roas * (1 - s_low)   # Least conservative
    aa_roas_adjusted = aa_roas_lower         # Governance uses lower bound

    # Multiplier Gap: positive = overvalued; negative = undervalued
    multiplier_gap_pct = ((channel.lt_roas - aa_roas) / channel.lt_roas * 100
                          if channel.lt_roas > 0 else 0.0)

    return ChannelOutput(
        channel_name=channel.channel_name,
        spend=channel.spend,
        lt_roas=channel.lt_roas,
        evidence_tier=tier,
        multiplier=multiplier,
        aa_roas=aa_roas,
        scepticism_factor=s_low,
        aa_roas_adjusted=aa_roas_adjusted,
        aa_roas_lower=aa_roas_lower,
        aa_roas_upper=aa_roas_upper,
        multiplier_gap_pct=multiplier_gap_pct,
    )


def apply_portfolio(channels: list[ChannelInput]) -> list[ChannelOutput]:
    """Apply multipliers to an entire portfolio of channels."""
    total_spend = sum(c.spend for c in channels)
    return [apply_multiplier(c, total_spend) for c in channels]
