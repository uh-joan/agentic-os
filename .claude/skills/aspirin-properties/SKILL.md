---
name: get_aspirin_pubchem_data
description: >
  Retrieves comprehensive molecular properties and chemical data for aspirin from PubChem database.
  Returns molecular formula, weight, physicochemical properties (LogP, TPSA, complexity),
  hydrogen bonding characteristics, and chemical identifiers (SMILES, InChI).
category: drug-discovery
mcp_servers:
  - pubchem_mcp
patterns:
  - json_parsing
  - property_extraction
data_scope:
  total_results: 1
  geographical: Global
  temporal: Current
created: 2025-11-22
complexity: simple
execution_time: ~2 seconds
---
# get_aspirin_pubchem_data


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Get aspirin properties data`
2. `@agent-pharma-search-specialist Show me aspirin properties information`
3. `@agent-pharma-search-specialist Find aspirin properties details`


Retrieves comprehensive molecular and physicochemical properties for aspirin from PubChem.