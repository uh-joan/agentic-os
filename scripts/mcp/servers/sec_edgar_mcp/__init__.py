"""SEC EDGAR MCP Server - Python API

Provides Python functions for SEC EDGAR company filings and financial data.
Data stays in execution environment - only summaries flow to model.

CRITICAL SEC EDGAR QUIRKS:
1. CIK required: Convert ticker to CIK first (use get_company_cik)
2. CIK format: 10-digit with leading zeros (e.g., "0000320193")
3. Filing types: 10-K (annual), 10-Q (quarterly), 8-K (current events)
4. Date format: "YYYY-MM-DD" for filters
5. filter_filings: Use to narrow by form type and date range
6. XBRL data: Use get_company_facts for structured financial metrics
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List, Union


def search_companies(
    query: str
) -> Dict[str, Any]:
    """
    Search for companies by name or ticker symbol

    Args:
        query: Company name or ticker symbol
              Examples: "Apple", "AAPL", "Microsoft", "Tesla", "Amazon"

    Returns:
        dict: Company search results

        Key fields:
        - cik: Central Index Key (10-digit)
        - name: Company name
        - ticker: Stock ticker

    Examples:
        # Search by name
        results = search_companies(query="Apple")

        # Extract CIK
        for company in results.get('data', []):
            cik = company.get('cik')
            name = company.get('name')
            ticker = company.get('ticker')
            print(f"{name} ({ticker}): CIK {cik}")

        # Search by ticker
        results = search_companies(query="AAPL")
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'search_companies',
        'query': query
    }

    return client.call_tool('sec-edgar', params)


def get_company_cik(
    ticker: str
) -> Dict[str, Any]:
    """
    Convert stock ticker to CIK (Central Index Key)

    CRITICAL: Most SEC queries require CIK, not ticker!
    Use this as STEP 1 before other queries.

    Args:
        ticker: Stock ticker symbol
               Examples: "AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"

    Returns:
        dict: CIK information

        Response structure:
        {
            "cik": "0000320193",  // 10-digit with leading zeros
            "ticker": "AAPL",
            "name": "Apple Inc."
        }

    Examples:
        # Get CIK for Apple
        result = get_company_cik(ticker="AAPL")
        cik = result.get('cik')
        print(f"Apple CIK: {cik}")

        # Use CIK for subsequent queries
        filings = get_company_submissions(cik_or_ticker=cik)
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'get_company_cik',
        'ticker': ticker
    }

    return client.call_tool('sec-edgar', params)


def get_company_submissions(
    cik_or_ticker: str
) -> Dict[str, Any]:
    """
    Get complete filing history for a company

    Args:
        cik_or_ticker: Company CIK (10-digit) or ticker symbol
                      Examples: "0000320193", "AAPL", "0000789019", "MSFT"

    Returns:
        dict: Company filing history

        Key fields:
        - cik: Central Index Key
        - entityName: Company name
        - filings.recent.accessionNumber: Filing IDs
        - filings.recent.primaryDocument: Document filenames
        - filings.recent.form: Filing types (10-K, 10-Q, 8-K, etc.)
        - filings.recent.filingDate: Filing dates
        - filings.recent.reportDate: Period end dates

    Examples:
        # Get all filings for Apple
        filings = get_company_submissions(cik_or_ticker="AAPL")

        # Extract recent filings
        entity_name = filings.get('entityName')
        recent = filings.get('filings', {}).get('recent', {})

        forms = recent.get('form', [])
        dates = recent.get('filingDate', [])
        accessions = recent.get('accessionNumber', [])

        print(f"{entity_name} - Recent Filings:")
        for form, date, accession in zip(forms[:10], dates[:10], accessions[:10]):
            print(f"  {date}: {form} ({accession})")

        # Use filter_filings to narrow results
        annual_reports = filter_filings(
            filings=filings,
            form_type="10-K",
            start_date="2020-01-01",
            end_date="2024-12-31"
        )
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'get_company_submissions',
        'cik_or_ticker': cik_or_ticker
    }

    return client.call_tool('sec-edgar', params)


def get_company_facts(
    cik_or_ticker: str
) -> Dict[str, Any]:
    """
    Get all XBRL financial data (structured metrics) for a company

    Returns standardized financial metrics across all filings.

    Args:
        cik_or_ticker: Company CIK or ticker
                      Examples: "0000320193", "AAPL"

    Returns:
        dict: XBRL financial facts

        Key concepts (US GAAP):
        - Assets: Total assets
        - Revenues: Revenue/sales
        - NetIncomeLoss: Net income
        - StockholdersEquity: Shareholders' equity
        - Cash: Cash and equivalents
        - Liabilities: Total liabilities
        - OperatingIncomeLoss: Operating income

    Examples:
        # Get all financial facts for Apple
        facts = get_company_facts(cik_or_ticker="AAPL")

        # Extract revenue data
        us_gaap = facts.get('facts', {}).get('us-gaap', {})
        revenues = us_gaap.get('Revenues', {})

        # Get units (typically USD)
        usd_data = revenues.get('units', {}).get('USD', [])

        # Extract recent annual revenues
        annual_revenues = []
        for item in usd_data:
            if item.get('form') == '10-K':  # Annual reports only
                fiscal_year = item.get('fy')
                value = item.get('val')
                end_date = item.get('end')
                annual_revenues.append((fiscal_year, value, end_date))

        # Sort by fiscal year
        annual_revenues.sort(key=lambda x: x[0], reverse=True)

        print("Recent Annual Revenues:")
        for fy, value, date in annual_revenues[:5]:
            print(f"  FY{fy} ({date}): ${value:,.0f}")
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'get_company_facts',
        'cik_or_ticker': cik_or_ticker
    }

    return client.call_tool('sec-edgar', params)


def get_company_concept(
    cik_or_ticker: str,
    taxonomy: str,
    tag: str
) -> Dict[str, Any]:
    """
    Get specific financial concept (metric) for a company

    More focused than get_company_facts - retrieves single metric.

    Args:
        cik_or_ticker: Company CIK or ticker

        taxonomy: XBRL taxonomy
                 Common values:
                 - "us-gaap" - US GAAP concepts
                 - "dei" - Document Entity Information
                 - "invest" - Investment Company concepts

        tag: Specific concept tag
            Common US GAAP tags:
            - "Assets" - Total assets
            - "Revenues" - Revenue/sales
            - "NetIncomeLoss" - Net income
            - "StockholdersEquity" - Equity
            - "Cash" - Cash and equivalents
            - "Liabilities" - Total liabilities
            - "OperatingIncomeLoss" - Operating income

    Returns:
        dict: Time series data for specific concept

    Examples:
        # Get revenue history for Apple
        revenue = get_company_concept(
            cik_or_ticker="AAPL",
            taxonomy="us-gaap",
            tag="Revenues"
        )

        # Extract values
        usd_data = revenue.get('units', {}).get('USD', [])

        # Filter for annual values
        annual_values = [
            (item['fy'], item['val'], item['end'])
            for item in usd_data
            if item.get('form') == '10-K'
        ]

        annual_values.sort(key=lambda x: x[0], reverse=True)

        print("Revenue History:")
        for fy, value, date in annual_values[:10]:
            print(f"  FY{fy}: ${value:,.0f}")

        # Get assets
        assets = get_company_concept(
            cik_or_ticker="AAPL",
            taxonomy="us-gaap",
            tag="Assets"
        )
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'get_company_concept',
        'cik_or_ticker': cik_or_ticker,
        'taxonomy': taxonomy,
        'tag': tag
    }

    return client.call_tool('sec-edgar', params)


def get_frames_data(
    taxonomy: str,
    tag: str,
    unit: str,
    frame: str
) -> Dict[str, Any]:
    """
    Get aggregated data across ALL companies for a specific metric and time period

    Useful for comparative analysis and industry benchmarking.

    Args:
        taxonomy: XBRL taxonomy (e.g., "us-gaap")

        tag: Concept tag (e.g., "Revenues", "Assets")

        unit: Unit of measure
             Common values:
             - "USD" - US Dollars
             - "shares" - Share counts
             - "pure" - Ratios/percentages

        frame: Reporting frame
              Format examples:
              - "CY2021Q4I" - Calendar Year 2021 Q4 Instant
              - "CY2021" - Calendar Year 2021 annual
              - "CY2020Q4I" - Calendar Year 2020 Q4
              - "Q1", "Q2", "Q3", "Q4" - Any year quarter

    Returns:
        dict: Aggregated data across companies

        Key fields:
        - data: Array of company values
        - Each entry has: cik, entityName, loc, val

    Examples:
        # Get revenues for all companies in CY2021
        frame_data = get_frames_data(
            taxonomy="us-gaap",
            tag="Revenues",
            unit="USD",
            frame="CY2021"
        )

        # Extract and rank companies
        companies = []
        for item in frame_data.get('data', []):
            cik = item.get('cik')
            name = item.get('entityName')
            value = item.get('val')
            companies.append((name, value, cik))

        # Sort by revenue
        companies.sort(key=lambda x: x[1], reverse=True)

        print("Top 20 Companies by Revenue (CY2021):")
        for name, revenue, cik in companies[:20]:
            print(f"  {name}: ${revenue:,.0f}")

        # Get Q4 2021 instant data
        q4_data = get_frames_data(
            taxonomy="us-gaap",
            tag="Assets",
            unit="USD",
            frame="CY2021Q4I"
        )
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'get_frames_data',
        'taxonomy': taxonomy,
        'tag': tag,
        'unit': unit,
        'frame': frame
    }

    return client.call_tool('sec-edgar', params)


def filter_filings(
    filings: Dict[str, Any],
    form_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Filter company filings by form type and date range

    Use after get_company_submissions to narrow results.

    Args:
        filings: Filings object from get_company_submissions

        form_type: Filing form type
                  Common types:
                  - "10-K" - Annual reports (Item 1, Item 7 for pipeline)
                  - "10-Q" - Quarterly reports
                  - "8-K" - Current reports (M&A, material events)
                  - "20-F" - Foreign company annual
                  - "DEF 14A" - Proxy statements
                  - "S-1" - IPO registration
                  - "4" - Insider trading
                  - "3" - Initial insider ownership

        start_date: Start date for filing date range
                   Format: "YYYY-MM-DD" (e.g., "2020-01-01")

        end_date: End date for filing date range
                 Format: "YYYY-MM-DD" (e.g., "2024-12-31")

        limit: Maximum number of results

    Returns:
        dict: Filtered filings

    Examples:
        # Get all filings first
        all_filings = get_company_submissions(cik_or_ticker="AAPL")

        # Filter for annual reports in last 5 years
        annual_reports = filter_filings(
            filings=all_filings,
            form_type="10-K",
            start_date="2019-01-01",
            end_date="2024-12-31"
        )

        # Process filtered results
        for filing in annual_reports.get('filings', []):
            form = filing.get('form')
            date = filing.get('filingDate')
            accession = filing.get('accessionNumber')
            print(f"{date}: {form} - {accession}")

        # Filter for recent M&A activity (8-K filings)
        current_events = filter_filings(
            filings=all_filings,
            form_type="8-K",
            start_date="2023-01-01",
            limit=10
        )

        # Filter for quarterly reports in 2023
        quarterly_2023 = filter_filings(
            filings=all_filings,
            form_type="10-Q",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
    """
    client = get_client('sec-mcp-server')

    params = {
        'method': 'filter_filings',
        'filings': filings
    }

    if form_type:
        params['form_type'] = form_type
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    if limit:
        params['limit'] = limit

    return client.call_tool('sec-edgar', params)


__all__ = [
    'search_companies',
    'get_company_cik',
    'get_company_submissions',
    'get_company_facts',
    'get_company_concept',
    'get_frames_data',
    'filter_filings'
]
