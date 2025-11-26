import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re
from typing import Dict, List, Tuple

# Pattern-based sponsor type detection (NO HARDCODED COMPANY NAMES)
ACADEMIC_KEYWORDS = [
    'university', 'college', 'institute', 'medical center',
    'cancer center', 'hospital', 'school of medicine',
    "children's hospital", 'research center', 'clinic',
    'foundation', 'academic'
]

GOVERNMENT_KEYWORDS = [
    'national institutes', 'nih', 'nci', 'niaid', 'nhlbi',
    'veterans affairs', 'department of', 'ministry of health',
    'public health', 'government', 'federal'
]

CRO_KEYWORDS = [
    'cro', 'contract research', 'clinical research organization',
    'research services', 'quintiles', 'covance', 'parexel'
]

# Therapeutic area query patterns
THERAPEUTIC_QUERIES = {
    'ultra_rare_metabolic': 'lysosomal storage OR mitochondrial disease OR organic acidemia OR urea cycle OR peroxisomal',
    'neuromuscular': 'muscular dystrophy OR spinal muscular atrophy OR myasthenia gravis OR neuropathy',
    'gene_therapy': 'gene therapy OR AAV OR lentiviral OR adenoviral OR CRISPR',
    'oncology_rare': 'rare cancer OR orphan cancer OR sarcoma OR mesothelioma',
    'any': 'orphan OR "rare disease"'
}

def is_academic_sponsor(sponsor: str) -> bool:
    """Check if sponsor is academic institution using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in ACADEMIC_KEYWORDS)

def is_government_sponsor(sponsor: str) -> bool:
    """Check if sponsor is government agency using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in GOVERNMENT_KEYWORDS)

def is_cro_sponsor(sponsor: str) -> bool:
    """Check if sponsor is CRO using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in CRO_KEYWORDS)

def extract_field(content, field_name):
    """Extract field value from markdown content."""
    pattern = rf'\*\*{re.escape(field_name)}:\*\*\s*(.+?)(?:\n\*\*|\n\n|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        value = match.group(1).strip()
        value = re.sub(r'\*\*', '', value)
        value = re.sub(r'\n+', ' ', value)
        return value
    return None

def query_ct_gov_with_pagination(query: str, phase: str) -> List[Dict]:
    """Query CT.gov with full pagination."""
    all_trials = []
    page_token = None
    page_count = 0

    print(f"Querying CT.gov: {query[:50]}... phase={phase}")

    while True:
        page_count += 1

        # Use condition parameter for the search query
        result = search(
            condition=query,
            phase=phase,
            pageSize=1000,
            pageToken=page_token if page_token else None
        )

        if not result:
            break

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)

        for i in range(1, len(trial_blocks), 2):
            if i+1 < len(trial_blocks):
                nct_id = trial_blocks[i]
                content = trial_blocks[i+1]

                trial = {
                    'nct_id': nct_id,
                    'sponsor': extract_field(content, 'Lead Sponsor'),
                    'intervention': extract_field(content, 'Interventions'),
                    'condition': extract_field(content, 'Conditions'),
                    'phase': extract_field(content, 'Phase'),
                    'status': extract_field(content, 'Status')
                }

                all_trials.append(trial)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match and len(all_trials) < 10000:
            page_token = next_token_match.group(1)
            print(f"  Page {page_count}: {len(trial_blocks)-1} trials")
        else:
            break

    print(f"  Total: {page_count} pages, {len(all_trials)} trials")
    return all_trials

def filter_and_aggregate_sponsors(
    trials: List[Dict],
    exclude_academic: bool,
    exclude_government: bool,
    exclude_cro: bool,
    min_programs: int,
    max_programs: int
) -> Tuple[Dict[str, List[Dict]], Dict[str, int]]:
    """Filter trials and aggregate by sponsor with filtering stats."""

    filtering_stats = {
        'total_trials': len(trials),
        'companies_before_filtering': 0,
        'excluded_academic': 0,
        'excluded_government': 0,
        'excluded_large_pharma': 0,
        'excluded_cro': 0,
        'excluded_small_portfolio': 0,
        'companies_after_filtering': 0
    }

    # Aggregate by sponsor
    sponsor_trials = {}
    for trial in trials:
        sponsor = trial.get('sponsor', 'Unknown')
        if sponsor not in sponsor_trials:
            sponsor_trials[sponsor] = []
        sponsor_trials[sponsor].append(trial)

    filtering_stats['companies_before_filtering'] = len(sponsor_trials)

    # Filter sponsors
    filtered_sponsors = {}
    for sponsor, sponsor_trial_list in sponsor_trials.items():
        # Check exclusions
        if exclude_academic and is_academic_sponsor(sponsor):
            filtering_stats['excluded_academic'] += 1
            continue

        if exclude_government and is_government_sponsor(sponsor):
            filtering_stats['excluded_government'] += 1
            continue

        if exclude_cro and is_cro_sponsor(sponsor):
            filtering_stats['excluded_cro'] += 1
            continue

        # Check portfolio size
        program_count = len(sponsor_trial_list)
        if program_count < min_programs:
            filtering_stats['excluded_small_portfolio'] += 1
            continue

        if program_count > max_programs:
            filtering_stats['excluded_large_pharma'] += 1
            continue

        filtered_sponsors[sponsor] = sponsor_trial_list

    filtering_stats['companies_after_filtering'] = len(filtered_sponsors)

    return filtered_sponsors, filtering_stats

def calculate_acquisition_score(sponsor: str, trials: List[Dict]) -> int:
    """Calculate acquisition attractiveness score."""
    score = 0

    total_programs = len(trials)
    phase2_count = sum(1 for t in trials if 'phase2' in str(t.get('phase', '')).lower())
    phase3_count = sum(1 for t in trials if 'phase3' in str(t.get('phase', '')).lower())
    recruiting_count = sum(1 for t in trials if 'recruiting' in str(t.get('status', '')).lower())

    # Portfolio sweet spot (2-5 programs): +30
    if 2 <= total_programs <= 5:
        score += 30
    elif total_programs == 1:
        score += 10
    elif total_programs > 5:
        score += 20

    # Has Phase 3 (de-risked): +25
    if phase3_count > 0:
        score += 25

    # Multiple programs (platform potential): +20
    if total_programs >= 3:
        score += 20

    # Active recruiting (momentum): +15
    if recruiting_count > 0:
        score += 15

    # Balanced Phase 2+3 portfolio: +10
    if phase2_count > 0 and phase3_count > 0:
        score += 10

    return score

def rank_acquisition_targets(
    sponsor_trials: Dict[str, List[Dict]],
    max_results: int
) -> List[Dict]:
    """Rank sponsors by acquisition attractiveness."""

    ranked_targets = []

    for sponsor, trials in sponsor_trials.items():
        # Calculate metrics
        total_programs = len(trials)
        phase2_count = sum(1 for t in trials if 'phase2' in str(t.get('phase', '')).lower())
        phase3_count = sum(1 for t in trials if 'phase3' in str(t.get('phase', '')).lower())
        recruiting_count = sum(1 for t in trials if 'recruiting' in str(t.get('status', '')).lower())

        # Find lead asset
        lead_asset = None
        for trial in sorted(trials, key=lambda t: (
            'phase3' in str(t.get('phase', '')).lower(),
            'phase2' in str(t.get('phase', '')).lower(),
            'recruiting' in str(t.get('status', '')).lower()
        ), reverse=True):
            lead_asset = trial
            break

        # Calculate score
        score = calculate_acquisition_score(sponsor, trials)

        ranked_targets.append({
            'sponsor': sponsor,
            'acquisition_score': score,
            'total_programs': total_programs,
            'phase2_count': phase2_count,
            'phase3_count': phase3_count,
            'recruiting_count': recruiting_count,
            'lead_asset': {
                'nct_id': lead_asset.get('nct_id', 'Unknown'),
                'intervention': lead_asset.get('intervention', 'Unknown'),
                'condition': lead_asset.get('condition', 'Unknown'),
                'phase': lead_asset.get('phase', 'Unknown'),
                'status': lead_asset.get('status', 'Unknown')
            } if lead_asset else None,
            'all_programs': trials
        })

    # Sort by score
    ranked_targets.sort(key=lambda x: x['acquisition_score'], reverse=True)

    # Add rank
    for i, target in enumerate(ranked_targets[:max_results], 1):
        target['rank'] = i

    return ranked_targets[:max_results]

def get_rare_disease_acquisition_targets(
    therapeutic_focus: str = 'any',
    min_programs: int = 1,
    max_programs: int = 8,
    exclude_academic: bool = True,
    exclude_government: bool = True,
    exclude_cro: bool = True,
    prefer_phase3: bool = True,
    max_results: int = 50
) -> Dict:
    """Get ranked rare disease acquisition targets with intelligent filtering.

    Args:
        therapeutic_focus: 'ultra_rare_metabolic', 'neuromuscular', 'gene_therapy', 'oncology_rare', 'any'
        min_programs: Minimum programs (default: 1)
        max_programs: Maximum programs (default: 8)
        exclude_academic: Exclude universities/medical centers (default: True)
        exclude_government: Exclude NIH/NCI (default: True)
        exclude_cro: Exclude CROs (default: True)
        prefer_phase3: Adaptive phase strategy (default: True)
        max_results: Top N targets (default: 50)

    Returns:
        dict: query_strategy, filtering_summary, top_targets, summary
    """

    # Get query
    query = THERAPEUTIC_QUERIES.get(therapeutic_focus, THERAPEUTIC_QUERIES['any'])

    # Adaptive phase strategy
    phase_expansion_reason = None
    phases_included = 'PHASE3 only'

    if prefer_phase3:
        # Try Phase 3 first
        trials_phase3 = query_ct_gov_with_pagination(query, 'PHASE3')
        sponsor_trials_phase3, _ = filter_and_aggregate_sponsors(
            trials_phase3,
            exclude_academic,
            exclude_government,
            exclude_cro,
            min_programs,
            max_programs
        )

        # Check if expansion needed
        if len(sponsor_trials_phase3) < 20:
            phase_expansion_reason = f'Phase 3 only: {len(sponsor_trials_phase3)} companies (threshold: 20)'
            print(f"\nExpanding to Phase 2: {phase_expansion_reason}")

            # Query both phases separately and combine
            trials_phase2 = query_ct_gov_with_pagination(query, 'PHASE2')
            trials_combined = trials_phase3 + trials_phase2

            sponsor_trials, filtering_stats = filter_and_aggregate_sponsors(
                trials_combined,
                exclude_academic,
                exclude_government,
                exclude_cro,
                min_programs,
                max_programs
            )
            phases_included = 'PHASE2+PHASE3'
        else:
            sponsor_trials = sponsor_trials_phase3
            filtering_stats = {
                'total_trials': len(trials_phase3),
                'companies_before_filtering': len({t.get('sponsor') for t in trials_phase3}),
                'excluded_academic': 0,
                'excluded_government': 0,
                'excluded_large_pharma': 0,
                'excluded_cro': 0,
                'excluded_small_portfolio': 0,
                'companies_after_filtering': len(sponsor_trials)
            }
            phase_expansion_reason = f'Phase 3 sufficient ({len(sponsor_trials)} companies ≥ 20)'
    else:
        # Query both phases separately and combine
        trials_phase2 = query_ct_gov_with_pagination(query, 'PHASE2')
        trials_phase3 = query_ct_gov_with_pagination(query, 'PHASE3')
        trials = trials_phase2 + trials_phase3

        sponsor_trials, filtering_stats = filter_and_aggregate_sponsors(
            trials,
            exclude_academic,
            exclude_government,
            exclude_cro,
            min_programs,
            max_programs
        )
        phases_included = 'PHASE2+PHASE3'
        phase_expansion_reason = 'Phase 2+3 from start'

    # Rank targets
    top_targets = rank_acquisition_targets(sponsor_trials, max_results)

    # Generate summary
    summary = f"""# Rare Disease Acquisition Targets

## Query Strategy
- Therapeutic Focus: {therapeutic_focus}
- Phases: {phases_included}
- Strategy: {phase_expansion_reason}

## Filtering
- Total Trials: {filtering_stats['total_trials']:,}
- Before Filtering: {filtering_stats['companies_before_filtering']:,} companies
- Excluded Academic: {filtering_stats['excluded_academic']:,}
- Excluded Government: {filtering_stats['excluded_government']:,}
- Excluded Large (>{max_programs}): {filtering_stats['excluded_large_pharma']:,}
- Excluded CRO: {filtering_stats['excluded_cro']:,}
- Excluded Small (<{min_programs}): {filtering_stats['excluded_small_portfolio']:,}
- After Filtering: {filtering_stats['companies_after_filtering']:,} companies

## Top 10 Targets

"""

    for target in top_targets[:10]:
        summary += f"""### {target['rank']}. {target['sponsor']} (Score: {target['acquisition_score']})
- Portfolio: {target['total_programs']} programs ({target['phase3_count']} P3, {target['phase2_count']} P2)
- Active: {target['recruiting_count']} recruiting
"""
        if target['lead_asset']:
            lead = target['lead_asset']
            summary += f"""- Lead: {lead['intervention']} - {lead['condition']} ({lead['phase']})
  NCT: {lead['nct_id']}
"""
        summary += "\n"

    return {
        'query_strategy': {
            'therapeutic_focus': therapeutic_focus,
            'phases_included': phases_included,
            'phase_expansion_reason': phase_expansion_reason
        },
        'filtering_summary': filtering_stats,
        'top_targets': top_targets,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_rare_disease_acquisition_targets(
        therapeutic_focus='ultra_rare_metabolic',
        prefer_phase3=True,
        max_results=30
    )

    print(result['summary'])
    print(f"\n✓ Found {len(result['top_targets'])} targets")
    print(f"✓ Strategy: {result['query_strategy']['phase_expansion_reason']}")
