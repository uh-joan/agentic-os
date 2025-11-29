---
name: get_glp1_agonist_properties
description: >
  Compare molecular properties of approved GLP-1 receptor agonists including semaglutide,
  liraglutide, dulaglutide, tirzepatide, and exenatide. Extracts critical drug-like properties
  from PubChem: molecular weight, lipophilicity (XLogP), topological polar surface area (TPSA),
  complexity, and hydrogen bonding characteristics. Provides strategic insights for oral formulation
  strategy and drug design optimization. Use this skill when analyzing formulation challenges,
  understanding oral bioavailability barriers, validating absorption enhancer strategies (SNAC),
  or supporting rationale for oral-first small molecule development. Keywords: GLP-1, molecular
  properties, oral formulation, drug design, peptide therapeutics, bioavailability, TPSA,
  lipophilicity, semaglutide, liraglutide, PK optimization.
category: drug-discovery
mcp_servers:
  - pubchem_mcp
patterns:
  - json_parsing
  - comparative_analysis
  - property_extraction
data_scope:
  total_results: 5
  geographical: Global
  temporal: Current approved drugs
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~5 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_glp1_agonist_properties


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Get glp1 agonist properties data`
2. `@agent-pharma-search-specialist Show me glp1 agonist properties information`
3. `@agent-pharma-search-specialist Find glp1 agonist properties details`


## Purpose

Compares molecular properties of approved GLP-1 receptor agonists to identify formulation challenges and support drug design strategy. Specifically addresses the oral bioavailability challenge that necessitates absorption enhancers like SNAC (for oral semaglutide) and validates the rationale for oral-first small molecule approaches.

## Business Value

- **Formulation Strategy**: Quantifies oral formulation challenges (all compounds >3000 Da, high TPSA)
- **Competitive Intelligence**: Validates need for absorption enhancers vs. oral-first design
- **Drug Design Optimization**: Informs PK/PD optimization for weekly dosing formulations
- **Portfolio Strategy**: Supports investment rationale for small molecule oral GLP-1 programs

## Compounds Analyzed

1. **Semaglutide** - Weekly injectable + oral (with SNAC)
2. **Liraglutide** - Daily injectable
3. **Dulaglutide** - Weekly injectable
4. **Tirzepatide** - Weekly injectable (GLP-1/GIP dual agonist)
5. **Exenatide** - Twice daily/weekly injectable

## Properties Extracted

- **Molecular Weight**: Critical for oral bioavailability (Rule of 5: <500 Da ideal)
- **XLogP**: Lipophilicity indicator for membrane permeability
- **TPSA**: Topological polar surface area (<140 Ų ideal for oral drugs)
- **Complexity**: Structural complexity score
- **H-Bond Donors/Acceptors**: Influences passive diffusion
- **Rotatable Bonds**: Conformational flexibility
- **Heavy Atoms**: Non-hydrogen atom count

## Key Insights Generated

1. **Molecular Weight Challenge**: All GLP-1 agonists are large peptides (>3000 Da), far exceeding Lipinski's Rule of 5 threshold
2. **TPSA Barrier**: Extremely high polar surface areas (>1000 Ų) confirm poor passive diffusion
3. **Lipophilicity Gap**: Peptide-based agonists lack sufficient lipophilicity for membrane permeation
4. **Strategic Validation**:
   - Oral semaglutide's SNAC co-formulation necessity is molecularly justified
   - Small molecule oral-first programs (e.g., orforglipron) address fundamental property limitations

## Usage Example

```python
from .claude.skills.glp1_agonist_properties.scripts.get_glp1_agonist_properties import get_glp1_agonist_properties

result = get_glp1_agonist_properties()
print(f"Analyzed {result['total_compounds']} GLP-1 agonists")
print(result['summary'])
```

## Implementation Details

### Data Source
- **PubChem API**: Authoritative compound property database
- **Query Method**: Compound name search with property extraction

### Error Handling
- Graceful handling of missing properties (displays 'N/A')
- Try-catch blocks for individual compound failures
- Successful query tracking

### Output Format
```python
{
    'total_compounds': 5,
    'successful_queries': 5,
    'properties_data': {
        'Semaglutide': {
            'molecular_weight': 4113.6,
            'xlogp': 'N/A',
            'tpsa': 1569,
            'complexity': 7280,
            ...
        },
        ...
    },
    'summary': '...'
}
```

## Strategic Context

### Oral Formulation Landscape
- **Current Oral GLP-1**: Only semaglutide (Rybelsus®) approved, requires SNAC absorption enhancer
- **Emerging Approaches**:
  - Small molecule oral-first designs (orforglipron, danuglipron)
  - Novel delivery technologies (permeation enhancers, nanoparticles)

### PK/PD Optimization
- **Weekly Dosing**: Large molecular weight enables slow clearance
- **Half-Life Determinants**: Albumin binding (fatty acid modifications), GLP-1 receptor affinity
- **Formulation Trade-offs**: Injectable convenience vs. oral patient preference

## Related Skills

- `get_glp1_trials` - Clinical development landscape
- `get_glp1_fda_drugs` - Regulatory approval status
- `get_glp1_patents` - Intellectual property analysis

## References

- Lipinski's Rule of 5: Oral drug-likeness criteria
- SNAC Technology: Oral peptide absorption enhancement
- PubChem Database: Molecular property standardization