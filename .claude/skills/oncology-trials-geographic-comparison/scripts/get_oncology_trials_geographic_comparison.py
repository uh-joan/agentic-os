import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re
from collections import defaultdict

def get_oncology_trials_geographic_comparison():
    """Compare Phase 3 oncology trials recruiting in US vs. China.

    Analyzes geographic distribution, therapeutic areas, and sponsor patterns
    for Phase 3 oncology trials currently recruiting in United States vs. China.

    Returns:
        dict: Contains comparison data and strategic insights
    """

    # Query 1: US Phase 3 Oncology Recruiting trials
    print("Querying US Phase 3 Oncology trials (RECRUITING)...")
    us_trials = []
    us_page_token = None
    us_query_count = 0

    while True:
        us_query_count += 1
        result = search(
            term="cancer OR oncology OR tumor OR carcinoma",
            phase="PHASE3",
            recruitmentStatus="RECRUITING",
            location="United States",
            pageSize=1000,
            pageToken=us_page_token
        )

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:  # Skip first empty split
            trial_data = {}

            # Extract NCT ID from next occurrence
            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial_data['nct_id'] = nct_match.group(0)

            # Extract fields
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if title_match:
                trial_data['title'] = title_match.group(1).strip()

            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', block)
            if status_match:
                trial_data['status'] = status_match.group(1).strip()

            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if conditions_match:
                trial_data['conditions'] = conditions_match.group(1).strip()

            sponsor_match = re.search(r'\*\*Sponsor:\*\*\s*(.+?)(?=\n|$)', block)
            if sponsor_match:
                trial_data['sponsor'] = sponsor_match.group(1).strip()

            interventions_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if interventions_match:
                trial_data['interventions'] = interventions_match.group(1).strip()

            if trial_data.get('nct_id'):
                us_trials.append(trial_data)

        # Check for next page
        next_page_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_page_match and us_query_count < 10:  # Safety limit
            us_page_token = next_page_match.group(1)
            print(f"  Page {us_query_count}: {len(trial_blocks)-1} trials, fetching next page...")
        else:
            break

    print(f"US query complete: {len(us_trials)} trials found in {us_query_count} pages\n")

    # Query 2: China Phase 3 Oncology Recruiting trials
    print("Querying China Phase 3 Oncology trials (RECRUITING)...")
    china_trials = []
    china_page_token = None
    china_query_count = 0

    while True:
        china_query_count += 1
        result = search(
            term="cancer OR oncology OR tumor OR carcinoma",
            phase="PHASE3",
            recruitmentStatus="RECRUITING",
            location="China",
            pageSize=1000,
            pageToken=china_page_token
        )

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:
            trial_data = {}

            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial_data['nct_id'] = nct_match.group(0)

            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if title_match:
                trial_data['title'] = title_match.group(1).strip()

            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', block)
            if status_match:
                trial_data['status'] = status_match.group(1).strip()

            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if conditions_match:
                trial_data['conditions'] = conditions_match.group(1).strip()

            sponsor_match = re.search(r'\*\*Sponsor:\*\*\s*(.+?)(?=\n|$)', block)
            if sponsor_match:
                trial_data['sponsor'] = sponsor_match.group(1).strip()

            interventions_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            if interventions_match:
                trial_data['interventions'] = interventions_match.group(1).strip()

            if trial_data.get('nct_id'):
                china_trials.append(trial_data)

        # Check for next page
        next_page_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_page_match and china_query_count < 10:
            china_page_token = next_page_match.group(1)
            print(f"  Page {china_query_count}: {len(trial_blocks)-1} trials, fetching next page...")
        else:
            break

    print(f"China query complete: {len(china_trials)} trials found in {china_query_count} pages\n")

    # Analyze data
    us_conditions = defaultdict(int)
    china_conditions = defaultdict(int)
    us_sponsors = defaultdict(int)
    china_sponsors = defaultdict(int)

    # Parse conditions and sponsors
    for trial in us_trials:
        conditions = trial.get('conditions', '')
        for condition in re.split(r'[,;]', conditions):
            condition = condition.strip()
            if condition:
                us_conditions[condition] += 1

        sponsor = trial.get('sponsor', 'Unknown')
        us_sponsors[sponsor] += 1

    for trial in china_trials:
        conditions = trial.get('conditions', '')
        for condition in re.split(r'[,;]', conditions):
            condition = condition.strip()
            if condition:
                china_conditions[condition] += 1

        sponsor = trial.get('sponsor', 'Unknown')
        china_sponsors[sponsor] += 1

    # Top conditions
    us_top_conditions = sorted(us_conditions.items(), key=lambda x: x[1], reverse=True)[:10]
    china_top_conditions = sorted(china_conditions.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top sponsors
    us_top_sponsors = sorted(us_sponsors.items(), key=lambda x: x[1], reverse=True)[:10]
    china_top_sponsors = sorted(china_sponsors.items(), key=lambda x: x[1], reverse=True)[:10]

    # Build summary
    summary = f"""
=== PHASE 3 ONCOLOGY TRIALS GEOGRAPHIC COMPARISON ===

OVERALL COMPARISON:
  United States: {len(us_trials)} recruiting trials
  China:         {len(china_trials)} recruiting trials
  Ratio:         {len(us_trials)/len(china_trials):.2f}:1 (US:China)

TOP CONDITIONS - UNITED STATES:
"""
    for condition, count in us_top_conditions:
        summary += f"  • {condition}: {count} trials\n"

    summary += f"\nTOP CONDITIONS - CHINA:\n"
    for condition, count in china_top_conditions:
        summary += f"  • {condition}: {count} trials\n"

    summary += f"\nTOP SPONSORS - UNITED STATES:\n"
    for sponsor, count in us_top_sponsors[:5]:
        summary += f"  • {sponsor}: {count} trials\n"

    summary += f"\nTOP SPONSORS - CHINA:\n"
    for sponsor, count in china_top_sponsors[:5]:
        summary += f"  • {sponsor}: {count} trials\n"

    summary += f"""
STRATEGIC INSIGHTS:
  • Trial Volume: {'US dominates' if len(us_trials) > len(china_trials) else 'China leads'} in Phase 3 oncology recruiting trials
  • Cost Advantage: China offers {100*(1 - len(china_trials)/max(len(us_trials), 1)):.0f}% {'fewer' if len(china_trials) < len(us_trials) else 'more'} competing trials
  • Sponsor Mix: {'US has more diverse sponsors' if len(us_sponsors) > len(china_sponsors) else 'China has more diverse sponsors'}
  • CRO Strategy: Consider dual-region trials for regulatory harmonization

DATA SOURCES:
  • ClinicalTrials.gov Phase 3 Oncology trials
  • Recruitment Status: RECRUITING only
  • Query Date: 2025-11-22
"""

    return {
        'total_us': len(us_trials),
        'total_china': len(china_trials),
        'us_trials': us_trials,
        'china_trials': china_trials,
        'us_top_conditions': us_top_conditions,
        'china_top_conditions': china_top_conditions,
        'us_top_sponsors': us_top_sponsors,
        'china_top_sponsors': china_top_sponsors,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_oncology_trials_geographic_comparison()
    print(result['summary'])
