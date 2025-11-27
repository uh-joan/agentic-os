#!/usr/bin/env python3
import sys
sys.path.insert(0, ".claude")

import re
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any

from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.sec_edgar_mcp import get_company_cik, get_company_facts
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.uspto_patents_mcp import google_search_by_assignee
from mcp.servers.financials_mcp import financial_intelligence


def get_clinical_pipeline(company_name: str) -> Dict[str, Any]:
    """Collect ACTIVE clinical trial pipeline from ClinicalTrials.gov with pagination.

    Focuses on active/recruiting trials only (not historical completed/terminated trials).
    This provides a true picture of current R&D pipeline for SWOT analysis.
    """
    print(f"\n📊 Collecting ACTIVE clinical pipeline for {company_name}...")

    try:
        all_trial_blocks = []
        page_token = None

        # Active pipeline statuses (exclude completed, terminated, withdrawn, suspended)
        active_status = "recruiting OR not_yet_recruiting OR active_not_recruiting OR enrolling_by_invitation"

        # Pagination loop - collect ALL active trials
        while True:
            if page_token:
                result = ct_search(
                    lead=company_name,
                    status=active_status,
                    pageSize=5000,
                    pageToken=page_token
                )
            else:
                result = ct_search(
                    lead=company_name,
                    status=active_status,
                    pageSize=5000
                )

            trials_text = result if isinstance(result, str) else str(result)

            # Parse trials from this page
            trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', trials_text)[1:]

            if not trial_blocks:
                break

            all_trial_blocks.extend(trial_blocks)

            # Check for next page
            page_match = re.search(r'pageToken:\s*"([^"]+)"', trials_text)
            if page_match:
                page_token = page_match.group(1)
                print(f"   Fetched {len(trial_blocks)} trials, continuing pagination...")
            else:
                break

        print(f"   Active trials collected: {len(all_trial_blocks)} (recruiting/ongoing only)")

        # Parse all collected trials
        phases = []
        statuses = []
        conditions = []

        for trial in all_trial_blocks:
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial)
            if phase_match:
                phases.append(phase_match.group(1).strip())

            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', trial)
            if status_match:
                statuses.append(status_match.group(1).strip())

            condition_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', trial)
            if condition_match:
                conditions.append(condition_match.group(1).strip())

        return {
            'total_trials': len(all_trial_blocks),
            'phase_distribution': dict(Counter(phases).most_common()),
            'status_distribution': dict(Counter(statuses).most_common(5)),
            'therapeutic_areas': dict(Counter(conditions).most_common(10)),
            'success': True
        }
    except Exception as e:
        return {'total_trials': 0, 'success': False, 'error': str(e)}


def get_financial_data(company_name: str) -> Dict[str, Any]:
    """Collect financial data from SEC EDGAR."""
    print(f"\n💰 Collecting financial data for {company_name}...")
    
    try:
        cik_result = get_company_cik(ticker=company_name)
        
        if isinstance(cik_result, str):
            cik_match = re.search(r'CIK:\s*(\d{10})', cik_result)
            if not cik_match:
                raise ValueError("Could not extract CIK")
            cik = cik_match.group(1)
        elif isinstance(cik_result, dict):
            cik = cik_result.get('cik', '')
        else:
            raise ValueError("Unexpected CIK format")
        
        facts = get_company_facts(cik_or_ticker=cik)
        
        # Simplified extraction (markdown response)
        revenue = None
        rd_spending = None
        
        if isinstance(facts, str):
            rev_match = re.search(r'Revenue[:\s]+\$?([\d,\.]+)\s*([MB])?', facts, re.I)
            rd_match = re.search(r'R.*D.*Expense[:\s]+\$?([\d,\.]+)\s*([MB])?', facts, re.I)
            
            if rev_match:
                val = float(rev_match.group(1).replace(',', ''))
                unit = rev_match.group(2)
                revenue = val * (1e9 if unit=='B' else 1e6 if unit=='M' else 1)
            
            if rd_match:
                val = float(rd_match.group(1).replace(',', ''))
                unit = rd_match.group(2)
                rd_spending = val * (1e9 if unit=='B' else 1e6 if unit=='M' else 1)
        
        return {'revenue': revenue, 'rd_spending': rd_spending, 'success': True}
    except Exception as e:
        return {'revenue': None, 'rd_spending': None, 'success': False, 'error': str(e)}


def get_approved_products(company_name: str) -> Dict[str, Any]:
    """Collect FDA approved products."""
    print(f"\n💊 Collecting FDA products for {company_name}...")
    
    try:
        # Use count-first pattern
        result = lookup_drug(
            search_term=company_name,
            search_type='general',
            count='openfda.brand_name.exact',
            limit=100
        )
        
        data = result.get('data', {})
        results = data.get('results', [])
        
        return {
            'total_products': len(results),
            'product_names': [item.get('term', '') for item in results[:20]],
            'therapeutic_areas': {},
            'success': True
        }
    except Exception as e:
        return {'total_products': 0, 'success': False, 'error': str(e)}


def get_patent_portfolio(company_name: str) -> Dict[str, Any]:
    """Collect patent portfolio from Google Patents."""
    print(f"\n📜 Collecting patents for {company_name}...")
    
    try:
        result = google_search_by_assignee(assignee_name=company_name, country="US", limit=500)
        
        if isinstance(result, str):
            patents = len(re.findall(r'###\s+\d+\.', result))
            years = re.findall(r'Publication\s+Date:\s*(\d{4})', result)
            
            return {
                'total_patents': patents,
                'publication_years': dict(Counter(years).most_common()),
                'success': True
            }
        
        return {'total_patents': 0, 'success': False}
    except Exception as e:
        return {'total_patents': 0, 'success': False, 'error': str(e)}


def get_market_performance(company_name: str) -> Dict[str, Any]:
    """Collect market data from Yahoo Finance."""
    print(f"\n📈 Collecting market data for {company_name}...")
    
    try:
        symbol = company_name.upper().replace(' ', '')
        result = financial_intelligence(method='stock_summary', symbol=symbol)
        
        market_cap = None
        stock_price = None
        
        if isinstance(result, str):
            mcap_match = re.search(r'Market\s+Cap[:\s]+\$?([\d,\.]+)\s*([BMK])?', result, re.I)
            price_match = re.search(r'Price[:\s]+\$?([\d,\.]+)', result, re.I)
            
            if mcap_match:
                val = float(mcap_match.group(1).replace(',', ''))
                unit = mcap_match.group(2)
                market_cap = val * (1e9 if unit=='B' else 1e6 if unit=='M' else 1e3 if unit=='K' else 1)
            
            if price_match:
                stock_price = float(price_match.group(1).replace(',', ''))
        
        return {'market_cap': market_cap, 'stock_price': stock_price, 'success': True}
    except Exception as e:
        return {'market_cap': None, 'stock_price': None, 'success': False, 'error': str(e)}


def categorize_swot(clinical_data, financial_data, fda_data, patent_data, market_data, company_name=None):
    """Categorize data into SWOT framework."""
    print("\n🎯 Categorizing into SWOT framework...")
    
    swot = {'strengths': [], 'weaknesses': [], 'opportunities': [], 'threats': []}
    
    # STRENGTHS
    if fda_data.get('total_products', 0) > 0:
        swot['strengths'].append({
            'category': 'Product Portfolio',
            'point': f"FDA-approved portfolio with {fda_data['total_products']} products",
            'evidence': f"Therapeutic areas: {len(fda_data.get('therapeutic_areas', {}))}"
        })
    
    if clinical_data.get('total_trials', 0) > 20:
        phase3 = clinical_data.get('phase_distribution', {}).get('Phase 3', 0)
        swot['strengths'].append({
            'category': 'Product Innovation',
            'point': f"Robust pipeline with {clinical_data['total_trials']} trials",
            'evidence': f"Including {phase3} Phase 3 programs"
        })
    
    if patent_data.get('total_patents', 0) > 50:
        swot['strengths'].append({
            'category': 'Intellectual Property',
            'point': f"Strong patent portfolio with {patent_data['total_patents']} patents",
            'evidence': "Active patent filing demonstrating innovation"
        })
    
    if financial_data.get('revenue'):
        rev_b = financial_data['revenue'] / 1e9
        swot['strengths'].append({
            'category': 'Financial Performance',
            'point': f"Revenue base of ${rev_b:.1f}B",
            'evidence': "SEC EDGAR filings show commercial operations"
        })
    
    # WEAKNESSES
    phase3 = clinical_data.get('phase_distribution', {}).get('Phase 3', 0)
    total = clinical_data.get('total_trials', 0)
    if total > 0 and phase3 < 5:
        swot['weaknesses'].append({
            'category': 'Clinical Development',
            'point': f"Limited late-stage pipeline ({phase3} Phase 3 trials)",
            'evidence': f"Out of {total} total trials"
        })
    
    # OPPORTUNITIES
    recruiting = clinical_data.get('status_distribution', {}).get('Recruiting', 0)
    if recruiting > 10:
        swot['opportunities'].append({
            'category': 'Market Expansion',
            'point': f"{recruiting} recruiting trials offer label expansion",
            'evidence': f"Across {len(clinical_data.get('therapeutic_areas', {}))} areas"
        })
    
    # THREATS
    if clinical_data.get('therapeutic_areas'):
        top_area = list(clinical_data['therapeutic_areas'].keys())[0]
        swot['threats'].append({
            'category': 'Competition',
            'point': f"Competitive pressure in {top_area}",
            'evidence': "Industry-wide investment in therapeutic area"
        })
    
    return swot


def format_swot_report(company_name, data_sources, swot_analysis, analysis_date):
    """Format SWOT as markdown report."""
    
    report = f"""# {company_name} SWOT Analysis

**Analysis Date:** {analysis_date}
**Generated by:** Pharmaceutical Research Intelligence Platform

---

## Executive Summary

Comprehensive SWOT analysis evaluating {company_name}'s strategic position across clinical development, commercial operations, intellectual property, and market performance.

### Data Sources Summary

| Source | Count | Details |
|--------|-------|---------|
| Active Clinical Pipeline | {data_sources['clinical_pipeline']['total_trials']} trials | {', '.join(f"{k}: {v}" for k, v in list(data_sources['clinical_pipeline'].get('phase_distribution', {}).items())[:3])} (recruiting/ongoing only) |
| Financial Data | SEC EDGAR | Revenue: ${(data_sources['financial_data'].get('revenue') or 0)/1e9:.1f}B |
| FDA Products | {data_sources['approved_products']['total_products']} | Therapeutic areas: {len(data_sources['approved_products'].get('therapeutic_areas', {}))} |
| Patents | {data_sources['patent_portfolio']['total_patents']} | US patent portfolio |
| Market Cap | ${(data_sources['market_performance'].get('market_cap') or 0)/1e9:.1f}B | Stock: ${data_sources['market_performance'].get('stock_price') or 0:.2f} |

---

## **Strengths**

"""
    
    for item in swot_analysis['strengths']:
        report += f"\n**{item['category']}**\n"
        report += f"- {item['point']}\n"
        report += f"  - *Evidence:* {item['evidence']}\n"
    
    report += "\n---\n\n## **Weaknesses**\n"
    
    for item in swot_analysis['weaknesses']:
        report += f"\n**{item['category']}**\n"
        report += f"- {item['point']}\n"
        report += f"  - *Evidence:* {item['evidence']}\n"
    
    report += "\n---\n\n## **Opportunities**\n"
    
    for item in swot_analysis['opportunities']:
        report += f"\n**{item['category']}**\n"
        report += f"- {item['point']}\n"
        report += f"  - *Evidence:* {item['evidence']}\n"
    
    report += "\n---\n\n## **Threats**\n"
    
    for item in swot_analysis['threats']:
        report += f"\n**{item['category']}**\n"
        report += f"- {item['point']}\n"
        report += f"  - *Evidence:* {item['evidence']}\n"
    
    report += """

---

## **Sources**

- ClinicalTrials.gov - Clinical trial registry
- SEC EDGAR - Financial filings (10-K, 10-Q)
- FDA Drugs Database - Approved products
- Google Patents - USPTO patent search
- Yahoo Finance - Market performance

---

*This analysis is based on publicly available data for informational purposes only.*
"""
    
    return report


def generate_company_swot_analysis(company_name: str) -> Dict[str, Any]:
    """Generate comprehensive company SWOT analysis.
    
    Args:
        company_name: Company name (e.g., "Exelixis", "Pfizer")
        
    Returns:
        dict: Contains data_sources, swot_analysis, formatted_report
    """
    print(f"\n{'='*80}")
    print(f"Generating SWOT Analysis for {company_name}")
    print(f"{'='*80}")
    
    analysis_date = datetime.now().strftime("%Y-%m-%d")
    
    # Collect data
    clinical_data = get_clinical_pipeline(company_name)
    financial_data = get_financial_data(company_name)
    fda_data = get_approved_products(company_name)
    patent_data = get_patent_portfolio(company_name)
    market_data = get_market_performance(company_name)
    
    # Categorize into SWOT
    swot_analysis = categorize_swot(
        clinical_data, financial_data, fda_data,
        patent_data, market_data, company_name
    )
    
    # Format report
    report = format_swot_report(
        company_name,
        {
            'clinical_pipeline': clinical_data,
            'financial_data': financial_data,
            'approved_products': fda_data,
            'patent_portfolio': patent_data,
            'market_performance': market_data
        },
        swot_analysis,
        analysis_date
    )
    
    return {
        'company_name': company_name,
        'last_updated': analysis_date,
        'data_sources': {
            'clinical_pipeline': clinical_data,
            'financial_data': financial_data,
            'approved_products': fda_data,
            'patent_portfolio': patent_data,
            'market_performance': market_data
        },
        'swot_analysis': swot_analysis,
        'formatted_report': report
    }


if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "Exelixis"
    
    result = generate_company_swot_analysis(company)
    
    print(f"\n{'='*80}")
    print(f"SWOT Analysis Complete: {result['company_name']}")
    print(f"{'='*80}")
    print(f"\nData Collection:")
    print(f"  Clinical Trials: {result['data_sources']['clinical_pipeline']['total_trials']}")
    print(f"  FDA Products: {result['data_sources']['approved_products']['total_products']}")
    print(f"  Patents: {result['data_sources']['patent_portfolio']['total_patents']}")
    print(f"\nSWOT Framework:")
    print(f"  Strengths: {len(result['swot_analysis']['strengths'])} points")
    print(f"  Weaknesses: {len(result['swot_analysis']['weaknesses'])} points")
    print(f"  Opportunities: {len(result['swot_analysis']['opportunities'])} points")
    print(f"  Threats: {len(result['swot_analysis']['threats'])} points")
    print(f"\n{'='*80}\n")
