import sys
import re
from collections import defaultdict
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_adc_trials_by_payload(payload_type='all'):
    """Get ADC clinical trials by payload class with geographic and competitive intelligence.

    Args:
        payload_type (str): Payload class to query
            - 'topoisomerase_i': Topo I inhibitor ADCs
            - 'dna_damaging': DNA-damaging agent ADCs
            - 'tubulin_inhibitor': Tubulin inhibitor ADCs
            - 'all': All ADC trials (default)

    Returns:
        dict: Contains total_count, payload_class, geographic_distribution,
              target_analysis, phase_distribution, sponsor_analysis
    """

    # Payload taxonomy
    payload_classes = {
        'topoisomerase_i': {
            'search_terms': ['deruxtecan', 'DXd', 'SN-38', 'exatecan', 'topoisomerase I inhibitor'],
            'description': 'Topoisomerase I inhibitor payloads'
        },
        'dna_damaging': {
            'search_terms': ['PBD', 'pyrrolobenzodiazepine', 'duocarmycin', 'calicheamicin'],
            'description': 'DNA-damaging agent payloads'
        },
        'tubulin_inhibitor': {
            'search_terms': ['MMAE', 'MMAF', 'monomethyl auristatin', 'maytansine', 'DM1', 'DM4'],
            'description': 'Tubulin inhibitor payloads'
        },
        'all': {
            'search_terms': ['antibody drug conjugate', 'ADC'],
            'description': 'All ADC trials (baseline)'
        }
    }

    if payload_type not in payload_classes:
        raise ValueError(f"Invalid payload_type. Must be one of: {list(payload_classes.keys())}")

    payload_config = payload_classes[payload_type]
    search_terms = payload_config['search_terms']

    # Aggregate all trials across search terms
    all_trials = []
    seen_nct_ids = set()

    for term in search_terms:
        print(f"  Searching for '{term}'...")
        page_token = None
        page_count = 0

        while True:
            try:
                result = search(
                    term=term,
                    pageSize=1000,
                    pageToken=page_token
                )

                if not result or not isinstance(result, str):
                    break

                # Extract trials from markdown
                trial_pattern = r'###\s+\d+\.\s+(NCT\d{8})'
                trials = re.split(trial_pattern, result)[1:]  # Skip first empty element

                page_trials = 0
                for i in range(0, len(trials), 2):
                    if i+1 < len(trials):
                        nct_id = trials[i]
                        content = trials[i+1]

                        # Deduplicate
                        if nct_id not in seen_nct_ids:
                            all_trials.append({
                                'nct_id': nct_id,
                                'content': content
                            })
                            seen_nct_ids.add(nct_id)
                            page_trials += 1

                page_count += 1
                print(f"    Page {page_count}: {page_trials} new trials (total unique: {len(all_trials)})")

                # Check for next page
                next_page_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
                if next_page_match:
                    page_token = next_page_match.group(1)
                else:
                    break

            except Exception as e:
                print(f"    Error on page {page_count + 1}: {e}")
                break

    print(f"\nTotal unique trials found: {len(all_trials)}")

    # Geographic classification
    def classify_geography(content):
        """Classify trial geography based on sponsor and location."""
        content_lower = content.lower()

        # China indicators
        china_patterns = [
            r'china', r'chinese', r'beijing', r'shanghai', r'guangzhou',
            r'shenzhen', r'hangzhou', r'nanjing', r'wuhan'
        ]

        # US/EU indicators
        us_eu_patterns = [
            r'united states', r'usa', r'u\.s\.', r'europe', r'european',
            r'pfizer', r'merck', r'roche', r'abbvie', r'bristol',
            r'johnson & johnson', r'novartis', r'astrazeneca', r'gsk',
            r'gilead', r'amgen', r'regeneron', r'seagen', r'immunogen'
        ]

        has_china = any(re.search(p, content_lower) for p in china_patterns)
        has_us_eu = any(re.search(p, content_lower) for p in us_eu_patterns)

        if has_china and not has_us_eu:
            return 'China'
        elif has_us_eu:
            return 'US_EU'
        else:
            return 'Other'

    # Target extraction
    def extract_targets(content):
        """Extract ADC targets from intervention text."""
        targets = []
        target_patterns = {
            'HER2': r'HER2|trastuzumab deruxtecan|T-DXd|enhertu',
            'TROP2': r'TROP2|sacituzumab|trodelvy',
            'B7-H3': r'B7-H3|B7H3',
            'NECTIN-4': r'NECTIN-4|NECTIN4|enfortumab|padcev',
            'CD19': r'CD19|loncastuximab',
            'CD22': r'CD22',
            'CD30': r'CD30|brentuximab|adcetris',
            'CD33': r'CD33|gemtuzumab',
            'CD79B': r'CD79B|polatuzumab',
            'EGFR': r'EGFR|cetuximab',
            'MUC16': r'MUC16|CA-125',
            'FOLR1': r'FOLR1|folate receptor|mirvetuximab',
            'GPRC5D': r'GPRC5D',
            'BCMA': r'BCMA',
            'CEACAM5': r'CEACAM5|CEA'
        }

        content_lower = content.lower()
        for target, pattern in target_patterns.items():
            if re.search(pattern, content_lower):
                targets.append(target)

        return targets if targets else ['Unknown']

    # Phase extraction
    def extract_phase(content):
        """Extract trial phase."""
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|\*\*)', content)
        if phase_match:
            phase = phase_match.group(1).strip()
            # Normalize phase
            if 'PHASE1' in phase.upper() or 'PHASE 1' in phase.upper():
                return 'PHASE1'
            elif 'PHASE2' in phase.upper() or 'PHASE 2' in phase.upper():
                return 'PHASE2'
            elif 'PHASE3' in phase.upper() or 'PHASE 3' in phase.upper():
                return 'PHASE3'
            elif 'PHASE4' in phase.upper() or 'PHASE 4' in phase.upper():
                return 'PHASE4'
        return 'Unknown'

    # Sponsor extraction
    def extract_sponsor(content):
        """Extract lead sponsor."""
        sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\n|\*\*)', content)
        if sponsor_match:
            return sponsor_match.group(1).strip()
        return 'Unknown'

    # Analyze trials
    geographic_dist = defaultdict(int)
    target_breakdown = defaultdict(int)
    phase_dist = defaultdict(int)
    sponsor_data = []

    for trial in all_trials:
        content = trial['content']

        # Geography
        geo = classify_geography(content)
        geographic_dist[geo] += 1

        # Targets
        targets = extract_targets(content)
        for target in targets:
            target_breakdown[target] += 1

        # Phase
        phase = extract_phase(content)
        phase_dist[phase] += 1

        # Sponsor
        sponsor = extract_sponsor(content)
        sponsor_data.append({
            'name': sponsor,
            'geography': geo
        })

    # Aggregate sponsor counts
    sponsor_counts = defaultdict(lambda: {'count': 0, 'geography': defaultdict(int)})
    for s in sponsor_data:
        sponsor_counts[s['name']]['count'] += 1
        sponsor_counts[s['name']]['geography'][s['geography']] += 1

    # Top sponsors
    top_sponsors = sorted(
        [
            {
                'name': name,
                'count': data['count'],
                'geography': max(data['geography'].items(), key=lambda x: x[1])[0] if data['geography'] else 'Unknown'
            }
            for name, data in sponsor_counts.items()
        ],
        key=lambda x: x['count'],
        reverse=True
    )[:10]

    # Generate summary
    summary = f"""ADC Trials Analysis: {payload_config['description']}

Total Trials: {len(all_trials)}
Payload Type: {payload_type}

Geographic Distribution:
  US/EU: {geographic_dist['US_EU']} ({100*geographic_dist['US_EU']/len(all_trials):.1f}%)
  China: {geographic_dist['China']} ({100*geographic_dist['China']/len(all_trials):.1f}%)
  Other: {geographic_dist['Other']} ({100*geographic_dist['Other']/len(all_trials):.1f}%)

Top Targets:
"""

    for target, count in sorted(target_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
        summary += f"  {target}: {count} trials ({100*count/len(all_trials):.1f}%)\n"

    summary += f"\nPhase Distribution:\n"
    for phase in ['PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', 'Unknown']:
        count = phase_dist[phase]
        if count > 0:
            summary += f"  {phase}: {count} trials ({100*count/len(all_trials):.1f}%)\n"

    summary += f"\nTop Sponsors:\n"
    for sponsor in top_sponsors[:5]:
        summary += f"  {sponsor['name']}: {sponsor['count']} trials ({sponsor['geography']})\n"

    return {
        'total_trials': len(all_trials),
        'payload_type': payload_type,
        'payload_description': payload_config['description'],
        'geographic_distribution': dict(geographic_dist),
        'target_breakdown': dict(target_breakdown),
        'phase_distribution': dict(phase_dist),
        'top_sponsors': top_sponsors,
        'summary': summary
    }

if __name__ == "__main__":
    import sys

    # Get payload type from command line or use default
    payload_type = sys.argv[1] if len(sys.argv) > 1 else 'all'

    print(f"Analyzing ADC trials by payload: {payload_type}\n")
    result = get_adc_trials_by_payload(payload_type)
    print("\n" + "="*80)
    print(result['summary'])
    print("="*80)
