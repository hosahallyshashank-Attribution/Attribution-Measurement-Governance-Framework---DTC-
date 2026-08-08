"""
DTC-MAIRF Worked Example: Brand Alpha
======================================
US mid-market DTC fashion brand — February–April 2024 baseline.
All figures anonymised per agreed confidentiality protocol.

BDAC Level 1 (Nascent) at baseline — platform dashboards only.
Two P&L structure: Acquisition + Retention (Reactivation absent).

Reference: Hosahally, Sukumar & Bharadwaj (2025).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.multipliers import ChannelInput, apply_portfolio
from core.posture import assign_portfolio_postures
from core.loa import generate_portfolio_loa
from outputs.triangulation_sheet import generate_csv, print_summary

# ── CHANNEL INPUTS ─────────────────────────────────────────────────────────
# Multipliers derived retrospectively from MMM and geo-tests (Q3–Q4 2024).
# Evidence tier reflects the AA source used per channel.
# Figures masked: spend values are proportional to actual, not exact.

channels = [
    ChannelInput(
        channel_name="FB Acquisition",
        spend=190_076,
        lt_roas=3.3,
        evidence_tier="IDIC",   # Dual validated: MMM + Platform Lift
        multiplier=1.12,        # -12% variance: validated anchor
    ),
    ChannelInput(
        channel_name="FB Retention",
        spend=17_582,
        lt_roas=13.7,
        evidence_tier="MDIC",   # MMM only
        multiplier=0.22,        # 78% overvaluation: value trap + structural exception
    ),
    ChannelInput(
        channel_name="Google Brand Search",
        spend=11_176,
        lt_roas=92.4,
        evidence_tier="MDIC",
        multiplier=0.02,        # 98% overvaluation: organic demand capture
    ),
    ChannelInput(
        channel_name="Google Brand Shopping",
        spend=4_465,
        lt_roas=12.7,
        evidence_tier="MDIC",
        multiplier=0.03,        # 97% overvaluation
    ),
    ChannelInput(
        channel_name="Google Non-Brand Search",
        spend=29_784,
        lt_roas=1.6,
        evidence_tier="IDIC",   # Geo-test validated
        multiplier=3.38,        # 238% undervaluation: hidden driver
    ),
    ChannelInput(
        channel_name="Google Shopping",
        spend=3_719,
        lt_roas=1.6,
        evidence_tier="BAC",    # Insufficient order volume for MMM
        multiplier=None,        # No multiplier available
    ),
    ChannelInput(
        channel_name="Google PMAX",
        spend=93_076,
        lt_roas=1.9,
        evidence_tier="MDIC",
        multiplier=3.68,        # 268% undervaluation: cross-inventory collapse
    ),
    ChannelInput(
        channel_name="Google Discovery",
        spend=0,
        lt_roas=2.0,
        evidence_tier="MDIC",
        multiplier=20.55,       # 41.1x aaROAS: channel characteristics exception
    ),
    ChannelInput(
        channel_name="Email",
        spend=14_892,
        lt_roas=36.5,
        evidence_tier="MDIC",
        multiplier=0.86,        # 14% variance: validated anchor
    ),
    ChannelInput(
        channel_name="SMS",
        spend=11_176,
        lt_roas=9.0,
        evidence_tier="BAC",    # GDPR permanent constraint
        multiplier=None,
    ),
    ChannelInput(
        channel_name="Affiliates",
        spend=0,
        lt_roas=0.0,
        evidence_tier="BAC",    # Zero paid spend
        multiplier=None,
    ),
]

# ── RUN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    total_spend = sum(c.spend for c in channels)

    # 1. Apply multipliers
    channel_outputs = apply_portfolio(channels)

    # 2. Assign governance postures
    posture_outputs = assign_portfolio_postures(channel_outputs)

    # 3. Generate LoA entries
    loa_entries = generate_portfolio_loa(
        channel_outputs,
        posture_outputs,
        period="Feb–Apr 2024",
        multiplier_version="v1.0 (retrospective Q3–Q4 2024)",
        analyst="DTC-MAIRF Toolkit",
    )

    # 4. Print summary to console
    print_summary(
        channel_outputs,
        posture_outputs,
        total_spend,
        brand_name="Brand Alpha (anonymised)",
        period="Feb–Apr 2024",
    )

    # 5. Export CSV
    generate_csv(
        channel_outputs,
        posture_outputs,
        total_spend,
        output_path="examples/brand_alpha/triangulation_summary.csv",
    )

    # 6. Print LoA summary
    print("\nLEDGER OF ASSUMPTIONS SUMMARY")
    print("-" * 60)
    for entry in loa_entries:
        print(f"  {entry.channel_name:<30} | {entry.posture:<12} | "
              f"CFO Ack: {'✓' if entry.cfo_acknowledged else '✗ REQUIRED'}")
    print()
