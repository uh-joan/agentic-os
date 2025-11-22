import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_egfr_inhibitor_trials():
    """Get EGFR inhibitor clinical trials across all phases."""
    all_trials = []
    page_token = None
    page_count = 0
    
    while True:
        page_count += 1
        if page_token:
            result = search(term="EGFR inhibitor", pageSize=1000, pageToken=page_token)
        else:
            result = search(term="EGFR inhibitor", pageSize=1000)
        
        trials_text = result if isinstance(result, str) else str(result)
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', trials_text)
        
        for block in trial_blocks[1:]:
            trial = {}
            nct_match = re.search(r'NCT\d{8}', trials_text[trials_text.find(block)-20:trials_text.find(block)])
            if nct_match:
                trial['nct_id'] = nct_match.group(0)
            
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if title_match:
                trial['title'] = title_match.group(1).strip()
            
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|\Z)', block)
            if status_match:
                trial['status'] = status_match.group(1).strip()
            
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|\Z)', block)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()
            
            if trial:
                all_trials.append(trial)
        
        page_token_match = re.search(r'pageToken:\s*"([^"]+)"', trials_text)
        if page_token_match:
            page_token = page_token_match.group(1)
        else:
            break
    
    total_count = len(all_trials)
    phases = {}
    statuses = {}
    
    for trial in all_trials:
        phase = trial.get('phase', 'Not Specified')
        phases[phase] = phases.get(phase, 0) + 1
        status = trial.get('status', 'Unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    summary = {
        'total_trials': total_count,
        'pages_fetched': page_count,
        'phase_distribution': dict(sorted(phases.items(), key=lambda x: x[1], reverse=True)),
        'status_distribution': dict(sorted(statuses.items(), key=lambda x: x[1], reverse=True))
    }
    
    return {'total_count': total_count, 'data': all_trials, 'summary': summary}

if __name__ == "__main__":
    result = get_egfr_inhibitor_trials()
    print(f"\nEGFR Inhibitor Trials: {result['summary']['total_trials']} trials, {result['summary']['pages_fetched']} pages")
    print(f"Phase distribution: {result['summary']['phase_distribution']}")
