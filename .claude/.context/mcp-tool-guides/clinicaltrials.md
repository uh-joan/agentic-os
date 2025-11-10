# ClinicalTrials.gov (mcp__ct-gov-mcp__ct_gov_studies)

## When to use
- Find trials by condition, intervention, sponsor
- Track trial status (recruiting, completed, terminated)
- Get enrollment numbers, study design details
- Identify competitors' pipeline programs

## Methods
```json
{
  "method": "search",           // Find trials
  "method": "get",              // Get specific trial details
  "method": "suggest"           // Get term suggestions
}
```

## Parameter patterns

### Search by condition
```json
{
  "method": "search",
  "condition": "Diabetes Mellitus Type 2",
  "intervention": "semaglutide",
  "status": "RECRUITING",
  "pageSize": 50
}
```

### Search by phase and sponsor
```json
{
  "method": "search",
  "intervention": "drug_name",
  "phase": "PHASE3",
  "lead": "Company Name",
  "pageSize": 50
}
```

### Get specific trial
```json
{
  "method": "get",
  "nctId": "NCT04000165",
  "format": "json"
}
```

## Key response fields
- `protocolSection.identificationModule.nctId` - Trial identifier
- `protocolSection.identificationModule.briefTitle` - Title
- `protocolSection.statusModule.overallStatus` - Status
- `protocolSection.designModule.phases` - Phase array
- `protocolSection.designModule.enrollmentInfo.count` - Enrollment
- `protocolSection.sponsorCollaboratorsModule.leadSponsor.name` - Sponsor

## Optimization rules
- Use specific status values: `"RECRUITING"`, `"COMPLETED"`, `"ACTIVE_NOT_RECRUITING"`
- Phase format: `"PHASE2"`, `"PHASE3"` (not "Phase 2", "Phase 3")
- Limit fields when counting: `fields=["NCTId", "BriefTitle"]`
- Use `pageSize` (default 10, max 100)
