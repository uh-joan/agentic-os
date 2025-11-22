import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_statistics
from mcp.servers.datacommons_mcp import get_population

def get_cvd_burden_per_capita():
    """Calculate CVD burden per capita by combining WHO and Data Commons data."""
    
    countries = [
        "United States", "United Kingdom", "Germany", "France", "Italy",
        "Spain", "Canada", "Australia", "Japan", "China",
        "India", "Brazil", "Mexico", "Russia", "South Africa"
    ]
    
    cvd_burden = []
    data_availability = {'total_countries': len(countries), 'who_success': 0, 
                        'dc_success': 0, 'both_success': 0, 'details': []}
    
    for country in countries:
        country_status = {'country': country, 'who_available': False, 
                         'dc_available': False, 'cvd_deaths': None, 'population': None}
        
        try:
            who_result = get_health_statistics(indicator="cardiovascular_disease_deaths", country=country)
            cvd_deaths = None
            
            if isinstance(who_result, dict):
                if 'value' in who_result:
                    cvd_deaths = who_result['value']
                    country_status['who_available'] = True
                elif 'data' in who_result and isinstance(who_result['data'], list):
                    if len(who_result['data']) > 0:
                        cvd_deaths = who_result['data'][0].get('value')
                        country_status['who_available'] = True
            elif isinstance(who_result, (int, float)):
                cvd_deaths = who_result
                country_status['who_available'] = True
            
            country_status['cvd_deaths'] = cvd_deaths
            if cvd_deaths:
                data_availability['who_success'] += 1
        except Exception as e:
            print(f"WHO error for {country}: {str(e)}")
        
        try:
            dc_result = get_population(location=country)
            population = None
            
            if isinstance(dc_result, dict):
                if 'population' in dc_result:
                    population = dc_result['population']
                    country_status['dc_available'] = True
                elif 'value' in dc_result:
                    population = dc_result['value']
                    country_status['dc_available'] = True
            elif isinstance(dc_result, (int, float)):
                population = dc_result
                country_status['dc_available'] = True
            
            country_status['population'] = population
            if population:
                data_availability['dc_success'] += 1
        except Exception as e:
            print(f"Data Commons error for {country}: {str(e)}")
        
        if cvd_deaths and population and cvd_deaths > 0 and population > 0:
            deaths_per_100k = (cvd_deaths / population) * 100000
            cvd_burden.append({
                'country': country,
                'cvd_deaths': int(cvd_deaths),
                'population': int(population),
                'deaths_per_100k': round(deaths_per_100k, 2)
            })
            data_availability['both_success'] += 1
        
        data_availability['details'].append(country_status)
    
    cvd_burden.sort(key=lambda x: x['deaths_per_100k'], reverse=True)
    
    if cvd_burden:
        avg_burden = sum(c['deaths_per_100k'] for c in cvd_burden) / len(cvd_burden)
        summary = {
            'countries_with_complete_data': len(cvd_burden),
            'average_burden_per_100k': round(avg_burden, 2),
            'highest_burden': {'country': cvd_burden[0]['country'], 'rate': cvd_burden[0]['deaths_per_100k']},
            'lowest_burden': {'country': cvd_burden[-1]['country'], 'rate': cvd_burden[-1]['deaths_per_100k']}
        }
    else:
        summary = {'countries_with_complete_data': 0, 
                  'note': 'No countries had both WHO and Data Commons data'}
    
    return {'cvd_burden_data': cvd_burden, 'summary': summary, 'data_availability': data_availability}

if __name__ == "__main__":
    result = get_cvd_burden_per_capita()
    print(f"\nCVD Burden Analysis: {result['data_availability']['total_countries']} countries")
    print(f"Complete data: {result['data_availability']['both_success']} countries")
