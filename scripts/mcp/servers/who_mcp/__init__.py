"""WHO Global Health Observatory MCP Server - Python API

Provides Python functions for WHO Global Health Observatory (GHO) data via OData API.
Data stays in execution environment - only summaries flow to model.

CRITICAL WHO GHO QUIRKS:
1. OData protocol: Standard OData filter syntax (eq, ne, ge, le, and, or)
2. Indicator codes: Use exact WHO codes (e.g., "WHOSIS_000001" for life expectancy)
3. Country codes: ISO 3-letter codes (USA, GBR, CHN)
4. Region codes: WHO regions (AFR, AMR, SEAR, EUR, EMR, WPR)
5. Time filtering: TimeDim field for years, date() function for ranges
6. Disaggregation: Dim1 for sex (MLE, FMLE, BTSX), check for null
7. Response format: OData JSON with value arrays
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def get_dimensions() -> Dict[str, Any]:
    """
    List all available data dimensions in WHO database

    Returns all dimension types (COUNTRY, REGION, YEAR, SEX, etc.)
    used for structuring health data.

    Returns:
        dict: Available data dimensions

        Response structure:
        {
            "dimensions": [
                {
                    "code": "COUNTRY",
                    "label": "Country"
                },
                {
                    "code": "REGION",
                    "label": "WHO Region"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Get all dimensions
        dims = get_dimensions()

        for dim in dims.get('dimensions', []):
            code = dim.get('code')
            label = dim.get('label')
            print(f"{code}: {label}")

        # Example 2: Check available dimensions before querying
        dims = get_dimensions()
        dim_codes = [d.get('code') for d in dims.get('dimensions', [])]

        if 'COUNTRY' in dim_codes:
            print("Country dimension available")
        if 'YEAR' in dim_codes:
            print("Time dimension available")
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'get_dimensions'
    }

    return client.call_tool('who-health', params)


def get_dimension_codes(
    dimension_code: str
) -> Dict[str, Any]:
    """
    Get codes for a specific dimension (countries, regions, years, etc.)

    Args:
        dimension_code: Dimension to retrieve
                       Common values:
                       - "COUNTRY" - ISO country codes
                       - "REGION" - WHO region codes
                       - "YEAR" - Available years
                       - "SEX" - Sex disaggregation codes

    Returns:
        dict: Dimension codes and labels

        Response structure:
        {
            "dimension": "COUNTRY",
            "codes": [
                {
                    "code": "USA",
                    "label": "United States of America"
                },
                {
                    "code": "GBR",
                    "label": "United Kingdom"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Get all country codes
        countries = get_dimension_codes(dimension_code="COUNTRY")

        for country in countries.get('codes', []):
            code = country.get('code')
            label = country.get('label')
            print(f"{code}: {label}")

        # Example 2: Get WHO regions
        regions = get_dimension_codes(dimension_code="REGION")

        for region in regions.get('codes', []):
            code = region.get('code')
            label = region.get('label')
            print(f"{code}: {label}")

        # WHO Regions:
        # AFR - African Region
        # AMR - Region of the Americas
        # SEAR - South-East Asia Region
        # EUR - European Region
        # EMR - Eastern Mediterranean Region
        # WPR - Western Pacific Region

        # Example 3: Get available years
        years = get_dimension_codes(dimension_code="YEAR")

        year_list = [y.get('code') for y in years.get('codes', [])]
        print(f"Data available for years: {min(year_list)} - {max(year_list)}")

        # Example 4: Get sex disaggregation codes
        sex_codes = get_dimension_codes(dimension_code="SEX")

        # Common codes:
        # MLE - Male
        # FMLE - Female
        # BTSX - Both sexes
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'get_dimension_codes',
        'dimension_code': dimension_code
    }

    return client.call_tool('who-health', params)


def search_indicators(
    keywords: str
) -> Dict[str, Any]:
    """
    Find health indicators using keywords and natural language queries

    Search WHO's health indicator catalog with keywords related to
    diseases, health conditions, risk factors, health systems, etc.

    Args:
        keywords: Search terms for health indicators
                 Examples:
                 - Disease burden: "life expectancy", "maternal mortality", "HIV"
                 - Risk factors: "tobacco", "obesity", "air pollution"
                 - Health systems: "health expenditure", "hospital beds"
                 - Child health: "infant mortality", "vaccination"

    Returns:
        dict: Matching health indicators with codes

        Response structure:
        {
            "indicators": [
                {
                    "IndicatorCode": "WHOSIS_000001",
                    "IndicatorName": "Life expectancy at birth (years)",
                    "Language": "en"
                },
                {
                    "IndicatorCode": "MDG_0000000001",
                    "IndicatorName": "Maternal mortality ratio",
                    "Language": "en"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for life expectancy indicators
        results = search_indicators(keywords="life expectancy")

        for indicator in results.get('indicators', []):
            code = indicator.get('IndicatorCode')
            name = indicator.get('IndicatorName')
            print(f"{code}: {name}")

        # Example 2: Search for maternal health
        results = search_indicators(keywords="maternal mortality")

        # Extract codes for further queries
        indicator_codes = [i.get('IndicatorCode') for i in results.get('indicators', [])]
        print(f"Found {len(indicator_codes)} maternal health indicators")

        # Example 3: Search for health expenditure
        results = search_indicators(keywords="health expenditure")

        for indicator in results.get('indicators', []):
            code = indicator.get('IndicatorCode')
            name = indicator.get('IndicatorName')
            if 'capita' in name.lower():
                print(f"Per capita indicator: {code} - {name}")

        # Example 4: Multi-keyword search
        results = search_indicators(keywords="tobacco smoking prevalence")

        # Example 5: Search for vaccination coverage
        results = search_indicators(keywords="vaccination coverage")

        for indicator in results.get('indicators', []):
            name = indicator.get('IndicatorName')
            if 'BCG' in name or 'DTP' in name or 'measles' in name.lower():
                code = indicator.get('IndicatorCode')
                print(f"{code}: {name}")
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'search_indicators',
        'keywords': keywords
    }

    return client.call_tool('who-health', params)


def get_health_data(
    indicator_code: str,
    top: Optional[int] = None,
    filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve comprehensive health indicator data with OData filtering

    Get raw health data with full OData query capabilities for
    advanced filtering, sorting, and data selection.

    Args:
        indicator_code: WHO health indicator code
                       Common codes:
                       - WHOSIS_000001 - Life expectancy at birth
                       - MDG_0000000001 - Maternal mortality ratio
                       - GHED_CHE_pc_PPP_INT - Health expenditure per capita
                       - M_Est_smk_curr_std - Smoking prevalence
                       - SA_0000001688 - Suicide mortality rate

        top: Maximum number of records to return (optional)
            Use to limit large datasets

        filter: OData filter expression for advanced filtering

               BASIC FILTERING:
               - Country: "SpatialDim eq 'USA'"
               - Year: "TimeDim eq 2020"
               - Combined: "SpatialDim eq 'USA' and TimeDim eq 2020"

               TIME RANGE FILTERING:
               - Range: "TimeDim ge 2015 and TimeDim le 2020"
               - Greater than: "TimeDim ge 2010"
               - Less than: "TimeDim le 2023"

               SEX DISAGGREGATION:
               - Male: "Dim1 eq 'MLE'"
               - Female: "Dim1 eq 'FMLE'"
               - Both sexes: "Dim1 eq 'BTSX'"

               DATE FUNCTIONS:
               - Date range: "date(TimeDimensionBegin) ge 2011-01-01 and date(TimeDimensionBegin) lt 2012-01-01"

               NULL CHECKS:
               - Has data: "Dim1 ne null"
               - No disaggregation: "Dim1 eq null"

    Returns:
        dict: Health data records

        Response structure:
        {
            "value": [
                {
                    "IndicatorCode": "WHOSIS_000001",
                    "SpatialDim": "USA",
                    "TimeDim": 2020,
                    "Dim1": "BTSX",
                    "NumericValue": 78.93,
                    "Low": 78.5,
                    "High": 79.3
                },
                ...
            ]
        }

    Examples:
        # Example 1: Get all life expectancy data (latest)
        data = get_health_data(
            indicator_code="WHOSIS_000001",
            top=100
        )

        for record in data.get('value', []):
            country = record.get('SpatialDim')
            year = record.get('TimeDim')
            value = record.get('NumericValue')
            print(f"{country} ({year}): {value} years")

        # Example 2: US data for 2020 only
        data = get_health_data(
            indicator_code="WHOSIS_000001",
            filter="SpatialDim eq 'USA' and TimeDim eq 2020"
        )

        # Example 3: Time range analysis
        data = get_health_data(
            indicator_code="WHOSIS_000001",
            filter="SpatialDim eq 'USA' and TimeDim ge 2010 and TimeDim le 2020"
        )

        # Build time series
        time_series = []
        for record in data.get('value', []):
            year = record.get('TimeDim')
            value = record.get('NumericValue')
            if year and value:
                time_series.append((year, value))

        time_series.sort()
        print("US Life Expectancy Trend:")
        for year, value in time_series:
            print(f"  {year}: {value:.2f} years")

        # Example 4: Sex-disaggregated data
        data = get_health_data(
            indicator_code="WHOSIS_000001",
            filter="SpatialDim eq 'USA' and TimeDim eq 2020 and Dim1 ne null"
        )

        for record in data.get('value', []):
            sex = record.get('Dim1')
            value = record.get('NumericValue')
            sex_label = {'MLE': 'Male', 'FMLE': 'Female', 'BTSX': 'Both'}.get(sex, sex)
            print(f"{sex_label}: {value:.2f} years")

        # Example 5: Multiple countries comparison
        data = get_health_data(
            indicator_code="GHED_CHE_pc_PPP_INT",
            filter="TimeDim eq 2019",
            top=200
        )

        # Rank by health expenditure
        countries = []
        for record in data.get('value', []):
            country = record.get('SpatialDim')
            value = record.get('NumericValue')
            if value:
                countries.append((country, value))

        countries.sort(key=lambda x: x[1], reverse=True)
        print("Top 10 Health Expenditure per Capita (2019):")
        for country, value in countries[:10]:
            print(f"  {country}: ${value:.0f}")
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'get_health_data',
        'indicator_code': indicator_code
    }

    if top:
        params['top'] = top
    if filter:
        params['filter'] = filter

    return client.call_tool('who-health', params)


def get_country_data(
    indicator_code: str,
    country_code: Optional[str] = None,
    region_code: Optional[str] = None,
    year: Optional[str] = None,
    sex: Optional[str] = None,
    top: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve health data for specific countries, regions, or time periods

    Simplified interface for common country/region queries without
    needing to write OData filter expressions.

    Args:
        indicator_code: WHO health indicator code (required)

        country_code: ISO 3-letter country code (optional)
                     Examples: "USA", "GBR", "CHN", "BRA", "IND"

        region_code: WHO region code (optional)
                    Values:
                    - "EUR" - European Region
                    - "AMR" - Region of the Americas
                    - "AFR" - African Region
                    - "EMR" - Eastern Mediterranean Region
                    - "SEAR" - South-East Asia Region
                    - "WPR" - Western Pacific Region

        year: Specific year or year range (optional)
             Formats:
             - "2020" - Single year
             - "2015:2020" - Year range

        sex: Sex dimension filter (optional)
            Values: "MLE", "FMLE", "BTSX"

        top: Maximum number of records (optional)

    Returns:
        dict: Country-specific health data

    Examples:
        # Example 1: Get US life expectancy for 2020
        data = get_country_data(
            indicator_code="WHOSIS_000001",
            country_code="USA",
            year="2020"
        )

        for record in data.get('value', []):
            value = record.get('NumericValue')
            print(f"US Life Expectancy (2020): {value} years")

        # Example 2: Time trend for specific country
        data = get_country_data(
            indicator_code="WHOSIS_000001",
            country_code="USA",
            year="2010:2020"
        )

        # Extract time series
        years = []
        values = []
        for record in data.get('value', []):
            year = record.get('TimeDim')
            value = record.get('NumericValue')
            if year and value:
                years.append(year)
                values.append(value)

        # Calculate trend
        if len(values) >= 2:
            change = values[-1] - values[0]
            print(f"Life expectancy change (2010-2020): {change:+.2f} years")

        # Example 3: Regional data (all countries in Europe)
        data = get_country_data(
            indicator_code="WHOSIS_000001",
            region_code="EUR",
            year="2020",
            top=100
        )

        # Analyze regional distribution
        values = [r.get('NumericValue') for r in data.get('value', []) if r.get('NumericValue')]
        if values:
            avg = sum(values) / len(values)
            print(f"European Region Average: {avg:.2f} years")
            print(f"Range: {min(values):.2f} - {max(values):.2f} years")

        # Example 4: Sex-disaggregated data
        male_data = get_country_data(
            indicator_code="WHOSIS_000001",
            country_code="USA",
            year="2020",
            sex="MLE"
        )

        female_data = get_country_data(
            indicator_code="WHOSIS_000001",
            country_code="USA",
            year="2020",
            sex="FMLE"
        )

        male_value = male_data.get('value', [{}])[0].get('NumericValue')
        female_value = female_data.get('value', [{}])[0].get('NumericValue')

        if male_value and female_value:
            gap = female_value - male_value
            print(f"Male: {male_value:.2f} years")
            print(f"Female: {female_value:.2f} years")
            print(f"Gender gap: {gap:.2f} years")

        # Example 5: Compare multiple countries
        countries = ["USA", "GBR", "JPN", "DEU", "FRA"]

        for country in countries:
            data = get_country_data(
                indicator_code="GHED_CHE_pc_PPP_INT",
                country_code=country,
                year="2019"
            )

            if data.get('value'):
                value = data['value'][0].get('NumericValue')
                print(f"{country}: ${value:.0f} per capita")
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'get_country_data',
        'indicator_code': indicator_code
    }

    if country_code:
        params['country_code'] = country_code
    if region_code:
        params['region_code'] = region_code
    if year:
        params['year'] = year
    if sex:
        params['sex'] = sex
    if top:
        params['top'] = top

    return client.call_tool('who-health', params)


def get_cross_table(
    indicator_code: str,
    countries: Optional[str] = None,
    years: Optional[str] = None,
    sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate tabular views of health data across countries and time periods

    Creates structured tables for easy comparison of health data
    across multiple countries and years.

    Args:
        indicator_code: WHO health indicator code (required)

        countries: Comma-separated list of country codes (optional)
                  Examples:
                  - "USA,GBR,CHN"
                  - "DEU,FRA,ITA"

        years: Year range (YYYY:YYYY) or specific year (YYYY) (optional)
              Examples:
              - "2015:2020" - Range
              - "2019" - Single year

        sex: Sex dimension filter (optional)
            Values: "MLE", "FMLE", "BTSX"

    Returns:
        dict: Tabular health data structure

        Response structure:
        {
            "rows": [
                {
                    "country": "USA",
                    "2015": 78.69,
                    "2016": 78.69,
                    "2017": 78.54,
                    "2018": 78.69,
                    "2019": 78.79,
                    "2020": 77.28
                },
                ...
            ]
        }

    Examples:
        # Example 1: Compare G7 countries
        table = get_cross_table(
            indicator_code="WHOSIS_000001",
            countries="USA,GBR,JPN,DEU,FRA,ITA,CAN",
            years="2015:2020"
        )

        # Display as table
        print("Life Expectancy Comparison (2015-2020)")
        print("-" * 60)

        for row in table.get('rows', []):
            country = row.get('country')
            print(f"{country:5s}", end="  ")
            for year in range(2015, 2021):
                value = row.get(str(year))
                if value:
                    print(f"{value:5.2f}", end="  ")
                else:
                    print("  N/A", end="  ")
            print()

        # Example 2: BRICS countries health expenditure
        table = get_cross_table(
            indicator_code="GHED_CHE_pc_PPP_INT",
            countries="BRA,RUS,IND,CHN,ZAF",
            years="2010:2020"
        )

        # Calculate growth rates
        for row in table.get('rows', []):
            country = row.get('country')
            start = row.get('2010')
            end = row.get('2020')

            if start and end:
                growth = ((end - start) / start) * 100
                print(f"{country}: {growth:+.1f}% growth (${start:.0f} → ${end:.0f})")

        # Example 3: Single year cross-country comparison
        table = get_cross_table(
            indicator_code="WHOSIS_000001",
            countries="USA,MEX,CAN",
            years="2020"
        )

        # Rank by value
        rankings = []
        for row in table.get('rows', []):
            country = row.get('country')
            value = row.get('2020')
            if value:
                rankings.append((country, value))

        rankings.sort(key=lambda x: x[1], reverse=True)
        print("North American Rankings (2020):")
        for rank, (country, value) in enumerate(rankings, 1):
            print(f"  {rank}. {country}: {value:.2f} years")

        # Example 4: Time series analysis
        table = get_cross_table(
            indicator_code="MDG_0000000001",
            countries="USA,GBR",
            years="2000:2020"
        )

        for row in table.get('rows', []):
            country = row.get('country')
            values = []

            for year in range(2000, 2021):
                value = row.get(str(year))
                if value:
                    values.append(value)

            if len(values) >= 2:
                reduction = ((values[0] - values[-1]) / values[0]) * 100
                print(f"{country}: {reduction:.1f}% reduction in maternal mortality")

        # Example 5: Gender comparison
        male_table = get_cross_table(
            indicator_code="WHOSIS_000001",
            countries="USA,JPN,AUS",
            years="2020",
            sex="MLE"
        )

        female_table = get_cross_table(
            indicator_code="WHOSIS_000001",
            countries="USA,JPN,AUS",
            years="2020",
            sex="FMLE"
        )

        print("Gender Gap Analysis (2020):")
        for m_row, f_row in zip(male_table.get('rows', []), female_table.get('rows', [])):
            country = m_row.get('country')
            male_val = m_row.get('2020')
            female_val = f_row.get('2020')

            if male_val and female_val:
                gap = female_val - male_val
                print(f"{country}: {gap:+.2f} year gap (M: {male_val:.2f}, F: {female_val:.2f})")
    """
    client = get_client('who-mcp-server')

    params = {
        'method': 'get_cross_table',
        'indicator_code': indicator_code
    }

    if countries:
        params['countries'] = countries
    if years:
        params['years'] = years
    if sex:
        params['sex'] = sex

    return client.call_tool('who-health', params)


__all__ = [
    'get_dimensions',
    'get_dimension_codes',
    'search_indicators',
    'get_health_data',
    'get_country_data',
    'get_cross_table'
]
