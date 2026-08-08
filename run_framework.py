"""
DTC-MAIRF Command-Line Interface
=================================
Run the full DTC-MAIRF governance framework from a CSV input file.

Usage:
    python run_framework.py --input data/channel_input_template.csv
                            --brand "My Brand"
                            --period "Q4 2024"
                            --output outputs/

Arguments:
    --input    Path to channel input CSV (see data/channel_input_template.csv)
    --brand    Brand name (used in report headers)
    --period   Reporting period (e.g. "Q4 2024")
    --output   Output directory for CSV and LoA report (default: outputs/)
    --example  Run built-in example: "brand_alpha" or "brand_x"
"""

import argparse
import csv
import os
import sys

from core.multipliers import ChannelInput, apply_portfolio
from core.posture import assign_portfolio_postures
from core.loa import generate_portfolio_loa
from outputs.triangulation_sheet import generate_csv, print_summary


def load_channels_from_csv(path: str) -> list[ChannelInput]:
    """Load channel inputs from a CSV file."""
    channels = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["channel_name"].startswith("#"):
                continue  # skip comment rows
            channels.append(ChannelInput(
                channel_name=row["channel_name"],
                spend=float(row["spend"]),
                lt_roas=float(row["lt_roas"]),
                evidence_tier=row["evidence_tier"].strip().upper(),
                multiplier=float(row["multiplier"]) if row.get("multiplier") else None,
                scepticism_override=float(row["scepticism_override"])
                    if row.get("scepticism_override") else None,
            ))
    return channels


def write_loa_report(loa_entries, output_path: str) -> None:
    """Write the Ledger of Assumptions as a structured text report."""
    with open(output_path, "w") as f:
        f.write("DTC-MAIRF LEDGER OF ASSUMPTIONS\n")
        f.write("=" * 80 + "\n\n")
        for entry in loa_entries:
            f.write(f"Channel:              {entry.channel_name}\n")
            f.write(f"Period:               {entry.period}\n")
            f.write(f"Evidence Tier:        {entry.evidence_tier}\n")
            f.write(f"AA Source:            {entry.aa_source}\n")
            f.write(f"Multiplier:           {entry.multiplier:.2f}x "
                    f"(version {entry.multiplier_version})\n")
            f.write(f"LT ROAS:              {entry.lt_roas:.1f}x\n")
            f.write(f"aaROAS:               {entry.aa_roas:.1f}x\n")
            f.write(f"aaROAS (governance):  {entry.aa_roas_governance:.1f}x "
                    f"[lower bound — used for decisions]\n")
            f.write(f"Scepticism Range:     {entry.scepticism_range}\n")
            f.write(f"Posture:              {entry.posture}\n")
            f.write(f"Governance Action:    {entry.governance_action}\n")
            f.write(f"CFO Acknowledged:     "
                    f"{'YES' if entry.cfo_acknowledged else 'REQUIRED — NOT YET ACKNOWLEDGED'}\n")
            f.write(f"Uncertainty Caveat:   {entry.uncertainty_caveat}\n")
            f.write(f"Analyst:              {entry.analyst}\n")
            f.write(f"Timestamp:            {entry.timestamp}\n")
            if entry.notes:
                f.write(f"Notes:                {entry.notes}\n")
            f.write("-" * 80 + "\n\n")
    print(f"Ledger of Assumptions saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="DTC-MAIRF Governance Framework")
    parser.add_argument("--input",   type=str, help="Path to channel input CSV")
    parser.add_argument("--brand",   type=str, default="Brand", help="Brand name")
    parser.add_argument("--period",  type=str, default="", help="Reporting period")
    parser.add_argument("--output",  type=str, default="outputs/", help="Output directory")
    parser.add_argument("--example", type=str, choices=["brand_alpha", "brand_x"],
                        help="Run built-in example")
    args = parser.parse_args()

    if args.example == "brand_alpha":
        os.system("python examples/brand_alpha/run.py")
        return
    elif args.example == "brand_x":
        os.system("python examples/brand_x/run.py")
        return

    if not args.input:
        print("ERROR: Provide --input CSV path or --example brand_alpha / brand_x")
        parser.print_help()
        sys.exit(1)

    channels = load_channels_from_csv(args.input)
    total_spend = sum(c.spend for c in channels)
    os.makedirs(args.output, exist_ok=True)

    channel_outputs = apply_portfolio(channels)
    posture_outputs = assign_portfolio_postures(channel_outputs)
    loa_entries     = generate_portfolio_loa(
        channel_outputs, posture_outputs,
        period=args.period, analyst="DTC-MAIRF Toolkit"
    )

    print_summary(channel_outputs, posture_outputs, total_spend,
                  brand_name=args.brand, period=args.period)

    csv_path = os.path.join(args.output, "triangulation_summary.csv")
    loa_path = os.path.join(args.output, "ledger_of_assumptions.txt")

    generate_csv(channel_outputs, posture_outputs, total_spend, output_path=csv_path)
    write_loa_report(loa_entries, output_path=loa_path)


if __name__ == "__main__":
    main()
