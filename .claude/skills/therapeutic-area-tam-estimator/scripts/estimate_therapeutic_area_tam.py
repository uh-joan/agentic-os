#!/usr/bin/env python3
"""
Estimate Total Addressable Market (TAM) for therapeutic areas.

Uses multi-source cascade for disease prevalence:
1. CDC PLACES (county-level US data)
2. CDC BRFSS (state-level US data)
3. WHO (global country data)
4. DataCommons (population statistics)

Returns None when insufficient data available.
"""

import sys
import json
import re
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, ".claude")

from mcp.servers.cdc_mcp import get_places_data, get_brfss_data, search_dataset
from mcp.servers.who_mcp import search_indicators, get_health_data
from mcp.servers.datacommons_mcp import search_indicators as dc_search_indicators, get_observations

# Hierarchical disease fallback mapping for rare diseases
# When a rare disease has no data, try broader categories
DISEASE_HIERARCHIES = {
    'nash': ['nafld', 'liver disease', 'metabolic disorders'],
    'nafld': ['liver disease', 'metabolic disorders'],
    'alzheimers': ['dementia', 'cognitive impairment'],
    'alzheimer': ['dementia', 'cognitive impairment'],
    'parkinsons': ['dementia', 'neurological disorders'],
    'parkinson': ['dementia', 'neurological disorders'],
    'als': ['neurological disorders'],
    'huntingtons': ['neurological disorders'],
    'huntington': ['neurological disorders'],
    'cystic fibrosis': ['respiratory disease', 'copd'],
    'duchenne': ['muscular dystrophy', 'neuromuscular disorders'],
    'sma': ['neuromuscular disorders'],
    'gaucher': ['metabolic disorders'],
    'fabry': ['metabolic disorders'],
}


def estimate_therapeutic_area_tam(
    indication: str,
    geography: str = "US",
    target_population: Optional[str] = None
) -> Dict:
    """
    Estimate Total Addressable Market for a therapeutic area.

    Args:
        indication: Disease/condition (e.g., "diabetes", "hypertension", "obesity")
        geography: Geographic scope ("US", "Global", or specific country code)
        target_population: Optional population segment (e.g., "adults", "elderly")

    Returns:
        dict: {
            'indication': str,
            'geography': str,
            'population': int,
            'prevalence_rate': float,
            'affected_population': int,
            'data_source': str,
            'data_quality': str,  # 'high', 'medium', 'low'
            'confidence_level': str,
            'notes': List[str]
        }
        Returns None if insufficient data available.
    """

    notes = []

    # Step 1: Try CDC PLACES data (US county-level, highest quality)
    if geography == "US":
        places_result = _try_cdc_places(indication, target_population)
        if places_result:
            notes.append("Using CDC PLACES county-level data")
            return {
                'indication': indication,
                'geography': geography,
                'population': places_result['population'],
                'prevalence_rate': places_result['prevalence'],
                'affected_population': places_result['affected'],
                'data_source': 'CDC PLACES',
                'data_quality': 'high',
                'confidence_level': 'High - County-level surveillance data',
                'notes': notes
            }

    # Step 2: Try CDC BRFSS data (US state-level)
    if geography == "US":
        brfss_result = _try_cdc_brfss(indication, target_population)
        if brfss_result:
            notes.append("Using CDC BRFSS state-level survey data")
            return {
                'indication': indication,
                'geography': geography,
                'population': brfss_result['population'],
                'prevalence_rate': brfss_result['prevalence'],
                'affected_population': brfss_result['affected'],
                'data_source': 'CDC BRFSS',
                'data_quality': 'medium',
                'confidence_level': 'Medium - State-level survey data',
                'notes': notes
            }

    # Step 3: Try WHO data (global/country-level)
    who_result = _try_who_data(indication, geography, target_population)
    if who_result:
        notes.append(f"Using WHO data for {geography}")
        return {
            'indication': indication,
            'geography': geography,
            'population': who_result['population'],
            'prevalence_rate': who_result['prevalence'],
            'affected_population': who_result['affected'],
            'data_source': 'WHO',
            'data_quality': 'medium',
            'confidence_level': 'Medium - WHO country estimates',
            'notes': notes
        }

    # Step 4: Try DataCommons (population + prevalence estimates)
    dc_result = _try_datacommons(indication, geography, target_population)
    if dc_result:
        notes.append(f"Using DataCommons estimates for {geography}")
        return {
            'indication': indication,
            'geography': geography,
            'population': dc_result['population'],
            'prevalence_rate': dc_result['prevalence'],
            'affected_population': dc_result['affected'],
            'data_source': 'DataCommons',
            'data_quality': 'low',
            'confidence_level': 'Low - Aggregated estimates',
            'notes': notes
        }

    # Step 5: Try hierarchical disease fallback for rare diseases
    indication_lower = indication.lower().strip()
    if indication_lower in DISEASE_HIERARCHIES:
        fallback_categories = DISEASE_HIERARCHIES[indication_lower]
        notes.append(f"No data for {indication}, trying hierarchical fallback")

        for fallback in fallback_categories:
            # Try all data sources for fallback category
            fallback_result = None

            # Try CDC PLACES
            if geography == "US":
                fallback_result = _try_cdc_places(fallback, target_population)
                if fallback_result:
                    notes.append(f"Using {fallback} as proxy estimate (hierarchical fallback)")
                    return {
                        'indication': indication,
                        'geography': geography,
                        'population': fallback_result['population'],
                        'prevalence_rate': fallback_result['prevalence'],
                        'affected_population': fallback_result['affected'],
                        'data_source': f'CDC PLACES (proxy: {fallback})',
                        'data_quality': 'medium',  # Downgraded from high
                        'confidence_level': f'Medium - Proxy estimate using {fallback} prevalence',
                        'notes': notes
                    }

            # Try CDC BRFSS
            if geography == "US":
                fallback_result = _try_cdc_brfss(fallback, target_population)
                if fallback_result:
                    notes.append(f"Using {fallback} as proxy estimate (hierarchical fallback)")
                    return {
                        'indication': indication,
                        'geography': geography,
                        'population': fallback_result['population'],
                        'prevalence_rate': fallback_result['prevalence'],
                        'affected_population': fallback_result['affected'],
                        'data_source': f'CDC BRFSS (proxy: {fallback})',
                        'data_quality': 'low',  # Downgraded from medium
                        'confidence_level': f'Low - Proxy estimate using {fallback} prevalence',
                        'notes': notes
                    }

            # Try WHO
            fallback_result = _try_who_data(fallback, geography, target_population)
            if fallback_result:
                notes.append(f"Using {fallback} as proxy estimate (hierarchical fallback)")
                return {
                    'indication': indication,
                    'geography': geography,
                    'population': fallback_result['population'],
                    'prevalence_rate': fallback_result['prevalence'],
                    'affected_population': fallback_result['affected'],
                    'data_source': f'WHO (proxy: {fallback})',
                    'data_quality': 'low',  # Downgraded from medium
                    'confidence_level': f'Low - Proxy estimate using {fallback} prevalence',
                    'notes': notes
                }

        notes.append(f"Hierarchical fallback exhausted for {indication}")

    # No data available (even after fallback)
    notes.append(f"Insufficient data available for {indication} in {geography}")
    return None


def _try_cdc_places(indication: str, target_population: Optional[str]) -> Optional[Dict]:
    """Try CDC PLACES county-level data."""
    try:
        # Map indication to CDC PLACES measure IDs
        measure_map = {
            'diabetes': 'DIABETES',
            'obesity': 'OBESITY',
            'hypertension': 'BPHIGH',
            'high blood pressure': 'BPHIGH',
            'chronic kidney disease': 'KIDNEY',
            'ckd': 'KIDNEY',
            'copd': 'COPD',
            'asthma': 'CASTHMA',
            'arthritis': 'ARTHRITIS',
            'coronary heart disease': 'CHD',
            'stroke': 'STROKE',
            'depression': 'DEPRESSION',
            'mental health': 'MHLTH',
            'cancer': 'CANCER'
        }

        measure_id = measure_map.get(indication.lower())
        if not measure_id:
            return None

        # Get recent data (2024 or latest available)
        result = get_places_data(
            geography_level='county',
            year='2024',
            measure_id=measure_id,
            limit=5000  # Get all counties
        )

        if not result or not isinstance(result, dict):
            return None

        data = result.get('data', [])
        if not data:
            return None

        # Calculate weighted average prevalence across counties
        total_population = 0
        total_affected = 0

        for record in data:
            try:
                prevalence = float(record.get('data_value', 0))
                # Estimate county population (US total ~330M / 3,000 counties ≈ 110k per county)
                county_pop = 110000

                affected = int((prevalence / 100) * county_pop)
                total_population += county_pop
                total_affected += affected
            except (ValueError, TypeError):
                continue

        if total_population == 0:
            return None

        avg_prevalence = (total_affected / total_population) * 100

        return {
            'population': total_population,
            'prevalence': avg_prevalence,
            'affected': total_affected
        }

    except Exception as e:
        print(f"CDC PLACES error: {e}")
        return None


def _try_cdc_brfss(indication: str, target_population: Optional[str]) -> Optional[Dict]:
    """Try CDC BRFSS comprehensive dataset (state-level survey data)."""
    try:
        # Map indication to BRFSS comprehensive topics
        topic_map = {
            'diabetes': 'Diabetes',
            'copd': 'COPD',
            'cardiovascular disease': 'Cardiovascular Disease',
            'heart attack': 'Cardiovascular Disease',
            'stroke': 'Cardiovascular Disease',
            'coronary heart disease': 'Cardiovascular Disease',
            'depression': 'Depression',
            'kidney disease': 'Kidney',
            'chronic kidney disease': 'Kidney',
            'kidney': 'Kidney'
        }

        topic = topic_map.get(indication.lower())
        if not topic:
            return None

        # Query BRFSS comprehensive dataset with topic filter
        result = search_dataset(
            dataset_name='brfss_comprehensive',
            where_clause=f"topic='{topic}' AND response='Yes' AND break_out='Overall'",
            limit=100  # All states
        )

        if not result or not isinstance(result, dict):
            return None

        data = result.get('data', [])
        if not data:
            return None

        # Calculate average prevalence across states
        prevalence_values = []
        for record in data:
            try:
                value = record.get('data_value')
                if value:
                    prevalence_values.append(float(value))
            except (ValueError, TypeError):
                continue

        if not prevalence_values:
            return None

        avg_prevalence = sum(prevalence_values) / len(prevalence_values)

        # Use actual US population
        population = 340000000
        affected = int((avg_prevalence / 100) * population)

        return {
            'population': population,
            'prevalence': avg_prevalence,
            'affected': affected
        }

    except Exception as e:
        print(f"CDC BRFSS error: {e}")
        return None


def _try_who_data(indication: str, geography: str, target_population: Optional[str]) -> Optional[Dict]:
    """Try WHO country-level data."""
    try:
        # Search for relevant WHO indicators
        indicators_result = search_indicators(keywords=indication)

        if not indicators_result or not isinstance(indicators_result, dict):
            return None

        indicators = indicators_result.get('indicators', [])
        if not indicators:
            return None

        # Use first relevant indicator with "prevalence" in name
        indicator_code = None
        for ind in indicators:
            if 'prevalence' in ind.get('name', '').lower():
                indicator_code = ind.get('code')
                break

        if not indicator_code:
            # Fallback to first indicator
            indicator_code = indicators[0].get('code')

        if not indicator_code:
            return None

        # Get country data
        country_code = 'USA' if geography == 'US' else geography

        country_data = get_health_data(
            indicator_code=indicator_code,
            top=20,
            filter=f"SpatialDim eq '{country_code}'"
        )

        if not country_data or not isinstance(country_data, dict):
            return None

        data = country_data.get('data', [])
        if not data:
            return None

        # Get most recent year's data (filter for both sexes if available)
        data_both_sexes = [d for d in data if d.get('dim1') == 'SEX_BTSX']
        if not data_both_sexes:
            # Fall back to any data
            data_both_sexes = data

        # Get latest year
        latest = max(data_both_sexes, key=lambda x: x.get('time_dim', 0))
        prevalence = float(latest.get('numeric_value', 0))

        # Estimate population (US: 340M, Global: 8B)
        population = 340000000 if country_code == 'USA' else 8000000000
        affected = int((prevalence / 100) * population)

        return {
            'population': population,
            'prevalence': prevalence,
            'affected': affected
        }

    except Exception as e:
        print(f"WHO data error: {e}")
        return None


def _try_datacommons(indication: str, geography: str, target_population: Optional[str]) -> Optional[Dict]:
    """Try DataCommons population and prevalence estimates."""
    try:
        # Search for disease prevalence variables
        search_result = dc_search_indicators(
            query=f"{indication} prevalence {geography}"
        )

        if not search_result or not isinstance(search_result, dict):
            return None

        variables = search_result.get('variables', [])
        if not variables:
            return None

        # Use first relevant variable
        variable_dcid = variables[0].get('dcid')
        if not variable_dcid:
            return None

        # Get observations
        place_dcid = 'country/USA' if geography == 'US' else f'country/{geography}'

        observations = get_observations(
            variable_dcid=variable_dcid,
            place_dcid=place_dcid,
            date='latest'
        )

        if not observations or not isinstance(observations, dict):
            return None

        # DataCommons structure: place_observations is a list
        place_obs = observations.get('place_observations', [])
        if not place_obs or not isinstance(place_obs, list):
            return None

        # Get time series data
        time_series = place_obs[0].get('time_series', [])
        if not time_series:
            return None

        # Latest is last element: [year, value]
        latest = time_series[-1]
        value = float(latest[1])

        # Get population from DataCommons (needed for both count and percentage variables)
        pop_result = get_observations(
            variable_dcid='Count_Person',
            place_dcid=place_dcid,
            date='latest'
        )

        population = 340000000  # Default US
        if pop_result and isinstance(pop_result, dict):
            pop_place_obs = pop_result.get('place_observations', [])
            if pop_place_obs:
                pop_time_series = pop_place_obs[0].get('time_series', [])
                if pop_time_series:
                    population = int(pop_time_series[-1][1])
        elif geography != 'US':
            population = 8000000000  # Default global

        # CRITICAL: Detect if variable is a count or percentage
        # Variables starting with "Count_Person_" return absolute counts
        # Other variables (Percent_, Rate_, etc.) return percentages
        if variable_dcid.startswith('Count_Person_'):
            # This is an absolute count - calculate prevalence
            affected = int(value)
            prevalence = (value / population) * 100
        else:
            # This is already a percentage
            prevalence = value
            affected = int((prevalence / 100) * population)

        return {
            'population': population,
            'prevalence': prevalence,
            'affected': affected
        }

    except Exception as e:
        print(f"DataCommons error: {e}")
        return None


if __name__ == "__main__":
    # Test with multiple indications
    test_cases = [
        ("diabetes", "US", None),
        ("obesity", "US", None),
        ("hypertension", "US", "adults"),
    ]

    print("=== Therapeutic Area TAM Estimator ===\n")

    for indication, geography, target_pop in test_cases:
        result = estimate_therapeutic_area_tam(indication, geography, target_pop)

        print(f"\nIndication: {indication}")
        print(f"Geography: {geography}")
        if target_pop:
            print(f"Target Population: {target_pop}")

        if result:
            print(f"\nEstimated TAM:")
            print(f"  Total Population: {result['population']:,}")
            print(f"  Prevalence Rate: {result['prevalence_rate']:.2f}%")
            print(f"  Affected Population: {result['affected_population']:,}")
            print(f"  Data Source: {result['data_source']}")
            print(f"  Data Quality: {result['data_quality']}")
            print(f"  Confidence: {result['confidence_level']}")
            if result['notes']:
                print(f"  Notes: {'; '.join(result['notes'])}")
        else:
            print("  ❌ Insufficient data available")

        print("-" * 60)
