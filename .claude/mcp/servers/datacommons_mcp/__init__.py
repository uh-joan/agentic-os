"""Data Commons MCP Server - Python API

Provides Python functions for Data Commons statistical and demographic data.
Data stays in execution environment - only summaries flow to model.

CRITICAL DATA COMMONS QUIRKS:
1. Two-step workflow: search_indicators → get_observations (MANDATORY) - validated in testing
2. Place names: ALWAYS qualify ("California, USA" not "California")
3. Variable DCIDs: Use exact DCIDs from search_indicators (don't guess)
4. Date format: "latest", "all", "YYYY", "YYYY-MM", "YYYY-MM-DD", or "range"
5. Place DCIDs: Returned as geo IDs (e.g., "geoId/06" for California)
6. Bilateral data: Variable may encode one place, use other in place_dcid
7. TOKEN USAGE (measured): search_indicators ~300 tokens, get_observations ~500 tokens
8. Total workflow: ~800 tokens for complete two-step query (validated)
9. Response format: Clean JSON, well-structured, easy to parse
10. Metadata rich: Includes source, measurement method, year
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List, Union


def _call_with_retry(tool_name: str, params: dict, max_retries: int = 2) -> Dict[str, Any]:
    """Call Data Commons MCP with retry logic for subprocess issues.

    Args:
        tool_name: MCP tool name
        params: Tool parameters
        max_retries: Maximum retry attempts (default: 2)

    Returns:
        Tool result dict
    """
    import time
    from mcp import client as mcp_client

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            client = mcp_client.get_client('datacommons-mcp')
            result = client.call_tool(tool_name, params)
            return result
        except BrokenPipeError as e:
            last_error = e
            if attempt < max_retries:
                # Close broken client and clear from registry
                if 'datacommons-mcp' in mcp_client._clients:
                    try:
                        mcp_client._clients['datacommons-mcp'].close()
                    except:
                        pass
                    del mcp_client._clients['datacommons-mcp']

                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                print(f"    [DC RETRY] BrokenPipeError on attempt {attempt + 1}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"    [DC RETRY] Max retries ({max_retries}) exceeded")
                raise last_error
        except Exception as e:
            # Other exceptions are not retryable
            raise

    raise last_error


def search_indicators(
    query: str,
    places: Optional[List[str]] = None,
    parent_place: Optional[str] = None,
    per_search_limit: int = 10,
    include_topics: bool = True,
    maybe_bilateral: bool = False
) -> Dict[str, Any]:
    """
    Search for statistical variables (indicators) and topics in Data Commons

    CRITICAL: This is STEP 1 - Always use this before get_observations!
    Results are CANDIDATES - filter and rank based on user context.

    Args:
        query: Search query for indicators
              Examples: "diabetes prevalence", "population", "GDP", "carbon emissions"

              RULES:
              - Search ONE concept at a time for focused results
              - ❌ WRONG: "health and unemployment rate"
              - ✅ CORRECT: "health" OR "unemployment rate" as separate searches

        places: List of human-readable place names (optional)
               CRITICAL: ALWAYS qualify place names with geography

               Examples:
               - ✅ CORRECT: ["California, USA"], ["Paris, France"], ["New York City, USA"]
               - ❌ WRONG: ["California"], ["Paris"], ["New York"]

               Common ambiguous cases:
               - "New York" → "New York City, USA" vs "New York State, USA"
               - "Madrid" → "Madrid, Spain" vs "Community of Madrid, Spain"
               - "London" → "London, UK" vs "London, Ontario, Canada"

               ❌ NEVER use DCIDs here (e.g., "geoId/06", "country/CAN")
               ✅ ALWAYS use readable names with context

        parent_place: Parent place for child sampling (optional)
                     Use ONLY when searching for indicators about child places

                     Example workflows:
                     - States in India: parent_place="India", places=[sample of states]
                     - Countries: parent_place="World", places=[sample of countries]
                     - Cities in USA: parent_place="USA", places=[sample of cities]

        per_search_limit: Maximum results per search (1-100, default: 10)
                         ⚠️  ONLY set when explicitly requested by user

        include_topics: Include topic hierarchy (default: True)

                       Use True for:
                       - Exploration and discovery
                       - Understanding data organization
                       - Finding related variables

                       Use False for:
                       - Specific data fetching
                       - Getting exact variable for observations

        maybe_bilateral: Set True for bilateral relationships (default: False)

                        Use True for:
                        - Trade, migration, exports between places
                        - "exports to France"
                        - Multi-place relationships

                        Use False for:
                        - Properties of a place (population, GDP)
                        - "unemployment rate"
                        - "carbon emissions in NYC"

    Returns:
        dict: Search results with candidate indicators

        Response structure:
        {
            "topics": [
                {
                    "dcid": "dc/t/TopicDcid",
                    "member_topics": ["dc/t/SubTopic1", ...],
                    "member_variables": ["dc/v/Variable1", ...],
                    "places_with_data": ["geoId/06", ...]
                }
            ],
            "variables": [
                {
                    "dcid": "dc/v/VariableDcid",
                    "places_with_data": ["geoId/06", "country/CAN", ...]
                }
            ],
            "dcid_name_mappings": {
                "dc/v/VariableDcid": "Readable Variable Name",
                "geoId/06": "California"
            },
            "dcid_place_type_mappings": {
                "geoId/06": ["State"],
                "country/CAN": ["Country"]
            },
            "resolved_parent_place": {...}  // If parent_place provided
        }

    Examples:
        # Example 1: Basic search for prevalence data
        results = search_indicators(
            query="diabetes prevalence",
            places=["United States"]
        )

        # Extract variable DCIDs
        for var in results.get('variables', []):
            dcid = var['dcid']
            name = results['dcid_name_mappings'].get(dcid)
            places = var.get('places_with_data', [])
            print(f"{name} ({dcid})")
            print(f"  Available in {len(places)} places")

        # Example 2: Child place sampling (states in India)
        results = search_indicators(
            query="population",
            parent_place="India",
            places=[
                "Uttar Pradesh, India",
                "Maharashtra, India",
                "Tripura, India",
                "Bihar, India",
                "Kerala, India"
            ]
        )

        # Example 3: Child place sampling (countries globally)
        results = search_indicators(
            query="GDP",
            parent_place="World",
            places=[
                "USA",
                "China",
                "Germany",
                "Nigeria",
                "Brazil"
            ]
        )

        # Example 4: Bilateral data search
        results = search_indicators(
            query="trade exports",
            places=["France"],
            maybe_bilateral=True
        )

        # Example 5: Multi-place bilateral
        results = search_indicators(
            query="trade exports",
            places=["USA", "Germany", "France"],
            maybe_bilateral=True
        )

        # Example 6: No place filtering
        results = search_indicators(query="trade")

        # Example 7: Exploration mode (include topics)
        results = search_indicators(
            query="health",
            places=["World"],
            include_topics=True
        )

        # Example 8: Data fetching mode (variables only)
        results = search_indicators(
            query="unemployment rate",
            places=["United States"],
            include_topics=False
        )
    """
    params = {
        'query': query,
        'per_search_limit': per_search_limit,
        'include_topics': include_topics,
        'maybe_bilateral': maybe_bilateral
    }

    if places:
        params['places'] = places
    if parent_place:
        params['parent_place'] = parent_place

    return _call_with_retry('search_indicators', params)


def get_observations(
    variable_dcid: str,
    place_dcid: str,
    child_place_type: Optional[str] = None,
    source_override: Optional[str] = None,
    date: str = "latest",
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch observations for a statistical variable

    CRITICAL: This is STEP 2 - Use after search_indicators!
    ⚠️  ALWAYS validate variable-place combinations with search_indicators first!

    Args:
        variable_dcid: Variable DCID from search_indicators
                      Format: "dc/v/VariableName" or similar
                      ❌ NEVER guess - must come from search_indicators

        place_dcid: Place DCID
                   Format: "geoId/06" (California), "country/USA", etc.
                   Get from search_indicators response

                   ⚠️  BILATERAL DATA NOTE:
                   For bilateral variables (e.g., "TradeExports_FRA"),
                   the variable encodes one place (France).
                   Use the OTHER place in place_dcid (e.g., "country/USA" for exports FROM USA)

        child_place_type: Get data for all children of this type (optional)

                         CRITICAL: MUST validate with search_indicators first!

                         Child type determination logic:
                         1. Use search_indicators with child sampling
                         2. Check dcid_place_type_mappings for sampled children
                         3. Use type common to ALL sampled children
                         4. If multiple common types, use most specific
                         5. If no common type and no majority (50%+), don't use child mode

                         Examples:
                         - "County" - All counties in a state
                         - "Country" - All countries globally
                         - "City" - All cities in a country

        source_override: Force specific data source (optional)

        date: Date filter (required, default: "latest")
             Values:
             - "latest" - Most recent observation (DEFAULT)
             - "all" - All available dates
             - "range" - Use date_range_start/end
             - "YYYY" - Specific year (e.g., "2020")
             - "YYYY-MM" - Specific month (e.g., "2020-06")
             - "YYYY-MM-DD" - Specific date (e.g., "2020-06-15")

             ⚠️  DATA VOLUME CONSTRAINT:
             When using child_place_type, MUST be conservative:
             - ❌ DON'T use date="all" with child_place_type
             - ✅ DO use date="latest" or specific date range

        date_range_start: Start date for range (YYYY, YYYY-MM, or YYYY-MM-DD)
                         Only if date="range"

        date_range_end: End date for range (YYYY, YYYY-MM, or YYYY-MM-DD)
                       Only if date="range"

    Returns:
        dict: Observation data

        Response structure:
        {
            "variable": {
                "dcid": "...",
                "name": "..."
            },
            "place_observations": [
                {
                    "place": {
                        "dcid": "geoId/06",
                        "name": "California",
                        "type": "State"
                    },
                    "time_series": [
                        ("2022-01-01", 39538223.0),
                        ("2021-01-01", 39237836.0),
                        ...
                    ]
                }
            ],
            "source_metadata": {...},
            "alternative_sources": [...]
        }

    Examples:
        # Example 1: Latest data for single place
        obs = get_observations(
            variable_dcid="Count_Person",
            place_dcid="geoId/06",  # California
            date="latest"
        )

        # Extract latest value
        for place_obs in obs.get('place_observations', []):
            place_name = place_obs['place']['name']
            time_series = place_obs.get('time_series', [])
            if time_series:
                latest_date, latest_value = time_series[0]
                print(f"{place_name}: {latest_value:,.0f} ({latest_date})")

        # Example 2: All counties in California
        # FIRST: Validate with search_indicators!
        obs = get_observations(
            variable_dcid="Count_Person",
            place_dcid="geoId/06",
            child_place_type="County",
            date="latest"  # ✅ CORRECT: latest with children
        )

        # Process all counties
        for place_obs in obs.get('place_observations', []):
            county_name = place_obs['place']['name']
            time_series = place_obs.get('time_series', [])
            if time_series:
                date, value = time_series[0]
                print(f"{county_name}: {value:,.0f}")

        # Example 3: Date range for single place
        obs = get_observations(
            variable_dcid="Count_Person",
            place_dcid="geoId/06",
            date="range",
            date_range_start="2010",
            date_range_end="2020"
        )

        # Plot time series
        for place_obs in obs.get('place_observations', []):
            time_series = place_obs.get('time_series', [])
            for date, value in time_series:
                print(f"{date}: {value:,.0f}")

        # Example 4: Specific year
        obs = get_observations(
            variable_dcid="Count_Person",
            place_dcid="country/USA",
            date="2020"
        )

        # Example 5: All countries globally (latest only)
        obs = get_observations(
            variable_dcid="Count_Person",
            place_dcid="Earth",
            child_place_type="Country",
            date="latest"  # ✅ CRITICAL: Use latest, not all!
        )

        # Example 6: Bilateral data (exports FROM USA TO France)
        # Variable: TradeExports_FRA (exports TO France)
        # place_dcid: country/USA (exports FROM USA)
        obs = get_observations(
            variable_dcid="TradeExports_FRA",
            place_dcid="country/USA",
            date="latest"
        )
    """
    params = {
        'variable_dcid': variable_dcid,
        'place_dcid': place_dcid,
        'date': date
    }

    if child_place_type:
        params['child_place_type'] = child_place_type
    if source_override:
        params['source_override'] = source_override
    if date_range_start:
        params['date_range_start'] = date_range_start
    if date_range_end:
        params['date_range_end'] = date_range_end

    return _call_with_retry('get_observations', params)


__all__ = ['search_indicators', 'get_observations']
