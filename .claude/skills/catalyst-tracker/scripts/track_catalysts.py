#!/usr/bin/env python3
"""Track catalysts across multiple sources (PDUFA, abstracts, trial predictions).

This skill aggregates catalyst events from:
1. PDUFA tracker - FDA approval dates from SEC 8-K filings
2. Abstract acceptance tracker - Conference presentation acceptances from SEC 8-Ks
3. Trial completion predictor - Predicted conference presentations based on trial completions

Generic and parameterized - works for any quarter/year (e.g., Q1 2026, Q4 2025).
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Add .claude to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import importlib.util

def load_tracker_module(skill_name: str, script_name: str):
    """Dynamically load a tracker module."""
    script_path = Path(__file__).parent.parent.parent / skill_name / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.replace('.py', ''), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def track_catalysts(
    quarter: str = "Q4",
    year: int = 2025,
    companies: Optional[List[str]] = None,
    max_companies: int = 100,
    include_predicted: bool = True,
    min_prediction_probability: float = 0.6,
    pdufa_lookback_months: int = 12,
    abstract_lookback_months: int = 9,
    deduplicate: bool = True,
    verbose: bool = True
) -> Dict[str, any]:
    """Track catalyst events across multiple sources.

    Args:
        quarter: Target quarter (Q1, Q2, Q3, Q4)
        year: Target year (e.g., 2025, 2026)
        companies: List of company names to track (optional)
        max_companies: Maximum companies to process (rate limiting)
        include_predicted: Include trial completion predictions
        min_prediction_probability: Minimum probability for predictions (0.0-1.0)
        pdufa_lookback_months: How far back to search for PDUFA dates
        abstract_lookback_months: How far back to search for abstracts
        deduplicate: Remove duplicate catalysts
        verbose: Print progress

    Returns:
        dict: {
            'quarter': str,
            'total': int,
            'catalysts': List[Dict],
            'by_source': Dict[str, int],
            'by_company': Dict[str, int],
            'summary': Dict,
            'errors': List[str]
        }
    """

    if verbose:
        print(f"\n{'='*80}")
        print(f"CATALYST TRACKER: {quarter} {year}")
        print(f"{'='*80}\n")

    all_catalysts = []
    errors = []
    by_source = defaultdict(int)

    # ========================================================================
    # SOURCE 1: PDUFA Dates (SEC 8-K Filings)
    # ========================================================================
    if verbose:
        print("🔍 SOURCE 1: PDUFA DATES (SEC 8-K Filings)")
        print("-" * 80)

    try:
        pdufa_module = load_tracker_module("pdufa-tracker", "track_pdufa_dates.py")
        pdufa_result = pdufa_module.track_pdufa_dates(
            quarter=quarter,
            year=year,
            companies=companies[:max_companies] if companies else None,
            lookback_months=pdufa_lookback_months
        )

        pdufa_dates = pdufa_result.get('pdufa_dates', [])
        if verbose:
            print(f"✓ Found {len(pdufa_dates)} PDUFA dates")

        for pdufa in pdufa_dates:
            all_catalysts.append({
                'source': 'PDUFA',
                'type': 'REGULATORY_APPROVAL',
                'company': pdufa.get('company'),
                'event': f"PDUFA date: {pdufa.get('drug_name', 'Unknown drug')}",
                'date': pdufa.get('pdufa_date'),
                'details': pdufa
            })
            by_source['PDUFA'] += 1

    except Exception as e:
        error_msg = f"PDUFA tracker error: {str(e)}"
        errors.append(error_msg)
        if verbose:
            print(f"✗ {error_msg}")

    print()

    # ========================================================================
    # SOURCE 2: Abstract Acceptances (SEC 8-K Filings)
    # ========================================================================
    if verbose:
        print("🔍 SOURCE 2: ABSTRACT ACCEPTANCES (SEC 8-K Filings)")
        print("-" * 80)

    try:
        abstract_module = load_tracker_module("abstract-acceptance-tracker", "track_abstract_acceptances.py")
        abstract_result = abstract_module.track_abstract_acceptances(
            quarter=quarter,
            year=year,
            companies=companies[:max_companies] if companies else None,
            lookback_months=abstract_lookback_months
        )

        abstracts = abstract_result.get('abstract_acceptances', [])
        if verbose:
            print(f"✓ Found {len(abstracts)} abstract acceptances")

        for abstract in abstracts:
            all_catalysts.append({
                'source': 'ABSTRACT',
                'type': 'CONFERENCE_PRESENTATION',
                'company': abstract.get('company'),
                'event': f"{abstract.get('conference')} presentation: {abstract.get('abstract_title', 'Unknown')}",
                'date': abstract.get('conference_date'),
                'details': abstract
            })
            by_source['ABSTRACT'] += 1

    except Exception as e:
        error_msg = f"Abstract tracker error: {str(e)}"
        errors.append(error_msg)
        if verbose:
            print(f"✗ {error_msg}")

    print()

    # ========================================================================
    # SOURCE 3: Trial Completion Predictions
    # ========================================================================
    if include_predicted:
        if verbose:
            print("🔍 SOURCE 3: TRIAL COMPLETION PREDICTIONS")
            print("-" * 80)

        try:
            predictor_module = load_tracker_module("trial-completion-predictor", "predict_trial_presentations.py")
            predictor_result = predictor_module.predict_trial_presentations(
                quarter=quarter,
                year=year,
                companies=companies[:max_companies] if companies else None,
                min_probability=min_prediction_probability
            )

            predictions = predictor_result.get('predictions', [])
            if verbose:
                print(f"✓ Found {len(predictions)} predicted presentations")

            for prediction in predictions:
                all_catalysts.append({
                    'source': 'PREDICTION',
                    'type': 'PREDICTED_PRESENTATION',
                    'company': prediction.get('company'),
                    'event': f"Predicted {prediction.get('conference')} presentation (trial completed {prediction.get('completion_date')})",
                    'date': prediction.get('predicted_presentation_date'),
                    'probability': prediction.get('probability'),
                    'details': prediction
                })
                by_source['PREDICTION'] += 1

        except Exception as e:
            error_msg = f"Predictor error: {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"✗ {error_msg}")

        print()

    # ========================================================================
    # DEDUPLICATION
    # ========================================================================
    if deduplicate and len(all_catalysts) > 0:
        if verbose:
            print("🔄 DEDUPLICATION")
            print("-" * 80)

        original_count = len(all_catalysts)

        # Deduplicate by (company, event, date)
        seen = set()
        deduplicated = []
        for catalyst in all_catalysts:
            key = (
                catalyst.get('company', '').lower(),
                catalyst.get('event', '').lower()[:50],  # First 50 chars
                catalyst.get('date', '')
            )
            if key not in seen:
                seen.add(key)
                deduplicated.append(catalyst)

        all_catalysts = deduplicated

        if verbose:
            print(f"Original: {original_count} catalysts")
            print(f"Deduplicated: {len(all_catalysts)} catalysts")
            print(f"Removed: {original_count - len(all_catalysts)} duplicates")
            print()

    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    by_company = defaultdict(int)
    for catalyst in all_catalysts:
        by_company[catalyst.get('company', 'Unknown')] += 1

    summary = {
        'total_catalysts': len(all_catalysts),
        'by_source': dict(by_source),
        'by_company': dict(by_company),
        'companies_with_catalysts': len(by_company),
        'companies_tracked': len(companies) if companies else 0
    }

    if verbose:
        print(f"{'='*80}")
        print(f"CATALYST TRACKING COMPLETE")
        print(f"{'='*80}\n")
        print(f"Total catalysts found: {len(all_catalysts)}")
        print(f"By source: {dict(by_source)}")
        print(f"Companies with catalysts: {len(by_company)}")
        if errors:
            print(f"\nErrors: {len(errors)}")
            for error in errors:
                print(f"  - {error}")
        print()

    return {
        'quarter': f'{quarter} {year}',
        'total': len(all_catalysts),
        'catalysts': all_catalysts,
        'by_source': dict(by_source),
        'by_company': dict(by_company),
        'summary': summary,
        'errors': errors
    }


if __name__ == "__main__":
    # Example: Track catalysts for Q1 2026
    result = track_catalysts(
        quarter="Q1",
        year=2026,
        companies=None,  # Will use all companies from discovery
        max_companies=50,
        include_predicted=True,
        min_prediction_probability=0.6
    )

    print("\n" + "="*80)
    print("CATALYST SUMMARY")
    print("="*80)
    print(f"\nQuarter: {result['quarter']}")
    print(f"Total catalysts: {result['total']}")
    print(f"\nBy source:")
    for source, count in result['by_source'].items():
        print(f"  {source}: {count}")
    print(f"\nCompanies with catalysts: {result['summary']['companies_with_catalysts']}")
