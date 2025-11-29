"""CDC MCP Server - Python API

Provides Python functions for CDC public health data via Socrata Open Data API (SODA).
Data stays in execution environment - only summaries flow to model.

AVAILABLE DATA SOURCES (73 datasets - Phase 4 Complete):
- PLACES: Local disease prevalence (county, place, census tract, ZIP code)
- BRFSS: Behavioral Risk Factor Surveillance (comprehensive 2011-present)
- YRBSS: Youth Risk Behavior Surveillance
- Respiratory Surveillance: RSV/COVID-19/Flu combined
- Vaccination Coverage: Teen, pregnant, kindergarten
- Birth Statistics: VSRR quarterly indicators
- Environmental Health: Air quality tracking
- NNDSS: National Notifiable Diseases Surveillance (real-time outbreak detection)
- COVID-19 Vaccination: County-level with equity metrics
- Drug Overdose: Real-time crisis monitoring

CRITICAL CDC API QUIRKS:
1. PLACES measure IDs: Use exact codes (e.g., "DIABETES", "OBESITY", "COPD")
2. Geography levels: county, place, tract, zcta
3. State codes: 2-letter abbreviations (e.g., "CA", "TX", "NY")
4. SoQL WHERE clauses: Use Socrata Query Language syntax
5. Rate limiting: 500ms delay between requests (conservative)
6. Response format: JSON with 'data' array
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def cdc_health_data(
    method: str,
    geography_level: Optional[str] = None,
    year: Optional[str] = None,
    state: Optional[str] = None,
    measure_id: Optional[str] = None,
    location: Optional[str] = None,
    dataset_type: Optional[str] = None,
    dataset_name: Optional[str] = None,
    where_clause: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Unified CDC public health data access

    Args:
        method: Operation to perform - 'get_places_data', 'get_brfss_data',
                'search_dataset', 'get_available_measures', 'list_datasets',
                'get_yrbss_data', 'get_respiratory_surveillance',
                'get_vaccination_coverage', 'get_birth_statistics',
                'get_environmental_health', 'get_tobacco_impact',
                'get_oral_vision_health', 'get_injury_surveillance',
                'get_tobacco_policy', 'get_infectious_disease',
                'get_nndss_surveillance', 'get_covid_vaccination',
                'get_overdose_surveillance'

        geography_level: For PLACES - 'county', 'place', 'tract', 'zcta'
        year: Data release year (e.g., "2023", "2024")
        state: State abbreviation (e.g., "CA", "TX", "NY")
        measure_id: Disease/condition code (e.g., "DIABETES", "OBESITY", "COPD")
        location: Specific location name (e.g., "Harris County")
        dataset_type: For BRFSS - 'obesity_national', 'obesity_state', 'diabetes', 'asthma'
        dataset_name: For search_dataset - dataset identifier
        where_clause: SoQL WHERE clause for filtering
        select_fields: List of fields to include
        order_by: Field to order results by
        limit: Maximum results (default: 100)
        offset: Starting position (default: 0)

    Returns:
        dict: CDC health data response

        Response structure:
        {
            'data': [
                {
                    'StateAbbr': 'CA',
                    'LocationName': 'Los Angeles County',
                    'Data_Value': 12.3,
                    'Measure': 'DIABETES',
                    ...
                },
                ...
            ],
            'meta': {
                'total_count': 3142,
                'dataset': 'places_county_2024'
            }
        }

    Examples:
        # Example 1: Get diabetes prevalence in California counties
        result = cdc_health_data(
            method='get_places_data',
            geography_level='county',
            year='2024',
            state='CA',
            measure_id='DIABETES'
        )

        for county in result.get('data', []):
            name = county.get('LocationName')
            value = county.get('Data_Value')
            print(f"{name}: {value}%")

        # Example 2: Get national obesity trends
        result = cdc_health_data(
            method='get_brfss_data',
            dataset_type='obesity_national'
        )

        # Example 3: Search comprehensive BRFSS data
        result = cdc_health_data(
            method='search_dataset',
            dataset_name='brfss_comprehensive',
            where_clause="measure LIKE '%diabetes%' AND year > 2020",
            limit=50
        )

        # Example 4: Get available measures for a dataset
        result = cdc_health_data(
            method='get_available_measures',
            dataset_name='places_county_2024'
        )

        measures = result.get('measures', [])
        print(f"Available measures: {len(measures)}")
        for measure in measures[:10]:
            print(f"  - {measure.get('measure_id')}: {measure.get('measure_name')}")

        # Example 5: List all CDC datasets
        result = cdc_health_data(
            method='list_datasets'
        )

        datasets = result.get('datasets', [])
        print(f"Total datasets: {len(datasets)}")

        # Example 6: Get NNDSS disease surveillance
        result = cdc_health_data(
            method='get_nndss_surveillance',
            where_clause="disease = 'Hepatitis A' AND year = 2024"
        )

        # Example 7: Get COVID vaccination by county
        result = cdc_health_data(
            method='get_covid_vaccination',
            state='CA',
            limit=100
        )

        # Example 8: Get drug overdose deaths
        result = cdc_health_data(
            method='get_overdose_surveillance',
            where_clause="state = 'CA' AND year = 2024"
        )

    PLACES Measure IDs (40+ available):
        Chronic Diseases:
        - DIABETES: Diagnosed diabetes
        - OBESITY: Adult obesity (BMI ≥30)
        - COPD: Chronic obstructive pulmonary disease
        - CASTHMA: Current asthma
        - CHD: Coronary heart disease
        - STROKE: Stroke
        - BPHIGH: High blood pressure
        - KIDNEY: Chronic kidney disease
        - CANCER: Cancer (excluding skin)
        - ARTHRITIS: Arthritis

        Mental Health:
        - DEPRESSION: Depression
        - MHLTH: Mental health not good ≥14 days

        Risk Factors:
        - CSMOKING: Current smoking
        - BINGE: Binge drinking
        - LPA: No leisure-time physical activity
        - SLEEP: Sleep <7 hours
    """
    client = get_client('cdc-mcp-server')

    params = {
        'method': method
    }

    # Add optional parameters
    if geography_level:
        params['geography_level'] = geography_level
    if year:
        params['year'] = year
    if state:
        params['state'] = state
    if measure_id:
        params['measure_id'] = measure_id
    if location:
        params['location'] = location
    if dataset_type:
        params['dataset_type'] = dataset_type
    if dataset_name:
        params['dataset_name'] = dataset_name
    if where_clause:
        params['where_clause'] = where_clause
    if select_fields:
        params['select_fields'] = select_fields
    if order_by:
        params['order_by'] = order_by
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset

    return client.call_tool('cdc_health_data', params)


# Convenience functions for common operations

def get_places_data(
    geography_level: str,
    year: str,
    measure_id: str,
    state: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Get PLACES local disease prevalence data

    Args:
        geography_level: 'county', 'place', 'tract', or 'zcta'
        year: '2023' or '2024'
        measure_id: Disease code (e.g., 'DIABETES', 'OBESITY')
        state: State abbreviation (optional)
        location: Specific location name (optional)
        limit: Maximum results (default: 100)

    Returns:
        dict: PLACES disease prevalence data
    """
    return cdc_health_data(
        method='get_places_data',
        geography_level=geography_level,
        year=year,
        measure_id=measure_id,
        state=state,
        location=location,
        limit=limit
    )


def get_brfss_data(
    dataset_type: str,
    year: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Get BRFSS behavioral risk factor data

    Args:
        dataset_type: 'obesity_national', 'obesity_state', 'diabetes', 'asthma', 'comprehensive'
        year: Data year (optional)
        state: State abbreviation (optional)
        limit: Maximum results (default: 100)

    Returns:
        dict: BRFSS behavioral risk data
    """
    return cdc_health_data(
        method='get_brfss_data',
        dataset_type=dataset_type,
        year=year,
        state=state,
        limit=limit
    )


def search_dataset(
    dataset_name: str,
    where_clause: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Search any CDC dataset with SoQL query

    Args:
        dataset_name: Dataset identifier (e.g., 'brfss_comprehensive')
        where_clause: SoQL WHERE clause for filtering
        limit: Maximum results (default: 100)

    Returns:
        dict: Dataset search results
    """
    return cdc_health_data(
        method='search_dataset',
        dataset_name=dataset_name,
        where_clause=where_clause,
        limit=limit
    )


def get_available_measures(dataset_name: str) -> Dict[str, Any]:
    """List available measures for a dataset

    Args:
        dataset_name: Dataset identifier

    Returns:
        dict: Available health measures
    """
    return cdc_health_data(
        method='get_available_measures',
        dataset_name=dataset_name
    )


def list_datasets() -> Dict[str, Any]:
    """List all available CDC datasets

    Returns:
        dict: All CDC datasets (73 total)
    """
    return cdc_health_data(method='list_datasets')


__all__ = [
    'cdc_health_data',
    'get_places_data',
    'get_brfss_data',
    'search_dataset',
    'get_available_measures',
    'list_datasets'
]
