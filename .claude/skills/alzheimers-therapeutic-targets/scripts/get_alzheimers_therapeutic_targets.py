import sys
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_diseases, get_disease_targets_summary

def get_alzheimers_therapeutic_targets():
    """Get top therapeutic targets for Alzheimer's disease with genetic evidence.

    Focuses on targets with strong genetic evidence scores, which are most
    likely to be valid therapeutic targets.

    Returns:
        dict: Contains disease info, top targets with genetic evidence, and summary statistics
    """
    results = {'disease_info': {}, 'top_targets': [], 'genetic_targets': [], 'summary': {}}

    print("Searching for Alzheimer's disease...")
    disease_results = search_diseases(query="Alzheimer's disease", size=5)

    if not disease_results or 'data' not in disease_results:
        return {'error': 'No disease data found'}

    diseases = disease_results.get('data', {}).get('search', {}).get('hits', [])
    if not diseases:
        return {'error': 'No matching diseases found'}

    disease = diseases[0]
    disease_id = disease.get('id', '')
    disease_name = disease.get('name', '')

    results['disease_info'] = {
        'id': disease_id,
        'name': disease_name,
        'description': disease.get('description', 'N/A')
    }

    print(f"Found disease: {disease_name} ({disease_id})")

    print("Retrieving associated therapeutic targets...")
    targets_results = get_disease_targets_summary(diseaseId=disease_id, minScore=0.0, size=50)

    if not targets_results or 'data' not in targets_results:
        return {'disease_info': results['disease_info'], 'error': 'No target associations found'}

    associations = targets_results.get('data', [])

    if not associations:
        return {'disease_info': results['disease_info'], 'error': 'No target associations in response'}

    print(f"Found {len(associations)} target associations")

    # Process all targets and identify those with strong genetic evidence
    top_targets = []
    genetic_targets = []

    for assoc in associations:
        # Extract target and score information
        target_id = assoc.get('targetId', 'N/A')
        score = assoc.get('score', 0)
        datatype_scores = assoc.get('datatypeScores', {})

        target_info = {
            'target_id': target_id,
            'association_score': round(score, 4),
            'datatype_scores': {}
        }

        # Extract evidence type scores
        genetic_score = 0
        if isinstance(datatype_scores, dict):
            for datatype, dt_score in datatype_scores.items():
                score_val = round(dt_score, 4) if isinstance(dt_score, (int, float)) else 0
                target_info['datatype_scores'][datatype] = score_val

                # Track genetic evidence specifically
                if 'genetic' in datatype.lower() or 'pathway' in datatype.lower():
                    genetic_score = max(genetic_score, score_val)

        target_info['genetic_evidence_score'] = genetic_score

        # Add to top targets (top 15 by overall score)
        if len(top_targets) < 15:
            top_targets.append(target_info)

        # Separately track targets with strong genetic evidence
        if genetic_score > 0.3:  # Threshold for meaningful genetic evidence
            genetic_targets.append(target_info)

    # Sort genetic targets by genetic evidence score
    genetic_targets.sort(key=lambda x: x['genetic_evidence_score'], reverse=True)

    results['top_targets'] = top_targets
    results['genetic_targets'] = genetic_targets

    # Calculate summary statistics
    total_targets = len(associations)
    avg_score = sum(t['association_score'] for t in top_targets) / len(top_targets) if top_targets else 0

    evidence_types = set()
    for target in top_targets:
        evidence_types.update(target['datatype_scores'].keys())

    avg_genetic_score = sum(t['genetic_evidence_score'] for t in genetic_targets) / len(genetic_targets) if genetic_targets else 0

    results['summary'] = {
        'disease': disease_name,
        'disease_id': disease_id,
        'total_targets': total_targets,
        'top_targets_shown': len(top_targets),
        'targets_with_genetic_evidence': len(genetic_targets),
        'avg_association_score': round(avg_score, 4),
        'avg_genetic_evidence_score': round(avg_genetic_score, 4),
        'evidence_types': sorted(list(evidence_types)),
        'num_evidence_types': len(evidence_types)
    }

    return results

if __name__ == "__main__":
    result = get_alzheimers_therapeutic_targets()

    if 'error' in result:
        print(f"\nError: {result['error']}")
    else:
        print(f"\n{'='*80}")
        print("ALZHEIMER'S DISEASE THERAPEUTIC TARGETS WITH GENETIC EVIDENCE")
        print(f"{'='*80}\n")

        summary = result['summary']
        print(f"Disease: {summary['disease']}")
        print(f"Total Targets: {summary['total_targets']}")
        print(f"Targets with Genetic Evidence: {summary['targets_with_genetic_evidence']}")
        print(f"Average Association Score: {summary['avg_association_score']}")
        print(f"Average Genetic Evidence Score: {summary['avg_genetic_evidence_score']}")
        print(f"\nEvidence Types Found: {', '.join(summary['evidence_types'])}\n")

        print(f"{'='*80}")
        print("TOP TARGETS BY GENETIC EVIDENCE")
        print(f"{'='*80}\n")

        for idx, target in enumerate(result['genetic_targets'][:10], 1):
            print(f"{idx}. Target ID: {target['target_id']}")
            print(f"   Overall Score: {target['association_score']}")
            print(f"   Genetic Evidence: {target['genetic_evidence_score']}")
            print(f"   Evidence Types: {list(target['datatype_scores'].keys())}\n")
