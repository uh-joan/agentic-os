import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search, get_study

def get_diabetes_drugs_stopped_safety():
    """Get diabetes clinical trials that stopped due to safety concerns.

    Uses complexQuery with AREA[WhyStopped] field to search for safety-related
    stop reasons. Extracts actual "Why Stopped" text from each trial for accurate
    severity scoring and transparency.

    Returns:
        dict: Contains:
            - total_count: Total number of safety-stopped trials
            - trials: List of trial details with 'why_stopped' field
            - categorizations: Breakdown by safety reason, phase, diabetes type
            - notable_drugs: Scored drug failures with actual safety reasons
            - summary: Human-readable summary with "Why Stopped" examples
    """

    print("Searching for diabetes trials stopped due to safety concerns...")
    print("(Using AREA[WhyStopped] field with safety keywords)\n")

    # Safety keywords to search for in "Why Stopped" field
    # Map keywords to severity scores
    safety_keywords = {
        'death': 10, 'mortality': 10,
        'toxicity': 8, 'toxic': 8,
        'adverse': 5, 'SAE': 5,
        'tolerability': 3, 'side effect': 3,
        'safety': 1, 'harm': 1, 'hypoglycemia': 1
    }

    all_nct_ids = set()
    nct_to_keywords = {}  # Track which keywords matched each trial

    # Search for each safety keyword in Why Stopped field
    for i, (keyword, severity_score) in enumerate(safety_keywords.items(), 1):
        print(f"  [{i}/{len(safety_keywords)}] Searching for '{keyword}' in Why Stopped...")
        page_num = 1
        next_token = None
        keyword_count = 0

        while True:
            # Use complexQuery to search WhyStopped field
            query = f'diabetes AND (AREA[OverallStatus]TERMINATED OR AREA[OverallStatus]WITHDRAWN OR AREA[OverallStatus]SUSPENDED) AND AREA[WhyStopped]{keyword}'

            if next_token:
                result = search(
                    complexQuery=query,
                    pageSize=1000,
                    pageToken=next_token
                )
            else:
                result = search(
                    complexQuery=query,
                    pageSize=1000
                )

            if not result or not isinstance(result, str):
                break

            # Extract NCT IDs
            page_nct_ids = set(re.findall(r'NCT\d{8}', result))

            # Track which keyword matched each trial
            for nct_id in page_nct_ids:
                if nct_id not in nct_to_keywords:
                    nct_to_keywords[nct_id] = []
                nct_to_keywords[nct_id].append((keyword, severity_score))

            new_ids = page_nct_ids - all_nct_ids
            all_nct_ids.update(new_ids)
            keyword_count += len(new_ids)

            # Progress for multi-page results
            if page_num > 1 or len(page_nct_ids) == 1000:
                print(f"    Page {page_num}: {len(page_nct_ids)} trials on page, {keyword_count} new (total: {len(all_nct_ids)})")

            # Check for next page
            next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
            if next_token_match:
                next_token = next_token_match.group(1)
                page_num += 1
            else:
                break

        if keyword_count > 0:
            print(f"    ✓ Found {keyword_count} new trials for '{keyword}'")

    nct_ids = list(all_nct_ids)
    total_count = len(nct_ids)
    print(f"\n  Total unique trials found: {total_count}")

    # Fetch detailed info for all trials
    print(f"\nFetching detailed info for all {total_count} trials...")
    trials = []
    error_count = 0

    for i, nct_id in enumerate(nct_ids, 1):
        if i % 50 == 0 or i == total_count:
            print(f"  Progress: {i}/{total_count} processed")

        try:
            trial_detail = get_study(nctId=nct_id)

            if not trial_detail or not isinstance(trial_detail, str):
                error_count += 1
                continue

            trial_data = parse_trial_detail(nct_id, trial_detail)
            if trial_data:
                trials.append(trial_data)

        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"    Error: {nct_id}: {str(e)[:60]}")
            continue

    print(f"\nCompleted: {len(trials)} trials retrieved ({error_count} errors)")

    # Categorize trials
    categorizations = categorize_trials(trials)

    # Score notable drugs
    print("\nAnalyzing notable drug failures...")
    scored_drugs = score_notable_drugs(trials, nct_to_keywords)

    # Generate summary
    summary = generate_summary(trials, categorizations, total_count, scored_drugs)

    return {
        'total_count': total_count,
        'trials': trials,
        'categorizations': categorizations,
        'notable_drugs': scored_drugs,
        'nct_to_keywords': nct_to_keywords,  # Mapping of NCT IDs to "Why Stopped" keywords
        'summary': summary
    }


def parse_trial_detail(nct_id, trial_detail):
    """Parse detailed trial information."""

    def extract_field(pattern, text, default="Not specified"):
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else default

    title = extract_field(r'\*\*(?:Study )?Title:?\*\*\s*(.+?)(?=\n\*\*|\n##|$)', trial_detail)
    status = extract_field(r'\*\*(?:Overall )?Status:?\*\*\s*(.+?)(?=\n|$)', trial_detail)
    why_stopped = extract_field(r'\*\*Why Stopped:?\*\*\s*(.+?)(?=\n|$)', trial_detail)
    phase = extract_field(r'\*\*Phase:?\*\*\s*(.+?)(?=\n|$)', trial_detail)
    sponsor = extract_field(r'\*\*Lead Sponsor:?\*\*\s*(.+?)(?=\(|$|\n)', trial_detail)

    # Conditions
    conditions = extract_field(r'## Conditions\s+[-\s]+(.*?)(?=\n##|\Z)', trial_detail)

    # Interventions
    intervention_match = re.search(
        r'## Interventions\s+###\s+([^:]+):\s+(.+?)(?=\n##|\Z)',
        trial_detail,
        re.DOTALL
    )
    if intervention_match:
        intervention = f"{intervention_match.group(1).strip()}: {intervention_match.group(2).strip().split(chr(10))[0]}"
    else:
        intervention = extract_field(r'\*\*Interventions?:?\*\*\s*(.+?)(?=\n\*\*|\n##|$)', trial_detail)

    return {
        'nct_id': nct_id,
        'title': title,
        'status': status,
        'why_stopped': why_stopped,
        'interventions': intervention,
        'phase': phase,
        'conditions': conditions,
        'sponsor': sponsor,
        'link': f"https://clinicaltrials.gov/study/{nct_id}"
    }


def categorize_trials(trials):
    """Categorize trials by phase, diabetes type, and status."""

    categorizations = {
        'by_phase': {},
        'by_diabetes_type': {},
        'by_status': {}
    }

    for trial in trials:
        # Categorize by phase
        phase = trial['phase']
        categorizations['by_phase'][phase] = categorizations['by_phase'].get(phase, 0) + 1

        # Categorize by diabetes type
        conditions_lower = trial['conditions'].lower()
        if 'type 1' in conditions_lower or 'type i' in conditions_lower or 't1d' in conditions_lower:
            dtype = 'Type 1 Diabetes'
        elif 'type 2' in conditions_lower or 'type ii' in conditions_lower or 't2d' in conditions_lower:
            dtype = 'Type 2 Diabetes'
        elif 'gestational' in conditions_lower or 'gdm' in conditions_lower:
            dtype = 'Gestational Diabetes'
        else:
            dtype = 'Other/Unspecified'
        categorizations['by_diabetes_type'][dtype] = \
            categorizations['by_diabetes_type'].get(dtype, 0) + 1

        # Categorize by status
        status_lower = trial['status'].lower()
        if 'terminated' in status_lower:
            status_key = 'terminated'
        elif 'withdrawn' in status_lower:
            status_key = 'withdrawn'
        elif 'suspended' in status_lower:
            status_key = 'suspended'
        else:
            status_key = trial['status']

        categorizations['by_status'][status_key] = \
            categorizations['by_status'].get(status_key, 0) + 1

    # Sort categorizations
    for cat_type in categorizations:
        categorizations[cat_type] = dict(sorted(
            categorizations[cat_type].items(),
            key=lambda x: x[1],
            reverse=True
        ))

    return categorizations


def extract_drug_name(intervention_text):
    """Extract drug name from intervention text."""
    if not intervention_text or intervention_text == "Not specified":
        return None

    # Common patterns: "Drug: Name" or "Biological: Name"
    match = re.search(r'(?:Drug|Biological):\s*([^,;\n]+)', intervention_text, re.IGNORECASE)
    if match:
        drug = match.group(1).strip()
        # Remove common suffixes
        drug = re.sub(r'\s*\(.*?\)\s*$', '', drug)  # Remove parenthetical
        return drug

    # Fallback: Take first compound-like name
    parts = intervention_text.split(':')
    if len(parts) > 1:
        return parts[1].split(',')[0].strip()

    return intervention_text.split(',')[0].strip()


def score_notable_drugs(trials, nct_to_keywords):
    """Score drugs based on multiple criteria to identify notable failures.

    Scoring criteria:
    1. Trial Count: Number of trials for same drug (3+ = 10pts, 2 = 5pts, 1 = 1pt)
    2. Phase: Latest phase reached (Phase 3/4 = 10pts, Phase 2 = 6pts, Phase 1 = 3pts)
    3. Major Pharma: Large pharmaceutical sponsor (Yes = 10pts, No = 0pts)
    4. Safety Severity: From "Why Stopped" keywords (Death = 10pts, Toxicity = 8pts, SAE = 5pts, etc.)
    5. Total Score: Sum of all scores

    Args:
        trials: List of trial dictionaries
        nct_to_keywords: Dict mapping NCT ID to list of (keyword, severity_score) tuples
    """

    # Major pharmaceutical companies
    major_pharma = {
        'pfizer', 'novartis', 'roche', 'merck', 'gsk', 'glaxosmithkline',
        'sanofi', 'abbvie', 'takeda', 'bayer', 'biogen', 'amgen',
        'bristol-myers squibb', 'bms', 'lilly', 'eli lilly', 'johnson',
        'astrazeneca', 'boehringer', 'novo nordisk', 'regeneron'
    }

    # Group trials by drug
    drugs = {}
    for trial in trials:
        drug_name = extract_drug_name(trial['interventions'])
        if not drug_name or len(drug_name) < 3:  # Skip very short names
            continue

        if drug_name not in drugs:
            drugs[drug_name] = {
                'trials': [],
                'nct_ids': [],
                'max_phase': 'N/A',
                'sponsors': set(),
                'safety_keywords': set(),
                'why_stopped_examples': []  # Store actual "Why Stopped" text
            }

        drugs[drug_name]['trials'].append(trial)
        drugs[drug_name]['nct_ids'].append(trial['nct_id'])
        drugs[drug_name]['sponsors'].add(trial['sponsor'])

        # Track highest phase (handle both "Phase 3" and "Phase3" formats)
        phase = trial['phase']
        phase_lower = phase.lower().replace(' ', '')

        if 'phase3' in phase_lower or 'phase4' in phase_lower:
            if drugs[drug_name]['max_phase'] == 'N/A' or \
               'phase1' in drugs[drug_name]['max_phase'].lower().replace(' ', '') or \
               'phase2' in drugs[drug_name]['max_phase'].lower().replace(' ', ''):
                drugs[drug_name]['max_phase'] = phase
        elif 'phase2' in phase_lower:
            if drugs[drug_name]['max_phase'] == 'N/A' or \
               'phase1' in drugs[drug_name]['max_phase'].lower().replace(' ', ''):
                drugs[drug_name]['max_phase'] = phase
        elif 'phase1' in phase_lower and drugs[drug_name]['max_phase'] == 'N/A':
            drugs[drug_name]['max_phase'] = phase

    # Score each drug
    scored_drugs = []
    for drug_name, data in drugs.items():
        score_breakdown = {}

        # 1. Trial Count Score
        trial_count = len(data['trials'])
        if trial_count >= 3:
            score_breakdown['trial_count'] = 10
        elif trial_count == 2:
            score_breakdown['trial_count'] = 5
        else:
            score_breakdown['trial_count'] = 1

        # 2. Phase Score (handle both "Phase 3" and "Phase3" formats)
        phase = data['max_phase']
        phase_lower = phase.lower().replace(' ', '')
        if 'phase3' in phase_lower or 'phase4' in phase_lower:
            score_breakdown['phase'] = 10
        elif 'phase2' in phase_lower:
            score_breakdown['phase'] = 6
        elif 'phase1' in phase_lower or 'earlyphase' in phase_lower:
            score_breakdown['phase'] = 3
        else:
            score_breakdown['phase'] = 0

        # 3. Major Pharma Score
        is_major_pharma = any(
            pharma in sponsor.lower()
            for sponsor in data['sponsors']
            for pharma in major_pharma
        )
        score_breakdown['major_pharma'] = 10 if is_major_pharma else 0

        # 4. Safety Severity Score (from actual "Why Stopped" text - more accurate than search keywords)
        max_severity = 0
        safety_keywords_dict = {
            'death': 10, 'mortality': 10, 'fatal': 10,
            'toxicity': 8, 'toxic': 8, 'hepatotoxicity': 8, 'cardiotoxicity': 8,
            'adverse': 5, 'SAE': 5, 'serious adverse': 5,
            'tolerability': 3, 'side effect': 3, 'intolerable': 3,
            'safety': 1, 'harm': 1, 'hypoglycemia': 1
        }

        for trial in data['trials']:
            why_stopped_raw = trial.get('why_stopped', 'Not specified')
            why_stopped = why_stopped_raw.lower()
            if why_stopped != 'not specified':
                # Store actual "Why Stopped" text (up to 3 examples)
                if len(data['why_stopped_examples']) < 3:
                    data['why_stopped_examples'].append({
                        'nct_id': trial['nct_id'],
                        'reason': why_stopped_raw
                    })
                # Scan actual "Why Stopped" text for all severity keywords
                for keyword, severity_score in safety_keywords_dict.items():
                    if keyword in why_stopped:
                        max_severity = max(max_severity, severity_score)
                        data['safety_keywords'].add(keyword)
        score_breakdown['safety_severity'] = max_severity

        # Total Score
        total_score = sum(score_breakdown.values())

        scored_drugs.append({
            'drug_name': drug_name,
            'trial_count': trial_count,
            'nct_ids': data['nct_ids'],
            'max_phase': phase,
            'sponsors': ', '.join(sorted(data['sponsors'])[:2]),  # Top 2 sponsors
            'safety_keywords': ', '.join(sorted(data['safety_keywords'])),
            'why_stopped_examples': data['why_stopped_examples'],
            'scores': score_breakdown,
            'total_score': total_score
        })

    # Sort by total score descending
    scored_drugs.sort(key=lambda x: x['total_score'], reverse=True)

    return scored_drugs


def format_why_stopped_examples(scored_drugs, top_n=10):
    """Format actual 'Why Stopped' reasons for top drugs."""

    lines = [
        "",
        "=" * 140,
        "ACTUAL 'WHY STOPPED' REASONS FOR TOP DRUGS",
        "=" * 140,
        ""
    ]

    for i, drug in enumerate(scored_drugs[:top_n], 1):
        if drug['why_stopped_examples']:
            lines.append(f"{i}. {drug['drug_name']} (Score: {drug['total_score']}, {len(drug['nct_ids'])} trials)")
            for example in drug['why_stopped_examples']:
                lines.append(f"   • {example['nct_id']}: {example['reason']}")
            lines.append("")

    if not any(drug['why_stopped_examples'] for drug in scored_drugs[:top_n]):
        lines.append("No 'Why Stopped' reasons available for top drugs.")
        lines.append("")

    return "\n".join(lines)


def format_notable_drugs_table(scored_drugs, top_n=20):
    """Format notable drugs as a table with scoring breakdown."""

    lines = [
        "=" * 140,
        "NOTABLE DRUG FAILURES - AUTOMATICALLY SCORED",
        "=" * 140,
        "",
        "Scoring Criteria:",
        "  • Trial Count: 3+ trials = 10pts | 2 trials = 5pts | 1 trial = 1pt",
        "  • Phase: Phase 3/4 = 10pts | Phase 2 = 6pts | Phase 1 = 3pts | N/A = 0pts",
        "  • Major Pharma: Yes = 10pts | No = 0pts",
        "  • Safety Severity: Death/Fatal = 10pts | Toxicity = 8pts | Adverse = 5pts | Tolerability = 3pts | Safety = 1pt",
        "",
        ""
    ]

    # Table header
    header = f"{'Rank':<5} {'Drug Name':<30} {'Trials':<7} {'Phase':<10} {'Pharma':<7} {'Severity':<9} {'TOTAL':<6} {'Sponsors'}"
    lines.append(header)
    lines.append("=" * 140)

    # Table rows
    for i, drug in enumerate(scored_drugs[:top_n], 1):
        row = (
            f"{i:<5} "
            f"{drug['drug_name'][:29]:<30} "
            f"{drug['scores']['trial_count']:<7} "
            f"{drug['scores']['phase']:<10} "
            f"{drug['scores']['major_pharma']:<7} "
            f"{drug['scores']['safety_severity']:<9} "
            f"{drug['total_score']:<6} "
            f"{drug['sponsors'][:50]}"
        )
        lines.append(row)

    lines.extend([
        "=" * 140,
        "",
        f"Showing top {min(top_n, len(scored_drugs))} of {len(scored_drugs)} unique drugs",
        ""
    ])

    return "\n".join(lines)


def generate_summary(trials, categorizations, total_count, scored_drugs):
    """Generate formatted summary with notable drugs table."""

    lines = [
        "=" * 80,
        "DIABETES TRIALS STOPPED DUE TO SAFETY CONCERNS",
        "=" * 80,
        "",
        f"Total Trials: {total_count}",
        ""
    ]

    if categorizations['by_status']:
        lines.append("Status Breakdown:")
        for status, count in categorizations['by_status'].items():
            lines.append(f"  • {status.title()}: {count} trials")
        lines.append("")

    if categorizations['by_phase']:
        lines.append("Phase Breakdown:")
        for phase, count in categorizations['by_phase'].items():
            lines.append(f"  • {phase}: {count} trials")
        lines.append("")

    if categorizations['by_diabetes_type']:
        lines.append("Diabetes Type Breakdown:")
        for dtype, count in categorizations['by_diabetes_type'].items():
            lines.append(f"  • {dtype}: {count} trials")
        lines.append("")

    # Add notable drugs table
    notable_table = format_notable_drugs_table(scored_drugs, top_n=20)
    lines.append(notable_table)

    # Add actual "Why Stopped" reasons for top drugs
    why_stopped_section = format_why_stopped_examples(scored_drugs, top_n=10)
    lines.append(why_stopped_section)

    # Show sample trials
    lines.extend([
        "=" * 80,
        "SAMPLE TRIALS (First 10):",
        "=" * 80,
        ""
    ])

    for i, trial in enumerate(trials[:10], 1):
        lines.extend([
            f"\n{i}. {trial['nct_id']} - {trial['status']}",
            f"   Title: {trial['title'][:80]}{'...' if len(trial['title']) > 80 else ''}",
            f"   Why Stopped: {trial['why_stopped']}",
            f"   Phase: {trial['phase']}",
            f"   Sponsor: {trial['sponsor']}",
            f"   Interventions: {trial['interventions'][:80]}{'...' if len(trial['interventions']) > 80 else ''}",
            f"   Link: {trial['link']}"
        ])

    lines.extend([
        "",
        "=" * 80,
        "NOTE: 'Why Stopped' reasons shown above are extracted from ClinicalTrials.gov.",
        "Visit the CT.gov links for complete trial details.",
        "=" * 80
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    result = get_diabetes_drugs_stopped_safety()
    print("\n" + result['summary'])
