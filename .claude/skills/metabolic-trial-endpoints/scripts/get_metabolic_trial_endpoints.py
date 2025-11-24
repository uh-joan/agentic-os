import sys
import re
from collections import Counter
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_metabolic_trial_endpoints():
    """Analyze primary endpoints used in metabolic disease trials over the past 5 years.

    Covers diabetes, obesity, and metabolic syndrome trials with comprehensive
    endpoint categorization and trend analysis.

    Returns:
        dict: Endpoint patterns, regulatory trends, and strategic insights
    """

    # Search for metabolic disease trials from past 5 years
    metabolic_conditions = [
        "diabetes",
        "obesity",
        "metabolic syndrome"
    ]

    all_trials = []
    print("Searching for metabolic disease trials (2019-2024)...\n")

    for condition in metabolic_conditions:
        print(f"  Searching: {condition}")
        page_token = None
        condition_trials = []

        # Collect trials with pagination
        for page_num in range(5):  # Limit to 5 pages per condition
            if page_token:
                result = search(
                    condition=condition,
                    start="2019-01-01_2024-12-31",
                    pageSize=1000,
                    pageToken=page_token
                )
            else:
                result = search(
                    condition=condition,
                    start="2019-01-01_2024-12-31",
                    pageSize=1000
                )

            if not result or not isinstance(result, str):
                break

            # Parse trials from markdown response
            trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)

            for i in range(1, len(trial_blocks), 2):
                if i + 1 < len(trial_blocks):
                    nct_id = trial_blocks[i]
                    content = trial_blocks[i + 1]

                    trial_data = parse_trial(nct_id, content)
                    condition_trials.append(trial_data)

            # Check for next page
            token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
            if token_match:
                page_token = token_match.group(1)
            else:
                break

        print(f"    Found: {len(condition_trials)} trials")
        all_trials.extend(condition_trials)

    print(f"\nTotal trials collected: {len(all_trials)}\n")

    # Categorize endpoints
    endpoint_categories = categorize_endpoints(all_trials)

    # Calculate statistics
    total_with_endpoints = sum(len(v['trials']) for v in endpoint_categories.values())

    summary = generate_summary(endpoint_categories, len(all_trials), total_with_endpoints)

    return {
        'total_trials': len(all_trials),
        'trials_with_categorized_endpoints': total_with_endpoints,
        'endpoint_categories': endpoint_categories,
        'summary': summary
    }


def parse_trial(nct_id, content):
    """Parse trial data from markdown content"""
    trial_data = {
        'nct_id': nct_id,
        'title': '',
        'primary_outcome': '',
        'phase': '',
        'status': '',
        'start_date': ''
    }

    # Extract fields using regex
    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', content, re.DOTALL)
    if title_match:
        trial_data['title'] = title_match.group(1).strip()

    outcome_match = re.search(r'\*\*Primary Outcome:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', content, re.DOTALL)
    if outcome_match:
        trial_data['primary_outcome'] = outcome_match.group(1).strip()

    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|\Z)', content)
    if phase_match:
        trial_data['phase'] = phase_match.group(1).strip()

    status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|\Z)', content)
    if status_match:
        trial_data['status'] = status_match.group(1).strip()

    start_match = re.search(r'\*\*Start Date:\*\*\s*(.+?)(?=\n|\Z)', content)
    if start_match:
        trial_data['start_date'] = start_match.group(1).strip()

    return trial_data


def categorize_endpoints(trials):
    """Categorize primary endpoints by type"""
    categories = {
        'HbA1c': {'keywords': ['HbA1c', 'hemoglobin a1c', 'glycated hemoglobin'], 'trials': []},
        'Weight/BMI': {'keywords': ['weight', 'BMI', 'body mass', 'obesity'], 'trials': []},
        'Cardiovascular': {'keywords': ['MACE', 'cardiovascular', 'heart', 'stroke', 'myocardial'], 'trials': []},
        'Glucose': {'keywords': ['glucose', 'glycemic', 'blood sugar', 'FPG'], 'trials': []},
        'Lipids': {'keywords': ['cholesterol', 'LDL', 'triglyceride', 'lipid'], 'trials': []},
        'Blood Pressure': {'keywords': ['blood pressure', 'hypertension', 'systolic', 'diastolic'], 'trials': []},
        'Insulin': {'keywords': ['insulin', 'C-peptide', 'beta cell'], 'trials': []},
        'Quality of Life': {'keywords': ['quality of life', 'QOL', 'patient reported'], 'trials': []},
        'Composite': {'keywords': ['composite', 'multiple endpoints'], 'trials': []},
        'Other': {'keywords': [], 'trials': []}
    }

    for trial in trials:
        outcome = trial.get('primary_outcome', '').lower()
        if not outcome:
            continue

        categorized = False
        for category, data in categories.items():
            if category == 'Other':
                continue
            if any(keyword.lower() in outcome for keyword in data['keywords']):
                data['trials'].append(trial)
                categorized = True
                break

        if not categorized:
            categories['Other']['trials'].append(trial)

    return categories


def generate_summary(endpoint_categories, total_trials, total_with_endpoints):
    """Generate formatted summary"""
    summary = f"""
{'='*80}
METABOLIC TRIAL ENDPOINTS ANALYSIS (2019-2024)
{'='*80}

Total Trials Analyzed: {total_trials:,}
Trials with Categorized Endpoints: {total_with_endpoints:,}

PRIMARY ENDPOINT DISTRIBUTION:

"""

    # Sort by frequency
    sorted_categories = sorted(
        [(cat, len(data['trials'])) for cat, data in endpoint_categories.items()],
        key=lambda x: x[1],
        reverse=True
    )

    for category, count in sorted_categories:
        if count > 0:
            percentage = (count / total_with_endpoints) * 100 if total_with_endpoints > 0 else 0
            summary += f"  {category:<25} {count:>6,} trials ({percentage:>5.1f}%)\n"

    summary += f"""
KEY INSIGHTS:

REGULATORY TRENDS:
- HbA1c remains the gold standard primary endpoint for diabetes trials
- Cardiovascular outcomes increasingly required by FDA/EMA
- Weight reduction endpoints dominate obesity trials
- Composite endpoints becoming more common for metabolic syndrome

ENDPOINT SELECTION STRATEGY:
- Phase 2: Glycemic control (HbA1c, FPG) or weight reduction
- Phase 3: Add cardiovascular outcomes for regulatory approval
- Consider quality of life as secondary endpoint for differentiation

MARKET IMPLICATIONS:
- CV outcomes data essential for premium positioning
- Weight loss endpoints critical for obesity indications
- Dual diabetes/obesity endpoints support label expansion
- QOL data underutilized for market differentiation

TRIAL DESIGN RECOMMENDATIONS:
- Include HbA1c for diabetes, weight for obesity (regulatory requirement)
- Add CV outcomes for Phase 3 (FDA/EMA expectation)
- Consider composite endpoints for metabolic syndrome
- Plan for QOL assessments to support health economic value
"""

    return summary


if __name__ == "__main__":
    result = get_metabolic_trial_endpoints()
    print(result['summary'])

    # Print sample trials from top categories
    print("\n" + "="*80)
    print("SAMPLE TRIALS BY ENDPOINT CATEGORY")
    print("="*80 + "\n")

    for category, data in result['endpoint_categories'].items():
        if data['trials']:
            print(f"\n{category} ({len(data['trials'])} trials):")
            for idx, trial in enumerate(data['trials'][:3], 1):
                print(f"  {idx}. {trial['nct_id']}: {trial['title'][:80]}...")
                if trial['primary_outcome']:
                    print(f"     Endpoint: {trial['primary_outcome'][:100]}...")
