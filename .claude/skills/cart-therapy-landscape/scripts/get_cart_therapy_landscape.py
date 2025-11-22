import sys
sys.path.insert(0, ".claude")

def get_cart_therapy_landscape():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_cart_therapy_landscape()
    print(f"Test skill: {result['total_count']} items")
