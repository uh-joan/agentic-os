# 2026+ Biotech Playbook: M&A Intelligence Skills & Queries

**Source**: Bowtide Biotech podcast transcript - "The Brutal Restructuring of the Biotech Market"

**Core Thesis**: Capital is concentrating at biotech companies that solve Big Pharma's 2030-2035 revenue replacement crisis. Only apex predator assets (late-stage, giant TAM, scalable) command multi-billion dollar acquisitions. The squeezed middle (70% of biotechs) faces capital extinction.

**Intelligence Requirements**: 22 new skills + 50+ strategic queries to operationalize the playbook

---

## Category 1: Patent Cliff & Revenue Gap Analysis

### Skill 1: `pharma-patent-cliff-forecast`
**Priority**: High ⭐⭐⭐

**User Query Examples**:
- "Which blockbuster drugs expire 2028-2035 and what's the revenue impact?"
- "Show me the patent cliff timeline by therapeutic area"
- "Quantify the oncology revenue cliff for top 10 pharma"

**MCP Servers**:
- `fda_mcp`: Drug approvals, exclusivity dates
- `sec_mcp`: Product revenue from 10-K filings
- `financials_mcp`: Analyst forecasts, guidance

**Output Structure**:
```python
{
    'company': 'Pfizer',
    'revenue_cliff_by_year': {
        '2028': {'products': [...], 'revenue_at_risk': 5.2B},
        '2029': {'products': [...], 'revenue_at_risk': 8.7B},
        '2030': {'products': [...], 'revenue_at_risk': 12.1B}
    },
    'by_therapeutic_area': {
        'oncology': {'revenue_at_risk': 15.4B, 'peak_year': 2030},
        'immunology': {'revenue_at_risk': 8.9B, 'peak_year': 2031}
    },
    'total_cliff_2028_2035': 45.3B
}
```

**Strategic Value**: Identifies specific pharma acquisition needs by franchise and timing

**Complexity**: Medium (SEC parsing + FDA exclusivity mapping)

---

### Skill 2: `pharma-2030-revenue-replacement-needs`
**Priority**: CRITICAL ⭐⭐⭐⭐⭐ (Foundation skill)

**User Query Examples**:
- "Quantify Pfizer's 2030-2035 revenue gap by franchise"
- "What are AbbVie's post-Humira replacement needs?"
- "Map Big Pharma's revenue deficits requiring M&A"

**MCP Servers**:
- `sec_mcp`: 10-K filings (segment revenue, product revenue)
- `financials_mcp`: Analyst guidance, revenue projections
- `fda_mcp`: Patent expiries

**Output Structure**:
```python
{
    'company': 'Pfizer',
    'analysis_period': '2030-2035',
    'current_revenue': 58.5B,
    'projected_baseline_2030': 42.3B,
    'revenue_gap': 16.2B,
    'franchise_deficits': {
        'oncology': {
            'expiring_products': ['Ibrance', 'Xtandi'],
            'revenue_loss': 8.5B,
            'replacement_need': 'Late-stage breast cancer / prostate cancer'
        },
        'immunology': {
            'expiring_products': [...],
            'revenue_loss': 4.7B,
            'replacement_need': 'RA / atopic dermatitis scalable franchise'
        }
    },
    'ma_budget_estimate': '25-30B (2027-2030)',
    'target_asset_profile': 'Phase 2b+, >$5B TAM, registrational by 2028'
}
```

**Strategic Value**: THE foundational skill - validates "build backwards from exit" principle

**Complexity**: High (multi-source data integration, financial modeling)

---

### Skill 3: `blockbuster-expiration-tracker`
**Priority**: Medium ⭐⭐

**User Query Examples**:
- "Get all drugs >$1B annual revenue expiring before 2033"
- "Track Keytruda exclusivity and revenue trajectory"
- "Which immunology blockbusters lose patent protection 2029-2032?"

**MCP Servers**:
- `fda_mcp`: Exclusivity dates, approval dates
- `sec_mcp`: Product revenue disclosures

**Output Structure**:
```python
{
    'blockbusters_at_risk': [
        {
            'drug': 'Keytruda',
            'company': 'Merck',
            'current_revenue': 25.0B,
            'patent_expiry': '2028-09',
            'therapeutic_area': 'oncology',
            'replacement_urgency': 'critical'
        }
    ],
    'revenue_cliff_heatmap': {
        '2028': 15.2B,
        '2029': 28.7B,
        '2030': 45.3B,
        '2031': 38.9B
    }
}
```

**Strategic Value**: Patent cliff heat map by year and company

**Complexity**: Medium (FDA data + SEC revenue mapping)

---

## Category 2: M&A Deal Intelligence

### Skill 4: `biotech-ma-deals-by-tam`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Analyze M&A deals by target addressable market size"
- "What TAM threshold predicts $1B+ vs $5B+ acquisitions?"
- "Compare acquisition multiples for large TAM vs niche TAM assets"

**MCP Servers**:
- `sec_mcp`: M&A filings (8-K, DEFM14A, deal value)
- `ct_gov_mcp`: Indication details, patient population
- `who_mcp`: Disease burden, prevalence
- `datacommons_mcp`: Population statistics

**Output Structure**:
```python
{
    'deal_stratification': {
        'apex_deals_5B_plus': {
            'count': 8,
            'avg_tam': 15.3B,
            'avg_phase': '2b/3',
            'examples': [
                {'target': 'Seagen', 'price': 43B, 'tam': 25B, 'indication': 'Oncology ADC'}
            ]
        },
        'mid_tier_1B_5B': {
            'count': 24,
            'avg_tam': 4.2B,
            'avg_phase': '2',
            'examples': [...]
        },
        'squeezed_middle_under_1B': {
            'count': 67,
            'avg_tam': 800M,
            'avg_phase': '1/2',
            'examples': [...]
        }
    },
    'tam_threshold_analysis': {
        '5B_plus_acquisition': {'min_tam': 8.5B, 'avg_tam': 15.3B},
        '1B_plus_acquisition': {'min_tam': 2.1B, 'avg_tam': 4.7B}
    }
}
```

**Strategic Value**: Validates thesis "Only giant TAM assets get acquired at premium valuations"

**Complexity**: High (multi-source integration, TAM estimation modeling)

---

### Skill 5: `biotech-ma-valuation-drivers`
**Priority**: CRITICAL ⭐⭐⭐⭐⭐

**User Query Examples**:
- "What predicts acquisition price: stage, TAM, scalability, or franchise fit?"
- "Quantify the platform premium in M&A valuations"
- "Regression analysis: which factors drive >10x revenue multiples?"

**MCP Servers**:
- `sec_mcp`: Deal terms, valuations, earnouts
- `ct_gov_mcp`: Trial phase, indication
- `fda_mcp`: Competitive landscape

**Output Structure**:
```python
{
    'regression_model': {
        'dependent_variable': 'acquisition_price_per_revenue_dollar',
        'r_squared': 0.87,
        'coefficients': {
            'phase_2b_3': 8.2,  # Strongest predictor
            'tam_over_10B': 6.7,
            'scalability_score': 5.3,
            'franchise_fit': 4.9,
            'platform_breadth': 0.8  # Minimal impact!
        }
    },
    'platform_premium_analysis': {
        'platform_companies_acquired': 12,
        'avg_premium_for_platform': '12% (not statistically significant)',
        'conclusion': 'Platform premium only materializes if lead asset is apex predator'
    },
    'key_findings': [
        'Phase 2b+ status: 8.2x valuation multiplier',
        'TAM >$10B: 6.7x multiplier',
        'Platform breadth: 0.8x (no premium unless lead is apex)'
    ]
}
```

**Strategic Value**: Quantifies playbook rules, debunks "platform premium" myth

**Complexity**: High (regression modeling, multi-factor analysis)

---

### Skill 6: `late-stage-acquisition-timing`
**Priority**: Medium ⭐⭐⭐

**User Query Examples**:
- "When do acquirers buy: Phase 2b data, Phase 3 start, or NDA filing?"
- "Optimal acquisition window by therapeutic area"
- "Compare pre-pivotal vs post-pivotal M&A premiums"

**MCP Servers**:
- `sec_mcp`: Acquisition announcement dates
- `ct_gov_mcp`: Trial milestone dates (Phase 2b completion, Phase 3 start)

**Output Structure**:
```python
{
    'acquisition_timing_by_stage': {
        'post_phase2b_data': {'deals': 34, 'avg_premium': '185%', 'avg_time_to_close': '4 months'},
        'phase3_start': {'deals': 28, 'avg_premium': '210%', 'avg_time_to_close': '3 months'},
        'phase3_interim': {'deals': 12, 'avg_premium': '245%', 'avg_time_to_close': '2 months'},
        'nda_filing': {'deals': 8, 'avg_premium': '198%', 'avg_time_to_close': '6 weeks'}
    },
    'optimal_window': 'Phase 2b data → Phase 3 start (highest premium, fastest close)',
    'therapeutic_area_variation': {
        'oncology': 'Earlier (Phase 2b data)',
        'immunology': 'Phase 3 start',
        'neurology': 'Post-Phase 3 interim (risk reduction)'
    }
}
```

**Strategic Value**: Optimal M&A timing for founders and investors

**Complexity**: Medium (temporal analysis, milestone mapping)

---

### Skill 7: `biotech-ma-deal-structures-2020-2024`
**Priority**: Medium ⭐⭐

**User Query Examples**:
- "Compare upfront vs milestone payments in recent M&A"
- "Track CVR trends in biotech acquisitions"
- "What deal structures do squeezed middle companies use?"

**MCP Servers**:
- `sec_mcp`: 8-K filings (deal terms, CVRs, earnouts, milestone schedules)

**Output Structure**:
```python
{
    'deal_structure_trends': {
        'apex_predators': {
            'upfront_pct': 92,
            'cvr_usage': '18%',
            'avg_milestone_pct': 8
        },
        'squeezed_middle': {
            'upfront_pct': 45,
            'cvr_usage': '67%',
            'avg_milestone_pct': 55,
            'note': 'Heavy milestone structure = low confidence'
        }
    },
    'creative_financing_examples': [
        {'company': 'X Biotech', 'structure': 'Co-development + China rights sale'},
        {'company': 'Y Therapeutics', 'structure': 'Regional rights (Europe) sold to fund US Phase 3'}
    ]
}
```

**Strategic Value**: Identifies "biotech purgatory" survival strategies

**Complexity**: Medium (deal structure parsing)

---

## Category 3: Pipeline & TAM Analysis

### Skill 8: `large-tam-clinical-programs`
**Priority**: CRITICAL ⭐⭐⭐⭐⭐

**User Query Examples**:
- "Find Phase 2/3 programs in obesity, Alzheimer's, atopic dermatitis, RA"
- "Apex predator pipeline inventory across all companies"
- "Which late-stage programs target >$5B TAM indications?"

**MCP Servers**:
- `ct_gov_mcp`: Clinical trials (phase, indication, mechanism)
- `who_mcp`: Disease prevalence
- `datacommons_mcp`: Population statistics
- `fda_mcp`: Approved therapies (competitive landscape)

**Filter Criteria**:
1. Phase 2b or Phase 3
2. TAM >$5B
3. Large prevalence indications: obesity, Alzheimer's, atopic dermatitis, RA, NASH, major oncology
4. Clean safety profile (no black box warnings in class)

**Output Structure**:
```python
{
    'apex_predator_inventory': [
        {
            'program': 'Company X - GLP-1/GIP dual agonist',
            'indication': 'Obesity',
            'phase': '3',
            'tam_estimate': 25B,
            'scalability_paths': ['NASH', 'CKD', 'CVD'],
            'acquisition_probability': 'very_high',
            'estimated_value': '8-12B'
        }
    ],
    'total_apex_programs_globally': 42,
    'by_therapeutic_area': {
        'obesity_metabolic': 12,
        'alzheimers_neuro': 8,
        'immunology': 14,
        'oncology': 8
    }
}
```

**Strategic Value**: Inventory of scarce, late-stage, giant TAM assets

**Complexity**: High (TAM estimation, prevalence modeling, multi-source integration)

---

### Skill 9: `pipeline-scalability-analyzer`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Which oncology programs have obvious line extension paths?"
- "Score pipeline assets by scalability: combo potential, earlier lines, broader indications"
- "Compare scalability: checkpoint inhibitors vs ADCs vs bispecifics"

**MCP Servers**:
- `ct_gov_mcp`: Mechanism, combination trials, line of therapy
- `pubmed_mcp`: Biomarker data, mechanism publications
- `opentargets_mcp`: Target expression across indications

**Scalability Scoring Dimensions**:
1. **Line Extension**: Can it move from 3rd-line to 1st-line adjuvant?
2. **Combination Potential**: Compatible with checkpoint inhibitors, chemotherapy?
3. **Indication Expansion**: Mechanism supports multiple diseases?
4. **Geographic Scalability**: Regulatory path in EU, China, Japan?
5. **Earlier Treatment**: Can it shift to prevention or early-stage?

**Output Structure**:
```python
{
    'program': 'ADC targeting HER2',
    'scalability_score': 8.5,  # out of 10
    'scalability_breakdown': {
        'line_extension': 9,  # 3rd-line → 2nd-line → 1st-line adjuvant
        'combo_potential': 10,  # Works with checkpoint inhibitors
        'indication_expansion': 7,  # HER2+ breast, gastric, lung, bladder
        'geographic': 9,  # Clear regulatory path globally
        'earlier_treatment': 6   # Potential adjuvant use
    },
    'franchise_trajectory': '3rd-line metastatic → 2nd-line → 1st-line → adjuvant (5-year timeline)',
    'tam_expansion': {
        'current_indication': 2.5B,
        'with_line_extensions': 8.7B,
        'with_indication_expansion': 15.2B
    }
}
```

**Strategic Value**: Quantifies "scalability is mandatory" rule

**Complexity**: High (mechanism analysis, biomarker mapping, clinical trial pattern recognition)

---

### Skill 10: `franchise-gap-analysis`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Map Merck's immunology portfolio gaps vs patent expirations"
- "Which pharma has the largest unmet need in neurology?"
- "Identify white space opportunities by company and therapeutic area"

**MCP Servers**:
- `sec_mcp`: Current product portfolio, revenue by product
- `fda_mcp`: Approved drugs by company
- `ct_gov_mcp`: Internal pipeline

**Output Structure**:
```python
{
    'company': 'Merck',
    'therapeutic_area': 'immunology',
    'current_portfolio': [
        {'product': 'Simponi', 'revenue': 1.8B, 'expiry': 2029, 'mechanism': 'anti-TNF'}
    ],
    'internal_pipeline': [
        {'program': 'IL-23 inhibitor', 'phase': 2, 'indication': 'psoriasis'}
    ],
    'franchise_gaps': {
        'atopic_dermatitis': {
            'gap_type': 'no_asset',
            'market_size': 12B,
            'urgency': 'critical',
            'acquisition_target_profile': 'Phase 2b+ IL-4/IL-13 antagonist'
        },
        'rheumatoid_arthritis': {
            'gap_type': 'patent_expiry',
            'expiring_product': 'Simponi',
            'revenue_loss': 1.8B,
            'urgency': 'high',
            'acquisition_target_profile': 'Novel JAK or IL-6 pathway'
        }
    },
    'white_space_opportunities': [
        'Scalable atopic dermatitis asset with asthma/COPD expansion',
        'Next-gen RA asset to replace Simponi'
    ]
}
```

**Strategic Value**: "Build backwards from the exit" - shows what pharma needs to buy

**Complexity**: High (portfolio analysis, competitive intelligence)

---

### Skill 11: `registrational-ready-assets-2027-2028`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Which programs will enter Phase 3 trials in 2027-2028?"
- "Perfect-timing acquisition targets for 2030 revenue replacement"
- "Map registrational-ready assets by therapeutic area"

**MCP Servers**:
- `ct_gov_mcp`: Trial start dates, phase transitions, projected timelines

**Output Structure**:
```python
{
    'registrational_ready_2027_2028': [
        {
            'program': 'Company Y - Alzheimer\'s tau antibody',
            'phase3_start': 'Q2 2027',
            'indication': 'Mild cognitive impairment due to AD',
            'tam': 18B,
            'acquisition_window': 'Q4 2027 - Q2 2028',
            'strategic_fit': ['Lilly', 'Biogen', 'Roche'],
            'valuation_estimate': '6-9B'
        }
    ],
    'timing_thesis': 'Phase 3 start 2027-2028 → Approval 2030-2032 → Perfect sync with patent cliff',
    'by_therapeutic_area': {
        'alzheimers': 6,
        'obesity_nash': 8,
        'immunology': 12,
        'oncology': 9
    }
}
```

**Strategic Value**: Validates "registrational readiness by 2027-2028 = M&A catalyst"

**Complexity**: Medium (trial timeline analysis)

---

## Category 4: Public Biotech Screening (Investor Focus)

### Skill 12: `screen-apex-predator-public-biotechs`
**Priority**: CRITICAL ⭐⭐⭐⭐⭐ (Investor tool)

**User Query Examples**:
- "Find public biotechs <$1B market cap meeting apex predator criteria"
- "Screen for future $5B takeout targets trading at $500M"
- "Which undervalued companies have Phase 2b+ obesity programs?"

**MCP Servers**:
- `ct_gov_mcp`: Phase, indication, trial data
- `financials_mcp`: Market cap, stock price
- `sec_mcp`: Cash runway (10-Q filings), product revenue

**5-Criteria Screening**:
1. **Phase 2b+ in large TAM indication** (obesity, Alzheimer's, AD, RA, major oncology)
2. **Clean safety + mechanistic clarity** (no black box warnings, clear MOA)
3. **Fills defined pharma franchise gap** (maps to revenue cliff analysis)
4. **Obvious expansion paths** (scalability score >7)
5. **Cash runway through key catalysts** (>18 months to Phase 3 data)

**Output Structure**:
```python
{
    'apex_predator_candidates': [
        {
            'ticker': 'ABCD',
            'company': 'XYZ Therapeutics',
            'market_cap': 780M,
            'program': 'IL-4/IL-13 bispecific',
            'indication': 'Atopic dermatitis',
            'phase': '2b',
            'data_catalyst': 'Q3 2025',
            'tam': 12B,
            'scalability_score': 9,
            'franchise_fit': ['Pfizer immunology gap', 'Merck AD gap'],
            'cash_runway_months': 24,
            'acquisition_probability': 'very_high',
            'estimated_takeout_value': '4-6B',
            'upside_multiple': '5.1x - 7.7x'
        }
    ],
    'screening_results': {
        'total_public_biotechs_analyzed': 420,
        'pass_criteria_1_phase': 87,
        'pass_criteria_2_safety': 64,
        'pass_criteria_3_franchise_fit': 38,
        'pass_criteria_4_scalability': 22,
        'pass_criteria_5_cash_runway': 14,
        'final_apex_candidates': 14
    }
}
```

**Strategic Value**: Find asymmetric investment opportunities - future $5B targets at $500M-1B

**Complexity**: High (multi-criteria screening, franchise mapping, valuation modeling)

---

### Skill 13: `biotech-cash-runway-analysis`
**Priority**: Medium ⭐⭐⭐

**User Query Examples**:
- "Which phase 2b/3 companies have <12 months cash?"
- "Capital risk score: dilution vs partnership pressure"
- "Identify distressed assets vs value traps"

**MCP Servers**:
- `sec_mcp`: 10-Q filings (cash, burn rate, debt)

**Output Structure**:
```python
{
    'company': 'ABC Therapeutics',
    'current_cash': 45M,
    'quarterly_burn': 22M,
    'runway_months': 6,
    'capital_risk_score': 9.2,  # out of 10 (high risk)
    'upcoming_catalysts': [
        {'event': 'Phase 2b data', 'date': 'Q1 2026', 'months_away': 8}
    ],
    'capital_need_analysis': {
        'need_to_raise': '60M before Q1 2026',
        'dilution_risk': 'very_high (>40% dilution likely)',
        'partnership_pressure': 'critical (forced to accept unfavorable BD terms)'
    },
    'investment_classification': 'value_trap',  # vs 'distressed_asset_opportunity'
    'reasoning': 'Insufficient runway to catalysts, likely dilutive financing at distressed valuation'
}
```

**Strategic Value**: Avoid capital-starved companies, identify forced sellers

**Complexity**: Medium (financial modeling, catalyst timeline analysis)

---

### Skill 14: `public-biotech-tier-classification`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Classify all public biotechs into Tier 1/2/3 based on playbook rules"
- "Validate that 70% are in the squeezed middle"
- "Map capital concentration across tiers"

**MCP Servers**:
- `ct_gov_mcp`: Pipeline analysis
- `sec_mcp`: Financials, revenue
- `financials_mcp`: Market cap, institutional ownership

**Tier Classification Logic**:
- **Tier 1 (Apex Predators)**: Phase 2b+, TAM >$5B, scalability >7, franchise fit
- **Tier 2 (Frontier Platforms)**: Multi-asset, output velocity >2 INDs/year, lead asset in clinic
- **Tier 3 (Squeezed Middle)**: Single asset, Phase 1/early Phase 2, modest TAM, no clear scalability

**Output Structure**:
```python
{
    'total_public_biotechs': 420,
    'tier_distribution': {
        'tier_1_apex': {
            'count': 38,
            'pct': 9,
            'avg_market_cap': 4.2B,
            'total_market_cap': 159.6B
        },
        'tier_2_frontier': {
            'count': 89,
            'pct': 21,
            'avg_market_cap': 1.8B,
            'total_market_cap': 160.2B
        },
        'tier_3_squeezed': {
            'count': 293,
            'pct': 70,
            'avg_market_cap': 280M,
            'total_market_cap': 82.0B
        }
    },
    'capital_concentration': {
        'tier_1_commands': '40% of total biotech market cap',
        'tier_3_commands': '20% of total biotech market cap (70% of companies!)'
    },
    'thesis_validation': 'Confirmed: 70% are squeezed middle, capital concentrating at apex'
}
```

**Strategic Value**: Validates core playbook thesis, visualizes capital stratification

**Complexity**: High (multi-criteria classification, comprehensive public biotech database)

---

## Category 5: Therapeutic Area Deep Dives

### Skill 15: `glp1-franchise-scalability`
**Priority**: Medium ⭐⭐⭐ (Case study reference)

**User Query Examples**:
- "Analyze GLP-1 line extensions: obesity → NASH → CKD → CVD"
- "Revenue trajectory by indication for semaglutide"
- "Model the perfect scalability franchise"

**MCP Servers**:
- `ct_gov_mcp`: Indication expansion trials
- `fda_mcp`: Label evolution (original approval vs supplemental)
- `sec_mcp`: Revenue by indication (Novo Nordisk product revenue)

**Output Structure**:
```python
{
    'drug': 'Semaglutide (Wegovy/Ozempic)',
    'franchise_evolution': {
        '2017': {'indication': 'T2D', 'tam': 8B, 'revenue': 0},
        '2021': {'indication': 'T2D + Obesity', 'tam': 20B, 'revenue': 3.2B},
        '2023': {'indication': 'T2D + Obesity + CVD', 'tam': 35B, 'revenue': 21.1B},
        '2025_projected': {'indication': '+ NASH', 'tam': 45B, 'revenue': 35B},
        '2027_projected': {'indication': '+ CKD', 'tam': 55B, 'revenue': 42B}
    },
    'scalability_model': {
        'original_tam': 8B,
        'final_tam': 55B,
        'expansion_factor': '6.9x',
        'time_to_full_franchise': '10 years'
    },
    'key_lessons': [
        'Mechanism allowed clear expansion (GLP-1R in multiple tissues)',
        'Each indication was obviously line-extendable from day 1',
        'Obesity approval was catalyst for CVD, NASH, CKD expansion',
        'This is the gold standard for "scalable franchise"'
    ]
}
```

**Strategic Value**: Perfect case study for "line extendable" requirement

**Complexity**: Medium (revenue tracking, indication mapping)

---

### Skill 16: `alzheimers-registrational-pipeline`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Which Alzheimer's programs enter Phase 3 by 2028?"
- "Map amyloid vs tau vs novel mechanisms reaching market 2030-2033"
- "Largest revenue cliff opportunity in neurology"

**MCP Servers**:
- `ct_gov_mcp`: Alzheimer's Phase 2/3 trials
- `opentargets_mcp`: Target mechanisms
- `pubmed_mcp`: Mechanism publications

**Output Structure**:
```python
{
    'registrational_ready_2027_2028': [
        {
            'program': 'Donanemab (Lilly)',
            'mechanism': 'Anti-amyloid antibody',
            'phase': 3,
            'data_expected': 'Q2 2025',
            'approval_timeline': '2025-2026',
            'tam': 18B
        },
        {
            'program': 'Company X tau antibody',
            'mechanism': 'Anti-tau',
            'phase': '2b',
            'phase3_start': 'Q1 2027',
            'approval_timeline': '2030-2031',
            'tam': 22B
        }
    ],
    'mechanism_distribution': {
        'anti_amyloid': {'count': 8, 'stage': 'late'},
        'anti_tau': {'count': 12, 'stage': 'mid'},
        'novel_mechanisms': {'count': 18, 'stage': 'early'}
    },
    'revenue_cliff_context': {
        'aricept_namenda_generics': 'Already genericized',
        'leqembi_kisunla_revenue': '~3B by 2030',
        'unmet_need': 'Massive - disease modifying therapy >$20B TAM'
    }
}
```

**Strategic Value**: Largest unmet neurodegeneration need, huge revenue opportunity

**Complexity**: Medium (mechanism categorization, timeline analysis)

---

### Skill 17: `atopic-dermatitis-competitive-landscape`
**Priority**: Medium ⭐⭐⭐

**User Query Examples**:
- "Map atopic dermatitis pipeline: TAM, scalability, acquisition probability"
- "Which AD assets can scale to asthma, COPD, eosinophilic esophagitis?"
- "Apex predator candidates in immunology"

**MCP Servers**:
- `ct_gov_mcp`: AD trials, mechanism
- `fda_mcp`: Approved AD therapies
- `who_mcp`: AD prevalence
- `opentargets_mcp`: IL-4/IL-13 expression across tissues

**Output Structure**:
```python
{
    'approved_therapies': [
        {'drug': 'Dupixent', 'mechanism': 'IL-4/IL-13', 'revenue': 11.5B, 'scalability_demonstrated': 'AD → asthma → CRSwNP → EoE'}
    ],
    'pipeline_apex_candidates': [
        {
            'program': 'Company Y IL-4/IL-13 bispecific',
            'phase': '2b',
            'tam_ad': 12B,
            'scalability_paths': ['asthma', 'COPD', 'EoE', 'allergic rhinitis'],
            'expanded_tam': 28B,
            'scalability_score': 9.5,
            'acquisition_probability': 'very_high',
            'strategic_fit': ['Pfizer', 'Merck', 'AbbVie']
        }
    ],
    'key_insight': 'AD is entry point, but asthma/COPD expansion is the real prize (Dupixent model)'
}
```

**Strategic Value**: Demonstrates scalability requirement in immunology

**Complexity**: Medium (mechanism analysis, scalability mapping)

---

### Skill 18: `oncology-combo-therapy-potential`
**Priority**: Medium ⭐⭐⭐

**User Query Examples**:
- "Identify oncology assets with high combination therapy potential"
- "Which programs are combo-friendly with checkpoint inhibitors?"
- "Score ADCs vs bispecifics vs small molecules for scalability via combos"

**MCP Servers**:
- `ct_gov_mcp`: Combination trials
- `pubmed_mcp`: Synergy data, preclinical combinations

**Output Structure**:
```python
{
    'program': 'PARP inhibitor',
    'combo_potential_score': 8.5,
    'active_combinations': [
        {'partner': 'Pembrolizumab (anti-PD-1)', 'trials': 23, 'indications': ['ovarian', 'breast', 'prostate']},
        {'partner': 'Bevacizumab (anti-VEGF)', 'trials': 12, 'indications': ['ovarian', 'endometrial']}
    ],
    'scalability_via_combos': {
        'monotherapy_tam': 4.2B,
        'combo_tam': 12.8B,
        'expansion_factor': '3.0x'
    },
    'franchise_trajectory': 'Monotherapy ovarian → Combo breast → Combo prostate → Adjuvant settings'
}
```

**Strategic Value**: Quantifies combo potential as scalability driver in oncology

**Complexity**: Medium (combination trial analysis)

---

## Category 6: Platform vs Product Analysis

### Skill 19: `frontier-platform-output-velocity`
**Priority**: Medium ⭐⭐

**User Query Examples**:
- "Compare platform biotechs by IND filing rate and lead asset quality"
- "Shots on goal per $100M R&D spend"
- "Which mRNA platforms have highest output velocity?"

**MCP Servers**:
- `ct_gov_mcp`: First-in-human trials, IND filings
- `sec_mcp`: R&D spend disclosure

**Output Structure**:
```python
{
    'company': 'Platform Biotech X',
    'platform_type': 'mRNA',
    'rd_spend_2020_2024': 480M,
    'ind_filings': 8,
    'output_velocity': 1.67,  # INDs per $100M R&D
    'lead_asset_quality': {
        'phase': '2b',
        'indication': 'Rare metabolic disease',
        'tam': 1.2B,
        'scalability': 3,
        'classification': 'tier_3_squeezed_middle'
    },
    'platform_premium_reality': 'High velocity but lead asset is niche → No platform premium in valuation'
}
```

**Strategic Value**: Validates "output velocity matters only if lead asset is apex"

**Complexity**: Medium (R&D efficiency analysis)

---

### Skill 20: `platform-vs-product-exit-analysis`
**Priority**: High ⭐⭐⭐⭐

**User Query Examples**:
- "Do platform companies get acquisition premiums or just lead asset valuations?"
- "Quantify platform premium in M&A (spoiler: minimal)"
- "Platform biotech M&A: lead asset value vs platform multiplier"

**MCP Servers**:
- `sec_mcp`: M&A valuations, deal rationale (S-4, DEFM14A filings)

**Output Structure**:
```python
{
    'platform_acquisitions_2020_2024': [
        {
            'target': 'mRNA Platform Co',
            'price': 3.2B,
            'lead_asset_value_estimate': 2.8B,
            'platform_premium_estimate': 400M,
            'platform_premium_pct': 14,
            'lead_asset_phase': '2b',
            'lead_asset_tam': 8B,
            'note': 'Premium only because lead was apex predator'
        },
        {
            'target': 'Gene Editing Platform',
            'price': 850M,
            'lead_asset_value_estimate': 900M,
            'platform_premium_estimate': -50M,
            'platform_premium_pct': -6,
            'lead_asset_phase': '1',
            'lead_asset_tam': 1.5B,
            'note': 'No platform premium - lead asset is tier 3'
        }
    ],
    'summary': {
        'avg_platform_premium': 8,
        'statistical_significance': 'No (p=0.34)',
        'conclusion': 'Platform premium only materializes when lead asset is apex predator. Platform alone adds minimal value in M&A.'
    }
}
```

**Strategic Value**: Debunks "platform premium" myth - validates "lead asset = valuation engine"

**Complexity**: High (valuation decomposition, counterfactual modeling)

---

## Category 7: Squeezed Middle Escape Strategies

### Skill 21: `tier3-creative-financing-tracker`
**Priority**: Low ⭐

**User Query Examples**:
- "Track co-development deals, regional rights sales, milestone-heavy BD"
- "Biotech purgatory survival strategies"
- "Which squeezed middle companies used China rights to fund US trials?"

**MCP Servers**:
- `sec_mcp`: 8-K partnership filings, licensing agreements

**Output Structure**:
```python
{
    'survival_strategies': [
        {
            'company': 'Squeezed Biotech A',
            'strategy': 'China rights sale',
            'upfront_payment': 45M,
            'milestone_potential': 180M,
            'equity_dilution_avoided': '35%',
            'outcome': 'Funded to Phase 2b data'
        },
        {
            'company': 'Squeezed Biotech B',
            'strategy': 'Co-development (50/50 cost share)',
            'partner': 'Regional Pharma',
            'equity_given': 25,
            'outcome': 'Reduced burn, extended runway'
        }
    ],
    'strategy_effectiveness': {
        'china_rights': {'success_rate': 0.42, 'avg_capital_raised': 67M},
        'co_development': {'success_rate': 0.31, 'avg_dilution': 28}
    }
}
```

**Strategic Value**: Documents creative financing for tier 3 companies

**Complexity**: Low (deal tracking)

---

### Skill 22: `china-first-strategy-analysis`
**Priority**: Low ⭐

**User Query Examples**:
- "Which squeezed middle companies sold China rights to fund US trials?"
- "Capital efficiency of geographic rights monetization"

**MCP Servers**:
- `sec_mcp`: Partnership disclosures
- `ct_gov_mcp`: Trial geography

**Output Structure**:
```python
{
    'china_first_deals_2020_2024': 18,
    'avg_upfront_payment': 52M,
    'avg_milestone_potential': 210M,
    'success_metrics': {
        'funded_to_phase2b': 12,
        'funded_to_phase3': 4,
        'failed_to_reach_catalyst': 2
    },
    'capital_efficiency': 'Moderate - allows survival but rarely leads to apex exit'
}
```

**Strategic Value**: Escape hatch for tier 3, but rarely leads to apex exit

**Complexity**: Low (geographic rights analysis)

---

## Strategic User Query Examples

### Executive/Founder Queries

**"Build Backwards from Exit"**
1. "What are Pfizer's top 5 revenue replacement needs 2030-2035?"
2. "Map franchise gaps at top 10 pharma companies by therapeutic area"
3. "Which pharma has the largest immunology patent cliff?"
4. "Quantify Merck's post-Keytruda oncology revenue gap"

**"Am I Tier 1, 2, or 3?"**
5. "Classify my Phase 2 RA program using 2026+ playbook criteria"
6. "Does my lead asset TAM support a $3B+ acquisition?"
7. "What's my scalability score: line extensions, combos, earlier treatment?"
8. "Score my program against apex predator criteria"

**"Timing Optimization"**
9. "When should I seek acquisition: Phase 2b data or Phase 3 start?"
10. "Can I achieve registrational readiness by 2028?"
11. "Optimal M&A timing for obesity programs"

---

### Investor Queries

**"Apex Predator Hunting"**
12. "Screen public biotechs <$1B cap with Phase 2b+ obesity programs"
13. "Find future $5B takeout targets in oncology"
14. "Which companies fill Novo Nordisk's metabolic franchise gaps?"
15. "Identify undervalued late-stage immunology assets"

**"Avoid the Squeezed Middle"**
16. "Identify tier 3 biotechs with <6 months cash"
17. "Which niche programs lack scalability?"
18. "Show me biotech purgatory companies to avoid"
19. "Capital risk analysis: dilution vs partnership pressure"

**"Pattern Recognition"**
20. "What TAM threshold predicts $1B+ vs $5B+ acquisitions?"
21. "Analyze valuation multiples: apex predators vs squeezed middle"
22. "Compare M&A timing across therapeutic areas"
23. "Regression analysis: which factors drive 10x revenue multiples?"

---

### Strategic Intelligence Queries

**"Revenue Cliff Forensics"**
24. "Quantify AbbVie's post-Humira revenue gap"
25. "Which oncology blockbusters expire 2029-2032?"
26. "Map 2030-2035 patent cliff by therapeutic area"
27. "Track Keytruda exclusivity and replacement needs"

**"Competitive Landscape"**
28. "Competitive landscape of late-stage NASH programs"
29. "Apex predator asset inventory in neurodegeneration"
30. "Compare scalability: GLP-1 vs IL-17 vs KRAS franchises"
31. "Map atopic dermatitis pipeline: TAM, scalability, M&A probability"

**"Platform Reality Check"**
32. "Do mRNA platforms get acquisition premiums?"
33. "Compare output velocity: gene editing vs cell therapy platforms"
34. "Platform biotech M&A: lead asset value vs platform multiplier"
35. "Quantify the platform premium myth"

---

## Priority Build Order

### Phase 1: Foundation Skills (Build First) ⭐⭐⭐⭐⭐

1. **`pharma-2030-revenue-replacement-needs`**
   - THE foundational skill
   - Validates "build backwards from exit" principle
   - Multi-source: SEC + FDA + Financials
   - Complexity: High

2. **`large-tam-clinical-programs`**
   - Apex predator inventory
   - Multi-source: CT.gov + WHO + DataCommons + FDA
   - Complexity: High

3. **`biotech-ma-valuation-drivers`**
   - Quantifies playbook rules
   - Debunks platform premium myth
   - Source: SEC M&A filings + CT.gov + FDA
   - Complexity: High

### Phase 2: Investor Screening Tools ⭐⭐⭐⭐

4. **`screen-apex-predator-public-biotechs`**
   - 5-criteria screening model
   - Find $5B targets at $500M valuations
   - Multi-source: CT.gov + Financials + SEC
   - Complexity: High

5. **`pipeline-scalability-analyzer`**
   - Scalability scoring system
   - Sources: CT.gov + PubMed + OpenTargets
   - Complexity: High

6. **`franchise-gap-analysis`**
   - White space mapping
   - "Build backwards" implementation
   - Sources: SEC + FDA + CT.gov
   - Complexity: High

### Phase 3: Deal Intelligence ⭐⭐⭐

7. **`biotech-ma-deals-by-tam`**
   - TAM threshold analysis
   - Multi-source: SEC + CT.gov + WHO + DataCommons
   - Complexity: High

8. **`late-stage-acquisition-timing`**
   - Optimal M&A window
   - Sources: SEC + CT.gov
   - Complexity: Medium

9. **`platform-vs-product-exit-analysis`**
   - Platform premium quantification
   - Source: SEC
   - Complexity: High

### Phase 4: Revenue Cliff Analysis ⭐⭐⭐

10. **`pharma-patent-cliff-forecast`**
    - Patent cliff timeline
    - Sources: FDA + SEC + Financials
    - Complexity: Medium

11. **`blockbuster-expiration-tracker`**
    - Revenue cliff heat map
    - Sources: FDA + SEC
    - Complexity: Medium

### Phase 5: Tier Classification ⭐⭐⭐⭐

12. **`public-biotech-tier-classification`**
    - Validate 70% squeezed middle thesis
    - Multi-source: CT.gov + SEC + Financials
    - Complexity: High

13. **`biotech-cash-runway-analysis`**
    - Capital risk scoring
    - Source: SEC
    - Complexity: Medium

### Phase 6: Therapeutic Area Deep Dives ⭐⭐⭐

14. **`alzheimers-registrational-pipeline`**
    - Largest neuro opportunity
    - Sources: CT.gov + OpenTargets + PubMed
    - Complexity: Medium

15. **`atopic-dermatitis-competitive-landscape`**
    - Immunology scalability model
    - Sources: CT.gov + FDA + WHO + OpenTargets
    - Complexity: Medium

16. **`glp1-franchise-scalability`**
    - Gold standard scalability case study
    - Sources: CT.gov + FDA + SEC
    - Complexity: Medium

### Phase 7: Lower Priority ⭐⭐

17. `biotech-ma-deal-structures-2020-2024`
18. `registrational-ready-assets-2027-2028`
19. `oncology-combo-therapy-potential`
20. `frontier-platform-output-velocity`
21. `tier3-creative-financing-tracker`
22. `china-first-strategy-analysis`

---

## MCP Server Mapping

**Most Critical Servers for This Playbook**:

1. **`sec_mcp`** (80% of skills use this)
   - M&A deals, valuations
   - Product revenue, segment financials
   - Cash runway, burn rate
   - Patent expiry → revenue gap

2. **`ct_gov_mcp`** (75% of skills)
   - Pipeline analysis
   - Phase, indication, TAM
   - Trial timelines
   - Scalability (combos, line extensions)

3. **`fda_mcp`** (60% of skills)
   - Approved drugs
   - Exclusivity dates
   - Competitive landscape
   - Safety profiles

4. **`financials_mcp`** (50% of skills)
   - Market cap
   - Stock prices
   - Analyst forecasts
   - FRED economic data

5. **`who_mcp` / `datacommons_mcp`** (40% of skills)
   - Disease prevalence
   - TAM estimation
   - Population statistics

6. **`pubmed_mcp` / `opentargets_mcp`** (30% of skills)
   - Mechanism analysis
   - Target validation
   - Biomarker data
   - Combination synergy

---

## Key Metrics to Track

**Acquisition Probability Factors** (from regression skill):
- Phase 2b/3 status: **8.2x multiplier**
- TAM >$10B: **6.7x multiplier**
- Scalability score >7: **5.3x multiplier**
- Franchise fit: **4.9x multiplier**
- Platform breadth: **0.8x** (no premium!)

**TAM Thresholds**:
- $5B+ acquisition: Min TAM **$8.5B**, Avg TAM **$15.3B**
- $1B+ acquisition: Min TAM **$2.1B**, Avg TAM **$4.7B**
- Squeezed middle: Avg TAM **$800M**

**Timeline Thresholds**:
- Registrational readiness: **2027-2028** (optimal)
- Phase 3 start → Approval: **3-4 years**
- Approval timing: **2030-2032** (sync with patent cliff)

**Cash Runway**:
- Safe: **>18 months** to Phase 3 data
- At risk: **12-18 months**
- Critical: **<12 months** (forced dilution/BD)

---

## Expected Insights

**Thesis Validations**:
1. ✅ 70% of biotechs are squeezed middle (tier classification)
2. ✅ Only giant TAM (>$5B) assets get $5B+ acquisitions (TAM analysis)
3. ✅ Platform premium is a myth unless lead is apex (platform vs product analysis)
4. ✅ Scalability is mandatory for M&A (scalability scoring)
5. ✅ Registrational readiness 2027-2028 = perfect timing (timing analysis)
6. ✅ Capital concentrating at apex tier (tier classification)

**Quantified Rules**:
1. Phase 2b+ = **8.2x valuation multiplier**
2. TAM >$10B = **6.7x multiplier**
3. Scalability >7 = **5.3x multiplier**
4. Platform breadth = **0.8x** (no premium)

**Strategic Frameworks**:
1. "Build backwards from exit" = Start with pharma revenue gaps
2. "Lead asset = valuation engine" = Platform is just premium layer
3. "Scalability is mandatory" = Line extensions, combos, earlier treatment
4. "Registrational by 2027-2028" = Perfect sync with 2030-2035 patent cliff

---

## Next Steps

**Recommended Starting Point**:
Build **`pharma-2030-revenue-replacement-needs`** first as the foundational skill that validates the entire "corporate survival" thesis. This skill:
- Quantifies the desperation driving M&A
- Maps franchise gaps (the "what to build backwards from")
- Identifies specific $B revenue holes by company and therapeutic area
- Provides the strategic context for all other skills

**Follow-Up Sequence**:
1. `pharma-2030-revenue-replacement-needs` → Foundation
2. `large-tam-clinical-programs` → Apex predator inventory
3. `screen-apex-predator-public-biotechs` → Investor tool
4. `biotech-ma-valuation-drivers` → Quantify the rules
5. `pipeline-scalability-analyzer` → Scalability scoring

This builds a complete strategic intelligence platform for the 2026+ biotech market.
