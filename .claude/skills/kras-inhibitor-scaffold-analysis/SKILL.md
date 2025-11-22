---
name: get_kras_inhibitor_scaffold_analysis
description: >
  Analyze structural similarity of KRAS inhibitor scaffolds using Tanimoto
  coefficient to identify chemically similar compounds. Uses sotorasib as
  reference compound for similarity search at 80% threshold. Provides scaffold
  diversity analysis, similarity distribution, and IP/FTO insights.

  Use this skill when analyzing:
  - Freedom-to-operate analysis for KRAS inhibitors
  - Scaffold hopping opportunities
  - IP landscape around existing KRAS drugs
  - Chemical space exploration for new KRAS candidates

  Keywords: KRAS inhibitor, scaffold analysis, Tanimoto similarity, sotorasib,
  chemical similarity, IP landscape, freedom-to-operate, structural diversity
category: chemistry
mcp_servers:
  - pubchem_mcp
patterns:
  - similarity_search
  - tanimoto_coefficient
  - structural_analysis
data_scope:
  total_results: 100
  reference_compound: Sotorasib (CID 146170874)
  similarity_threshold: 80%
  coverage: PubChem compound database
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~3 seconds
token_efficiency: ~99% reduction vs raw PubChem JSON
---

# get_kras_inhibitor_scaffold_analysis

## Purpose

Analyze structural similarity of KRAS inhibitor scaffolds using sotorasib (LUMAKRAS) as reference compound to identify chemically similar structures for IP/FTO analysis and scaffold hopping opportunities.

## Strategic Value

**Business Applications:**
- **Freedom-to-Operate**: Identify structural crowding around approved KRAS inhibitors
- **IP Strategy**: Map chemical space covered by existing patents
- **Scaffold Hopping**: Find alternative scaffolds with similar Tanimoto scores
- **Competitive Intelligence**: Understand competitor chemical space
- **Lead Optimization**: Discover structurally diverse candidates

**Key Metrics:**
- Tanimoto similarity scores (0-100%)
- Scaffold diversity distribution
- Chemical space density
- Novel scaffold opportunities

## Usage

### When to Use This Skill

Trigger this skill for queries about:
- "Analyze KRAS inhibitor scaffolds"
- "Find compounds similar to sotorasib"
- "KRAS inhibitor chemical space analysis"
- "Freedom-to-operate for KRAS G12C inhibitors"
- "Alternative scaffolds for KRAS inhibition"

### Command Line

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/kras-inhibitor-scaffold-analysis/scripts/get_kras_inhibitor_scaffold_analysis.py
```

### Programmatic Import

```python
import sys
sys.path.insert(0, ".claude")
from skills.kras_inhibitor_scaffold_analysis.scripts.get_kras_inhibitor_scaffold_analysis import get_kras_inhibitor_scaffold_analysis

result = get_kras_inhibitor_scaffold_analysis()
print(f"Similar compounds found: {result['total_similar_compounds']}")
```

## Implementation Details

### Data Collection Approach

**Two-Step Process:**
1. Retrieve sotorasib CID from PubChem by name
2. Perform similarity search using Tanimoto coefficient

**Similarity Search:**
- Reference: Sotorasib (LUMAKRAS, CID 146170874)
- Threshold: 80% Tanimoto similarity
- Max Results: 100 compounds
- Method: PubChem 2D structural fingerprint comparison

**Tanimoto Coefficient:**
- Jaccard index for molecular fingerprints
- Range: 0-100% (100% = identical structure)
- Industry standard for scaffold similarity

### Data Structure

```python
{
    'reference_compound': {
        'name': 'sotorasib',
        'cid': 146170874
    },
    'total_similar_compounds': int,
    'similarity_distribution': {
        'high_similarity_90_100': int,
        'medium_similarity_85_90': int,
        'moderate_similarity_80_85': int
    },
    'similar_compounds': [
        {
            'cid': int,
            'similarity_score': float,
            'similarity_tier': str
        }
    ],
    'summary': str
}
```

### Analysis Components

**Similarity Categorization:**
- **High (90-100%)**: Closely related scaffolds, high IP risk
- **Medium (85-90%)**: Similar core, potential FTO concerns
- **Moderate (80-85%)**: Scaffold hopping opportunities

**IP/FTO Insights:**
- High similarity (>90%): Likely covered by existing patents
- Medium similarity (85-90%): Review patent claims carefully
- Moderate similarity (80-85%): Potential design-around space

## Output Format

### Summary Report

```
KRAS INHIBITOR SCAFFOLD ANALYSIS (Sotorasib Reference)

Reference Compound: Sotorasib (CID 146170874)
Similarity Threshold: 80% Tanimoto

SIMILARITY DISTRIBUTION:
  High Similarity (90-100%):     15 compounds
  Medium Similarity (85-90%):    28 compounds
  Moderate Similarity (80-85%):  57 compounds

Total Similar Compounds: 100

IP/FTO STRATEGIC INSIGHTS:
- Chemical space around sotorasib is moderately crowded
- 15 high-similarity compounds suggest established IP coverage
- 57 moderate-similarity compounds offer scaffold hopping opportunities
- Consider exploring <80% similarity space for true novelty
```

## Business Value

- **IP Risk Assessment**: Quantify structural crowding around approved drugs
- **Scaffold Hopping**: Identify alternative chemical space for new candidates
- **Competitive Analysis**: Understand competitor chemical strategies
- **Lead Optimization**: Prioritize structurally diverse series
- **Patent Strategy**: Guide composition-of-matter claim strategy

## Maintenance Notes

**Data Freshness:**
- PubChem compound database updated weekly
- Re-run skill to capture new compounds
- Similarity scores are static (based on 2D fingerprints)

**Known Limitations:**
- 2D similarity only (no 3D conformational analysis)
- Tanimoto threshold affects result count
- Some novel scaffolds may be missed if <80% similar

**Future Enhancements:**
- Add 3D shape similarity (ROCS)
- Include adagrasib and other KRAS G12C inhibitors as references
- Map to patent families for direct IP overlap
- Add bioactivity filters (only active compounds)

## Version History

- **v1.0** (2025-11-22): Initial implementation with sotorasib reference
  - Tanimoto similarity search (80% threshold)
  - Similarity tier categorization
  - IP/FTO strategic insights
