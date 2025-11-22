import sys
sys.path.insert(0, ".claude")

def get_us_phase3_obesity_recruiting_trials():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_us_phase3_obesity_recruiting_trials()
    print(f"Test skill: {result['total_count']} items")
