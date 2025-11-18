# Pharmaceutical Research Intelligence

## Architecture

**Multi-agent pattern**: Data gathering + analytical agents

**Agents**:
- `pharma-search-specialist`: Query → JSON plan (Claude Code executes MCP queries) → `data_dump/`
- `search-orchestrator`: Project context → JSON plan with mcp_queries + specialist_delegations + synthesis_plan (used by `/create-plan`)
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `patient-flow-modeler`: Reads `data_dump/` → eligibility funnels, treatment sequencing, multi-year patient flows
- `uptake-dynamics-analyst`: Reads `temp/` + `data_dump/` → market share evolution, treated patient projections
- `pricing-strategy-analyst`: Reads `data_dump/` → IRP modeling, tiered pricing, launch sequencing
- `revenue-synthesizer`: Reads `temp/` → revenue forecasts, peak sales, NPV-ready streams
- `market-sizing-analyst`: Reads `data_dump/` → TAM/SAM/SOM market sizing synthesis
- `competitive-analyst`: Reads `data_dump/` → competitive landscape mapping, pipeline threats
- `opportunity-identifier`: Reads `temp/` → BD opportunities (partnerships, acquisitions, white space)
- `strategy-synthesizer`: Reads `temp/` → strategic planning, action prioritization, scenario analysis
- `comparable-analyst`: Reads `data_dump/` → deal benchmarking, licensing precedents, M&A valuation ranges
- `npv-modeler`: Reads `data_dump/` → risk-adjusted NPV, DCF analysis, sensitivity scenarios
- `structure-optimizer`: Reads `temp/` → upfront/milestone/royalty optimization, risk-sharing frameworks
- `target-identifier`: Reads `data_dump/` → novel drug target identification from genetics and multi-omics
- `target-validator`: Reads `temp/` + `data_dump/` → CRISPR/RNAi validation study design, genetic safety assessment
- `target-druggability-assessor`: Reads `temp/` + `data_dump/` → protein structure analysis, modality selection, genetic safety prediction
- `target-hypothesis-synthesizer`: Reads `temp/` + `data_dump/` → therapeutic hypotheses, MOA, patient populations, PoC trial designs
- `safety-pharmacology-analyst`: Reads `data_dump/` → hERG/QT assessment, CNS/respiratory safety, ICH S7A/S7B compliance
- `genetic-toxicology-analyst`: Reads `data_dump/` → Ames/micronucleus evaluation, ICH S2(R1) study design, genotoxicity risk
- `toxicology-analyst`: Reads `data_dump/` → NOAEL/safety margins, repeat-dose/reproductive/carcinogenicity study design
- `toxicologist-regulatory-strategist`: Reads `temp/` + `data_dump/` → FIH dose calculation, IND Module 2.4/2.6 assembly, regulatory strategy
- `rwe-study-designer`: Reads `data_dump/` → RWE protocol development, data source selection, feasibility assessment
- `rwe-outcomes-analyst`: Reads `data_dump/` + `temp/` → outcomes algorithm development, treatment pathway mapping, phenotype validation
- `rwe-analytics-strategist`: Reads `data_dump/` + `temp/` → causal inference methods, propensity scoring, sensitivity analysis
- `regulatory-risk-analyst`: Reads `data_dump/` + `temp/` → CRL probability scoring, AdComm likelihood, label restriction risk, mitigation strategies
- `regulatory-precedent-analyst`: Reads `data_dump/` → historical FDA/EMA precedents, success/failure patterns, endpoint acceptance analysis
- `regulatory-pathway-analyst`: Reads `temp/` + `data_dump/` → optimal regulatory pathway (NDA, 505(b)(2), Accelerated Approval), designation strategies
- `regulatory-label-strategist`: Reads `data_dump/` + `temp/` → label negotiation (indication, contraindications, warnings, REMS), restriction mitigation
- `regulatory-adcomm-strategist`: Reads `data_dump/` + `temp/` → AdComm preparation, voting prediction, panel analysis, presentation strategy

## MCP Servers (see .mcp.json)

- **ct-gov-mcp**: ClinicalTrials.gov trial data
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO, medical coding)
- **pubmed-mcp**: PubMed biomedical literature
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
- **who-mcp-server**: WHO Global Health Observatory data
- **sec-mcp-server**: SEC EDGAR financial filings
- **healthcare-mcp**: CMS Medicare provider data
- **financials-mcp-server**: Yahoo Finance, FRED economic data
- **datacommons-mcp**: Population/disease stats
- **patents-mcp-server**: USPTO patent search
- **opentargets-mcp-server**: Target validation, genetics
- **pubchem-mcp-server**: Compound properties, ADME

**Tool specs**: `.claude/.context/mcp-tool-guides/` (clinicaltrials.md, fda.md, pubmed.md, etc.)

## pharma-search-specialist

**Role**: Query analysis → JSON execution plan (no execution)
**Input**: User query
**Output**: JSON with execution_plan array (step, tool, method, params, token_budget)
**Tools**: Read only (reads `.claude/.context/mcp-tool-guides/`)
**Use for**: Ad-hoc queries, simple data gathering

See `.claude/agents/pharma-search-specialist.md` for plan format and examples.

## search-orchestrator

**Role**: Multi-phase project planning → JSON plan with MCP queries + specialist delegations + synthesis
**Input**: Project context files (project-brief.md, user-profile.md, PROJECT_WORKFLOW.md, .claude/project-context.md)
**Output**: JSON with mcp_queries (data gathering), specialist_delegations (analysis), synthesis_plan (compilation)
**Tools**: Read only
**Use for**: Task Master workflows, complex analytical pipelines, multi-phase projects
**Invoked by**: `/create-plan` command

See `.claude/agents/search-orchestrator.md` for plan format and examples.

## FDA Query Validation (AUTOMATIC)

**All FDA MCP queries are automatically validated and optimized** by `scripts/utils/fda_query_validator.py`.

### Why This Matters
- Without count parameter: 67,000 tokens → **EXCEEDS 25k MCP LIMIT** → **QUERY FAILS**
- With count parameter: 400 tokens → Query succeeds (99.4% reduction)

### Auto-Validation Rules
1. **Count parameter auto-added** if missing for general/adverse_events queries
2. **.exact suffix auto-added** if missing from count parameter
3. **Field selection recommended** for large detail queries
4. **Validation report** shows fixes applied and token savings

### Default Count Parameters
- `search_type: "general"` → `"count": "openfda.brand_name.exact"`
- `search_type: "adverse_events"` → `"count": "patient.reaction.reactionmeddrapt.exact"`
- `search_type: "recalls"` → Count optional (small dataset)
- `search_type: "shortages"` → Count optional (small dataset)

**See:** `scripts/utils/README.md` for validator documentation and examples.

## Execution Protocol

### 1. Determine Workflow Type

**Use `search-orchestrator` for**:
- Multi-phase projects requiring Task Master workflows
- Complex analytical pipelines (data gathering → analysis → synthesis)
- Projects with context files (project-brief.md, user-profile.md, PROJECT_WORKFLOW.md)
- When using `/create-plan` command
- Workflows requiring multiple specialist agents in sequence

**Use `pharma-search-specialist` for**:
- Ad-hoc queries
- Simple data gathering (single or few MCP queries)
- Direct user questions without project context
- Quick lookups and explorations

### 2. If Using search-orchestrator

Template for `/create-plan` command:
```
"You are search-orchestrator. Read .claude/agents/search-orchestrator.md.

Analyze project context files and create comprehensive workflow plan with:
1. mcp_queries: Data gathering tasks (direct MCP tool calls)
2. specialist_delegations: Analysis tasks (specify which agents)
3. synthesis_plan: Final compilation and report generation

Return ONLY JSON plan."
```

See `/create-plan` command documentation for full workflow integration.

### 3. If Using pharma-search-specialist

#### 3a. Classify Query Complexity

**Simple** (single database, <5 steps):
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

**Complex** (multi-database, >5 steps):
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis
- Keywords: "competitive", "landscape", "compare", "analyze market", "identify leaders"

**Uncertain/Exploratory**:
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research
- Keywords: "explore", "discover", "what are all", "map the space"

#### 3b. Invoke Specialist

Use the template matching the complexity classification from Step 1.

**For simple queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read relevant tool guide from .claude/.context/mcp-tool-guides/ (e.g., fda.md, clinicaltrials.md).
Read performance-optimization.md and apply count-first + field selection.
Return ONLY JSON execution plan."
```

**For complex queries** (multi-database, competitive analysis, workflows):
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read search-strategy-protocols.md (4-phase execution).
Read search-workflows.md (find similar workflow template).
Read performance-optimization.md (token efficiency - MANDATORY count-first for FDA).
Read cross-database-integration.md (if linking entities).
Read relevant tool guides (fda.md for FDA queries, clinicaltrials.md for CT.gov, pubmed.md for PubMed).
Return ONLY JSON execution plan."
```

**For uncertain/exploratory queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Apply 'ultrathink' mode from search-strategy-protocols.md.
Read search-workflows.md for inspiration.
Read quality-control.md for validation criteria.
Read performance-optimization.md (MANDATORY count-first for FDA).
Read relevant tool guides (fda.md, clinicaltrials.md, pubmed.md, etc.).
Design custom workflow. Return ONLY JSON execution plan."
```

#### 3c. Execute Plan
Parse JSON → execute each step → save to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/` → present findings

**After execution**: Save raw MCP results to data_dump/, then optionally invoke analytical agents.

### 4. Invoke Analytical Agents (If Needed)

**epidemiology-analyst** - Prevalence modeling, segmentation, eligibility funnels

Use for: Market sizing, drug-eligible population estimates, patient segmentation

Template:
```
"You are epidemiology-analyst. Read .claude/agents/epidemiology-analyst.md.
Analyze data_dump/[folder]/ and return prevalence model, segmentation, eligibility funnel."
```

**patient-flow-modeler** - Treatment-eligible population projections and sequencing

Use for: Eligibility funnels, treatment line distribution, multi-year patient flows, sensitivity analysis

Template:
```
"You are patient-flow-modeler. Read .claude/agents/patient-flow-modeler.md.
Analyze data_dump/[folder]/ and return eligibility funnel with multi-year patient flow projections."
```

**uptake-dynamics-analyst** - Market share evolution and adoption dynamics

Use for: Uptake modeling, competitive displacement, treated patient projections

Template:
```
"You are uptake-dynamics-analyst. Read .claude/agents/uptake-dynamics-analyst.md.
Read temp/patient_flow_*.md and data_dump/[competitive folder]/ and return market share evolution with treated patient projections."
```

**pricing-strategy-analyst** - Global pricing optimization and launch sequencing

Use for: IRP modeling, tiered pricing, launch sequence optimization

Template:
```
"You are pricing-strategy-analyst. Read .claude/agents/pricing-strategy-analyst.md.
Analyze data_dump/[pricing folder]/ and return IRP modeling with tiered pricing strategy and launch sequencing."
```

**revenue-synthesizer** - Pharmaceutical revenue forecasting synthesis

Use for: Revenue projections, peak sales, NPV-ready streams

Template:
```
"You are revenue-synthesizer. Read .claude/agents/revenue-synthesizer.md.
Read temp/patient_flow_*.md, temp/uptake_dynamics_*.md, and optionally temp/pricing_strategy_*.md. Return multi-year revenue forecast with sensitivity analysis."
```

**market-sizing-analyst** - TAM/SAM/SOM market sizing synthesis

Use for: Market sizing, addressable market analysis, revenue potential assessment

Template:
```
"You are market-sizing-analyst. Read .claude/agents/market-sizing-analyst.md.
Analyze data_dump/ and synthesize TAM/SAM/SOM market sizing with competitive landscape."
```

**competitive-analyst** - Competitive landscape mapping and pipeline threat assessment

Use for: Market leader analysis, pipeline dynamics, competitive positioning, threat scoring

Template:
```
"You are competitive-analyst. Read .claude/agents/competitive-analyst.md.
Analyze data_dump/[folder]/ and return competitive landscape analysis with threat assessment."
```

**opportunity-identifier** - BD opportunity screening

Use for: Partnership targets, acquisition candidates, white space identification

Template:
```
"You are opportunity-identifier. Read .claude/agents/opportunity-identifier.md.
Read temp/competitive_analysis_*.md and return BD opportunity screening."
```

**strategy-synthesizer** - Strategic planning synthesis

Use for: Market positioning strategy, action prioritization, scenario planning, risk mitigation

Template:
```
"You are strategy-synthesizer. Read .claude/agents/strategy-synthesizer.md.
Read temp/competitive_analysis_*.md and temp/bd_opportunities_*.md and return strategic plan."
```

**comparable-analyst** - Deal benchmarking and licensing precedent analysis

Use for: M&A valuation ranges, licensing deal multiples, upfront/milestone/royalty benchmarks

Template:
```
"You are comparable-analyst. Read .claude/agents/comparable-analyst.md.
Analyze data_dump/[folder]/ and return comparable deal analysis with valuation ranges."
```

**npv-modeler** - Risk-adjusted NPV modeling and DCF analysis

Use for: Probability-weighted revenue forecasts, development cost modeling, sensitivity analysis

Template:
```
"You are npv-modeler. Read .claude/agents/npv-modeler.md.
Analyze data_dump/[folder]/ and return NPV analysis with sensitivity scenarios."
```

**structure-optimizer** - Deal structure optimization

Use for: Upfront/milestone/royalty allocation, risk-sharing frameworks, NPV-equivalent structure design

Template:
```
"You are structure-optimizer. Read .claude/agents/structure-optimizer.md.
Read temp/npv_analysis_*.md and temp/deal_comparables_*.md and return deal structure recommendations."
```

**target-identifier** - Novel drug target identification from genetics and multi-omics

Use for: Target prioritization, genetic evidence scoring, multi-omics integration, novel opportunity flagging

Template:
```
"You are target-identifier. Read .claude/agents/target-identifier.md.
Analyze data_dump/[folder]/ and return prioritized target list with genetic evidence and delegation recommendations."
```

**target-validator** - CRISPR/RNAi validation study design and genetic safety assessment

Use for: Validation experiment design, genetic evidence-based triage, human knockout phenotype safety prediction, go/no-go criteria

Template:
```
"You are target-validator. Read .claude/agents/target-validator.md.
Read temp/target_identification_*.md and data_dump/[folder]/ and return validation plan with genetic safety assessment."
```

**target-druggability-assessor** - Protein structure analysis, modality selection, genetic safety prediction

Use for: Druggability scoring, small molecule vs. biologic tractability, on-target toxicity prediction, modality recommendation

Template:
```
"You are target-druggability-assessor. Read .claude/agents/target-druggability-assessor.md.
Read temp/target_validation_*.md and data_dump/[folder]/ and return druggability assessment with modality recommendations."
```

**target-hypothesis-synthesizer** - Therapeutic hypothesis development with MOA, patient populations, PoC trial designs

Use for: MOA development, patient population definition, biomarker strategy, clinical PoC design, competitive differentiation

Template:
```
"You are target-hypothesis-synthesizer. Read .claude/agents/target-hypothesis-synthesizer.md.
Read temp/target_identification_*.md, temp/target_validation_*.md, temp/target_druggability_*.md, and data_dump/[folder]/ and return therapeutic hypothesis."
```

**safety-pharmacology-analyst** - Cardiovascular, CNS, and respiratory safety assessment

Use for: hERG liability evaluation, thorough QT strategy, ICH S7A/S7B compliance, TQT study recommendations

Template:
```
"You are safety-pharmacology-analyst. Read .claude/agents/safety-pharmacology-analyst.md.
Analyze data_dump/[folder]/ and return hERG assessment, TQT strategy, and ICH S7A/S7B safety pharmacology package."
```

**genetic-toxicology-analyst** - DNA damage and mutagenicity assessment

Use for: ICH S2(R1) genotoxicity evaluation, Ames test design, micronucleus study recommendations, ICH M7 impurity control

Template:
```
"You are genetic-toxicology-analyst. Read .claude/agents/genetic-toxicology-analyst.md.
Analyze data_dump/[folder]/ and return Ames predictions, ICH S2(R1) study battery, and genotoxicity risk assessment."
```

**toxicology-analyst** - Repeat-dose toxicology and NOAEL determination

Use for: Safety margin calculation, target organ prediction, GLP study design, reproductive/carcinogenicity assessment

Template:
```
"You are toxicology-analyst. Read .claude/agents/toxicology-analyst.md.
Analyze data_dump/[folder]/ and return NOAEL predictions, safety margins, and ICH-compliant toxicology study designs."
```

**toxicologist-regulatory-strategist** - IND toxicology package assembly and FIH dose calculation

Use for: First-in-human dose justification, Module 2.4/2.6 preparation, regulatory strategy for clinical trials

Template:
```
"You are toxicologist-regulatory-strategist. Read .claude/agents/toxicologist-regulatory-strategist.md.
Read temp/safety_pharmacology_*.md, temp/genetic_toxicology_*.md, temp/toxicology_*.md, and data_dump/[folder]/ and return IND package with FIH dose."
```

**rwe-study-designer** - Real-world evidence study protocol design and feasibility assessment

Use for: RWE protocol development, observational cohort design, data source selection, patient identification algorithms

Template:
```
"You are rwe-study-designer. Read .claude/agents/rwe-study-designer.md.
Analyze data_dump/[rwe_methodology folder]/ and return RWE study design with feasibility assessment."
```

**rwe-outcomes-analyst** - Treatment pattern analysis and clinical outcomes algorithm development

Use for: Outcomes algorithm development, treatment pathway mapping, phenotype validation, patient journey analysis

Template:
```
"You are rwe-outcomes-analyst. Read .claude/agents/rwe-outcomes-analyst.md.
Read temp/rwe_study_design_*.md and data_dump/[treatment_patterns folder]/ and return outcomes analysis with validated algorithms."
```

**rwe-analytics-strategist** - Statistical analysis strategy development for causal inference

Use for: Propensity score methods, sensitivity analysis, missing data strategies, effect estimation

Template:
```
"You are rwe-analytics-strategist. Read .claude/agents/rwe-analytics-strategist.md.
Read temp/rwe_study_design_*.md and data_dump/[causal_inference folder]/ and return statistical analysis plan with sensitivity analyses."
```

**regulatory-risk-analyst** - CRL probability scoring and approval risk assessment

Use for: CRL probability scoring, AdComm likelihood prediction, label restriction risk, mitigation strategies

Template:
```
"You are regulatory-risk-analyst. Read .claude/agents/regulatory-risk-analyst.md.
Read temp/regulatory_precedent_*.md and data_dump/[folder]/ and return CRL probability score with risk mitigation strategies."
```

**regulatory-precedent-analyst** - Historical FDA/EMA approval precedent analysis

Use for: Comparable program identification, success/failure patterns, endpoint acceptance analysis

Template:
```
"You are regulatory-precedent-analyst. Read .claude/agents/regulatory-precedent-analyst.md.
Analyze data_dump/[folder]/ and return precedent analysis with comparable approvals and regulatory decision trends."
```

**regulatory-pathway-analyst** - Optimal regulatory pathway selection and designation strategies

Use for: Regulatory pathway selection (Standard NDA, 505(b)(2), Accelerated Approval, Breakthrough), designation strategies, submission timing

Template:
```
"You are regulatory-pathway-analyst. Read .claude/agents/regulatory-pathway-analyst.md.
Read temp/regulatory_precedent_*.md and data_dump/[folder]/ and return optimal pathway recommendation with designation strategy."
```

**regulatory-label-strategist** - FDA label negotiation and restriction mitigation

Use for: Indication statement optimization, contraindication/warning language, REMS mitigation, label negotiation tactics

Template:
```
"You are regulatory-label-strategist. Read .claude/agents/regulatory-label-strategist.md.
Read temp/regulatory_precedent_*.md and data_dump/[folder]/ and return label strategy with indication wording and REMS mitigation."
```

**regulatory-adcomm-strategist** - FDA Advisory Committee preparation and voting prediction

Use for: AdComm convening prediction, panel composition analysis, voting outcome forecasting, presentation strategy

Template:
```
"You are regulatory-adcomm-strategist. Read .claude/agents/regulatory-adcomm-strategist.md.
Read temp/regulatory_precedent_*.md and data_dump/[folder]/ and return AdComm strategy with voting prediction and presentation plan."
```

### 5. Save Analytical Outputs (If Agents Invoked)

After analytical agent execution, Claude Code saves outputs to `temp/`:
- `temp/epidemiology_analysis_{YYYY-MM-DD}_{HHMMSS}_{condition}.md`
- `temp/patient_flow_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/uptake_dynamics_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/pricing_strategy_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/revenue_forecast_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/market_sizing_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/competitive_analysis_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/bd_opportunities_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/strategic_plan_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/deal_comparables_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/npv_analysis_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/deal_structure_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/target_identification_{YYYY-MM-DD}_{HHMMSS}_{disease}.md`
- `temp/target_validation_{YYYY-MM-DD}_{HHMMSS}_{gene}.md`
- `temp/target_druggability_{YYYY-MM-DD}_{HHMMSS}_{gene}.md`
- `temp/target_hypothesis_{YYYY-MM-DD}_{HHMMSS}_{gene_disease}.md`
- `temp/safety_pharmacology_{YYYY-MM-DD}_{HHMMSS}_{compound}.md`
- `temp/genetic_toxicology_{YYYY-MM-DD}_{HHMMSS}_{compound}.md`
- `temp/toxicology_{YYYY-MM-DD}_{HHMMSS}_{compound}.md`
- `temp/ind_package_{YYYY-MM-DD}_{HHMMSS}_{compound}.md`
- `temp/rwe_study_design_{YYYY-MM-DD}_{HHMMSS}_{research_question}.md`
- `temp/rwe_outcomes_analysis_{YYYY-MM-DD}_{HHMMSS}_{research_question}.md`
- `temp/rwe_analytics_strategy_{YYYY-MM-DD}_{HHMMSS}_{research_question}.md`
- `temp/regulatory_risk_assessment_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/regulatory_precedent_analysis_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/regulatory_pathway_recommendation_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/regulatory_label_strategy_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`
- `temp/regulatory_adcomm_strategy_{YYYY-MM-DD}_{HHMMSS}_{asset}.md`

**Agent Constraint**: Analytical agents are read-only (tools: [Read]). Claude Code orchestrator handles file persistence.

## File Structure

**data_dump/**: Raw MCP results (query.json, results.json, summary.md, metadata.json)
**temp/**: Analytical agent outputs (epidemiology_analysis_*.md, patient_flow_*.md, uptake_dynamics_*.md, pricing_strategy_*.md, revenue_forecast_*.md, market_sizing_*.md, competitive_analysis_*.md, bd_opportunities_*.md, strategic_plan_*.md, deal_comparables_*.md, npv_analysis_*.md, deal_structure_*.md, target_identification_*.md, target_validation_*.md, target_druggability_*.md, target_hypothesis_*.md, safety_pharmacology_*.md, genetic_toxicology_*.md, toxicology_*.md, ind_package_*.md, rwe_study_design_*.md, rwe_outcomes_analysis_*.md, rwe_analytics_strategy_*.md) - written by Claude Code after agent execution
**.claude/.context/mcp-tool-guides/**: Tool documentation (DO NOT MODIFY)

## Token Efficiency

**Critical**: Task calls carry full conversation history (~50k tokens per call).

**Best Practices**:
1. Keep specialist prompts minimal (use template above)
2. After receiving execution plan, consider clearing context if conversation is long
3. Limit MCP results (max 50-100 records per query)
4. Use count/pagination before fetching large datasets

## Design Principles

1. **Multi-agent**: Planning agents (pharma-search-specialist for ad-hoc queries, search-orchestrator for projects) + analytical agents (epidemiology-analyst, patient-flow-modeler, uptake-dynamics-analyst, pricing-strategy-analyst, revenue-synthesizer, market-sizing-analyst, competitive-analyst, opportunity-identifier, strategy-synthesizer, comparable-analyst, npv-modeler, structure-optimizer, target-identifier, target-validator, target-druggability-assessor, target-hypothesis-synthesizer, safety-pharmacology-analyst, genetic-toxicology-analyst, toxicology-analyst, toxicologist-regulatory-strategist, rwe-study-designer, rwe-outcomes-analyst, rwe-analytics-strategist, regulatory-risk-analyst, regulatory-precedent-analyst, regulatory-pathway-analyst, regulatory-label-strategist, regulatory-adcomm-strategist)
2. **Separation of concerns**: Planning vs execution vs analysis - agents plan, Claude Code executes MCP queries, analysts process results
3. **Read-only analysts**: All analytical agents use only Read tool; Claude Code orchestrator handles file writes to temp/
4. **Token optimization**: Conservative limits, pagination, count strategies
5. **Audit trail**: Raw MCP results → data_dump/, analytical outputs → temp/
6. **Agent constraints**: Planning agents plan only (no execution), analytical agents read only (no writes), Claude Code handles all execution and file persistence
