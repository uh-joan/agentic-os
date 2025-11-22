---
name: get_texas_cardiologist_providers
description: >
  Retrieves Medicare provider data for cardiologists practicing in Texas from CMS database.
  Returns comprehensive provider directory with NPIs, practice locations, service volumes,
  beneficiary counts, and Medicare payment data. Includes geographic distribution analysis.
category: healthcare
mcp_servers:
  - healthcare_mcp
patterns:
  - json_parsing
  - aggregation
  - geographic_distribution
data_scope:
  total_results: ~850
  geographical: Texas (US)
  temporal: Current
created: 2025-11-22
complexity: simple
execution_time: ~2 seconds
---

# get_texas_cardiologist_providers

Retrieves Medicare provider data for cardiologists practicing in Texas.
