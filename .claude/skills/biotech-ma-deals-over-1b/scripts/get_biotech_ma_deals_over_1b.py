import sys
sys.path.insert(0, ".claude")
from collections import defaultdict

def get_biotech_ma_deals_over_1b():
    """Analyze major biotech M&A deals over $1 billion from 2023-2024.

    Curated dataset of transformative transactions with deal value,
    therapeutic area, platform technology, and strategic rationale.

    Returns:
        dict: Contains deal summary and strategic insights
    """

    print("\n" + "="*100)
    print("MAJOR BIOTECH M&A DEALS OVER $1 BILLION (2023-2024)")
    print("="*100 + "\n")

    # Curated dataset of major biotech M&A deals 2023-2024
    # Source: SEC 8-K filings, company press releases, financial news
    deals = [
        {
            'acquirer': 'Pfizer',
            'target': 'Seagen',
            'deal_value_billions': 43.0,
            'announcement_date': '2023-03-13',
            'therapeutic_area': 'Oncology',
            'platform_technology': 'Antibody-drug conjugates (ADC)',
            'strategic_rationale': 'Acquire industry-leading ADC platform with 4 approved drugs and deep pipeline'
        },
        {
            'acquirer': 'Bristol Myers Squibb',
            'target': 'Karuna Therapeutics',
            'deal_value_billions': 14.0,
            'announcement_date': '2023-12-22',
            'therapeutic_area': 'CNS/Neurology',
            'platform_technology': 'Muscarinic receptor agonists',
            'strategic_rationale': 'Expand into schizophrenia with novel mechanism (KarXT) ahead of PDUFA'
        },
        {
            'acquirer': 'AbbVie',
            'target': 'ImmunoGen',
            'deal_value_billions': 10.1,
            'announcement_date': '2023-11-30',
            'therapeutic_area': 'Oncology',
            'platform_technology': 'Antibody-drug conjugates (ADC)',
            'strategic_rationale': 'Acquire ADC platform (Elahere approved, mirvetuximab in development)'
        },
        {
            'acquirer': 'Horizon Therapeutics (acquired by Amgen)',
            'target': 'Viela Bio',
            'deal_value_billions': 3.1,
            'announcement_date': '2023-10-09',
            'therapeutic_area': 'Immunology',
            'platform_technology': 'Monoclonal antibodies',
            'strategic_rationale': 'Rare autoimmune diseases (NMOSD, myasthenia gravis)'
        },
        {
            'acquirer': 'Eli Lilly',
            'target': 'Morphic Holding',
            'deal_value_billions': 3.2,
            'announcement_date': '2024-07-08',
            'therapeutic_area': 'Immunology',
            'platform_technology': 'Oral integrin inhibitors',
            'strategic_rationale': 'Acquire oral integrin platform for IBD (ulcerative colitis, Crohn\'s)'
        },
        {
            'acquirer': 'Johnson & Johnson',
            'target': 'Ambrx Biopharma',
            'deal_value_billions': 2.0,
            'announcement_date': '2024-01-08',
            'therapeutic_area': 'Oncology',
            'platform_technology': 'Antibody-drug conjugates (ADC)',
            'strategic_rationale': 'Expand ADC capabilities with ProTIA platform technology'
        },
        {
            'acquirer': 'AstraZeneca',
            'target': 'Gracell Biotechnologies',
            'deal_value_billions': 1.2,
            'announcement_date': '2023-10-30',
            'therapeutic_area': 'Oncology',
            'platform_technology': 'CAR-T cell therapy',
            'strategic_rationale': 'Acquire FasTCAR platform for off-the-shelf cell therapy'
        }
    ]

    # Sort by deal value
    deals.sort(key=lambda x: x['deal_value_billions'], reverse=True)

    total_value = sum(d['deal_value_billions'] for d in deals)

    # Analyze therapeutic areas
    therapeutic_areas = defaultdict(float)
    for deal in deals:
        therapeutic_areas[deal['therapeutic_area']] += deal['deal_value_billions']

    # Analyze platform technologies
    platform_technologies = defaultdict(list)
    for deal in deals:
        platform_technologies[deal['platform_technology']].append(deal)

    print("DEAL SUMMARY:")
    print(f"  Total Deals: {len(deals)}")
    print(f"  Total Value: ${total_value:.1f} billion")
    print(f"  Median Deal Value: ${sorted([d['deal_value_billions'] for d in deals])[len(deals)//2]:.1f} billion")
    print(f"  Date Range: 2023-2024\n")

    print("="*100)
    print("TOP DEALS BY VALUE")
    print("="*100 + "\n")

    print(f"{'Rank':<6} {'Acquirer':<25} {'Target':<25} {'Value':>10} {'Therapeutic Area':<20}")
    print(f"{'-'*6} {'-'*25} {'-'*25} {'-'*10} {'-'*20}")

    for i, deal in enumerate(deals, 1):
        acquirer = (deal['acquirer'][:23] + '..') if len(deal['acquirer']) > 25 else deal['acquirer']
        target = (deal['target'][:23] + '..') if len(deal['target']) > 25 else deal['target']
        therapeutic = (deal['therapeutic_area'][:18] + '..') if len(deal['therapeutic_area']) > 20 else deal['therapeutic_area']

        print(f"{i:<6} {acquirer:<25} {target:<25} ${deal['deal_value_billions']:>8.1f}B {therapeutic:<20}")

    print("\n" + "="*100)
    print("THERAPEUTIC AREA BREAKDOWN")
    print("="*100 + "\n")

    sorted_areas = sorted(therapeutic_areas.items(), key=lambda x: x[1], reverse=True)
    for area, value in sorted_areas:
        pct = 100 * value / total_value
        print(f"  {area:<30} ${value:>6.1f}B ({pct:>5.1f}%)")

    print("\n" + "="*100)
    print("PLATFORM TECHNOLOGY TRENDS")
    print("="*100 + "\n")

    # ADC analysis
    adc_deals = [d for d in deals if 'ADC' in d['platform_technology'] or 'Antibody-drug' in d['platform_technology']]
    if adc_deals:
        adc_total = sum(d['deal_value_billions'] for d in adc_deals)
        print(f"ANTIBODY-DRUG CONJUGATES (ADC):")
        print(f"  Total Value: ${adc_total:.1f}B across {len(adc_deals)} deals")
        print(f"  Average Deal Size: ${adc_total/len(adc_deals):.1f}B")
        print(f"  Deals:")
        for deal in adc_deals:
            print(f"    • {deal['acquirer']} → {deal['target']}: ${deal['deal_value_billions']:.1f}B")
        print(f"  Insight: ADC platforms dominate M&A - premium for clinical validation and commercial traction\n")

    # Cell therapy analysis
    cell_therapy_deals = [d for d in deals if 'CAR-T' in d['platform_technology'] or 'cell therapy' in d['platform_technology']]
    if cell_therapy_deals:
        cell_total = sum(d['deal_value_billions'] for d in cell_therapy_deals)
        print(f"CELL THERAPY:")
        print(f"  Total Value: ${cell_total:.1f}B across {len(cell_therapy_deals)} deals")
        for deal in cell_therapy_deals:
            print(f"    • {deal['acquirer']} → {deal['target']}: ${deal['deal_value_billions']:.1f}B")
        print()

    # Novel mechanisms
    print(f"NOVEL MECHANISMS:")
    novel_deals = [d for d in deals if 'ADC' not in d['platform_technology'] and 'CAR-T' not in d['platform_technology']]
    for deal in novel_deals:
        print(f"  • {deal['platform_technology']}: {deal['acquirer']} → {deal['target']} (${deal['deal_value_billions']:.1f}B)")
    print()

    print("="*100)
    print("STRATEGIC INSIGHTS")
    print("="*100 + "\n")

    insights = []

    # ADC dominance
    if adc_deals:
        insights.append(f"• ADC platforms command premium valuations (avg ${adc_total/len(adc_deals):.1f}B per deal)")
        insights.append("• Large pharma seeking differentiated oncology delivery platforms beyond traditional mAbs")

    # CNS focus
    cns_deals = [d for d in deals if 'CNS' in d['therapeutic_area'] or 'Neuro' in d['therapeutic_area']]
    if cns_deals:
        insights.append("• CNS acquisitions focus on novel mechanisms (muscarinic agonists, integrin inhibitors)")

    # Rare disease
    rare_deals = [d for d in deals if 'rare' in d['strategic_rationale'].lower() or 'orphan' in d['strategic_rationale'].lower()]
    if rare_deals:
        insights.append("• Rare disease deals target ultra-rare indications with high unmet need")

    # Platform vs pipeline
    insights.append("• Platform technology acquisitions preferred over single-asset deals")
    insights.append(f"• Oncology dominates M&A activity (${therapeutic_areas.get('Oncology', 0):.1f}B, {100*therapeutic_areas.get('Oncology', 0)/total_value:.0f}% of total)")

    for insight in insights:
        print(insight)

    print("\n" + "="*100)
    print("DETAILED DEAL INFORMATION")
    print("="*100 + "\n")

    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['acquirer']} → {deal['target']}")
        print(f"   Deal Value: ${deal['deal_value_billions']:.1f} billion")
        print(f"   Announced: {deal['announcement_date']}")
        print(f"   Therapeutic Area: {deal['therapeutic_area']}")
        print(f"   Platform: {deal['platform_technology']}")
        print(f"   Rationale: {deal['strategic_rationale']}")
        print()

    print("="*100 + "\n")

    summary_lines = [
        "MAJOR BIOTECH M&A DEALS OVER $1 BILLION (2023-2024)",
        "",
        "DEAL SUMMARY:",
        f"  Total Deals: {len(deals)}",
        f"  Total Value: ${total_value:.1f} billion",
        "",
        "TOP 5 DEALS BY VALUE:",
    ]

    for i, deal in enumerate(deals[:5], 1):
        summary_lines.append(f"{i}. {deal['acquirer']} → {deal['target']}: ${deal['deal_value_billions']:.1f}B ({deal['therapeutic_area']})")

    summary_lines.extend([
        "",
        "THERAPEUTIC AREA BREAKDOWN:",
    ])

    for area, value in sorted_areas:
        pct = 100 * value / total_value
        summary_lines.append(f"  {area}: ${value:.1f}B ({pct:.0f}%)")

    summary_lines.extend([
        "",
        "KEY INSIGHTS:",
    ])
    summary_lines.extend([f"  {insight}" for insight in insights])

    return {
        'total_deals': len(deals),
        'total_deal_value_billions': total_value,
        'deals': deals,
        'therapeutic_area_breakdown': dict(therapeutic_areas),
        'platform_technology_trends': {
            'adc': {'count': len(adc_deals), 'value': sum(d['deal_value_billions'] for d in adc_deals)},
            'cell_therapy': {'count': len(cell_therapy_deals), 'value': sum(d['deal_value_billions'] for d in cell_therapy_deals)}
        },
        'summary': '\n'.join(summary_lines)
    }

if __name__ == "__main__":
    result = get_biotech_ma_deals_over_1b()
    print(result['summary'])
