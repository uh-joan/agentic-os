import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_alzheimers_all_trials():
    """Get all Alzheimer's disease clinical trials across all phases and mechanisms.

    Collects comprehensive data on Alzheimer's trials including:
    - All clinical phases (Early Phase 1 through Phase 4)
    - All recruitment statuses
    - Categorization by mechanism of action

    Returns:
        dict: Contains total_count, trials_by_phase, trials_by_status,
              mechanism_categories, and summary
    """

    # Collect all Alzheimer's trials with pagination
    print("Collecting Alzheimer's disease clinical trials...")

    all_trials = []
    page_size = 1000
    page = 1

    while True:
        try:
            result = search(
                condition="Alzheimer Disease",
                pageSize=page_size,
                pageToken=None if page == 1 else f"page_{page}"
            )

            # Parse markdown response
            if not result or len(result) < 100:
                break

            # Extract NCT IDs and basic info
            nct_pattern = r'NCT\d{8}'
            nct_ids = re.findall(nct_pattern, result)

            if not nct_ids:
                break

            all_trials.extend(nct_ids)

            # Check if there are more pages (markdown response contains pagination info)
            if "Next page" not in result and len(nct_ids) < page_size:
                break

            page += 1

        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break

    # Get detailed data for phase and status analysis
    # Use search with different filters to get breakdowns

    trials_by_phase = {}
    phases = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"]

    for phase in phases:
        try:
            result = search(
                condition="Alzheimer Disease",
                phase=phase,
                pageSize=1
            )
            # Extract count from markdown
            count_match = re.search(r'(\d+)\s+stud(?:y|ies)', result)
            count = int(count_match.group(1)) if count_match else 0
            trials_by_phase[phase] = count
        except:
            trials_by_phase[phase] = 0

    trials_by_status = {}
    statuses = [
        "recruiting",
        "not_yet_recruiting",
        "active_not_recruiting",
        "completed",
        "terminated",
        "suspended",
        "withdrawn"
    ]

    for status in statuses:
        try:
            result = search(
                condition="Alzheimer Disease",
                status=status,
                pageSize=1
            )
            count_match = re.search(r'(\d+)\s+stud(?:y|ies)', result)
            count = int(count_match.group(1)) if count_match else 0
            trials_by_status[status] = count
        except:
            trials_by_status[status] = 0

    # Mechanism categorization through intervention searches
    mechanism_categories = {}

    mechanisms = {
        "Anti-amyloid antibodies": ["aducanumab", "lecanemab", "donanemab", "gantenerumab", "solanezumab"],
        "Tau inhibitors": ["tau", "MAPT", "microtubule"],
        "BACE inhibitors": ["BACE", "beta-secretase"],
        "Gamma-secretase modulators": ["gamma-secretase", "presenilin"],
        "Neuroinflammation": ["TREM2", "complement", "microglia", "neuroinflammation"],
        "Synaptic plasticity": ["BDNF", "synaptic", "neurotrophin"],
        "Metabolic interventions": ["APOE", "lipid", "cholesterol", "metabolism"],
        "Neuroprotection": ["neuroprotection", "oxidative stress", "mitochondrial"]
    }

    for mechanism, terms in mechanisms.items():
        total = 0
        for term in terms:
            try:
                result = search(
                    condition="Alzheimer Disease",
                    intervention=term,
                    pageSize=1
                )
                count_match = re.search(r'(\d+)\s+stud(?:y|ies)', result)
                count = int(count_match.group(1)) if count_match else 0
                total += count
            except:
                continue
        mechanism_categories[mechanism] = total

    total_count = len(set(all_trials))

    # Create summary
    summary_lines = ["\n=== Alzheimer's Disease Clinical Trials Landscape ===\n"]
    summary_lines.append(f"Total unique trials: {total_count}\n")

    summary_lines.append("TRIALS BY PHASE:")
    for phase, count in trials_by_phase.items():
        pct = (count / sum(trials_by_phase.values()) * 100) if sum(trials_by_phase.values()) > 0 else 0
        summary_lines.append(f"  {phase}: {count} ({pct:.1f}%)")

    summary_lines.append("\nTRIALS BY STATUS:")
    for status, count in sorted(trials_by_status.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            summary_lines.append(f"  {status}: {count}")

    summary_lines.append("\nTRIALS BY MECHANISM (with potential overlap):")
    for mechanism, count in sorted(mechanism_categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            summary_lines.append(f"  {mechanism}: {count}")

    summary = "\n".join(summary_lines)

    return {
        'total_count': total_count,
        'trials_by_phase': trials_by_phase,
        'trials_by_status': trials_by_status,
        'mechanism_categories': mechanism_categories,
        'summary': summary
    }

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    result = get_alzheimers_all_trials()
    print(result['summary'])
    print(f"\nCollected data on {result['total_count']} unique Alzheimer's disease trials")
