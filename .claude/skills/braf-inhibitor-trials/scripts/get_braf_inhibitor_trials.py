import sys
import re
from collections import Counter
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_braf_inhibitor_trials():
    """Get all BRAF inhibitor clinical trials with pagination."""
    
    all_trials = []
    page_token = None
    
    while True:
        if page_token:
            result = search(term="BRAF inhibitor", pageSize=1000, pageToken=page_token)
        else:
            result = search(term="BRAF inhibitor", pageSize=1000)
        
        trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)
        
        for i in range(1, len(trial_blocks), 2):
            if i + 1 < len(trial_blocks):
                nct_id = trial_blocks[i]
                block = trial_blocks[i + 1]
                
                title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
                phases_match = re.search(r'\*\*Phases:\*\*\s*(.+?)(?:\n|$)', block)
                status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', block)
                
                trial = {
                    'nct_id': nct_id,
                    'title': title_match.group(1).strip() if title_match else '',
                    'phases': phases_match.group(1).strip() if phases_match else '',
                    'status': status_match.group(1).strip() if status_match else ''
                }
                all_trials.append(trial)
        
        page_token_match = re.search(r'Page Token:\s*`([^`]+)`', result)
        if page_token_match:
            page_token = page_token_match.group(1)
        else:
            break
    
    phase_counts = Counter([t['phases'] for t in all_trials if t['phases']])
    
    return {
        'total_count': len(all_trials),
        'phase_distribution': dict(phase_counts),
        'trials': all_trials
    }

if __name__ == "__main__":
    result = get_braf_inhibitor_trials()
    print(f"BRAF inhibitor trials: {result['total_count']} total")
    print(f"Phase distribution: {result['phase_distribution']}")
