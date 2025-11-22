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

Retrieves comprehensive molecular and physicochemical properties for aspirin from PubChem.
