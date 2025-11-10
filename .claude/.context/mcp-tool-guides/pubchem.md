# PubChem (mcp__pubchem-mcp-server__pubchem)

## When to use
- Compound property lookups (MW, logP)
- Structure searches (SMILES, InChI)
- Drug-likeness predictions
- Safety alerts (structural alerts)

## Methods
```json
{
  "method": "search_compounds",     // Search by name/CAS
  "method": "get_compound_info",    // Get details by CID
  "method": "search_by_smiles",     // Structure search
  "method": "get_compound_properties" // Get properties
}
```

## Parameter patterns

### Search compound
```json
{
  "method": "search_compounds",
  "query": "semaglutide",
  "max_records": 10
}
```

### Get compound properties
```json
{
  "method": "get_compound_properties",
  "cid": "56843331"
}
```

## Key response fields
- `CID` - PubChem ID
- `MolecularFormula` - Formula
- `MolecularWeight` - MW
- `XLogP` - Lipophilicity
- `TPSA` - Polar surface area

## Optimization rules
- Search by name first to get CID
- Then use CID for property lookups
- Use SMILES for exact structure matches
