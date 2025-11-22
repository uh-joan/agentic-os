import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search

def get_checkpoint_inhibitor_rwe_studies():
    """Search PubMed for real-world evidence studies on checkpoint inhibitor effectiveness.

    Focuses on:
    - Real-world performance vs clinical trial efficacy
    - Real-world response rates and survival data
    - Patient selection patterns in real-world settings

    Returns:
        dict: Contains total_count, studies summary, and study details
    """

    # Construct search query for RWE studies on checkpoint inhibitors
    # Include key terms: checkpoint inhibitor, real-world, effectiveness, outcomes
    query = (
        '("checkpoint inhibitor" OR "immune checkpoint" OR "PD-1" OR "PD-L1" OR '
        '"CTLA-4" OR "nivolumab" OR "pembrolizumab" OR "atezolizumab" OR '
        '"durvalumab" OR "ipilimumab") AND '
        '("real world" OR "real-world" OR "retrospective" OR "observational" OR '
        '"effectiveness" OR "real world evidence" OR "RWE") AND '
        '("response rate" OR "survival" OR "outcomes" OR "effectiveness" OR '
        '"overall survival" OR "progression free survival")'
    )

    # Search with larger result set to capture comprehensive RWE landscape
    result = search(query=query, max_results=100)

    # Parse results
    if not result or 'articles' not in result:
        return {
            'total_count': 0,
            'summary': 'No real-world evidence studies found for checkpoint inhibitors',
            'studies': []
        }

    articles = result.get('articles', [])
    total_count = len(articles)

    # Analyze study characteristics
    study_types = {}
    cancer_types = {}
    checkpoint_targets = {
        'PD-1': 0,
        'PD-L1': 0,
        'CTLA-4': 0,
        'Combination': 0
    }

    studies_detail = []

    for article in articles:
        title = article.get('title', '').lower()
        abstract = article.get('abstract', '').lower()
        combined_text = f"{title} {abstract}"

        # Identify study type
        if 'retrospective' in combined_text:
            study_types['Retrospective'] = study_types.get('Retrospective', 0) + 1
        if 'observational' in combined_text:
            study_types['Observational'] = study_types.get('Observational', 0) + 1
        if 'real world' in combined_text or 'real-world' in combined_text:
            study_types['Real-World'] = study_types.get('Real-World', 0) + 1

        # Identify cancer types
        cancer_keywords = {
            'melanoma': 'Melanoma',
            'lung cancer': 'Lung Cancer',
            'nsclc': 'NSCLC',
            'renal cell': 'Renal Cell Carcinoma',
            'bladder': 'Bladder Cancer',
            'head and neck': 'Head and Neck Cancer',
            'hepatocellular': 'Hepatocellular Carcinoma',
            'gastric': 'Gastric Cancer'
        }

        for keyword, cancer_type in cancer_keywords.items():
            if keyword in combined_text:
                cancer_types[cancer_type] = cancer_types.get(cancer_type, 0) + 1

        # Identify checkpoint targets
        if 'pd-1' in combined_text or 'nivolumab' in combined_text or 'pembrolizumab' in combined_text:
            checkpoint_targets['PD-1'] += 1
        if 'pd-l1' in combined_text or 'atezolizumab' in combined_text or 'durvalumab' in combined_text:
            checkpoint_targets['PD-L1'] += 1
        if 'ctla-4' in combined_text or 'ipilimumab' in combined_text:
            checkpoint_targets['CTLA-4'] += 1
        if 'combination' in combined_text:
            checkpoint_targets['Combination'] += 1

        # Extract key study details
        study_detail = {
            'pmid': article.get('pmid', 'N/A'),
            'title': article.get('title', 'N/A'),
            'authors': article.get('authors', [])[:3],  # First 3 authors
            'journal': article.get('journal', 'N/A'),
            'pub_date': article.get('pub_date', 'N/A'),
            'has_abstract': bool(article.get('abstract'))
        }
        studies_detail.append(study_detail)

    # Sort study types by frequency
    study_types_sorted = sorted(study_types.items(), key=lambda x: x[1], reverse=True)
    cancer_types_sorted = sorted(cancer_types.items(), key=lambda x: x[1], reverse=True)
    checkpoint_sorted = sorted(checkpoint_targets.items(), key=lambda x: x[1], reverse=True)

    # Build summary
    summary = f"""Real-World Evidence Studies on Checkpoint Inhibitor Effectiveness

Total Studies Found: {total_count}

Study Types:
"""
    for study_type, count in study_types_sorted:
        summary += f"  - {study_type}: {count} studies\n"

    summary += f"\nCancer Types (Top 5):\n"
    for cancer_type, count in cancer_types_sorted[:5]:
        summary += f"  - {cancer_type}: {count} studies\n"

    summary += f"\nCheckpoint Targets:\n"
    for target, count in checkpoint_sorted:
        if count > 0:
            summary += f"  - {target}: {count} studies\n"

    summary += f"\nRecent Publications (Top 10 by date):\n"
    # Sort by publication date (most recent first)
    studies_sorted = sorted(
        studies_detail,
        key=lambda x: x.get('pub_date', ''),
        reverse=True
    )[:10]

    for i, study in enumerate(studies_sorted, 1):
        authors_str = ', '.join(study['authors']) if study['authors'] else 'N/A'
        summary += f"\n{i}. PMID: {study['pmid']}\n"
        summary += f"   Title: {study['title'][:100]}...\n"
        summary += f"   Authors: {authors_str}\n"
        summary += f"   Journal: {study['journal']}\n"
        summary += f"   Date: {study['pub_date']}\n"

    return {
        'total_count': total_count,
        'summary': summary,
        'study_types': dict(study_types_sorted),
        'cancer_types': dict(cancer_types_sorted),
        'checkpoint_targets': dict(checkpoint_sorted),
        'studies': studies_detail
    }

if __name__ == "__main__":
    result = get_checkpoint_inhibitor_rwe_studies()
    print(result['summary'])
