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

Comprehensive chemical properties for three major anticoagulant drugs from PubChem.
