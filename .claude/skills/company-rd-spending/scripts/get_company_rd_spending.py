import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_facts
from datetime import datetime
from typing import Optional

def get_company_rd_spending(ticker: str, quarters: int = 8) -> dict:
    """Extract quarterly R&D spending data from SEC filings.

    Retrieves time series of R&D spending with revenue context and YoY growth
    calculations for strategic investment analysis.

    Args:
        ticker: Company ticker symbol (e.g., "MDT", "ABBV")
        quarters: Number of recent quarters to analyze (default 8 = 2 years)

    Returns:
        dict: Contains quarterly R&D data with:
            - total_quarters: Number of quarters retrieved
            - company_name: Official company name
            - data: List of quarterly records with spending, revenue, ratios
            - summary: Formatted table for display
    """

    # Fetch company facts from SEC EDGAR
    # print(f"Fetching SEC EDGAR data for {ticker}...")  # Disabled for JSON output
    facts_response = get_company_facts(cik_or_ticker=ticker)

    if not facts_response or 'error' in facts_response:
        return {
            'data': {
                'total_quarters': 0
            },
            'source_metadata': {
                'source': 'SEC EDGAR',
                'mcp_server': 'sec_edgar_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'ticker': ticker,
                    'quarters': quarters
                },
                'data_count': 0,
                'data_type': 'financial_data'
            },
            'summary': f"Failed to fetch data for {ticker} (source: SEC EDGAR, {datetime.now().strftime('%Y-%m-%d')})",
            'error': f"Failed to fetch data for {ticker}"
        }

    company_name = facts_response.get('entityName', ticker)
    facts = facts_response.get('facts', {})

    # Navigate to US-GAAP taxonomy
    us_gaap = facts.get('us-gaap', {})

    # Extract R&D expense concept (try multiple common variations)
    rd_data = []
    for concept_name in ['ResearchAndDevelopmentExpense',
                         'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost',
                         'ResearchDevelopmentAndComputerSoftwareExpense']:
        rd_concept = us_gaap.get(concept_name, {})
        if rd_concept:
            rd_units = rd_concept.get('units', {})
            rd_data = rd_units.get('USD', [])
            if rd_data:
                # print(f"Using R&D concept: {concept_name}")  # Disabled for JSON output
                break

    # Extract Revenue concept (try multiple common names)
    revenue_data = []
    for concept_name in ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet']:
        revenue_concept = us_gaap.get(concept_name, {})
        if revenue_concept:
            revenue_units = revenue_concept.get('units', {})
            revenue_data = revenue_units.get('USD', [])
            if revenue_data:
                break

    if not rd_data:
        return {
            'data': {
                'total_quarters': 0
            },
            'source_metadata': {
                'source': 'SEC EDGAR',
                'mcp_server': 'sec_edgar_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'ticker': ticker,
                    'quarters': quarters
                },
                'data_count': 0,
                'data_type': 'financial_data'
            },
            'summary': f"No R&D expense data found for {ticker} (source: SEC EDGAR, {datetime.now().strftime('%Y-%m-%d')})",
            'error': f"No R&D expense data found for {ticker}"
        }

    # Filter for quarterly data (3-month periods) and recent filings
    # Use form types 10-Q and 10-K, focusing on quarterly duration
    quarterly_rd = {}
    for item in rd_data:
        # Get fiscal period end date
        end_date = item.get('end', '')
        form = item.get('form', '')
        value = item.get('val', 0)
        frame = item.get('frame', '')

        # Only include 10-Q forms (quarterly filings)
        # If frame is available, verify it's quarterly (contains 'Q')
        # If frame is not available, accept 10-Q forms
        if form == '10-Q':
            is_quarterly = True
        elif frame and 'Q' in frame:
            is_quarterly = True
        else:
            is_quarterly = False

        if not is_quarterly:
            continue

        # Store by end date (will keep most recent filing if duplicates)
        if end_date not in quarterly_rd or item.get('filed', '') > quarterly_rd[end_date].get('filed', ''):
            quarterly_rd[end_date] = {
                'end': end_date,
                'rd_expense': value,
                'form': form,
                'filed': item.get('filed', ''),
                'frame': frame if frame else 'N/A'
            }

    # Build revenue lookup by end date
    quarterly_revenue = {}
    for item in revenue_data:
        end_date = item.get('end', '')
        form = item.get('form', '')
        value = item.get('val', 0)
        frame = item.get('frame', '')

        # Only include 10-Q forms or frames with 'Q'
        if form == '10-Q':
            is_quarterly = True
        elif frame and 'Q' in frame:
            is_quarterly = True
        else:
            is_quarterly = False

        if not is_quarterly:
            continue

        if end_date not in quarterly_revenue or item.get('filed', '') > quarterly_revenue[end_date].get('filed', ''):
            quarterly_revenue[end_date] = {
                'revenue': value,
                'filed': item.get('filed', '')
            }

    # Combine R&D and revenue data
    combined_data = []
    for end_date, rd_info in quarterly_rd.items():
        revenue_info = quarterly_revenue.get(end_date, {})

        quarter_record = {
            'end_date': end_date,
            'rd_expense': rd_info['rd_expense'],
            'revenue': revenue_info.get('revenue', 0),
            'form': rd_info['form'],
            'frame': rd_info['frame']
        }

        # Calculate R&D intensity
        if quarter_record['revenue'] > 0:
            quarter_record['rd_intensity'] = (quarter_record['rd_expense'] / quarter_record['revenue']) * 100
        else:
            quarter_record['rd_intensity'] = None

        combined_data.append(quarter_record)

    # Sort by end date (most recent first)
    combined_data.sort(key=lambda x: x['end_date'], reverse=True)

    # Limit to requested number of quarters
    combined_data = combined_data[:quarters]

    # Calculate YoY growth (compare to same quarter previous year)
    for i, record in enumerate(combined_data):
        # Look for quarter from 4 quarters ago (1 year)
        yoy_growth = None
        if i + 4 < len(combined_data):
            prior_year_record = combined_data[i + 4]
            if prior_year_record['rd_expense'] > 0:
                yoy_growth = ((record['rd_expense'] - prior_year_record['rd_expense']) /
                             prior_year_record['rd_expense']) * 100

        record['yoy_growth'] = yoy_growth

    # Format summary table
    summary_lines = [
        f"\n{company_name} - Quarterly R&D Spending Analysis",
        f"Data Source: SEC EDGAR (US-GAAP)",
        f"Quarters Analyzed: {len(combined_data)}",
        "",
        "| Quarter Ending | R&D Spending | Revenue    | R&D % | YoY Growth |",
        "|----------------|--------------|------------|-------|------------|"
    ]

    for record in combined_data:
        end_date = datetime.strptime(record['end_date'], '%Y-%m-%d').strftime('%Y-Q%m')
        rd_millions = record['rd_expense'] / 1_000_000
        rev_billions = record['revenue'] / 1_000_000_000 if record['revenue'] > 0 else 0

        rd_str = f"${rd_millions:,.0f}M"
        rev_str = f"${rev_billions:.2f}B" if rev_billions > 0 else "N/A"

        if record['rd_intensity'] is not None:
            intensity_str = f"{record['rd_intensity']:.1f}%"
        else:
            intensity_str = "N/A"

        if record['yoy_growth'] is not None:
            growth_str = f"{record['yoy_growth']:+.1f}%"
        else:
            growth_str = "N/A"

        summary_lines.append(
            f"| {end_date:14} | {rd_str:12} | {rev_str:10} | {intensity_str:5} | {growth_str:10} |"
        )

    # Add insights
    if combined_data:
        recent = combined_data[0]
        summary_lines.extend([
            "",
            "Key Insights:",
            f"- Most Recent Quarter: {recent['end_date']}",
            f"- Latest R&D Spending: ${recent['rd_expense']/1_000_000:,.0f}M"
        ])

        if recent['rd_intensity'] is not None:
            summary_lines.append(f"- R&D Intensity: {recent['rd_intensity']:.1f}% of revenue")

        if recent['yoy_growth'] is not None:
            trend = "increasing" if recent['yoy_growth'] > 0 else "decreasing"
            summary_lines.append(f"- YoY Trend: {trend} ({recent['yoy_growth']:+.1f}%)")

        # Calculate average R&D intensity
        intensities = [r['rd_intensity'] for r in combined_data if r['rd_intensity'] is not None]
        if intensities:
            avg_intensity = sum(intensities) / len(intensities)
            summary_lines.append(f"- Average R&D Intensity: {avg_intensity:.1f}% over {len(intensities)} quarters")

    return {
        'data': {
            'total_quarters': len(combined_data),
            'company_name': company_name,
            'quarterly_data': combined_data
        },
        'source_metadata': {
            'source': 'SEC EDGAR',
            'mcp_server': 'sec_edgar_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {
                'ticker': ticker,
                'quarters': quarters
            },
            'data_count': len(combined_data),
            'data_type': 'financial_data'
        },
        'summary': f"{'\n'.join(summary_lines)}\n\n(source: SEC EDGAR, {datetime.now().strftime('%Y-%m-%d')})"
    }


if __name__ == "__main__":
    import json
    # Default example: Medtronic (medical device company with significant R&D)
    ticker = sys.argv[1] if len(sys.argv) > 1 else "MDT"
    quarters = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    result = get_company_rd_spending(ticker=ticker, quarters=quarters)

    # For JSON verification (required by verify_source_attribution.py)
    print(json.dumps(result, indent=2))
