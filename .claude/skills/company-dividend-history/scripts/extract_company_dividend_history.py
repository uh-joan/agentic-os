import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_facts

def extract_company_dividend_history(ticker: str, quarters: int = 12) -> dict:
    """Extract dividend payment history and payout trends from SEC EDGAR filings.

    Analyzes dividend payments, payout ratios, dividend growth, and sustainability
    by extracting cash flow data from XBRL filings.

    Args:
        ticker: Company ticker symbol (e.g., "MDT", "ABBV", "PFE")
        quarters: Number of recent quarters to analyze (default 12 = 3 years)

    Returns:
        dict: Contains dividend data, payout ratios, growth trends, summary
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

    # Extract dividend payments (try multiple concept variations)
    div_data = []
    for concept_name in ['PaymentsOfDividendsCommonStock',
                          'PaymentsOfDividends',
                          'DividendsCommonStockCash',
                          'PaymentsOfOrdinaryDividends']:
        div_concept = us_gaap.get(concept_name, {})
        if div_concept:
            div_units = div_concept.get('units', {})
            div_data = div_units.get('USD', [])
            if div_data:
                print(f"Using dividend concept: {concept_name}")
                break

    # Extract operating cash flow for payout ratio
    ocf_concept = us_gaap.get('NetCashProvidedByUsedInOperatingActivities', {})
    ocf_units = ocf_concept.get('units', {})
    ocf_data = ocf_units.get('USD', [])

    # Extract net income for payout ratio
    ni_concept = us_gaap.get('NetIncomeLoss', {})
    ni_units = ni_concept.get('units', {})
    ni_data = ni_units.get('USD', [])

    # Build lookup dictionaries by end date (quarterly data from 10-Q and 10-K)
    def build_quarterly_lookup(data):
        result = {}
        for item in data:
            form = item.get('form', '')
            frame = item.get('frame', '')

            # Accept quarterly data from both 10-Q and 10-K forms
            # Quarterly data has frame like "CY2024Q1" or form "10-Q"
            is_quarterly = False
            if form == '10-Q':
                is_quarterly = True
            elif frame and 'Q' in frame:
                is_quarterly = True

            if is_quarterly:
                end_date = item.get('end', '')
                value = abs(item.get('val', 0))  # Absolute value (payments are negative)
                if end_date not in result or item.get('filed', '') > result[end_date].get('filed', ''):
                    result[end_date] = {'value': value, 'filed': item.get('filed', '')}
        return result

    div_lookup = build_quarterly_lookup(div_data)
    ocf_lookup = build_quarterly_lookup(ocf_data)
    ni_lookup = build_quarterly_lookup(ni_data)

    # Get all dates and sort
    all_dates = sorted(div_lookup.keys(), reverse=False)  # Oldest first for delta calculation

    # Check if we have any dividend data
    if not all_dates:
        return {
            'error': f"No dividend data found for {ticker}",
            'summary': f"No dividend payments found in XBRL data for {company_name}. Company may not pay dividends or data not available."
        }

    # Calculate quarterly increments (not cumulative values)
    # XBRL often reports year-to-date cumulative at fiscal year-end
    # We need to calculate deltas between consecutive quarters
    quarterly_data = []
    prev_div = 0
    prev_ocf = 0
    prev_ni = 0

    for i, end_date in enumerate(all_dates):
        div_cumulative = div_lookup.get(end_date, {}).get('value', 0)
        ocf_cumulative = ocf_lookup.get(end_date, {}).get('value', 0)
        ni_cumulative = ni_lookup.get(end_date, {}).get('value', 0)

        # Calculate incremental (delta from previous quarter)
        if i == 0:
            # First quarter - use cumulative as incremental
            div_increment = div_cumulative
            ocf_increment = ocf_cumulative
            ni_increment = ni_cumulative
        else:
            # Calculate delta
            div_increment = div_cumulative - prev_div
            ocf_increment = ocf_cumulative - prev_ocf
            ni_increment = ni_cumulative - prev_ni

            # If delta is negative, likely a new fiscal year reset - use cumulative
            if div_increment < 0:
                div_increment = div_cumulative
            if ocf_increment < 0:
                ocf_increment = ocf_cumulative
            if ni_increment < 0:
                ni_increment = ni_cumulative

        # Store for next iteration
        prev_div = div_cumulative
        prev_ocf = ocf_cumulative
        prev_ni = ni_cumulative

        quarter_record = {
            'date': end_date,
            'dividends': div_increment,
            'operating_cf': ocf_increment,
            'net_income': ni_increment,
            'payout_ratio_ocf': (div_increment / ocf_increment * 100) if ocf_increment > 0 else None,
            'payout_ratio_ni': (div_increment / ni_increment * 100) if ni_increment > 0 else None
        }
        quarterly_data.append(quarter_record)

    # Reverse to show most recent first
    quarterly_data.reverse()

    # Keep only requested number of quarters
    quarterly_data = quarterly_data[:quarters]

    # Calculate totals and averages
    total_dividends = sum(q['dividends'] for q in quarterly_data)
    total_ocf = sum(q['operating_cf'] for q in quarterly_data)
    total_ni = sum(q['net_income'] for q in quarterly_data)

    avg_dividends = total_dividends / len(quarterly_data) if quarterly_data else 0
    avg_ocf = total_ocf / len(quarterly_data) if quarterly_data else 0
    avg_ni = total_ni / len(quarterly_data) if quarterly_data else 0

    payout_ratios_ocf = [q['payout_ratio_ocf'] for q in quarterly_data if q['payout_ratio_ocf'] is not None]
    payout_ratios_ni = [q['payout_ratio_ni'] for q in quarterly_data if q['payout_ratio_ni'] is not None]

    avg_payout_ocf = sum(payout_ratios_ocf) / len(payout_ratios_ocf) if payout_ratios_ocf else None
    avg_payout_ni = sum(payout_ratios_ni) / len(payout_ratios_ni) if payout_ratios_ni else None

    # Calculate dividend growth
    if len(quarterly_data) >= 8:
        recent_4q = sum(q['dividends'] for q in quarterly_data[:4])
        older_4q = sum(q['dividends'] for q in quarterly_data[4:8])
        yoy_growth = ((recent_4q - older_4q) / older_4q * 100) if older_4q > 0 else None
    else:
        yoy_growth = None

    # Sustainability assessment
    if avg_payout_ocf:
        if avg_payout_ocf > 100:
            sustainability = "⚠️  Unsustainable (paying more than OCF)"
        elif avg_payout_ocf > 80:
            sustainability = "⚠️  High payout (limited flexibility)"
        elif avg_payout_ocf > 50:
            sustainability = "✓  Moderate payout (sustainable)"
        else:
            sustainability = "✓  Low payout (room to grow)"
    else:
        sustainability = "Unknown"

    # Dividend policy assessment
    if avg_payout_ocf and avg_payout_ni:
        if avg_payout_ni < 50:
            policy = "Growth-oriented (retaining earnings)"
        elif avg_payout_ni < 70:
            policy = "Balanced (growth + income)"
        elif avg_payout_ni < 90:
            policy = "Income-oriented (mature)"
        else:
            policy = "High payout (potential dividend trap)"
    else:
        policy = "Unknown"

    # Format summary
    summary_lines = [
        f"\n{company_name} - DIVIDEND ANALYSIS",
        "=" * 80,
        f"Data Period: {len(quarterly_data)} quarters\n"
    ]

    summary_lines.append("QUARTERLY DIVIDEND PAYMENTS:")
    summary_lines.append("| Quarter    | Dividends | Op CF    | Net Inc  | Payout (OCF) | Payout (NI) |")
    summary_lines.append("|------------|-----------|----------|----------|--------------|-------------|")

    for q in quarterly_data[:8]:  # Show up to 8 quarters
        date_str = q['date'][:10]
        div_m = q['dividends'] / 1_000_000
        ocf_m = q['operating_cf'] / 1_000_000
        ni_m = q['net_income'] / 1_000_000
        payout_ocf_str = f"{q['payout_ratio_ocf']:.0f}%" if q['payout_ratio_ocf'] else "N/A"
        payout_ni_str = f"{q['payout_ratio_ni']:.0f}%" if q['payout_ratio_ni'] else "N/A"

        summary_lines.append(
            f"| {date_str} | ${div_m:7.0f}M | ${ocf_m:6.0f}M | ${ni_m:6.0f}M | {payout_ocf_str:>12} | {payout_ni_str:>11} |"
        )

    summary_lines.append("\nDIVIDEND METRICS (Quarterly Average):")
    summary_lines.append(f"  Dividend Payment: ${avg_dividends/1_000_000:,.0f}M")
    summary_lines.append(f"  Operating Cash Flow: ${avg_ocf/1_000_000:,.0f}M")
    summary_lines.append(f"  Net Income: ${avg_ni/1_000_000:,.0f}M\n")

    if avg_payout_ocf:
        summary_lines.append(f"  Payout Ratio (OCF): {avg_payout_ocf:.0f}%")
    if avg_payout_ni:
        summary_lines.append(f"  Payout Ratio (Net Income): {avg_payout_ni:.0f}%")

    summary_lines.append(f"\n  Annual Dividend Rate: ${total_dividends/len(quarterly_data)*4/1_000_000:,.0f}M")

    if yoy_growth is not None:
        summary_lines.append(f"  YoY Growth: {yoy_growth:+.1f}%")

    summary_lines.append(f"\nDIVIDEND SUSTAINABILITY: {sustainability}")
    summary_lines.append(f"DIVIDEND POLICY: {policy}")

    # Key insights
    summary_lines.append("\nKEY INSIGHTS:")

    # Dividend growth trend
    if yoy_growth is not None:
        if yoy_growth > 10:
            summary_lines.append(f"- Strong dividend growth ({yoy_growth:.1f}% YoY) = shareholder-friendly")
        elif yoy_growth > 5:
            summary_lines.append(f"- Moderate dividend growth ({yoy_growth:.1f}% YoY) = stable policy")
        elif yoy_growth > -5:
            summary_lines.append(f"- Flat dividends ({yoy_growth:.1f}% YoY) = maintaining commitment")
        else:
            summary_lines.append(f"- Declining dividends ({yoy_growth:.1f}% YoY) = potential stress")

    # Payout sustainability
    if avg_payout_ocf:
        if avg_payout_ocf > 100:
            summary_lines.append(f"- Payout ratio {avg_payout_ocf:.0f}% unsustainable without debt/asset sales")
        elif avg_payout_ocf > 80:
            summary_lines.append(f"- Payout ratio {avg_payout_ocf:.0f}% leaves limited room for growth investments")
        elif avg_payout_ocf < 40:
            summary_lines.append(f"- Payout ratio {avg_payout_ocf:.0f}% = room for dividend increases")

    # Dividend consistency
    div_payments = [q['dividends'] for q in quarterly_data if q['dividends'] > 0]
    if div_payments:
        min_div = min(div_payments)
        max_div = max(div_payments)
        volatility = ((max_div - min_div) / min_div * 100) if min_div > 0 else 0

        if volatility < 5:
            summary_lines.append(f"- Dividend payments very consistent (volatility: {volatility:.1f}%)")
        elif volatility < 15:
            summary_lines.append(f"- Dividend payments moderately consistent (volatility: {volatility:.1f}%)")
        else:
            summary_lines.append(f"- Dividend payments volatile (volatility: {volatility:.1f}%) = irregular policy")

    return {
        'company_name': company_name,
        'quarters_analyzed': len(quarterly_data),
        'data': quarterly_data,
        'totals': {
            'total_dividends': total_dividends,
            'total_operating_cf': total_ocf,
            'total_net_income': total_ni,
            'avg_payout_ratio_ocf': avg_payout_ocf,
            'avg_payout_ratio_ni': avg_payout_ni,
            'yoy_growth': yoy_growth
        },
        'sustainability': sustainability,
        'policy': policy,
        'summary': '\n'.join(summary_lines)
    }


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "MDT"
    quarters = int(sys.argv[2]) if len(sys.argv) > 2 else 12

    result = extract_company_dividend_history(ticker=ticker, quarters=quarters)

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(result['summary'])
