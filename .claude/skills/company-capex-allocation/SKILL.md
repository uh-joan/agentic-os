---
name: extract_company_capex_allocation
description: >
  Extract capital allocation patterns: CapEx, operating cash flow, dividends,
  share buybacks, and free cash flow from SEC EDGAR filings. Analyzes how
  companies deploy cash between growth investments and shareholder returns.
---
# extract_company_capex_allocation


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Which companies are working on company capex allocation?`
2. `@agent-pharma-search-specialist Show me the competitive landscape for company capex allocation`
3. `@agent-pharma-search-specialist Who's developing company capex allocation therapies?`


## Purpose

Analyzes capital allocation strategy by extracting quarterly CapEx, operating cash flow, dividends, and buybacks from SEC EDGAR XBRL data. Identifies whether company prioritizes growth investments vs shareholder returns.

## Usage

```python
from .claude.skills.company_capex_allocation.scripts.extract_company_capex_allocation import extract_company_capex_allocation

# Get 8 quarters of capital allocation for Medtronic
result = extract_company_capex_allocation(ticker="MDT", quarters=8)
print(result['summary'])
```

**Command Line**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-capex-allocation/scripts/extract_company_capex_allocation.py MDT 8
```

## Returns

```python
{
    'company_name': str,
    'quarters_analyzed': int,
    'data': [
        {
            'date': 'YYYY-MM-DD',
            'capex': int,  # Property, plant & equipment investments
            'operating_cf': int,  # Operating cash flow
            'dividends': int,  # Dividend payments
            'buybacks': int,  # Share repurchases
            'free_cash_flow': int,  # Operating CF - CapEx
            'capex_intensity': float,  # CapEx as % of revenue
            'fcf_margin': float  # FCF as % of revenue
        }
    ],
    'totals': {
        'total_capex': int,
        'total_operating_cf': int,
        'avg_capex_intensity': float,
        'avg_fcf_margin': float
    },
    'allocation_priorities': str,  # Growth vs Returns analysis
    'summary': str
}
```

## Use Cases

- **Growth vs Harvest**: Is company investing in growth (high CapEx) or harvesting cash?
- **Capital intensity**: Compare CapEx % across competitors
- **Shareholder returns**: Dividend + buyback sustainability analysis
- **Financial flexibility**: Free cash flow available for M&A or debt reduction
- **Strategy shifts**: Changes in capital allocation signal strategic pivots

## Key Metrics

**CapEx Intensity** = CapEx / Revenue
- <3%: Asset-light business
- 3-5%: Moderate capital needs
- 5-8%: Capital-intensive (manufacturing)
- >8%: Heavy infrastructure (utilities, telecom)

**FCF Margin** = (Operating CF - CapEx) / Revenue
- <5%: Limited financial flexibility
- 5-10%: Moderate cash generation
- 10-15%: Strong cash generation
- >15%: Excellent cash generator

**Payout Ratio** = (Dividends + Buybacks) / Operating CF
- <30%: Growth-oriented (retaining cash)
- 30-50%: Balanced (growth + returns)
- 50-70%: Returns-oriented (mature)
- >70%: Unsustainable (returning more than generating)

## Example Output

```
MEDTRONIC PLC - CAPITAL ALLOCATION ANALYSIS
===========================================
Data Period: 8 quarters (2 years)

CAPITAL ALLOCATION BREAKDOWN (Quarterly Avg):
  Operating Cash Flow: $1,125M
  CapEx: $(500M)          (44% of OCF)
  Free Cash Flow: $625M   (56% of OCF)

  Dividends: $(550M)      (49% of OCF)
  Buybacks: $(350M)       (31% of OCF)

  Total to Shareholders: $(900M) (80% of OCF)

ALLOCATION PRIORITY: Growth-Oriented with Returns
  - CapEx: 44% (investing in growth)
  - Shareholders: 80% (also returning cash)
  - Funding gap: Financed via debt/asset sales

CAPITAL INTENSITY:
  - Average CapEx: 6.1% of revenue
  - Industry: Medtech (typical 4-6%)
  - Assessment: Above average (growth investments)

FREE CASH FLOW:
  - Average FCF Margin: 7.3%
  - Trend: Stable
  - Sustainability: Good cash generation

KEY INSIGHTS:
- Recent buyback spike in Q2 2024 ($2.5B) = opportunistic
- CapEx increasing (5% → 6.5%) = scaling Diabetes manufacturing
- Payout ratio 80% = returning more than FCF (debt-funded)
```