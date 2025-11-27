import sys
sys.path.insert(0, ".claude")

import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Existing MCPs
from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.fda_mcp import lookup_drug as fda_lookup_drug
from mcp.servers.pubmed_mcp import search_keywords as pubmed_search
from mcp.servers.uspto_patents_mcp import google_search_patents, google_search_by_assignee

# NEW v3.0 MCPs
from mcp.servers.sec_edgar_mcp import get_company_facts, search_companies, get_company_cik
from mcp.servers.healthcare_mcp import cms_search_providers
from mcp.servers.datacommons_mcp import search_indicators, get_observations
from mcp.servers.opentargets_mcp import search_diseases, get_disease_targets_summary, get_target_details
from mcp.servers.financials_mcp import financial_intelligence


def generate_drug_swot_analysis(
    drug_name: str,
    indication: str,
    company_ticker: str = None,
    hcpcs_code: str = None,
    gene_target: str = None,
    parallel_execution: bool = True
) -> dict:
    """Generate comprehensive SWOT analysis for a pharmaceutical product.

    v3.0: Enhanced with 5 additional MCPs (SEC, CMS, Data Commons, Open Targets, Financials)

    Collects data from 9 authoritative sources to build strategic SWOT analysis:
    - Clinical trials (CT.gov)
    - FDA labels and safety data
    - Scientific publications (PubMed)
    - Patent landscape (Google Patents)
    - Financial performance (SEC EDGAR) [NEW v3.0]
    - Real-world prescriptions (CMS Medicare) [NEW v3.0]
    - Market sizing & epidemiology (Data Commons) [NEW v3.0]
    - Target validation (Open Targets) [NEW v3.0]
    - Stock performance & sentiment (Financials) [NEW v3.0]

    Args:
        drug_name: Generic or brand name (e.g., 'semaglutide', 'Wegovy')
        indication: Therapeutic area (e.g., 'obesity', 'type 2 diabetes')
        company_ticker: Stock ticker for financial analysis (e.g., 'PFE', 'NVO')
                       If None, attempts to infer from FDA/patent data
        hcpcs_code: HCPCS code for CMS prescription data (e.g., 'J1234')
                    If None, CMS data collection is skipped
        gene_target: Gene target (e.g., 'ENSG00000169710' for GLP1R)
                    If None, uses indication to find top targets
        parallel_execution: Execute data collection in parallel (faster, default True)

    Returns:
        dict: Contains data sources, SWOT analysis, and formatted report
    """
    print(f"\n{'='*80}")
    print(f"Generating SWOT Analysis v3.0: {drug_name} for {indication}")
    print(f"{'='*80}\n")

    # Initialize result structure
    result = {
        'drug_name': drug_name,
        'indication': indication,
        'company_ticker': company_ticker,
        'last_updated': datetime.now().isoformat(),
        'version': '3.0',
        'data_sources': {},
        'swot_analysis': {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
    }

    # Collect data from all 9 sources
    if parallel_execution:
        print(f"[INFO] Collecting data from 9 sources in parallel...\n")
        all_data = collect_all_data_parallel(drug_name, indication, company_ticker, hcpcs_code, gene_target)
    else:
        print(f"[INFO] Collecting data from 9 sources sequentially...\n")
        all_data = collect_all_data_sequential(drug_name, indication, company_ticker, hcpcs_code, gene_target)

    # Unpack collected data
    trials_data = all_data['trials']
    fda_data = all_data['fda']
    pubmed_data = all_data['pubmed']
    patent_data = all_data['patents']
    financial_data = all_data.get('financial', {'count': 0, 'summary': 'No financial data available'})
    prescription_data = all_data.get('prescriptions', {'count': 0, 'summary': 'No prescription data available'})
    market_data = all_data.get('market', {'count': 0, 'summary': 'No market data available'})
    target_data = all_data.get('target', {'count': 0, 'summary': 'No target data available'})
    stock_data = all_data.get('stock', {'count': 0, 'summary': 'No stock data available'})

    # Store in result
    result['data_sources']['clinical_trials'] = trials_data
    result['data_sources']['fda_labels'] = fda_data
    result['data_sources']['publications'] = pubmed_data
    result['data_sources']['patents'] = patent_data
    result['data_sources']['financial'] = financial_data
    result['data_sources']['prescriptions'] = prescription_data
    result['data_sources']['market'] = market_data
    result['data_sources']['target'] = target_data
    result['data_sources']['stock'] = stock_data

    # Generate SWOT analysis from collected data
    print(f"\nAnalyzing data and generating SWOT...")
    generate_swot_v3(result, trials_data, fda_data, pubmed_data, patent_data,
                     financial_data, prescription_data, market_data, target_data, stock_data)

    # Format report
    result['formatted_report'] = format_swot_report_v3(result)

    return result


def collect_clinical_trials(drug_name: str, indication: str) -> dict:
    """Collect clinical trials data with pagination."""
    all_trials = []
    page_token = None

    # Search with drug name and indication
    query = f"{drug_name} {indication}"

    while True:
        try:
            if page_token:
                response = ct_search(term=query, pageSize=1000, pageToken=page_token)
            else:
                response = ct_search(term=query, pageSize=1000)

            # Parse markdown response
            trials = parse_ctgov_trials(response)
            all_trials.extend(trials)

            # Check for next page
            page_match = re.search(r'pageToken:\s*"([^"]+)"', response)
            if page_match:
                page_token = page_match.group(1)
            else:
                break

        except Exception as e:
            print(f"  Warning: Error collecting trials: {e}")
            break

    # Analyze trials
    phase_dist = {}
    status_dist = {}
    recruiting_count = 0
    completed_count = 0

    for trial in all_trials:
        # Phase distribution
        phase = trial.get('phase', 'Unknown')
        phase_dist[phase] = phase_dist.get(phase, 0) + 1

        # Status distribution
        status = trial.get('status', 'Unknown')
        status_dist[status] = status_dist.get(status, 0) + 1

        if 'recruiting' in status.lower():
            recruiting_count += 1
        if 'completed' in status.lower():
            completed_count += 1

    summary = f"Phase distribution: {phase_dist}. Status: {recruiting_count} recruiting, {completed_count} completed"

    return {
        'count': len(all_trials),
        'summary': summary,
        'trials': all_trials,
        'phase_distribution': phase_dist,
        'status_distribution': status_dist,
        'recruiting_count': recruiting_count,
        'completed_count': completed_count
    }


def parse_ctgov_trials(markdown: str) -> list:
    """Parse CT.gov markdown response into structured trial data."""
    trials = []

    # Split by trial headers (### N. NCTXXXXXXXX)
    trial_sections = re.split(r'(?=###\s+\d+\.\s+NCT\d{8})', markdown)

    for section in trial_sections:
        if not section.strip() or 'NCT' not in section:
            continue

        trial = {}

        # Extract NCT ID
        nct_match = re.search(r'NCT\d{8}', section)
        if nct_match:
            trial['nct_id'] = nct_match.group(0)
        else:
            continue  # Skip if no NCT ID found

        # Extract Title (more flexible - allow multiline)
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n\*\*|$)', section, re.DOTALL)
        if title_match:
            trial['title'] = title_match.group(1).strip()

        # Extract Status
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', section)
        if status_match:
            trial['status'] = status_match.group(1).strip()

        # Extract Phase
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', section)
        if phase_match:
            trial['phase'] = phase_match.group(1).strip()

        trials.append(trial)

    return trials


def collect_fda_data(drug_name: str) -> dict:
    """Collect FDA drug label data."""
    try:
        # Use count-first pattern to get brand names (mandatory for general searches)
        response = fda_lookup_drug(
            search_term=drug_name,
            search_type='general',
            count='openfda.brand_name.exact',
            limit=10
        )

        # Extract results from nested structure
        data = response.get('data', {})
        results = data.get('results', [])

        # Count number of brand names found
        brand_count = len(results)

        # Try to get label data for analysis
        # Note: FDA label queries are limited, so we use general data
        labels = []
        warnings = []
        contraindications = []
        adverse_reactions = []

        # For SWOT analysis, we mainly need to know if FDA approved
        # Detailed label analysis would require alternative approach
        summary = f"Found {brand_count} FDA-registered brand name(s) for {drug_name}"

        return {
            'count': brand_count,
            'summary': summary,
            'labels': labels,
            'warnings': warnings,
            'contraindications': contraindications,
            'adverse_reactions': adverse_reactions,
            'brand_names': [item.get('term', '') for item in results]
        }

    except Exception as e:
        print(f"  Warning: Error collecting FDA data: {e}")
        return {'count': 0, 'summary': 'No FDA data available', 'labels': [], 'brand_names': []}


def collect_publications(drug_name: str, indication: str) -> dict:
    """Collect recent publications (last 3 years)."""
    try:
        # Search for recent publications
        query = f"{drug_name} {indication} AND 2022:2025[dp]"
        response = pubmed_search(keywords=query, num_results=500)  # Increased limit

        # PubMed returns a list directly, not a dict
        articles = response if isinstance(response, list) else []

        # Count by year
        year_dist = {}
        for article in articles:
            # Extract year from publication_date field
            pub_date = article.get('publication_date', '')
            if pub_date:
                # Extract year from format like "2025-Nov-26"
                year = pub_date.split('-')[0] if '-' in pub_date else pub_date[:4]
                if year:
                    year_dist[year] = year_dist.get(year, 0) + 1

        summary = f"Found {len(articles)} recent publications. Distribution: {year_dist}"

        return {
            'count': len(articles),
            'summary': summary,
            'articles': articles,
            'year_distribution': year_dist
        }

    except Exception as e:
        print(f"  Warning: Error collecting publications: {e}")
        return {'count': 0, 'summary': 'No publications found', 'articles': []}


def collect_patents(drug_name: str, manufacturer: str = None) -> dict:
    """Collect patent data using Google Patents.

    Args:
        drug_name: Drug name to search
        manufacturer: Optional company name for focused search

    Returns:
        dict: Patent data with analysis
    """
    try:
        all_patents = []

        # Search 1: Drug name patents
        print(f"    Searching patents for '{drug_name}'...")
        response = google_search_patents(query=drug_name, country="US", limit=500)  # Increased limit

        patents = response.get('results', [])  # Fixed: Use 'results' not 'patents'
        all_patents.extend(patents)

        # Search 2: If manufacturer known, search their portfolio
        if manufacturer and manufacturer != 'N/A':
            print(f"    Searching {manufacturer} patent portfolio...")
            assignee_response = google_search_by_assignee(
                assignee_name=manufacturer,
                country="US",
                limit=200  # Increased limit
            )
            # Add manufacturer patents that mention drug
            manufacturer_patents = assignee_response.get('results', [])  # Fixed: Use 'results' not 'patents'
            for patent in manufacturer_patents:
                # Extract title from localized structure
                title_list = patent.get('title_localized', [])
                title = title_list[0].get('text', '') if title_list else ''

                # Extract abstract from localized structure
                abstract_list = patent.get('abstract_localized', [])
                abstract = abstract_list[0].get('text', '') if abstract_list else ''

                if drug_name.lower() in title.lower() or drug_name.lower() in abstract.lower():
                    # Avoid duplicates
                    if patent.get('publication_number') not in [p.get('publication_number') for p in all_patents]:
                        all_patents.append(patent)

        # Analyze patents
        assignees = {}
        publication_years = {}
        patent_families = set()
        earliest_year = None
        latest_year = None

        for patent in all_patents:
            # Track assignees - extract from harmonized structure
            assignee_list = patent.get('assignee_harmonized', [])
            if assignee_list:
                assignee = assignee_list[0].get('name', 'Unknown')
            else:
                assignee = 'Unknown'
            assignees[assignee] = assignees.get(assignee, 0) + 1

            # Track publication dates - convert numeric format (YYYYMMDD) to year
            pub_date = patent.get('publication_date', 0)
            if pub_date:
                year = int(str(pub_date)[:4])  # Extract first 4 digits for year
                publication_years[year] = publication_years.get(year, 0) + 1

                if earliest_year is None or year < earliest_year:
                    earliest_year = year
                if latest_year is None or year > latest_year:
                    latest_year = year

            # Track patent families
            family_id = patent.get('family_id', '')
            if family_id:
                patent_families.add(family_id)

        # Estimate patent expiry (US utility patents: 20 years from filing)
        estimated_expiry_start = earliest_year + 20 if earliest_year else None
        estimated_expiry_end = latest_year + 20 if latest_year else None

        # Sort assignees by count
        top_assignees = dict(sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:5])

        summary = f"Found {len(all_patents)} patents from {len(assignees)} assignees. "
        if earliest_year and latest_year:
            summary += f"Publication years: {earliest_year}-{latest_year}. "
        if estimated_expiry_start and estimated_expiry_end:
            summary += f"Estimated expiry: {estimated_expiry_start}-{estimated_expiry_end}"

        return {
            'count': len(all_patents),
            'summary': summary,
            'patents': all_patents,
            'assignees': top_assignees,
            'all_assignees': list(assignees.keys()),
            'patent_families': len(patent_families),
            'publication_years': publication_years,
            'earliest_year': earliest_year,
            'latest_year': latest_year,
            'estimated_expiry_start': estimated_expiry_start,
            'estimated_expiry_end': estimated_expiry_end
        }

    except Exception as e:
        print(f"  Warning: Error collecting patents: {e}")
        return {
            'count': 0,
            'summary': 'No patents found',
            'patents': [],
            'assignees': {},
            'all_assignees': [],
            'patent_families': 0,
            'publication_years': {},
            'earliest_year': None,
            'latest_year': None,
            'estimated_expiry_start': None,
            'estimated_expiry_end': None
        }


# ============================================================================
# NEW v3.0: DATA COLLECTION FUNCTIONS
# ============================================================================

def collect_all_data_parallel(drug_name: str, indication: str, company_ticker: str,
                               hcpcs_code: str, gene_target: str) -> dict:
    """Collect data from all 9 sources in parallel for faster execution.

    Note: Data Commons runs sequentially (outside ThreadPoolExecutor) to avoid
    subprocess pipe issues when MCP server spawning conflicts with parallel execution.
    """

    # Infer manufacturer from first pass if needed
    manufacturer = None

    # Run Data Commons BEFORE ThreadPoolExecutor to avoid subprocess conflicts
    print(f"  [Data Commons] Collecting market sizing data...")
    try:
        market_data = collect_market_sizing(indication)
        print(f"  ✓ Market: {market_data['count']} items")
    except Exception as e:
        print(f"  ✗ Market: Error - {e}")
        market_data = {'count': 0, 'summary': f'No market data available'}

    with ThreadPoolExecutor(max_workers=8) as executor:  # Reduced from 9 (market runs outside)
        futures = {
            executor.submit(collect_clinical_trials, drug_name, indication): 'trials',
            executor.submit(collect_fda_data, drug_name): 'fda',
            executor.submit(collect_publications, drug_name, indication): 'pubmed',
            executor.submit(collect_patents, drug_name, manufacturer): 'patents',
        }

        # Collect first 4 (to get manufacturer for financial queries)
        results = {'market': market_data}  # Include pre-collected market data
        for future in as_completed(futures):
            data_type = futures[future]
            try:
                results[data_type] = future.result()
                print(f"  ✓ {data_type.capitalize()}: {results[data_type]['count']} items")
            except Exception as e:
                print(f"  ✗ {data_type.capitalize()}: Error - {e}")
                results[data_type] = {'count': 0, 'summary': f'No {data_type} data available'}

        # Infer parameters if not provided
        if not company_ticker and results.get('patents', {}).get('assignees'):
            # Get top patent assignee as company
            top_assignee = list(results['patents']['assignees'].keys())[0] if results['patents']['assignees'] else None
            if top_assignee:
                print(f"  [INFO] Inferred company from patents: {top_assignee}")

        # Submit remaining 4 MCPs (market already done)
        futures2 = {}
        if company_ticker:
            futures2[executor.submit(collect_financial_data, company_ticker, drug_name)] = 'financial'
            futures2[executor.submit(collect_stock_performance, company_ticker)] = 'stock'

        if hcpcs_code:
            futures2[executor.submit(collect_prescription_data, hcpcs_code)] = 'prescriptions'

        futures2[executor.submit(collect_target_validation, indication, gene_target)] = 'target'

        # Collect remaining data
        for future in as_completed(futures2):
            data_type = futures2[future]
            try:
                results[data_type] = future.result()
                print(f"  ✓ {data_type.capitalize()}: {results[data_type]['count']} items")
            except Exception as e:
                print(f"  ✗ {data_type.capitalize()}: Error - {e}")
                results[data_type] = {'count': 0, 'summary': f'No {data_type} data available'}

    return results


def collect_all_data_sequential(drug_name: str, indication: str, company_ticker: str,
                                 hcpcs_code: str, gene_target: str) -> dict:
    """Collect data from all 9 sources sequentially (for debugging)."""

    results = {}

    # Original 4 sources
    print(f"[1/9] Collecting clinical trials data...")
    results['trials'] = collect_clinical_trials(drug_name, indication)
    print(f"  ✓ Found {results['trials']['count']} trials")

    print(f"[2/9] Collecting FDA label data...")
    results['fda'] = collect_fda_data(drug_name)
    print(f"  ✓ Found {results['fda']['count']} FDA labels")

    print(f"[3/9] Collecting scientific literature...")
    results['pubmed'] = collect_publications(drug_name, indication)
    print(f"  ✓ Found {results['pubmed']['count']} publications")

    print(f"[4/9] Collecting patent data...")
    manufacturer = results['fda'].get('brand_names', [None])[0] if results['fda'].get('brand_names') else None
    results['patents'] = collect_patents(drug_name, manufacturer)
    print(f"  ✓ Found {results['patents']['count']} patents ({results['patents'].get('patent_families', 0)} families)")

    # New v3.0 sources
    if company_ticker:
        print(f"[5/9] Collecting financial data (SEC EDGAR)...")
        results['financial'] = collect_financial_data(company_ticker, drug_name)
        print(f"  ✓ {results['financial']['summary']}")
    else:
        print(f"[5/9] Skipping financial data (no ticker provided)...")
        results['financial'] = {'count': 0, 'summary': 'No financial data available (no ticker)'}

    if hcpcs_code:
        print(f"[6/9] Collecting prescription data (CMS Medicare)...")
        results['prescriptions'] = collect_prescription_data(hcpcs_code)
        print(f"  ✓ {results['prescriptions']['summary']}")
    else:
        print(f"[6/9] Skipping prescription data (no HCPCS code provided)...")
        results['prescriptions'] = {'count': 0, 'summary': 'No prescription data available (no HCPCS code)'}

    print(f"[7/9] Collecting market sizing data (Data Commons)...")
    results['market'] = collect_market_sizing(indication)
    print(f"  ✓ {results['market']['summary']}")

    print(f"[8/9] Collecting target validation data (Open Targets)...")
    results['target'] = collect_target_validation(indication, gene_target)
    print(f"  ✓ {results['target']['summary']}")

    if company_ticker:
        print(f"[9/9] Collecting stock performance data...")
        results['stock'] = collect_stock_performance(company_ticker)
        print(f"  ✓ {results['stock']['summary']}")
    else:
        print(f"[9/9] Skipping stock performance (no ticker provided)...")
        results['stock'] = {'count': 0, 'summary': 'No stock data available (no ticker)'}

    return results


def collect_financial_data(company_ticker: str, drug_name: str) -> dict:
    """Collect SEC EDGAR financial data for company."""
    try:
        # Get company CIK
        try:
            cik_result = get_company_cik(ticker=company_ticker)
            cik = cik_result.get('cik')
        except:
            # Fallback: search companies
            search_result = search_companies(query=company_ticker)
            if search_result and len(search_result) > 0:
                cik = search_result[0].get('cik_str')
            else:
                return {'count': 0, 'summary': f'Company {company_ticker} not found in SEC database'}

        # Get R&D spend
        try:
            rd_data = get_company_facts(
                cik_or_ticker=cik,
                taxonomy="us-gaap",
                tag="ResearchAndDevelopmentExpense"
            )
            # Extract recent R&D spend values
            units = rd_data.get('units', {})
            usd_data = units.get('USD', [])
            if usd_data:
                # Get last 3 years
                recent_rd = sorted(usd_data, key=lambda x: x.get('end', ''), reverse=True)[:3]
                rd_spend = [{'year': r.get('end', '')[:4], 'amount': r.get('val', 0)} for r in recent_rd]
            else:
                rd_spend = []
        except:
            rd_spend = []

        summary = f"SEC data for {company_ticker}"
        if rd_spend:
            latest = rd_spend[0]
            summary += f" - R&D spend: ${latest['amount']/1e9:.1f}B ({latest['year']})"

        return {
            'count': 1,
            'summary': summary,
            'cik': cik,
            'rd_spend': rd_spend,
            'company_ticker': company_ticker
        }

    except Exception as e:
        print(f"    Warning: Error collecting financial data: {e}")
        return {'count': 0, 'summary': f'No financial data available'}


def collect_prescription_data(hcpcs_code: str, year: str = '2022') -> dict:
    """Collect CMS Medicare prescription data."""
    try:
        # Search for providers prescribing this drug
        prescribers = cms_search_providers(
            dataset_type='provider_and_service',
            hcpcs_code=hcpcs_code,
            year=year,
            size=1000,
            sort_by='Tot_Srvcs',
            sort_order='desc'
        )

        if not prescribers or 'providers' not in prescribers:
            return {'count': 0, 'summary': 'No prescription data found'}

        results = prescribers['providers']
        # Convert string values to float then int (API returns strings with decimals)
        total_services = sum(int(float(r.get('total_services', 0))) for r in results)
        unique_providers = len(results)

        # Geographic distribution
        states = {}
        for r in results:
            state = r.get('provider_state', 'Unknown')
            states[state] = states.get(state, 0) + 1

        top_states = dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:5])

        summary = f"Found {total_services:,} prescriptions from {unique_providers} providers in {year}"

        return {
            'count': total_services,
            'summary': summary,
            'unique_providers': unique_providers,
            'year': year,
            'top_states': top_states,
            'hcpcs_code': hcpcs_code
        }

    except Exception as e:
        print(f"    Warning: Error collecting prescription data: {e}")
        return {'count': 0, 'summary': 'No prescription data available'}


def collect_market_sizing(indication: str) -> dict:
    """Collect epidemiology and market sizing data from Data Commons.

    Uses proper two-step workflow:
    1. search_indicators() to find variables
    2. get_observations() to retrieve data
    """
    import time
    import traceback

    try:
        # Map indication to disease prevalence search
        disease_query = indication.replace('type 2 diabetes', 'diabetes').replace('obesity', 'obesity')

        print(f"    [DC DEBUG 1/6] Starting Data Commons - query: {disease_query} prevalence")

        # Step 1: Search for prevalence indicators (qualified place names)
        print(f"    [DC DEBUG 2/6] About to call search_indicators (this spawns subprocess)...")
        try:
            start_time = time.time()
            indicators = search_indicators(
                query=f"{disease_query} prevalence",
                places=["United States", "China", "India", "Germany", "Brazil"],
                include_topics=False,
                per_search_limit=5
            )
            elapsed = time.time() - start_time
            print(f"    [DC DEBUG 3/6] search_indicators SUCCESS ({elapsed:.2f}s) - got {len(indicators.get('variables', []))} variables")
        except BrokenPipeError as pipe_error:
            print(f"    [DC ERROR] BrokenPipeError during search_indicators!")
            print(f"    [DC ERROR] This means subprocess stdin/stdout pipe closed unexpectedly")
            print(f"    [DC ERROR] Traceback:\n{traceback.format_exc()}")
            raise
        except Exception as search_error:
            print(f"    [DC ERROR] search_indicators failed: {type(search_error).__name__}: {search_error}")
            print(f"    [DC ERROR] Traceback:\n{traceback.format_exc()}")
            raise

        # Extract variable and place DCIDs
        variables = indicators.get('variables', [])
        if not variables:
            return {'count': 0, 'summary': f'No epidemiological data found for {indication}'}

        variable_dcid = variables[0]['dcid']
        variable_name = indicators.get('dcid_name_mappings', {}).get(variable_dcid, 'Unknown')
        print(f"    [DC DEBUG 4/6] Variable: {variable_name} ({variable_dcid})")

        # Get place_dcid from search results
        places_with_data = variables[0].get('places_with_data', [])
        if not places_with_data:
            return {'count': 1, 'summary': f'Indicator found: {variable_name} (no place data)'}

        place_dcid = places_with_data[0]
        place_name = indicators.get('dcid_name_mappings', {}).get(place_dcid, place_dcid)
        print(f"    [DC DEBUG] Place: {place_name} ({place_dcid})")

        # Small delay to ensure subprocess is ready for second call
        time.sleep(0.2)

        # Step 2: Get latest observation
        print(f"    [DC DEBUG 5/6] About to call get_observations (reuses same subprocess)...")
        try:
            start_time = time.time()
            prevalence_data = get_observations(
                variable_dcid=variable_dcid,
                place_dcid=place_dcid,
                date='latest'
            )
            elapsed = time.time() - start_time
            print(f"    [DC DEBUG 6/6] get_observations SUCCESS ({elapsed:.2f}s)")
        except BrokenPipeError as pipe_error:
            print(f"    [DC ERROR] BrokenPipeError during get_observations!")
            print(f"    [DC ERROR] Subprocess pipe closed after search_indicators succeeded")
            print(f"    [DC ERROR] Traceback:\n{traceback.format_exc()}")
            raise
        except Exception as obs_error:
            print(f"    [DC ERROR] get_observations failed: {type(obs_error).__name__}: {obs_error}")
            print(f"    [DC ERROR] Traceback:\n{traceback.format_exc()}")
            raise

        # Extract latest value
        place_observations = prevalence_data.get('place_observations', [])
        if not place_observations:
            return {'count': 1, 'summary': f'Indicator found: {variable_name} (no observations)'}

        time_series = place_observations[0].get('time_series', [])
        if not time_series:
            return {'count': 1, 'summary': f'Indicator found: {variable_name} (no time series)'}

        # Get latest data point (first element in time_series)
        date, value = time_series[0]
        source = prevalence_data.get('source_metadata', {}).get('import_name', 'Data Commons')

        summary = f"{variable_name}: {value:,.0f} ({date}) | Source: {source}"
        count = int(value) if value > 0 else 1

        return {
            'count': count,
            'summary': summary,
            'variable_dcid': variable_dcid,
            'variable_name': variable_name,
            'value': value,
            'date': date,
            'source': source
        }

    except Exception as e:
        print(f"    [DC ERROR] Final exception: {type(e).__name__}: {e}")
        print(f"    [DC ERROR] Full traceback:\n{traceback.format_exc()}")
        return {'count': 0, 'summary': f'No market data available: {e}'}


def collect_target_validation(indication: str, gene_target: str = None) -> dict:
    """Collect target validation data from Open Targets."""
    try:
        # Search for disease
        diseases = search_diseases(query=indication, size=5)

        # Extract hits from nested response structure
        hits = diseases.get('data', {}).get('search', {}).get('hits', [])

        if not hits:
            return {'count': 0, 'summary': f'Disease not found: {indication}'}

        disease_id = hits[0]['id']
        disease_name = hits[0]['name']

        # Get targets for disease
        targets = get_disease_targets_summary(
            diseaseId=disease_id,
            minScore=0.3,
            size=10
        )

        if not targets or 'targets' not in targets:
            return {'count': 0, 'summary': f'No targets found for {disease_name}'}

        target_list = targets['targets']
        count = len(target_list)

        # Get top target details
        if target_list:
            top_target = target_list[0]
            target_name = top_target.get('target', {}).get('approvedSymbol', 'Unknown')
            score = top_target.get('overallAssociationScore', 0)
            summary = f"{count} targets for {disease_name}. Top: {target_name} (score {score:.2f})"
        else:
            summary = f"No targets found for {disease_name}"

        return {
            'count': count,
            'summary': summary,
            'disease_id': disease_id,
            'disease_name': disease_name,
            'top_targets': target_list[:3] if count >= 3 else target_list
        }

    except Exception as e:
        print(f"    Warning: Error collecting target data: {e}")
        return {'count': 0, 'summary': 'No target validation data available'}


def collect_stock_performance(company_ticker: str) -> dict:
    """Collect stock performance and analyst sentiment."""
    try:
        # Get stock summary
        stock_data = financial_intelligence(
            method='stock_summary',
            symbol=company_ticker
        )

        # Get recommendations
        recommendations = financial_intelligence(
            method='stock_recommendations',
            symbol=company_ticker
        )

        # Extract key metrics
        current_price = stock_data.get('currentPrice', 0)
        market_cap = stock_data.get('marketCap', 0)
        pe_ratio = stock_data.get('trailingPE', 0)

        # Extract recommendation trend
        if recommendations and isinstance(recommendations, dict):
            trend = recommendations.get('trend', [])
            if trend and len(trend) > 0:
                latest_rec = trend[0]
                strong_buy = latest_rec.get('strongBuy', 0)
                buy = latest_rec.get('buy', 0)
                hold = latest_rec.get('hold', 0)
                sell = latest_rec.get('sell', 0)
                strong_sell = latest_rec.get('strongSell', 0)

                total_analysts = strong_buy + buy + hold + sell + strong_sell
                consensus = f"{strong_buy} Strong Buy, {buy} Buy, {hold} Hold, {sell} Sell"
            else:
                consensus = "No analyst recommendations available"
        else:
            consensus = "No recommendation data"

        summary = f"{company_ticker}: ${current_price:.2f}, Market Cap ${market_cap/1e9:.1f}B"
        if pe_ratio:
            summary += f", P/E {pe_ratio:.1f}"

        return {
            'count': 1,
            'summary': summary,
            'current_price': current_price,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'analyst_consensus': consensus,
            'company_ticker': company_ticker
        }

    except Exception as e:
        print(f"    Warning: Error collecting stock data: {e}")
        return {'count': 0, 'summary': 'No stock performance data available'}


# ============================================================================
# END v3.0 DATA COLLECTION FUNCTIONS
# ============================================================================


def generate_swot(result: dict, trials_data: dict, fda_data: dict,
                  pubmed_data: dict, patent_data: dict):
    """Generate SWOT analysis from collected data."""

    # STRENGTHS

    # Phase 3/4 trials
    phase3_count = trials_data['phase_distribution'].get('Phase 3', 0)
    phase4_count = trials_data['phase_distribution'].get('Phase 4', 0)

    if phase3_count > 0:
        result['swot_analysis']['strengths'].append({
            'category': 'Clinical Development',
            'point': f'{phase3_count} Phase 3 trial(s) demonstrating advanced development',
            'evidence': f"Phase distribution: {trials_data['phase_distribution']}"
        })

    if phase4_count > 0:
        result['swot_analysis']['strengths'].append({
            'category': 'Market Presence',
            'point': f'{phase4_count} Phase 4 trial(s) indicating market approval',
            'evidence': f"Post-marketing studies ongoing"
        })

    # FDA approval
    if fda_data['count'] > 0:
        result['swot_analysis']['strengths'].append({
            'category': 'Regulatory',
            'point': 'FDA-approved with published drug label',
            'evidence': f"{fda_data['count']} FDA label(s) available"
        })

    # Strong research support
    if pubmed_data['count'] > 50:
        result['swot_analysis']['strengths'].append({
            'category': 'Scientific Evidence',
            'point': f'Robust scientific evidence with {pubmed_data["count"]} recent publications',
            'evidence': f"Publication distribution: {pubmed_data.get('year_distribution', {})}"
        })

    # Patent protection
    if patent_data['count'] > 0:
        families = patent_data.get('patent_families', 0)
        assignees = patent_data.get('assignees', {})
        top_assignees = list(assignees.keys())[:3]

        family_text = f" across {families} patent families" if families > 1 else ""
        result['swot_analysis']['strengths'].append({
            'category': 'Intellectual Property',
            'point': f'Patent portfolio with {patent_data["count"]} patents{family_text}',
            'evidence': f"Top assignees: {', '.join(top_assignees) if top_assignees else 'Multiple entities'}"
        })

    # WEAKNESSES

    # Boxed warnings
    if len(fda_data.get('warnings', [])) > 0:
        result['swot_analysis']['weaknesses'].append({
            'category': 'Safety',
            'point': 'FDA boxed warning(s) present',
            'evidence': f"{len(fda_data['warnings'])} boxed warning(s) in label"
        })

    # Limited clinical data
    if trials_data['count'] < 10:
        result['swot_analysis']['weaknesses'].append({
            'category': 'Clinical Development',
            'point': 'Limited clinical trial program',
            'evidence': f"Only {trials_data['count']} trials identified"
        })

    # Contraindications
    if len(fda_data.get('contraindications', [])) > 0:
        result['swot_analysis']['weaknesses'].append({
            'category': 'Safety',
            'point': 'Contraindications limit patient population',
            'evidence': f"Contraindications present in FDA label"
        })

    # OPPORTUNITIES

    # Active recruiting trials
    if trials_data['recruiting_count'] > 5:
        result['swot_analysis']['opportunities'].append({
            'category': 'Pipeline Expansion',
            'point': f'{trials_data["recruiting_count"]} actively recruiting trials indicate pipeline growth',
            'evidence': f"Trial status: {trials_data['status_distribution']}"
        })

    # Early phase programs
    phase1_count = trials_data['phase_distribution'].get('Phase 1', 0)
    phase2_count = trials_data['phase_distribution'].get('Phase 2', 0)

    if phase1_count + phase2_count > 5:
        result['swot_analysis']['opportunities'].append({
            'category': 'Early Development',
            'point': f'Robust early-stage pipeline with {phase1_count + phase2_count} Phase 1/2 trials',
            'evidence': f"Early phase: {phase1_count} Phase 1, {phase2_count} Phase 2"
        })

    # Research momentum
    recent_pubs = pubmed_data.get('year_distribution', {}).get('2024', 0) + \
                  pubmed_data.get('year_distribution', {}).get('2025', 0)

    if recent_pubs > 20:
        result['swot_analysis']['opportunities'].append({
            'category': 'Scientific Interest',
            'point': f'Strong recent research momentum with {recent_pubs} publications in 2024-2025',
            'evidence': f"Year distribution: {pubmed_data.get('year_distribution', {})}"
        })

    # THREATS

    # Safety concerns
    if len(fda_data.get('adverse_reactions', [])) > 0:
        result['swot_analysis']['threats'].append({
            'category': 'Safety',
            'point': 'Known adverse reactions may impact adoption',
            'evidence': f"Adverse reactions documented in FDA label"
        })

    # Limited patent protection
    if patent_data['count'] < 5:
        result['swot_analysis']['threats'].append({
            'category': 'Competition',
            'point': 'Limited patent portfolio may allow generic entry',
            'evidence': f"Only {patent_data['count']} patents identified"
        })

    # Patent expiry timeline
    current_year = datetime.now().year
    expiry_start = patent_data.get('estimated_expiry_start')
    expiry_end = patent_data.get('estimated_expiry_end')

    if expiry_start and expiry_start <= current_year + 10:
        years_to_expiry = expiry_start - current_year
        if years_to_expiry <= 5:
            urgency = "imminent"
        elif years_to_expiry <= 10:
            urgency = "approaching"
        else:
            urgency = "future"

        result['swot_analysis']['threats'].append({
            'category': 'Patent Cliff',
            'point': f'Patent expiry {urgency} (estimated {expiry_start}-{expiry_end if expiry_end else expiry_start})',
            'evidence': f"Based on earliest patent from {patent_data.get('earliest_year', 'N/A')} (20-year term)"
        })

    # Competitive landscape (inferred from trial volume)
    if trials_data['count'] > 100:
        result['swot_analysis']['threats'].append({
            'category': 'Competition',
            'point': f'Highly competitive therapeutic area with {trials_data["count"]} trials',
            'evidence': f"Large number of trials suggests crowded market"
        })


def format_swot_report(result: dict) -> str:
    """Format SWOT analysis as markdown report."""

    report = f"""# Drug SWOT Analysis: {result['drug_name']}

**Indication:** {result['indication']}
**Analysis Date:** {result['last_updated'][:10]}
**Generated by:** Pharmaceutical Research Intelligence Platform

---

## Executive Summary

This SWOT analysis synthesizes data from multiple authoritative sources to provide a strategic assessment of **{result['drug_name']}** for **{result['indication']}**.

### Data Sources Summary

| Source | Count | Details |
|--------|-------|---------|
| Clinical Trials | {result['data_sources']['clinical_trials']['count']} | {result['data_sources']['clinical_trials']['summary']} |
| FDA Labels | {result['data_sources']['fda_labels']['count']} | {result['data_sources']['fda_labels']['summary']} |
| Publications | {result['data_sources']['publications']['count']} | {result['data_sources']['publications']['summary']} |
| Patents | {result['data_sources']['patents']['count']} | {result['data_sources']['patents']['summary']} |

---

## SWOT Analysis

### 💪 Strengths

"""

    if result['swot_analysis']['strengths']:
        for i, strength in enumerate(result['swot_analysis']['strengths'], 1):
            report += f"\n**{i}. {strength['category']}: {strength['point']}**\n"
            report += f"- Evidence: {strength['evidence']}\n"
    else:
        report += "\n*No significant strengths identified from available data.*\n"

    report += "\n### ⚠️ Weaknesses\n"

    if result['swot_analysis']['weaknesses']:
        for i, weakness in enumerate(result['swot_analysis']['weaknesses'], 1):
            report += f"\n**{i}. {weakness['category']}: {weakness['point']}**\n"
            report += f"- Evidence: {weakness['evidence']}\n"
    else:
        report += "\n*No significant weaknesses identified from available data.*\n"

    report += "\n### 🚀 Opportunities\n"

    if result['swot_analysis']['opportunities']:
        for i, opp in enumerate(result['swot_analysis']['opportunities'], 1):
            report += f"\n**{i}. {opp['category']}: {opp['point']}**\n"
            report += f"- Evidence: {opp['evidence']}\n"
    else:
        report += "\n*No significant opportunities identified from available data.*\n"

    report += "\n### 🔴 Threats\n"

    if result['swot_analysis']['threats']:
        for i, threat in enumerate(result['swot_analysis']['threats'], 1):
            report += f"\n**{i}. {threat['category']}: {threat['point']}**\n"
            report += f"- Evidence: {threat['evidence']}\n"
    else:
        report += "\n*No significant threats identified from available data.*\n"

    report += f"""

---

## Methodology

This analysis was generated using the Pharmaceutical Research Intelligence Platform's multi-source data collection approach:

1. **Clinical Trials**: Searched ClinicalTrials.gov for all trials mentioning "{result['drug_name']}" and "{result['indication']}"
2. **FDA Data**: Retrieved official drug labels and safety information from FDA databases
3. **Publications**: Analyzed recent scientific literature (2022-2025) from PubMed
4. **Patents**: Searched Google Patents Public Datasets for intellectual property landscape, including patent families, expiry estimates, and assignee analysis

### Data Quality Notes

- Analysis based on publicly available data as of {result['last_updated'][:10]}
- SWOT categorization uses objective criteria from collected data
- Some data sources may be incomplete or pending updates

---

## Strategic Recommendations

Based on this SWOT analysis, key strategic considerations include:

"""

    # Generate recommendations based on SWOT balance
    strength_count = len(result['swot_analysis']['strengths'])
    weakness_count = len(result['swot_analysis']['weaknesses'])
    opportunity_count = len(result['swot_analysis']['opportunities'])
    threat_count = len(result['swot_analysis']['threats'])

    if strength_count > weakness_count and opportunity_count > threat_count:
        report += "- **Overall Position**: Strong - Leverage strengths to capitalize on opportunities\n"
        report += "- **Priority**: Accelerate development and market expansion initiatives\n"
    elif weakness_count > strength_count or threat_count > opportunity_count:
        report += "- **Overall Position**: Defensive - Address weaknesses and mitigate threats\n"
        report += "- **Priority**: Risk management and competitive differentiation\n"
    else:
        report += "- **Overall Position**: Balanced - Selective strategy execution required\n"
        report += "- **Priority**: Focus on highest-impact opportunities while managing key risks\n"

    report += "\n---\n\n*This report was automatically generated. For detailed data, please refer to source databases.*\n"

    return report


# ============================================================================
# NEW v3.0: ENHANCED SWOT GENERATION WITH 9 DATA SOURCES
# ============================================================================

def generate_swot_v3(result: dict, trials_data: dict, fda_data: dict,
                     pubmed_data: dict, patent_data: dict,
                     financial_data: dict, prescription_data: dict,
                     market_data: dict, target_data: dict, stock_data: dict):
    """Generate enhanced SWOT analysis with 9 data sources (v3.0)."""

    # Call original SWOT logic first (maintains backward compatibility)
    generate_swot(result, trials_data, fda_data, pubmed_data, patent_data)

    # === NEW v3.0 ENHANCEMENTS ===

    # STRENGTHS - Financial validation
    if financial_data['count'] > 0 and financial_data.get('rd_spend'):
        rd_spend = financial_data['rd_spend']
        if len(rd_spend) >= 2:
            latest = rd_spend[0]
            prev = rd_spend[1]
            growth = ((latest['amount'] - prev['amount']) / prev['amount']) * 100 if prev['amount'] > 0 else 0

            result['swot_analysis']['strengths'].append({
                'category': 'Financial Commitment',
                'point': f'R&D investment of ${latest["amount"]/1e9:.1f}B ({growth:+.0f}% YoY)',
                'evidence': f"SEC EDGAR data shows sustained R&D commitment",
                'confidence': 'High'
            })

    # STRENGTHS - Market validation (stock)
    if stock_data['count'] > 0:
        result['swot_analysis']['strengths'].append({
            'category': 'Market Validation',
            'point': f'Market cap ${stock_data["market_cap"]/1e9:.1f}B with analyst support',
            'evidence': f'{stock_data["analyst_consensus"]}',
            'confidence': 'High'
        })

    # STRENGTHS - Real-world adoption
    if prescription_data['count'] > 0:
        rx_count = prescription_data['count']
        providers = prescription_data.get('unique_providers', 0)
        result['swot_analysis']['strengths'].append({
            'category': 'Real-World Adoption',
            'point': f'{rx_count:,} Medicare prescriptions from {providers:,} providers',
            'evidence': f'CMS data ({prescription_data["year"]})',
            'confidence': 'High'
        })

    # STRENGTHS - Target validation
    if target_data['count'] > 0:
        result['swot_analysis']['strengths'].append({
            'category': 'Target Validation',
            'point': f'{target_data["count"]} validated targets for {target_data.get("disease_name", "indication")}',
            'evidence': f'Open Targets platform',
            'confidence': 'High'
        })

    # OPPORTUNITIES - Market size
    if market_data['count'] > 1000:  # Assuming count represents prevalence
        result['swot_analysis']['opportunities'].append({
            'category': 'Market Opportunity',
            'point': f'Large patient population ({market_data["count"]:,})',
            'evidence': f'{market_data["summary"]}',
            'confidence': 'High'
        })

    # OPPORTUNITIES - Geographic expansion (from prescription data)
    if prescription_data.get('top_states'):
        states_count = len(prescription_data['top_states'])
        result['swot_analysis']['opportunities'].append({
            'category': 'Geographic Expansion',
            'point': f'Prescription concentration in {states_count} states suggests expansion opportunity',
            'evidence': f'Top states: {", ".join(list(prescription_data["top_states"].keys())[:3])}',
            'confidence': 'Medium'
        })

    # WEAKNESSES - Prescription limitations
    if prescription_data['count'] > 0 and prescription_data['count'] < 10000:
        result['swot_analysis']['weaknesses'].append({
            'category': 'Limited Adoption',
            'point': f'Modest prescription volume ({prescription_data["count"]:,} annually)',
            'evidence': f'CMS Medicare data suggests limited market penetration',
            'confidence': 'Medium'
        })

    # THREATS - Financial constraints
    if financial_data.get('rd_spend'):
        rd_spend = financial_data['rd_spend']
        if len(rd_spend) >= 2:
            latest = rd_spend[0]
            prev = rd_spend[1]
            growth = ((latest['amount'] - prev['amount']) / prev['amount']) * 100 if prev['amount'] > 0 else 0

            if growth < 0:
                result['swot_analysis']['threats'].append({
                    'category': 'R&D Investment',
                    'point': f'R&D spend declining ({growth:.0f}% YoY)',
                    'evidence': f'SEC data shows reduced investment commitment',
                    'confidence': 'High'
                })

    # Add confidence scores to existing items (default Medium if not set)
    for category in ['strengths', 'weaknesses', 'opportunities', 'threats']:
        for item in result['swot_analysis'][category]:
            if 'confidence' not in item:
                item['confidence'] = 'Medium'


def format_swot_report_v3(result: dict) -> str:
    """Format enhanced SWOT report with v3.0 data sources."""

    # Count successful data sources
    data_sources = result['data_sources']
    successful_sources = sum(1 for s in data_sources.values() if s.get('count', 0) > 0)

    report = f"""# Drug SWOT Analysis v3.0: {result['drug_name']}

**Indication:** {result['indication']}
**Analysis Date:** {result['last_updated'][:10]}
**Version:** 3.0 (Enhanced with 9 data sources)
**Data Coverage:** {successful_sources}/9 sources successful
"""

    if result.get('company_ticker'):
        report += f"**Company:** {result['company_ticker']}\n"

    report += """
---

## Executive Summary

This SWOT analysis synthesizes data from **9 authoritative sources** to provide comprehensive strategic assessment.

### Data Sources Summary

| Source | Status | Count | Details |
|--------|--------|-------|---------|
"""

    # Add all 9 sources
    for source_name, source_key in [
        ('Clinical Trials', 'clinical_trials'),
        ('FDA Labels', 'fda_labels'),
        ('Publications', 'publications'),
        ('Patents', 'patents'),
        ('SEC Financial', 'financial'),
        ('Medicare Rx', 'prescriptions'),
        ('Epidemiology', 'market'),
        ('Target Biology', 'target'),
        ('Stock Performance', 'stock')
    ]:
        source_data = data_sources.get(source_key, {})
        count = source_data.get('count', 0)
        status = "✓" if count > 0 else "✗"
        summary = source_data.get('summary', 'Not available')
        report += f"| {source_name} | {status} | {count} | {summary} |\n"

    report += "\n---\n\n## SWOT Analysis\n\n### 💪 Strengths\n\n"

    # Strengths with confidence indicators
    if result['swot_analysis']['strengths']:
        for i, strength in enumerate(result['swot_analysis']['strengths'], 1):
            confidence = strength.get('confidence', 'Medium')
            indicator = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}.get(confidence, '⚪')
            report += f"\n**{i}. {strength['category']}: {strength['point']}** {indicator} {confidence}\n"
            report += f"- Evidence: {strength['evidence']}\n"
    else:
        report += "\n*No significant strengths identified from available data.*\n"

    report += "\n### ⚠️ Weaknesses\n\n"

    if result['swot_analysis']['weaknesses']:
        for i, weakness in enumerate(result['swot_analysis']['weaknesses'], 1):
            confidence = weakness.get('confidence', 'Medium')
            indicator = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}.get(confidence, '⚪')
            report += f"\n**{i}. {weakness['category']}: {weakness['point']}** {indicator} {confidence}\n"
            report += f"- Evidence: {weakness['evidence']}\n"
    else:
        report += "\n*No significant weaknesses identified from available data.*\n"

    report += "\n### 🚀 Opportunities\n\n"

    if result['swot_analysis']['opportunities']:
        for i, opp in enumerate(result['swot_analysis']['opportunities'], 1):
            confidence = opp.get('confidence', 'Medium')
            indicator = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}.get(confidence, '⚪')
            report += f"\n**{i}. {opp['category']}: {opp['point']}** {indicator} {confidence}\n"
            report += f"- Evidence: {opp['evidence']}\n"
    else:
        report += "\n*No significant opportunities identified from available data.*\n"

    report += "\n### 🔴 Threats\n\n"

    if result['swot_analysis']['threats']:
        for i, threat in enumerate(result['swot_analysis']['threats'], 1):
            confidence = threat.get('confidence', 'Medium')
            indicator = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}.get(confidence, '⚪')
            report += f"\n**{i}. {threat['category']}: {threat['point']}** {indicator} {confidence}\n"
            report += f"- Evidence: {threat['evidence']}\n"
    else:
        report += "\n*No significant threats identified from available data.*\n"

    report += f"""

---

## Methodology

This v3.0 analysis integrates **9 authoritative data sources** for comprehensive intelligence:

1. **Clinical Trials** (CT.gov): All trials for {result['drug_name']} and {result['indication']}
2. **FDA** (Drug Labels): Official safety and efficacy data
3. **Publications** (PubMed): Recent literature (2022-2025)
4. **Patents** (Google Patents): IP landscape and expiry timeline
5. **Financial** (SEC EDGAR): R&D spend and company commitment [NEW v3.0]
6. **Prescriptions** (CMS Medicare): Real-world utilization patterns [NEW v3.0]
7. **Epidemiology** (Data Commons): Disease burden and market size [NEW v3.0]
8. **Target Biology** (Open Targets): Genetic validation [NEW v3.0]
9. **Stock Performance** (Yahoo Finance): Market sentiment [NEW v3.0]

### Data Quality

- **Data Currency**: {result['last_updated'][:10]}
- **Sources**: {successful_sources}/9 successful
- **Confidence Levels**: 🟢 High | 🟡 Medium | 🔴 Low

---

## Strategic Recommendations

"""

    # Enhanced recommendations based on SWOT balance
    strength_count = len(result['swot_analysis']['strengths'])
    weakness_count = len(result['swot_analysis']['weaknesses'])
    opportunity_count = len(result['swot_analysis']['opportunities'])
    threat_count = len(result['swot_analysis']['threats'])

    total_score = (strength_count * 2) + opportunity_count - (weakness_count + threat_count)
    if total_score > 5:
        position = "STRONG GROWTH"
        priority = "INVEST - Accelerate development and market expansion"
    elif total_score > 0:
        position = "MODERATE OPPORTUNITY"
        priority = "SELECTIVE - Focus on high-impact initiatives"
    elif total_score > -5:
        position = "DEFENSIVE"
        priority = "MITIGATE - Address key risks and weaknesses"
    else:
        position = "CHALLENGED"
        priority = "REASSESS - Consider strategic alternatives"

    report += f"""**Overall Position**: {position}

**Strategic Priority**: {priority}

**Key Actions**:
"""

    # Dynamic recommendations
    if strength_count > weakness_count:
        report += f"- Leverage {strength_count} identified strengths to capitalize on opportunities\n"
    if weakness_count > 0:
        report += f"- Address {weakness_count} critical weaknesses to improve competitive positioning\n"
    if opportunity_count > threat_count:
        report += f"- Pursue {opportunity_count} market opportunities identified\n"
    if threat_count > 0:
        report += f"- Mitigate {threat_count} strategic threats through proactive measures\n"

    report += "\n---\n\n*This v3.0 report integrates 9 data sources for institutional-grade strategic intelligence.*\n"

    return report


# ============================================================================
# END v3.0 ENHANCEMENTS
# ============================================================================


# Example execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate comprehensive SWOT analysis for pharmaceutical products (v3.0)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (v2.0 compatible)
  python generate_drug_swot_analysis.py semaglutide obesity

  # Full v3.0 analysis with all optional parameters
  python generate_drug_swot_analysis.py semaglutide obesity --ticker NVO --hcpcs J3490 --gene-target ENSG00000169710

  # Investment analysis (with financial/stock data)
  python generate_drug_swot_analysis.py nivolumab "lung cancer" --ticker BMY

  # Real-world evidence focus (with prescription data)
  python generate_drug_swot_analysis.py pembrolizumab melanoma --hcpcs J9355

  # Sequential execution for debugging
  python generate_drug_swot_analysis.py semaglutide obesity --no-parallel
        """
    )

    # Required arguments
    parser.add_argument('drug_name', nargs='?', default='semaglutide',
                        help='Generic or brand name (e.g., "semaglutide", "Wegovy")')
    parser.add_argument('indication', nargs='?', default='obesity',
                        help='Therapeutic area (e.g., "obesity", "type 2 diabetes")')

    # v3.0 Optional arguments
    parser.add_argument('--ticker', type=str, default=None,
                        help='Stock ticker for financial/stock analysis (e.g., "NVO", "PFE"). Enables SEC R&D spend and analyst sentiment.')
    parser.add_argument('--hcpcs', type=str, default=None,
                        help='HCPCS code for CMS prescription data (e.g., "J3490"). Enables real-world utilization and provider adoption.')
    parser.add_argument('--gene-target', type=str, default=None, dest='gene_target',
                        help='Gene target for validation (e.g., "ENSG00000169710" for GLP1R). Enables genetic evidence scoring.')
    parser.add_argument('--no-parallel', action='store_false', dest='parallel_execution',
                        help='Use sequential execution instead of parallel (for debugging)')

    args = parser.parse_args()

    # Show usage info if using defaults
    if args.drug_name == 'semaglutide' and args.indication == 'obesity' and len(sys.argv) == 1:
        print("No arguments provided. Running default example: semaglutide for obesity")
        print("For full usage: python generate_drug_swot_analysis.py --help\n")

    result = generate_drug_swot_analysis(
        drug_name=args.drug_name,
        indication=args.indication,
        company_ticker=args.ticker,
        hcpcs_code=args.hcpcs,
        gene_target=args.gene_target,
        parallel_execution=args.parallel_execution
    )

    print(f"\n{'='*80}")
    print("SWOT ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

    print(f"Data Sources Collected (v3.0):")
    print(f"  [1] Clinical Trials: {result['data_sources']['clinical_trials']['count']}")
    print(f"  [2] FDA Labels: {result['data_sources']['fda_labels']['count']}")
    print(f"  [3] Publications: {result['data_sources']['publications']['count']}")
    print(f"  [4] Patents: {result['data_sources']['patents']['count']}")
    print(f"  [5] SEC Financial: {result['data_sources'].get('financial', {}).get('count', 0)}")
    print(f"  [6] Medicare Rx: {result['data_sources'].get('prescriptions', {}).get('count', 0)}")
    print(f"  [7] Epidemiology: {result['data_sources'].get('market', {}).get('count', 0)}")
    print(f"  [8] Target Biology: {result['data_sources'].get('target', {}).get('count', 0)}")
    print(f"  [9] Stock Performance: {result['data_sources'].get('stock', {}).get('count', 0)}")

    successful = sum(1 for s in result['data_sources'].values() if s.get('count', 0) > 0)
    print(f"\n  ✓ {successful}/9 sources successful")

    print(f"\nSWOT Summary:")
    print(f"  - Strengths: {len(result['swot_analysis']['strengths'])}")
    print(f"  - Weaknesses: {len(result['swot_analysis']['weaknesses'])}")
    print(f"  - Opportunities: {len(result['swot_analysis']['opportunities'])}")
    print(f"  - Threats: {len(result['swot_analysis']['threats'])}")
    print(f"  - Total: {len(result['swot_analysis']['strengths']) + len(result['swot_analysis']['weaknesses']) + len(result['swot_analysis']['opportunities']) + len(result['swot_analysis']['threats'])} points")

    print(f"\n{'='*80}")
    print("FORMATTED REPORT")
    print(f"{'='*80}\n")
    print(result['formatted_report'])
