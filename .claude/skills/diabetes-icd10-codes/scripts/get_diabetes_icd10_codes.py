import sys
sys.path.insert(0, ".claude")
from mcp.servers.nlm_codes_mcp import search_icd10

def get_diabetes_icd10_codes():
    """Get all ICD-10 diagnosis codes for diabetes mellitus.
    
    Returns:
        dict: Contains total_count, codes by category, and summary
    """
    
    print("Searching for diabetes ICD-10 codes...")
    result = search_icd10(search_term="diabetes mellitus")
    
    if not result or not isinstance(result, dict):
        return {'total_count': 0, 'categories': {}, 'summary': 'No diabetes ICD-10 codes found'}
    
    codes_data = result.get('data', [])
    total_count = len(codes_data)
    
    categories = {
        'Type 1 Diabetes': [],
        'Type 2 Diabetes': [],
        'Gestational Diabetes': [],
        'Drug/Chemical Induced': [],
        'Other Specified Diabetes': [],
        'Unspecified Diabetes': [],
        'Complications': [],
        'Other': []
    }
    
    for item in codes_data:
        code = item.get('code', '')
        description = item.get('description', '')
        desc_lower = description.lower()
        
        if 'type 1' in desc_lower or 'type i' in desc_lower:
            categories['Type 1 Diabetes'].append({'code': code, 'description': description})
        elif 'type 2' in desc_lower or 'type ii' in desc_lower:
            categories['Type 2 Diabetes'].append({'code': code, 'description': description})
        elif 'gestational' in desc_lower:
            categories['Gestational Diabetes'].append({'code': code, 'description': description})
        elif 'drug' in desc_lower or 'chemical' in desc_lower or 'induced' in desc_lower:
            categories['Drug/Chemical Induced'].append({'code': code, 'description': description})
        elif 'complication' in desc_lower or 'with' in desc_lower:
            categories['Complications'].append({'code': code, 'description': description})
        elif 'other specified' in desc_lower:
            categories['Other Specified Diabetes'].append({'code': code, 'description': description})
        elif 'unspecified' in desc_lower:
            categories['Unspecified Diabetes'].append({'code': code, 'description': description})
        else:
            categories['Other'].append({'code': code, 'description': description})
    
    summary_lines = [f"Total ICD-10 codes found: {total_count}", "", "Breakdown by category:"]
    
    for category, codes in categories.items():
        if codes:
            summary_lines.append(f"  {category}: {len(codes)} codes")
    
    summary = "\n".join(summary_lines)
    
    return {'total_count': total_count, 'categories': categories, 'summary': summary}

if __name__ == "__main__":
    result = get_diabetes_icd10_codes()
    print(result['summary'])
