import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_cart_bcell_malignancies_trials():
    """Get all recruiting CAR-T cell therapy trials for B-cell malignancies.

    Returns:
        dict: Contains total_count, trials, and summary statistics
    """
    all_trials = []
    page_token = None

    # Search for CAR-T trials
    while True:
        params = {
            "term": "CAR-T OR CAR T-cell OR chimeric antigen receptor",
            "status": "recruiting",
            "pageSize": 100
        }

        if page_token:
            params["pageToken"] = page_token

        result = search(**params)

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:
            trial = {}

            # Extract NCT ID
            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial['nct_id'] = nct_match.group()

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()

            # Extract condition
            condition_match = re.search(r'\*\*Condition:\*\*\s*(.+?)(?:\n|$)', block)
            if condition_match:
                condition = condition_match.group(1).strip()
                trial['condition'] = condition

                # Filter for B-cell malignancies
                if any(term in condition.upper() for term in [
                    'LYMPHOMA', 'LEUKEMIA', 'MYELOMA', 'B-CELL', 'B CELL'
                ]):
                    trial['is_bcell'] = True
                else:
                    trial['is_bcell'] = False
            else:
                trial['is_bcell'] = False

            if trial and trial.get('is_bcell'):
                all_trials.append(trial)

        # Check for next page
        token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if token_match:
            page_token = token_match.group(1)
        else:
            break

    # Analyze targets
    target_counts = {'CD19': 0, 'CD22': 0, 'BCMA': 0, 'CD20': 0, 'Other': 0}
    phase_counts = {}

    for trial in all_trials:
        title = trial.get('title', '').upper()

        # Target identification
        if 'CD19' in title:
            target_counts['CD19'] += 1
        if 'CD22' in title:
            target_counts['CD22'] += 1
        if 'BCMA' in title:
            target_counts['BCMA'] += 1
        if 'CD20' in title:
            target_counts['CD20'] += 1

        # Phase distribution
        phase = trial.get('phase', 'Unknown')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    total_count = len(all_trials)

    summary = f"""
Total CAR-T trials for B-cell malignancies: {total_count}

Target Distribution:
"""
    for target, count in sorted(target_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = (count / total_count) * 100 if total_count > 0 else 0
            summary += f"- {target}: {count} trials ({pct:.1f}%)\n"

    summary += "\nPhase Distribution:\n"
    for phase, count in sorted(phase_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_count) * 100 if total_count > 0 else 0
        summary += f"- {phase}: {count} trials ({pct:.1f}%)\n"

    return {
        'total_count': total_count,
        'trials': all_trials,
        'target_distribution': target_counts,
        'phase_distribution': phase_counts,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_cart_bcell_malignancies_trials()
    print(result['summary'])

    if result['total_count'] > 0:
        print("\nSample trials (first 5):")
        for i, trial in enumerate(result['trials'][:5], 1):
            print(f"\n{i}. {trial.get('nct_id', 'N/A')}")
            print(f"   Title: {trial.get('title', 'N/A')[:100]}...")
            print(f"   Phase: {trial.get('phase', 'N/A')}")
            print(f"   Condition: {trial.get('condition', 'N/A')[:80]}...")
