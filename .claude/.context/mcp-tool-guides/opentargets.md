# Open Targets (mcp__opentargets-mcp-server__opentargets_info)

## When to use
- Target validation (genetic evidence)
- Drug-target-disease associations
- Safety predictions for targets
- Approved drug precedents

## Methods
```json
{
  "method": "search_targets",       // Find genes/targets
  "method": "search_diseases",      // Find diseases
  "method": "get_target_disease_associations", // Get associations
  "method": "get_target_details"    // Target info
}
```

## Parameter patterns

### Search targets
```json
{
  "method": "search_targets",
  "query": "GLP1R",
  "size": 10
}
```

### Get associations
```json
{
  "method": "get_target_disease_associations",
  "targetId": "ENSG00000012048",
  "diseaseId": "EFO_0000305",
  "minScore": 0.5
}
```

## Key response fields
- `id` - Ensembl gene ID
- `approvedSymbol` - Gene symbol
- `associationScore` - Evidence strength
- `approvedName` - Gene name

## Optimization rules
- Use gene symbols for search (GLP1R, DPP4)
- Filter by minScore (0.5+ for strong associations)
- Check `datatypeScores` for evidence types
