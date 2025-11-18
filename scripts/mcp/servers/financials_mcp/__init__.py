"""Financial Intelligence MCP Server - Python API

Provides Python functions for Yahoo Finance stock data and Federal Reserve economic data (FRED).
Data stays in execution environment - only summaries flow to model.

CRITICAL FINANCIAL INTELLIGENCE QUIRKS:
1. Unified tool: Single tool (financial-intelligence) with method parameter for all queries
2. Symbol input: Stock tickers for stock methods, search terms for economic methods
3. FRED API key: Required for full FRED functionality (set FRED_API_KEY env var)
4. Sentiment analysis: Automated bullish/bearish classification for news
5. Rate limiting: 120 req/min for FRED, automatic throttling for Yahoo Finance
6. Response format: JSON with nested data structures
7. Search vs Data: fred_series_search (no API key) vs fred_series_data (requires key)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def financial_intelligence(
    method: str,
    symbol: str = ""
) -> Dict[str, Any]:
    """
    Unified financial and economic intelligence tool

    Provides access to 27 methods across stock analysis, economic data, and advanced analytics.

    Args:
        method: The analysis method to perform (REQUIRED)

               STOCK ANALYSIS METHODS (11):
               - "stock_profile" - Company details, address, industry, employees, business summary
               - "stock_summary" - Key metrics: market cap, P/E, EPS, beta, enterprise values
               - "stock_estimates" - Analyst EPS/revenue estimates, price targets, recommendations
               - "stock_pricing" - Real-time pricing, volume, daily ranges, extended hours
               - "stock_financials" - Cash flow, income highlights, balance sheet ratios
               - "stock_revenue_breakdown" - Revenue by business segment & geography
               - "stock_earnings_history" - Historical EPS trends & earnings analysis
               - "stock_recommendations" - Analyst rating trends & consensus changes
               - "stock_esg" - Environmental, Social, Governance scores & controversies
               - "stock_dividends" - Dividend history, yield calculations, payout ratios
               - "stock_technicals" - Technical indicators, moving averages, volatility

               ADVANCED ANALYTICS METHODS (4):
               - "stock_news" - Recent news with sentiment analysis (stock-specific or general search)
               - "stock_peers" - Industry peer comparison based on key financial metrics
               - "stock_screener" - Multi-criteria stock discovery (filter by P/E, market cap, etc.)
               - "stock_correlation" - Portfolio correlation analysis for risk management

               ECONOMIC & MARKET METHODS (2):
               - "economic_indicators" - Comprehensive macro dashboard (GDP, unemployment, inflation, rates)
               - "market_indices" - Major indices (S&P 500, NASDAQ, DOW, VIX) & sector performance

               FRED ECONOMIC DATA METHODS (12):
               - "fred_series_search" - Search 800,000+ economic series by keywords (NO API KEY REQUIRED)
               - "fred_series_data" - Fetch specific FRED series observations (REQUIRES API KEY)
               - "fred_categories" - Browse economic data categories hierarchically (REQUIRES API KEY)
               - "fred_releases" - Economic calendar with release schedules (REQUIRES API KEY)
               - "fred_vintage_data" - Historical data revision analysis (REQUIRES API KEY)
               - "fred_tags" - Tag-based economic concept discovery (REQUIRES API KEY)
               - "fred_regional_data" - Geographic economic analysis (state/MSA data) (REQUIRES API KEY)
               - "fred_sources" - Data source transparency and quality assessment (REQUIRES API KEY)
               - "fred_series_updates" - Real-time monitoring of recently updated indicators (REQUIRES API KEY)
               - "fred_series_relationships" - Deep metadata analysis and series connections (REQUIRES API KEY)
               - "fred_maps_data" - Geographic economic data visualization and mapping (REQUIRES API KEY)

        symbol: Input parameter (context-dependent)

               FOR STOCK METHODS: Stock ticker symbol
               Examples: "AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"

               FOR SEARCH METHODS: Search terms/keywords
               Examples: "unemployment", "GDP", "inflation", "tesla bitcoin"

               FOR SCREENER: JSON criteria object
               Example: '{"maxPE":20,"minMarketCap":1000000000,"minDividendYield":2}'

               FOR CORRELATION: Comma-separated symbols
               Example: "AAPL,MSFT,GOOGL,AMZN,TSLA"

               FOR FRED DATA: Series ID, category ID, or search terms
               Examples: "UNRATE" (unemployment), "GDP", "10" (category), "regional"

               FOR MARKET/ECONOMIC: Empty string or any value (ignored)
               Example: "" or "market_overview"

    Returns:
        dict: Method-specific financial or economic data

    Examples:
        # Example 1: Stock profile analysis
        profile = financial_intelligence(
            method="stock_profile",
            symbol="AAPL"
        )

        company_name = profile.get('companyName')
        industry = profile.get('industry')
        employees = profile.get('fullTimeEmployees')
        summary = profile.get('longBusinessSummary')

        print(f"{company_name} ({industry})")
        print(f"Employees: {employees:,}")
        print(f"Summary: {summary[:200]}...")

        # Example 2: Key financial metrics
        summary = financial_intelligence(
            method="stock_summary",
            symbol="TSLA"
        )

        market_cap = summary.get('marketCap')
        pe_ratio = summary.get('trailingPE')
        eps = summary.get('trailingEPS')
        beta = summary.get('beta')

        print(f"Market Cap: ${market_cap:,.0f}")
        print(f"P/E Ratio: {pe_ratio:.2f}")
        print(f"EPS: ${eps:.2f}")
        print(f"Beta: {beta:.2f}")

        # Example 3: Analyst estimates and price targets
        estimates = financial_intelligence(
            method="stock_estimates",
            symbol="GOOGL"
        )

        current_price = estimates.get('currentPrice')
        target_mean = estimates.get('targetMeanPrice')
        target_high = estimates.get('targetHighPrice')
        target_low = estimates.get('targetLowPrice')

        upside = ((target_mean - current_price) / current_price * 100) if target_mean and current_price else 0

        print(f"Current Price: ${current_price:.2f}")
        print(f"Target Price: ${target_mean:.2f} ({upside:+.1f}% upside)")
        print(f"Range: ${target_low:.2f} - ${target_high:.2f}")

        # Example 4: Real-time pricing
        pricing = financial_intelligence(
            method="stock_pricing",
            symbol="MSFT"
        )

        current_price = pricing.get('regularMarketPrice')
        change = pricing.get('regularMarketChange')
        change_pct = pricing.get('regularMarketChangePercent')
        volume = pricing.get('regularMarketVolume')
        market_state = pricing.get('marketState')

        print(f"Price: ${current_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
        print(f"Volume: {volume:,}")
        print(f"Market: {market_state}")

        # Example 5: Financial performance
        financials = financial_intelligence(
            method="stock_financials",
            symbol="AMZN"
        )

        revenue = financials.get('totalRevenue')
        operating_cf = financials.get('operatingCashflow')
        ebitda = financials.get('ebitda')
        profit_margin = financials.get('profitMargins')

        print(f"Revenue: ${revenue:,.0f}")
        print(f"Operating Cash Flow: ${operating_cf:,.0f}")
        print(f"EBITDA: ${ebitda:,.0f}")
        print(f"Profit Margin: {profit_margin*100:.2f}%")

        # Example 6: Revenue breakdown by segment and geography
        breakdown = financial_intelligence(
            method="stock_revenue_breakdown",
            symbol="TSLA"
        )

        # Analyze by segment
        segments = breakdown.get('segments', {})
        for segment, revenue in segments.items():
            print(f"{segment}: ${revenue:,.0f}")

        # Analyze by geography
        geography = breakdown.get('geography', {})
        for region, revenue in geography.items():
            pct = (revenue / sum(geography.values()) * 100) if geography else 0
            print(f"{region}: ${revenue:,.0f} ({pct:.1f}%)")

        # Example 7: News with sentiment analysis
        news = financial_intelligence(
            method="stock_news",
            symbol="AAPL"
        )

        for article in news.get('news', [])[:5]:
            title = article.get('title')
            sentiment = article.get('sentiment')
            score = article.get('sentimentScore', 0)
            publisher = article.get('publisher')

            sentiment_emoji = "📈" if sentiment == "bullish" else "📉" if sentiment == "bearish" else "➖"
            print(f"{sentiment_emoji} {title}")
            print(f"   {publisher} | Sentiment: {sentiment} ({score:+.2f})")

        # Example 8: General market news search
        market_news = financial_intelligence(
            method="stock_news",
            symbol="fed rate cuts"
        )

        # Example 9: Peer comparison
        peers = financial_intelligence(
            method="stock_peers",
            symbol="NVDA"
        )

        print("NVDA vs Peers:")
        for peer in peers.get('peers', []):
            symbol = peer.get('symbol')
            name = peer.get('name')
            market_cap = peer.get('marketCap')
            pe_ratio = peer.get('trailingPE')
            print(f"{symbol} - {name}")
            print(f"  Market Cap: ${market_cap:,.0f}, P/E: {pe_ratio:.2f}")

        # Example 10: Stock screener - value stocks
        screener_results = financial_intelligence(
            method="stock_screener",
            symbol='{"maxPE":15,"minDividendYield":0.03,"minMarketCap":1000000000}'
        )

        print("Value Stocks (P/E < 15, Div Yield > 3%, Market Cap > $1B):")
        for stock in screener_results.get('results', []):
            ticker = stock.get('symbol')
            name = stock.get('name')
            pe = stock.get('trailingPE')
            div_yield = stock.get('dividendYield', 0) * 100
            print(f"{ticker}: P/E {pe:.2f}, Yield {div_yield:.2f}%")

        # Example 11: Portfolio correlation analysis
        correlation = financial_intelligence(
            method="stock_correlation",
            symbol="AAPL,MSFT,GOOGL,AMZN,TSLA"
        )

        # Extract correlation matrix
        matrix = correlation.get('correlationMatrix', {})

        print("Portfolio Correlation Matrix:")
        for stock1, correlations in matrix.items():
            print(f"\n{stock1}:")
            for stock2, corr_value in correlations.items():
                if stock1 != stock2:
                    print(f"  vs {stock2}: {corr_value:.3f}")

        # Example 12: Economic indicators dashboard
        econ = financial_intelligence(
            method="economic_indicators",
            symbol=""
        )

        gdp = econ.get('GDP')
        unemployment = econ.get('unemployment')
        inflation = econ.get('inflation')
        fed_rate = econ.get('fedFundsRate')

        print(f"GDP Growth: {gdp}%")
        print(f"Unemployment: {unemployment}%")
        print(f"Inflation: {inflation}%")
        print(f"Fed Funds Rate: {fed_rate}%")

        # Example 13: Market indices overview
        indices = financial_intelligence(
            method="market_indices",
            symbol=""
        )

        sp500 = indices.get('SP500')
        nasdaq = indices.get('NASDAQ')
        dow = indices.get('DOW')
        vix = indices.get('VIX')

        print(f"S&P 500: {sp500.get('price')} ({sp500.get('change'):+.2f}%)")
        print(f"NASDAQ: {nasdaq.get('price')} ({nasdaq.get('change'):+.2f}%)")
        print(f"DOW: {dow.get('price')} ({dow.get('change'):+.2f}%)")
        print(f"VIX: {vix.get('price')}")

        # Example 14: FRED series search (NO API KEY REQUIRED)
        search_results = financial_intelligence(
            method="fred_series_search",
            symbol="unemployment"
        )

        print("Unemployment-related series:")
        for series in search_results.get('series', [])[:10]:
            series_id = series.get('id')
            title = series.get('title')
            print(f"{series_id}: {title}")

        # Example 15: FRED series data (REQUIRES API KEY)
        unemployment_data = financial_intelligence(
            method="fred_series_data",
            symbol="UNRATE"
        )

        observations = unemployment_data.get('observations', [])
        if observations:
            latest = observations[-1]
            date = latest.get('date')
            value = latest.get('value')
            print(f"Latest Unemployment Rate ({date}): {value}%")

            # Calculate trend
            if len(observations) >= 12:
                year_ago = observations[-13].get('value')
                change = float(value) - float(year_ago)
                print(f"Year-over-year change: {change:+.2f}%")

        # Example 16: FRED categories (browse economic data)
        categories = financial_intelligence(
            method="fred_categories",
            symbol=""
        )

        print("Root Economic Categories:")
        for category in categories.get('categories', []):
            cat_id = category.get('id')
            name = category.get('name')
            print(f"{cat_id}: {name}")

        # Example 17: Economic calendar
        releases = financial_intelligence(
            method="fred_releases",
            symbol=""
        )

        print("Upcoming Economic Releases:")
        for release in releases.get('releases', [])[:10]:
            name = release.get('name')
            next_release = release.get('realtime_start')
            print(f"{name}: {next_release}")

        # Example 18: Historical data revisions
        vintage_data = financial_intelligence(
            method="fred_vintage_data",
            symbol="GDP"
        )

        print("GDP Data Revisions:")
        vintages = vintage_data.get('vintages', [])
        for vintage in vintages[:5]:
            vintage_date = vintage.get('vintage_date')
            value = vintage.get('value')
            print(f"{vintage_date}: {value}")

        # Example 19: Tag-based discovery
        tags = financial_intelligence(
            method="fred_tags",
            symbol="inflation"
        )

        print("Inflation-related tags:")
        for tag in tags.get('tags', [])[:10]:
            tag_name = tag.get('name')
            series_count = tag.get('series_count')
            print(f"{tag_name}: {series_count} series")

        # Example 20: Regional economic data
        regional = financial_intelligence(
            method="fred_regional_data",
            symbol="california"
        )

        print("California Economic Data:")
        for series in regional.get('series', [])[:10]:
            title = series.get('title')
            series_id = series.get('id')
            print(f"{series_id}: {title}")

        # Example 21: Data source transparency
        sources = financial_intelligence(
            method="fred_sources",
            symbol=""
        )

        print("FRED Data Sources:")
        for source in sources.get('sources', [])[:10]:
            source_id = source.get('id')
            name = source.get('name')
            link = source.get('link')
            print(f"{source_id}. {name}")
            print(f"   {link}")

        # Example 22: Recently updated series
        updates = financial_intelligence(
            method="fred_series_updates",
            symbol=""
        )

        print("Recently Updated Economic Indicators:")
        for series in updates.get('series', [])[:10]:
            series_id = series.get('id')
            title = series.get('title')
            last_updated = series.get('last_updated')
            print(f"{series_id} ({last_updated}): {title}")

        # Example 23: Series relationships and metadata
        relationships = financial_intelligence(
            method="fred_series_relationships",
            symbol="UNRATE"
        )

        print("UNRATE Relationships:")
        related_series = relationships.get('related_series', [])
        for series in related_series[:5]:
            series_id = series.get('id')
            title = series.get('title')
            print(f"  {series_id}: {title}")

        # Example 24: Geographic economic mapping
        maps_data = financial_intelligence(
            method="fred_maps_data",
            symbol="state"
        )

        print("State-level Economic Data:")
        for series in maps_data.get('series', [])[:10]:
            title = series.get('title')
            series_id = series.get('id')
            print(f"{series_id}: {title}")

        # Example 25: Dividend analysis
        dividends = financial_intelligence(
            method="stock_dividends",
            symbol="KO"
        )

        div_yield = dividends.get('dividendYield', 0) * 100
        payout_ratio = dividends.get('payoutRatio', 0) * 100
        five_year_avg = dividends.get('fiveYearAvgDividendYield', 0) * 100

        print(f"Dividend Yield: {div_yield:.2f}%")
        print(f"Payout Ratio: {payout_ratio:.2f}%")
        print(f"5-Year Avg Yield: {five_year_avg:.2f}%")

        # Example 26: Technical analysis
        technicals = financial_intelligence(
            method="stock_technicals",
            symbol="SPY"
        )

        sma_50 = technicals.get('fiftyDayAverage')
        sma_200 = technicals.get('twoHundredDayAverage')
        current_price = technicals.get('regularMarketPrice')

        print(f"Current: ${current_price:.2f}")
        print(f"50-day MA: ${sma_50:.2f}")
        print(f"200-day MA: ${sma_200:.2f}")

        if sma_50 and sma_200:
            if sma_50 > sma_200:
                print("Signal: Golden Cross (Bullish)")
            else:
                print("Signal: Death Cross (Bearish)")

        # Example 27: ESG scoring
        esg = financial_intelligence(
            method="stock_esg",
            symbol="TSLA"
        )

        total_esg = esg.get('totalEsg')
        environment = esg.get('environmentScore')
        social = esg.get('socialScore')
        governance = esg.get('governanceScore')

        print(f"Total ESG Score: {total_esg}")
        print(f"  Environment: {environment}")
        print(f"  Social: {social}")
        print(f"  Governance: {governance}")
    """
    client = get_client('financials-mcp-server')

    params = {
        'method': method,
        'symbol': symbol
    }

    return client.call_tool('financial-intelligence', params)


__all__ = ['financial_intelligence']
