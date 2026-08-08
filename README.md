# DTC-MAIRF: Marketing Accounting Investment Risk Framework

**An open-source Python toolkit for governing marketing capital allocation under measurement uncertainty in Direct-to-Consumer brands.**

---

## Overview

The DTC-MAIRF (DTC Marketing Accounting Investment Risk Framework) is a governance architecture that produces systematic, auditable, and financially accountable capital allocation decisions despite irreducible attribution measurement uncertainty.

This toolkit operationalises the framework proposed in:

> Hosahally, S., Sukumar, A., & Bharadwaj, M. (2025). *Attribution Risk: Formalising a Governance Framework for Marketing Capital Allocation under Measurement Uncertainty.*

### The core problem

Platform-reported ROAS figures systematically diverge from true incremental channel contribution. Last-touch attribution simultaneously **overvalues** conversion-stage channels (capturing organic demand) and **undervalues** upper-funnel channels (missing cross-channel contribution) — in the same portfolio, at the same time, by magnitudes that reverse apparent channel performance rankings entirely.

This is not a measurement problem that can be solved. It is a governance problem that must be managed.

---

## What the toolkit does

Given channel-level spend, platform ROAS, and available attribution multipliers, the toolkit:

1. **Applies multipliers** (BAC / MDIC / IDIC) with tier-appropriate scepticism factors
2. **Calculates aaROAS** (Advanced Attribution ROAS) using the lower bound for governance decisions
3. **Assigns governance postures** (CRITICAL / STRATEGIC / SPECULATIVE / EXPLORATORY / VERIFIED)
4. **Flags CFO escalation** where concentration thresholds are breached
5. **Generates the Triangulation Summary Sheet** as a CSV
6. **Produces the Ledger of Assumptions** as an auditable governance record

---

## Evidence tiers

| Tier | Source | Scepticism Factor | Capital Authority |
|------|--------|-------------------|-------------------|
| **Tier 1 — BAC** | Industry benchmark multipliers (M², Measured.com) | 10–40% | RESTRICTED — CFO approval >20% budget |
| **Tier 2 — MDIC** | Brand-specific MMM statistical regression | 5–15% | CONDITIONAL — Judgement Override |
| **Tier 3 — IDIC** | Geo-test / RCT causal proof | 0–5% | UNRESTRICTED — CFO sign-off >30% budget |

---

## Five governance postures

| Posture | Trigger | Governance Action |
|---------|---------|-------------------|
| **CRITICAL** | Budget >40% + Tier 1 BAC only | MANDATORY HOLD — IDIC validation within 90 days |
| **STRATEGIC** | Budget >30% + Tier 3 IDIC proof | CONFIDENT SCALE — CFO sign-off required |
| **SPECULATIVE** | Multiplier Gap >50% at Tier 2 MDIC | JUDGEMENT OVERRIDE — joint CMO/CFO review |
| **EXPLORATORY** | Budget <20% + Tier 1 BAC | AUTONOMOUS TEST — Safe Harbour applies |
| **VERIFIED** | Small footprint + Tier 3 IDIC | OPTIMISE / SCALE — quarterly Finance review |

---

## Installation

```bash
git clone https://github.com/[your-username]/dtc-mairf.git
cd dtc-mairf
pip install -r requirements.txt
```

No external dependencies required beyond Python 3.10+.

---

## Quick start

### Run the Brand Alpha example

```bash
python run_framework.py --example brand_alpha
```

### Run the Brand X example

```bash
python run_framework.py --example brand_x
```

### Run with your own data

1. Copy `data/channel_input_template.csv` and fill in your channel data
2. Run:

```bash
python run_framework.py \
  --input data/my_channels.csv \
  --brand "My Brand" \
  --period "Q4 2024" \
  --output outputs/
```

Outputs:
- `outputs/triangulation_summary.csv` — Triangulation Summary Sheet
- `outputs/ledger_of_assumptions.txt` — Ledger of Assumptions audit record

---

## Repository structure

```
dtc-mairf/
├── README.md
├── run_framework.py          — Main CLI entry point
├── data/
│   └── channel_input_template.csv
├── core/
│   ├── multipliers.py        — BAC/MDIC/IDIC multiplier engine
│   ├── posture.py            — Decision Matrix posture assignment
│   └── loa.py                — Ledger of Assumptions generator
├── outputs/
│   └── triangulation_sheet.py — CSV and console report generator
└── examples/
    ├── brand_alpha/run.py    — Brand Alpha worked example
    └── brand_x/run.py        — Brand X worked example
```

---

## Input format

| Column | Type | Description |
|--------|------|-------------|
| `channel_name` | string | Channel identifier |
| `spend` | float | Media spend in currency units |
| `lt_roas` | float | Platform last-touch ROAS |
| `evidence_tier` | string | BAC / MDIC / IDIC |
| `multiplier` | float | aaRev ÷ LT Rev (leave blank if unavailable) |
| `scepticism_override` | float | Override default scepticism lower bound (optional) |
| `notes` | string | Free text notes for Ledger of Assumptions |

---

## Citation

If you use this toolkit in academic research, please cite:

```
Hosahally, S., Sukumar, A., & Bharadwaj, M. (2025). Attribution Risk:
Formalising a Governance Framework for Marketing Capital Allocation under
Measurement Uncertainty. [Journal TBC].
```

---

## Licence

MIT Licence — free to use, modify, and distribute with attribution.

---

## Contributors

- **Shashank Hosahally** — BCU Business School / M-Squared Attribution
- **Prof. Arun Sukumar** — Birmingham City University
- **Madan Bharadwaj** — M-Squared Attribution
