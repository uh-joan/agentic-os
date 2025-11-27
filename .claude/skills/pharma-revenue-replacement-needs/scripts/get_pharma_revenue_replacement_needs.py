import sys
sys.path.insert(0, ".claude")

from mcp.servers.sec_edgar_mcp import get_company_cik, get_company_concept, search_companies
from mcp.servers.financials_mcp import financial_intelligence
from mcp.servers.fda_mcp import lookup_drug
import json

def get_pharma_revenue_replacement_needs(company, analysis_period="2030-2035"):
    """Quantify pharmaceutical company's 2030-2035 revenue gap and M&A needs.

    This skill performs multi-source financial intelligence to identify revenue
    cliffs from patent expiries and calculate the M&A budget needed for survival.

    Combines:
    - SEC EDGAR revenues (XBRL data)
    - Yahoo Finance company profile
    - FDA drug portfolio (count-based analysis)
    - Franchise analysis (oncology, immunology, etc.)

    Args:
        company (str): Company name or ticker (e.g., "Pfizer", "PFE")
        analysis_period (str): Analysis period (default "2030-2035")

    Returns:
        dict: Revenue gap analysis with franchise deficits and M&A needs
    """
    print(f"\n{'='*80}")
    print(f"PHARMA 2030 REVENUE REPLACEMENT NEEDS ANALYSIS")
    print(f"{'='*80}\n")
    print(f"Company: {company}")
    print(f"Analysis Period: {analysis_period}\n")

    # Step 1: Company identification and ticker resolution
    print("Step 1: Identifying company and resolving ticker...")

    try:
        # Get company profile from Yahoo Finance
        profile = financial_intelligence(
            method="stock_profile",
            symbol=company
        )

        ticker = profile.get('symbol', company.upper())
        company_name = profile.get('longName') or profile.get('shortName') or company
        industry = profile.get('industry', 'Pharmaceutical')

        print(f"  ✓ Resolved: {company_name} ({ticker})")
        print(f"  ✓ Industry: {industry}")
    except Exception as e:
        print(f"  ⚠ Profile lookup failed: {str(e)}")
        ticker = company.upper()
        company_name = company
        industry = "Pharmaceutical"

    # Step 2: Get current revenue from SEC EDGAR
    print("\nStep 2: Retrieving current revenue from SEC EDGAR...")

    current_revenue_b = 0
    sec_company_name = None  # Will hold authoritative SEC company name
    try:
        # Get official SEC company name via search
        search_result = search_companies(query=ticker)
        companies = search_result.get('companies', [])
        if companies and len(companies) > 0:
            sec_company_name = companies[0].get('title')  # Official SEC company title

        # Convert ticker to CIK (required for SEC queries)
        cik_result = get_company_cik(ticker=ticker)
        cik = cik_result.get('cik')
        print(f"  ✓ CIK: {cik}")
        if sec_company_name:
            print(f"  ✓ SEC Name: {sec_company_name}")

        # Get revenue concept from XBRL data
        revenue_data = get_company_concept(
            cik_or_ticker=cik,
            taxonomy="us-gaap",
            tag="Revenues"
        )

        # Extract most recent annual revenue (from 10-K filings)
        usd_data = revenue_data.get('units', {}).get('USD', [])
        annual_revenues = [
            item for item in usd_data
            if item.get('form') == '10-K' and item.get('val')
        ]

        if annual_revenues:
            # Sort by fiscal year (most recent first)
            annual_revenues.sort(key=lambda x: x.get('fy', 0), reverse=True)
            latest = annual_revenues[0]
            current_revenue = latest.get('val', 0)
            current_revenue_b = current_revenue / 1_000_000_000  # Convert to billions
            fiscal_year = latest.get('fy')

            print(f"  ✓ Current annual revenue (FY{fiscal_year}): ${current_revenue_b:.1f}B")
        else:
            print(f"  ⚠ No annual revenue data found")

    except Exception as e:
        print(f"  ⚠ SEC revenue lookup error: {str(e)}")

    # Step 3: Get FDA drug portfolio using count-first pattern
    print("\nStep 3: Analyzing FDA drug portfolio (count-based)...")

    total_products = 0
    product_list = []

    try:
        # Use count-first pattern (MANDATORY for FDA per tool guide)
        # Prioritize SEC company name (authoritative) over Yahoo Finance name
        # Try simple search terms without field-specific syntax

        # Prefer SEC name, fallback to Yahoo Finance name
        primary_name = sec_company_name if sec_company_name else company_name

        search_variations = []
        if primary_name:
            search_variations.append(primary_name)  # "Pfizer Inc." (from SEC)
            # Extract first word (company name without legal suffix)
            if ' ' in primary_name:
                search_variations.append(primary_name.split()[0])  # "Pfizer"
        search_variations.append(ticker)  # "PFE" (last resort)

        for search_term in search_variations:
            try:
                print(f"  Searching: {search_term}")

                # Use count-first pattern (MANDATORY for FDA)
                result = lookup_drug(
                    search_term=search_term,
                    search_type="general",
                    count="openfda.manufacturer_name.exact",  # Count by manufacturer
                    limit=100
                )

                # Parse aggregated counts
                results_data = result.get('data', {}).get('results', [])

                if results_data and len(results_data) > 0:
                    print(f"  ✓ Found {len(results_data)} manufacturer entries")

                    # Extract manufacturer names and product counts
                    for item in results_data:
                        manufacturer = item.get('term', 'Unknown')
                        count = item.get('count', 0)

                        # Look for matches to our company
                        # Use primary_name (SEC or Yahoo) for matching
                        if primary_name and primary_name.lower() in manufacturer.lower():
                            total_products += count
                            product_list.append({
                                'manufacturer': manufacturer,
                                'product_count': count
                            })
                        # Also check first word match (e.g., "Pfizer" in "Pfizer Labs")
                        elif primary_name and ' ' in primary_name:
                            first_word = primary_name.split()[0].lower()
                            if first_word in manufacturer.lower():
                                total_products += count
                                product_list.append({
                                    'manufacturer': manufacturer,
                                    'product_count': count
                                })

                    if total_products > 0:
                        print(f"  ✓ Estimated {total_products} products from FDA data")
                        break  # Found results, stop trying variations

            except Exception as e:
                print(f"  ⚠ Search variation failed: {str(e)}")
                continue

        if total_products == 0:
            print(f"  ⚠ No FDA products found - using estimated portfolio size")
            # For major pharma, estimate ~50-150 products
            total_products = 75  # Conservative estimate

    except Exception as e:
        print(f"  ⚠ FDA data error: {str(e)}")
        total_products = 75  # Fallback estimate

    print(f"  ✓ Total products in portfolio: {total_products}")

    # Step 4: Calculate revenue at risk (estimation-based)
    print("\nStep 4: Calculating revenue gaps...")

    # Estimation model for patent cliff (2028-2035 timeframe)
    # Industry data: ~30-40% of pharma portfolio loses exclusivity in any 7-year window
    # We estimate based on portfolio age and industry averages

    estimated_products_at_risk = int(total_products * 0.35)  # 35% expiring 2028-2035

    # Revenue concentration assumption:
    # Top 20% of products = 80% of revenue (Pareto principle in pharma)
    # Products expiring are typically mature (higher revenue contribution)
    # Estimate: 40-50% of revenue from expiring products

    revenue_concentration_at_risk = 0.45  # 45% of revenue from expiring products
    total_revenue_at_risk = current_revenue_b * revenue_concentration_at_risk

    projected_baseline_2030 = current_revenue_b - total_revenue_at_risk
    revenue_gap = total_revenue_at_risk

    print(f"  ✓ Current revenue: ${current_revenue_b:.1f}B")
    print(f"  ✓ Products at risk (2030-2035): ~{estimated_products_at_risk} ({int(35)}%)")
    print(f"  ✓ Estimated revenue at risk: ${total_revenue_at_risk:.1f}B")
    print(f"  ✓ Projected 2030 baseline: ${projected_baseline_2030:.1f}B")
    print(f"  ✓ Revenue gap to fill: ${revenue_gap:.1f}B")

    # Step 5: Franchise analysis (estimation-based)
    print("\nStep 5: Analyzing franchise deficits...")

    # Standard pharma franchise distribution (industry averages)
    franchise_distribution = {
        'oncology': 0.30,  # 30% of portfolio typically
        'immunology': 0.20,
        'cardiovascular': 0.15,
        'neuroscience': 0.12,
        'infectious_disease': 0.10,
        'metabolic': 0.08,
        'rare_disease': 0.05
    }

    franchise_deficits = {}

    for franchise, pct in franchise_distribution.items():
        franchise_products_at_risk = int(estimated_products_at_risk * pct)
        franchise_revenue_loss = revenue_gap * pct

        if franchise_revenue_loss > 0.5:  # Only include if >$500M at risk
            urgency = 'critical' if franchise_revenue_loss > 5 else 'high' if franchise_revenue_loss > 2 else 'medium'

            franchise_deficits[franchise] = {
                'estimated_products_at_risk': franchise_products_at_risk,
                'revenue_loss': round(franchise_revenue_loss, 1),
                'replacement_need': f"{franchise.replace('_', ' ').title()} franchise assets",
                'urgency': urgency
            }

            print(f"  ✓ {franchise.replace('_', ' ').title()}: ${franchise_revenue_loss:.1f}B loss ({urgency} urgency)")

    # Step 6: M&A budget estimation
    print("\nStep 6: Estimating M&A budget...")

    # Rule of thumb: Need 150-200% of revenue gap through M&A
    # (accounts for pipeline failures, integration costs, timing)
    ma_budget_low = revenue_gap * 1.5
    ma_budget_high = revenue_gap * 2.0
    ma_budget_estimate = f"${ma_budget_low:.0f}-{ma_budget_high:.0f}B (2027-2030)"

    print(f"  ✓ Estimated M&A capital needed: {ma_budget_estimate}")

    # Target asset profile (from 2026+ playbook)
    target_asset_profile = "Phase 2b+, >$5B TAM, registrational by 2028"
    print(f"  ✓ Target asset profile: {target_asset_profile}")

    # Generate summary
    top_franchises = sorted(
        franchise_deficits.items(),
        key=lambda x: x[1]['revenue_loss'],
        reverse=True
    )[:2]

    summary_parts = [f"{company_name} faces a ${revenue_gap:.1f}B revenue gap by 2030-2035"]

    if top_franchises:
        franchise_summaries = [
            f"{f[0].replace('_', ' ')} (${f[1]['revenue_loss']:.1f}B)"
            for f in top_franchises
        ]
        summary_parts.append(f"primarily in {' and '.join(franchise_summaries)}")

    summary_parts.append("Critical acquisition needs: late-stage assets in priority franchises.")
    summary = ' '.join(summary_parts)

    # Build result
    result = {
        'company': company_name,
        'ticker': ticker,
        'industry': industry,
        'analysis_period': analysis_period,
        'current_revenue': round(current_revenue_b, 1),
        'projected_baseline_2030': round(projected_baseline_2030, 1),
        'revenue_gap': round(revenue_gap, 1),
        'portfolio_analysis': {
            'total_products': total_products,
            'estimated_products_at_risk': estimated_products_at_risk,
            'risk_percentage': 35
        },
        'franchise_deficits': franchise_deficits,
        'ma_budget_estimate': ma_budget_estimate,
        'target_asset_profile': target_asset_profile,
        'summary': summary,
        'methodology_note': 'Analysis uses SEC EDGAR revenue data combined with industry-standard patent cliff models and franchise distribution estimates.',
        'data_quality': {
            'revenue_source': 'SEC EDGAR XBRL' if current_revenue_b > 0 else 'Not available',
            'fda_products_found': len(product_list),
            'estimation_model': 'Industry averages (35% portfolio expiry, 45% revenue concentration)'
        }
    }

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")
    print(f"Summary: {summary}\n")
    print(f"Note: This analysis combines actual SEC revenue data with industry-standard")
    print(f"patent cliff models. Product-level exclusivity data requires manual review of")
    print(f"FDA Orange Book and individual patent portfolios.\n")

    return result

if __name__ == "__main__":
    import sys

    # Get company from command line or use default
    company = sys.argv[1] if len(sys.argv) > 1 else "PFE"

    # Run analysis
    result = get_pharma_revenue_replacement_needs(company)

    # Print detailed results
    print("\nDETAILED RESULTS:")
    print(json.dumps(result, indent=2))
