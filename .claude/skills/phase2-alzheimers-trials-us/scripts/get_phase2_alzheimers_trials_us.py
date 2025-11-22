import sys
sys.path.insert(0, ".claude")

def get_phase2_alzheimers_trials_us():
    return {'total_count': 10, 'data': [], 'summary': 'Test skill'}

if __name__ == "__main__":
    result = get_phase2_alzheimers_trials_us()
    print(f"Test skill: {result['total_count']} items")
