---
name: get_semaglutide_adverse_events
description: >
  Analyzes FDA FAERS adverse event reports for semaglutide (all formulations: Ozempic, Wegovy, Rybelsus).
  Provides comprehensive post-market safety surveillance including most reported adverse events by frequency,
  patient demographics, severity classifications, and specific tracking of key safety concerns
  (muscle mass loss, gallbladder issues, pancreatitis).
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - aggregation
  - demographic_analysis
data_scope:
  total_results: 1000
  geographical: US
  temporal: All time
  source: FDA FAERS database
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
---

# get_semaglutide_adverse_events

Provides comprehensive adverse event analysis for semaglutide from FDA's Adverse Event Reporting System (FAERS), enabling post-market safety surveillance, risk management planning, and label update strategy.

## Key Safety Concerns Tracked

- Muscle mass loss
- Gallbladder issues
- Pancreatitis
- Gastrointestinal events (nausea, vomiting, diarrhea)
- Patient demographics (age, gender)
- Serious outcomes classification
