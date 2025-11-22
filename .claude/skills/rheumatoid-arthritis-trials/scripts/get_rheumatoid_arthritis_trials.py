import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_rheumatoid_arthritis_trials():
    """Get comprehensive rheumatoid arthritis clinical trials with full pagination."""
    all_trials = []
    page_token = None
    page_count = 0
    
    while True:
        page_count += 1
        if page_token:
            result = search(term="rheumatoid arthritis", pageSize=1000, pageToken=page_token)
        else:
            result = search(term="rheumatoid arthritis", pageSize=1000)
        
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)
        
        for block in trial_blocks[1:]:
            trial = {}
            nct_match = re.search(r'NCT\d{8}', result[result.find(block)-20:result.find(block)])
            if nct_match:
                trial['nct_id'] = nct_match.group()
            
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n|$)', block)
            if title_match:
                trial['title'] = title_match.group(1).strip()
            
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', block)
            if status_match:
                trial['status'] = status_match.group(1).strip()
            
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|$)', block)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()
            
            all_trials.append(trial)
        
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1)
        else:
            break
    
    phase_dist = {}
    status_dist = {}
    for trial in all_trials:
        phase = trial.get('phase', 'Not specified')
        phase_dist[phase] = phase_dist.get(phase, 0) + 1
        status = trial.get('status', 'Unknown')
        status_dist[status] = status_dist.get(status, 0) + 1
    
    return {
        'total_count': len(all_trials),
        'data': all_trials,
        'summary': {
            'total_trials': len(all_trials),
            'pages_fetched': page_count,
            'phase_distribution': dict(sorted(phase_dist.items(), key=lambda x: x[1], reverse=True)),
            'status_distribution': dict(sorted(status_dist.items(), key=lambda x: x[1], reverse=True))
        }
    }

if __name__ == "__main__":
    result = get_rheumatoid_arthritis_trials()
    print(f"\nRA Trials: {result['summary']['total_trials']} trials, {result['summary']['pages_fetched']} pages")
    print(f"Phase distribution: {result['summary']['phase_distribution']}")
