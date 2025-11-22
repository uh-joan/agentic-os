import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_diabetes_recruiting_trials():
    """Get all recruiting diabetes clinical trials with categorization."""
    all_trials = []
    page_token = None
    page_count = 0
    
    phase_counts = {}
    diabetes_type_counts = {'Type 1': 0, 'Type 2': 0, 'Gestational': 0, 'Other/Unspecified': 0}
    
    while True:
        page_count += 1
        if page_token:
            result = search(query="diabetes", recruitmentStatus="RECRUITING", pageSize=1000, pageToken=page_token)
        else:
            result = search(query="diabetes", recruitmentStatus="RECRUITING", pageSize=1000)
        
        if not result or not isinstance(result, str):
            break
            
        trials = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)[1:]
        
        for trial_text in trials:
            trial_data = {}
            
            nct_match = re.search(r'NCT\d{8}', trial_text)
            if nct_match:
                trial_data['nct_id'] = nct_match.group(0)
            
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_text)
            if phase_match:
                phase = phase_match.group(1).strip()
                trial_data['phase'] = phase
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
            else:
                trial_data['phase'] = 'Not Specified'
                phase_counts['Not Specified'] = phase_counts.get('Not Specified', 0) + 1
            
            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', trial_text)
            if conditions_match:
                conditions = conditions_match.group(1).strip()
                conditions_lower = conditions.lower()
                
                if 'type 1' in conditions_lower or 't1d' in conditions_lower:
                    diabetes_type_counts['Type 1'] += 1
                    trial_data['diabetes_type'] = 'Type 1'
                elif 'type 2' in conditions_lower or 't2d' in conditions_lower:
                    diabetes_type_counts['Type 2'] += 1
                    trial_data['diabetes_type'] = 'Type 2'
                elif 'gestational' in conditions_lower or 'gdm' in conditions_lower:
                    diabetes_type_counts['Gestational'] += 1
                    trial_data['diabetes_type'] = 'Gestational'
                else:
                    diabetes_type_counts['Other/Unspecified'] += 1
                    trial_data['diabetes_type'] = 'Other/Unspecified'
            
            all_trials.append(trial_data)
        
        next_token_match = re.search(r'nextPageToken:\s*"([^"]+)"', result)
        if next_token_match and len(trials) > 0:
            page_token = next_token_match.group(1)
        else:
            break
    
    return {
        'total_count': len(all_trials),
        'pages_retrieved': page_count,
        'trials': all_trials,
        'phase_distribution': dict(sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)),
        'diabetes_type_distribution': dict(sorted(diabetes_type_counts.items(), key=lambda x: x[1], reverse=True))
    }

if __name__ == "__main__":
    result = get_diabetes_recruiting_trials()
    print(f"\nDiabetes Recruiting Trials: {result['total_count']:,} trials, {result['pages_retrieved']} pages")
    print(f"Type distribution: {result['diabetes_type_distribution']}")
