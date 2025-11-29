import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re
from collections import defaultdict

def get_enhanced_antibody_trials_by_geography():
    """Get enhanced antibody trials with geographic and temporal analysis.

    Uses CT.gov location filtering for accurate geographic classification.
    Analyzes ADC, bispecific, and multispecific antibody trials across
    US, EU, and China with temporal trends (2015-2024).

    Returns:
        dict: Contains total_trials, geographic_distribution, format_breakdown,
              temporal_trends, inflection_point, and visualization
    """

    print("Collecting enhanced antibody trials with location-based filtering...")
    print("="*80)

    # Define search terms for each format
    format_terms = {
        'ADC': ['antibody drug conjugate', 'ADC'],
        'bispecific': ['bispecific antibody', 'bispecific'],
        'multispecific': ['trispecific', 'tetraspecific', 'multispecific']
    }

    # Define regions
    regions = {
        'US': 'United States',
        'EU': ['Germany', 'France', 'United Kingdom', 'Spain', 'Italy', 'Netherlands'],
        'China': 'China'
    }

    # Data structures for results
    geographic_counts = {'US_EU': 0, 'China': 0, 'Other': 0}
    format_breakdown = {
        'ADC': {'US_EU': 0, 'China': 0, 'Other': 0, 'total': 0},
        'bispecific': {'US_EU': 0, 'China': 0, 'Other': 0, 'total': 0},
        'multispecific': {'US_EU': 0, 'China': 0, 'Other': 0, 'total': 0}
    }
    temporal_data = defaultdict(lambda: {'US_EU': 0, 'China': 0, 'Other': 0})

    # Collect trials with temporal data (sample for efficiency)
    all_trials_sample = []
    seen_nct_ids = set()

    # Query each format × location combination
    for format_name, terms in format_terms.items():
        print(f"\n{format_name.upper()} Trials:")
        print("-"*40)

        format_total = 0

        # US trials
        us_count = 0
        for term in terms:
            result = search(term=term, location=regions['US'], pageSize=100)
            count = extract_trial_count(result)
            us_count += count

            # Collect sample for temporal analysis
            trials = extract_trials_with_dates(result, 'US_EU')
            for trial in trials:
                if trial['nct_id'] not in seen_nct_ids:
                    seen_nct_ids.add(trial['nct_id'])
                    all_trials_sample.append(trial)

        # Remove duplicates from multiple search terms
        us_count = count_unique_trials_from_region(format_name, 'US', terms)
        format_breakdown[format_name]['US_EU'] += us_count
        print(f"  US:    {us_count:4} trials")

        # EU trials
        eu_count = 0
        for country in regions['EU']:
            for term in terms:
                result = search(term=term, location=country, pageSize=100)
                count = extract_trial_count(result)
                eu_count += count

                # Collect sample for temporal analysis
                trials = extract_trials_with_dates(result, 'US_EU')
                for trial in trials:
                    if trial['nct_id'] not in seen_nct_ids:
                        seen_nct_ids.add(trial['nct_id'])
                        all_trials_sample.append(trial)

        format_breakdown[format_name]['US_EU'] += eu_count
        print(f"  EU:    {eu_count:4} trials")

        # China trials
        china_count = 0
        for term in terms:
            result = search(term=term, location=regions['China'], pageSize=100)
            count = extract_trial_count(result)
            china_count += count

            # Collect sample for temporal analysis
            trials = extract_trials_with_dates(result, 'China')
            for trial in trials:
                if trial['nct_id'] not in seen_nct_ids:
                    seen_nct_ids.add(trial['nct_id'])
                    all_trials_sample.append(trial)

        china_count = count_unique_trials_from_region(format_name, 'China', terms)
        format_breakdown[format_name]['China'] = china_count
        print(f"  China: {china_count:4} trials")

        # Calculate format total
        format_total = format_breakdown[format_name]['US_EU'] + format_breakdown[format_name]['China']
        format_breakdown[format_name]['total'] = format_total
        print(f"  TOTAL: {format_total:4} trials")

    # Calculate geographic totals
    for format_name in format_breakdown:
        geographic_counts['US_EU'] += format_breakdown[format_name]['US_EU']
        geographic_counts['China'] += format_breakdown[format_name]['China']

    total_trials = geographic_counts['US_EU'] + geographic_counts['China']

    print(f"\n{'='*80}")
    print(f"Total Enhanced Antibody Trials: {total_trials:,}")
    print(f"  US/EU: {geographic_counts['US_EU']:,} ({geographic_counts['US_EU']/total_trials*100:.1f}%)")
    print(f"  China: {geographic_counts['China']:,} ({geographic_counts['China']/total_trials*100:.1f}%)")
    print(f"{'='*80}\n")

    # Build temporal trends from sample
    for trial in all_trials_sample:
        if trial['year']:
            temporal_data[trial['year']][trial['geography']] += 1

    # Calculate temporal trends
    temporal_trends = []
    for year in sorted(temporal_data.keys()):
        temporal_trends.append({
            'year': year,
            'US_EU': temporal_data[year]['US_EU'],
            'China': temporal_data[year]['China'],
            'Other': temporal_data[year]['Other']
        })

    # Find inflection point (when China >= US_EU)
    inflection_point = None
    for trend in temporal_trends:
        if trend['China'] >= trend['US_EU'] and trend['China'] > 0:
            inflection_point = {
                'year': trend['year'],
                'description': f"China surpassed US/EU in enhanced antibody trials ({trend['China']} vs {trend['US_EU']})"
            }
            break

    # Create visualization
    visualization = create_visualization(geographic_counts, format_breakdown, temporal_trends)

    return {
        'total_trials': total_trials,
        'date_range': '2015-2024',
        'geographic_distribution': geographic_counts,
        'format_breakdown': format_breakdown,
        'temporal_trends': temporal_trends,
        'inflection_point': inflection_point,
        'visualization': visualization,
        'summary': create_summary(total_trials, geographic_counts, format_breakdown, inflection_point)
    }


def count_unique_trials_from_region(format_name, region, terms):
    """Query region for all terms and count unique trials."""
    location = 'United States' if region == 'US' else 'China'
    all_nct_ids = set()

    for term in terms:
        result = search(term=term, location=location, pageSize=1000)

        # Extract all NCT IDs
        nct_ids = re.findall(r'NCT\d{8}', result)
        all_nct_ids.update(nct_ids)

        # Check for pagination
        page_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        page_token = page_token_match.group(1) if page_token_match else None

        while page_token:
            result = search(term=term, location=location, pageSize=1000, pageToken=page_token)
            nct_ids = re.findall(r'NCT\d{8}', result)
            all_nct_ids.update(nct_ids)

            next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
            if next_token_match and next_token_match.group(1) != page_token:
                page_token = next_token_match.group(1)
            else:
                break

    return len(all_nct_ids)


def extract_trial_count(result):
    """Extract total trial count from search result."""
    count_match = re.search(r'Results:\*\*\s+\d+\s+of\s+([\d,]+)', result)
    if count_match:
        return int(count_match.group(1).replace(',', ''))
    return 0


def extract_trials_with_dates(result, geography):
    """Extract trial data including dates for temporal analysis."""
    trials = []

    # Parse trials from markdown
    trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)

    # Process trials (skip first element which is header)
    for i in range(1, len(trial_blocks), 2):
        if i + 1 >= len(trial_blocks):
            break

        nct_id = trial_blocks[i]
        content = trial_blocks[i + 1]

        # Extract first posted date
        first_post_match = re.search(r'\*\*First Posted:\*\*\s*(.+?)(?=\n\*\*|\n###|$)', content)
        first_posted = first_post_match.group(1).strip() if first_post_match else ''

        # Extract year
        year = None
        if first_posted:
            year_match = re.search(r'\d{4}', first_posted)
            if year_match:
                year_int = int(year_match.group(0))
                if 2015 <= year_int <= 2024:
                    year = year_int

        trials.append({
            'nct_id': nct_id,
            'year': year,
            'geography': geography
        })

    return trials


def create_visualization(geo_counts, format_breakdown, temporal_trends):
    """Create ASCII visualization of the data."""

    viz = []
    viz.append("\n" + "="*80)
    viz.append("ENHANCED ANTIBODY TRIALS: GEOGRAPHIC & FORMAT ANALYSIS")
    viz.append("="*80)

    # Geographic distribution
    viz.append("\nGEOGRAPHIC DISTRIBUTION:")
    viz.append("-" * 40)
    total = sum(geo_counts.values())
    for region, count in sorted(geo_counts.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        pct = (count / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 2)
        viz.append(f"{region:10} {count:4} ({pct:5.1f}%) {bar}")

    # Format breakdown by geography
    viz.append("\nFORMAT BREAKDOWN BY GEOGRAPHY:")
    viz.append("-" * 40)
    for fmt, counts in format_breakdown.items():
        if counts['total'] == 0:
            continue
        viz.append(f"\n{fmt.upper()}:")
        for region in ['US_EU', 'China']:
            count = counts[region]
            total_fmt = counts['total']
            pct = (count / total_fmt * 100) if total_fmt > 0 else 0
            bar = '▓' * int(pct / 2)
            viz.append(f"  {region:10} {count:4} ({pct:5.1f}%) {bar}")

    # Temporal trends (line chart)
    if temporal_trends:
        viz.append("\nTEMPORAL TRENDS (Sample - Trials per Year):")
        viz.append("-" * 40)
        max_count = max(max(t['US_EU'], t['China']) for t in temporal_trends if t['US_EU'] > 0 or t['China'] > 0)
        if max_count > 0:
            scale = 40 / max_count

            for trend in temporal_trends:
                viz.append(f"\n{trend['year']}:")
                us_eu_bar = '●' * int(trend['US_EU'] * scale)
                china_bar = '○' * int(trend['China'] * scale)
                viz.append(f"  US/EU: {trend['US_EU']:3} {us_eu_bar}")
                viz.append(f"  China: {trend['China']:3} {china_bar}")

    viz.append("\n" + "="*80)

    return '\n'.join(viz)


def create_summary(total, geo_counts, format_breakdown, inflection):
    """Create text summary of findings."""

    summary = []
    summary.append(f"\nENHANCED ANTIBODY TRIALS GEOGRAPHIC ANALYSIS")
    summary.append(f"Total Trials: {total:,}")
    summary.append(f"\nGeographic Distribution:")
    summary.append(f"  US/EU: {geo_counts['US_EU']:,} ({geo_counts['US_EU']/total*100:.1f}%)")
    summary.append(f"  China: {geo_counts['China']:,} ({geo_counts['China']/total*100:.1f}%)")

    summary.append(f"\nFormat Breakdown:")
    for fmt, counts in format_breakdown.items():
        if counts['total'] == 0:
            continue
        summary.append(f"  {fmt.upper()}: {counts['total']:,} total")
        summary.append(f"    US/EU: {counts['US_EU']:,} ({counts['US_EU']/counts['total']*100:.1f}%), China: {counts['China']:,} ({counts['China']/counts['total']*100:.1f}%)")

    if inflection:
        summary.append(f"\nInflection Point: {inflection['year']}")
        summary.append(f"  {inflection['description']}")

    return '\n'.join(summary)


if __name__ == "__main__":
    result = get_enhanced_antibody_trials_by_geography()
    print(result['summary'])
    print(result['visualization'])
