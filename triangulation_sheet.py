"""
DTC-MAIRF Triangulation Summary Sheet Generator
================================================
Generates the Triangulation Summary Sheet — the framework's central
governance output — as both a CSV file and a formatted console report.

Columns produced:
  Channel | Spend | % Budget | LT ROAS | aaROAS | aaROAS (governance) |
  Multiplier Gap % | Evidence Tier | Posture | Governance Action |
  CFO Escalation | Scepticism Range
"""

import csv
import io
from core.multipliers import ChannelOutput
from core.posture import PostureOutput


def _fmt_roas(v: float) -> str:
    return f"{v:.1f}x"

def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%"

def _fmt_spend(v: float) -> str:
    return f"${v:,.0f}"


def generate_csv(
    channel_outputs: list[ChannelOutput],
    posture_outputs: list[PostureOutput],
    total_spend: float,
    output_path: str = None,
) -> str:
    """
    Generate the Triangulation Summary Sheet as CSV.
    Returns the CSV string; optionally writes to output_path.
    """
    posture_map = {p.channel_name: p for p in posture_outputs}

    fieldnames = [
        "Channel",
        "Spend ($)",
        "% Budget",
        "LT ROAS",
        "aaROAS",
        "aaROAS (governance lower bound)",
        "Multiplier Gap %",
        "Evidence Tier",
        "Posture",
        "Governance Action",
        "CFO Escalation Required",
        "Scepticism Range",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for ch in channel_outputs:
        p = posture_map.get(ch.channel_name)
        budget_pct = ch.spend / total_spend * 100 if total_spend > 0 else 0
        s_range = {
            "BAC":  "10–40%",
            "MDIC": "5–15%",
            "IDIC": "0–5%",
        }.get(ch.evidence_tier, "N/A")

        writer.writerow({
            "Channel":                           ch.channel_name,
            "Spend ($)":                         _fmt_spend(ch.spend),
            "% Budget":                          _fmt_pct(budget_pct),
            "LT ROAS":                           _fmt_roas(ch.lt_roas),
            "aaROAS":                            _fmt_roas(ch.aa_roas),
            "aaROAS (governance lower bound)":   _fmt_roas(ch.aa_roas_lower),
            "Multiplier Gap %":                  _fmt_pct(ch.multiplier_gap_pct),
            "Evidence Tier":                     ch.evidence_tier,
            "Posture":                           p.posture if p else "N/A",
            "Governance Action":                 p.governance_action if p else "N/A",
            "CFO Escalation Required":           "YES" if (p and p.cfо_escalation_required) else "NO",
            "Scepticism Range":                  s_range,
        })

    csv_str = output.getvalue()

    if output_path:
        with open(output_path, "w", newline="") as f:
            f.write(csv_str)
        print(f"Triangulation Summary Sheet saved to: {output_path}")

    return csv_str


def print_summary(
    channel_outputs: list[ChannelOutput],
    posture_outputs: list[PostureOutput],
    total_spend: float,
    brand_name: str = "Brand",
    period: str = "",
) -> None:
    """Print a formatted Triangulation Summary Sheet to console."""
    posture_map = {p.channel_name: p for p in posture_outputs}

    print("\n" + "="*90)
    print(f"  DTC-MAIRF TRIANGULATION SUMMARY SHEET")
    print(f"  {brand_name}{' — ' + period if period else ''}")
    print(f"  Total Media Spend: {_fmt_spend(total_spend)}")
    print("="*90)

    header = (
        f"{'Channel':<30} {'Spend':>10} {'%Bdgt':>6} "
        f"{'LT ROAS':>8} {'aaROAS':>8} {'Gap%':>7} "
        f"{'Tier':>5} {'Posture':>12} {'CFO':>4}"
    )
    print(header)
    print("-"*90)

    posture_symbols = {
        "CRITICAL":    "🔴",
        "STRATEGIC":   "🟢",
        "SPECULATIVE": "🟡",
        "EXPLORATORY": "🔵",
        "VERIFIED":    "✅",
    }

    for ch in channel_outputs:
        p = posture_map.get(ch.channel_name)
        budget_pct = ch.spend / total_spend * 100 if total_spend > 0 else 0
        posture = p.posture if p else "N/A"
        cfo = "YES" if (p and p.cfо_escalation_required) else "NO"
        symbol = posture_symbols.get(posture, "  ")

        print(
            f"{ch.channel_name:<30} "
            f"{_fmt_spend(ch.spend):>10} "
            f"{_fmt_pct(budget_pct):>6} "
            f"{_fmt_roas(ch.lt_roas):>8} "
            f"{_fmt_roas(ch.aa_roas):>8} "
            f"{_fmt_pct(ch.multiplier_gap_pct):>7} "
            f"{ch.evidence_tier:>5} "
            f"{symbol}{posture:>11} "
            f"{cfo:>4}"
        )

    print("="*90)
    critical = [p for p in posture_outputs if p.posture == "CRITICAL"]
    speculative = [p for p in posture_outputs if p.posture == "SPECULATIVE"]
    if critical or speculative:
        print(f"\n  ⚠  CFO ESCALATION REQUIRED: "
              f"{', '.join(p.channel_name for p in critical + speculative)}")
    print()
