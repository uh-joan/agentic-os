import sys
sys.path.insert(0, ".claude")
from mcp.servers.uspto_patents_mcp import google_search_by_assignee
from mcp.servers.ct_gov_mcp import search
import re

def get_novo_nordisk_novel_patents():
    """Identify Novo Nordisk patents in areas not yet in clinical development.

    Compares recent patents (2022-2025) against active clinical pipeline
    to identify novel therapeutic areas that may represent future R&D directions.

    Returns:
        dict: Contains patents, pipeline indications, and novelty analysis
    """

    print("Step 1: Fetching recent Novo Nordisk patents (2022-2025)...")
    print("=" * 80)

    # Use API-level date filtering for efficiency (10x faster)
    try:
        print(f"  Fetching patents with API-level date filter (2022-2025)...")
        result = google_search_by_assignee(
            assignee_name="Novo Nordisk",
            country="US",
            limit=500,
            start_date=20220101,  # January 1, 2022
            end_date=20251231     # December 31, 2025
        )

        # Process results directly (already filtered by date)
        raw_patents = result.get('results', [])
        print(f"  Retrieved {len(raw_patents)} patents from 2022-2025\n")

        patents = []
        for p in raw_patents:
            # Extract title from localized array
            title_data = p.get('title_localized', [{}])
            title = title_data[0].get('text', '') if title_data else ''

            patents.append({
                'patentNumber': p.get('publication_number', 'Unknown'),
                'title': title,
                'publicationDate': str(p.get('publication_date', ''))
            })

    except Exception as e:
        print(f"Error fetching patents: {e}")
        import traceback
        traceback.print_exc()
        patents = []

    print("Step 2: Fetching active Novo Nordisk clinical pipeline...")
    print("=" * 80)

    # Get active clinical trials for Novo Nordisk
    try:
        trials_result = search(
            term="Novo Nordisk",
            filter_overallStatus="RECRUITING,ACTIVE_NOT_RECRUITING,ENROLLING_BY_INVITATION",
            pageSize=1000
        )

        # Parse markdown response to extract conditions
        trials_text = trials_result if isinstance(trials_result, str) else str(trials_result)

        # Extract conditions from trials
        condition_pattern = r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)'
        conditions = re.findall(condition_pattern, trials_text)

        # Flatten and normalize conditions
        pipeline_conditions = set()
        for cond_list in conditions:
            for cond in cond_list.split('|'):
                pipeline_conditions.add(cond.strip().lower())

        print(f"Found {len(pipeline_conditions)} unique conditions in active pipeline\n")

    except Exception as e:
        print(f"Error fetching trials: {e}")
        pipeline_conditions = set()

    print("Step 3: Analyzing patents for novel therapeutic areas...")
    print("=" * 80)

    # Categorize patents and identify novel areas
    patent_categories = {
        'GLP-1 Related': [],
        'Diabetes (non-GLP-1)': [],
        'Obesity': [],
        'NASH/Liver': [],
        'Cardiovascular': [],
        'Kidney/Nephrology': [],
        'Alzheimer/Neurodegeneration': [],
        'Hemophilia': [],
        'Growth Hormone': [],
        'Inflammation/Immunology': [],
        'Cancer/Oncology': [],
        'Antibody Therapeutics': [],
        'Gene/Cell Therapy': [],
        'Novel/Unclassified': []
    }

    # Therapeutic area keyword mapping
    area_keywords = {
        'GLP-1 Related': ['glp-1', 'glp1', 'glucagon-like peptide', 'semaglutide', 'liraglutide'],
        'Diabetes (non-GLP-1)': ['diabetes', 'diabetic', 'glycemic', 'insulin', 'glucose'],
        'Obesity': ['obesity', 'weight', 'adipose', 'bariatric'],
        'NASH/Liver': ['nash', 'liver', 'hepatic', 'steatosis', 'cirrhosis'],
        'Cardiovascular': ['cardiovascular', 'cardiac', 'heart', 'atherosclerosis'],
        'Kidney/Nephrology': ['kidney', 'renal', 'nephro', 'dialysis'],
        'Alzheimer/Neurodegeneration': ['alzheimer', 'cognitive', 'neurodegeneration', 'dementia'],
        'Hemophilia': ['hemophilia', 'factor viii', 'factor ix', 'bleeding', 'coagulation'],
        'Growth Hormone': ['growth hormone', 'somatropin', 'hgh', 'growth deficiency'],
        'Inflammation/Immunology': ['inflammation', 'inflammatory', 'immune', 'autoimmune'],
        'Cancer/Oncology': ['cancer', 'oncology', 'tumor', 'carcinoma', 'leukemia'],
        'Antibody Therapeutics': ['antibody', 'antibodies', 'monoclonal', 'bispecific'],
        'Gene/Cell Therapy': ['gene therapy', 'crispr', 'genetic', 'cell therapy', 'car-t']
    }

    novel_patents = []

    for patent in patents:
        title = patent.get('title', '').lower()
        patent_num = patent.get('patentNumber', 'Unknown')
        pub_date = patent.get('publicationDate', 'Unknown')

        # Categorize patent
        categorized = False
        for category, keywords in area_keywords.items():
            if any(kw in title for kw in keywords):
                patent_info = {
                    'patent_number': patent_num,
                    'title': patent.get('title', ''),
                    'publication_date': pub_date,
                    'category': category
                }
                patent_categories[category].append(patent_info)

                # Check if this represents a novel area
                # (not well-represented in current pipeline)
                is_novel = True
                for keyword in keywords:
                    if any(keyword in cond for cond in pipeline_conditions):
                        is_novel = False
                        break

                if is_novel and category not in ['GLP-1 Related', 'Diabetes (non-GLP-1)']:
                    novel_patents.append(patent_info)

                categorized = True
                break

        if not categorized:
            patent_categories['Novel/Unclassified'].append({
                'patent_number': patent_num,
                'title': patent.get('title', ''),
                'publication_date': pub_date,
                'category': 'Novel/Unclassified'
            })
            novel_patents.append(patent_categories['Novel/Unclassified'][-1])

    # Generate summary
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\nTotal Recent Patents: {len(patents)}")
    print(f"Active Pipeline Conditions: {len(pipeline_conditions)}")
    print(f"Potentially Novel Patents: {len(novel_patents)}")

    print("\n" + "-" * 80)
    print("PATENT DISTRIBUTION BY THERAPEUTIC AREA")
    print("-" * 80)

    for category, cat_patents in patent_categories.items():
        if cat_patents:
            print(f"\n{category}: {len(cat_patents)} patents")
            for i, p in enumerate(cat_patents[:3], 1):
                print(f"  {i}. {p['patent_number']} - {p['title'][:70]}...")

    print("\n" + "-" * 80)
    print("POTENTIALLY NOVEL AREAS (Not Well-Represented in Pipeline)")
    print("-" * 80)

    if novel_patents:
        for i, patent in enumerate(novel_patents[:15], 1):
            print(f"\n{i}. [{patent['category']}] {patent['patent_number']}")
            print(f"   Published: {patent['publication_date']}")
            print(f"   Title: {patent['title']}")
    else:
        print("\nNo clearly novel areas identified - all patents align with current pipeline focus.")

    return {
        'total_patents': len(patents),
        'pipeline_conditions_count': len(pipeline_conditions),
        'patent_categories': {k: len(v) for k, v in patent_categories.items() if v},
        'novel_patents': novel_patents,
        'novel_count': len(novel_patents)
    }

if __name__ == "__main__":
    result = get_novo_nordisk_novel_patents()
    print("\n" + "=" * 80)
    print(f"Analysis complete: {result['novel_count']} novel patents identified")
    print("=" * 80)
