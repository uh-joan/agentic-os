import sys
sys.path.insert(0, ".claude")

def get_company_segment_geographic_financials():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_company_segment_geographic_financials()
    print(f"Test skill: {result['total_count']} items")
