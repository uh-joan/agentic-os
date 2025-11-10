# SEC EDGAR (mcp__sec-mcp-server__sec-edgar)

## When to use
- Company financials (R&D spend, revenue)
- Pipeline mentions in 10-K/10-Q filings
- M&A activity (8-K filings)
- Financial metrics for biotech companies

## Methods
```json
{
  "method": "search_companies",     // Find companies
  "method": "get_company_cik",      // Ticker → CIK
  "method": "get_company_submissions", // Filing history
  "method": "get_company_facts"     // XBRL financial data
}
```

## Parameter patterns

### Get company CIK
```json
{
  "method": "get_company_cik",
  "ticker": "PFE"
}
```

### Get filings
```json
{
  "method": "get_company_submissions",
  "cik_or_ticker": "PFE"
}
```

### Filter filings
```json
{
  "method": "filter_filings",
  "filings": [...],
  "form_type": "10-K",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31"
}
```

## Key response fields
- `cik` - Central Index Key
- `entityName` - Company name
- `filings.recent.accessionNumber` - Filing ID
- `filings.recent.primaryDocument` - Document URL
- `filings.recent.form` - Filing type

## Optimization rules
- Convert ticker to CIK first (required for most queries)
- Use `filter_filings` to narrow by form type and date
- 10-K: Annual reports (Item 1, Item 7 for pipeline)
- 8-K: Current events (M&A, material changes)
