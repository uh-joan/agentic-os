# Search Execution Workflows

> **Recovered from LSH commit 3e02457 (Oct 9, 2025)**
> Comprehensive workflow templates for common pharmaceutical intelligence search patterns.
> These workflows were lost during optimization but provide valuable patterns for complex multi-database searches.

**⚠️ Note**: This file is 833 lines. Reference specific workflows by name:
- Workflow 1: Comprehensive Drug Profile Search
- Workflow 2: Competitive Pipeline Analysis
- Workflow 3: KOL Identification and Mapping
- Workflow 4: Market Access Intelligence
- Workflow 5: Safety Signal Detection
- Workflow 6: Financial Impact Assessment
- And many more...

## SEARCH EXECUTION WORKFLOWS

### Workflow 1: Comprehensive Drug Profile Search
**Think hard about prioritizing most impactful databases first**
Step 1: FDA Status Check (COUNT FIRST - MANDATORY)
fda_approvals:
  search_term: "openfda.brand_name:DRUG_NAME"
  count: "application_number"
  → Then: search_term: "application_number:BLA######"
          count: "submissions.submission_status_date"

Step 2: Patent/Exclusivity Assessment
fda_orange_book:
  search_term: "drug_name.exact:DRUG_NAME"
  fields_for_general: "patent_expire_date,exclusivity_date,exclusivity_code"

Step 3: Clinical Trial Landscape
ct_gov:
  intervention: "DRUG_NAME"
  status: ["RECRUITING", "ACTIVE_NOT_RECRUITING", "COMPLETED"]
  fields: ["NCTId", "Phase", "PrimaryOutcome", "CompletionDate"]

Step 4: Safety Profile (Count First)
fda_faers:
  search_term: "products.brand_name:DRUG_NAME"
  count: "patient.reaction.reactionmeddrapt.exact"
  limit: 100

Step 5: Scientific Evidence
pubmed:
  query: "DRUG_NAME[Title/Abstract] AND (efficacy OR safety OR clinical trial)"
  filters: "published last 2 years, humans, clinical trial"

Step 6: Financial Impact
yahoo_finance:
  symbol: "COMPANY_TICKER"
  metrics: ["revenue", "pipeline_value", "market_cap"]
  events: "around approval date"

### Workflow 2: Competitive Pipeline Analysis
Step 1: Identify Competitors (via SEC)
sec_filings:
  form_type: "10-K"
  search_terms: "therapeutic_area AND (Phase 2 OR Phase 3)"
  companies: ["COMP1", "COMP2", "COMP3"]

Step 2: Clinical Trial Tracking (Optimized)
ct_gov:
  sponsor: "Company Name"
  phase: ["PHASE2", "PHASE3"]
  status: ["RECRUITING", "ACTIVE_NOT_RECRUITING"]
  fields: ["NCTId", "BriefTitle", "Phase", "PrimaryCompletionDate"]

Step 3: Recent Publications (Filtered)
pubmed:
  affiliation: "Company Name"
  publication_date: "last 12 months"
  publication_type: "clinical trial OR systematic review"

Step 4: Regulatory Milestones
fda_calendar:
  sponsor: "Company Name"
  date_range: "next 12 months"
  event_type: "PDUFA OR advisory_committee"

Step 5: Financial Metrics
yahoo_finance:
  symbols: ["COMP1", "COMP2", "COMP3"]
  metrics: ["R&D_expense", "cash_runway", "market_cap"]
  compare: true

### Workflow 3: Safety Signal Investigation
Step 1: Initial Signal Detection (COUNT ONLY)
fda_faers:
  search_term: "products.brand_name:DRUG_NAME+AND+receivedate:[20240101+TO+*]"
  count: "patient.reaction.reactionmeddrapt.exact"
  limit: 200

Step 2: Severity Assessment (Targeted Fields)
fda_faers:
  search_term: "products.brand_name:DRUG_NAME+AND+serious:1"
  fields_for_general: "patient.reaction.reactionmeddrapt,outcome"
  limit: 1000

Step 3: Comparator Analysis (Class Effect Check)
fda_faers:
  search_term: "products.drug_class:CLASS_NAME"
  count: "products.brand_name"
  filter_reaction: "TOP_SIGNALS_FROM_STEP1"

Step 4: Literature Validation
pubmed:
  query: "DRUG_NAME AND (adverse OR safety OR toxicity)"
  filters: "case reports, last 6 months"

Step 5: Regulatory Actions
fda_alerts:
  drug_name: "DRUG_NAME"
  alert_type: "safety_communication OR label_change OR REMS"

### Workflow 4: Market Opportunity Assessment
Step 1: Disease Epidemiology
Step 1: Disease Epidemiology (Enhanced with Data Commons)
datacommons:
  statVars: ["Prevalence_Disease_[CONDITION]", "Incidence_Disease_[CONDITION]", "MortalityRate_Cause_[CONDITION]"]
  places: ["country/USA", "continent/EU", "continent/AS"]
  date: "2019/2024"

who_data:
  disease_code: "ICD_CODE"
  metrics: ["prevalence", "incidence", "mortality"]
  regions: ["global", "US", "EU", "Asia"]

Step 2: Current Treatment Landscape
cms_providers:
  diagnosis_codes: ["ICD10_CODES"]
  procedure_codes: ["CPT_CODES"]
  aggregate_by: "specialty,geography"

Step 3: Competitive Trials
ct_gov:
  condition: "DISEASE_NAME"
  phase: ["PHASE2", "PHASE3"]
  status: ["RECRUITING"]
  count_by: "sponsor"

Step 4: Economic Burden
fred_data:
  series: ["healthcare_spending", "disease_specific_costs"]
  correlation_with: "drug_approvals"

Step 5: Payer Landscape
sec_filings:
  companies: ["major_payers"]
  search_terms: "coverage_policy AND DISEASE_AREA"

### Workflow 5: Population Health & Market Sizing
Step 1: Target Population Sizing
datacommons:
statVars: ["Count_Person", "Count_Person_[AGE_GROUP]", "Prevalence_Disease_[CONDITION]"]
places: ["country/USA"]
breakdown: "Age,Gender,Race"
Step 2: Healthcare Infrastructure
datacommons:
statVars: ["Count_MedicalFacility_Hospital", "Count_MedicalProvider_Specialist_[TYPE]"]
places: ["state/CA", "state/NY", "state/TX", "state/FL"]
Step 3: Socioeconomic Factors
datacommons:
statVars: ["Median_Income_Household", "Count_Person_NoHealthInsurance", "UnemploymentRate"]
places: [target_markets]
correlation_with: "disease_prevalence"
Step 4: Competitive Treatment Access
cms_providers:
cross_reference_with: datacommons_population_density
aggregate_by: "geographic_coverage"

### Workflow 6: Patent Landscape Analysis
**Think hard about FTO vs competitive intelligence objectives**

Step 1: Broad Patent Landscape (COUNT FIRST - use limit parameter)
uspto_patents:
  method: "ppubs_search_patents"
  query: "therapeutic_area AND mechanism"
  limit: 100
  sort: "date_publ desc"
  → Result: Total patent count, top assignees, recent filings

Step 2: Competitor Portfolio Deep Dive
uspto_patents:
  method: "ppubs_search_patents"
  query: "assignee:\"Company Name\" AND therapeutic_area"
  limit: 50
  → Result: Company's patent estate, claim scope, patent families

Step 3: Patent Family Analysis (Continuation Practice)
uspto_patents:
  method: "get_app_continuity"
  app_num: "14412875"  # From Step 2 results
  → Result: Parent/child relationships, divisionals, CIPs

Step 4: Assignment Tracking (M&A Intelligence)
uspto_patents:
  method: "get_app_assignment"
  app_num: "14412875"
  → Result: Ownership history, licensing deals, change of control

Step 5: FTO Analysis (Blocking Patent Check)
uspto_patents:
  method: "ppubs_get_full_document"
  guid: "[GUID from Step 2]"
  source_type: "USPAT"
  → Result: Full patent text, independent claims, claim scope

Step 6: Patent Expiry Timeline
uspto_patents:
  method: "get_app_metadata"
  app_num: "14412875"
  → Result: Filing date, grant date, PTE eligibility, expiry calculation

### OpenTargets MCP (opentargets-mcp-server) - GENETIC TARGET VALIDATION OPTIMIZATION

**Think hard about genetic evidence as gold standard for target validation**

#### CORE CAPABILITIES (6 methods)
1. **search_targets**: Find targets by gene symbol/name → Returns Ensembl gene IDs
2. **search_diseases**: Find diseases by name/synonym → Returns EFO disease IDs
3. **get_target_disease_associations**: Get target-disease associations with evidence scores
4. **get_disease_targets_summary**: Get all targets for a disease (overview)
5. **get_target_details**: Comprehensive target profile (tractability, safety, drugs)
6. **get_disease_details**: Comprehensive disease profile (phenotypes, therapeutic area)

#### GENETIC EVIDENCE QUERIES

**Target Discovery Workflow**:
```
1. search_diseases: "Alzheimer's disease" → EFO_0000249
2. get_disease_targets_summary: diseaseId="EFO_0000249", minScore=0.5, size=50
   → Returns: Top 50 genetically validated targets with association scores
3. get_target_details: id=[top_target_ensembl_id]
   → Returns: Tractability (small molecule, antibody), known drugs, safety liabilities
```

**Target Validation Workflow**:
```
1. search_targets: "JAK1" → ENSG00000162434
2. search_diseases: "rheumatoid arthritis" → EFO_0000685
3. get_target_disease_associations: targetId="ENSG00000162434", diseaseId="EFO_0000685"
   → Returns: Association score (0-1), evidence breakdown (genetic, somatic, drug, pathways)
4. Interpret evidence strength:
   - Score >0.7: STRONG genetic evidence (streamlined validation recommended)
   - Score 0.3-0.7: MODERATE evidence (standard validation required)
   - Score <0.3: WEAK evidence (extensive validation needed)
```

**Genetic Safety Assessment Workflow**:
```
1. search_targets: "BTK" → ENSG00000010671
2. get_target_details: id="ENSG00000010671"
   → Returns: Safety liabilities (e.g., X-linked agammaglobulinemia for BTK deficiency)
3. get_target_disease_associations: targetId="ENSG00000010671" (all diseases)
   → Returns: Pleiotropic effects (multiple disease associations = broad on-target effects)
4. Safety interpretation:
   - Genetic loss-of-function = disease → ON-TARGET toxicity risk
   - Multiple disease associations → Pleiotropic effects (manage dosing/monitoring)
```

**Clinical Precedent Check (Repurposing Opportunities)**:
```
1. search_targets: "IL6R" → ENSG00000160712
2. get_target_disease_associations: targetId="ENSG00000160712" (all diseases)
   → Check for known drugs in drug evidence type
3. If known drug in OTHER indication + genetic evidence in NEW indication:
   → REPURPOSING OPPORTUNITY (e.g., tocilizumab RA → COVID-19)
```

**Genetic Biomarker Identification**:
```
1. get_target_disease_associations: targetId=[target], diseaseId=[disease]
   → Extract genetic variants from genetic association evidence
2. Identify GWAS SNPs and rare variants as patient selection biomarkers
3. Design companion diagnostic for genetic enrichment
4. Stratify trial population by genotype (variant carriers vs non-carriers)
```

#### EFFICIENT QUERYING

**Entity Mapping** (CRITICAL):
- Always use `search_targets` to map gene symbols → Ensembl gene IDs (ENSG00000...)
- Always use `search_diseases` to map disease names → EFO IDs (EFO_...)
- Store mappings to avoid repeated searches

**Evidence Filtering**:
- Use `minScore` parameter to filter associations (0.5 = high confidence, 0.7 = very strong)
- Adjust `size` parameter based on scope (default 25, max 500 for comprehensive searches)
- For disease target overview: Use `get_disease_targets_summary` (faster than individual queries)

**Evidence Type Prioritization**:
1. **Genetic associations** (GWAS, rare variants): HIGHEST validation quality (2x clinical PoS)
2. **Somatic mutations**: Cancer-specific validation (oncogene addiction)
3. **Drugs**: Clinical precedent (de-risks druggability, repurposing opportunities)
4. **Pathways**: Biological mechanism context (supports MOA understanding)
5. **Animal models**: Phenotype validation (supports in vivo validation)

#### QUERY PATTERNS BY USE CASE

**Pattern 1: Target Discovery for Indication**
```
Step 1: Map disease name to EFO ID
opentargets:
  method: "search_diseases"
  query: "rheumatoid arthritis"
  size: 10
  → Result: EFO_0000685 (rheumatoid arthritis)

Step 2: Get all validated targets for disease
opentargets:
  method: "get_disease_targets_summary"
  diseaseId: "EFO_0000685"
  minScore: 0.5
  size: 50
  → Result: 127 targets with association scores (JAK1, IL6R, TNF, etc.)

Step 3: Get detailed profiles for top targets
opentargets:
  method: "get_target_details"
  id: "ENSG00000162434"  # JAK1
  → Result: Small molecule tractability, known drugs (tofacitinib), safety data
```

**Pattern 2: Target Validation Assessment**
```
Step 1: Map entities to IDs
opentargets:
  method: "search_targets"
  query: "KRAS"
  → Result: ENSG00000133703

opentargets:
  method: "search_diseases"
  query: "lung adenocarcinoma"
  → Result: EFO_0000571

Step 2: Get association evidence
opentargets:
  method: "get_target_disease_associations"
  targetId: "ENSG00000133703"
  diseaseId: "EFO_0000571"
  → Result: Association score 0.92 (somatic mutation evidence from COSMIC)

Step 3: Validation decision
IF score >0.9 AND somatic mutation evidence → STRONG oncogene driver
  → Streamlined validation (genetic evidence = validation)
```

**Pattern 3: Genetic Safety Profiling**
```
Step 1: Get comprehensive target profile
opentargets:
  method: "get_target_details"
  id: "ENSG00000010671"  # BTK
  → Result: Safety liabilities (X-linked agammaglobulinemia)

Step 2: Check pleiotropic effects
opentargets:
  method: "get_target_disease_associations"
  targetId: "ENSG00000010671"
  # No diseaseId = all diseases
  → Result: Multiple disease associations (immune deficiency, autoimmune)

Step 3: Safety interpretation
- BTK deficiency → X-linked agammaglobulinemia (immune deficiency)
- Flag: Complete BTK inhibition = ON-TARGET immune suppression risk
- Mitigation: Partial inhibition, dosing strategy, monitoring
```

**Pattern 4: Competitive Target Landscape**
```
Step 1: Get all targets for therapeutic area
opentargets:
  method: "get_disease_targets_summary"
  diseaseId: "EFO_0000685"  # Rheumatoid arthritis
  minScore: 0.3
  size: 100
  → Result: 200+ targets (broad landscape)

Step 2: Cross-reference with clinical trials (ClinicalTrials.gov)
ct_gov:
  condition: "rheumatoid arthritis"
  status: "recruiting OR active_not_recruiting"
  → Result: 450 active trials

Step 3: Competitive gap analysis
- Identify genetically validated targets WITHOUT active trials (white space)
- Identify targets with weak genetic evidence BUT many trials (crowded, risky)
- Prioritize: Strong genetic evidence (>0.7) + no/few trials = opportunity
```

**Pattern 5: Biomarker-Driven Trial Design**
```
Step 1: Get genetic evidence for target-disease
opentargets:
  method: "get_target_disease_associations"
  targetId: "ENSG00000162434"  # JAK1
  diseaseId: "EFO_0000685"  # RA
  → Result: Genetic association evidence (GWAS SNPs: rs2476601 PTPN22)

Step 2: Extract genetic biomarkers
- GWAS variants: rs2476601 (PTPN22), HLA-DRB1 shared epitope
- Rare variants: JAK1 coding variants (if available)

Step 3: Design genetic enrichment strategy
- Companion diagnostic: HLA-DRB1 genotyping
- Inclusion criteria: HLA-DRB1 positive patients (genetic RA risk)
- Expected enrichment: 30-50% PoS improvement vs unselected population
```

#### EVIDENCE INTERPRETATION GUIDELINES

**Association Score Interpretation**:
- **0.9-1.0**: Very strong evidence (GWAS P<5e-8, strong somatic mutations, multiple drugs)
- **0.7-0.9**: Strong evidence (GWAS significant, somatic mutations, clinical precedent)
- **0.5-0.7**: Moderate evidence (suggestive GWAS, pathway evidence, animal models)
- **0.3-0.5**: Weak-moderate evidence (pathway only, text mining, expression)
- **<0.3**: Weak evidence (requires extensive validation)

**Evidence Type Hierarchy** (Target Validation):
1. **Genetic associations + Drugs**: Highest confidence (genetic validation + clinical precedent)
2. **Somatic mutations** (oncology): High confidence (driver mutations)
3. **Genetic associations** (rare variants, GWAS): High confidence (causal evidence)
4. **Drugs only**: Moderate confidence (clinical precedent, but no genetic validation)
5. **Pathways + Animal models**: Moderate confidence (biological plausibility)
6. **Text mining + Expression**: Low confidence (correlation, not causation)

**Safety Liability Flags**:
- **Genetic LOF = disease**: ON-TARGET toxicity risk (e.g., BTK deficiency → immune deficiency)
- **Pleiotropic effects**: Multiple disease associations = broad on-target effects (dose carefully)
- **Essential genes**: Embryonic lethality or severe phenotypes (therapeutic window concern)
- **Immune function**: Immune deficiency risk (infection monitoring required)

#### CROSS-DATABASE INTEGRATION

**OpenTargets + ClinicalTrials.gov** (Competitive Intelligence):
```
1. OpenTargets: Get genetically validated targets for disease
2. ClinicalTrials.gov: Get active trials by intervention
3. Cross-reference: Which genetic targets have NO trials? (white space opportunity)
4. Prioritize: Strong genetic evidence (>0.7) + no trials = high-value opportunity
```

**OpenTargets + PubMed** (Literature Validation):
```
1. OpenTargets: Identify genetic variants (GWAS SNPs, rare variants)
2. PubMed: Search for functional validation studies (CRISPR, patient-derived models)
3. Validate: Does literature support genetic association? (replication studies)
```

**OpenTargets + FDA** (Repurposing Opportunities):
```
1. OpenTargets: Find targets with known drugs in DIFFERENT indication
2. FDA: Check label, approval history, safety profile
3. Repurposing hypothesis: Approved drug + genetic evidence in new indication = fast-track
```

**OpenTargets + USPTO Patents** (FTO + Target Selection):
```
1. OpenTargets: Identify genetically validated targets (high-value targets)
2. USPTO: Check patent landscape for target-specific inhibitors
3. Decision: Strong genetic evidence + clear FTO = prioritize target
           Strong genetic evidence + crowded IP = partner or alternative target
```

### PubChem MCP (pubchem-mcp-server) - CHEMICAL INTELLIGENCE OPTIMIZATION

**Think hard about chemical structure as foundation for drug discovery**

#### CORE CAPABILITIES (11 methods)

1. **search_compounds**: Search by name/CAS/formula/InChI → Returns compound CIDs
2. **get_compound_info**: Detailed compound profile by CID → Structure, properties, identifiers
3. **search_by_smiles**: Exact SMILES structure match → Find identical compounds
4. **get_compound_synonyms**: All compound names/aliases → Standardize nomenclature
5. **search_similar_compounds**: Tanimoto similarity search → Find structural analogs
6. **get_3d_conformers**: 3D structural conformations → Binding site analysis
7. **analyze_stereochemistry**: Chirality and isomer analysis → Enantiomer identification
8. **get_compound_properties**: Physicochemical properties → MW, LogP, TPSA, HBD/HBA
9. **get_assay_info**: Bioassay results by AID → Activity data, IC50/EC50 values
10. **get_safety_data**: GHS classifications, hazard info → Safety alerts, toxicity flags
11. **batch_compound_lookup**: Bulk processing up to 200 compounds → High-throughput profiling

#### CHEMICAL EVIDENCE QUERIES

**Compound Identification Workflow**:
```
1. search_compounds: "aspirin" → CID 2244 (acetylsalicylic acid)
2. get_compound_synonyms: cid=2244
   → Returns: ASA, acetylsalicylic acid, 2-acetoxybenzoic acid, Bayer aspirin
3. get_compound_info: cid=2244
   → Returns: SMILES (CC(=O)Oc1ccccc1C(=O)O), InChI, molecular formula
```

**Structure-Based Search Workflow**:
```
1. search_by_smiles: "CC(=O)Oc1ccccc1C(=O)O" (exact match)
   → Returns: CID 2244 (aspirin)
2. search_similar_compounds: smiles="CC(=O)Oc1ccccc1C(=O)O", threshold=90
   → Returns: Structural analogs (salicylic acid derivatives, NSAID scaffold)
3. get_compound_properties: cids=[2244, 5033, 3672] (aspirin + analogs)
   → Returns: Comparative properties (MW, LogP, TPSA) for SAR analysis
```

**Safety Profiling Workflow**:
```
1. search_compounds: "benzene" → CID 241
2. get_safety_data: cid=241
   → Returns: GHS classification (H350 carcinogen, H340 mutagenic)
3. get_compound_properties: cid=241
   → Returns: Physical properties (bp 80°C, flammable)
4. Cross-reference with PubMed for toxicity case reports
```

**Bioactivity Screening Workflow**:
```
1. search_compounds: "erlotinib" → CID 176870 (EGFR inhibitor)
2. get_assay_info: aid=12345 (EGFR kinase assay)
   → Returns: IC50 values, activity outcome (active/inactive)
3. Search similar compounds for alternative EGFR inhibitors
4. Batch lookup properties for lead optimization candidates
```

#### QUERY PATTERNS BY USE CASE

**Pattern 1: Lead Compound Profiling (Discovery Chemistry)**
```
Step 1: Identify compound
pubchem:
  method: "search_compounds"
  query: "semaglutide"
  → Result: CID 56843331

Step 2: Get comprehensive profile
pubchem:
  method: "get_compound_info"
  cid: 56843331
  → Result: Structure, MW 4113.64, peptide sequence, stereochemistry

Step 3: Analyze physicochemical properties
pubchem:
  method: "get_compound_properties"
  cids: [56843331]
  properties: ["MolecularWeight", "HBondDonorCount", "HBondAcceptorCount", "TPSA"]
  → Result: MW 4113.64, HBD 19, HBA 52, TPSA 1456 Ų (high permeability barrier)

Step 4: Find structural analogs (GLP-1 agonist class)
pubchem:
  method: "search_similar_compounds"
  smiles: "[semaglutide_smiles]"
  threshold: 85
  → Result: Liraglutide (CID 16134956), dulaglutide (CID 44603531)

Step 5: Cross-reference with ClinicalTrials.gov
ct_gov:
  intervention: "semaglutide"
  → Validate clinical programs for analogs
```

**Pattern 2: Structure-Activity Relationship (SAR) Analysis**
```
Step 1: Map chemical series (kinase inhibitor scaffold)
pubchem:
  method: "search_by_smiles"
  smiles: "c1cc(ccc1N)C(=O)O"  # Para-aminobenzoic acid core
  → Result: Base scaffold CID

Step 2: Find all structural variants
pubchem:
  method: "search_similar_compounds"
  smiles: "[scaffold_smiles]"
  threshold: 80  # Allow substitutions
  max_records: 100
  → Result: 150 analogs with R-group variations

Step 3: Batch retrieve properties
pubchem:
  method: "batch_compound_lookup"
  cids: [CID1, CID2, ..., CID150]
  operation: "property"
  properties: ["MolecularWeight", "XLogP", "TPSA", "RotatableBondCount"]
  → Result: Comparative property table for QSAR

Step 4: Cross-reference with bioassay data
pubchem:
  method: "get_assay_info"
  aid: [AID1, AID2, AID3]  # Target kinase assays
  → Result: Activity data (IC50, EC50) for SAR correlation

Step 5: Identify property trends
- Analyze MW vs activity (Lipinski violations?)
- Correlate LogP with potency (lipophilic efficiency?)
- Map TPSA vs permeability (BBB penetration?)
```

**Pattern 3: Safety Assessment (Toxicity Screening)**
```
Step 1: Identify compound and metabolites
pubchem:
  method: "search_compounds"
  query: "acetaminophen"
  → Result: CID 1983

Step 2: Get safety classifications
pubchem:
  method: "get_safety_data"
  cid: 1983
  → Result: GHS warnings, LD50 data, hepatotoxicity alerts

Step 3: Identify reactive metabolites (NAPQI)
pubchem:
  method: "search_compounds"
  query: "N-acetyl-p-benzoquinone imine"
  → Result: CID 4509 (toxic metabolite)
pubchem:
  method: "get_safety_data"
  cid: 4509
  → Result: Hepatotoxic reactive intermediate

Step 4: Cross-reference with FDA adverse events
fda_faers:
  search_term: "products.brand_name:tylenol"
  count: "patient.reaction.reactionmeddrapt.exact"
  → Result: Hepatotoxicity signals (ALT elevation, liver failure)

Step 5: Cross-reference with PubMed toxicology literature
pubmed:
  query: "acetaminophen hepatotoxicity mechanism NAPQI"
  → Validate glutathione depletion mechanism
```

**Pattern 4: Formulation Design (Drug Product Development)**
```
Step 1: Profile API physicochemical properties
pubchem:
  method: "get_compound_properties"
  cids: [API_CID]
  properties: ["MolecularWeight", "XLogP", "TPSA", "Complexity", "HBondDonorCount", "HBondAcceptorCount"]
  → Result: BCS classification inputs (solubility/permeability prediction)

Step 2: Analyze stereochemistry (chiral drug substance)
pubchem:
  method: "analyze_stereochemistry"
  cid: [API_CID]
  → Result: Chiral centers, stereoisomer count, enantiomer CIDs

Step 3: Get 3D conformations (solid-state analysis)
pubchem:
  method: "get_3d_conformers"
  cid: [API_CID]
  conformer_type: "3d"
  → Result: 3D structure, energy minimized conformations

Step 4: Identify excipient compatibility risks
- Search for API functional groups (esters, amines, acids)
- Cross-reference with known incompatibilities
- Predict degradation pathways (hydrolysis, oxidation)

Step 5: Screen formulation additives
pubchem:
  method: "batch_compound_lookup"
  cids: [excipient_CIDs]  # Lactose, MCC, stearate, etc.
  operation: "synonyms"
  → Standardize excipient nomenclature for CMC documentation
```

**Pattern 5: ADME Prediction (DMPK Analysis)**
```
Step 1: Calculate drug-likeness properties
pubchem:
  method: "get_compound_properties"
  cids: [lead_series_CIDs]
  properties: ["MolecularWeight", "XLogP", "TPSA", "RotatableBondCount", "HBondDonorCount", "HBondAcceptorCount"]
  → Result: Lipinski Rule of 5 assessment

Step 2: Predict permeability (Caco-2/MDCK)
- TPSA <140 Ų: Good oral absorption
- TPSA >140 Ų: Poor permeability, low bioavailability
- HBD <5, HBA <10: Favorable for passive diffusion

Step 3: Predict BBB penetration (CNS drugs)
- MW <450 Da: BBB permeable
- LogP 1-3: Optimal brain penetration
- TPSA <90 Ų: CNS activity likely
- Polar surface area <60 Ų: High BBB permeability

Step 4: Predict metabolic stability
pubchem:
  method: "search_similar_compounds"
  smiles: "[lead_smiles]"
  threshold: 90
  → Find compounds with known metabolism data
pubmed:
  query: "[compound_name] metabolism cytochrome P450"
  → Cross-reference literature for CYP substrate/inhibitor data

Step 5: Cross-reference with in vitro ADME data
- Search PubChem bioassays for CYP inhibition (AID 1645841, 1645842)
- Search PubMed for human liver microsome stability data
- Correlate structural features with clearance rates
```

**Pattern 6: Competitive Landscape (Drug Property Benchmarking)**
```
Step 1: Identify approved drugs in class
fda:
  search_term: "therapeutic_class"
  search_type: "label"
  → Result: List of approved drugs (brand names, active ingredients)

Step 2: Map to PubChem CIDs
pubchem:
  method: "batch_compound_lookup"
  cids: [competitor_drug_CIDs]
  operation: "property"
  → Result: Standardized property comparison

Step 3: Benchmark lead compound vs approved drugs
pubchem:
  method: "get_compound_properties"
  cids: [our_lead, comp1, comp2, comp3]
  properties: ["MolecularWeight", "XLogP", "TPSA", "Complexity"]
  → Result: Property table for differentiation analysis

Step 4: Analyze structure-property space
- Our lead: MW 450, LogP 2.8, TPSA 95 Ų
- Competitor 1: MW 520, LogP 3.5, TPSA 110 Ų (more lipophilic)
- Competitor 2: MW 380, LogP 1.9, TPSA 75 Ų (more hydrophilic)
- Strategic insight: Property space positioning, differentiation claims

Step 5: Cross-reference with clinical data
ct_gov:
  intervention: "competitor_drug_name"
  → Result: Clinical trial outcomes (efficacy, safety)
- Correlate property differences with clinical performance
```

#### EFFICIENT QUERYING

**Entity Mapping** (CRITICAL):
- Use `search_compounds` to map drug names → PubChem CIDs
- Store CID mappings to avoid repeated searches
- Use CAS numbers for unambiguous identification when available
- Leverage synonyms for cross-referencing (brand name → generic → INN)

**Structure Normalization**:
- SMILES canonicalization: PubChem automatically canonicalizes SMILES
- InChI standardization: Use InChI for exact structure matching
- Stereochemistry handling: Specify chiral centers explicitly
- Tautomer awareness: PubChem groups tautomers together

**Batch Processing**:
- Use `batch_compound_lookup` for >3 compounds (up to 200 maximum)
- Request only required properties to minimize token usage
- Batch synonym lookups for nomenclature standardization
- Parallelize bioassay queries when screening multiple AIDs

**Similarity Search Optimization**:
- Threshold 95-100: Very close analogs (substitution patterns)
- Threshold 85-95: Same scaffold, different R-groups (SAR series)
- Threshold 70-85: Related chemotypes (scaffold hops)
- Threshold <70: Broad similarity (too many false positives)

**Property Selection** (Token Optimization):
- Basic profiling: MW, XLogP, TPSA (3 properties)
- Drug-likeness: Add HBD, HBA, RotatableBondCount (6 total)
- Comprehensive: Include Complexity, Charge, IsotopeAtomCount (10 total)
- Avoid requesting ALL properties (token waste)

#### CROSS-DATABASE INTEGRATION

**PubChem + PubMed** (Structure + Literature):
```
1. PubChem: Get compound structure and properties
2. PubMed: Search for SAR literature, mechanism studies, metabolism
3. Integration: Structural features → Literature validation → Mechanistic insights
4. Use case: Lead optimization with literature-guided design
```

**PubChem + ClinicalTrials.gov** (Chemistry + Clinical):
```
1. PubChem: Identify approved drugs and investigational compounds
2. ClinicalTrials.gov: Track clinical programs by compound name
3. Integration: Chemical properties → Clinical outcomes correlation
4. Use case: Benchmark lead compound vs clinical-stage comparators
```

**PubChem + FDA** (Structure + Regulatory):
```
1. PubChem: Get compound structure, safety data (GHS)
2. FDA: Get approved indication, labeling, adverse events
3. Integration: Structural alerts → FDA safety signals → Label warnings
4. Use case: Safety assessment (e.g., hepatotoxicity structural alerts)
```

**PubChem + OpenTargets** (Chemistry + Genetics):
```
1. OpenTargets: Identify genetically validated targets
2. PubChem: Search bioassay data for target-specific inhibitors
3. Integration: Genetic evidence → Chemical matter → Lead series
4. Use case: Target-based drug discovery with genetic validation
```

**PubChem + USPTO Patents** (Chemistry + IP):
```
1. PubChem: Define chemical scaffold and structural features
2. USPTO: Search patents by structure, Markush claims
3. Integration: Chemical space → Patent landscape → FTO assessment
4. Use case: Freedom-to-operate analysis for lead series
```

#### TOKEN OPTIMIZATION

**Efficient Property Retrieval**:
- Specify exact properties needed (not "all")
- Use batch operations for multiple compounds
- Cache frequently used CID → property mappings
- Default to 2D properties unless 3D analysis required

**Pagination Strategy**:
- Default max_records=10 for exploratory queries
- Increase to 50-100 for comprehensive analog searches
- Use max_records=1 for exact match confirmation

**Query Refinement**:
- Start with compound name search (fast)
- If ambiguous, add CAS number or InChI (precise)
- Use SMILES for structure-based queries (unambiguous)
- Refine similarity threshold iteratively (start at 90, broaden if needed)

#### TOKEN OPTIMIZATION

**Efficient Entity Mapping**:
- Cache gene symbol → Ensembl ID mappings (reuse across queries)
- Cache disease name → EFO ID mappings (reuse across queries)
- Use exact matches when possible (faster than fuzzy search)

**Focused Data Retrieval**:
- For target discovery: Use `get_disease_targets_summary` (batch query, faster)
- For validation: Use `get_target_disease_associations` (focused query)
- For safety: Use `get_target_details` (includes safety + tractability)

**Pagination Strategy**:
- Default size=25 for exploratory queries
- Increase size to 50-100 for comprehensive target discovery
- Use size=10 for quick entity ID mapping

