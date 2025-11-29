# Skills Library Inventory vs 2026 Biotech Playbook

## Overview
- **Total Skills Implemented**: 82 folder-based skills + archived/deprecated
- **Status**: 82 active, all migrated to Anthropic folder structure
- **Migration Status**: 100% complete (as of 2025-11-28)
- **Library Growth**: Comprehensive coverage of core M&A, pipeline, and competitive intelligence needs

---

## Category-by-Category Mapping

### 1. Patent Cliff & Revenue Gap Analysis

#### Implemented Skills:
- **pharma-revenue-replacement-needs** (PRIMARY)
  - Status: COMPLETE - v1.0
  - Servers: sec_edgar_mcp, financials_mcp, fda_mcp
  - Calculates 2030-2035 revenue gaps for Big Pharma
  - Franchise-specific analysis (oncology, immunology, CVD, etc.)
  - Patent cliff modeling with urgency levels
  - Token efficiency: 99% reduction

- **glp1-obesity-patents**
  - Status: COMPLETE
  - Servers: uspto_patents_mcp
  - Patent trend analysis for competitive therapeutic areas
  - Assignee aggregation and timeline analysis

- **crispr-ip-landscape**
  - Status: COMPLETE
  - Servers: uspto_patents_mcp
  - Complex patent analysis with geographic mapping
  - Patent family detection and technology classification
  - Assignee categorization (industry vs academic)

- **company-rd-spending**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - R&D expense tracking (quarterly and YoY)
  - Investment velocity analysis for pipeline assessment

- **novo-nordisk-novel-patents**
  - Status: COMPLETE
  - Servers: uspto_patents_mcp, ct_gov_mcp
  - Company-specific patent analysis
  - Therapeutic area classification of IP portfolio

#### Missing/Incomplete:
- [ ] Portfolio product maturity scoring (launch timing by franchise)
- [ ] Peak sales trajectory modeling by drug
- [ ] Probability-adjusted NPV calculations
- [ ] Generic entry timing analysis
- [ ] Revenue bridge analysis (approved → at-risk → replacement)

---

### 2. M&A Deal Intelligence

#### Implemented Skills:
- **biotech-ma-deals-over-1b** (PRIMARY)
  - Status: COMPLETE - Curated dataset
  - Covers 2023-2024 major transactions ($1B+)
  - 7 deals analyzed: Pfizer-Seagen ($43B), AbbVie-ImmunoGen ($10.1B), etc.
  - Therapeutic area and platform technology trends
  - Execution time: <1 second

- **biotech-ma-deals-sec** (SECONDARY)
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - Extracts M&A filings from SEC (8-K, S-4 forms)
  - Deduplication logic for known deals
  - Filing metadata parsing and date filtering
  - Complexity: complex

- **rare-disease-acquisition-targets** (PRIMARY FOR TARGETING)
  - Status: COMPLETE - v3.0
  - Servers: ct_gov_mcp, financials_mcp
  - Yahoo Finance financial enrichment (v3.0)
  - Cash runway calculation and distress signal detection
  - Acquisition scoring (clinical + financial factors)
  - 6 distress signals: cash runway, free cash flow, D/E ratio, quick ratio, negative EPS, low P/E
  - ~28% enrichment coverage for public companies
  - Execution time: ~10-60 sec (clinical vs financial mode)

- **company-acquisitions-analysis**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - Historical acquisition data extraction
  - Trend analysis of company acquisition patterns
  - XBRL extraction patterns

#### Missing/Incomplete:
- [ ] Real-time M&A pipeline (current negotiations not in SEC filings)
- [ ] Deal closure probability models
- [ ] Strategic fit scoring (culture, geography, franchise overlap)
- [ ] Integration success prediction (post-merger synergy tracking)
- [ ] Divestiture pipeline (assets for sale)
- [ ] Licensin deal intelligence (out-licensing partner assessment)

---

### 3. Pipeline & TAM Analysis

#### Implemented Skills - Pipeline Structure:

- **indication-drug-pipeline-breakdown** (PRIMARY)
  - Status: COMPLETE - Complex skill
  - Servers: ct_gov_mcp, fda_mcp
  - Phase breakdown for ANY indication (generic parameterized)
  - Company/sponsor attribution with M&A tracking
  - Unique drug counts per phase
  - FDA approval status correlation
  - ASCII visualization of pipeline distribution
  - Trigger keywords: "active pipeline", "drug per phase", "competitive landscape", "phase distribution"
  - Complexity: Complex, last updated 2025-11-25

- **get_company_pipeline_indications** (PRIMARY FOR COMPANY)
  - Status: COMPLETE - Generic skill
  - Servers: ct_gov_mcp
  - ANY pharmaceutical company's pipeline
  - Therapeutic areas and indications where active
  - Phase analysis and condition aggregation
  - Parameterized search
  - Replaces: novo-nordisk-pipeline-indications
  - Trigger keywords: "company pipeline", "therapeutic areas targeting", "strategic focus areas"

- **indication-pipeline-attrition** (SECONDARY)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - Terminated and withdrawn trial tracking
  - Failure patterns and competitive intelligence
  - Sponsor aggregation and phase breakdown
  - Use case: Identify de-risking opportunities

- **forecast-drug-pipeline** (SECONDARY)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - Drug pipeline completion forecasting
  - Route-specific (subcutaneous, IV, oral, etc.)
  - Therapeutic area and sponsor filtering
  - Approval timing estimates (+2 years standard offset)
  - CLI enabled: forecast by route/area/sponsor

- **clinical-trials-term-phase** (GENERIC BASE)
  - Status: COMPLETE - v2.0 Generic
  - Servers: ct_gov_mcp
  - Base generic skill for ANY term + phase
  - Replaces 20+ specific trial skills (glp1-trials, adc-trials, etc.)
  - Pagination and markdown parsing reference
  - Complexity: Medium

#### Implemented Skills - TAM & Epidemiology:

- **disease-burden-per-capita** (PRIMARY)
  - Status: COMPLETE - v2.0 Generic + CLI enabled
  - Servers: who_mcp, datacommons_mcp
  - ANY disease + country combinations
  - Multi-server integration pattern
  - WHO health indicators + Data Commons population
  - Per-capita rate calculation (true burden metric)
  - Supports 32 countries
  - CLI signature: `<country_code> <disease_indicator>`

- **get_cvd_disease_burden**
  - Status: COMPLETE
  - Servers: who_mcp
  - Multi-term disease aggregation
  - Disease burden epidemiology

- **get_cvd_burden_per_capita**
  - Status: COMPLETE
  - Servers: who_mcp, datacommons_mcp
  - CVD-specific burden with population normalization
  - Error handling for data gaps

- **disease-genetic-targets** (PARAMETERIZED)
  - Status: COMPLETE
  - Servers: opentargets_mcp
  - ANY disease genetic validation
  - Top-N target filtering by score
  - CLI enabled
  - Pattern: Score-based prioritization

- **ultra-rare-metabolic-targets** (COMPLEX TAM)
  - Status: COMPLETE - Complex skill
  - Servers: opentargets_mcp
  - Ultra-rare disease target discovery
  - Druggability assessment
  - Multi-query aggregation with filtering
  - Population-based rare disease filtering
  - CLI enabled: `--max-population N`

- **large-tam-clinical-programs** (IN DEVELOPMENT - DATA QUALITY ISSUES)
  - Status: Incomplete/Flagged
  - Servers: ct_gov_mcp, who_mcp, datacommons_mcp, fda_mcp
  - Identified data quality issues:
    - Search terms too broad (e.g., 'liver fibrosis' captures non-NASH trials)
    - TAM estimates use 5% fallback when WHO fails
    - Regional TAM based only on population (not pricing)
    - Acquisition probability scoring unvalidated
  - Needs Tier 1-5 improvements before production use
  - Note: INCOMPLETE - flagged in index

#### Missing/Incomplete:
- [ ] TAM regression analysis (identify under-served vs over-served indications)
- [ ] Pipeline velocity metrics (time from Phase 1 → approval)
- [ ] Regulatory pathway impact on timelines (orphan vs standard)
- [ ] Combination therapy competitive effects (mono vs combo trials)
- [ ] Manufacturing/supply chain bottleneck analysis
- [ ] Geographic TAM variations (US vs EU vs China regulatory differences)
- [ ] Real-world epidemiology (not just clinical trial proxies)

---

### 4. Public Biotech Screening

#### Implemented Skills:

- **pharma-company-stock-data** (SCREENING BASE)
  - Status: COMPLETE - Generic with CLI
  - Servers: financials_mcp
  - Multi-company stock metrics
  - Stock price, market cap, P/E, beta, performance
  - CLI enabled: `--companies "Company1,Company2,..."`
  - Complexity: Medium

- **company-rd-spending**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - R&D as % of revenue
  - YoY growth tracking
  - Investment intensity screening

- **company-capex-allocation**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - Capital expenditure trends
  - Quarterly filtering and XBRL extraction
  - Manufacturing investment vs development

- **company-dividend-history**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - Payout ratio analysis
  - Cash return to shareholders

- **company-segment-geographic-financials**
  - Status: COMPLETE
  - Servers: sec_edgar_mcp
  - Geographic revenue breakdown
  - Segment profitability (oncology vs immunology, etc.)
  - JSON parsing of XBRL data

- **company-clinical-trials-portfolio** (GENERIC PARAMETER)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - ANY pharma company's trial portfolio
  - Status, condition, phase, year filtering
  - CLI enabled with argparse
  - Example: `Pfizer --status RECRUITING --phase PHASE3`
  - Complexity: Medium

#### Missing/Incomplete:
- [ ] Credit ratings and debt analysis (S&P, Moody's)
- [ ] Insider trading activity (blackout periods, executive purchases)
- [ ] Patent expiration calendar (when major products go generic)
- [ ] Institutional ownership tracking (activist investor positions)
- [ ] Short interest analysis (indicates market skepticism)
- [ ] Analyst coverage and EPS forecast trends
- [ ] Cash flow statement deep dives (operating vs investing vs financing)

---

### 5. Therapeutic Area Deep Dives

#### Implemented Skills - Indication-Specific Trials:

- **glp1-diabetes-drugs** (EXAMPLE)
  - Status: COMPLETE
  - Servers: fda_mcp
  - FDA approved GLP-1 drugs (21 unique after deduplication)

- **obesity-drugs-early-development** (COMPLEX)
  - Status: COMPLETE
  - Servers: fda_mcp, ct_gov_mcp
  - FDA obesity drugs + Phase 1/2 trials
  - Known drug list pattern (avoids false positives)
  - 6 approved drugs with 502 total early-stage trials

- **glp1-obesity-company-analysis**
  - Status: COMPLETE
  - Multi-server company competitive analysis

- **indication-drug-pipeline-breakdown** (WORKS FOR ANY)
  - Can be parameterized for:
    - Obesity, diabetes, Alzheimer's, KRAS, etc.
    - Shows phase distribution and company positioning

#### Implemented Skills - Disease Targets:

- **alzheimers-genetic-targets**
  - Status: COMPLETE
  - Servers: opentargets_mcp
  - Disease→Target association with evidence aggregation

- **alzheimers-therapeutic-targets**
  - Status: COMPLETE
  - Disease association query pattern

- **alzheimers-fda-drugs**
  - Status: COMPLETE
  - FDA approved Alzheimer's drugs with deduplication

- **cancer-immunotherapy-targets**
  - Status: COMPLETE
  - Multi-term cancer search
  - JSON parsing and deduplication
  - Prioritization scoring

- **ra-targets-and-trials** (COMPLEX MULTI-SERVER)
  - Status: COMPLETE
  - Servers: opentargets_mcp, ct_gov_mcp
  - Disease→Target→Trials integration pattern
  - Full data integration example

#### Implemented Skills - Literature & Publications:

- **checkpoint-inhibitor-rwe-studies**
  - Status: COMPLETE
  - Servers: pubmed_mcp
  - Real-world evidence literature
  - Study classification and trend analysis

- **anti-amyloid-antibody-publications**
  - Status: COMPLETE
  - Servers: pubmed_mcp
  - Topic categorization from literature

- **crispr-sickle-cell-publications**
  - Status: COMPLETE
  - Servers: pubmed_mcp
  - Trend analysis and keyword extraction

- **glp1-response-biomarkers**
  - Status: COMPLETE
  - Servers: pubmed_mcp
  - Literature synthesis by category

- **crispr-2024-papers**
  - Status: COMPLETE
  - Servers: pubmed_mcp
  - Date filtering and publication trends

#### Implemented Skills - Adverse Events & Safety:

- **semaglutide-adverse-events**
  - Status: COMPLETE
  - Servers: fda_mcp
  - Adverse event aggregation by demographic

- **cart-adverse-events-comparison**
  - Status: COMPLETE
  - Servers: fda_mcp
  - Multi-product AE comparison

- **diabetes-drugs-stopped-safety**
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - Safety-stopped trials identification
  - Multi-category aggregation

- **safety-stopped-trials** (GENERIC)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - ANY therapeutic area stopped trials
  - Drug failure analysis with multi-keyword search
  - Complexity: Moderate

#### Implemented Skills - IP & Manufacturing:

- **cart-manufacturing-patents**
  - Status: COMPLETE
  - Servers: uspto_patents_mcp
  - Manufacturing technology patent analysis
  - Assignee aggregation

- **kras-inhibitor-scaffold-analysis**
  - Status: COMPLETE
  - Servers: pubchem_mcp
  - Structural similarity analysis (Tanimoto coefficient)
  - Chemistry-focused competitive intelligence

- **glp1-agonist-properties**
  - Status: COMPLETE
  - Servers: pubchem_mcp
  - Molecular property comparison

#### Implemented Skills - Platform/Modality Tech:

- **adc-trials-by-payload** (IN DEVELOPMENT)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - ADC trial classification by payload type
  - Target extraction and deduplication
  - Complexity: Complex

- **enhanced-antibody-trials-by-geography** (IN DEVELOPMENT)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - Antibody trial geographic distribution
  - Multi-term search and format classification
  - Complexity: Complex

- **bispecific-antibody-trials** (IN DEVELOPMENT)
  - Status: COMPLETE
  - Servers: ct_gov_mcp
  - Bispecific therapeutic development landscape
  - Target extraction and competitive intelligence
  - Complexity: Complex

#### Missing/Incomplete:
- [ ] Combination therapy trials (synergy detection)
- [ ] Biomarker-driven patient stratification analysis
- [ ] Real-world outcomes vs trial efficacy comparison
- [ ] Geographic variation in drug penetration/market access
- [ ] Reimbursement/pricing landscape
- [ ] Patient preference and adherence data
- [ ] Health economic models (ICER, QALYs)

---

### 6. Platform vs Product Analysis

#### Implemented Skills:

- **novo-nordisk-novel-patents**
  - Status: COMPLETE
  - Platform IP portfolio assessment

- **indication-drug-pipeline-breakdown**
  - Can identify platform companies (multiple indications with same MOA)
  - Example: Use on "GLP-1 receptor agonist" to see all companies developing across obesity/diabetes

- **rare-disease-acquisition-targets**
  - Scoring includes "platform company identification"
  - Multi-program companies flagged as acquisition targets
  - Parameter: `min_programs=3` to filter for platforms

- **large-tam-clinical-programs** (INCOMPLETE)
  - Intended to identify platform opportunities in large TAM spaces
  - Data quality issues prevent production use

#### Missing/Incomplete:
- [ ] Technology platform valuation models
- [ ] Platform extensibility scoring (how many indications can use MOA?)
- [ ] Core IP patent estate analysis (strength/breadth/duration)
- [ ] Adjacent market opportunities (label expansions)
- [ ] Manufacturing platform economics
- [ ] Regulatory pathway acceleration (platform-based approvals)
- [ ] Licensing value assessment (platform licensing vs product licensing)

---

### 7. Squeezed Middle Strategies

#### Implemented Skills:

- **company-product-launch-timeline** (ANALYZE)
  - Status: COMPLETE - Complex skill
  - Servers: fda_mcp, ct_gov_mcp
  - Company product launch analysis by year
  - Multi-skill composition pattern
  - Temporal analysis and company focus area filtering
  - CLI enabled: `<company_name> --focus-area {area} --start-year 2020`
  - Complexity: Complex

- **forecast-drug-pipeline**
  - Can identify gaps in pipeline (2026-2027 completion forecasting)
  - Spot opportunities where competitors have dry periods

- **indication-pipeline-attrition**
  - Identify attrition rates (high attrition = opportunity to differentiate)
  - Sponsor aggregation shows failed competitors

- **companies-by-moa** (GENERIC COMPETITIVE)
  - Status: COMPLETE
  - Servers: ct_gov_mcp, fda_mcp
  - ANY MOA/disease combinations
  - Company competitive assessment (leaders, late-stage, early-stage)
  - Phase filtering and academic filtering
  - Trigger keywords: "companies working on", "who's developing"
  - Complexity: Moderate
  - Last updated: 2025-11-25

#### Missing/Incomplete:
- [ ] Orphan drug lifecycle analysis (exclusivity periods, annual sales potential)
- [ ] Niche market penetration models (% of total addressable market)
- [ ] First-to-market vs fast-follower success analysis
- [ ] Combination therapy feasibility (can mono drugs be combined?)
- [ ] Line extension opportunities (new indication for existing molecule)
- [ ] Geographic arbitrage analysis (earlier approval in smaller markets)
- [ ] Manufacturing cost benchmarking (competitive cost analysis)

---

## Summary by Maturity Level

### PRODUCTION READY (Fully Tested & Deployed)
- pharma-revenue-replacement-needs
- biotech-ma-deals-over-1b
- rare-disease-acquisition-targets (v3.0)
- indication-drug-pipeline-breakdown
- companies-by-moa
- disease-burden-per-capita (v2.0)
- company-clinical-trials-portfolio
- crispr-ip-landscape
- pharma-company-stock-data
- glp1-fda-drugs, alzheimers-fda-drugs, etc. (18+ FDA drug skills)
- All CT.gov trial skills (clinical-trials-term-phase generic base + specific implementations)
- All company financial skills (R&D, capex, dividends, segment analysis)
- All safety/adverse event skills

### MATURE (Well-Tested, Minor Issues)
- biotech-ma-deals-sec
- get_company_pipeline_indications
- indication-pipeline-attrition
- forecast-drug-pipeline
- company-product-launch-timeline
- rare disease skills (acquisition targets, orphan drugs)

### IN DEVELOPMENT / LIMITED DATA QUALITY
- large-tam-clinical-programs (FLAGGED: search term broadness, TAM fallback logic issues)
- adc-trials-by-payload (new implementation, needs validation)
- enhanced-antibody-trials-by-geography (new, needs validation)
- bispecific-antibody-trials (new, needs validation)

### STRATEGIC ANALYSIS (Multi-Server Composites)
- drug-swot-analysis (9 servers)
- company-swot-analysis (5 servers)
- generate_drug_swot_analysis

---

## Critical Gaps vs 2026 Playbook

### IMMEDIATE PRIORITIES (Tier 1 - Start Now for 2026 impact):
1. **Patent Cliff Quantification** - pharma-revenue-replacement-needs exists but needs:
   - Peak sales trajectory by franchise
   - Probability-adjusted NPV models
   - Generic entry timing analysis
   - Revenue bridge (approved → at-risk → replacement)

2. **M&A Pipeline Intelligence** - Curated dataset exists but missing:
   - Current negotiations (real-time intelligence)
   - Strategic fit scoring algorithms
   - Deal failure/renegotiation detection
   - Divestiture pipeline analysis

3. **TAM Analytics** - large-tam-clinical-programs exists but flagged for quality issues
   - Needs data validation fix before use
   - Geographic TAM variation by regulatory pathway
   - Pricing impact on market sizing

### HIGH PRIORITY (Tier 2 - Q1 2026):
4. **Biotech Screening Enhancements**:
   - Credit rating + debt analysis
   - Patent expiration calendar
   - Insider trading / institutional ownership
   - EPS forecast trends from analyst coverage

5. **Platform Analysis**:
   - Technology platform valuation models
   - Label expansion potential (adjacent markets)
   - Manufacturing platform economics

### MEDIUM PRIORITY (Tier 3 - Q2 2026+):
6. **Niche Market Economics**:
   - Orphan drug annual sales potential models
   - Market penetration forecasting
   - Line extension opportunities
   - Geographic arbitrage analysis

---

## Quick Reference: Playbook Coverage %

| Playbook Category | Implementation | Status | Priority |
|-------------------|----------------|--------|----------|
| Patent Cliff Analysis | 40% | Has foundation, needs extensions | Tier 1 |
| M&A Deal Intelligence | 60% | Curated deals + targeting, missing pipeline | Tier 1 |
| Pipeline & TAM | 70% | Strong on pipeline, TAM needs quality fix | Tier 1 |
| Public Biotech Screening | 50% | Basic financials, missing credit/insider/analyst | Tier 2 |
| Therapeutic Area Deep Dives | 85% | Excellent trial/target/literature coverage | Complete |
| Platform vs Product | 30% | Identified but not systematically analyzed | Tier 3 |
| Squeezed Middle | 45% | Good competitive positioning, missing niche economics | Tier 2 |

**Overall: 55% Implementation → Targeting 85%+ by 2026 with Tier 1 additions**

