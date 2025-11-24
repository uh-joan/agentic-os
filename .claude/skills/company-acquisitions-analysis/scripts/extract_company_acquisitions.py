import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_facts

def extract_company_acquisitions(ticker: str, periods: int = 12) -> dict:
    """Extract M&A history and goodwill trends from SEC EDGAR filings.

    Analyzes acquisition cash payments, goodwill changes, and impairments
    to identify major M&A activity and integration success/failure.

    Args:
        ticker: Company ticker symbol (e.g., "MDT", "ABBV", "PFE")
        periods: Number of recent periods to analyze (default 12 = 3 years)

    Returns:
        dict: Contains acquisition data, goodwill trends, impairments, summary
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

    # Extract acquisition payments
    acquire_concept = us_gaap.get('PaymentsToAcquireBusinessesNetOfCashAcquired', {})
    acquire_units = acquire_concept.get('units', {})
    acquire_data = acquire_units.get('USD', [])

    acquisition_payments = []
    if acquire_data:
        sorted_data = sorted(acquire_data, key=lambda x: x.get('end', ''), reverse=True)[:periods]
        for item in sorted_data:
            amount = abs(item.get('val', 0))
            if amount > 0:  # Only include actual acquisitions
                acquisition_payments.append({
                    'date': item.get('end', 'N/A'),
                    'amount': amount,
                    'form': item.get('form', 'N/A'),
                    'filed': item.get('filed', 'N/A')
                })

    # Extract goodwill trend
    goodwill_concept = us_gaap.get('Goodwill', {})
    goodwill_units = goodwill_concept.get('units', {})
    goodwill_data = goodwill_units.get('USD', [])

    goodwill_trend = []
    if goodwill_data:
        sorted_data = sorted(goodwill_data, key=lambda x: x.get('end', ''), reverse=True)[:periods]
        prev_value = None
        for item in sorted_data:
            value = item.get('val', 0)
            change_pct = None
            if prev_value and prev_value > 0:
                change_pct = ((value - prev_value) / prev_value) * 100

            goodwill_trend.append({
                'date': item.get('end', 'N/A'),
                'goodwill': value,
                'change_pct': change_pct,
                'form': item.get('form', 'N/A')
            })
            prev_value = value

        # Reverse to show oldest first for trend calculation
        goodwill_trend.reverse()

    # Extract impairments
    impairment_concept = us_gaap.get('GoodwillImpairmentLoss', {})
    impairment_units = impairment_concept.get('units', {})
    impairment_data = impairment_units.get('USD', [])

    impairments = []
    if impairment_data:
        sorted_data = sorted(impairment_data, key=lambda x: x.get('end', ''), reverse=True)[:periods]
        for item in sorted_data:
            amount = item.get('val', 0)
            if amount > 0:  # Only include actual impairments
                impairments.append({
                    'date': item.get('end', 'N/A'),
                    'amount': amount,
                    'form': item.get('form', 'N/A')
                })

    # Format summary
    summary_lines = [
        f"\n{company_name} - M&A ANALYSIS",
        "=" * 80,
        f"Data Period: {periods} quarters\n"
    ]

    # Acquisition payments summary
    summary_lines.append("ACQUISITION CASH PAYMENTS:")
    if acquisition_payments:
        for payment in acquisition_payments[:8]:  # Top 8
            date = payment['date']
            amount_m = payment['amount'] / 1_000_000

            # Flag major acquisitions
            flag = ""
            if amount_m > 1000:
                flag = "  🚨 MAJOR ACQUISITION"
            elif amount_m > 200:
                flag = "  Significant"
            elif amount_m > 50:
                flag = "  Bolt-on"
            else:
                flag = "  Tuck-in"

            summary_lines.append(f"  {date}: ${amount_m:,.0f}M{flag}")
    else:
        summary_lines.append("  No acquisition activity detected")

    # Goodwill trend summary
    summary_lines.append("\nGOODWILL TREND:")
    if goodwill_trend:
        oldest = goodwill_trend[0]
        newest = goodwill_trend[-1]

        oldest_value = oldest['goodwill'] / 1_000_000
        newest_value = newest['goodwill'] / 1_000_000
        change = newest_value - oldest_value
        change_pct = (change / oldest_value) * 100 if oldest_value > 0 else 0

        summary_lines.append(f"  {oldest['date']}: ${oldest_value:,.0f}M")
        summary_lines.append(f"  {newest['date']}: ${newest_value:,.0f}M")
        summary_lines.append(f"  Change: {'+' if change > 0 else ''}${change:,.0f}M ({change_pct:+.1f}%)")

        # Interpretation
        if change_pct > 20:
            summary_lines.append("  ⚠️  Goodwill growing rapidly (acquisition-heavy growth)")
        elif change_pct > 5:
            summary_lines.append("  ✓  Moderate goodwill growth (balanced M&A)")
        elif change_pct > -5:
            summary_lines.append("  ✓  Goodwill stable (organic growth period)")
        else:
            summary_lines.append("  🚨 Goodwill declining (impairments or divestitures)")
    else:
        summary_lines.append("  No goodwill data available")

    # Impairments summary
    summary_lines.append("\nGOODWILL IMPAIRMENTS:")
    if impairments:
        for impair in impairments[:5]:
            date = impair['date']
            amount_m = impair['amount'] / 1_000_000
            summary_lines.append(f"  {date}: ${amount_m:,.0f}M write-down 🚨")
        summary_lines.append("  ⚠️  Impairments indicate acquisition integration challenges")
    else:
        summary_lines.append("  None detected (healthy)")

    # Key insights
    summary_lines.append("\nKEY INSIGHTS:")

    # Find largest acquisition
    if acquisition_payments:
        largest = max(acquisition_payments, key=lambda x: x['amount'])
        largest_amount_m = largest['amount'] / 1_000_000
        summary_lines.append(f"- Largest acquisition: ${largest_amount_m:,.0f}M in {largest['date'][:4]}")

        # Check if it explains goodwill growth
        if goodwill_trend and len(goodwill_trend) > 1:
            gw_change = (goodwill_trend[-1]['goodwill'] - goodwill_trend[0]['goodwill']) / 1_000_000
            if abs(gw_change) > largest_amount_m * 0.3:  # If goodwill change is >30% of acquisition
                summary_lines.append(f"- Goodwill increase (${gw_change:,.0f}M) consistent with acquisition activity")

    # Acquisition frequency
    if acquisition_payments:
        total_spend = sum(p['amount'] for p in acquisition_payments) / 1_000_000
        avg_per_period = total_spend / periods
        summary_lines.append(f"- Average acquisition spend: ${avg_per_period:,.0f}M per quarter")

        if avg_per_period > 200:
            summary_lines.append("- Strategy: Aggressive M&A (high integration risk)")
        elif avg_per_period > 50:
            summary_lines.append("- Strategy: Bolt-on acquisitions (balanced growth)")
        else:
            summary_lines.append("- Strategy: Selective M&A (organic-focused)")

    # Impairment risk
    if goodwill_trend and not impairments:
        newest_gw = goodwill_trend[-1]['goodwill'] / 1_000_000
        if newest_gw > 40000:  # >$40B goodwill
            summary_lines.append(f"- Goodwill at ${newest_gw:,.0f}M - monitor for impairment risk")

    return {
        'company_name': company_name,
        'acquisition_payments': acquisition_payments,
        'goodwill_trend': goodwill_trend,
        'impairments': impairments,
        'summary': '\n'.join(summary_lines)
    }


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "MDT"
    periods = int(sys.argv[2]) if len(sys.argv) > 2 else 12

    result = extract_company_acquisitions(ticker=ticker, periods=periods)

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(result['summary'])
