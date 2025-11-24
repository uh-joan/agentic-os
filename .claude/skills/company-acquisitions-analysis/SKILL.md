---
name: extract_company_acquisitions
description: >
  Extract M&A history, acquisition spending, goodwill trends, and integration
  impacts from SEC EDGAR filings. Identifies major acquisitions, tracks
  goodwill changes, and highlights potential write-down risks.
---

# extract_company_acquisitions

## Purpose

Analyzes acquisition activity and integration success by extracting M&A cash payments, goodwill trends, and impairment history from SEC EDGAR XBRL data. Essential for understanding segment volatility from acquisitions.

## Usage

```python
from .claude.skills.company_acquisitions_analysis.scripts.extract_company_acquisitions import extract_company_acquisitions

# Get last 3 years of M&A activity for Medtronic
result = extract_company_acquisitions(ticker="MDT", periods=12)
print(result['summary'])
```

**Command Line**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-acquisitions-analysis/scripts/extract_company_acquisitions.py MDT 12
```

## Returns

```python
{
    'company_name': str,
    'acquisition_payments': [
        {'date': 'YYYY-MM-DD', 'amount': int, 'form': '10-K/10-Q'}
    ],
    'goodwill_trend': [
        {'date': 'YYYY-MM-DD', 'goodwill': int, 'change_pct': float}
    ],
    'impairments': [
        {'date': 'YYYY-MM-DD', 'amount': int}
    ],
    'summary': str  # Formatted output
}
```

## Use Cases

- Identify major acquisition years (explain segment volatility)
- Track goodwill growth (acquisition frequency indicator)
- Spot impairment risks (goodwill not generating returns)
- Analyze integration success (revenue synergies vs cost)
- Compare acquisition intensity across competitors

## Key Insights

- **Large spike in acquisition spend** = integration period ahead (volatility)
- **Goodwill growing faster than revenue** = acquisition-heavy growth
- **Goodwill stable** = organic growth period
- **Impairments** = acquisition integration failed

## Example Output

```
ABBOTT LABORATORIES - M&A ANALYSIS
==================================
Data Period: 12 quarters (3 years)

ACQUISITION CASH PAYMENTS:
  2023-Q4: $1,867M  🚨 MAJOR ACQUISITION
  2024-Q2: $211M    Bolt-on
  2025-Q1: $98M     Tuck-in

GOODWILL TREND:
  2023-Q1: $40,986M
  2025-Q2: $42,007M
  Change: +$1,021M (+2.5%)

IMPAIRMENTS: None (healthy)

KEY INSIGHT: $1.9B acquisition in FY 2023 explains
Medical Surgical segment volatility in 2024.
```
