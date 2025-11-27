# CVD Precision Medicine Opportunity Assessment

**Status**: Conceptual
**Priority**: Medium
**Complexity**: Medium-High
**Estimated Value**: $5B+ market opportunity validation
**Implementation Time**: 2-3 hours (initial analysis)

---

## Overview

**Business Problem**: Cardiovascular disease (CVD) is the leading cause of death globally (17.9M deaths/year, $1 trillion annual cost), but treatments are largely "one-size-fits-all" (statins, beta-blockers, ACE inhibitors). Precision medicine revolution (genetic risk scores, biomarker-driven patient selection) promises to identify high-risk subpopulations who benefit most from targeted therapies.

**Decision**: Should we invest $500M-2B in CVD precision medicine programs (genetic testing + targeted therapies)? Which patient segments have highest ROI?

**Impact**: Validates $5B+ market opportunity for precision CVD therapies, guides R&D portfolio allocation.

---

## Why This Scenario is Compelling (7/10)

### Strategic Importance
- **Massive disease burden**: 17.9M CVD deaths/year, $1 trillion annual cost (larger than oncology)
- **Genetic revolution**: Polygenic risk scores identify patients with 5-10x higher CVD risk
- **Pharma precedent**: PCSK9 inhibitors showed precision medicine works (genetic validation → targeted therapy → approval)
- **Unmet need**: Current therapies miss 30-40% of high-risk patients (poor response to statins)

### Multi-Dimensional Analysis Required
- **Disease burden**: Global CVD epidemiology (cvd-disease-burden, cvd-burden-per-capita)
- **Genetic targets**: Validate precision medicine targets (disease-genetic-targets)
- **Clinical landscape**: CVD trials by mechanism (company-clinical-trials-portfolio, indication-pipeline-breakdown)
- **Market validation**: Per-capita burden to justify targeted therapies (cvd-burden-per-capita)
- **Competitive positioning**: Who is developing precision CVD therapies? (company-pipeline-indications)

### Actionable Output
Investment recommendation: "Invest $500M in PCSK9-related programs for familial hypercholesterolemia subset" or "Avoid - genetic risk scores not yet actionable clinically"

---

## Skills Orchestration

| Phase | Skill | MCP Server | Purpose | Expected Output |
|-------|-------|------------|---------|-----------------|
| **1. Disease Burden Quantification** | cvd-disease-burden | who_mcp | Global CVD mortality and morbidity | 17.9M deaths/year, prevalence by country |
| | cvd-burden-per-capita | who_mcp + datacommons_mcp | Per-capita burden to validate market size | Deaths per 100k population by country |
| **2. Genetic Target Validation** | disease-genetic-targets | opentargets_mcp | Precision medicine targets (PCSK9, APOE, LPA) | Genetic association scores for CVD targets |
| **3. Clinical Landscape Mapping** | company-clinical-trials-portfolio | ct_gov_mcp | CVD trials by sponsor and mechanism | 500+ CVD trials by phase and target |
| | indication-pipeline-breakdown | ct_gov_mcp | Pipeline density by CVD subtype | Trials for heart failure, MI, stroke, dyslipidemia |
| **4. Precision Medicine Pipeline** | company-pipeline-indications | ct_gov_mcp + opentargets_mcp | Who is developing precision CVD therapies? | Genetic biomarker-driven CVD trials |
| **5. Market Opportunity Sizing** | disease-burden-per-capita | who_mcp + datacommons_mcp | Per-capita analysis for targeted therapy pricing | Market size for high-risk subpopulations |

**Total**: 6 core skills (note: cvd-burden-per-capita used twice for different analyses) across 3 MCP servers

---

## Detailed Analytical Workflow

### Phase 1: Disease Burden Quantification (Validate Market Size)

**Objective**: Quantify global CVD burden to understand total addressable market.

**Skills Execution**:
```python
# 1. Global CVD mortality and morbidity
cvd_burden = cvd_disease_burden()
# Output:
# - Global deaths: 17.9 million/year (32% of all deaths)
# - Ischemic heart disease: 9.1M deaths/year
# - Stroke: 6.2M deaths/year
# - Heart failure: 2.6M deaths/year
# - Cost: $1 trillion/year (direct + indirect)
# - Demographics: Increasing with aging populations (projected 25M deaths/year by 2030)

# 2. Per-capita burden by country
per_capita_burden = cvd_burden_per_capita()
# Output (deaths per 100k population):
# - Russia: 650 deaths/100k (highest)
# - Eastern Europe: 450-550 deaths/100k
# - United States: 220 deaths/100k
# - Western Europe: 150-200 deaths/100k
# - Japan: 100 deaths/100k (lowest among developed countries)
#
# High-risk populations:
# - Eastern Europe, Central Asia: 2-3x higher burden than Western Europe
# - Opportunity: Target high-burden regions with precision therapies
```

**Analysis**:
- **Total market**: $1 trillion annual cost, 17.9M deaths/year
- **Geographic variation**: 6x difference between highest (Russia) and lowest (Japan) burden
- **Addressable market**: If precision medicine reduces CVD by 20% in high-risk 10% of population:
  - 10% of 17.9M deaths = 1.79M high-risk patients/year
  - 20% reduction = 358k lives saved/year
  - Therapy value: $50k/year × 10M high-risk patients = $500B addressable market

**Key Insight**: Market is massive ($1T total, $500B addressable for precision therapies), with high geographic variation suggesting genetic and environmental risk factors.

---

### Phase 2: Genetic Target Validation (Is Precision Medicine Real?)

**Objective**: Validate that CVD has actionable genetic targets for precision medicine.

**Skills Execution**:
```python
# 3. CVD genetic targets
genetic_targets = disease_genetic_targets(disease="cardiovascular disease")
# Output:
# - PCSK9: Association score 0.92 (loss-of-function variants = 50% lower LDL, 90% lower CVD risk)
#   - Actionable: PCSK9 inhibitors approved (Repatha, Praluent), genetic testing identifies super-responders
# - APOE4: Association score 0.88 (3x higher CVD risk, poor statin response)
#   - Actionable: Genetic testing → alternative lipid-lowering (ezetimibe, bempedoic acid)
# - LPA (Lipoprotein(a)): Association score 0.85 (high Lp(a) = 2-4x CVD risk, resistant to statins)
#   - Actionable: Lp(a)-lowering therapies in Phase 3 (pelacarsen, olpasiran)
# - LDLR (familial hypercholesterolemia): Association score 0.95 (20x higher CVD risk)
#   - Actionable: Intensive LDL-lowering (PCSK9 inhibitors, ezetimibe, statins)
# - 9p21 locus: Association score 0.75 (1.5x higher MI risk, mechanism unclear)
#   - Not yet actionable (no therapies targeting this pathway)
```

**Analysis**:
- **Validated targets**: PCSK9, APOE4, LPA, LDLR (all have approved therapies or Phase 3 programs)
- **Genetic validation**: Association scores 0.85-0.95 (very strong evidence)
- **Precision medicine proof**: PCSK9 inhibitors reduce CVD by 50-60% in genetic high-risk patients (vs. 20-30% in general population)
- **Unmet need**: Lp(a) affects 20% of population, no approved therapies yet (Phase 3 programs ongoing)

**Key Insight**: CVD precision medicine is REAL and VALIDATED (PCSK9 proof-of-concept). Multiple targets with genetic evidence and therapies in development.

---

### Phase 3: Clinical Landscape Mapping (What's in Development?)

**Objective**: Map CVD clinical trials to identify precision medicine programs.

**Skills Execution**:
```python
# 4. CVD trials by sponsor
cvd_trials = company_clinical_trials_portfolio(therapeutic_area="cardiovascular")
# Output:
# - Total trials: 3,500+ (all CVD subtypes)
# - Heart failure: 800 trials (device + drug)
# - Dyslipidemia: 450 trials (statins, PCSK9 inhibitors, Lp(a)-lowering)
# - Hypertension: 600 trials
# - Thrombosis: 350 trials
# - Precision medicine trials (genetic biomarker): 120 trials (3% of total)

# 5. Pipeline by CVD subtype
pipeline_breakdown = indication_pipeline_breakdown(indication="dyslipidemia")
# Output:
# - PCSK9 inhibitors: 25 trials (market saturated: Repatha, Praluent approved)
# - Lp(a)-lowering: 15 trials (Phase 3: pelacarsen, olpasiran; Phase 2: multiple siRNAs)
# - Bempedoic acid: 10 trials (approved 2023, oral LDL-lowering for statin-intolerant)
# - ANGPTL3 inhibitors: 8 trials (Phase 2, triglyceride-lowering)
# - Gene therapy: 5 trials (Phase 1/2, one-time PCSK9 silencing)

# 6. Precision medicine pipeline
precision_trials = company_pipeline_indications(indication="cardiovascular", biomarker="genetic")
# Output:
# - Amgen (Repatha): Phase 4 studies with PCSK9 genetic testing for patient selection
# - Novartis (pelacarsen): Phase 3 Lp(a)-lowering, genetic high-risk population
# - Arrowhead (ARO-APOC3): Phase 2, familial chylomicronemia (ultra-rare, genetic)
# - Verve Therapeutics (VERVE-101): Phase 1, in vivo gene editing for PCSK9 (familial hypercholesterolemia)
```

**Analysis**:
- **PCSK9 space**: Saturated (Repatha, Praluent approved, multiple biosimilars coming)
- **Lp(a) space**: HOT (15 trials, Phase 3 readouts 2025-2026, no approved therapies yet)
- **Gene therapy**: EARLY (Phase 1/2, one-time treatment, curative potential for familial hypercholesterolemia)
- **Precision medicine adoption**: SLOW (only 3% of CVD trials use genetic biomarkers)

**Key Insight**: Lp(a)-lowering is the next big precision CVD opportunity (Phase 3 programs, genetic validation, 20% population prevalence, no competition yet).

---

### Phase 4: Market Opportunity Sizing (What's the ROI?)

**Objective**: Calculate addressable market for precision CVD therapies by patient segment.

**Skills Execution**:
```python
# 7. Per-capita burden for targeted therapy pricing
per_capita_analysis = cvd_burden_per_capita()
# Output (deaths per 100k):
# - High-burden countries (Eastern Europe, Central Asia): 450-650 deaths/100k
# - Medium-burden (US, Western Europe): 150-250 deaths/100k
# - Low-burden (Japan, South Korea): 100-150 deaths/100k
#
# Market sizing by genetic segment:
# - PCSK9 loss-of-function carriers: 2-3% of population (very low CVD risk, no therapy needed)
# - PCSK9 gain-of-function carriers: <1% of population (familial hypercholesterolemia, need intensive therapy)
# - High Lp(a) (>50 mg/dL): 20% of population (2-4x CVD risk)
#   - Addressable: 20% × 1 billion adults (high CVD risk regions) = 200M patients
#   - Pricing: $5,000-10,000/year (similar to PCSK9 inhibitors)
#   - Market: $1-2 trillion (if all treated)
#   - Realistic market (10% penetration): $100-200B
# - APOE4 carriers: 25% of population (1.5-3x CVD risk, poor statin response)
#   - Addressable: 25% × 1 billion adults = 250M patients
#   - Therapy: Alternative lipid-lowering (ezetimibe, bempedoic acid)
#   - Market: $50-100B (lower pricing than PCSK9 inhibitors)
```

**Analysis**:
- **PCSK9 market**: Saturated ($5-10B, limited to familial hypercholesterolemia and statin-intolerant patients)
- **Lp(a) market**: MASSIVE ($100-200B addressable, 200M high-risk patients globally, no approved therapies)
- **APOE4 market**: LARGE ($50-100B, 250M patients, but requires genetic testing infrastructure)
- **Gene therapy market**: NICHE ($5-10B, familial hypercholesterolemia only, curative potential)

**Key Insight**: Lp(a)-lowering therapies have $100-200B market potential (10x larger than PCSK9). This is the precision CVD mega-opportunity.

---

## Expected Output Format

### Executive Summary Dashboard

```markdown
## CVD Precision Medicine Investment Thesis

### Disease Burden ✅ MASSIVE
- **Global CVD Mortality**: 17.9M deaths/year (32% of all deaths)
- **Annual Cost**: $1 trillion (direct + indirect)
- **Demographics**: Increasing (projected 25M deaths/year by 2030)
- **Geographic Variation**: 6x difference (Russia 650/100k vs. Japan 100/100k)

### Genetic Validation ✅ STRONG
- **PCSK9**: Association 0.92, loss-of-function = 90% lower CVD risk (VALIDATED: Repatha, Praluent approved)
- **Lp(a)**: Association 0.85, high levels = 2-4x CVD risk (EMERGING: Phase 3 programs ongoing)
- **APOE4**: Association 0.88, 3x higher CVD risk, poor statin response (ACTIONABLE: genetic testing → alternative therapies)
- **LDLR**: Association 0.95, familial hypercholesterolemia = 20x CVD risk (VALIDATED: intensive LDL-lowering)

### Clinical Landscape ⚠️ PCSK9 SATURATED / LP(A) OPPORTUNITY
- **PCSK9 inhibitors**: 25 trials (AVOID - market saturated, Repatha/Praluent approved)
- **Lp(a)-lowering**: 15 trials (OPPORTUNITY - Phase 3 readouts 2025-2026, no approved therapies)
- **Gene therapy**: 5 trials (EARLY - Phase 1/2, curative potential for familial hypercholesterolemia)
- **Precision medicine adoption**: SLOW (only 3% of CVD trials use genetic biomarkers)

### Market Opportunity ✅ $100-200B (LP(A) ALONE)
- **PCSK9 market**: $5-10B (saturated, limited to familial hypercholesterolemia)
- **Lp(a) market**: $100-200B (200M high-risk patients, no approved therapies, Phase 3 programs)
- **APOE4 market**: $50-100B (250M patients, requires genetic testing infrastructure)
- **Gene therapy market**: $5-10B (niche, familial hypercholesterolemia only)

### RECOMMENDATION: STRATEGIC YES - INVEST IN LP(A)-LOWERING

**Investment Strategy**:
1. **Acquire Lp(a)-lowering asset** (Phase 2/3 stage, $500M-1B valuation)
   - Rationale: $100-200B market, genetic validation, no approved therapies, Phase 3 readouts 2025-2026
   - Risk: Phase 3 failure (30% probability), competitive landscape (2-3 programs in Phase 3)
   - ROI: $10-20B peak revenue (10-20% market share of $100B market)

2. **Partner on APOE4 genetic testing** (diagnostic + therapeutic package)
   - Rationale: 25% population carries APOE4, poor statin response → alternative therapies needed
   - Investment: $100-200M (genetic testing infrastructure + alternative lipid-lowering promotion)
   - ROI: $5-10B peak revenue (alternative therapies: ezetimibe, bempedoic acid)

3. **Monitor gene therapy programs** (wait for Phase 2 data)
   - Rationale: Curative potential (one-time treatment) for familial hypercholesterolemia
   - Risk: Early stage (Phase 1/2), safety concerns (in vivo gene editing), regulatory path unclear
   - Investment: $0 now (wait for more data), option to acquire for $300-500M if Phase 2 successful

**Total Investment**: $600M-1.3B (Lp(a) acquisition + APOE4 partnership)
**Expected ROI**: $15-30B peak revenue (risk-adjusted)

### AVOID: Me-too PCSK9 inhibitors (market saturated)
```

### Detailed Supporting Analysis

**Section 1: CVD Disease Burden**
- Global mortality and morbidity by CVD subtype (ischemic heart disease, stroke, heart failure)
- Per-capita burden by country (identify high-burden regions for targeted therapies)
- Cost breakdown (direct medical costs, indirect productivity losses)
- Demographics (aging populations = increasing burden)

**Section 2: Genetic Target Validation**
- Top 10 genetic targets for CVD with association scores
- Mechanism of action (PCSK9 LDL-lowering, Lp(a) thrombosis, APOE4 poor statin response)
- Proof-of-concept (PCSK9 inhibitors reduce CVD by 50-60% in genetic high-risk patients)
- Unmet needs (Lp(a) has no approved therapies despite 20% population prevalence)

**Section 3: Competitive Pipeline**
- Trials by mechanism (PCSK9, Lp(a), ANGPTL3, APOC3, gene therapy)
- Phase distribution (Phase 3 readouts expected 2025-2026 for Lp(a) programs)
- Company positioning (Novartis pelacarsen, Eli Lilly olpasiran, Arrowhead ARO-LP(a))

**Section 4: Market Opportunity**
- Addressable population by genetic segment (Lp(a) 200M, APOE4 250M, LDLR 10M)
- Pricing benchmarks (PCSK9 inhibitors $5-10k/year, gene therapy $1-2M one-time)
- Penetration assumptions (10-20% of addressable market = $100-200B for Lp(a))

**Section 5: Investment Scenarios**
- **Scenario A**: Acquire Lp(a) Phase 3 asset ($1B) → $20B peak revenue (success case)
- **Scenario B**: Partner on APOE4 genetic testing ($200M) → $10B peak revenue (success case)
- **Scenario C**: Acquire gene therapy Phase 2 asset ($500M) → $5B peak revenue (success case)
- Risk-adjusted NPV for each scenario

---

## Implementation Guide

### Prerequisites
1. Access to WHO CVD mortality data
2. Data Commons population statistics
3. Open Targets genetic association database
4. ClinicalTrials.gov for pipeline mapping

### Execution Steps

**Step 1: Disease Burden Quantification** (30 minutes)
```bash
# Global CVD burden
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/cvd-disease-burden/scripts/get_cvd_disease_burden.py

# Per-capita burden by country
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/cvd-burden-per-capita/scripts/get_cvd_burden_per_capita.py
```

**Step 2: Genetic Target Validation** (30 minutes)
```bash
# CVD genetic targets
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-genetic-targets/scripts/get_disease_genetic_targets.py
```

**Step 3: Clinical Landscape** (45 minutes)
```bash
# CVD trials by sponsor
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-clinical-trials-portfolio/scripts/get_company_clinical_trials_portfolio.py

# Pipeline by CVD subtype
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/indication-pipeline-breakdown/scripts/get_indication_pipeline_breakdown.py

# Precision medicine pipeline
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-pipeline-indications/scripts/get_company_pipeline_indications.py
```

**Step 4: Market Opportunity Sizing** (30 minutes)
- Use cvd-burden-per-capita output to calculate addressable populations
- Model pricing scenarios (PCSK9 benchmark: $5-10k/year, gene therapy: $1-2M one-time)
- Calculate market size by genetic segment (Lp(a), APOE4, LDLR)

**Step 5: Synthesis & Investment Recommendation** (30 minutes)
- Score opportunities (genetic validation, clinical progress, market size, competition)
- Calculate risk-adjusted NPV for Lp(a), APOE4, gene therapy scenarios
- Generate executive summary dashboard

**Total Time**: 2.5-3 hours for comprehensive analysis

---

## Value Proposition

### Quantified Benefits

**Decision Quality**:
- **Without this analysis**: "CVD is big, we should do PCSK9 programs" → invest $1B in saturated market
  - Risk: PCSK9 market saturated (Repatha, Praluent + biosimilars)
  - Risk: Miss Lp(a) opportunity (100x larger addressable market)
- **With this analysis**: Data-driven focus on Lp(a) → invest $1B in $100-200B market
  - Benefit: Avoid $1B in PCSK9 me-too programs
  - Benefit: Capture Lp(a) opportunity before market saturates (Phase 3 readouts 2025-2026)

**Financial Impact**:
- **Market opportunity**: $100-200B (Lp(a)) vs. $5-10B (PCSK9) = 10-20x larger addressable market
- **Peak revenue**: $20B (10% Lp(a) market share) vs. $2B (10% PCSK9 market share) = 10x revenue potential
- **Risk-adjusted NPV**: $5-10B (Lp(a) Phase 3 asset) vs. $1-2B (PCSK9 biosimilar)

**Time Savings**:
- **Manual analysis**: 4-6 weeks (genetic research + epidemiology + trial mapping + market sizing)
- **Automated skills**: 3 hours (95% time reduction)
- **Time-to-decision**: Week 1 vs. Month 2 (critical for Lp(a) M&A timing before Phase 3 readouts)

### Strategic Advantages

1. **Precision medicine validation**: Genetic data proves biology is real (PCSK9 precedent, Lp(a) genetic evidence)
2. **Market opportunity quantification**: $100-200B Lp(a) market vs. $5-10B PCSK9 market = clear investment priority
3. **Competitive positioning**: Lp(a) Phase 3 programs = acquisition window before approvals (2025-2026)
4. **Portfolio optimization**: Balance short-term (APOE4 genetic testing) and long-term (Lp(a) therapy) investments

---

## Next Steps for Implementation

### Immediate Actions
1. **Run pilot analysis**: Execute all 6 skills for CVD precision medicine landscape
2. **Validate genetic data**: Cross-check Open Targets with GWAS Catalog and published literature
3. **Model Lp(a) market scenarios**: Conservative (5% penetration), base (10%), optimistic (20%)
4. **Identify Lp(a) acquisition targets**: Screen Phase 2/3 programs (Novartis pelacarsen, Eli Lilly olpasiran, Arrowhead ARO-LP(a))

### Medium-Term Enhancements
1. **Real-world evidence**: Track PCSK9 inhibitor uptake (is precision medicine being adopted in practice?)
2. **Payer analysis**: Will payers reimburse Lp(a) therapies? (PCSK9 reimbursement struggles in Europe)
3. **Genetic testing infrastructure**: Model costs of population-wide Lp(a) screening (blood test $50-100)
4. **Combination therapy modeling**: Lp(a)-lowering + PCSK9 inhibitor for ultra-high-risk patients

### Long-Term Vision
1. **Real-time monitoring**: Track Phase 3 readouts for Lp(a) programs (2025-2026)
2. **Portfolio optimization**: Model multiple CVD precision medicine bets (Lp(a) + APOE4 + gene therapy)
3. **M&A strategy**: Identify optimal acquisition timing (before Phase 3 readout = lower price, after = lower risk)
4. **Commercial planning**: Build genetic testing infrastructure (partnerships with diagnostic companies)

---

## Risks and Mitigations

### Clinical Risks
- **Risk**: Lp(a) Phase 3 trials fail to show CVD benefit (only LDL-lowering proven so far)
  - **Mitigation**: Genetic evidence is strong (association 0.85), but clinical benefit still needs Phase 3 confirmation
- **Risk**: Gene therapy safety issues (immune response, off-target editing)
  - **Mitigation**: Wait for Phase 2 data before investing (don't bet on Phase 1 programs)

### Commercial Risks
- **Risk**: Genetic testing adoption too slow (physicians don't order Lp(a) tests)
  - **Mitigation**: Bundle genetic testing with therapy (free testing for patients, diagnostic partnerships)
- **Risk**: Payer resistance to high pricing ($5-10k/year for Lp(a) therapy)
  - **Mitigation**: Outcomes-based contracts (pay only if CVD reduced), installment payment plans

### Competitive Risks
- **Risk**: Multiple Lp(a) programs succeed (3 in Phase 3) → market fragmentation
  - **Mitigation**: First-to-market advantage (Novartis pelacarsen leading), differentiation on dosing/safety
- **Risk**: PCSK9 biosimilars erode pricing ($1-2k/year vs. $5-10k for branded)
  - **Mitigation**: Avoid PCSK9 space entirely (focus on Lp(a) where no biosimilars for 10+ years)

---

## Related Scenarios

This scenario pairs well with:
- **Disease Burden Per Capita**: CVD epidemiology informs market sizing for precision therapies
- **Rare Disease M&A**: Familial hypercholesterolemia (LDLR mutations) = orphan drug opportunity
- **Alzheimer's Investment Thesis**: APOE4 is shared genetic risk factor for both CVD and Alzheimer's

---

## Success Metrics

### Analysis Quality
- ✅ All 6 skills execute successfully
- ✅ CVD disease burden quantified (17.9M deaths/year, $1T cost)
- ✅ Genetic targets validated with association scores > 0.8
- ✅ Market opportunity sized by genetic segment (Lp(a) $100-200B, APOE4 $50-100B)

### Decision Impact
- ✅ Investment committee accepts Lp(a) recommendation (vs. PCSK9 me-too programs)
- ✅ M&A offer made to Lp(a) Phase 3 program (Novartis pelacarsen or Eli Lilly olpasiran)
- ✅ APOE4 genetic testing partnership initiated (diagnostic + therapeutic bundle)

### Business Outcomes (5-year horizon)
- ✅ Lp(a) therapy approved with CVD benefit (Phase 3 success)
- ✅ Market share captured (10-20% of $100B Lp(a) market = $10-20B peak revenue)
- ✅ Precision medicine infrastructure built (genetic testing, patient selection, KOL education)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-27
**Next Review**: On first pilot implementation
