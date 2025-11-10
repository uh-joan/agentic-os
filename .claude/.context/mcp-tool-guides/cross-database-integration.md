# Cross-Database Integration Patterns

> **Recovered from LSH commit 3e02457 (Oct 9, 2025)**
> Strategies for linking entities and triangulating data across multiple pharmaceutical databases.

## ENTITY LINKING STRATEGIES

### Drug Name Mapping
**Challenge**: Same drug, multiple identifiers across databases

**Mapping Chain**:
```
Brand Name → Generic Name → INN → ATC Code → NDC → RxNorm → UNII
```

**Examples**:
- Brand: "Ozempic", "Rybelsus", "Wegovy"
- Generic: "semaglutide"
- ATC Code: A10BJ06 (GLP-1 agonist)
- UNII: 53AXN4NNHX

**Tools**:
- FDA `fda_info`: Maps brand ↔ generic ↔ NDC ↔ UNII
- NLM `nlm_ct_codes` (RxTerms): Maps drug names ↔ strengths ↔ forms
- WHO: Maps ATC codes ↔ INN
- ClinicalTrials.gov: Uses intervention names (often generic)
- PubMed: Uses MeSH terms and substance names

**Workflow**:
1. Start with known identifier (e.g., "Ozempic")
2. Query FDA to get generic name + UNII
3. Use generic name for ClinicalTrials.gov
4. Use MeSH term for PubMed
5. Use UNII for chemical database queries

### Company Name Mapping
**Challenge**: Subsidiaries, acquisitions, ticker symbols

**Mapping Chain**:
```
Subsidiary → Parent Company → Stock Ticker → CIK Number → LEI
```

**Examples**:
- Subsidiary: "Genentech"
- Parent: "Roche Holding AG"
- Ticker: "RHHBY" (ADR)
- CIK: 0001070012

**Tools**:
- SEC `sec-edgar`: Maps ticker ↔ CIK ↔ company name
- Yahoo Finance: Maps ticker ↔ company name
- ClinicalTrials.gov: Uses legal entity names (sponsors)
- USPTO `uspto_patents`: Uses assignee names

**Workflow**:
1. Identify all variants (legal name, DBA, subsidiaries)
2. Get CIK from SEC for financial data
3. Get ticker for market data
4. Use legal name for clinical trials
5. Check assignee variations for patents

### Disease/Indication Mapping
**Challenge**: Clinical vs coding vs MeSH terminology

**Mapping Chain**:
```
Clinical Description → ICD-10-CM → ICD-11 → MeSH → Clinical Trial Condition
```

**Examples**:
- Clinical: "Type 2 diabetes"
- ICD-10-CM: E11 (Type 2 diabetes mellitus)
- ICD-11: 5A11 (Type 2 diabetes mellitus)
- MeSH: D003924 (Diabetes Mellitus, Type 2)
- CT.gov: "Diabetes Mellitus, Type 2" or "Type 2 Diabetes"

**Tools**:
- NLM `nlm_ct_codes`: Maps ICD-10-CM ↔ ICD-11 ↔ ICD-9-CM
- PubMed: Uses MeSH terms
- ClinicalTrials.gov: Uses free text condition terms
- Data Commons: Uses disease ontologies

**Workflow**:
1. Start with clinical description
2. Map to ICD-10-CM using nlm_ct_codes
3. Get MeSH term for PubMed searches
4. Use both clinical and MeSH terms for CT.gov
5. Use ICD codes for epidemiology data

### Investigator/KOL Mapping
**Challenge**: Author name variations, affiliations, multiple roles

**Mapping Chain**:
```
Author Name → ORCID → Trial PI → Institution → NPI → Publications
```

**Examples**:
- Variations: "J. Smith", "John Smith", "Smith, J.", "Smith JA"
- ORCID: 0000-0002-1234-5678 (unique researcher ID)
- NPI: 1234567890 (if clinician)
- Institution: "Harvard Medical School"

**Tools**:
- PubMed: Author fields, ORCID links
- ClinicalTrials.gov: Principal Investigator, study chair
- NLM `nlm_ct_codes`: NPI lookups (organizations & individuals)
- OpenTargets: Author contributions to genetic studies

**Workflow**:
1. Search PubMed by author name + affiliation
2. Get ORCID if available
3. Search CT.gov for PI role
4. Use NPI lookup for prescriber/provider data
5. Cross-reference institution affiliations

### Geographic Mapping
**Challenge**: Different granularities across databases

**Mapping Chain**:
```
Census Tract → ZIP Code → County → State → Country → WHO Region
```

**Examples**:
- Census Tract: 06037264100 (LA County census tract)
- ZIP: 90001
- County: Los Angeles County (geoId/06037)
- State: California (geoId/06)
- Country: USA (country/USA)
- WHO Region: AMR (Americas)

**Tools**:
- Data Commons: Hierarchical geographic entities with geoId
- CMS `cms_search_providers`: Geographic provider filtering
- ClinicalTrials.gov: City, state, country for trial sites
- WHO: Regional health statistics

**Workflow**:
1. Start with location description (e.g., "Los Angeles")
2. Get geoId from Data Commons for standardization
3. Query CMS for providers in that geoId
4. Search CT.gov for trials in city/state
5. Aggregate to state or national level for WHO data

## TIMELINE ALIGNMENT STRATEGIES

### Clinical Development → Regulatory → Market Events

**Event Sequence**:
```
Trial Start → Trial Complete → Results Published → FDA Submission → FDA Approval → Market Launch → Post-Market Surveillance
```

**Data Sources by Timeline Stage**:

**Pre-Clinical (Years -5 to -3)**:
- USPTO Patents: Target/compound filings
- PubMed: Preclinical research publications
- SEC Filings: Pipeline mentions in 10-K

**Clinical Trials (Years -3 to 0)**:
- ClinicalTrials.gov: Trial start, completion, status changes
- PubMed: Protocol publications, interim results
- SEC Filings: Pipeline updates, milestone announcements

**Regulatory Review (Years 0 to +1)**:
- FDA: Submission date, review milestones, approval
- SEC Filings: 8-K forms for regulatory milestones
- ClinicalTrials.gov: Results posting

**Market Entry (Years +1 to +2)**:
- FDA: Official approval date, label
- SEC Filings: Revenue recognition, sales guidance
- Yahoo Finance: Stock price reactions
- CMS: Initial prescriber adoption patterns

**Post-Market (Years +2+)**:
- FDA FAERS: Adverse event accumulation
- PubMed: Real-world evidence publications
- ClinicalTrials.gov: Phase 4 trials, label expansions
- SEC Filings: Sales trajectories, patent litigation

### Alignment Workflow
1. **Anchor event**: Identify FDA approval date (most reliable)
2. **Work backward**: Find trial start/complete dates
3. **Work forward**: Track market entry and post-market events
4. **Validate**: Check SEC filings for company-reported timelines
5. **Cross-reference**: Verify consistency across sources

### Handling Time Lags
- **Trial results → Publication**: 12-24 month lag typical
- **Trial complete → FDA submission**: 6-12 months
- **FDA submission → Approval**: 6-12 months (standard), 2-6 months (priority)
- **Approval → Market entry**: 1-3 months
- **Adverse events → Label update**: Variable, 6-24 months

## DATA TRIANGULATION PATTERNS

### Pattern 1: Trial Status Validation
**Goal**: Confirm clinical trial progress

**Sources**:
1. ClinicalTrials.gov: Official status
2. SEC Filings: Company announcements
3. PubMed: Results publications
4. Company Press Releases: Commercial messaging

**Validation Logic**:
- ✅ **High Confidence**: All 4 sources agree
- ⚠️ **Medium Confidence**: 2-3 sources agree, 1 lag/missing
- ❌ **Low Confidence**: Contradictions exist
- 🔍 **Investigate**: ClinicalTrials.gov says "completed" but no results posted after 12+ months

**Example**:
```
CT.gov: "Completed 2023-03-15"
SEC 10-Q: "Phase 3 trial met primary endpoint" (filed 2023-05-10)
PubMed: No publication yet (checked 2023-09-20)
→ Medium confidence, publication likely pending
```

### Pattern 2: Safety Signal Confirmation
**Goal**: Validate adverse event patterns

**Sources**:
1. FDA FAERS: Post-market reports
2. PubMed: Case reports, meta-analyses
3. WHO VigiBase: International ADR database
4. FDA Label: Warnings/precautions section

**Validation Logic**:
- ✅ **Established Signal**: FDA label mentions + FAERS reports + literature
- ⚠️ **Emerging Signal**: FAERS spike + some literature, no label yet
- 🔍 **Investigate**: Geographic clustering (one country reports, others don't)

**Example**:
```
FAERS: 50 reports of event X (2022-2023)
PubMed: 3 case reports of event X (2023)
FDA Label: No mention of event X
WHO: 15 reports from Europe
→ Emerging signal, regulatory review likely ongoing
```

### Pattern 3: Financial Impact Validation
**Goal**: Confirm pipeline value and market assumptions

**Sources**:
1. SEC Filings: Revenue guidance, R&D spend
2. Yahoo Finance: Analyst estimates, stock movements
3. ClinicalTrials.gov: Trial scale (patient count, sites)
4. Data Commons: Disease prevalence (TAM estimation)

**Validation Logic**:
- ✅ **Aligned**: Company guidance matches analyst models matches epidemiology
- ⚠️ **Optimistic**: Company guidance > analyst models
- 🔍 **Investigate**: Revenue reported but no approved indication

**Example**:
```
SEC: "Peak sales potential $2B" (company estimate)
Analysts: Consensus $1.5B (Yahoo Finance)
Epidemiology: 500K eligible patients × $15K/year = $7.5B TAM
→ Penetration assumption: 13-20% market share implied
```

### Pattern 4: Prescriber Pattern Validation
**Goal**: Understand real-world drug utilization

**Sources**:
1. CMS Provider Data: Medicare claims, prescriber volume
2. ClinicalTrials.gov: Trial investigator sites
3. NPI Lookups: Provider specialty, credentials
4. PubMed: Author affiliations on clinical studies

**Validation Logic**:
- ✅ **KOL Network**: High prescribers overlap with trial investigators and publications
- ⚠️ **Geographic Concentration**: Prescribing concentrated in trial site regions
- 🔍 **Off-Label Use**: Prescribing for non-approved indications (check label)

**Example**:
```
CMS: Top prescriber in CA, 500 patients/year
CT.gov: PI for 3 trials at Stanford (CA)
PubMed: 15 publications on this drug class
NPI: Endocrinologist, Stanford-affiliated
→ High-confidence KOL, expected utilization pattern
```

## ENTITY RELATIONSHIP GRAPHS

### Drug-Company-Trial-Investigator Network
```
Drug (semaglutide)
├── Companies
│   ├── Novo Nordisk (sponsor)
│   └── Contract CROs (trial operators)
├── Clinical Trials
│   ├── NCT12345 (Phase 3, diabetes)
│   │   ├── PI: Dr. Smith, Harvard
│   │   └── Sites: 50 locations, 15 states
│   └── NCT67890 (Phase 3, obesity)
│       ├── PI: Dr. Jones, Stanford
│       └── Sites: 40 locations, 12 states
├── Publications
│   ├── NEJM 2021 (efficacy)
│   └── Lancet 2022 (safety)
└── Regulatory
    ├── FDA Approval: 2017 (Ozempic, diabetes)
    └── FDA Approval: 2021 (Wegovy, obesity)
```

### Building the Graph
1. **Start with entity**: Drug, company, or investigator
2. **Query each database**: Collect related entities
3. **Link via identifiers**: Use mapping strategies above
4. **Validate connections**: Confirm relationships across sources
5. **Visualize network**: Identify clusters, gaps, anomalies

### Analysis Patterns
- **Hub nodes**: Highly connected entities (e.g., KOLs on multiple trials)
- **Isolated nodes**: Entities with few connections (investigate why)
- **Clusters**: Groups of related entities (e.g., regional trial networks)
- **Gaps**: Missing links (e.g., no trials in expected indication)

## CONTRADICTION RESOLUTION

### When Sources Disagree

**Type 1: Timing Differences**
- **Cause**: Data update frequencies vary
- **Resolution**: Use most recent authoritative source
- **Example**: CT.gov updated weekly, SEC quarterly

**Type 2: Definition Differences**
- **Cause**: Different metrics or inclusion criteria
- **Resolution**: Align definitions, convert units
- **Example**: "Revenue" (GAAP vs non-GAAP)

**Type 3: Coverage Differences**
- **Cause**: Databases have different scope/geography
- **Resolution**: Document coverage, note limitations
- **Example**: CMS covers Medicare only (65+), not full population

**Type 4: Data Quality Issues**
- **Cause**: Errors, missing data, outdated info
- **Resolution**: Cross-validate with 3rd source, flag uncertainty
- **Example**: CT.gov trial "recruiting" but sponsor says "completed"

### Resolution Protocol
1. **Identify contradiction**: Document specific discrepancy
2. **Check timestamps**: Which source is most recent?
3. **Check definitions**: Are they measuring the same thing?
4. **Check coverage**: Do they cover the same population/geography?
5. **Consult 3rd source**: Tie-breaker if needed
6. **Document**: Report finding with confidence level and explanation

## INTEGRATION CHECKLIST

Before considering search complete:
- [ ] Entity names standardized across databases
- [ ] Timeline events aligned and validated
- [ ] Key findings confirmed across 2+ sources
- [ ] Contradictions identified and resolved
- [ ] Confidence levels assigned to all claims
- [ ] Data gaps documented
- [ ] Relationship graph constructed (if applicable)
- [ ] Geographic mappings validated
- [ ] Next integration steps identified
