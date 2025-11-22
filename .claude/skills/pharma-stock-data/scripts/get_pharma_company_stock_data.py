import sys
sys.path.insert(0, ".claude")
from mcp.servers.financials_mcp import get_stock_quote

def get_pharma_company_stock_data(companies=None):
    if companies is None:
        companies = ['PFE', 'MRK', 'JNJ']
    results = []
    for ticker in companies:
        quote = get_stock_quote(ticker)
        results.append({'ticker': ticker, 'data': quote})
    return {'total_count': len(results), 'companies': results}

if __name__ == "__main__":
    result = get_pharma_company_stock_data()
    print(f"Pharma stock data: {result['total_count']} companies")
