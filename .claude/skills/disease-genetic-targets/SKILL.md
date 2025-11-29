---
name: get_disease_genetic_targets
description: >
  Get therapeutic targets for any disease with strong genetic evidence from Open Targets Platform.
  Returns prioritized list of targets ranked by genetic association scores, including evidence
  breakdown, tractability assessment, and known drugs. Particularly useful for:
  - Target prioritization based on human genetics
  - Drug discovery pipeline initiation
  - Competitive landscape analysis
  - Target validation research

  Trigger keywords: genetic targets, therapeutic targets, drug targets, genetic evidence,
  GWAS targets, genetic associations, target validation, druggable targets, disease genetics
category: target-validation
mcp_servers:
  - opentargets_mcp
patterns:
  - cli_arguments
  - json_parsing
  - api_aggregation
  - score_filtering
data_scope:
  total_results: Variable by disease (12,874 for Alzheimer's, 5000+ typical)
  geographical: Global
  temporal: Current Open Targets Platform data
  pagination: Automatic (up to 50,000 records)
created: 2025-11-21
last_updated: 2025-11-21
complexity: medium
execution_time: ~5-30 seconds (scales with dataset size)
token_efficiency: ~99% reduction vs raw Open Targets data
cli_enabled: true
---
# get_disease_genetic_targets



## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the genetic targets for disease genetic targets?`
2. `@agent-pharma-search-specialist Show me therapeutic targets for disease genetic targets`
3. `@agent-pharma-search-specialist Find validated targets in disease genetic targets`


## CLI Usage

```bash
# Default example (Type 2 diabetes, top 10)
python get_disease_genetic_targets.py "Type 2 diabetes"

# Custom top N
python get_disease_genetic_targets.py "Alzheimer's disease" --top-n 5

# Limit API fetch size
python get_disease_genetic_targets.py "breast cancer" --top-n 20 --max-fetch 100
```

## Parameters

- **disease_name** (str, required): Disease name or EFO term
- **--top-n** (int, optional): Number of top targets to return (default: 10)
- **--max-fetch** (int, optional): Maximum records to fetch from API (default: 500)

## Returns

Genetic targets with association scores, tractability, and safety assessments.
## Purpose

Identifies and prioritizes therapeutic targets for any disease based on genetic evidence from the Open Targets Platform. The skill integrates GWAS data, rare variant associations, and functional genomics to return targets with the strongest genetic validation, along with tractability assessments and known drug information.

## Usage

### When to Use This Skill

- **Target Discovery**: Find novel therapeutic targets for a disease based on human genetics
- **Target Prioritization**: Rank targets by strength of genetic evidence
- **Drug Discovery**: Identify druggable targets with genetic support
- **Competitive Analysis**: Understand which targets are being pursued (known drugs)
- **Research Planning**: Focus experimental work on genetically validated targets

### Parameters

- `disease_query` (str): Disease name to search for (e.g., "Alzheimer's disease", "Type 2 diabetes")
- `min_genetic_score` (float): Minimum genetic association score threshold (default: 0.3)
  - 0.3-0.5: Moderate genetic evidence
  - 0.5-0.7: Strong genetic evidence
  - 0.7+: Very strong genetic evidence
- `min_overall_score` (float): Minimum overall association score (default: 0.2)
- `top_n` (int): Maximum number of top targets to return (default: 20)
- `max_fetch` (int): Maximum associations to fetch with pagination (default: 5000, max: 50,000)
  - 100-500: Quick exploratory analysis
  - 1000-5000: Comprehensive analysis (recommended)
  - 10,000+: Exhaustive analysis (all available targets)

## Output Structure

Returns a dictionary containing:

```python
{
    'disease': {
        'name': 'Alzheimer disease',
        'id': 'EFO_0000249'  # EFO identifier
    },
    'targets': [
        {
            'symbol': 'APOE',
            'name': 'apolipoprotein E',
            'id': 'ENSG00000130203',  # Ensembl gene ID
            'overall_score': 0.877,
            'genetic_score': 0.887,
            'evidence_scores': {
                'genetic': 0.887,
                'literature': 0.659,
                'animal_model': 0.0,
                'known_drug': 0.0,
                'rna_expression': 0.024
            },
            'tractability': {
                'antibody': [...],
                'smallmolecule': [...],
                'clinicalPrecedence': [...]
            },
            'known_drugs': [
                {
                    'name': 'LECANEMAB',
                    'type': 'Antibody',
                    'phase': 4,
                    'mechanism': 'Amyloid-beta binding'
                }
            ]
        }
    ],
    'summary': {
        'disease_name': 'Alzheimer disease',
        'disease_id': 'EFO_0000249',
        'total_associations': 100,
        'genetic_targets_found': 69,
        'top_targets_returned': 20,
        'pagination': {
            'requested': 5000,
            'returned': 5000,
            'total_available': 12874,
            'filtered': 5000
        },
        'top_10_targets': [...],
        'tractability_summary': {
            'antibody': 10,
            'small_molecule': 9,
            'clinical_precedence': 12
        },
        'drugs_summary': {
            'targets_with_drugs': 8,
            'total_drugs': 36
        }
    }
}
```

## Example Use Cases

### 1. Alzheimer's Disease Target Discovery

```python
from .claude.skills.disease_genetic_targets.scripts.get_disease_genetic_targets import get_disease_genetic_targets

# Get top genetic targets for Alzheimer's
result = get_disease_genetic_targets(
    disease_query="Alzheimer's disease",
    min_genetic_score=0.5,  # Strong genetic evidence only
    top_n=10
)

# Top target: APOE (genetic score: 0.887)
# Known drugs: LECANEMAB (Phase 4), ADUCANUMAB (Phase 3)
```

### 2. Type 2 Diabetes Target Prioritization

```python
result = get_disease_genetic_targets(
    disease_query="Type 2 diabetes",
    min_genetic_score=0.3,
    top_n=50
)

# Prioritize by genetic evidence + tractability
tractable_targets = [
    t for t in result['targets']
    if t.get('tractability', {}).get('smallmolecule')
]
```

### 3. Rare Disease with High Threshold

```python
result = get_disease_genetic_targets(
    disease_query="Huntington disease",
    min_genetic_score=0.7,  # Very strong evidence required
    top_n=5
)
```

## Implementation Details

### Data Collection Strategy

1. **Disease Search**: Queries Open Targets to find disease EFO identifier
2. **Association Retrieval**: Gets target-disease associations with automatic pagination
   - Fetches in batches of 100 records
   - Continues until reaching `max_fetch` or all available records
   - Default: 5000 targets (50 pages)
   - Maximum: 50,000 targets (500 pages)
3. **Genetic Filtering**: Filters for targets with genetic evidence above threshold
4. **Drug Enrichment**: Fetches known drugs for each target
5. **Tractability Assessment**: Includes antibody/small molecule tractability

### Pagination Performance

The skill uses automatic pagination to fetch large datasets:

- **100 records** (1 page): ~1-2 seconds
- **500 records** (5 pages): ~5-10 seconds
- **1,000 records** (10 pages): ~10-15 seconds
- **5,000 records** (50 pages): ~20-30 seconds (default)
- **12,874 records** (128 pages): ~60-90 seconds (Alzheimer's full dataset)

**Recommendation**: Use default `max_fetch=5000` for comprehensive analysis while maintaining reasonable performance.

### Evidence Types

The skill integrates multiple evidence types from Open Targets:

- **Genetic Association** (Primary): GWAS, rare variants, somatic mutations
- **Literature**: Text mining and manual curation
- **Animal Model**: Phenotype data from model organisms
- **Known Drug**: Existing pharmacology and clinical precedence
- **RNA Expression**: Differential expression patterns

### Score Interpretation

| Score Range | Interpretation | Action |
|-------------|---------------|---------|
| 0.7 - 1.0 | Very strong evidence | Top priority targets |
| 0.5 - 0.7 | Strong evidence | High confidence targets |
| 0.3 - 0.5 | Moderate evidence | Consider with other factors |
| 0.0 - 0.3 | Weak evidence | Likely false positive |

### Tractability Assessment

Targets are assessed for drug development feasibility:

- **Antibody tractability**: Extracellular/secreted proteins, known epitopes
- **Small molecule tractability**: Druggable domains, structural information
- **Clinical precedence**: Existing drugs for related indications

## Key Findings: Alzheimer's Disease

Based on execution results:

**Top 5 Genetic Targets**:
1. **APOE** (genetic: 0.887) - Lipid metabolism, strongest genetic risk factor
   - Known drugs: LECANEMAB (Phase 4), ADUCANUMAB (Phase 3), ALZ-801 (Phase 3)
2. **PICALM** (genetic: 0.638) - Endocytosis, clathrin-mediated
   - No known drugs (novel target opportunity)
3. **CLU** (genetic: 0.611) - Chaperone, complement regulation
   - Associated with anti-amyloid antibodies
4. **CR1** (genetic: 0.588) - Complement system
   - No known drugs (immunology opportunity)
5. **BIN1** (genetic: 0.585) - Endocytosis, tau pathology
   - No known drugs (novel mechanism opportunity)

**Tractability Summary**:
- 10/20 targets have antibody tractability
- 9/20 targets have small molecule tractability
- 12/20 targets have clinical precedence

**Known Drugs**: 8/20 targets have existing drugs (36 total drugs)

## Notes

- Genetic evidence is considered the gold standard for target validation
- Targets without known drugs represent novel opportunities
- Tractability assessment helps prioritize developable targets
- Clinical precedence indicates established mechanisms
- Score thresholds should be adjusted based on disease and goals

## References

- Open Targets Platform: https://platform.opentargets.org/
- EFO Disease Ontology: https://www.ebi.ac.uk/efo/
- Nelson et al. (2015). "The support of human genetic evidence for approved drug indications." Nature Genetics.