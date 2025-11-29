import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_trials_by_phase_and_design(
    therapeutic_area,
    phase,
    allocation=None,
    intervention_model=None,
    masking=None,
    primary_purpose=None
):
    """Get clinical trials filtered by phase and study design characteristics.

    Essential for regulatory experts assessing impact of new design requirements.
    Supports filtering by phase AND multiple design parameters to find trials
    matching specific methodological criteria.

    Args:
        therapeutic_area (str): Disease/condition (e.g., "diabetes", "oncology")
        phase (str): Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3", "PHASE4")
        allocation (str, optional): Allocation type (e.g., "randomized", "nonrandomized", "na")
        intervention_model (str, optional): Study design (e.g., "parallel", "crossover", "factorial", "sequential", "single")
        masking (str, optional): Blinding level (e.g., "none", "single", "double", "triple", "quadruple")
        primary_purpose (str, optional): Study purpose (e.g., "treatment", "prevention", "diagnostic", "supportive")

    Returns:
        dict: Contains total_count, trials_summary, design_breakdown, and matching_trials

    Examples:
        # Find Phase 3 diabetes trials using randomized parallel design
        result = get_trials_by_phase_and_design(
            therapeutic_area="diabetes",
            phase="PHASE3",
            allocation="randomized",
            intervention_model="parallel"
        )

        # Find Phase 2 oncology trials using single-arm design
        result = get_trials_by_phase_and_design(
            therapeutic_area="oncology",
            phase="PHASE2",
            intervention_model="single"
        )

        # Find cardiovascular trials WITHOUT double-blind masking
        result = get_trials_by_phase_and_design(
            therapeutic_area="cardiovascular",
            phase="PHASE3",
            masking="none"
        )
    """

    # Build query parameters
    params = {
        "condition": therapeutic_area,
        "phase": phase,
        "pageSize": 5000
    }

    # Add optional design filters if specified
    if allocation:
        params["allocation"] = allocation
    if intervention_model:
        # CT.gov uses "assignment" parameter for intervention model
        params["assignment"] = intervention_model
    if masking:
        params["masking"] = masking
    if primary_purpose:
        params["purpose"] = primary_purpose

    # Collect all trials with pagination
    all_trials = []
    page_token = None

    while True:
        if page_token:
            params["pageToken"] = page_token

        result = search(**params)

        if not result or not isinstance(result, str):
            break

        # Split trials by NCT ID headers
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        # Process each trial block (skip first empty element)
        for block in trial_blocks[1:]:
            trial_data = {}

            # Extract NCT ID from the block (it's in the first line after split)
            nct_match = re.search(r'NCT\d{8}', result[result.find(block) - 20:result.find(block)])
            if nct_match:
                trial_data['nct_id'] = nct_match.group()

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
            if title_match:
                trial_data['title'] = title_match.group(1).strip()

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
            if phase_match:
                trial_data['phase'] = phase_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', block)
            if status_match:
                trial_data['status'] = status_match.group(1).strip()

            # Extract design characteristics
            allocation_match = re.search(r'\*\*Allocation:\*\*\s*(.+?)(?:\n|$)', block)
            if allocation_match:
                trial_data['allocation'] = allocation_match.group(1).strip()

            intervention_match = re.search(r'\*\*Intervention Model:\*\*\s*(.+?)(?:\n|$)', block)
            if intervention_match:
                trial_data['intervention_model'] = intervention_match.group(1).strip()

            masking_match = re.search(r'\*\*Masking:\*\*\s*(.+?)(?:\n|$)', block)
            if masking_match:
                trial_data['masking'] = masking_match.group(1).strip()

            purpose_match = re.search(r'\*\*Primary Purpose:\*\*\s*(.+?)(?:\n|$)', block)
            if purpose_match:
                trial_data['primary_purpose'] = purpose_match.group(1).strip()

            if trial_data.get('nct_id'):
                all_trials.append(trial_data)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1)
        else:
            break

    # Generate design breakdown
    design_breakdown = {
        'allocation': {},
        'intervention_model': {},
        'masking': {},
        'primary_purpose': {}
    }

    for trial in all_trials:
        # Count allocation types
        alloc = trial.get('allocation', 'Not Specified')
        design_breakdown['allocation'][alloc] = design_breakdown['allocation'].get(alloc, 0) + 1

        # Count intervention models
        model = trial.get('intervention_model', 'Not Specified')
        design_breakdown['intervention_model'][model] = design_breakdown['intervention_model'].get(model, 0) + 1

        # Count masking levels
        mask = trial.get('masking', 'Not Specified')
        design_breakdown['masking'][mask] = design_breakdown['masking'].get(mask, 0) + 1

        # Count primary purposes
        purpose = trial.get('primary_purpose', 'Not Specified')
        design_breakdown['primary_purpose'][purpose] = design_breakdown['primary_purpose'].get(purpose, 0) + 1

    # Sort breakdowns by frequency
    for category in design_breakdown:
        design_breakdown[category] = dict(sorted(
            design_breakdown[category].items(),
            key=lambda x: x[1],
            reverse=True
        ))

    # Generate summary
    total_count = len(all_trials)

    # Build filter description
    filters_applied = [f"Phase: {phase}", f"Condition: {therapeutic_area}"]
    if allocation:
        filters_applied.append(f"Allocation: {allocation}")
    if intervention_model:
        filters_applied.append(f"Intervention Model: {intervention_model}")
    if masking:
        filters_applied.append(f"Masking: {masking}")
    if primary_purpose:
        filters_applied.append(f"Primary Purpose: {primary_purpose}")

    summary_parts = [
        f"## Trials by Phase and Design: {therapeutic_area.title()}",
        f"\n**Filters Applied**: {', '.join(filters_applied)}",
        f"\n**Total Trials Found**: {total_count}",
        "\n### Design Breakdown",
        "\n**Allocation:**"
    ]

    for alloc, count in list(design_breakdown['allocation'].items())[:5]:
        summary_parts.append(f"  - {alloc}: {count} ({count/total_count*100:.1f}%)")

    summary_parts.append("\n**Intervention Model:**")
    for model, count in list(design_breakdown['intervention_model'].items())[:5]:
        summary_parts.append(f"  - {model}: {count} ({count/total_count*100:.1f}%)")

    summary_parts.append("\n**Masking:**")
    for mask, count in list(design_breakdown['masking'].items())[:5]:
        summary_parts.append(f"  - {mask}: {count} ({count/total_count*100:.1f}%)")

    # Status breakdown
    status_counts = {}
    for trial in all_trials:
        status = trial.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    summary_parts.append("\n### Status Distribution")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        summary_parts.append(f"  - {status}: {count} ({count/total_count*100:.1f}%)")

    trials_summary = '\n'.join(summary_parts)

    return {
        'total_count': total_count,
        'trials_summary': trials_summary,
        'design_breakdown': design_breakdown,
        'matching_trials': all_trials
    }

if __name__ == "__main__":
    # Test case: Phase 3 diabetes trials with randomized parallel design
    print("Testing: Phase 3 diabetes trials with randomized parallel design...")
    result = get_trials_by_phase_and_design(
        therapeutic_area="diabetes",
        phase="PHASE3",
        allocation="randomized",
        intervention_model="parallel"
    )

    print(f"\nTotal trials found: {result['total_count']}")
    print("\n" + result['trials_summary'])

    # Show a few examples
    print("\n### Sample Matching Trials:")
    for trial in result['matching_trials'][:3]:
        print(f"\n**{trial.get('nct_id')}**: {trial.get('title', 'N/A')[:80]}...")
        print(f"  Phase: {trial.get('phase')}, Status: {trial.get('status')}")
        print(f"  Design: {trial.get('allocation')} {trial.get('intervention_model')}, Masking: {trial.get('masking')}")
