import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re

def get_us_china_oncology_trial_comparison():
    """Compare Phase 3 oncology trials recruiting in US vs. China.

    Returns:
        dict: Contains comparison data and summary
    """
    print("Collecting US Phase 3 oncology trials...")

    # Query for US trials
    us_trials = []
    us_page_token = None

    while True:
        us_result = search(
            query="cancer OR oncology OR tumor OR carcinoma",
            filter_overallStatus="RECRUITING",
            filter_phase="PHASE3",
            filter_geo="distance(40,-100,2000mi)",  # Covers continental US
            pageSize=1000,
            pageToken=us_page_token
        )

        # Parse trials from markdown
        trial_pattern = r'###\s+\d+\.\s+NCT\d{8}'
        us_trials_batch = re.findall(trial_pattern, us_result)
        us_trials.extend(us_trials_batch)

        # Check for next page
        next_page_match = re.search(r'pageToken:\s*"([^"]+)"', us_result)
        if next_page_match and len(us_trials_batch) > 0:
            us_page_token = next_page_match.group(1)
            print(f"  US trials so far: {len(us_trials)}, fetching next page...")
        else:
            break

    print(f"\nCollecting China Phase 3 oncology trials...")

    # Query for China trials
    china_trials = []
    china_page_token = None

    while True:
        china_result = search(
            query="cancer OR oncology OR tumor OR carcinoma",
            filter_overallStatus="RECRUITING",
            filter_phase="PHASE3",
            filter_geo="distance(39.9,116.4,2000km)",  # Beijing coordinates, covers China
            pageSize=1000,
            pageToken=china_page_token
        )

        # Parse trials from markdown
        china_trials_batch = re.findall(trial_pattern, china_result)
        china_trials.extend(china_trials_batch)

        # Check for next page
        next_page_match = re.search(r'pageToken:\s*"([^"]+)"', china_result)
        if next_page_match and len(china_trials_batch) > 0:
            china_page_token = next_page_match.group(1)
            print(f"  China trials so far: {len(china_trials)}, fetching next page...")
        else:
            break

    # Calculate comparison metrics
    us_count = len(us_trials)
    china_count = len(china_trials)
    total = us_count + china_count

    us_percentage = (us_count / total * 100) if total > 0 else 0
    china_percentage = (china_count / total * 100) if total > 0 else 0

    ratio = us_count / china_count if china_count > 0 else float('inf')

    summary = f"""
Phase 3 Oncology Trials - Geographic Comparison
================================================

United States:
  - Total trials recruiting: {us_count:,}
  - Percentage of combined total: {us_percentage:.1f}%

China:
  - Total trials recruiting: {china_count:,}
  - Percentage of combined total: {china_percentage:.1f}%

Comparison:
  - Combined total: {total:,} trials
  - US to China ratio: {ratio:.2f}:1
  - Difference: {abs(us_count - china_count):,} trials ({('US leads' if us_count > china_count else 'China leads')})

Strategic Insights:
  - {'US has significantly more trials, indicating stronger oncology clinical infrastructure' if ratio > 1.5 else 'Relatively balanced distribution, both regions are major oncology hubs' if 0.67 <= ratio <= 1.5 else 'China has more trials, reflecting rapid expansion of clinical capacity'}
  - Geographic expansion opportunity: {'Consider China for clinical development expansion' if ratio > 2 else 'Both regions offer robust clinical trial ecosystems' if 0.5 <= ratio <= 2 else 'Consider US for additional trial sites'}
"""

    return {
        'us_count': us_count,
        'china_count': china_count,
        'total': total,
        'us_percentage': us_percentage,
        'china_percentage': china_percentage,
        'ratio': ratio,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_us_china_oncology_trial_comparison()
    print(result['summary'])
