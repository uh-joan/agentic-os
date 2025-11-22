import sys
import re
from collections import Counter
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_checkpoint_inhibitor_combination_therapies():
    """Analyze combination therapy patterns in checkpoint inhibitor trials."""
    all_trials = []
    page_token = None
    
    while True:
        if page_token:
            result = search(term="checkpoint inhibitor", pageSize=1000, pageToken=page_token)
        else:
            result = search(term="checkpoint inhibitor", pageSize=1000)
        
        if not result or not isinstance(result, str):
            break
            
        trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)
        
        for i in range(1, len(trial_blocks), 2):
            if i + 1 < len(trial_blocks):
                nct_id = trial_blocks[i]
                content = trial_blocks[i + 1]
                
                trial_data = {'nct_id': nct_id, 'title': '', 'interventions': [], 'phase': '', 'status': ''}
                
                title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', content, re.DOTALL)
                if title_match:
                    trial_data['title'] = title_match.group(1).strip()
                
                interventions_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', content, re.DOTALL)
                if interventions_match:
                    interventions_text = interventions_match.group(1).strip()
                    intervention_items = re.findall(r'(?:Drug|Biological|Procedure|Other):\s*([^\n]+)', interventions_text)
                    trial_data['interventions'] = [item.strip() for item in intervention_items]
                
                phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|\Z)', content)
                if phase_match:
                    trial_data['phase'] = phase_match.group(1).strip()
                
                status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|\Z)', content)
                if status_match:
                    trial_data['status'] = status_match.group(1).strip()
                
                all_trials.append(trial_data)
        
        token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if token_match:
            page_token = token_match.group(1)
        else:
            break
    
    combination_patterns = []
    checkpoint_inhibitors = []
    partner_drugs = []
    phase_distribution = Counter()
    
    ci_keywords = ['pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab', 'avelumab',
                   'cemiplimab', 'dostarlimab', 'anti-PD-1', 'anti-PD-L1', 'anti-CTLA-4',
                   'ipilimumab', 'tremelimumab', 'PD-1', 'PD-L1', 'CTLA-4']
    
    for trial in all_trials:
        if len(trial['interventions']) >= 2:
            trial_cis = []
            trial_partners = []
            
            for intervention in trial['interventions']:
                intervention_lower = intervention.lower()
                is_ci = any(keyword.lower() in intervention_lower for keyword in ci_keywords)
                
                if is_ci:
                    trial_cis.append(intervention)
                    checkpoint_inhibitors.append(intervention)
                else:
                    trial_partners.append(intervention)
                    partner_drugs.append(intervention)
            
            if trial_cis and trial_partners:
                combination_patterns.append({
                    'nct_id': trial['nct_id'],
                    'checkpoint_inhibitors': trial_cis,
                    'partner_drugs': trial_partners,
                    'phase': trial['phase'],
                    'status': trial['status']
                })
                
                if trial['phase']:
                    phase_distribution[trial['phase']] += 1
    
    ci_counter = Counter(checkpoint_inhibitors)
    partner_counter = Counter(partner_drugs)
    
    summary = {
        'total_trials': len(all_trials),
        'combination_trials': len(combination_patterns),
        'top_checkpoint_inhibitors': ci_counter.most_common(10),
        'top_partner_drugs': partner_counter.most_common(20),
        'phase_distribution': dict(phase_distribution.most_common()),
        'combination_patterns': combination_patterns[:50]
    }
    
    summary_text = f"""Checkpoint Inhibitor Combination Therapy Analysis
=================================================

Total Trials Found: {len(all_trials)}
Combination Trials: {len(combination_patterns)} ({len(combination_patterns)/len(all_trials)*100:.1f}% of all trials)

Top Checkpoint Inhibitors:
"""
    for ci, count in ci_counter.most_common(10):
        summary_text += f"  • {ci}: {count} trials\n"
    
    summary_text += f"\nTop Partner Drug Classes (Most Common Combinations):\n"
    for partner, count in partner_counter.most_common(20):
        summary_text += f"  • {partner}: {count} trials\n"
    
    summary_text += f"\nPhase Distribution of Combination Trials:\n"
    for phase, count in sorted(phase_distribution.items(), key=lambda x: x[1], reverse=True):
        summary_text += f"  • {phase}: {count} trials\n"
    
    return {
        'total_count': len(all_trials),
        'summary': summary_text,
        'data': summary
    }

if __name__ == "__main__":
    result = get_checkpoint_inhibitor_combination_therapies()
    print(result['summary'])
