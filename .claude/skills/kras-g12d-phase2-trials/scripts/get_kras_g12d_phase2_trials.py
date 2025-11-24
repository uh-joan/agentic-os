import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_kras_g12d_phase2_trials():
    """Get KRAS G12D inhibitor Phase 2 trials."""
    result = search(query="KRAS G12D", filter_phase="PHASE2", pageSize=100)
    
    trials = []
    if result:
        trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)
        for i in range(1, len(trial_blocks), 2):
            if i + 1 < len(trial_blocks):
                nct_id = trial_blocks[i]
                content = trial_blocks[i + 1]
                trial_data = {'nct_id': nct_id}
                
                for field, pattern in [
                    ('title', r'\*\*Title:\*\*\s*(.+?)(?:\n|$)'),
                    ('sponsor', r'\*\*Sponsor:\*\*\s*(.+?)(?:\n|$)'),
                    ('status', r'\*\*Status:\*\*\s*(.+?)(?:\n|$)'),
                    ('start_date', r'\*\*Start Date:\*\*\s*(.+?)(?:\n|$)'),
                    ('enrollment', r'\*\*Enrollment:\*\*\s*(.+?)(?:\n|$)')
                ]:
                    match = re.search(pattern, content)
                    if match:
                        trial_data[field] = match.group(1).strip()
                
                trials.append(trial_data)
    
    return {'total_count': len(trials), 'trials': trials}

if __name__ == "__main__":
    result = get_kras_g12d_phase2_trials()
    print(f"Total KRAS G12D Phase 2 trials: {result['total_count']}")
    for t in result['trials'][:5]:
        print(f"  {t['nct_id']}: {t.get('sponsor', 'N/A')} - {t.get('status', 'N/A')}")
