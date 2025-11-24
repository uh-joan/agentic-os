import sys
import re
from collections import defaultdict, Counter
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_pd1_checkpoint_trials():
    """Get all PD-1/PD-L1 checkpoint inhibitor clinical trials across solid tumors.

    Searches for major checkpoint inhibitors and organizes by cancer indication.

    Returns:
        dict: Contains total_count, trials_by_indication, company_matrix, and summary
    """
    print("Querying ClinicalTrials.gov for PD-1/PD-L1 checkpoint inhibitor trials...")

    # Search for PD-1/PD-L1 inhibitors with comprehensive query
    search_query = (
        "PD-1 inhibitor OR PD-L1 inhibitor OR "
        "pembrolizumab OR nivolumab OR atezolizumab OR durvalumab OR "
        "cemiplimab OR avelumab OR dostarlimab OR retifanlimab OR "
        "checkpoint inhibitor solid tumor"
    )

    all_trials = []
    page_token = None
    page_count = 0

    # Pagination loop - collect ALL trials
    while True:
        page_count += 1
        print(f"  Fetching page {page_count}...")

        if page_token:
            result = search(query=search_query, pageSize=1000, pageToken=page_token)
        else:
            result = search(query=search_query, pageSize=1000)

        if not result or not isinstance(result, str):
            break

        # Parse trials from markdown
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:  # Skip first empty block
            all_trials.append(block)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match and next_token_match.group(1) != page_token:
            page_token = next_token_match.group(1)
        else:
            break

    print(f"  Retrieved {len(all_trials)} total trials across {page_count} pages")

    # Parse and categorize trials
    trials_by_indication = defaultdict(list)
    company_counts = defaultdict(lambda: defaultdict(int))
    phase_distribution = Counter()
    status_distribution = Counter()
    drug_mentions = Counter()

    # Common PD-1/PD-L1 drugs to track
    pd1_drugs = [
        'pembrolizumab', 'nivolumab', 'cemiplimab', 'dostarlimab',
        'retifanlimab', 'toripalimab', 'sintilimab', 'tislelizumab'
    ]
    pdl1_drugs = [
        'atezolizumab', 'durvalumab', 'avelumab', 'cosibelimab'
    ]

    for trial_text in all_trials:
        # Extract NCT ID (reconstruct from context)
        nct_match = re.search(r'NCT\d{8}', trial_text)
        if not nct_match:
            continue
        nct_id = nct_match.group(0)

        # Extract title and condition
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', trial_text)
        condition_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', trial_text)
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_text)
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', trial_text)
        sponsor_match = re.search(r'\*\*Sponsor:\*\*\s*(.+?)(?:\n|$)', trial_text)

        title = title_match.group(1).strip() if title_match else "Unknown"
        condition = condition_match.group(1).strip() if condition_match else "Unknown"
        phase = phase_match.group(1).strip() if phase_match else "Unknown"
        status = status_match.group(1).strip() if status_match else "Unknown"
        sponsor = sponsor_match.group(1).strip() if sponsor_match else "Unknown"

        # Only include solid tumor trials (exclude hematologic malignancies)
        condition_lower = condition.lower()
        title_lower = title.lower()
        combined_text = condition_lower + " " + title_lower

        # Exclude hematologic malignancies
        heme_keywords = ['leukemia', 'lymphoma', 'myeloma', 'myeloid', 'lymphoid']
        if any(keyword in combined_text for keyword in heme_keywords):
            continue

        # Must mention solid tumor or specific solid tumor types
        solid_tumor_keywords = [
            'solid tumor', 'carcinoma', 'melanoma', 'sarcoma', 'cancer',
            'lung', 'breast', 'colorectal', 'gastric', 'pancreatic',
            'hepatocellular', 'renal', 'bladder', 'ovarian', 'cervical',
            'head and neck', 'esophageal', 'prostate', 'endometrial'
        ]

        if not any(keyword in combined_text for keyword in solid_tumor_keywords):
            continue

        # Categorize by indication
        indication = "Other Solid Tumors"
        if 'lung' in combined_text or 'nsclc' in combined_text or 'sclc' in combined_text:
            indication = "Lung Cancer"
        elif 'melanoma' in combined_text:
            indication = "Melanoma"
        elif 'breast' in combined_text:
            indication = "Breast Cancer"
        elif 'renal' in combined_text or 'kidney' in combined_text:
            indication = "Renal Cell Carcinoma"
        elif 'bladder' in combined_text or 'urothelial' in combined_text:
            indication = "Bladder/Urothelial Cancer"
        elif 'head and neck' in combined_text or 'hnscc' in combined_text:
            indication = "Head and Neck Cancer"
        elif 'gastric' in combined_text or 'stomach' in combined_text:
            indication = "Gastric Cancer"
        elif 'colorectal' in combined_text or 'crc' in combined_text:
            indication = "Colorectal Cancer"
        elif 'hepatocellular' in combined_text or 'liver cancer' in combined_text:
            indication = "Hepatocellular Carcinoma"
        elif 'ovarian' in combined_text:
            indication = "Ovarian Cancer"
        elif 'cervical' in combined_text:
            indication = "Cervical Cancer"
        elif 'pancreatic' in combined_text:
            indication = "Pancreatic Cancer"
        elif 'prostate' in combined_text:
            indication = "Prostate Cancer"
        elif 'esophageal' in combined_text:
            indication = "Esophageal Cancer"
        elif 'endometrial' in combined_text or 'uterine' in combined_text:
            indication = "Endometrial Cancer"
        elif 'sarcoma' in combined_text:
            indication = "Sarcoma"

        trial_info = {
            'nct_id': nct_id,
            'title': title,
            'condition': condition,
            'phase': phase,
            'status': status,
            'sponsor': sponsor,
            'indication': indication
        }

        trials_by_indication[indication].append(trial_info)
        phase_distribution[phase] += 1
        status_distribution[status] += 1

        # Track company × indication
        company_counts[sponsor][indication] += 1

        # Track drug mentions
        for drug in pd1_drugs + pdl1_drugs:
            if drug.lower() in combined_text:
                drug_mentions[drug] += 1

    # Sort indications by trial count
    sorted_indications = sorted(
        trials_by_indication.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    # Generate company × indication matrix (top companies)
    top_companies = sorted(
        [(company, sum(indications.values())) for company, indications in company_counts.items()],
        key=lambda x: x[1],
        reverse=True
    )[:15]  # Top 15 companies

    company_matrix = []
    for company, total in top_companies:
        row = {
            'company': company,
            'total_trials': total,
            'by_indication': dict(company_counts[company])
        }
        company_matrix.append(row)

    # Generate summary
    total_trials = sum(len(trials) for trials in trials_by_indication.values())

    summary = {
        'total_trials': total_trials,
        'total_indications': len(trials_by_indication),
        'top_indications': [
            {'indication': ind, 'count': len(trials)}
            for ind, trials in sorted_indications[:10]
        ],
        'phase_distribution': dict(phase_distribution.most_common()),
        'status_distribution': dict(status_distribution.most_common()),
        'top_drugs': dict(drug_mentions.most_common(10)),
        'top_companies': [
            {'company': company, 'trials': count}
            for company, count in top_companies[:10]
        ]
    }

    return {
        'total_count': total_trials,
        'trials_by_indication': dict(sorted_indications),
        'company_matrix': company_matrix,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_pd1_checkpoint_trials()

    print("\n" + "="*80)
    print("PD-1/PD-L1 CHECKPOINT INHIBITOR TRIALS - SOLID TUMORS")
    print("="*80)
    print(f"\nTotal Trials: {result['total_count']}")
    print(f"Indications Covered: {result['summary']['total_indications']}")

    print("\n--- Top Indications by Trial Count ---")
    for item in result['summary']['top_indications']:
        print(f"  {item['indication']}: {item['count']} trials")

    print("\n--- Phase Distribution ---")
    for phase, count in result['summary']['phase_distribution'].items():
        print(f"  {phase}: {count} trials")

    print("\n--- Top Checkpoint Inhibitors ---")
    for drug, count in result['summary']['top_drugs'].items():
        print(f"  {drug.title()}: {count} mentions")

    print("\n--- Top Companies (by trial count) ---")
    for item in result['summary']['top_companies']:
        print(f"  {item['company']}: {item['trials']} trials")

    print("\n--- Company × Indication Matrix (Top 5 Companies) ---")
    for company_data in result['company_matrix'][:5]:
        print(f"\n{company_data['company']} ({company_data['total_trials']} trials):")
        sorted_indications = sorted(
            company_data['by_indication'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for indication, count in sorted_indications[:5]:
            print(f"  - {indication}: {count} trials")

    print("\n" + "="*80)
