import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import get_observations

def get_california_population_time_series():
    result = get_observations(variable="Count_Person", entity="geoId/06")
    observations = result.get('observations', [])
    if not observations:
        return {'error': 'No data found'}
    sorted_obs = sorted(observations, key=lambda x: x['date'])
    return {'summary': {'total_years': len(sorted_obs)}, 'observations': sorted_obs}

if __name__ == "__main__":
    result = get_california_population_time_series()
    print(f"California population: {len(result['observations'])} years of data")
