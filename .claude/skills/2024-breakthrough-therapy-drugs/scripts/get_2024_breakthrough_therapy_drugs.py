import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs
from datetime import datetime

def get_2024_breakthrough_therapy_drugs():
    """Get all FDA-approved drugs from 2024."""
    
    result = search_drugs(search='approval_date:[20240101 TO 20241231]', limit=1000)
    
    if not result or 'results' not in result:
        return {'total_count': 0, 'drugs': [], 'summary': 'No drugs found approved in 2024'}
    
    all_drugs = result.get('results', [])
    drugs_2024 = []
    
    for drug in all_drugs:
        openfda = drug.get('openfda', {})
        
        approval_date = None
        submissions = drug.get('submissions', [])
        
        for submission in submissions:
            if submission.get('submission_status') == 'AP':
                date_str = submission.get('submission_status_date')
                if date_str:
                    try:
                        approval_date = datetime.strptime(date_str, "%Y%m%d")
                        break
                    except:
                        pass
        
        if approval_date and approval_date.year == 2024:
            drug_info = {
                'brand_name': openfda.get('brand_name', ['Unknown'])[0] if openfda.get('brand_name') else 'Unknown',
                'generic_name': openfda.get('generic_name', ['Unknown'])[0] if openfda.get('generic_name') else 'Unknown',
                'manufacturer': openfda.get('manufacturer_name', ['Unknown'])[0] if openfda.get('manufacturer_name') else 'Unknown',
                'application_number': openfda.get('application_number', ['Unknown'])[0] if openfda.get('application_number') else 'Unknown',
                'approval_date': approval_date.strftime("%Y-%m-%d"),
                'product_type': openfda.get('product_type', ['Unknown'])[0] if openfda.get('product_type') else 'Unknown',
                'route': openfda.get('route', ['Unknown'])[0] if openfda.get('route') else 'Unknown',
                'pharm_class': openfda.get('pharm_class_epc', [])
            }
            
            drugs_2024.append(drug_info)
    
    drugs_2024.sort(key=lambda x: x['approval_date'], reverse=True)
    
    manufacturers_count = {}
    for drug in drugs_2024:
        mfr = drug['manufacturer']
        manufacturers_count[mfr] = manufacturers_count.get(mfr, 0) + 1
    
    top_manufacturers = sorted(manufacturers_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    summary = {
        'total_drugs_2024': len(drugs_2024),
        'top_manufacturers': dict(top_manufacturers)
    }
    
    return {'total_count': len(drugs_2024), 'drugs': drugs_2024, 'summary': summary}

if __name__ == "__main__":
    result = get_2024_breakthrough_therapy_drugs()
    print(f"Total FDA Approvals in 2024: {result['summary']['total_drugs_2024']}")
    for mfr, count in list(result['summary']['top_manufacturers'].items())[:5]:
        print(f"  • {mfr}: {count} drug(s)")
