import sys
sys.path.insert(0, ".claude")

def get_kras_comprehensive_analysis():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_kras_comprehensive_analysis()
    print(f"Test skill: {result['total_count']} items")
