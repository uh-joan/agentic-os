"""Healthcare MCP Server - Python API

Provides Python functions for CMS Medicare provider data and NLM medical codes.
Data stays in execution environment - only summaries flow to model.

CRITICAL HEALTHCARE MCP QUIRKS:
1. CMS Medicare data: Three dataset types (geography_and_service, provider_and_service, provider)
2. Dataset selection: Choose based on analysis goal (geographic vs provider-level)
3. Year parameter: 2013-latest (defaults to latest), data availability varies
4. HCPCS codes: Must match exactly (e.g., '99213', '27447')
5. Geographic levels: National, State, County, ZIP
6. Response size: max 5000 records per query (use pagination for more)
7. Field names: Underscore-based (Rndrng_Prvdr_Type, Tot_Mdcr_Pymt_Amt)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def cms_search_providers(
    dataset_type: str,
    year: Optional[str] = None,
    hcpcs_code: Optional[str] = None,
    provider_type: Optional[str] = None,
    geo_level: Optional[str] = None,
    geo_code: Optional[str] = None,
    place_of_service: Optional[str] = None,
    size: int = 10,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Search Medicare Physician & Other Practitioners data using CMS database

    Access Medicare Part B service data from CMS. Choose dataset type based on analysis goal.

    Args:
        dataset_type: Type of dataset to search (REQUIRED)

                     VALUES AND USE CASES:

                     "geography_and_service" - Geographic analysis
                     Use when you need to:
                     - Compare regions (states, counties, ZIP codes)
                     - Analyze geographic patterns in healthcare delivery
                     - Study regional variations in service provision
                     - Calculate per-capita/per-beneficiary rates by region
                     - Map healthcare service distribution

                     "provider_and_service" - Provider-level analysis
                     Use when you need to:
                     - Analyze individual provider performance
                     - Track specific procedures by provider
                     - Calculate total procedures across providers
                     - Study provider-level service patterns
                     - Identify high-volume providers

                     "provider" - Provider demographics
                     Use when you need to:
                     - Analyze provider demographics
                     - Study provider participation in Medicare
                     - Understand provider practice patterns
                     - Examine beneficiary characteristics and risk scores
                     - Analyze provider-level aggregated metrics

        year: Year of dataset (2013 to latest, default: latest)
             Examples: "2023", "2022", "2021"

             ⚠️  Data availability varies by year and dataset type

        hcpcs_code: HCPCS procedure/service code (optional)
                   Common codes:
                   - "99213" - Established patient office visit (moderate)
                   - "99214" - Established patient office visit (moderate-high)
                   - "27447" - Total knee arthroplasty
                   - "27130" - Total hip arthroplasty
                   - "93010" - Electrocardiogram interpretation
                   - "80053" - Comprehensive metabolic panel
                   - "36415" - Blood draw

        provider_type: Provider specialty type (optional)
                      Examples: "Cardiology", "Podiatry", "Family Practice",
                               "Internal Medicine", "Orthopedic Surgery"
                      Supports partial matches, case-insensitive

        geo_level: Geographic level for filtering (optional)
                  Values: "National", "State", "County", "ZIP"
                  Use with geo_code parameter

        geo_code: Geographic code (optional)
                 Examples:
                 - State: "CA", "NY", "TX"
                 - County: "06037" (Los Angeles County)
                 - ZIP: "90210", "10001"
                 Must match geo_level specified

        place_of_service: Service location code (optional)
                         Common codes:
                         - "F" - Facility
                         - "O" - Office
                         - "H" - Hospital

        size: Number of results to return (1-5000, default: 10)
             Use with offset for pagination

        offset: Starting result number (0-based, default: 0)
               Use with size for pagination

        sort_by: Field to sort results by (optional)
                Common fields:
                - "Tot_Srvcs" - Total services
                - "Tot_Benes" - Total beneficiaries
                - "Tot_Mdcr_Pymt_Amt" - Total Medicare payment
                - "Avg_Mdcr_Pymt_Amt" - Average Medicare payment

        sort_order: Sort order (default: "desc")
                   Values: "asc", "desc"

    Returns:
        dict: Medicare provider data

        Response varies by dataset_type:

        geography_and_service fields:
        - Rndrng_Prvdr_Geo_Lvl: Geographic level
        - Rndrng_Prvdr_Geo_Cd: Geographic code
        - HCPCS_Cd: HCPCS code
        - HCPCS_Desc: Service description
        - Tot_Rndrng_Prvdrs: Total providers
        - Tot_Benes: Total beneficiaries
        - Tot_Srvcs: Total services
        - Avg_Mdcr_Pymt_Amt: Average Medicare payment

        provider_and_service fields:
        - Rndrng_NPI: Provider NPI
        - Rndrng_Prvdr_Last_Org_Name: Provider name
        - Rndrng_Prvdr_Type: Provider specialty
        - HCPCS_Cd: HCPCS code
        - Tot_Srvcs: Total services
        - Avg_Mdcr_Pymt_Amt: Average Medicare payment

        provider fields:
        - Rndrng_NPI: Provider NPI
        - Rndrng_Prvdr_Last_Org_Name: Provider name
        - Rndrng_Prvdr_Type: Provider specialty
        - Tot_HCPCS_Cds: Unique procedure codes
        - Tot_Benes: Total beneficiaries
        - Bene_Avg_Age: Average beneficiary age
        - Bene_Avg_Risk_Scre: Average risk score

    Examples:
        # Example 1: Geographic analysis - office visits in California
        results = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="State",
            geo_code="CA",
            hcpcs_code="99213",
            year="2023",
            size=50
        )

        # Extract geographic data
        for record in results.get('data', []):
            geo_desc = record.get('Rndrng_Prvdr_Geo_Desc')
            tot_services = record.get('Tot_Srvcs')
            tot_benes = record.get('Tot_Benes')
            avg_payment = record.get('Avg_Mdcr_Pymt_Amt')
            print(f"{geo_desc}: {tot_services:,} services, {tot_benes:,} beneficiaries")
            print(f"  Average payment: ${avg_payment:.2f}")

        # Example 2: Compare knee replacements across states
        results = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="State",
            hcpcs_code="27447",
            year="2023",
            sort_by="Tot_Srvcs",
            sort_order="desc",
            size=10
        )

        # Rank states by volume
        print("Top 10 States by Knee Replacement Volume:")
        for rank, record in enumerate(results.get('data', []), 1):
            state = record.get('Rndrng_Prvdr_Geo_Desc')
            volume = record.get('Tot_Srvcs')
            providers = record.get('Tot_Rndrng_Prvdrs')
            avg_payment = record.get('Avg_Mdcr_Pymt_Amt')
            print(f"{rank}. {state}: {volume:,} procedures")
            print(f"   {providers} providers, avg payment ${avg_payment:,.2f}")

        # Example 3: Provider-level analysis - high-volume knee surgeons
        results = cms_search_providers(
            dataset_type="provider_and_service",
            geo_level="State",
            geo_code="CA",
            hcpcs_code="27447",
            year="2023",
            sort_by="Tot_Srvcs",
            sort_order="desc",
            size=20
        )

        # Identify top providers
        print("Top 20 Knee Replacement Providers in California:")
        for provider in results.get('data', []):
            npi = provider.get('Rndrng_NPI')
            last_name = provider.get('Rndrng_Prvdr_Last_Org_Name')
            first_name = provider.get('Rndrng_Prvdr_First_Name')
            city = provider.get('Rndrng_Prvdr_City')
            volume = provider.get('Tot_Srvcs')
            avg_payment = provider.get('Avg_Mdcr_Pymt_Amt')

            name = f"{first_name} {last_name}" if first_name else last_name
            print(f"{name} ({city}): {volume} procedures")
            print(f"  NPI: {npi}, Avg payment: ${avg_payment:.2f}")

        # Example 4: Cardiology practice patterns
        results = cms_search_providers(
            dataset_type="provider_and_service",
            provider_type="Cardiology",
            hcpcs_code="93010",
            year="2023",
            sort_by="Tot_Srvcs",
            sort_order="desc",
            size=100
        )

        # Analyze practice patterns
        total_ecgs = sum(r.get('Tot_Srvcs', 0) for r in results.get('data', []))
        total_providers = len(results.get('data', []))
        avg_per_provider = total_ecgs / total_providers if total_providers else 0

        print(f"Cardiology ECG Analysis:")
        print(f"  Total ECGs: {total_ecgs:,}")
        print(f"  Providers: {total_providers}")
        print(f"  Average per provider: {avg_per_provider:.0f}")

        # Example 5: Provider demographics and patient characteristics
        results = cms_search_providers(
            dataset_type="provider",
            provider_type="Family Practice",
            geo_level="State",
            geo_code="TX",
            year="2023",
            sort_by="Tot_Benes",
            sort_order="desc",
            size=50
        )

        # Analyze patient populations
        for provider in results.get('data', []):
            name = provider.get('Rndrng_Prvdr_Last_Org_Name')
            city = provider.get('Rndrng_Prvdr_City')
            tot_benes = provider.get('Tot_Benes')
            avg_age = provider.get('Bene_Avg_Age')
            avg_risk = provider.get('Bene_Avg_Risk_Scre')
            female_cnt = provider.get('Bene_Feml_Cnt')
            male_cnt = provider.get('Bene_Male_Cnt')

            if tot_benes:
                female_pct = (female_cnt / tot_benes * 100) if female_cnt else 0
                print(f"{name} ({city})")
                print(f"  Beneficiaries: {tot_benes:,}")
                print(f"  Avg age: {avg_age:.1f}, Risk score: {avg_risk:.2f}")
                print(f"  Gender: {female_pct:.1f}% female")

        # Example 6: ZIP code analysis - compare payments
        results = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="ZIP",
            hcpcs_code="99214",
            year="2023",
            sort_by="Avg_Mdcr_Pymt_Amt",
            sort_order="desc",
            size=100
        )

        # Find payment variation
        payments = [r.get('Avg_Mdcr_Pymt_Amt', 0) for r in results.get('data', [])]
        if payments:
            max_payment = max(payments)
            min_payment = min(payments)
            avg_payment = sum(payments) / len(payments)

            print(f"Office Visit (99214) Payment Variation Across ZIP Codes:")
            print(f"  Range: ${min_payment:.2f} - ${max_payment:.2f}")
            print(f"  Average: ${avg_payment:.2f}")
            print(f"  Variation: {(max_payment - min_payment) / avg_payment * 100:.1f}%")

        # Example 7: County-level analysis - Los Angeles
        results = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="County",
            geo_code="06037",
            hcpcs_code="27130",
            year="2023"
        )

        # Example 8: Pagination for large result sets
        all_providers = []
        page_size = 1000
        offset = 0

        while True:
            page = cms_search_providers(
                dataset_type="provider",
                provider_type="Internal Medicine",
                geo_level="State",
                geo_code="FL",
                year="2023",
                size=page_size,
                offset=offset
            )

            providers = page.get('data', [])
            all_providers.extend(providers)

            if len(providers) < page_size:
                break

            offset += page_size

        print(f"Total Internal Medicine providers in Florida: {len(all_providers)}")

        # Example 9: Place of service comparison
        office_data = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="State",
            geo_code="NY",
            hcpcs_code="99213",
            place_of_service="O",
            year="2023"
        )

        facility_data = cms_search_providers(
            dataset_type="geography_and_service",
            geo_level="State",
            geo_code="NY",
            hcpcs_code="99213",
            place_of_service="F",
            year="2023"
        )

        office_total = office_data.get('data', [{}])[0].get('Tot_Srvcs', 0)
        facility_total = facility_data.get('data', [{}])[0].get('Tot_Srvcs', 0)

        print(f"NY Office Visits (99213):")
        print(f"  Office setting: {office_total:,}")
        print(f"  Facility setting: {facility_total:,}")

        # Example 10: Multi-year trend analysis
        years = ["2021", "2022", "2023"]
        trend_data = []

        for year in years:
            result = cms_search_providers(
                dataset_type="geography_and_service",
                geo_level="National",
                hcpcs_code="27447",
                year=year
            )

            if result.get('data'):
                record = result['data'][0]
                trend_data.append({
                    'year': year,
                    'total_services': record.get('Tot_Srvcs'),
                    'avg_payment': record.get('Avg_Mdcr_Pymt_Amt')
                })

        print("National Knee Replacement Trends:")
        for data in trend_data:
            year = data['year']
            services = data['total_services']
            payment = data['avg_payment']
            print(f"  {year}: {services:,} procedures, ${payment:.2f} avg payment")

        if len(trend_data) >= 2:
            growth = ((trend_data[-1]['total_services'] - trend_data[0]['total_services']) /
                     trend_data[0]['total_services'] * 100)
            print(f"  Growth: {growth:+.1f}%")
    """
    client = get_client('healthcare-mcp')

    params = {
        'dataset_type': dataset_type,
        'size': size,
        'offset': offset,
        'sort_order': sort_order
    }

    if year:
        params['year'] = year
    if hcpcs_code:
        params['hcpcs_code'] = hcpcs_code
    if provider_type:
        params['provider_type'] = provider_type
    if geo_level:
        params['geo_level'] = geo_level
    if geo_code:
        params['geo_code'] = geo_code
    if place_of_service:
        params['place_of_service'] = place_of_service
    if sort_by:
        params['sort_by'] = sort_by

    return client.call_tool('cms_search_providers', params)


__all__ = ['cms_search_providers']
