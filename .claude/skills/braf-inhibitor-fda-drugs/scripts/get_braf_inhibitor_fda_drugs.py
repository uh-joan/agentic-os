import sys
sys.path.insert(0, ".claude")

def get_braf_inhibitor_fda_drugs():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_braf_inhibitor_fda_drugs()
    print(f"Test skill: {result['total_count']} items")
