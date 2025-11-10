# PubMed (mcp__pubmed-mcp__pubmed_articles)

## When to use
- Literature searches for drugs, conditions, mechanisms
- Find clinical study publications
- Get article metadata (authors, abstract, journal)
- Download full-text PDFs (when available)

## Methods
```json
{
  "method": "search_keywords",  // Search with keywords
  "method": "search_advanced",  // Search with filters
  "method": "get_article_metadata", // Get article details
  "method": "get_article_pdf"   // Download PDF
}
```

## Parameter patterns

### Keyword search
```json
{
  "method": "search_keywords",
  "keywords": "semaglutide diabetes",
  "num_results": 20
}
```

### Advanced search with filters
```json
{
  "method": "search_advanced",
  "term": "GLP-1 agonist",
  "journal": "N Engl J Med",
  "start_date": "2020/01/01",
  "end_date": "2024/12/31",
  "num_results": 50
}
```

### Get specific article
```json
{
  "method": "get_article_metadata",
  "pmid": "12345678"
}
```

## Key response fields
- `pmid` - PubMed ID
- `title` - Article title
- `abstract` - Full abstract text
- `authors` - Author list
- `journal` - Journal name
- `pub_date` - Publication date

## Optimization rules
- Use MeSH terms for precision: `"Diabetes Mellitus, Type 2"[MeSH]`
- Date filters: `("2020/01/01"[PDAT] : "2024/12/31"[PDAT])`
- Study type filters: `AND (randomized controlled trial[pt])`
- Human studies only: `AND humans[MeSH]`

## Known Limitations
- **MCP result count**: May return fewer results than `num_results` requested
  - Example: Requested 30, received 2 (observed in testing)
  - **Workaround**: Request conservative numbers (10-20) and expect partial returns
  - Not a query issue - appears to be MCP tool limitation
