---
name: get_ultra_rare_metabolic_targets
description: >
  Identifies genetic targets for ultra-rare metabolic diseases with small patient populations (<500).
  Searches metabolic disease categories (lysosomal storage, mitochondrial, peroxisomal disorders),
  filters for OMIM/Orphanet-annotated ultra-rare conditions, and retrieves associated genetic targets
  with tractability assessments. Returns prioritized targets by disease count and association score.
  Useful for orphan drug discovery, rare disease target validation, and portfolio strategy.
category: target-validation
mcp_servers:
  - opentargets_mcp
patterns:
  - cli_arguments
  - multi_query_aggregation
  - json_parsing
  - data_aggregation
  - filtering
  - druggability_assessment
data_scope:
  total_results: 194 targets across 92 diseases
  geographical: Global
  temporal: Current
created: 2025-11-22
last_updated: 2025-11-22
complexity: complex
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
cli_enabled: true
---
# get_ultra_rare_metabolic_targets



## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the genetic targets for ultra rare metabolic targets?`
2. `@agent-pharma-search-specialist Show me therapeutic targets for ultra rare metabolic targets`
3. `@agent-pharma-search-specialist Find validated targets in ultra rare metabolic targets`


## CLI Usage

```bash
# Default example (max population 500)
python get_ultra_rare_metabolic_targets.py

# Custom max population
python get_ultra_rare_metabolic_targets.py 1000

# Very rare (population < 100)
python get_ultra_rare_metabolic_targets.py 100
```

## Parameters

- **max_population** (int, optional): Maximum affected population threshold (default: 500)

## Returns

Ultra-rare metabolic targets with genetic evidence, druggability scores, and patient population.
## Purpose
Identifies and prioritizes genetic targets for ultra-rare metabolic diseases with very small patient populations (default <500 patients). Combines disease search, genetic association data, and tractability assessments to guide orphan drug discovery.

## Usage
When user needs:
- Genetic targets for ultra-rare metabolic diseases
- Orphan drug discovery opportunities
- Multi-disease target identification
- Tractability assessment for rare disease genes
- Portfolio strategy for rare disease programs

## Implementation Details
Multi-step approach:
1. **Disease Discovery**: Searches 5 metabolic disease categories (lysosomal storage, mitochondrial, peroxisomal, inborn errors, general metabolic disorders)
2. **Ultra-Rare Filtering**: Identifies diseases with OMIM/Orphanet annotations and ultra-rare keywords (deficiency, syndrome, dystrophy, etc.)
3. **Target Retrieval**: Gets genetic associations for each disease with confidence scores
4. **Tractability Assessment**: Evaluates small molecule and antibody druggability
5. **Prioritization**: Ranks by disease count (multi-indication potential) and association score

## Key Features
- Identifies targets associated with multiple ultra-rare diseases (single therapy, multiple indications)
- Filters for high-confidence associations (score > 0.5)
- Includes tractability data for both small molecules and antibodies
- Links to OMIM/Orphanet disease databases for epidemiology data
- Handles top 20 diseases for efficiency while maintaining comprehensive coverage

## Example Output
```
Total diseases analyzed: 92
Total unique genetic targets: 194
High-priority targets (3+ diseases): 24
Clinically tractable targets: 31

Top target: MTCO2 (mitochondrially encoded cytochrome c oxidase II)
  - Associated diseases: 7
  - Max association score: 1.000
  - Diseases include: Kearns-Sayre syndrome, mitochondrial complex IV deficiency
```

## Data Fields
- **Target identification**: Gene symbol, Ensembl ID, approved name
- **Disease associations**: Disease count, individual disease names/IDs, association scores
- **Tractability**: Small molecule and antibody druggability categories
- **Rare disease markers**: OMIM IDs, Orphanet IDs

## Business Applications
- **Orphan drug discovery**: Identify high-value targets for rare disease programs
- **Multi-indication strategy**: Find targets treating multiple ultra-rare conditions
- **Portfolio optimization**: Prioritize programs with genetic validation and tractability
- **Partnership opportunities**: Identify targets for academic/industry collaboration