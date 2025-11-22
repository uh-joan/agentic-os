import sys
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_disease, get_associated_targets

def get_alzheimers_genetic_targets():
    """Get genetic targets and drug associations for Alzheimer's disease.
    
    Returns:
        dict: Contains summary statistics and top targets with evidence
    """
    results = {'disease_info': {}, 'top_targets': [], 'summary': {}}
    
    print("Searching for Alzheimer's disease...")
    disease_results = search_disease(query="Alzheimer's disease", size=5)
    
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
    
    print("Retrieving associated genetic targets...")
    targets_results = get_associated_targets(disease_id=disease_id, size=20)
    
    if not targets_results or 'data' not in targets_results:
        return {'disease_info': results['disease_info'], 'error': 'No target associations found'}
    
    associations = targets_results.get('data', {}).get('disease', {}).get('associatedTargets', {}).get('rows', [])
    
    if not associations:
        return {'disease_info': results['disease_info'], 'error': 'No target associations in response'}
    
    print(f"Found {len(associations)} target associations")
    
    top_targets = []
    for assoc in associations[:10]:
        target = assoc.get('target', {})
        target_info = {
            'gene_symbol': target.get('approvedSymbol', 'N/A'),
            'gene_name': target.get('approvedName', 'N/A'),
            'target_id': target.get('id', 'N/A'),
            'association_score': round(assoc.get('score', 0), 4),
            'evidence_count': len(assoc.get('datatypeScores', [])),
            'datatype_scores': {}
        }
        
        for dt_score in assoc.get('datatypeScores', []):
            datatype = dt_score.get('componentId', 'unknown')
            score = round(dt_score.get('score', 0), 4)
            target_info['datatype_scores'][datatype] = score
        
        top_targets.append(target_info)
    
    results['top_targets'] = top_targets
    
    total_targets = len(associations)
    avg_score = sum(t['association_score'] for t in top_targets) / len(top_targets) if top_targets else 0
    
    evidence_types = set()
    for target in top_targets:
        evidence_types.update(target['datatype_scores'].keys())
    
    results['summary'] = {
        'disease': disease_name,
        'disease_id': disease_id,
        'total_targets': total_targets,
        'top_targets_shown': len(top_targets),
        'avg_association_score': round(avg_score, 4),
        'evidence_types': sorted(list(evidence_types)),
        'num_evidence_types': len(evidence_types)
    }
    
    return results

if __name__ == "__main__":
    result = get_alzheimers_genetic_targets()
    
    if 'error' in result:
        print(f"\nError: {result['error']}")
    else:
        print(f"\n{'='*80}")
        print("ALZHEIMER'S DISEASE GENETIC TARGETS")
        print(f"{'='*80}\n")
        
        summary = result['summary']
        print(f"Total Targets: {summary['total_targets']}")
        print(f"Average Score: {summary['avg_association_score']}")
        print(f"Evidence Types: {summary['num_evidence_types']}\n")
        
        for idx, target in enumerate(result['top_targets'][:5], 1):
            print(f"{idx}. {target['gene_symbol']} - Score: {target['association_score']}")
