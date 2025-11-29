---
name: get_anticoagulant_chemical_properties
description: >
  Retrieves comprehensive chemical properties for anticoagulant drugs (warfarin, rivaroxaban, apixaban) from PubChem.
  Returns molecular formula, weight, SMILES, InChI, LogP, TPSA, and hydrogen bond donor/acceptor counts.
category: drug-discovery
mcp_servers:
  - pubchem_mcp
patterns:
  - json_parsing
  - multi_compound_query
data_scope:
  total_results: 3
  geographical: Global
  temporal: Current
created: 2025-11-22
complexity: medium
execution_time: ~2 seconds
token_efficiency: 99%
---
# get_anticoagulant_chemical_properties


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist Compare chemical properties of warfarin, rivaroxaban, and apixaban`
2. `@agent-pharma-search-specialist What are the LogP and TPSA values for major anticoagulant drugs?`
3. `@agent-pharma-search-specialist Show me molecular properties and bioavailability indicators for oral anticoagulants`
4. `@agent-pharma-search-specialist Get SMILES and InChI structures for warfarin, rivaroxaban, and apixaban`
5. `@agent-pharma-search-specialist Analyze drug-likeness properties of direct oral anticoagulants vs warfarin`


Comprehensive chemical properties for three major anticoagulant drugs from PubChem.