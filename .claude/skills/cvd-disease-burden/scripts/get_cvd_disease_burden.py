import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_stats

def get_cvd_disease_burden():
    """Get WHO cardiovascular disease burden data globally.
    
    Returns:
        dict: Contains total_records, indicators, and summary statistics
    """
    
    search_terms = [
        "cardiovascular disease mortality",
        "cardiovascular disease death rate",
        "heart disease",
        "stroke",
        "ischemic heart disease"
    ]
    
    all_indicators = []
    unique_indicators = set()
    
    for term in search_terms:
        try:
            result = get_health_stats(indicator=term, country="all")
            
            if isinstance(result, dict):
                if 'value' in result:
                    indicators = [result]
                elif 'fact' in result:
                    indicators = result['fact']
                else:
                    indicators = []
                
                for indicator in indicators:
                    indicator_key = f"{indicator.get('GHO', '')}_{indicator.get('COUNTRY', '')}_{indicator.get('YEAR', '')}"
                    if indicator_key not in unique_indicators:
                        unique_indicators.add(indicator_key)
                        all_indicators.append(indicator)
        
        except Exception as e:
            print(f"Warning: Error fetching {term}: {str(e)}")
            continue
    
    countries = set()
    years = set()
    indicator_codes = set()
    
    for ind in all_indicators:
        if 'COUNTRY' in ind:
            countries.add(ind['COUNTRY'])
        if 'YEAR' in ind:
            years.add(ind['YEAR'])
        if 'GHO' in ind:
            indicator_codes.add(ind['GHO'])
    
    death_rates = []
    for ind in all_indicators:
        if 'Numeric' in ind and ind['Numeric']:
            try:
                death_rates.append(float(ind['Numeric']))
            except (ValueError, TypeError):
                pass
    
    avg_rate = sum(death_rates) / len(death_rates) if death_rates else 0
    
    summary = {
        'total_records': len(all_indicators),
        'unique_countries': len(countries),
        'year_range': f"{min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}",
        'indicator_types': len(indicator_codes),
        'average_death_rate': round(avg_rate, 2) if death_rates else 0,
        'indicators_found': list(indicator_codes)[:10]
    }
    
    return {'total_records': len(all_indicators), 'data': all_indicators, 'summary': summary}

if __name__ == "__main__":
    result = get_cvd_disease_burden()
    
    print(f"\n{'='*60}")
    print("WHO Cardiovascular Disease Burden Data")
    print(f"{'='*60}\n")
    
    print(f"Total Records: {result['summary']['total_records']}")
    print(f"Countries: {result['summary']['unique_countries']}")
    print(f"Year Range: {result['summary']['year_range']}")
