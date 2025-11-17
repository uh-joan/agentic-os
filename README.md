# Pharmaceutical Research Intelligence Platform

AI-powered pharmaceutical research system using Claude Code with specialized MCP servers for drug discovery, clinical trials, regulatory data, and competitive intelligence.

## Architecture

Multi-agent system: data gathering + analytical modeling

**Agents:**

*Planning Agents:*
- `pharma-search-specialist`: Query → JSON plan (Claude Code executes MCP) → `data_dump/`
- `search-orchestrator`: Project context → JSON plan with mcp_queries + specialist_delegations + synthesis_plan

*Epidemiological Analysis:*
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `market-sizing-analyst`: Reads `data_dump/` → TAM/SAM/SOM market sizing synthesis

*Forecasting Pipeline:*
- `patient-flow-modeler`: Reads `data_dump/` → eligibility funnels, treatment sequencing, multi-year patient flows
- `uptake-dynamics-analyst`: Reads `temp/` + `data_dump/` → market share evolution, treated patient projections
- `pricing-strategy-analyst`: Reads `data_dump/` → IRP modeling, tiered pricing, launch sequencing
- `revenue-synthesizer`: Reads `temp/` → revenue forecasts, peak sales, NPV-ready streams

*Competitive Intelligence:*
- `competitive-analyst`: Reads `data_dump/` → competitive landscape mapping, pipeline threats
- `opportunity-identifier`: Reads `temp/` → BD opportunities (partnerships, acquisitions, white space)
- `strategy-synthesizer`: Reads `temp/` → strategic planning, action prioritization, scenario analysis

*Asset Valuation:*
- `comparable-analyst`: Reads `data_dump/` → deal benchmarking, licensing precedents, M&A valuation ranges
- `npv-modeler`: Reads `data_dump/` → risk-adjusted NPV, DCF analysis, sensitivity scenarios
- `structure-optimizer`: Reads `temp/` → upfront/milestone/royalty optimization, risk-sharing frameworks

*Target Discovery & Validation:*
- `target-identifier`: Reads `data_dump/` → novel drug target identification from genetics and multi-omics
- `target-validator`: Reads `temp/` + `data_dump/` → CRISPR/RNAi validation study design, genetic safety assessment
- `target-druggability-assessor`: Reads `temp/` + `data_dump/` → protein structure analysis, modality selection, genetic safety prediction
- `target-hypothesis-synthesizer`: Reads `temp/` + `data_dump/` → therapeutic hypotheses, MOA, patient populations, PoC trial designs

*Toxicology & Regulatory:*
- `safety-pharmacology-analyst`: Reads `data_dump/` → hERG/QT assessment, CNS/respiratory safety, ICH S7A/S7B compliance
- `genetic-toxicology-analyst`: Reads `data_dump/` → Ames/micronucleus evaluation, ICH S2(R1) study design, genotoxicity risk
- `toxicology-analyst`: Reads `data_dump/` → NOAEL/safety margins, repeat-dose/reproductive/carcinogenicity study design
- `toxicologist-regulatory-strategist`: Reads `temp/` + `data_dump/` → FIH dose calculation, IND Module 2.4/2.6 assembly, regulatory strategy

*Real-World Evidence:*
- `rwe-study-designer`: Reads `data_dump/` → RWE protocol development, data source selection, feasibility assessment
- `rwe-outcomes-analyst`: Reads `data_dump/` + `temp/` → outcomes algorithm development, treatment pathway mapping, phenotype validation
- `rwe-analytics-strategist`: Reads `data_dump/` + `temp/` → causal inference methods, propensity scoring, sensitivity analysis

*Regulatory Strategy:*
- `regulatory-risk-analyst`: Reads `data_dump/` + `temp/` → CRL probability scoring, AdComm likelihood, label restriction risk, mitigation strategies
- `regulatory-precedent-analyst`: Reads `data_dump/` → historical FDA/EMA precedents, success/failure patterns, endpoint acceptance analysis
- `regulatory-pathway-analyst`: Reads `temp/` + `data_dump/` → optimal regulatory pathway (NDA, 505(b)(2), Accelerated Approval), designation strategies
- `regulatory-label-strategist`: Reads `data_dump/` + `temp/` → label negotiation (indication, contraindications, warnings, REMS), restriction mitigation
- `regulatory-adcomm-strategist`: Reads `data_dump/` + `temp/` → AdComm preparation, voting prediction, panel analysis, presentation strategy

**Workflow:**
- **Ad-hoc queries**: Query → pharma-search-specialist (plans) → Claude Code executes MCP → analytical agents → results
- **Project workflows**: Context files → search-orchestrator (plans) → Claude Code executes → specialist agents → synthesis

## MCP Servers

The platform integrates 12 specialized MCP servers (see `.mcp.json`):

### Core Pharmaceutical Data
- **ct-gov-mcp**: ClinicalTrials.gov trial data
  - Tool: `mcp__ct-gov-mcp__ct_gov_studies`
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
  - Tool: `mcp__fda-mcp__fda_info`
- **pubmed-mcp**: PubMed biomedical literature
  - Tool: `mcp__pubmed-mcp__pubmed_articles`

### Medical Coding & Standards
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO)
  - Tool: `mcp__nlm-codes-mcp__nlm_ct_codes`
- **who-mcp-server**: WHO Global Health Observatory data
  - Tool: `mcp__who-mcp-server__who-health`

### Chemistry & Biology
- **pubchem-mcp-server**: Compound properties, ADME data
  - Tool: `mcp__pubchem-mcp-server__pubchem`
- **opentargets-mcp-server**: Target validation, gene-drug-disease associations
  - Tool: `mcp__opentargets-mcp-server__opentargets_info`

### Financial & Legal
- **sec-mcp-server**: SEC EDGAR financial filings
  - Tool: `mcp__sec-mcp-server__sec-edgar`
- **patents-mcp-server**: USPTO patent search
  - Tool: `mcp__patents-mcp-server__uspto_patents`
- **financials-mcp-server**: Yahoo Finance stock data + FRED economic indicators
  - Tool: `mcp__financials-mcp-server__financial-intelligence`

### Healthcare Systems
- **healthcare-mcp**: CMS Medicare provider data
  - Tool: `mcp__healthcare-mcp__cms_search_providers`
- **datacommons-mcp**: Population statistics, disease demographics
  - Tools: `mcp__datacommons-mcp__search_indicators`, `mcp__datacommons-mcp__get_observations`

## Quick Start

### 1. Query the System

```bash
# Example queries:
"FDA-approved GLP-1 drugs"
"Clinical trials for Alzheimer's disease in Phase 3"
"Adverse events for atorvastatin"
"Competitive landscape for JAK inhibitors"
```

### 2. System Flow

1. **Classify query** (simple, complex, or exploratory)
2. **Invoke specialist agent** using appropriate template
3. **Receive execution plan** (JSON format)
4. **Execute MCP tool calls** sequentially
5. **Save results** to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/`

### 3. Results Structure

Each query creates a timestamped directory in `data_dump/`:

```
data_dump/2025-11-10_183054_fda_baricitinib/
├── query.json         # Original query parameters
├── results.json       # Raw MCP response
├── summary.md         # Human-readable summary
└── metadata.json      # Execution metadata
```

## Query Complexity Classification

### Simple Queries (single database, <5 steps)
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

### Complex Queries (multi-database, >5 steps)
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis

### Exploratory Queries
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research

## Documentation

### Core Documentation
- **`.claude/CLAUDE.md`**: Architecture overview and execution protocols
- **`.claude/agents/pharma-search-specialist.md`**: Agent specification and examples
- **`.mcp.json`**: MCP server configuration

### Tool Guides (`.claude/.context/mcp-tool-guides/`)
- **fda.md**: FDA database queries (drugs, adverse events, recalls)
- **clinicaltrials.md**: ClinicalTrials.gov search patterns
- **pubmed.md**: PubMed literature searches
- **sec-edgar.md**: SEC financial filings
- **datacommons.md**: Population and disease statistics
- **opentargets.md**: Target validation queries
- **pubchem.md**: Chemical compound searches
- **uspto-patents.md**: Patent search strategies

### Strategy Protocols (`.claude/.context/`)
- **performance-optimization.md**: Token efficiency, count-first strategies
- **search-strategy-protocols.md**: 4-phase execution, cognitive directives
- **search-workflows.md**: Proven workflow templates
- **cross-database-integration.md**: Entity linking across sources
- **quality-control.md**: Validation criteria, confidence levels

## Key Features

### Token Optimization
- **Count-first strategy**: Reduces FDA queries from 67K → 400 tokens (99.4% savings)
- **Field selection**: 70-90% token reduction on detail queries
- **Conservative limits**: Max 50-100 records per query
- **Pagination support**: For large datasets

### Data Quality
- **Audit trail**: All queries and results saved
- **Metadata tracking**: Timestamps, parameters, token usage
- **Validation steps**: Quality checks on multi-step workflows
- **Source transparency**: Original MCP responses preserved

### Intelligence Capabilities
- **Multi-database synthesis**: Link entities across FDA, ClinicalTrials.gov, PubMed
- **Competitive analysis**: Pipeline comparison, market positioning
- **Safety monitoring**: Adverse event detection and trending
- **Target validation**: Gene-drug-disease associations

## Example Workflows

### Drug Safety Analysis
1. FDA general search (count-first) → identify products
2. FDA adverse events (aggregated) → safety signals
3. PubMed literature → clinical evidence
4. ClinicalTrials.gov → ongoing trials

### Competitive Landscape
1. ClinicalTrials.gov → pipeline programs by sponsor
2. FDA approvals → marketed products
3. SEC EDGAR → R&D spend, financial health
4. Patents → IP protection timeline

### Target Validation
1. OpenTargets → gene-disease associations
2. PubMed → mechanism literature
3. ClinicalTrials.gov → clinical validation
4. PubChem → tool compounds

### Epidemiological Analysis (using epidemiology-analyst + patient-flow-modeler)
1. Data Commons + WHO + CMS → prevalence data gathering
2. PubMed → severity distribution studies
3. ClinicalTrials.gov → eligibility criteria patterns
4. FDA + CMS → contraindication prevalence
5. Epidemiology-analyst → prevalence model with demographics
6. Patient-flow-modeler → eligibility funnel + multi-year patient flows
7. Output: Treatment-eligible population with 5-10 year projections and sensitivity analysis

### Competitive Landscape Analysis (using competitive intelligence agents)
1. FDA + ClinicalTrials.gov + SEC + PubMed + OpenTargets → competitive data gathering
2. competitive-analyst → competitive landscape with pipeline threats
3. opportunity-identifier → BD opportunities (partnerships, acquisitions, white space)
4. strategy-synthesizer → strategic plan with positioning and action roadmap
5. Output: Actionable strategic recommendations with scenario planning and decision triggers

## Agents

### Data Gathering

#### pharma-search-specialist
Data gathering coordinator. Input: query → Output: JSON execution plan with MCP tool calls

### Epidemiological Analysis

#### epidemiology-analyst
Prevalence modeling and market sizing. Input: `data_dump/` → Output: Models, segmentation, eligibility funnels

**Capabilities**: Age-standardization, severity segmentation, biomarker stratification, eligibility funnels, sensitivity analysis, CMS real-world evidence integration

#### market-sizing-analyst
TAM/SAM/SOM market sizing synthesis. Input: `data_dump/` → Output: Complete market sizing analysis with executive summary, funnel breakdowns, competitive landscape, timeline projections

**Capabilities**: TAM (total prevalence from Data Commons/WHO/PubMed), SAM (eligibility funnels from CMS/FDA/CT.gov), SOM (competitive analysis from SEC/financials), cross-validation, sensitivity analysis, revenue projections. Covers all 12 MCP servers with no data gaps.

### Forecasting Pipeline

Sequential agents for pharmaceutical forecasting (patient flows → uptake → pricing → revenue):

#### patient-flow-modeler
Treatment-eligible population projections and sequencing. Input: `data_dump/` → Output: Eligibility funnels, multi-year patient flows, sensitivity analysis

**Capabilities**: Eligibility funnel construction (diagnosed → severity-eligible → label-eligible → drug-eligible), treatment line distribution (1L/2L/3L), annual progression modeling, multi-year patient flow projections (5-10 years), scenario analysis (conservative/base/optimistic), tornado sensitivity analysis, treatment sequencing pathways

#### uptake-dynamics-analyst
Market share evolution and adoption dynamics. Input: `temp/patient_flow_*.md` + `data_dump/` → Output: Year-by-year market share evolution, treated patient projections, sensitivity analysis

**Capabilities**: Bass diffusion modeling, S-curve adoption, competitive displacement attribution, launch sequencing impact, treated patient counts (eligible pool × market share), 5-year projections with low/base/high scenarios

#### pricing-strategy-analyst
Global pricing optimization and launch sequencing. Input: `data_dump/` → Output: IRP modeling, tiered pricing strategy, launch sequencing timeline, revenue impact comparison

**Capabilities**: IRP spillover risk modeling, 4-tier pricing framework (premium/competitive/value/access), phased launch sequencing (IRP-free first, IRP-sensitive delayed), cumulative 5-year revenue optimization, sensitivity analysis (±20% price variation)

#### revenue-synthesizer
Pharmaceutical revenue forecasting synthesis. Input: `temp/patient_flow_*.md` + `temp/uptake_dynamics_*.md` + optional `temp/pricing_strategy_*.md` → Output: Multi-year revenue forecast, peak sales, NPV-ready streams

**Capabilities**: Revenue formula (Treated Patients × Annual Cost × Compliance × Net Price %), 5-10 year projections, low/base/high scenarios, tornado sensitivity analysis, risk-adjusted peak sales, geographic breakdown (US/EU5/Japan/RoW), cumulative revenue metrics

### Competitive Intelligence

#### competitive-analyst
Competitive landscape mapping and pipeline threat assessment. Input: `data_dump/` → Output: Competitive analysis with market structure, pipeline threats, differentiation matrix, genetic biomarker intelligence

**Capabilities**: Current market structure (leaders, moats, vulnerabilities), pipeline dynamics (Phase 2/3 segmentation, threat scoring 🔴🟡🟢), differentiation matrix (MOA, efficacy, safety, dosing), genetic biomarker competitive positioning, gaps analysis (white space, crowded segments)

#### opportunity-identifier
BD opportunity screening for partnerships, acquisitions, and white space. Input: `temp/competitive_analysis_*.md` → Output: Prioritized BD opportunities with deal economics and timing triggers

**Capabilities**: Partnership screening (<$1B biotech, Phase 1/2, weak commercialization), acquisition screening (<$500M, Phase 2+, undervaluation signals), white space identification (patient populations, geographic gaps, indication expansion), priority tiering (🔴 0-6mo, 🟡 6-12mo, 🟢 12-24mo), deal economics framework

#### strategy-synthesizer
Strategic planning synthesis from competitive intelligence and BD opportunities. Input: `temp/competitive_analysis_*.md` + `temp/bd_opportunities_*.md` → Output: Strategic plan with positioning, action roadmap, scenario planning

**Capabilities**: Strategic positioning frameworks (offensive/defensive/flanking/guerrilla), action prioritization (immediate/near/medium-term horizons), scenario planning (best/base/worst case), decision triggers (go/no-go criteria), risk mitigation strategies (competitive/regulatory/commercial/execution), success metrics and KPIs

### Asset Valuation

Sequential agents for pharmaceutical asset valuation (comparables → NPV → deal structure):

#### comparable-analyst
Deal benchmarking and licensing precedent analysis. Input: `data_dump/` → Output: Comparable deal analysis with valuation ranges

**Capabilities**: Three-dimensional matching (indication × stage × structure), stage-appropriate valuation multiples (Phase 1-3, approved), upfront/peak sales benchmarks, total deal/peak sales ratios, milestone structure patterns, royalty rate analysis, 25th/50th/75th percentile ranges

#### npv-modeler
Risk-adjusted NPV modeling and DCF analysis. Input: `data_dump/` → Output: NPV analysis with sensitivity scenarios

**Capabilities**: Probability of success (PoS) frameworks by therapeutic area, program-specific adjustments (FDA Breakthrough, orphan drug, novel mechanism), probability-weighted revenue forecasts with patent exclusivity, risk-adjusted development costs, operating cash flow modeling (COGS, SG&A, R&D, tax), phase-appropriate discount rates (10-15%), tornado sensitivity analysis, bull/base/bear scenarios

#### structure-optimizer
Deal structure optimization for licensing transactions. Input: `temp/npv_analysis_*.md` + `temp/deal_comparables_*.md` → Output: Upfront/milestone/royalty allocation recommendations

**Capabilities**: NPV-equivalent structure design (seller-favorable/balanced/buyer-favorable), discount rate sensitivity (buyer vs seller WACC), risk allocation analysis (development/regulatory/commercial/timing), milestone allocation (40-50% development, 50-60% commercial), tiered royalty structures (8-20% by sales tier), comparables benchmarking, win-win value creation, dependency validation

### Target Discovery & Validation

Sequential agents for pharmaceutical target discovery and validation (identification → validation → druggability → hypothesis):

#### target-identifier
Novel drug target identification from genetics and multi-omics. Input: `data_dump/` → Output: Prioritized target list with genetic evidence scores and clinical precedents

**Capabilities**: GWAS mining (lead variants, fine-mapping, functional annotation), multi-omics integration (transcriptomics, proteomics, metabolomics, causal inference), OpenTargets genetic evidence scoring (preferred), clinical precedent identification, novel opportunity flagging (strong genetics + no known drugs), multi-criteria target ranking (genetic 40%, precedent 25%, expression 20%, pathway 15%)

#### target-validator
CRISPR/RNAi validation study design and genetic safety assessment. Input: `temp/target_identification_*.md` + `data_dump/` → Output: Validation plan with genetic safety assessment and go/no-go criteria

**Capabilities**: Genetic evidence-based triage (>0.7: STREAMLINED validation with 30-50% timeline reduction; 0.5-0.7: standard 4-phase; <0.5: extended), four-phase validation framework (CRISPR knockout, RNAi validation, patient-derived models, in vivo models), human knockout phenotype safety prediction (GREEN/YELLOW/RED flags), rescue experiment design (pharmacological + genetic), statistical power analysis, go/no-go decision criteria

#### target-druggability-assessor
Protein structure analysis, modality selection, and genetic safety prediction. Input: `temp/target_validation_*.md` + `data_dump/` → Output: Druggability assessment with modality recommendations and safety flags

**Capabilities**: Protein structure analysis (crystal structures, druggable pockets, ligandability scoring), small molecule tractability (target class precedents, Lipinski Rule of Five, oral bioavailability), biologic modality assessment (antibody accessibility, ADC feasibility, bispecific opportunities, gene therapy suitability), genetic safety prediction (LOF phenotype analysis, clinical precedent validation, on-target toxicity prediction using OpenTargets), modality selection framework (decision tree comparing small molecule/antibody/PROTAC/gene therapy), tissue expression profiling, selectivity assessment (homology, off-target prediction)

#### target-hypothesis-synthesizer
Therapeutic hypothesis development with MOA, patient populations, and PoC trial designs. Input: `temp/target_identification_*.md` + `temp/target_validation_*.md` + `temp/target_druggability_*.md` + `data_dump/` → Output: Comprehensive therapeutic hypothesis

**Capabilities**: MOA development (pharmacodynamic cascade: target engagement → pathway modulation → phenotypic reversal → clinical benefit), patient population definition (genetic stratification, disease subtyping, addressable market sizing), multi-tier biomarker strategy (selection, engagement, PD, efficacy, safety with companion diagnostic plan), clinical PoC design (Phase 1b/2a trial with go/no-go criteria, adaptive enrollment, realistic timelines), competitive differentiation (first-in-class vs best-in-class positioning), development timeline & risk mitigation

### Toxicology & Regulatory

Sequential agents for pharmaceutical toxicology assessment and IND preparation (safety pharmacology → genetic toxicology → general toxicology → regulatory assembly):

#### safety-pharmacology-analyst
Cardiovascular, CNS, and respiratory safety assessment. Input: `data_dump/` → Output: hERG/QT assessment, TQT strategy, ICH S7A/S7B safety pharmacology package

**Capabilities**: hERG patch clamp IC50 evaluation with safety margin calculations (total and free drug), cardiovascular risk categorization (low/moderate/high based on >30×/10-30×/<10× margins), dog telemetry study design (GLP-compliant, QTc/HR/BP monitoring), thorough QT study decision logic per ICH S7B/E14, CNS receptor binding panels (GABA-A, NMDA, opioid, 5-HT2A, D2), brain penetration prediction (LogP/TPSA/P-gp status), neurobehavioral study design (Irwin screen, EEG), respiratory safety assessment (plethysmography, opioid receptor risk, ABG), approved drug benchmarking (erlotinib, gefitinib, moxifloxacin precedents), Phase 1 clinical monitoring protocols (ECG, sedation, SpO2)

#### genetic-toxicology-analyst
DNA damage and mutagenicity assessment. Input: `data_dump/` → Output: Ames predictions, ICH S2(R1) study battery, genotoxicity risk assessment

**Capabilities**: Structural alert screening (aromatic amines, nitro compounds, epoxides, quinones, PAHs), QSAR model integration (MultiCase MC4PC, Derek Nexus, ToxTree), Ames test design (5 bacterial strains, ±S9, GLP-compliant), in vitro mammalian cell micronucleus assay (CHO/TK6/L5178Y, ±S9), in vivo rat micronucleus decision logic per ICH S2(R1), metabolite genotoxicity assessment (CYP1A2/3A4 activation pathways), ICH M7 impurity genotoxicity classification (Class 1-5 with TTC limits), equivocal result resolution strategies, approved drug genotox precedents, regulatory strategy for positive findings (ICH S9 oncology exemption, risk-benefit analysis)

#### toxicology-analyst
Repeat-dose toxicology and NOAEL determination. Input: `data_dump/` → Output: NOAEL predictions, safety margins, ICH-compliant toxicology study designs

**Capabilities**: NOAEL determination from approved drug analogs, dose-based safety margin calculations (target ≥10×), AUC-based safety margin calculations (target ≥25×), target organ prediction from structural alerts (hepatotoxicity, nephrotoxicity, cardiotoxicity), GLP study design (28-day, 90-day, 6-month repeat-dose in rat/dog/monkey), reproductive toxicity assessment per ICH S5(R3) (Segment I/II/III study battery, abbreviated vs full justification), carcinogenicity evaluation per ICH S1 (2-year rat bioassay, 6-month Tg-rasH2 mouse alternative), acute toxicity and GHS classification (LD50 prediction, oral/dermal/inhalation routes), species sensitivity ranking for FIH calculations, ICH M3(R2) study timing (Phase 1, 2, 3, NDA gates)

#### toxicologist-regulatory-strategist
IND toxicology package assembly and FIH dose calculation. Input: `temp/safety_pharmacology_*.md` + `temp/genetic_toxicology_*.md` + `temp/toxicology_*.md` + `data_dump/` → Output: IND Module 2.4/2.6 package with FIH dose justification

**Capabilities**: First-in-human (FIH) dose calculation via allometric scaling (FDA 2005 guidance: HED = Animal NOAEL × (Animal Wt/Human Wt)^0.33), safety factor application (standard 10×, elevated >10× for genetic safety concerns, reduced 6× for oncology), species selection for FIH (most sensitive species by AUC comparison), modified Fibonacci dose escalation design (100%/67%/50%/40%/33% increments with DLT criteria), IND Module 2.4 nonclinical overview assembly (pharmacology, PK, toxicology, integrated safety summary), IND Module 2.6 toxicology tables (repeat-dose, genetic toxicology, safety pharmacology summaries), cardiovascular safety strategy per ICH S7B/E14 (hERG margin assessment, dog telemetry integration, TQT study timing), OpenTargets genetic safety integration (essential gene assessment, HLA hypersensitivity screening, CYP pharmacogenetics), clinical hold risk assessment (low/moderate/high with mitigation strategies), FDA Pre-IND meeting preparation (discussion topics, briefing documents), nonclinical study timeline and budget planning (Phase 1 through NDA gates)

### Real-World Evidence

Sequential agents for real-world evidence study design, outcomes analysis, and statistical methodology (study design → outcomes → analytics):

#### rwe-study-designer
Real-world evidence study protocol design and feasibility assessment. Input: `data_dump/` → Output: RWE study design with patient algorithms, data source evaluation, and feasibility analysis

**Capabilities**: Observational study design (retrospective/prospective cohorts, case-control, cross-sectional), pragmatic trial framework (PRECIS-2), synthetic control arms (propensity score matching, concurrent/historical controls), data source strategy (claims databases, EHR platforms, disease registries, linked datasets), patient identification algorithm development (ICD-10/11 codes, treatment codes, inclusion/exclusion logic, washout periods), feasibility assessment (population estimation, data completeness, event accrual, follow-up duration), bias mitigation strategies (selection, confounding, information, time-related biases), FDA RWE framework compliance

#### rwe-outcomes-analyst
Treatment pattern analysis and clinical outcomes algorithm development. Input: `temp/rwe_study_design_*.md` + `data_dump/` → Output: Validated outcomes algorithms with treatment pathway mapping

**Capabilities**: Treatment pattern analysis (line-of-therapy algorithms, treatment switching, discontinuation patterns, persistence metrics MPR/PDC, re-treatment, concomitant medications), outcomes algorithm development (hospitalization codes, progression proxies, mortality ascertainment, adverse event identification, healthcare utilization), phenotype validation (PPV assessment, sensitivity/specificity evaluation, external validation), patient journey mapping (diagnosis-to-treatment intervals, treatment-to-outcome timelines, healthcare touchpoints, geographic variation), algorithm misclassification impact assessment

#### rwe-analytics-strategist
Statistical analysis strategy development for causal inference from real-world data. Input: `temp/rwe_study_design_*.md` + `data_dump/` → Output: Statistical analysis plan with propensity methods and sensitivity analyses

**Capabilities**: Propensity score methods (1:1 matching, IPTW with ATE/ATT/overlap weights, stratification, covariate balance diagnostics, common support assessment), advanced causal inference (instrumental variable analysis, difference-in-differences, regression discontinuity, synthetic control, marginal structural models), effect estimation (risk difference/NNT, risk ratio, hazard ratio, odds ratio, RMST), sensitivity analysis framework (E-value calculation, quantitative bias analysis, negative control outcomes, falsification tests), missing data strategies (multiple imputation MICE, inverse probability weighting, pattern mixture models), sample size and power assessment, doubly robust estimation, STROBE compliance

### Regulatory Strategy

Sequential agents for pharmaceutical regulatory strategy and FDA approval optimization (precedent analysis → pathway selection → risk assessment → label strategy → AdComm preparation):

#### regulatory-precedent-analyst
Historical FDA/EMA approval precedent analysis. Input: `data_dump/` → Output: Precedent analysis with comparable approvals and regulatory decision trends

**Capabilities**: Comparable program identification (3-dimensional matching: indication × endpoint × pathway), success/failure pattern analysis, endpoint acceptance precedents (surrogate vs clinical, accelerated approval pathways), regulatory decision trend analysis (approval rates by pathway, timeline benchmarks), precedent-based argumentation frameworks

#### regulatory-pathway-analyst
Optimal regulatory pathway selection and designation strategies. Input: `temp/regulatory_precedent_*.md` + `data_dump/` → Output: Pathway recommendation with designation strategy

**Capabilities**: Pathway qualification (Standard NDA, 505(b)(2), Accelerated Approval, Breakthrough Therapy, Fast Track, Priority Review, Orphan Drug), designation strategy optimization (application timing, documentation requirements, FDA meeting recommendations), submission timing optimization, precedent-based pathway justification

#### regulatory-risk-analyst
CRL probability scoring and approval risk assessment. Input: `temp/regulatory_precedent_*.md` + `data_dump/` → Output: CRL probability score with risk mitigation strategies

**Capabilities**: Quantitative CRL probability scoring (0-100% with confidence intervals), AdComm likelihood prediction (convening triggers, probability assessment), label restriction risk assessment (biomarker restrictions, line-of-therapy limitations, REMS requirements), deficiency prediction (CMC, nonclinical, clinical), risk mitigation strategy recommendations, contingency planning frameworks

#### regulatory-label-strategist
FDA label negotiation and restriction mitigation. Input: `temp/regulatory_precedent_*.md` + `data_dump/` → Output: Label strategy with indication wording and REMS mitigation

**Capabilities**: Indication statement optimization (line-of-therapy language, biomarker restriction negotiation, precedent-based argumentation), contraindication and warning language strategy (boxed warning mitigation, Section 5 Warnings optimization), REMS mitigation strategies (ETASU resistance, Medication Guide acceptance), dose modification guideline design, label negotiation tactics with precedent citations

#### regulatory-adcomm-strategist
FDA Advisory Committee preparation and voting prediction. Input: `temp/regulatory_precedent_*.md` + `data_dump/` → Output: AdComm strategy with voting prediction and presentation plan

**Capabilities**: AdComm convening likelihood prediction (risk-based triggers, precedent patterns, 0-100% probability), panel composition analysis (member expertise, voting history, affiliation assessment), voting outcome forecasting (member-level predictions, aggregate forecasts with confidence intervals), presentation strategy design (briefing document structure, slide deck, key messaging, Q&A preparation), stakeholder preparation planning (FDA coordination, medical expert selection, patient advocate engagement)

## Design Principles

1. **Multi-agent**: Planning agents (pharma-search-specialist for ad-hoc, search-orchestrator for projects) + analytical agents (epidemiology-analyst, patient-flow-modeler, uptake-dynamics-analyst, pricing-strategy-analyst, revenue-synthesizer, market-sizing-analyst, competitive-analyst, opportunity-identifier, strategy-synthesizer, comparable-analyst, npv-modeler, structure-optimizer, target-identifier, target-validator, target-druggability-assessor, target-hypothesis-synthesizer, safety-pharmacology-analyst, genetic-toxicology-analyst, toxicology-analyst, toxicologist-regulatory-strategist, rwe-study-designer, rwe-outcomes-analyst, rwe-analytics-strategist, regulatory-risk-analyst, regulatory-precedent-analyst, regulatory-pathway-analyst, regulatory-label-strategist, regulatory-adcomm-strategist)
2. **Separation**: Planning vs execution vs analysis - agents plan, Claude Code executes MCP queries, analysts process results
3. **Token optimization**: Conservative limits, pagination, count-first
4. **Audit trail**: All results → data_dump/, analytical outputs → temp/
5. **Modular**: Easy to add MCP servers and agents

## Contributing

**New MCP Servers:**
1. Add to `.mcp.json`
2. Create tool guide in `.claude/.context/mcp-tool-guides/`
3. Update `.claude/CLAUDE.md`, `README.md`, `.claude/settings.local.json`

**New Agents:**
1. Create in `.claude/agents/` (follow `epidemiology-analyst.md` structure)
2. Use frontmatter, enumerated capability domains, response methodology, example output
3. Update `.claude/CLAUDE.md` and `README.md`
