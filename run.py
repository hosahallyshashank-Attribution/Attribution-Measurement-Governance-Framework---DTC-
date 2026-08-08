"""
DTC-MAIRF Worked Example: Brand X
===================================
Large-scale retention-dominated DTC brand — Q4 2023.
All figures anonymised per agreed confidentiality protocol.
Data provided by M-Squared Attribution (Bharadwaj, 2024).

BDAC Level 2 (Developing) — MMM operational across all three P&Ls.
Three P&L structure: Acquisition (4%) + Retention (85%) + Reactivation (13%).

Key governance finding: Promo · All at 58% of total budget — CRITICAL posture.
Cross-P&L halo effect confirmed: all prospecting channels carry measurable
halo contribution to Retention and Reactivation revenue.

Reference: Hosahally, Sukumar & Bharadwaj (2025) — Appendix A.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.multipliers import ChannelInput, apply_portfolio
from core.posture import assign_portfolio_postures
from core.loa import generate_portfolio_loa
from outputs.triangulation_sheet import generate_csv, print_summary

# ── CHANNEL INPUTS ─────────────────────────────────────────────────────────
# Multipliers calibrated from cross-brand benchmark averages and
# model-derived custom coefficients adjusted through historical
# incrementality experiments (M-Squared Attribution methodology).
# Spend figures are exact from Q4 2023 dataset.

channels = [
    ChannelInput(
        channel_name="Roku OTT Prospecting",
        spend=767_788,
        lt_roas=115.0,
        evidence_tier="IDIC",
        multiplier=0.26,        # 26% aaMultiplier — scale
    ),
    ChannelInput(
        channel_name="Apple Search Ads Brand",
        spend=358_340,
        lt_roas=13.1,
        evidence_tier="IDIC",
        multiplier=0.11,        # 11% aaMultiplier — cut
    ),
    ChannelInput(
        channel_name="Google Display",
        spend=54_736,
        lt_roas=11.0,
        evidence_tier="IDIC",
        multiplier=4.67,        # 467% aaMultiplier — scale (hidden driver)
    ),
    ChannelInput(
        channel_name="Facebook Prospecting",
        spend=487_992,
        lt_roas=26.5,
        evidence_tier="IDIC",
        multiplier=1.06,        # 106% aaMultiplier — scale
    ),
    ChannelInput(
        channel_name="TV Prospecting",
        spend=5_941_151,
        lt_roas=1.4,
        evidence_tier="MDIC",  # MMM — halo effect Y across retention
        multiplier=3.73,        # 373% aaMultiplier — hold pending testing
    ),
    ChannelInput(
        channel_name="Ad Roll Mobile Ad Network",
        spend=465_697,
        lt_roas=5.0,
        evidence_tier="IDIC",
        multiplier=8.38,        # 838% aaMultiplier — scale (reactivation ROAS selected)
        # Note: channel characteristics exception applies for reactivation
        # post-ATT IDFA degradation limits match rates for lapsed customers
    ),
    ChannelInput(
        channel_name="Roku OTT Prospecting 2",
        spend=2_224_969,
        lt_roas=39.7,
        evidence_tier="IDIC",
        multiplier=0.26,        # 26% aaMultiplier
    ),
    ChannelInput(
        channel_name="Radio Prospecting",
        spend=3_205_108,
        lt_roas=10.5,
        evidence_tier="IDIC",
        multiplier=0.34,        # 34% aaMultiplier — cut
    ),
    ChannelInput(
        channel_name="Google Non-Brand Search",
        spend=6_703_595,
        lt_roas=2.8,
        evidence_tier="IDIC",
        multiplier=0.36,        # 36% aaMultiplier — cut
    ),
    ChannelInput(
        channel_name="Google Brand Search",
        spend=2_457_429,
        lt_roas=16.8,
        evidence_tier="IDIC",
        multiplier=0.53,        # 53% aaMultiplier — scale
    ),
    ChannelInput(
        channel_name="Google Non-Brand Shopping",
        spend=4_172_791,
        lt_roas=3.1,
        evidence_tier="MDIC",
        multiplier=0.0,         # 0% aaMultiplier — hold
    ),
    ChannelInput(
        channel_name="TikTok Prospecting",
        spend=809_483,
        lt_roas=17.8,
        evidence_tier="IDIC",
        multiplier=0.04,        # 4% aaMultiplier — cut
    ),
    ChannelInput(
        channel_name="Google UAC Prospecting",
        spend=4_716_412,
        lt_roas=3.3,
        evidence_tier="IDIC",
        multiplier=2.07,        # 207% aaMultiplier — scale (hidden driver)
    ),
    ChannelInput(
        channel_name="Google Youtube Prospecting",
        spend=3_154_976,
        lt_roas=1.9,
        evidence_tier="MDIC",  # High multiplier variation — evidence gap
        multiplier=2.58,        # 258% aaMultiplier — requires IDIC testing
    ),
    ChannelInput(
        channel_name="Promo All",
        spend=49_237_284,       # 58% of total budget — CRITICAL posture
        lt_roas=5.4,
        evidence_tier="MDIC",  # Promotional mechanic precludes holdout design
        multiplier=0.63,        # 63% aaMultiplier — cut spend
        # Note: Consolidation Risk at maximum scale
        # Judgement Override required — mandatory IDIC testing before scaling
    ),
]

# ── RUN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    total_spend = sum(c.spend for c in channels)

    channel_outputs  = apply_portfolio(channels)
    posture_outputs  = assign_portfolio_postures(channel_outputs)
    loa_entries      = generate_portfolio_loa(
        channel_outputs,
        posture_outputs,
        period="Q4 2023",
        multiplier_version="v1.0 (M-Squared calibrated multipliers)",
        analyst="DTC-MAIRF Toolkit",
    )

    print_summary(
        channel_outputs,
        posture_outputs,
        total_spend,
        brand_name="Brand X (anonymised)",
        period="Q4 2023",
    )

    generate_csv(
        channel_outputs,
        posture_outputs,
        total_spend,
        output_path="examples/brand_x/triangulation_summary.csv",
    )

    print("\nLEDGER OF ASSUMPTIONS SUMMARY")
    print("-" * 60)
    for entry in loa_entries:
        print(f"  {entry.channel_name:<35} | {entry.posture:<12} | "
              f"CFO Ack: {'✓' if entry.cfo_acknowledged else '✗ REQUIRED'}")
    print()
