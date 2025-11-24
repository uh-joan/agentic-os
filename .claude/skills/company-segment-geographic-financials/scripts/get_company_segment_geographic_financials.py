import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_cik, get_company_submissions
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import time

def get_company_segment_geographic_financials(ticker, quarters=8):
    """Extract comprehensive segment & geographic financials for ANY company.

    Uses SEC EDGAR XBRL dimensional analysis to extract:
    - Segment revenue (by business unit/product line)
    - Geographic revenue (by region/country)
    - Revenue reconciliation (segment total vs consolidated)

    Args:
        ticker (str): Stock ticker symbol (e.g., "JNJ", "PFE", "ABT")
        quarters (int, optional): Number of quarters to analyze (default: 8)

    Returns:
        dict: {
            'company': str,
            'ticker': str,
            'cik': str,
            'quarters_analyzed': int,
            'segment_revenue': dict,
            'geographic_revenue': dict,
            'reconciliation': dict,
            'summary': str
        }
    """

    print("="*80)
    print(f"EXTRACTING SEGMENT & GEOGRAPHIC FINANCIALS: {ticker}")
    print("="*80)

    # Step 1: Get CIK
    print(f"\nStep 1: Looking up CIK for {ticker}...")
    cik_result = get_company_cik(ticker=ticker.upper())

    if 'error' in cik_result or not cik_result.get('cik'):
        return {
            'error': f'Could not find CIK for ticker {ticker}',
            'ticker': ticker
        }

    cik = cik_result['cik']
    company_name = cik_result.get('name', ticker)
    print(f"✓ Found: {company_name} (CIK: {cik})")

    # Step 2: Get recent 10-Q, 10-K, and 20-F filings
    print(f"\nStep 2: Fetching recent filings for {company_name}...")
    submissions = get_company_submissions(cik_or_ticker=cik)

    if 'error' in submissions:
        return {
            'error': f'Could not get submissions for {ticker}',
            'company': company_name,
            'ticker': ticker,
            'cik': cik
        }

    # Get recent filings (10-Q, 10-K, and 20-F for international companies)
    recent_filings = submissions.get('recentFilings', [])

    # Filter for quarterly and annual reports (including foreign company annual reports)
    target_filings = []
    for filing in recent_filings:
        form = filing.get('form')
        if form in ['10-Q', '10-K', '20-F'] and len(target_filings) < quarters:
            target_filings.append({
                'form': form,
                'accession': filing.get('accessionNumber', '').replace('-', ''),
                'filing_date': filing.get('filingDate', ''),
                'primary_doc': filing.get('primaryDocument', '')
            })

    if not target_filings:
        return {
            'error': 'No 10-Q, 10-K, or 20-F filings found',
            'company': company_name,
            'ticker': ticker,
            'cik': cik
        }

    print(f"✓ Found {len(target_filings)} recent filings")

    # Step 3: Download and parse XBRL files
    print(f"\nStep 3: Parsing XBRL dimensional data from {len(target_filings)} filings...")

    all_segment_data = defaultdict(lambda: defaultdict(float))
    all_geography_data = defaultdict(lambda: defaultdict(float))
    consolidated_revenue_data = []  # For reconciliation

    revenue_concepts = [
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'Revenues',
        'SalesRevenueNet',
        'Revenue',
        'RevenueFromContractWithCustomerIncludingAssessedTax'
    ]

    dimensional_facts_count = 0

    for filing in target_filings:
        # Construct XBRL instance document URL
        cik_padded = cik.zfill(10)
        accession = filing['accession']
        primary_doc = filing['primary_doc']

        # Find the XML instance document (usually ends with .xml or .htm)
        if primary_doc.endswith('.htm'):
            xml_filename = primary_doc.replace('.htm', '_htm.xml')
        else:
            xml_filename = primary_doc

        url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession}/{xml_filename}"

        print(f"  Downloading {filing['form']} from {filing['filing_date']}...")

        try:
            # SEC requires User-Agent with email
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Research/Analysis pharma-research@example.com'
            })

            # Rate limiting: SEC allows max 10 req/sec
            time.sleep(0.17)  # ~6 req/sec to be safe

            with urllib.request.urlopen(req) as response:
                xml_content = response.read()

            xml_root = ET.fromstring(xml_content)

            # Parse contexts to extract dimensional information
            contexts = parse_xbrl_contexts(xml_root)

            # Extract revenue facts with dimensions
            filing_facts = extract_dimensional_revenue(
                xml_root, contexts, revenue_concepts, filing['form']
            )

            # Defensive: ensure filing_facts is a list
            if filing_facts is None:
                print(f"    Warning: extract_dimensional_revenue returned None for {filing['form']}")
                filing_facts = []

            dimensional_facts_count += len(filing_facts)

            # Organize by segment and geography
            for fact in filing_facts:
                segment = fact['segment']
                geography = fact['geography']
                period = fact['end_date']
                value = fact['value']
                dimension_axis = fact.get('segment_axis', '')

                # Track consolidated revenue (no dimensions)
                if not segment and not geography:
                    consolidated_revenue_data.append(fact)

                # Track segment revenue (with dimension axis for hierarchy detection)
                if segment:
                    segment_key = f"{segment}|{dimension_axis}"
                    # Use max to handle duplicate/YTD facts
                    all_segment_data[segment_key][period] = max(
                        all_segment_data[segment_key][period], value
                    )

                # Track geography revenue (with dimension axis)
                if geography:
                    geography_axis = fact.get('geography_axis', '')
                    geography_key = f"{geography}|{geography_axis}"
                    all_geography_data[geography_key][period] = max(
                        all_geography_data[geography_key][period], value
                    )

        except Exception as e:
            print(f"    Warning: Could not parse {filing['form']}: {e}")
            continue

    print(f"✓ Processed {dimensional_facts_count} dimensional facts")

    # Step 4: Calculate reconciliation and identify correct segment axis
    print(f"\nStep 3: Identifying primary segment axis and calculating reconciliation...")
    print("-"*80)

    # Get latest period
    all_periods = set()
    for segment_periods in all_segment_data.values():
        all_periods.update(segment_periods.keys())
    for geo_periods in all_geography_data.values():
        all_periods.update(geo_periods.keys())

    latest_period = max(all_periods) if all_periods else None

    # Get consolidated revenue for latest period
    consolidated_total = 0
    if consolidated_revenue_data and latest_period:
        # Sort by date and get most recent
        consolidated_revenue_data.sort(key=lambda x: x['end_date'], reverse=True)
        for item in consolidated_revenue_data:
            if item['end_date'] == latest_period:
                consolidated_total = max(consolidated_total, item['value'])

    # Group segments by their dimension axis
    segments_by_axis = defaultdict(dict)
    for segment_key, periods in all_segment_data.items():
        if '|' in segment_key:
            segment_name, axis = segment_key.rsplit('|', 1)
        else:
            segment_name, axis = segment_key, ''

        if latest_period in periods:
            if segment_name not in segments_by_axis[axis]:
                segments_by_axis[axis][segment_name] = periods[latest_period]
            else:
                # Take max if duplicate
                segments_by_axis[axis][segment_name] = max(
                    segments_by_axis[axis][segment_name],
                    periods[latest_period]
                )

    # Find which axis to use for segment breakdown
    # Axis priority order (lower number = higher priority)
    axis_priority_map = {
        'StatementBusinessSegmentsAxis': 1,
        'ProductOrServiceAxis': 2,
        'SubsegmentsAxis': 3
    }

    def get_axis_priority(axis):
        """Extract axis priority from full axis name."""
        axis_name = axis.split(':')[-1] if ':' in axis else axis
        return axis_priority_map.get(axis_name, 99)

    # Evaluate all axes and select best one
    # Prefer: 1) >1 segment, 2) highest priority, 3) best variance, 4) most segments
    best_axis = None
    best_priority = 999
    best_variance = float('inf')
    max_segments = 0

    if consolidated_total > 0:
        for axis, segments in segments_by_axis.items():
            # Skip axes with only 1 segment (not useful for breakdown)
            if len(segments) <= 1:
                continue

            axis_total = sum(segments.values())
            variance = abs(consolidated_total - axis_total)
            variance_pct = (variance / consolidated_total * 100) if consolidated_total > 0 else 0
            priority = get_axis_priority(axis)

            # Select based on priority first, then variance, then segment count
            is_better = False
            if priority < best_priority:
                # Higher priority axis
                is_better = True
            elif priority == best_priority:
                # Same priority - prefer better variance
                if variance_pct < best_variance:
                    is_better = True
                elif variance_pct == best_variance and len(segments) > max_segments:
                    # Same priority and variance - prefer more segments
                    is_better = True

            if is_better:
                best_axis = axis
                best_priority = priority
                best_variance = variance_pct
                max_segments = len(segments)

    # Fallback: if no axis has >1 segment, use the one with most segments
    if best_axis is None and segments_by_axis:
        best_axis = max(segments_by_axis.keys(), key=lambda k: len(segments_by_axis[k]))
        best_variance = float('inf')

    # Use the best reconciling axis (or try to find top-level segments)
    if best_axis is not None and best_variance < 5:  # Within 5% is acceptable
        filtered_segments = segments_by_axis[best_axis]
    else:
        # Try to find top-level segments by testing different combinations
        # Get all segments from best axis
        candidate_segments = segments_by_axis.get(best_axis, {})

        # IMPORTANT: Detect and remove rollup segments before greedy algorithm
        # This prevents double-counting hierarchical segments
        candidate_segments = detect_rollup_segments(
            candidate_segments, consolidated_total, tolerance_pct=5
        )

        if consolidated_total > 0 and len(candidate_segments) > 2:
            # Sort segments by revenue (descending)
            sorted_segments = sorted(candidate_segments.items(), key=lambda x: x[1], reverse=True)

            # Strategy: Greedy algorithm to find segments that reconcile
            # Start with largest segment, then add segments that improve reconciliation
            selected_segments = {}
            remaining_segments = list(sorted_segments)

            # Start with the largest segment
            if remaining_segments:
                seg_name, seg_value = remaining_segments[0]
                selected_segments[seg_name] = seg_value
                remaining_segments = remaining_segments[1:]

                current_total = seg_value
                current_variance_pct = abs(consolidated_total - current_total) / consolidated_total * 100

                # Greedy: add segments that reduce the gap to consolidated
                max_iterations = 20
                for _ in range(max_iterations):
                    if current_variance_pct < 1.0 or not remaining_segments:
                        break

                    best_addition = None
                    best_new_variance = current_variance_pct

                    # Try adding each remaining segment
                    for seg_name, seg_value in remaining_segments:
                        new_total = current_total + seg_value
                        new_variance_pct = abs(consolidated_total - new_total) / consolidated_total * 100

                        # Accept if it reduces variance
                        if new_variance_pct < best_new_variance:
                            best_new_variance = new_variance_pct
                            best_addition = (seg_name, seg_value)

                    # If found improvement, add it
                    if best_addition:
                        seg_name, seg_value = best_addition
                        selected_segments[seg_name] = seg_value
                        remaining_segments.remove(best_addition)
                        current_total += seg_value
                        current_variance_pct = best_new_variance
                    else:
                        # No improvement possible
                        break

                best_subset = selected_segments
                best_subset_variance = current_variance_pct
                best_subset_size = len(selected_segments)

            if best_subset is not None and best_subset_variance < 20:  # Reasonable threshold
                filtered_segments = best_subset
            else:
                filtered_segments = candidate_segments
        else:
            # Fallback: use all segments from best axis
            filtered_segments = candidate_segments

    # Calculate segment total for latest period
    segment_total = sum(filtered_segments.values())

    # Step 4b: Filter geographies using similar logic
    geographies_by_axis = defaultdict(dict)
    for geography_key, periods in all_geography_data.items():
        if '|' in geography_key:
            geography_name, axis = geography_key.rsplit('|', 1)
        else:
            geography_name, axis = geography_key, ''

        if latest_period in periods:
            if geography_name not in geographies_by_axis[axis]:
                geographies_by_axis[axis][geography_name] = periods[latest_period]
            else:
                # Take max if duplicate
                geographies_by_axis[axis][geography_name] = max(
                    geographies_by_axis[axis][geography_name],
                    periods[latest_period]
                )

    # For geography, just use the axis with the most geographies
    filtered_geographies = {}
    if geographies_by_axis:
        # Find axis with most geographies
        best_geo_axis = max(geographies_by_axis.keys(), key=lambda k: len(geographies_by_axis[k]))
        filtered_geographies = geographies_by_axis[best_geo_axis]

    # Display reconciliation
    reconciliation = {}
    if latest_period:
        print(f"Latest period: {latest_period}")
        if consolidated_total > 0:
            print(f"Consolidated revenue: ${consolidated_total:,.0f}")
            reconciliation['consolidated_revenue'] = consolidated_total
        print(f"Segment total: ${segment_total:,.0f}")
        reconciliation['segment_total'] = segment_total

        if consolidated_total > 0:
            variance = consolidated_total - segment_total
            variance_pct = (variance / consolidated_total * 100) if consolidated_total > 0 else 0
            print(f"Variance: ${variance:,.0f} ({variance_pct:.2f}%)")
            reconciliation['variance'] = variance
            reconciliation['variance_pct'] = variance_pct

    # Step 5: Format results
    print(f"\nStep 4: Formatting results...")
    print("-"*80)

    # Get unique periods analyzed
    periods_analyzed = sorted(all_periods, reverse=True) if all_periods else []

    # Format segment revenue
    segment_revenue_summary = {}
    if filtered_segments:
        print("\nSegment Revenue Summary:")
        for segment in sorted(filtered_segments.keys()):
            latest_value = filtered_segments[segment]
            segment_revenue_summary[segment] = {
                'latest_period': latest_period,
                'latest_revenue': latest_value
            }
            print(f"  {segment}: ${latest_value:,.0f}")

    # Format geographic revenue
    geographic_revenue_summary = {}
    if filtered_geographies:
        print("\nGeographic Revenue Summary:")
        for geography in sorted(filtered_geographies.keys()):
            latest_value = filtered_geographies[geography]
            geographic_revenue_summary[geography] = {
                'latest_period': latest_period,
                'latest_revenue': latest_value
            }
            print(f"  {geography}: ${latest_value:,.0f}")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nCompany: {company_name} ({ticker})")
    print(f"CIK: {cik}")
    print(f"Latest Period: {latest_period}")
    print(f"\nSegments analyzed: {len(filtered_segments)}")
    print(f"Geographies analyzed: {len(filtered_geographies)}")
    print(f"Quarters analyzed: {len(periods_analyzed)}")
    print(f"XBRL dimensional facts: {dimensional_facts_count}")

    return {
        'company': company_name,
        'ticker': ticker.upper(),
        'cik': cik,
        'latest_period': latest_period,
        'quarters_requested': quarters,
        'quarters_analyzed': len(periods_analyzed),
        'segment_revenue': segment_revenue_summary,
        'geographic_revenue': geographic_revenue_summary,
        'reconciliation': reconciliation,
        'total_segments': len(filtered_segments),
        'total_geographies': len(filtered_geographies),
        'dimensional_facts_count': dimensional_facts_count
    }


def parse_xbrl_contexts(xml_root):
    """Parse XBRL contexts to extract dimensional information.

    Contexts define the dimensional attributes of facts:
    - Segment (business unit, product line)
    - Geography (region, country)
    - Time period (instant or duration)

    Returns:
        dict: context_id -> {
            'start_date': str or None,
            'end_date': str,
            'segment': str or None,
            'geography': str or None
        }
    """
    contexts = {}

    # Find all context elements
    for context in xml_root.findall('.//{http://www.xbrl.org/2003/instance}context'):
        context_id = context.get('id')

        # Extract period information
        period = context.find('{http://www.xbrl.org/2003/instance}period')
        start_date = None
        end_date = None

        if period is not None:
            instant = period.find('{http://www.xbrl.org/2003/instance}instant')
            if instant is not None:
                end_date = instant.text
            else:
                start_elem = period.find('{http://www.xbrl.org/2003/instance}startDate')
                end_elem = period.find('{http://www.xbrl.org/2003/instance}endDate')
                if start_elem is not None:
                    start_date = start_elem.text
                if end_elem is not None:
                    end_date = end_elem.text

        # Extract dimensions (segment, geography, etc.)
        # Collect ALL segments from ALL axes (don't filter at context level)
        segments_by_axis = {}
        geographies_by_axis = {}

        # Preference order for segment axes (prefer top-level over subsegments)
        segment_priority = {
            'StatementBusinessSegmentsAxis': 1,
            'ProductOrServiceAxis': 2,
            'SubsegmentsAxis': 3
        }

        entity = context.find('{http://www.xbrl.org/2003/instance}entity')
        if entity is not None:
            for member in entity.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                dimension_attr = member.get('dimension')
                member_value = member.text

                if not dimension_attr or not member_value:
                    continue

                # Extract namespace and local name
                if ':' in member_value:
                    member_value = member_value.split(':')[1]

                # Get axis name (without namespace)
                axis_name = dimension_attr.split(':')[-1] if ':' in dimension_attr else dimension_attr

                dim_lower = dimension_attr.lower()

                # Classify as segment or geography
                if 'segment' in dim_lower or 'product' in dim_lower or 'business' in dim_lower:
                    normalized = normalize_segment_name(member_value)
                    if normalized:
                        priority = segment_priority.get(axis_name, 99)
                        # Store segment with axis and priority
                        segments_by_axis[dimension_attr] = {
                            'segment': normalized,
                            'priority': priority
                        }

                elif 'geograph' in dim_lower or 'region' in dim_lower or 'country' in dim_lower:
                    normalized = normalize_geography_name(member_value)
                    if normalized:
                        geographies_by_axis[dimension_attr] = normalized

        contexts[context_id] = {
            'start_date': start_date,
            'end_date': end_date,
            'segments_by_axis': segments_by_axis,  # Dict of {axis: {segment, priority}}
            'geographies_by_axis': geographies_by_axis  # Dict of {axis: geography}
        }

    return contexts


def normalize_segment_name(raw_segment):
    """Normalize segment names for consistency."""
    if not raw_segment:
        return None

    # Remove common suffixes
    segment = raw_segment.replace('Member', '').replace('Segment', '')

    # Convert camelCase to readable format
    segment = re.sub(r'([a-z])([A-Z])', r'\1 \2', segment)

    # Remove extra whitespace
    segment = ' '.join(segment.split())

    return segment if segment else None


def detect_rollup_segments(segments_dict, consolidated_revenue, tolerance_pct=5):
    """
    Detect and filter out rollup/aggregate segments that create double-counting.

    A segment is identified as a rollup if:
    1. Its name contains rollup keywords (Total, Gross, Net Product, etc.)
    2. Its value approximately equals the sum of other segments (hierarchical parent)

    Args:
        segments_dict: Dictionary of {segment_name: revenue_value}
        consolidated_revenue: Total consolidated revenue for validation
        tolerance_pct: Tolerance percentage for sum-equals detection

    Returns:
        dict: Filtered segments with rollups removed
    """
    if not segments_dict or len(segments_dict) <= 1:
        return segments_dict

    # Step 1: Identify potential rollups by keyword
    rollup_keywords = ['total', 'reportables', 'gross', 'net product', 'net sales', 'consolidated',
                       'sales revenue', 'all other', 'combined', 'brands', ' other']

    potential_rollups = {}
    potential_components = {}

    for seg_name, value in segments_dict.items():
        seg_lower = seg_name.lower()
        if any(keyword in seg_lower for keyword in rollup_keywords):
            potential_rollups[seg_name] = value
        else:
            potential_components[seg_name] = value

    # Step 2: Simple strategy - if variance with components-only is better, use it
    if potential_components:
        component_sum = sum(potential_components.values())
        component_variance_pct = abs(consolidated_revenue - component_sum) / max(consolidated_revenue, 1) * 100

        original_sum = sum(segments_dict.values())
        original_variance_pct = abs(consolidated_revenue - original_sum) / max(consolidated_revenue, 1) * 100

        # If removing rollups significantly improves variance, use components only
        if component_variance_pct < original_variance_pct * 0.5:  # At least 50% improvement
            return potential_components

    # Fallback: return all segments (no rollups detected)
    return segments_dict


def normalize_geography_name(raw_geography):
    """Normalize geography names for consistency."""
    if not raw_geography:
        return None

    # Remove common suffixes
    geography = raw_geography.replace('Member', '').replace('Countries', '')

    # Convert camelCase to readable format
    geography = re.sub(r'([a-z])([A-Z])', r'\1 \2', geography)

    # Remove extra whitespace
    geography = ' '.join(geography.split())

    return geography if geography else None


def extract_dimensional_revenue(xml_root, contexts, revenue_concepts, form):
    """Extract revenue facts with dimensional context information.

    Args:
        xml_root: XML root element
        contexts: Parsed context dictionary
        revenue_concepts: List of revenue concept names to search for
        form: Filing form type (10-Q, 10-K, or 20-F)

    Returns:
        list: Revenue facts with dimensions
    """
    facts = []

    # Discover us-gaap and ifrs-full namespaces (support both US and international companies)
    namespaces_found = {}
    elem_count = 0
    for elem in xml_root.iter():
        tag = elem.tag
        if '}' in tag:
            ns = tag.split('}')[0].strip('{')
            if 'us-gaap' in ns:
                namespaces_found['us-gaap'] = ns
            elif 'ifrs-full' in ns.lower():
                namespaces_found['ifrs-full'] = ns

        elem_count += 1
        # Stop if we found both namespaces, or checked enough elements (20K should be enough)
        if len(namespaces_found) >= 2 or elem_count > 20000:
            break

    # Must have at least one accounting standard namespace
    if 'us-gaap' not in namespaces_found and 'ifrs-full' not in namespaces_found:
        return facts

    # Search for revenue concepts in both US GAAP and IFRS namespaces
    for concept_name in revenue_concepts:
        # Try US GAAP namespace
        if 'us-gaap' in namespaces_found:
            xpath = f".//{{{namespaces_found['us-gaap']}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                _process_revenue_element(elem, facts, contexts, concept_name, form)

        # Try IFRS namespace
        if 'ifrs-full' in namespaces_found:
            xpath = f".//{{{namespaces_found['ifrs-full']}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                _process_revenue_element(elem, facts, contexts, concept_name, form)

    return facts


def _process_revenue_element(elem, facts, contexts, concept_name, form):
    """Helper function to process a single revenue element."""
    context_ref = elem.get('contextRef')

    if context_ref and elem.text and context_ref in contexts:
        try:
            value = float(elem.text)
            context_info = contexts[context_ref]

            # Only include facts with valid end dates
            if not context_info['end_date']:
                return

            # Extract segments and geographies from all axes
            segments_by_axis = context_info.get('segments_by_axis', {})
            geographies_by_axis = context_info.get('geographies_by_axis', {})

            # If this context has segment dimensions, create one fact per segment axis
            if segments_by_axis:
                for axis, seg_info in segments_by_axis.items():
                    facts.append({
                        'concept': concept_name,
                        'value': value,
                        'end_date': context_info['end_date'],
                        'start_date': context_info['start_date'],
                        'segment': seg_info['segment'],
                        'geography': None,
                        'segment_axis': axis,
                        'geography_axis': None,
                        'form': form
                    })

            # If this context has geography dimensions (and no segments), create facts
            if geographies_by_axis and not segments_by_axis:
                for axis, geo_name in geographies_by_axis.items():
                    facts.append({
                        'concept': concept_name,
                        'value': value,
                        'end_date': context_info['end_date'],
                        'start_date': context_info['start_date'],
                        'segment': None,
                        'geography': geo_name,
                        'segment_axis': None,
                        'geography_axis': axis,
                        'form': form
                    })

            # If no dimensions, this is consolidated revenue
            if not segments_by_axis and not geographies_by_axis:
                facts.append({
                    'concept': concept_name,
                    'value': value,
                    'end_date': context_info['end_date'],
                    'start_date': context_info['start_date'],
                    'segment': None,
                    'geography': None,
                    'segment_axis': None,
                    'geography_axis': None,
                    'form': form
                })

        except (ValueError, TypeError):
            pass  # Skip invalid values


if __name__ == "__main__":
    # Ticker parameter is REQUIRED (no default)
    if len(sys.argv) < 2:
        print("Error: Ticker symbol required")
        print("Usage: python3 get_company_segment_geographic_financials.py <TICKER> [QUARTERS]")
        print("\nExamples:")
        print("  python3 get_company_segment_geographic_financials.py JNJ")
        print("  python3 get_company_segment_geographic_financials.py ABT 4")
        print("  python3 get_company_segment_geographic_financials.py PFE 8")
        print("\nDescription:")
        print("  Extracts segment and geographic revenue data from SEC EDGAR XBRL filings")
        print("  for any publicly traded company using dimensional analysis.")
        print("  Includes revenue reconciliation to verify data completeness.")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    quarters = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    result = get_company_segment_geographic_financials(
        ticker=ticker,
        quarters=quarters
    )

    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    # Display key metrics
    print("\n" + "="*80)
    print("KEY METRICS")
    print("="*80)

    if result.get('segment_revenue'):
        print("\nSegments by Revenue:")
        segments_sorted = sorted(
            result['segment_revenue'].items(),
            key=lambda x: x[1]['latest_revenue'],
            reverse=True
        )
        for i, (segment, data) in enumerate(segments_sorted, 1):
            revenue = data['latest_revenue']
            total_segment = sum(s['latest_revenue'] for s in result['segment_revenue'].values())
            pct = (revenue / total_segment * 100) if total_segment > 0 else 0
            print(f"{i}. {segment}: ${revenue:,.0f} ({pct:.1f}%)")

    if result.get('geographic_revenue') and len(result['geographic_revenue']) > 0:
        print("\nGeographies by Revenue:")
        geographies_sorted = sorted(
            result['geographic_revenue'].items(),
            key=lambda x: x[1]['latest_revenue'],
            reverse=True
        )
        for i, (geography, data) in enumerate(geographies_sorted, 1):
            revenue = data['latest_revenue']
            total_geo = sum(g['latest_revenue'] for g in result['geographic_revenue'].values())
            pct = (revenue / total_geo * 100) if total_geo > 0 else 0
            print(f"{i}. {geography}: ${revenue:,.0f} ({pct:.1f}%)")
