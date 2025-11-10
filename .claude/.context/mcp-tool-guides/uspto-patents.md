# USPTO Patents (mcp__patents-mcp-server__uspto_patents)

## When to use
- Patent landscape analysis
- Freedom-to-operate (FTO) assessment
- Competitor IP portfolio tracking
- Patent prosecution monitoring

## Methods
```json
{
  "method": "ppubs_search_patents",     // Search granted patents
  "method": "ppubs_search_applications", // Search applications
  "method": "ppubs_get_patent_by_number", // Get specific patent
  "method": "get_app_metadata"          // Application status
}
```

## Parameter patterns

### Search patents
```json
{
  "method": "ppubs_search_patents",
  "query": "GLP-1 AND diabetes",
  "limit": 50
}
```

### Company-specific search
```json
{
  "method": "ppubs_search_patents",
  "query": "assignee:\"Novo Nordisk\" AND GLP-1",
  "limit": 100
}
```

### Get patent details
```json
{
  "method": "ppubs_get_patent_by_number",
  "patent_number": "11234567"
}
```

## Key response fields
- `patentNumber` - Patent number
- `patentTitle` - Title
- `assigneeEntityName` - Owner
- `filingDate` - Application date
- `patentIssueDate` - Grant date

## Optimization rules
- Use Boolean operators: AND, OR, NOT
- Field-specific: `assignee:`, `inventor:`, `date:`
- Limit by date range: `date:[20200101 TO 20241231]`
- Check patent status with `get_app_metadata`
