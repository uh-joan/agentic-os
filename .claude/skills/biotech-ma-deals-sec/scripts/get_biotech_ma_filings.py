import sys
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import search_filings

def get_biotech_ma_filings():
    all_filings = []
    for keyword in ["merger acquisition", "definitive agreement"]:
        result = search_filings(query=f"{keyword} biotech", form_type="8-K", start=0, count=100)
        if result and 'filings' in result:
            all_filings.extend(result['filings'])
    return {'total_count': len(all_filings), 'filings': all_filings}

if __name__ == "__main__":
    result = get_biotech_ma_filings()
    print(f"Biotech M&A filings: {result['total_count']}")
