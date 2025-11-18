#!/usr/bin/env python3
"""
Atomic ClinicalTrials.gov Query Functions

Reusable query functions for ClinicalTrials.gov MCP server.
Each function performs a single, focused query.
"""
import re
from pathlib import Path
import sys

# Add scripts to path for MCP client
script_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(script_dir))

from mcp.client import get_client


def extract_count(text: str) -> int:
    """
    Extract total count from MCP response

    Args:
        text: MCP response text containing "X of Y studies found"

    Returns:
        Total count (Y), or 0 if not found
    """
    match = re.search(r'(\d+) of ([\d,]+) studies found', text)
    return int(match.group(2).replace(',', '')) if match else 0


def get_trial_count(condition: str, **filters) -> int:
    """
    Get total trial count for condition with optional filters

    Args:
        condition: Medical condition (e.g., "obesity", "diabetes")
        **filters: Optional filters (status, phase, location, etc.)

    Returns:
        Total trial count
    """
    client = get_client('ct-gov-mcp')
    result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': condition,
        'pageSize': 10,
        **filters
    })
    return extract_count(result)


def get_phase_distribution(condition: str, status: str = None) -> dict[str, int]:
    """
    Get trial counts by phase

    Args:
        condition: Medical condition
        status: Optional status filter (e.g., "recruiting")

    Returns:
        Dict mapping phase to trial count
    """
    client = get_client('ct-gov-mcp')
    phases = {}

    for phase in ['EARLY_PHASE1', 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4']:
        params = {
            'method': 'search',
            'condition': condition,
            'phase': phase,
            'pageSize': 10
        }
        if status:
            params['status'] = status

        result = client.call_tool('ct_gov_studies', params)
        phases[phase] = extract_count(result)

    return phases


def get_sponsor_breakdown(condition: str, status: str = None) -> dict[str, int]:
    """
    Get trial counts by sponsor type (industry vs academic)

    Args:
        condition: Medical condition
        status: Optional status filter

    Returns:
        Dict with 'industry' and 'academic' counts
    """
    client = get_client('ct-gov-mcp')

    params_base = {
        'method': 'search',
        'condition': condition,
        'pageSize': 10
    }
    if status:
        params_base['status'] = status

    # Industry-sponsored
    industry_params = {**params_base, 'funderType': 'industry'}
    industry_result = client.call_tool('ct_gov_studies', industry_params)
    industry_count = extract_count(industry_result)

    # Academic/other
    academic_params = {**params_base, 'funderType': 'other'}
    academic_result = client.call_tool('ct_gov_studies', academic_params)
    academic_count = extract_count(academic_result)

    return {
        'industry': industry_count,
        'academic': academic_count
    }


def get_intervention_analysis(condition: str, interventions: list[str],
                              status: str = None) -> dict[str, int]:
    """
    Get trial counts by intervention/drug

    Args:
        condition: Medical condition
        interventions: List of intervention terms to search
        status: Optional status filter

    Returns:
        Dict mapping intervention name to trial count
    """
    client = get_client('ct-gov-mcp')
    results = {}

    params_base = {
        'method': 'search',
        'condition': condition,
        'pageSize': 10
    }
    if status:
        params_base['status'] = status

    for intervention in interventions:
        params = {**params_base, 'intervention': intervention}
        result = client.call_tool('ct_gov_studies', params)
        results[intervention] = extract_count(result)

    return results


def get_status_breakdown(condition: str) -> dict[str, int]:
    """
    Get trial counts by status

    Args:
        condition: Medical condition

    Returns:
        Dict mapping status to trial count
    """
    client = get_client('ct-gov-mcp')
    statuses = {}

    for status in ['recruiting', 'active_not_recruiting', 'completed',
                   'not_yet_recruiting', 'terminated', 'withdrawn']:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': condition,
            'status': status,
            'pageSize': 10
        })
        statuses[status] = extract_count(result)

    return statuses


def get_location_breakdown(condition: str, locations: list[str],
                           status: str = None) -> dict[str, int]:
    """
    Get trial counts by location

    Args:
        condition: Medical condition
        locations: List of locations (e.g., ["United States", "United Kingdom"])
        status: Optional status filter

    Returns:
        Dict mapping location to trial count
    """
    client = get_client('ct-gov-mcp')
    results = {}

    params_base = {
        'method': 'search',
        'condition': condition,
        'pageSize': 10
    }
    if status:
        params_base['status'] = status

    for location in locations:
        params = {**params_base, 'location': location}
        result = client.call_tool('ct_gov_studies', params)
        results[location] = extract_count(result)

    return results
