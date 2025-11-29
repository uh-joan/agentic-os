---
name: extract_company_dividend_history
description: >
  Extract dividend payment history, payout ratios, dividend growth, and
  sustainability analysis from SEC EDGAR filings. Analyzes cash flow
  and net income to assess dividend policy and shareholder returns.
---
# extract_company_dividend_history


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Which companies are working on company dividend history?`
2. `@agent-pharma-search-specialist Show me the competitive landscape for company dividend history`
3. `@agent-pharma-search-specialist Who's developing company dividend history therapies?`


## Purpose

Analyzes dividend payment history and sustainability by extracting quarterly dividend payments, operating cash flow, and net income from SEC EDGAR XBRL data. Calculates payout ratios and dividend growth trends.

## Usage

```python
from .claude.skills.company_dividend_history.scripts.extract_company_dividend_history import extract_company_dividend_history

# Get 12 quarters of dividend history for Medtronic
result = extract_company_dividend_history(ticker="MDT", quarters=12)
print(result['summary'])
```

**Command Line**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-dividend-history/scripts/extract_company_dividend_history.py MDT 12
```

## Returns

```python
{
    'company_name': str,
    'quarters_analyzed': int,
    'data': [
        {
            'date': 'YYYY-MM-DD',
            'dividends': int,  # Dividend payments
            'operating_cf': int,  # Operating cash flow
            'net_income': int,  # Net income
            'payout_ratio_ocf': float,  # Dividends / Operating CF (%)
            'payout_ratio_ni': float  # Dividends / Net Income (%)
        }
    ],
    'totals': {
        'total_dividends': int,
        'total_operating_cf': int,
        'total_net_income': int,
        'avg_payout_ratio_ocf': float,
        'avg_payout_ratio_ni': float,
        'yoy_growth': float  # Year-over-year dividend growth (%)
    },
    'sustainability': str,  # Dividend sustainability assessment
    'policy': str,  # Dividend policy classification
    'summary': str
}
```

## Use Cases

- **Dividend sustainability**: Is company paying more than it generates in cash flow?
- **Income investing**: Assess dividend reliability and growth potential
- **Shareholder returns**: Compare dividends to buybacks for total shareholder return
- **Capital allocation**: Understand balance between growth investments and shareholder payouts
- **Dividend growth**: Track dividend increases over time

## Key Metrics

**Payout Ratio (Operating Cash Flow)** = Dividends / Operating CF
- <40%: Growth-oriented (retaining cash for investments)
- 40-60%: Balanced (growth + income)
- 60-80%: Income-oriented (mature company)
- >80%: High payout (limited flexibility)
- >100%: Unsustainable (paying more than generating)

**Payout Ratio (Net Income)** = Dividends / Net Income
- <50%: Growth-oriented
- 50-70%: Balanced
- 70-90%: Income-oriented
- >90%: Potential dividend trap

**Dividend Growth**:
- >10% YoY: Strong growth (shareholder-friendly)
- 5-10% YoY: Moderate growth (stable)
- 0-5% YoY: Flat (maintaining commitment)
- <0% YoY: Declining (potential stress)

## Example Output

```
MEDTRONIC PLC - DIVIDEND ANALYSIS
================================================================================
Data Period: 12 quarters (3 years)

QUARTERLY DIVIDEND PAYMENTS:
| Quarter    | Dividends | Op CF    | Net Inc  | Payout (OCF) | Payout (NI) |
|------------|-----------|----------|----------|--------------|-------------|
| 2025-01-31 |    $687M  |  $1088M  |   $945M  |          63% |         73% |
| 2024-10-31 |    $679M  |  $1129M  |   $982M  |          60% |         69% |
| 2024-07-31 |    $675M  |  $1005M  |   $901M  |          67% |         75% |
| 2024-04-30 |    $658M  |   $986M  |   $834M  |          67% |         79% |

DIVIDEND METRICS (Quarterly Average):
  Dividend Payment: $675M
  Operating Cash Flow: $1,052M
  Net Income: $915M

  Payout Ratio (OCF): 64%
  Payout Ratio (Net Income): 74%

  Annual Dividend Rate: $2,700M

  YoY Growth: +2.8%

DIVIDEND SUSTAINABILITY: ✓  Moderate payout (sustainable)
DIVIDEND POLICY: Income-oriented (mature)

KEY INSIGHTS:
- Moderate dividend growth (2.8% YoY) = stable policy
- Payout ratio 64% leaves room for growth investments
- Dividend payments very consistent (volatility: 3.2%)
```

## Data Source

SEC EDGAR XBRL Concepts:
- `PaymentsOfDividends` - Quarterly dividend payments
- `NetCashProvidedByUsedInOperatingActivities` - Operating cash flow
- `NetIncomeLoss` - Net income

## Related Skills

- **extract_company_capex_allocation**: Analyze CapEx and buybacks (complete capital allocation picture)
- **get_company_rd_spending**: R&D spending trends
- **extract_company_acquisitions**: M&A activity and cash deployment