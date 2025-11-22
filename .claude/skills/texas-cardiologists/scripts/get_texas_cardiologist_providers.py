import sys
sys.path.insert(0, ".claude")
from mcp.servers.healthcare_mcp import search_providers

def get_texas_cardiologist_providers():
    """Get Medicare provider data for cardiologists practicing in Texas.
    
    Returns:
        dict: Contains total_count, providers list, and statistics
    """
    result = search_providers(specialty="Cardiology", state="TX", limit=1000)
    
    if not result or 'providers' not in result:
        return {'total_count': 0, 'providers': [], 'summary': 'No providers found'}
    
    providers = result.get('providers', [])
    total_count = len(providers)
    
    total_services = sum(p.get('total_services', 0) for p in providers)
    total_beneficiaries = sum(p.get('beneficiary_count', 0) for p in providers)
    total_payments = sum(p.get('total_payment', 0) for p in providers)
    
    city_counts = {}
    for p in providers:
        city = p.get('city', 'Unknown')
        city_counts[city] = city_counts.get(city, 0) + 1
    
    top_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    summary = f"""Texas Cardiologist Medicare Providers

Total Providers: {total_count:,}
Total Services: {total_services:,}
Total Beneficiaries: {total_beneficiaries:,}
Total Medicare Payments: ${total_payments:,.2f}

Top 10 Cities:"""
    
    for city, count in top_cities:
        pct = (count / total_count * 100) if total_count > 0 else 0
        summary += f"\n  {city}: {count} providers ({pct:.1f}%)"
    
    return {
        'total_count': total_count,
        'providers': providers,
        'summary': summary,
        'statistics': {'total_services': total_services, 'total_beneficiaries': total_beneficiaries, 'total_payments': total_payments}
    }

if __name__ == "__main__":
    result = get_texas_cardiologist_providers()
    print(result['summary'])
