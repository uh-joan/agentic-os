import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs

def get_adc_fda_drugs():
    """Get all FDA approved antibody-drug conjugate (ADC) drugs."""
    
    adc_terms = ["antibody-drug conjugate", "antibody drug conjugate", "ADC"]
    all_results = []
    
    for term in adc_terms:
        result = search_drugs(search_term=term, limit=100)
        if result and 'results' in result:
            all_results.extend(result['results'])
    
    # Deduplicate by generic name
    unique_drugs = {}
    for drug in all_results:
        openfda = drug.get('openfda', {})
        generic_name = openfda.get('generic_name', [])
        
        if generic_name:
            key = generic_name[0].lower()
            if key not in unique_drugs:
                unique_drugs[key] = {
                    'generic_name': generic_name[0],
                    'brand_name': openfda.get('brand_name', [''])[0],
                    'manufacturer': openfda.get('manufacturer_name', [''])[0],
                    'approval_date': drug.get('effective_time', 'Unknown')
                }
    
    drugs_list = list(unique_drugs.values())
    
    return {
        'total_count': len(drugs_list),
        'adc_drugs': drugs_list
    }

if __name__ == "__main__":
    result = get_adc_fda_drugs()
    print(f"ADC approved drugs: {result['total_count']} unique drugs")
    for drug in result['adc_drugs']:
        print(f"  {drug['brand_name']} ({drug['generic_name']}) - {drug['manufacturer']}")
