import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_disease, get_associated_targets
from mcp.servers.ct_gov_mcp import search

def get_ra_targets_and_trials():
    """Get top 10 genetic targets for RA and match with recruiting trials."""
    
    # Get RA disease ID from Open Targets
    disease_result = search_disease(query="rheumatoid arthritis", size=5)
    disease_id = None
    disease_name = None
    
    if disease_result and 'data' in disease_result:
        data = disease_result['data']
        if 'search' in data and 'hits' in data['search']:
            for hit in data['search']['hits']:
                if hit.get('entity') == 'disease':
                    disease_id = hit.get('id')
                    disease_name = hit.get('name')
                    break
    
    if not disease_id:
        return {'success': False, 'error': 'Could not find RA disease ID'}
    
    # Get associated targets
    targets_result = get_associated_targets(disease_id=disease_id, size=10)
    targets_data = []
    
    if targets_result and 'data' in targets_result:
        data = targets_result['data']
        if 'disease' in data and 'associatedTargets' in data['disease']:
            rows = data['disease']['associatedTargets'].get('rows', [])
            for row in rows:
                target = row.get('target', {})
                targets_data.append({
                    'gene_symbol': target.get('approvedSymbol', 'N/A'),
                    'gene_name': target.get('approvedName', 'N/A'),
                    'overall_score': row.get('score', 0),
                    'trial_count': 0
                })
    
    # Get recruiting RA trials
    all_trials = []
    page_token = None
    
    while True:
        if page_token:
            ct_result = search(query="rheumatoid arthritis", filter_overallStatus="RECRUITING", 
                             pageSize=1000, pageToken=page_token)
        else:
            ct_result = search(query="rheumatoid arthritis", filter_overallStatus="RECRUITING", 
                             pageSize=1000)
        
        if not ct_result:
            break
        
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', ct_result)
        all_trials.extend([block for block in trial_blocks if block.strip()])
        
        token_match = re.search(r'pageToken:\s*"([^"]+)"', ct_result)
        if token_match:
            page_token = token_match.group(1)
        else:
            break
    
    # Match trials to targets
    for target in targets_data:
        gene_symbol = target['gene_symbol'].upper()
        trial_count = sum(1 for trial in all_trials if gene_symbol in trial.upper())
        target['trial_count'] = trial_count
    
    targets_data.sort(key=lambda x: x['overall_score'], reverse=True)
    targets_with_trials = sum(1 for t in targets_data if t['trial_count'] > 0)
    
    return {
        'success': True,
        'disease_name': disease_name,
        'total_targets': len(targets_data),
        'total_trials': len(all_trials),
        'targets_with_trials': targets_with_trials,
        'targets_data': targets_data
    }

if __name__ == "__main__":
    result = get_ra_targets_and_trials()
    if result.get('success'):
        print(f"RA Targets & Trials: {result['total_targets']} targets, {result['total_trials']} trials")
        print(f"Targets with trials: {result['targets_with_trials']}")
