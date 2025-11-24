import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_facts

def extract_company_capex_allocation(ticker: str, quarters: int = 8) -> dict:
    """Extract capital allocation: CapEx, cash flow, dividends, buybacks.

    Analyzes how company deploys cash between growth investments (CapEx)
    and shareholder returns (dividends + buybacks). Calculates free cash
    flow and capital intensity metrics.

    Args:
        ticker: Company ticker symbol (e.g., "MDT", "ABBV", "PFE")
        quarters: Number of recent quarters to analyze (default 8 = 2 years)

    Returns:
        dict: Capital allocation data, metrics, strategic assessment
    """

    print(f"Fetching SEC EDGAR data for {ticker}...")
    result = get_company_facts(cik_or_ticker=ticker)

    if not result or 'error' in result:
        return {
            'error': f"Failed to fetch data for {ticker}",
            'summary': "No data available"
        }

    company_name = result.get('entityName', ticker)
    facts = result.get('facts', {})
    us_gaap = facts.get('us-gaap', {})

    # Extract CapEx
    capex_concept = us_gaap.get('PaymentsToAcquirePropertyPlantAndEquipment', {})
    capex_units = capex_concept.get('units', {})
    capex_data = capex_units.get('USD', [])

    # Extract Operating Cash Flow
    ocf_concept = us_gaap.get('NetCashProvidedByUsedInOperatingActivities', {})
    ocf_units = ocf_concept.get('units', {})
    ocf_data = ocf_units.get('USD', [])

    # Extract Dividends
    div_concept = us_gaap.get('PaymentsOfDividends', {})
    div_units = div_concept.get('units', {})
    div_data = div_units.get('USD', [])

    # Extract Buybacks
    buyback_concept = us_gaap.get('PaymentsForRepurchaseOfCommonStock', {})
    buyback_units = buyback_concept.get('units', {})
    buyback_data = buyback_units.get('USD', [])

    # Extract Revenue for intensity calculations
    revenue_concept = us_gaap.get('RevenueFromContractWithCustomerExcludingAssessedTax', {})
    if not revenue_concept:
        revenue_concept = us_gaap.get('Revenues', {})
    revenue_units = revenue_concept.get('units', {}) if revenue_concept else {}
    revenue_data = revenue_units.get('USD', [])

    # Build lookup dictionaries by end date (quarterly 10-Q only)
    def build_quarterly_lookup(data):
        result = {}
        for item in data:
            if item.get('form') == '10-Q':  # Only quarterly filings
                end_date = item.get('end', '')
                value = abs(item.get('val', 0))  # Absolute value (payments are negative)
                if end_date not in result or item.get('filed', '') > result[end_date].get('filed', ''):
                    result[end_date] = {'value': value, 'filed': item.get('filed', '')}
        return result

    capex_lookup = build_quarterly_lookup(capex_data)
    ocf_lookup = build_quarterly_lookup(ocf_data)
    div_lookup = build_quarterly_lookup(div_data)
    buyback_lookup = build_quarterly_lookup(buyback_data)
    revenue_lookup = build_quarterly_lookup(revenue_data)

    # Get all dates and sort
    all_dates = set(list(capex_lookup.keys()) + list(ocf_lookup.keys()))
    sorted_dates = sorted(all_dates, reverse=True)[:quarters]

    # Combine data by quarter
    quarterly_data = []
    for end_date in sorted_dates:
        capex_val = capex_lookup.get(end_date, {}).get('value', 0)
        ocf_val = ocf_lookup.get(end_date, {}).get('value', 0)
        div_val = div_lookup.get(end_date, {}).get('value', 0)
        buyback_val = buyback_lookup.get(end_date, {}).get('value', 0)
        revenue_val = revenue_lookup.get(end_date, {}).get('value', 0)

        fcf = ocf_val - capex_val

        quarter_record = {
            'date': end_date,
            'capex': capex_val,
            'operating_cf': ocf_val,
            'dividends': div_val,
            'buybacks': buyback_val,
            'revenue': revenue_val,
            'free_cash_flow': fcf,
            'capex_intensity': (capex_val / revenue_val * 100) if revenue_val > 0 else None,
            'fcf_margin': (fcf / revenue_val * 100) if revenue_val > 0 else None
        }
        quarterly_data.append(quarter_record)

    # Calculate totals and averages
    total_capex = sum(q['capex'] for q in quarterly_data)
    total_ocf = sum(q['operating_cf'] for q in quarterly_data)
    total_fcf = sum(q['free_cash_flow'] for q in quarterly_data)
    total_dividends = sum(q['dividends'] for q in quarterly_data)
    total_buybacks = sum(q['buybacks'] for q in quarterly_data)
    total_revenue = sum(q['revenue'] for q in quarterly_data if q['revenue'] > 0)

    intensities = [q['capex_intensity'] for q in quarterly_data if q['capex_intensity'] is not None]
    fcf_margins = [q['fcf_margin'] for q in quarterly_data if q['fcf_margin'] is not None]

    avg_capex_intensity = sum(intensities) / len(intensities) if intensities else None
    avg_fcf_margin = sum(fcf_margins) / len(fcf_margins) if fcf_margins else None

    # Strategic assessment
    avg_capex = total_capex / len(quarterly_data) if quarterly_data else 0
    avg_ocf = total_ocf / len(quarterly_data) if quarterly_data else 0
    avg_dividends = total_dividends / len(quarterly_data) if quarterly_data else 0
    avg_buybacks = total_buybacks / len(quarterly_data) if quarterly_data else 0

    capex_pct = (avg_capex / avg_ocf * 100) if avg_ocf > 0 else 0
    div_pct = (avg_dividends / avg_ocf * 100) if avg_ocf > 0 else 0
    buyback_pct = (avg_buybacks / avg_ocf * 100) if avg_ocf > 0 else 0
    shareholder_pct = div_pct + buyback_pct

    # Determine allocation priority
    if capex_pct > 50:
        priority = "Growth-Focused (High CapEx)"
    elif shareholder_pct > 70:
        priority = "Returns-Focused (High Payout)"
    elif capex_pct > 40 and shareholder_pct > 50:
        priority = "Growth-Oriented with Returns (Leveraged)"
    elif capex_pct > 30 and shareholder_pct > 40:
        priority = "Balanced (Growth + Returns)"
    else:
        priority = "Conservative (Cash Accumulation)"

    # Sustainability check
    if shareholder_pct > 100:
        sustainability = "⚠️  Returning more than OCF (debt/asset-funded)"
    elif shareholder_pct > 80:
        sustainability = "⚠️  High payout (limited flexibility)"
    elif shareholder_pct > 50:
        sustainability = "✓  Moderate payout (sustainable)"
    else:
        sustainability = "✓  Low payout (growth-oriented)"

    # Format summary
    summary_lines = [
        f"\n{company_name} - CAPITAL ALLOCATION ANALYSIS",
        "=" * 80,
        f"Data Period: {len(quarterly_data)} quarters\n"
    ]

    summary_lines.append("QUARTERLY CAPITAL ALLOCATION DETAIL:")
    summary_lines.append("| Quarter    | CapEx    | Op CF    | FCF      | Div      | Buyback  |")
    summary_lines.append("|------------|----------|----------|----------|----------|----------|")

    for q in quarterly_data[:8]:  # Show up to 8 quarters
        date_str = q['date'][:10]
        capex_m = q['capex'] / 1_000_000
        ocf_m = q['operating_cf'] / 1_000_000
        fcf_m = q['free_cash_flow'] / 1_000_000
        div_m = q['dividends'] / 1_000_000
        buy_m = q['buybacks'] / 1_000_000

        summary_lines.append(
            f"| {date_str} | ${capex_m:6.0f}M | ${ocf_m:6.0f}M | ${fcf_m:6.0f}M | ${div_m:6.0f}M | ${buy_m:6.0f}M |"
        )

    summary_lines.append("\nCAPITAL ALLOCATION BREAKDOWN (Quarterly Average):")
    summary_lines.append(f"  Operating Cash Flow: ${avg_ocf/1_000_000:,.0f}M")
    summary_lines.append(f"  CapEx: ${avg_capex/1_000_000:,.0f}M          ({capex_pct:.0f}% of OCF)")
    summary_lines.append(f"  Free Cash Flow: ${(avg_ocf-avg_capex)/1_000_000:,.0f}M   ({100-capex_pct:.0f}% of OCF)\n")

    if avg_dividends > 0:
        summary_lines.append(f"  Dividends: ${avg_dividends/1_000_000:,.0f}M      ({div_pct:.0f}% of OCF)")
    if avg_buybacks > 0:
        summary_lines.append(f"  Buybacks: ${avg_buybacks/1_000_000:,.0f}M       ({buyback_pct:.0f}% of OCF)")

    summary_lines.append(f"\n  Total to Shareholders: ${(avg_dividends+avg_buybacks)/1_000_000:,.0f}M ({shareholder_pct:.0f}% of OCF)")

    summary_lines.append(f"\nALLOCATION PRIORITY: {priority}")
    summary_lines.append(f"  - CapEx: {capex_pct:.0f}% of OCF")
    summary_lines.append(f"  - Shareholders: {shareholder_pct:.0f}% of OCF")
    summary_lines.append(f"  - {sustainability}")

    if shareholder_pct > 100:
        funding_gap = shareholder_pct + capex_pct - 100
        summary_lines.append(f"  - Funding gap: {funding_gap:.0f}% (via debt/asset sales)")

    if avg_capex_intensity:
        summary_lines.append(f"\nCAPITAL INTENSITY:")
        summary_lines.append(f"  - Average CapEx: {avg_capex_intensity:.1f}% of revenue")

        # Industry benchmarks
        if avg_capex_intensity < 3:
            assessment = "Asset-light business"
        elif avg_capex_intensity < 5:
            assessment = "Moderate capital needs"
        elif avg_capex_intensity < 8:
            assessment = "Capital-intensive (manufacturing)"
        else:
            assessment = "Heavy infrastructure investment"

        summary_lines.append(f"  - Assessment: {assessment}")

    if avg_fcf_margin:
        summary_lines.append(f"\nFREE CASH FLOW:")
        summary_lines.append(f"  - Average FCF Margin: {avg_fcf_margin:.1f}% of revenue")

        if avg_fcf_margin > 15:
            fcf_quality = "Excellent cash generator"
        elif avg_fcf_margin > 10:
            fcf_quality = "Strong cash generation"
        elif avg_fcf_margin > 5:
            fcf_quality = "Moderate cash generation"
        else:
            fcf_quality = "Limited financial flexibility"

        summary_lines.append(f"  - Quality: {fcf_quality}")

        # Trend analysis
        if len(fcf_margins) >= 4:
            recent_avg = sum(fcf_margins[:4]) / 4
            older_avg = sum(fcf_margins[4:8]) / len(fcf_margins[4:8]) if len(fcf_margins) > 4 else recent_avg
            if recent_avg > older_avg * 1.1:
                trend = "Improving"
            elif recent_avg < older_avg * 0.9:
                trend = "Declining"
            else:
                trend = "Stable"
            summary_lines.append(f"  - Trend: {trend}")

    # Key insights
    summary_lines.append("\nKEY INSIGHTS:")

    # Buyback opportunism
    if quarterly_data:
        max_buyback_q = max(quarterly_data, key=lambda x: x['buybacks'])
        if max_buyback_q['buybacks'] > avg_buybacks * 3:
            summary_lines.append(
                f"- Large buyback in {max_buyback_q['date'][:7]} "
                f"(${max_buyback_q['buybacks']/1_000_000:,.0f}M) = opportunistic"
            )

    # CapEx trends
    if len(quarterly_data) >= 4:
        recent_capex_intensity = sum(intensities[:4]) / 4 if len(intensities) >= 4 else avg_capex_intensity
        older_capex_intensity = sum(intensities[4:8]) / len(intensities[4:8]) if len(intensities) > 4 else recent_capex_intensity

        if recent_capex_intensity and older_capex_intensity:
            capex_change = ((recent_capex_intensity - older_capex_intensity) / older_capex_intensity) * 100
            if abs(capex_change) > 15:
                direction = "increasing" if capex_change > 0 else "decreasing"
                summary_lines.append(
                    f"- CapEx intensity {direction} ({older_capex_intensity:.1f}% → {recent_capex_intensity:.1f}%)"
                )

    # Payout ratio sustainability
    if shareholder_pct > 100:
        summary_lines.append(f"- Payout ratio {shareholder_pct:.0f}% unsustainable without external financing")
    elif shareholder_pct > 80:
        summary_lines.append(f"- Payout ratio {shareholder_pct:.0f}% leaves limited room for M&A or flexibility")

    return {
        'company_name': company_name,
        'quarters_analyzed': len(quarterly_data),
        'data': quarterly_data,
        'totals': {
            'total_capex': total_capex,
            'total_operating_cf': total_ocf,
            'total_free_cf': total_fcf,
            'total_dividends': total_dividends,
            'total_buybacks': total_buybacks,
            'avg_capex_intensity': avg_capex_intensity,
            'avg_fcf_margin': avg_fcf_margin
        },
        'allocation_priorities': priority,
        'sustainability': sustainability,
        'summary': '\n'.join(summary_lines)
    }


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "MDT"
    quarters = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    result = extract_company_capex_allocation(ticker=ticker, quarters=quarters)

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(result['summary'])
