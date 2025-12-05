import sys
sys.path.insert(0, ".claude")
from datetime import datetime
from mcp.servers.opentargets_mcp import search_diseases, get_disease_targets_summary

def get_alzheimers_therapeutic_targets():
    """Get top therapeutic targets for Alzheimer's disease with genetic evidence.

    Focuses on targets with strong genetic evidence scores, which are most
    likely to be valid therapeutic targets.

    Returns:
        dict: Contains disease info, top targets with genetic evidence, and summary statistics
    """
    results = {'disease_info': {}, 'top_targets': [], 'genetic_targets': [], 'summary': {}}

    # print("Searching for Alzheimer's disease...")  # Disabled for JSON output
    disease_results = search_diseases(query="Alzheimer's disease", size=5)

    if not disease_results or 'data' not in disease_results:
        return {
            'data': {},
            'source_metadata': {
                'source': 'Open Targets Platform',
                'mcp_server': 'opentargets_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'disease_query': "Alzheimer's disease"
                },
                'data_count': 0,
                'data_type': 'therapeutic_targets'
            },
            'summary': f"No disease data found (source: Open Targets Platform, {datetime.now().strftime('%Y-%m-%d')})",
            'error': 'No disease data found'
        }

    diseases = disease_results.get('data', {}).get('search', {}).get('hits', [])
    if not diseases:
        return {
            'data': {},
            'source_metadata': {
                'source': 'Open Targets Platform',
                'mcp_server': 'opentargets_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'disease_query': "Alzheimer's disease"
                },
                'data_count': 0,
                'data_type': 'therapeutic_targets'
            },
            'summary': f"No matching diseases found (source: Open Targets Platform, {datetime.now().strftime('%Y-%m-%d')})",
            'error': 'No matching diseases found'
        }

    disease = diseases[0]
    disease_id = disease.get('id', '')
    disease_name = disease.get('name', '')

    results['disease_info'] = {
        'id': disease_id,
        'name': disease_name,
        'description': disease.get('description', 'N/A')
    }

    # print(f"Found disease: {disease_name} ({disease_id})")  # Disabled for JSON output

    # print("Retrieving associated therapeutic targets...")  # Disabled for JSON output
    targets_results = get_disease_targets_summary(diseaseId=disease_id, minScore=0.0, size=50)

    if not targets_results or 'data' not in targets_results:
        return {
            'data': {'disease_info': results['disease_info']},
            'source_metadata': {
                'source': 'Open Targets Platform',
                'mcp_server': 'opentargets_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'disease_query': "Alzheimer's disease",
                    'disease_id': disease_id
                },
                'data_count': 0,
                'data_type': 'therapeutic_targets'
            },
            'summary': f"No target associations found for {disease_name} (source: Open Targets Platform, {datetime.now().strftime('%Y-%m-%d')})",
            'error': 'No target associations found'
        }

    associations = targets_results.get('data', [])

    if not associations:
        return {
            'data': {'disease_info': results['disease_info']},
            'source_metadata': {
                'source': 'Open Targets Platform',
                'mcp_server': 'opentargets_mcp',
                'query_date': datetime.now().strftime('%Y-%m-%d'),
                'query_params': {
                    'disease_query': "Alzheimer's disease",
                    'disease_id': disease_id
                },
                'data_count': 0,
                'data_type': 'therapeutic_targets'
            },
            'summary': f"No target associations in response for {disease_name} (source: Open Targets Platform, {datetime.now().strftime('%Y-%m-%d')})",
            'error': 'No target associations in response'
        }

    # print(f"Found {len(associations)} target associations")  # Disabled for JSON output

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

    return {
        'data': results,
        'source_metadata': {
            'source': 'Open Targets Platform',
            'mcp_server': 'opentargets_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {
                'disease_query': "Alzheimer's disease",
                'min_score': 0.0,
                'max_targets': 50
            },
            'data_count': total_targets,
            'data_type': 'therapeutic_targets'
        },
        'summary': f"Found {total_targets} therapeutic targets for {disease_name}, {len(genetic_targets)} with genetic evidence (source: Open Targets Platform, {datetime.now().strftime('%Y-%m-%d')})"
    }

if __name__ == "__main__":
    import json
    result = get_alzheimers_therapeutic_targets()

    # For JSON verification (required by verify_source_attribution.py)
    print(json.dumps(result, indent=2))
