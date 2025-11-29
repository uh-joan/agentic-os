import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_bispecific_antibody_trials(mechanism_type='all'):
    """Get bispecific/multispecific antibody trials by mechanism complexity.

    Args:
        mechanism_type (str): Mechanism class to query
            - 'all': All bispecific antibodies
            - 't_cell_engager': Simple CD3+ T-cell engagers
            - 'checkpoint_modulator': Checkpoint inhibitor bispecifics
            - 'complex_modulator': Trispecific/tetraspecific constructs

    Returns:
        dict: Contains total_count, mechanism_type, geographic_distribution,
              target_combinations, complexity_analysis, phase_distribution
    """

    # Mechanism taxonomy
    mechanism_types = {
        'all': {
            'search_terms': ['bispecific', 'bispecific antibody'],
            'description': 'All bispecific antibodies'
        },
        't_cell_engager': {
            'search_terms': ['CD3 bispecific', 'T-cell engager', 'BiTE', 'CD3+'],
            'description': 'Simple T-cell engagers (CD3 + tumor antigen)'
        },
        'checkpoint_modulator': {
            'search_terms': ['PD-1 bispecific', 'PD-L1 bispecific', 'CTLA-4 bispecific', 'LAG-3 bispecific'],
            'description': 'Checkpoint inhibitor bispecifics'
        },
        'complex_modulator': {
            'search_terms': ['trispecific', 'tetraspecific', 'TGF-beta trap bispecific', 'IL-15 bispecific'],
            'description': 'Complex immune modulators (3+ mechanisms)'
        }
    }

    if mechanism_type not in mechanism_types:
        raise ValueError(f"Invalid mechanism_type. Choose from: {list(mechanism_types.keys())}")

    config = mechanism_types[mechanism_type]

    # Initialize aggregators
    all_trials = []
    seen_nct_ids = set()
    geographic_dist = {'US_EU': 0, 'China': 0, 'Other': 0}
    target_combinations = {}
    complexity_counts = {'simple': 0, 'complex': 0}
    phase_dist = {}
    sponsor_data = {}

    def classify_geography(content):
        """Classify trial geography based on sponsor and location."""
        content_lower = content.lower()

        # China indicators
        china_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'guangzhou',
            'shenzhen', 'hangzhou', 'nanjing', 'wuhan', 'chengdu',
            'innovent', 'hengrui', 'beigene', 'hutchmed', 'cstone',
            'junshi', 'transcenta', 'akeso', 'antengene'
        ]

        # US/EU indicators
        us_eu_indicators = [
            'united states', 'usa', 'u.s.', 'america', 'american',
            'pfizer', 'merck', 'bristol', 'abbvie', 'amgen', 'genentech',
            'roche', 'novartis', 'sanofi', 'astrazeneca', 'gsk',
            'regeneron', 'gilead', 'biogen', 'bms', 'lilly',
            'germany', 'german', 'france', 'french', 'uk', 'british',
            'netherlands', 'swiss', 'switzerland', 'belgium', 'italy'
        ]

        if any(indicator in content_lower for indicator in china_indicators):
            return 'China'
        elif any(indicator in content_lower for indicator in us_eu_indicators):
            return 'US_EU'
        else:
            return 'Other'

    def extract_targets(intervention_text):
        """Extract target combinations from intervention name."""
        if not intervention_text:
            return None

        intervention_lower = intervention_text.lower()

        # T-cell engager patterns
        t_cell_patterns = [
            r'cd3[+\s]*(?:x\s*)?([a-z0-9]+)',
            r'([a-z0-9]+)[+\s]*(?:x\s*)?cd3',
        ]

        for pattern in t_cell_patterns:
            match = re.search(pattern, intervention_lower)
            if match and 'cd3' in intervention_lower:
                target = match.group(1).upper()
                if target not in ['CD3', 'X', 'BISPECIFIC', 'ANTIBODY']:
                    return f"CD3+{target}"

        # Checkpoint combinations
        checkpoint_targets = ['pd-1', 'pd-l1', 'ctla-4', 'lag-3', 'lag3',
                             'tim-3', 'tim3', 'tigit']
        found_checkpoints = [cp for cp in checkpoint_targets if cp in intervention_lower]

        if len(found_checkpoints) >= 2:
            combo = '+'.join([cp.upper().replace('-', '') for cp in found_checkpoints[:2]])
            return combo

        # Other bispecific patterns
        if 'bispecific' in intervention_lower:
            # Try to extract two target mentions
            target_pattern = r'\b(cd\d+[a-z]?|her\d|egfr|bcma|psma|dll\d|vegf|ang2|tgf[β-]?beta|il-?\d+)\b'
            targets = re.findall(target_pattern, intervention_lower)
            if len(targets) >= 2:
                return '+'.join([t.upper() for t in targets[:2]])

        return 'Other'

    def assess_complexity(content):
        """Assess mechanism complexity (simple vs complex)."""
        content_lower = content.lower()
        mechanisms = []

        # Count distinct mechanism types
        if re.search(r'cd3|t-cell engager|bite', content_lower):
            mechanisms.append('t_cell_engagement')
        if re.search(r'pd-1|pd-l1|ctla-4|lag-3|tim-3|tigit', content_lower):
            mechanisms.append('checkpoint_modulation')
        if re.search(r'tgf-?beta|il-15|il-2|cd28|4-1bb', content_lower):
            mechanisms.append('immune_modulation')
        if re.search(r'vegf|ang2', content_lower):
            mechanisms.append('angiogenesis')

        # Trispecific/tetraspecific are automatically complex
        if re.search(r'trispecific|tetraspecific|multi-?specific', content_lower):
            return 'complex'

        # Simple = single mechanism, Complex = multiple mechanisms
        return 'simple' if len(mechanisms) == 1 else 'complex'

    # Query each search term for this mechanism type
    for search_term in config['search_terms']:
        print(f"Querying: {search_term}")
        page_token = None
        page_count = 0

        while True:
            try:
                result = search(
                    intervention=search_term,
                    pageSize=1000,
                    pageToken=page_token
                )

                if not result:
                    break

                page_count += 1

                # Parse markdown response
                trial_pattern = r'###\s+\d+\.\s+(NCT\d{8})'
                trials = re.split(trial_pattern, result)

                # Process trials (skip first element which is header)
                for i in range(1, len(trials), 2):
                    if i + 1 >= len(trials):
                        break

                    nct_id = trials[i]
                    content = trials[i + 1]

                    # Skip duplicates
                    if nct_id in seen_nct_ids:
                        continue
                    seen_nct_ids.add(nct_id)

                    # Extract fields
                    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', content)
                    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', content)
                    status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', content)
                    sponsor_match = re.search(r'\*\*Sponsor:\*\*\s*(.+?)(?:\n|$)', content)
                    intervention_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?:\n|$)', content)
                    location_match = re.search(r'\*\*Locations:\*\*\s*(.+?)(?:\n|$)', content)

                    title = title_match.group(1).strip() if title_match else "Unknown"
                    phase = phase_match.group(1).strip() if phase_match else "Unknown"
                    status = status_match.group(1).strip() if status_match else "Unknown"
                    sponsor = sponsor_match.group(1).strip() if sponsor_match else "Unknown"
                    intervention = intervention_match.group(1).strip() if intervention_match else ""
                    location = location_match.group(1).strip() if location_match else ""

                    # Geographic classification
                    geo_content = f"{sponsor} {location}".lower()
                    geography = classify_geography(geo_content)
                    geographic_dist[geography] += 1

                    # Target combination extraction
                    target_combo = extract_targets(intervention)
                    if target_combo:
                        target_combinations[target_combo] = target_combinations.get(target_combo, 0) + 1

                    # Complexity assessment
                    complexity = assess_complexity(f"{title} {intervention}")
                    complexity_counts[complexity] += 1

                    # Phase distribution
                    phase_clean = phase.upper().replace(' ', '')
                    phase_dist[phase_clean] = phase_dist.get(phase_clean, 0) + 1

                    # Sponsor tracking
                    if sponsor not in sponsor_data:
                        sponsor_data[sponsor] = {
                            'count': 0,
                            'geography': geography
                        }
                    sponsor_data[sponsor]['count'] += 1

                    all_trials.append({
                        'nct_id': nct_id,
                        'title': title,
                        'phase': phase,
                        'status': status,
                        'sponsor': sponsor,
                        'intervention': intervention,
                        'geography': geography,
                        'target_combo': target_combo,
                        'complexity': complexity
                    })

                # Check for next page
                next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
                if next_token_match and page_count < 10:  # Safety limit
                    page_token = next_token_match.group(1)
                    print(f"  Page {page_count} complete, continuing...")
                else:
                    break

            except Exception as e:
                print(f"Error querying {search_term}: {str(e)}")
                break

    # Sort target combinations by frequency
    sorted_targets = sorted(
        target_combinations.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]  # Top 20

    # Sort sponsors by count
    top_sponsors = sorted(
        [
            {
                'name': name,
                'count': data['count'],
                'geography': data['geography']
            }
            for name, data in sponsor_data.items()
        ],
        key=lambda x: x['count'],
        reverse=True
    )[:10]

    total_trials = len(all_trials)

    # Calculate percentages for summary
    us_eu_pct = (geographic_dist['US_EU'] / total_trials * 100) if total_trials > 0 else 0
    china_pct = (geographic_dist['China'] / total_trials * 100) if total_trials > 0 else 0
    simple_pct = (complexity_counts['simple'] / total_trials * 100) if total_trials > 0 else 0
    complex_pct = (complexity_counts['complex'] / total_trials * 100) if total_trials > 0 else 0

    # Generate summary
    summary = f"""
Bispecific Antibody Trial Analysis - {config['description']}

Total Trials: {total_trials}

Geographic Distribution:
- US/EU: {geographic_dist['US_EU']} ({us_eu_pct:.1f}%)
- China: {geographic_dist['China']} ({china_pct:.1f}%)
- Other: {geographic_dist['Other']} ({(geographic_dist['Other']/total_trials*100) if total_trials > 0 else 0:.1f}%)

Mechanism Complexity:
- Simple (single mechanism): {complexity_counts['simple']} ({simple_pct:.1f}%)
- Complex (multiple mechanisms): {complexity_counts['complex']} ({complex_pct:.1f}%)

Top Target Combinations:
"""

    for target, count in sorted_targets[:5]:
        pct = (count / total_trials * 100) if total_trials > 0 else 0
        summary += f"- {target}: {count} ({pct:.1f}%)\n"

    summary += f"\nPhase Distribution:\n"
    for phase, count in sorted(phase_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = (count / total_trials * 100) if total_trials > 0 else 0
        summary += f"- {phase}: {count} ({pct:.1f}%)\n"

    summary += f"\nTop Sponsors:\n"
    for sponsor in top_sponsors[:5]:
        summary += f"- {sponsor['name']} ({sponsor['geography']}): {sponsor['count']} trials\n"

    return {
        'total_trials': total_trials,
        'mechanism_type': mechanism_type,
        'mechanism_description': config['description'],
        'geographic_distribution': geographic_dist,
        'target_combinations': dict(sorted_targets),
        'complexity_analysis': complexity_counts,
        'phase_distribution': phase_dist,
        'top_sponsors': top_sponsors,
        'summary': summary.strip(),
        'trials': all_trials  # Full dataset for further analysis
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze bispecific antibody trials by mechanism complexity'
    )
    parser.add_argument(
        '--mechanism',
        default='all',
        choices=['all', 't_cell_engager', 'checkpoint_modulator', 'complex_modulator'],
        help='Mechanism type to analyze'
    )

    args = parser.parse_args()

    print(f"Analyzing {args.mechanism} bispecific antibody trials...")
    print("=" * 70)

    result = get_bispecific_antibody_trials(args.mechanism)

    print(result['summary'])
    print("\n" + "=" * 70)
    print(f"Analysis complete. {result['total_trials']} trials analyzed.")
