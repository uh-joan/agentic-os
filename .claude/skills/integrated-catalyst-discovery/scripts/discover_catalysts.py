#!/usr/bin/env python3
"""Integrated catalyst discovery combining bottom-up discovery with multi-source tracking.

End-to-end workflow:
1. Bottom-up discovery: Find companies with trials completing in target period
2. Catalyst tracking: Search for PDUFA dates, abstracts, predictions
3. Enrichment: Add catalyst data to companies
4. Confidence scoring: Prioritize by HIGH/MEDIUM/LOW confidence

Generic and parameterized - works for any quarter/year (e.g., Q1 2026, Q4 2025).
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Add .claude to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import importlib.util


def load_module(skill_name: str, script_name: str):
    """Dynamically load a skill module."""
    script_path = Path(__file__).parent.parent.parent / skill_name / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.replace('.py', ''), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_catalysts(
    quarter: str = "Q4",
    year: int = 2025,
    phases: Optional[List[str]] = None,
    min_market_cap: float = 0,
    max_discovery_trials: int = 5000,
    max_tracking_companies: int = 100,
    include_predicted: bool = True,
    min_prediction_probability: float = 0.6,
    verbose: bool = True
) -> Dict[str, any]:
    """Integrated catalyst discovery workflow.

    Args:
        quarter: Target quarter (Q1, Q2, Q3, Q4)
        year: Target year (e.g., 2025, 2026)
        phases: Trial phases to include (default: PHASE2, PHASE3)
        min_market_cap: Minimum market cap filter (default: 0 = no filter)
        max_discovery_trials: Maximum trials to search in discovery
        max_tracking_companies: Maximum companies to track (SEC rate limiting)
        include_predicted: Include trial completion predictions
        min_prediction_probability: Minimum probability for predictions (0.0-1.0)
        verbose: Print progress

    Returns:
        dict: {
            'quarter': str,
            'total_companies': int,
            'companies': List[Dict],  # With catalyst enrichment
            'discovery_stats': Dict,
            'tracking_stats': Dict,
            'confidence_breakdown': Dict[str, int]
        }
    """

    if phases is None:
        phases = ['PHASE2', 'PHASE3']

    if verbose:
        print("\n" + "="*80)
        print(f"INTEGRATED CATALYST DISCOVERY: {quarter} {year}")
        print("="*80)
        print()

    # ========================================================================
    # STEP 1: Bottom-Up Discovery
    # ========================================================================
    if verbose:
        print("🔍 STEP 1: BOTTOM-UP DISCOVERY")
        print("-" * 80)
        print(f"Target: {quarter} {year}")
        print(f"Phases: {', '.join(phases)}")
        print(f"Min market cap: ${min_market_cap:,.0f}" if min_market_cap > 0 else "Min market cap: No filter")
        print()

    # Load and run discovery
    discovery_module = load_module("bottom-up-catalyst-discovery", "discover_catalyst_candidates.py")
    discovery_result = discovery_module.discover_catalyst_candidates(
        quarter=quarter,
        year=year,
        phases=phases,
        min_market_cap=min_market_cap,
        max_trials=max_discovery_trials,
        verbose=False  # Suppress internal logging
    )

    companies = discovery_result.get('investable_companies', [])

    if verbose:
        print(f"✓ Discovery complete")
        print(f"  Companies found: {len(companies)}")
        print(f"  Catalyst events: {discovery_result.get('total_catalyst_events', 0)}")
        print()

    # ========================================================================
    # STEP 2: Catalyst Tracking
    # ========================================================================
    if verbose:
        print("📊 STEP 2: CATALYST TRACKING")
        print("-" * 80)
        print(f"Tracking {min(len(companies), max_tracking_companies)} companies")
        print(f"Sources: PDUFA dates, Abstract acceptances, Trial predictions")
        print()

    # Extract company names
    company_names = [c['name'] for c in companies if c.get('name')][:max_tracking_companies]

    # Load and run tracker
    tracker_module = load_module("catalyst-tracker", "track_catalysts.py")
    tracking_result = tracker_module.track_catalysts(
        quarter=quarter,
        year=year,
        companies=company_names,
        max_companies=max_tracking_companies,
        include_predicted=include_predicted,
        min_prediction_probability=min_prediction_probability,
        verbose=False  # Suppress internal logging
    )

    tracked_catalysts = tracking_result.get('catalysts', [])

    if verbose:
        print(f"✓ Tracking complete")
        print(f"  Additional catalysts found: {len(tracked_catalysts)}")
        print(f"  Sources: {tracking_result.get('by_source', {})}")
        print()

    # ========================================================================
    # STEP 3: Enrichment - Add Catalyst Data to Companies
    # ========================================================================
    if verbose:
        print("💎 STEP 3: ENRICHMENT")
        print("-" * 80)

    # Group tracked catalysts by company
    catalysts_by_company = defaultdict(list)
    for catalyst in tracked_catalysts:
        company_name = catalyst.get('company', '')
        catalysts_by_company[company_name].append(catalyst)

    # Enrich companies with catalyst data
    enriched_count = 0
    for company in companies:
        company_name = company.get('name', '')

        # Add tracked catalysts
        tracked = catalysts_by_company.get(company_name, [])
        company['tracked_catalysts'] = tracked

        # Count enrichment
        if tracked:
            enriched_count += 1

    if verbose:
        print(f"✓ Enrichment complete")
        print(f"  Companies with tracked catalysts: {enriched_count}")
        print()

    # ========================================================================
    # STEP 4: Confidence Scoring
    # ========================================================================
    if verbose:
        print("🎯 STEP 4: CONFIDENCE SCORING")
        print("-" * 80)

    confidence_breakdown = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

    for company in companies:
        tracked = company.get('tracked_catalysts', [])
        trials = company.get('trials', [])

        # HIGH: Has PDUFA date or abstract acceptance (dated catalysts)
        has_pdufa = any(c.get('source') == 'PDUFA' for c in tracked)
        has_abstract = any(c.get('source') == 'ABSTRACT' for c in tracked)

        if has_pdufa or has_abstract:
            company['confidence'] = 'HIGH'
            confidence_breakdown['HIGH'] += 1

        # MEDIUM: Has trial completions or predictions
        elif trials or any(c.get('source') == 'PREDICTION' for c in tracked):
            company['confidence'] = 'MEDIUM'
            confidence_breakdown['MEDIUM'] += 1

        # LOW: Only early stage or no specific catalyst
        else:
            company['confidence'] = 'LOW'
            confidence_breakdown['LOW'] += 1

    # Sort by confidence (HIGH → MEDIUM → LOW), then by catalyst count
    confidence_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    companies.sort(
        key=lambda c: (
            confidence_order.get(c.get('confidence', 'LOW'), 3),
            -len(c.get('trials', [])) - len(c.get('tracked_catalysts', []))
        )
    )

    if verbose:
        print(f"✓ Confidence scoring complete")
        print(f"  HIGH confidence: {confidence_breakdown['HIGH']} companies")
        print(f"  MEDIUM confidence: {confidence_breakdown['MEDIUM']} companies")
        print(f"  LOW confidence: {confidence_breakdown['LOW']} companies")
        print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    if verbose:
        print("="*80)
        print("INTEGRATED DISCOVERY COMPLETE")
        print("="*80)
        print()
        print(f"Quarter: {quarter} {year}")
        print(f"Total companies: {len(companies)}")
        print(f"Trial completion events: {discovery_result.get('total_catalyst_events', 0)}")
        print(f"Tracked catalysts (PDUFA/abstracts/predictions): {len(tracked_catalysts)}")
        print()
        print("Confidence breakdown:")
        print(f"  HIGH: {confidence_breakdown['HIGH']} (dated catalysts)")
        print(f"  MEDIUM: {confidence_breakdown['MEDIUM']} (trial completions/predictions)")
        print(f"  LOW: {confidence_breakdown['LOW']} (early stage)")
        print()

    return {
        'quarter': f'{quarter} {year}',
        'total_companies': len(companies),
        'companies': companies,
        'discovery_stats': discovery_result.get('summary', {}),
        'tracking_stats': tracking_result.get('summary', {}),
        'confidence_breakdown': confidence_breakdown,
        'total_trial_events': discovery_result.get('total_catalyst_events', 0),
        'total_tracked_catalysts': len(tracked_catalysts)
    }


if __name__ == "__main__":
    # Example: Discover Q1 2026 catalysts
    result = discover_catalysts(
        quarter="Q1",
        year=2026,
        phases=['PHASE2', 'PHASE3'],
        min_market_cap=0,  # No filter - keep all companies
        max_discovery_trials=5000,
        max_tracking_companies=50,
        include_predicted=True,
        min_prediction_probability=0.6,
        verbose=True
    )

    # Show top 20 companies
    print("\n" + "="*80)
    print("TOP 20 COMPANIES BY CONFIDENCE")
    print("="*80)
    print()

    for i, company in enumerate(result['companies'][:20], 1):
        confidence = company.get('confidence', 'LOW')
        name = company.get('name', 'Unknown')
        ticker = company.get('ticker', 'N/A')
        trial_count = len(company.get('trials', []))
        tracked_count = len(company.get('tracked_catalysts', []))
        mcap = company.get('market_cap', 0)

        print(f"{i}. {name} ({ticker})")
        print(f"   Confidence: {confidence}")
        print(f"   Trial events: {trial_count}")
        print(f"   Tracked catalysts: {tracked_count}")
        if mcap:
            print(f"   Market cap: ${mcap:,.0f}")

        # Show catalyst details
        if tracked_count > 0:
            print("   Tracked events:")
            for cat in company['tracked_catalysts'][:2]:
                print(f"     - {cat.get('event')} ({cat.get('source')})")

        print()
