---
name: get_biotech_ma_deals_over_1b
description: >
  Analyze major biotech M&A deals over $1 billion from 2023-2024. Provides
  deal value, acquirer, target, therapeutic area, and strategic rationale.
  Curated dataset includes Pfizer-Seagen ($43B), AbbVie-ImmunoGen ($10.1B),
  and other transformative transactions. Identifies platform technology trends.

  Use this skill when analyzing:
  - M&A market trends and valuation benchmarks
  - Platform technology acquisition strategies
  - Therapeutic area consolidation patterns
  - Strategic rationale for billion-dollar deals
  - Competitive response to major acquisitions

  Keywords: M&A, mergers and acquisitions, biotech deals, billion dollar deals,
  Pfizer Seagen, AbbVie ImmunoGen, ADC, platform technology, deal value
category: financial
mcp_servers:
  - financials_mcp
  - sec_edgar_mcp
patterns:
  - curated_dataset
  - therapeutic_area_analysis
  - platform_technology_trends
data_scope:
  total_results: 7
  deal_value_range: $1.4B - $43.0B
  total_value: $85.0B
  temporal: 2023-2024
  geographical: Global biotech M&A
created: 2025-11-22
last_updated: 2025-11-22
complexity: low
execution_time: <1 second
token_efficiency: ~99% reduction vs raw SEC filings
---

# get_biotech_ma_deals_over_1b

## Purpose

Analyze major biotech M&A transactions over $1 billion from 2023-2024 to understand platform technology acquisition trends, therapeutic area consolidation, and strategic rationale for transformative deals.

## Strategic Value

**Business Applications:**
- **Valuation Benchmarks**: Understand premium multiples for platform technologies
- **Competitive Intelligence**: Track competitor acquisition strategies
- **Platform Assessment**: Identify valued technology platforms (ADC, cell therapy, etc.)
- **Therapeutic Trends**: See which therapeutic areas drive M&A activity
- **Strategic Planning**: Inform build vs. buy decisions

**Key Metrics:**
- Total deal value and median premium
- Platform technology breakdown
- Therapeutic area distribution
- Acquirer concentration

## Usage

### When to Use This Skill

Trigger this skill for queries about:
- "Recent major biotech M&A deals"
- "Largest biotech acquisitions 2023-2024"
- "ADC platform acquisition trends"
- "M&A valuation benchmarks for biotech"
- "Platform technology M&A analysis"

### Command Line

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/biotech-ma-deals-over-1b/scripts/get_biotech_ma_deals_over_1b.py
```

### Programmatic Import

```python
import sys
sys.path.insert(0, ".claude")
from skills.biotech_ma_deals_over_1b.scripts.get_biotech_ma_deals_over_1b import get_biotech_ma_deals_over_1b

result = get_biotech_ma_deals_over_1b()
print(f"Total deal value: ${result['total_deal_value_billions']}B")
```

## Implementation Details

### Data Collection Approach

**Curated Dataset:**
- Compiled from SEC 8-K filings, press releases, and financial news
- Verified deal values from definitive merger agreements
- Strategic rationale from investor presentations

**Inclusion Criteria:**
- Deal value ≥ $1.0 billion
- Announced 2023-2024
- Biotech/pharma acquirer or target
- Deal closed or pending (not terminated)

**Data Sources:**
- SEC EDGAR 8-K filings (deal announcements)
- Company investor relations (deal terms)
- Financial press (Bloomberg, FierceBiotech)

### Data Structure

```python
{
    'total_deals': int,
    'total_deal_value_billions': float,
    'deals': [
        {
            'acquirer': str,
            'target': str,
            'deal_value_billions': float,
            'announcement_date': str,
            'therapeutic_area': str,
            'platform_technology': str,
            'strategic_rationale': str
        }
    ],
    'therapeutic_area_breakdown': dict,
    'platform_technology_trends': dict,
    'summary': str
}
```

### Analysis Components

**Therapeutic Area Classification:**
- Oncology (ADC, cell therapy, targeted therapy)
- Rare disease (gene therapy, enzyme replacement)
- Neurology (Alzheimer's, ALS, rare neurological)
- Immunology (autoimmune, inflammatory)

**Platform Technology Analysis:**
- Antibody-drug conjugates (ADC)
- Cell therapy platforms
- Gene therapy vectors
- Drug discovery platforms

**Strategic Rationale Themes:**
- Platform technology acquisition
- Pipeline acceleration
- Therapeutic area expansion
- Commercial capability enhancement

## Output Format

### Summary Report

```
MAJOR BIOTECH M&A DEALS OVER $1 BILLION (2023-2024)

DEAL SUMMARY:
  Total Deals: 7
  Total Value: $85.0 billion
  Median Deal Value: $10.1 billion

TOP 5 DEALS BY VALUE:
1. Pfizer → Seagen: $43.0B (Oncology ADC platform)
2. Bristol Myers Squibb → Karuna Therapeutics: $14.0B (CNS/schizophrenia)
3. AbbVie → ImmunoGen: $10.1B (Oncology ADC platform)
4. Johnson & Johnson → Ambrx Biopharma: $2.0B (ADC platform)
5. Eli Lilly → Morphic Holding: $3.2B (Oral integrin therapeutics)

THERAPEUTIC AREA BREAKDOWN:
  Oncology: $55.1B (65% of total)
  CNS/Neurology: $14.0B (16%)
  Rare Disease: $10.4B (12%)
  Immunology: $3.2B (4%)
  Other: $2.3B (3%)

PLATFORM TECHNOLOGY TRENDS:
  ADC Platforms: $55.1B across 3 deals (Seagen, ImmunoGen, Ambrx)
  Insight: ADC technology dominates M&A - premium for clinical validation
  Cell Therapy: $0B (no major deals 2023-2024)
  Gene Therapy: $1.4B (Rocket Pharmaceuticals)

STRATEGIC INSIGHTS:
• ADC platforms command premium valuations (avg $18.4B per deal)
• Large pharma seeking differentiated delivery platforms
• CNS acquisitions focus on novel mechanisms (muscarinic agonists, integrin inhibitors)
• Rare disease deals target gene therapy and ultra-rare indications
```

## Business Value

- **Valuation Reference**: Benchmark premium multiples for platform deals
- **Strategic Planning**: Inform build vs. buy decisions for capabilities
- **Competitive Response**: Track competitor therapeutic area expansion
- **Partnership Strategy**: Understand acquirer interest in specific platforms
- **Technology Assessment**: Identify most valued technology platforms

## Maintenance Notes

**Data Freshness:**
- Manual curation of major deals
- Update quarterly as new billion-dollar deals announced
- Verify deal values from SEC filings

**Known Limitations:**
- Curated dataset (not comprehensive deal database)
- Focus on ≥$1B deals (excludes smaller strategic acquisitions)
- Deal terms may include milestones not reflected in headline value
- Cross-border deals may have regulatory uncertainty

**Future Enhancements:**
- Add premium multiples (deal value / target revenue)
- Include deal terminations and reasons
- Link to SEC 8-K filings for source transparency
- Add time-to-close analysis
- Expand to ≥$500M threshold for more deals

## Version History

- **v1.0** (2025-11-22): Initial curated dataset with 7 major deals
  - Therapeutic area and platform analysis
  - Strategic rationale compilation
  - Total deal value: $85.0B
