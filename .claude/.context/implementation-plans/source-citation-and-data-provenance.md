# Source Citation and Data Provenance Architecture

**Date**: 2025-12-03
**Priority**: CRITICAL - Foundation for trustability and scientific rigor
**Impact**: All outputs (reports, skills, agent responses)

---

## Executive Summary

This document defines a comprehensive architecture for **source citation and data provenance tracking** across the entire Agentic OS platform. The goal is to make every output—reports, agent responses, skill results—fully traceable to authoritative data sources, with clear distinction between MCP-verified data and analytical insights.

**Core Principle**: **ALWAYS cite sources**. Every claim must be traceable to either:
1. **MCP-verified data** (clinicaltrials.gov, FDA, PubMed, etc.) - preferred
2. **Analytical insights** (derived from MCP data) - clearly labeled
3. **Internal knowledge** (model training data) - minimized and explicitly labeled

**What this fixes**:
- ❌ Current: Mixed MCP data + internal knowledge, inconsistent citations
- ✅ Future: Every claim sourced, MCP data preferred, internal knowledge explicit

---

## Architecture Overview

### Four-Layer Source Citation System

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Verification (Source validation)                  │
│  - Verify every claim has source                            │
│  - Check source validity (MCP server + date)                │
│  - Flag unsourced claims                                    │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Reports (Structured output with citations)        │
│  - Frontmatter: Complete data sources                       │
│  - Inline citations: Every major claim                      │
│  - Clear distinction: MCP data vs analysis vs internal      │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Agents (Instruction to cite sources)              │
│  - Always cite sources inline                               │
│  - Prefer MCP data over internal knowledge                  │
│  - Label internal knowledge explicitly                      │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Skills (Return source metadata)                   │
│  - Every skill returns source_metadata dict                 │
│  - Includes: source, mcp_server, query_date, params, count  │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Skills (Data Collection with Source Metadata)

### Current State

Skills return data without source metadata:

```python
# CURRENT (glp1-fda-drugs example)
return {
    'drugs': [...],
    'total_count': 21,
    'summary': "..."
}
# ❌ NO source metadata - where did this come from?
```

### Future State (Required)

Every skill MUST return source metadata:

```python
# REQUIRED FORMAT
return {
    'data': {
        'drugs': [...],
        'total_count': 21
    },
    'source_metadata': {
        'source': 'FDA Drug Database',           # Human-readable source name
        'mcp_server': 'fda_mcp',                # MCP server identifier
        'query_date': '2025-12-03',             # ISO 8601 date
        'query_params': {                        # Query parameters used
            'search_term': 'GLP-1 receptor agonist',
            'search_type': 'general',
            'limit': 100
        },
        'data_count': 21,                        # Number of records
        'data_type': 'fda_approved_drugs',      # Type of data collected
        'query_url': 'https://api.fda.gov/...' # Optional: API endpoint
    },
    'summary': "..."  # Human-readable summary (unchanged)
}
```

### Source Metadata Standard

**Required fields**:
- `source` (string): Human-readable source name for citations
  - Examples: "ClinicalTrials.gov", "FDA Drug Database", "PubMed", "SEC EDGAR"
- `mcp_server` (string): MCP server identifier
  - Examples: "ct_gov_mcp", "fda_mcp", "pubmed_mcp"
- `query_date` (string): ISO 8601 date when query executed
  - Format: "YYYY-MM-DD"
- `query_params` (dict): Parameters used in query (for reproducibility)
- `data_count` (int): Number of records returned
- `data_type` (string): Type of data (for categorization)
  - Examples: "clinical_trials", "fda_approved_drugs", "publications", "patents"

**Optional fields**:
- `query_url` (string): API endpoint URL (if available)
- `data_version` (string): Data version/snapshot identifier
- `temporal_coverage` (string): Temporal range of data
  - Example: "2020-01-01 to 2025-12-03"

### Implementation Pattern

**All skills must follow this pattern**:

```python
def get_example_skill():
    """Example skill with source metadata pattern.

    Returns:
        dict: Contains 'data', 'source_metadata', and 'summary'
    """
    # 1. Execute MCP query
    result = mcp_function(params)

    # 2. Process data
    processed_data = process(result)

    # 3. Create summary
    summary = format_summary(processed_data)

    # 4. REQUIRED: Return with source metadata
    return {
        'data': processed_data,
        'source_metadata': {
            'source': 'ClinicalTrials.gov',
            'mcp_server': 'ct_gov_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {
                'term': 'GLP-1',
                'phase': 'Phase 3'
            },
            'data_count': len(processed_data),
            'data_type': 'clinical_trials'
        },
        'summary': summary
    }
```

### Migration Strategy for Existing Skills

**All 98 existing skills must be updated**. Use this checklist:

- [ ] Add `source_metadata` to return dict
- [ ] Wrap existing return data in `data` key
- [ ] Populate required fields (source, mcp_server, query_date, query_params, data_count, data_type)
- [ ] Update SKILL.md with new return format
- [ ] Update skill tests to validate source_metadata presence

**Migration script**: `.claude/tools/migrate_skills_source_metadata.py` (to be created)

---

## Layer 2: Agents (Instruction to Cite Sources)

### pharma-search-specialist.md Updates

**Add to agent instructions** (near top of agent definition):

```markdown
## CRITICAL: Source Citation Requirements

You MUST follow these source citation principles:

### 1. Always Return Source Metadata
Every skill you create MUST include source_metadata in the return dict:
- source: Human-readable source name (e.g., "ClinicalTrials.gov")
- mcp_server: Server identifier (e.g., "ct_gov_mcp")
- query_date: ISO 8601 date
- query_params: Query parameters used
- data_count: Number of records
- data_type: Type of data

### 2. Prefer MCP Data Over Internal Knowledge
When creating skills:
- ALWAYS query MCP servers for data (preferred)
- NEVER infer or estimate data from internal knowledge
- If MCP query fails, explicitly state data unavailable

### 3. Code Must Include Source Attribution
Generated skill code should include source comments:

```python
# Data source: ClinicalTrials.gov via ct_gov_mcp
# Query date: 2025-12-03
# Query: term="GLP-1", phase="Phase 3"
result = search(term="GLP-1", phase="Phase 3")
```

### 4. Summary Must Cite Source
When returning summary to user, always state source:

GOOD: "Found 156 GLP-1 Phase 3 trials (source: ClinicalTrials.gov, query date: 2025-12-03)"
BAD: "Found 156 GLP-1 Phase 3 trials" (no source!)
```

### competitive-landscape-analyst.md Updates

**Add source citation section**:

```markdown
## CRITICAL: Source Citation in Reports

You MUST follow these citation principles:

### 1. Distinguish Data Types
Every claim in your report falls into one of three categories:

**Category A: MCP-Verified Data** (PREFERRED)
- Data retrieved from MCP servers (CT.gov, FDA, PubMed, etc.)
- Citation format: `(source: ClinicalTrials.gov)`
- Example: "156 Phase 3 trials found (source: ClinicalTrials.gov)"

**Category B: Analytical Insights** (DERIVED FROM MCP DATA)
- Analysis, calculations, or synthesis from MCP data
- Citation format: `[analysis based on ClinicalTrials.gov data]`
- Example: "High attrition expected based on 60% trial completion rate [analysis based on ClinicalTrials.gov data]"

**Category C: Internal Knowledge** (MINIMIZE)
- Industry knowledge, market estimates, projections from training data
- Citation format: `[internal knowledge]` or `[estimated]`
- Example: "Market projected at $100B by 2030 [estimated from industry consensus]"
- USE SPARINGLY - Try to find MCP data first

### 2. Always Try MCP Data First
Before using internal knowledge, ask yourself:
- Can I get this from an MCP server? (trials, FDA approvals, publications, financials, patents)
- Can I derive this from MCP data? (calculate from trial counts, approval dates, etc.)
- Only if answer is NO, use internal knowledge and label it

### 3. Frontmatter Source Metadata
Every report must have complete data sources in frontmatter:

```yaml
data_sources_mcp_verified:
  - skill_name: Data description (source: SourceName, date: YYYY-MM-DD)
  - glp1_trials: 156 Phase 3 trials (source: ClinicalTrials.gov, date: 2025-12-03)
  - glp1_fda_drugs: 21 approved drugs (source: FDA Drug Database, date: 2025-12-03)

data_sources_internal_knowledge:
  - Market projections ($100B by 2030) [estimated from industry analyst consensus]
  - Clinical efficacy comparisons [from published literature, not real-time]
  - Pricing estimates [from public disclosures and industry sources]
```

### 4. Inline Citations
Major claims must have inline citations:

GOOD:
- "156 Phase 3 GLP-1 trials active (source: ClinicalTrials.gov)"
- "Tirzepatide shows 22% weight loss [Jastreboff et al., NEJM 2022, PMID: 35658024]"
- "Market estimated at $100B by 2030 [internal projection based on industry consensus]"

BAD:
- "156 Phase 3 GLP-1 trials active" (no source!)
- "Tirzepatide shows 22% weight loss" (no citation!)
- "Market will be $100B by 2030" (sounds like fact, but it's projection!)

### 5. Tables Must Have Source Column
When presenting data tables, include source column or footer:

| Drug | Efficacy | Source |
|------|----------|--------|
| Tirzepatide | 22% weight loss | Jastreboff et al., NEJM 2022 |
| Semaglutide | 15% weight loss | STEP-1 trial |

Or use table footer:
**Source**: FDA Drug Database (query date: 2025-12-03)
```

---

## Layer 3: Reports (Structured Output with Citations)

### Report Template Updates

**Update**: `.claude/.context/templates/competitive-landscape-report.md`

**Add to frontmatter section**:

```yaml
---
title: {Therapeutic Area} Competitive Landscape Analysis
date: YYYY-MM-DD
analyst: competitive-landscape-analyst
therapeutic_area: {therapeutic_area}

# SOURCE METADATA (REQUIRED)
data_sources_mcp_verified:
  - {skill_name}: {data_description} (source: {SourceName}, date: YYYY-MM-DD)
  - Example: glp1_trials: 156 Phase 3 trials (source: ClinicalTrials.gov, date: 2025-12-03)

data_sources_internal_knowledge:
  - {knowledge_type}: {description} [internal source/estimation basis]
  - Example: Market projections: $100B by 2030 [estimated from industry analyst consensus]

source_validation:
  mcp_verified_claims: {count}  # Claims backed by MCP data
  analytical_insights: {count}   # Claims derived from MCP data
  internal_knowledge: {count}    # Claims from training data (should be minimal)

data_freshness:
  - ClinicalTrials.gov: YYYY-MM-DD
  - FDA Database: YYYY-MM-DD
  - PubMed: YYYY-MM-DD
---
```

**Add inline citation requirements**:

```markdown
## Inline Citation Standards

### Format 1: MCP-Verified Data
Use parenthetical source citation immediately after claim:

"156 Phase 3 GLP-1 trials are currently recruiting (source: ClinicalTrials.gov, 2025-12-03)"

### Format 2: Published Literature
Use author-year-PMID format:

"Tirzepatide demonstrated 22% weight loss (Jastreboff et al., NEJM 2022, PMID: 35658024)"

### Format 3: Analytical Insight
Use bracketed analysis label:

"High attrition expected based on 60% completion rate [analysis based on ClinicalTrials.gov data]"

### Format 4: Internal Knowledge (Minimize)
Use bracketed internal label:

"Market projected at $100B by 2030 [estimated from industry consensus, not real-time MCP data]"

### Tables and Figures
Always include source in caption or footer:

**Table 1**: GLP-1 Trial Distribution by Phase
| Phase | Count | % |
|-------|-------|---|
| Phase 3 | 156 | 68% |
| Phase 4 | 73 | 32% |

**Source**: ClinicalTrials.gov (query date: 2025-12-03)
```

### Citation Checklist (Add to Template)

**Before finalizing report, verify**:

- [ ] Frontmatter has complete `data_sources_mcp_verified` list
- [ ] Frontmatter has `data_sources_internal_knowledge` list (if any)
- [ ] Every major claim (>80% of sentences) has inline citation
- [ ] Tables/figures have source attribution
- [ ] Internal knowledge usage is <20% of claims
- [ ] MCP data sources have query dates
- [ ] Published literature has PMID or DOI
- [ ] Report distinguishes MCP data vs analysis vs internal knowledge

---

## Layer 4: Verification (Source Validation)

### New Verification Check: Source Attribution

**File**: `.claude/tools/verification/verify_source_attribution.py`

**Purpose**: Validate that skills and reports have proper source attribution

**Usage**:
```bash
# Verify skill return format
python3 .claude/tools/verification/verify_source_attribution.py \
  --type skill \
  --execution-output "$(cat skill_output.json)" \
  --json

# Verify report citations
python3 .claude/tools/verification/verify_source_attribution.py \
  --type report \
  --file reports/competitive-landscape/2025-12-03_glp1-landscape.md \
  --json
```

**Checks for Skills**:
1. ✓ Return dict has `source_metadata` key
2. ✓ `source_metadata` has required fields (source, mcp_server, query_date, query_params, data_count, data_type)
3. ✓ `query_date` is valid ISO 8601 format
4. ✓ `data_count` matches actual data length
5. ✓ Summary mentions source

**Checks for Reports**:
1. ✓ Frontmatter has `data_sources_mcp_verified`
2. ✓ Each data source has format: `skill: description (source: Name, date: YYYY-MM-DD)`
3. ✓ Report body has inline citations (heuristic: >70% of major claims cited)
4. ✓ Internal knowledge usage is minimal (<20% of claims)
5. ✓ Tables/figures have source attribution
6. ✓ Source dates are within reasonable timeframe (not outdated)

**Output**:
```json
{
  "valid": true|false,
  "checks": {
    "source_metadata_present": true|false,
    "required_fields_complete": true|false,
    "inline_citations_present": true|false,
    "internal_knowledge_minimal": true|false,
    "tables_sourced": true|false
  },
  "issues": [
    "Missing source metadata in return dict",
    "Frontmatter lacks data_sources_mcp_verified",
    "Internal knowledge usage high (45% of claims)"
  ],
  "recommendations": [
    "Add source_metadata to skill return",
    "Reduce internal knowledge usage by querying MCP servers"
  ]
}
```

### Integration with pharma-search-specialist

**The pharma-search-specialist agent MUST**:
1. Generate skills with `source_metadata` in return dict
2. Run `verify_source_attribution.py` on generated skill
3. Self-correct if verification fails (max 3 attempts)
4. Only return verified, properly sourced skill code

**Add to pharma-search-specialist workflow**:

```markdown
## Step 5: Verify Source Attribution (MANDATORY)

After generating and testing the skill, you MUST verify source attribution:

```bash
python3 .claude/tools/verification/verify_source_attribution.py \
  --type skill \
  --execution-output "$(python3 .claude/skills/{skill_name}/scripts/{skill_function}.py)" \
  --json
```

If verification fails:
1. Review issues in verification output
2. Fix skill code (add source_metadata, correct format, etc.)
3. Re-execute and re-verify (max 3 attempts)
4. Only return skill to main agent if verification passes

This ensures every skill is properly sourced before being added to the skills library.
```

---

## Documentation Updates Required

### Priority 1: Core Architecture (CLAUDE.md)

**File**: `.claude/CLAUDE.md`

**Section to add** (after "Design Principles"):

```markdown
## Source Citation and Data Provenance

**Principle**: Every output must be traceable to authoritative data sources.

### Source Hierarchy (Trustability Order)

1. **MCP-Verified Data** (MOST TRUSTABLE)
   - Data retrieved from MCP servers (ClinicalTrials.gov, FDA, PubMed, SEC, WHO, CDC, etc.)
   - Always includes: source name, query date, query parameters
   - Citation format: `(source: ClinicalTrials.gov, 2025-12-03)`
   - Use: Preferred for ALL factual claims

2. **Published Literature** (HIGH TRUSTABILITY)
   - Peer-reviewed publications from PubMed
   - Always includes: Author, journal, year, PMID/DOI
   - Citation format: `(Jastreboff et al., NEJM 2022, PMID: 35658024)`
   - Use: Clinical efficacy, trial results, scientific evidence

3. **Analytical Insights** (DERIVED, MODERATE TRUSTABILITY)
   - Calculations, synthesis, or analysis derived from MCP data
   - Citation format: `[analysis based on ClinicalTrials.gov data]`
   - Use: Patterns, trends, comparisons synthesized from MCP data

4. **Internal Knowledge** (LOWEST TRUSTABILITY - MINIMIZE)
   - Industry consensus, market projections, estimates from training data
   - Citation format: `[estimated from industry consensus]` or `[internal knowledge]`
   - Use: ONLY when MCP data unavailable, always explicitly labeled
   - Constraint: Should be <20% of claims in any report

### Source Attribution Standards

**Skills**:
- Every skill returns `source_metadata` dict
- Includes: source, mcp_server, query_date, query_params, data_count, data_type
- Verified by `verify_source_attribution.py`

**Agents**:
- pharma-search-specialist: Generates skills with source metadata
- competitive-landscape-analyst: Cites sources inline in reports
- All agents: Prefer MCP data over internal knowledge

**Reports**:
- Frontmatter: Complete `data_sources_mcp_verified` and `data_sources_internal_knowledge`
- Inline citations: Every major claim (>70%) cited
- Tables/figures: Source attribution in caption or footer
- Source validation checklist before publication

### Benefits

✅ **Trustability**: Every claim traceable to authoritative source
✅ **Reproducibility**: Query parameters enable re-execution
✅ **Transparency**: Clear distinction MCP data vs internal knowledge
✅ **Scientific rigor**: Follows academic citation standards
✅ **Compliance**: Audit trail for regulatory/legal requirements
```

### Priority 2: Agent Definitions

**Files to update**:
1. `.claude/agents/pharma-search-specialist.md`
2. `.claude/agents/competitive-landscape-analyst.md`

**Changes**: Add source citation requirements sections (detailed in Layer 2 above)

### Priority 3: Templates

**Files to update**:
1. `.claude/.context/templates/competitive-landscape-report.md`
2. `.claude/.context/templates/skill-frontmatter-template.yaml`

**Changes**: Add source metadata requirements (detailed in Layer 3 above)

### Priority 4: Code Examples

**Files to update**:
1. `.claude/.context/code-examples/skills_library_pattern.md`

**Add section**:

```markdown
## Source Metadata Pattern

Every skill MUST return source metadata:

```python
def example_skill():
    # Query MCP server
    result = mcp_function(params)

    # Process data
    data = process(result)

    # REQUIRED: Return with source metadata
    return {
        'data': data,
        'source_metadata': {
            'source': 'ClinicalTrials.gov',
            'mcp_server': 'ct_gov_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {'term': 'GLP-1', 'phase': 'Phase 3'},
            'data_count': len(data),
            'data_type': 'clinical_trials'
        },
        'summary': format_summary(data)
    }
```

Benefits:
- Traceability: Every data point has known origin
- Reproducibility: Query params enable re-execution
- Trustability: User knows exactly where data came from
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Establish standards and update documentation

**Tasks**:
1. ✅ Create this implementation plan
2. [ ] Update CLAUDE.md with source citation principles
3. [ ] Update pharma-search-specialist.md with source requirements
4. [ ] Update competitive-landscape-analyst.md with citation requirements
5. [ ] Update report templates with source metadata sections
6. [ ] Update code examples with source metadata patterns

**Deliverables**:
- Updated documentation (6 files)
- Source citation standards established

### Phase 2: Verification Infrastructure (Week 2)
**Goal**: Build tools to validate source attribution

**Tasks**:
1. [ ] Create `verify_source_attribution.py` script
2. [ ] Add skill validation checks (source_metadata presence, format)
3. [ ] Add report validation checks (frontmatter, inline citations)
4. [ ] Integrate with pharma-search-specialist workflow
5. [ ] Test verification on 5 sample skills and reports

**Deliverables**:
- `verify_source_attribution.py` (200-300 lines)
- Integration with pharma-search-specialist
- Test results showing validation works

### Phase 3: Skills Migration (Week 3-4)
**Goal**: Update existing skills to return source metadata

**Tasks**:
1. [ ] Create migration script `migrate_skills_source_metadata.py`
2. [ ] Audit all 98 skills for source metadata presence
3. [ ] Batch migrate skills by category:
   - Clinical trials skills (13 skills)
   - FDA drug skills (20 skills)
   - Financial skills (15 skills)
   - Patents skills (10 skills)
   - Publications skills (8 skills)
   - Disease/public health skills (12 skills)
   - Analytical skills (10 skills)
   - Specialized skills (10 skills)
4. [ ] Verify migrated skills with `verify_source_attribution.py`
5. [ ] Update index.json with source metadata capabilities

**Deliverables**:
- 98 skills updated with source_metadata
- Migration script
- Updated index.json

### Phase 4: Report Regeneration (Week 5)
**Goal**: Regenerate key reports with proper source attribution

**Tasks**:
1. [ ] Audit existing reports for source citation quality
2. [ ] Identify reports requiring regeneration (10-15 reports)
3. [ ] Regenerate reports with updated competitive-landscape-analyst
4. [ ] Verify reports with `verify_source_attribution.py`
5. [ ] Archive old reports to `/reports/archive/pre-source-citation/`

**Deliverables**:
- 10-15 regenerated reports with proper citations
- Archive of old reports
- Citation quality metrics (% claims cited)

### Phase 5: Validation and Rollout (Week 6)
**Goal**: Validate system and establish ongoing compliance

**Tasks**:
1. [ ] Run end-to-end tests (new query → skill creation → report generation)
2. [ ] Measure citation quality metrics:
   - % skills with source_metadata
   - % reports with frontmatter sources
   - % claims with inline citations
   - % internal knowledge usage
3. [ ] Create source citation dashboard (optional)
4. [ ] Document lessons learned
5. [ ] Establish ongoing compliance checks (pre-commit hooks, CI/CD)

**Deliverables**:
- Test results showing >95% compliance
- Citation quality metrics dashboard
- Lessons learned document
- Ongoing compliance process

---

## Success Metrics

### Quantitative Metrics

**Skills Library**:
- ✅ 100% of skills return `source_metadata` (98/98 skills)
- ✅ 100% of skills pass `verify_source_attribution.py` (98/98 skills)
- ✅ Average source metadata completeness: 100% (all required fields present)

**Reports**:
- ✅ 100% of reports have `data_sources_mcp_verified` in frontmatter
- ✅ >70% of major claims have inline citations
- ✅ <20% of claims use internal knowledge (preferably <10%)
- ✅ 100% of tables/figures have source attribution

**Agent Behavior**:
- ✅ pharma-search-specialist generates skills with source_metadata 100% of time
- ✅ competitive-landscape-analyst cites sources inline >90% of time
- ✅ Internal knowledge usage flagged and minimized

### Qualitative Metrics

**Trustability**:
- ✅ Every claim traceable to source
- ✅ User can reproduce queries
- ✅ Clear distinction MCP data vs internal knowledge

**Scientific Rigor**:
- ✅ Citation standards match academic publications
- ✅ Published literature includes PMID/DOI
- ✅ Analytical insights clearly labeled as derived

**User Experience**:
- ✅ Source attribution doesn't clutter readability
- ✅ Citations feel natural, not forced
- ✅ Frontmatter provides transparency without verbosity

---

## Examples: Before and After

### Example 1: Skill Return Format

**BEFORE** (No source metadata):
```python
return {
    'drugs': [
        {'brand_name': 'OZEMPIC', 'approval_date': '2017-12-05'},
        {'brand_name': 'WEGOVY', 'approval_date': '2021-06-04'}
    ],
    'total_count': 21,
    'summary': "Found 21 GLP-1 drugs"
}
# ❌ Where did this data come from? When was it queried?
```

**AFTER** (With source metadata):
```python
return {
    'data': {
        'drugs': [
            {'brand_name': 'OZEMPIC', 'approval_date': '2017-12-05'},
            {'brand_name': 'WEGOVY', 'approval_date': '2021-06-04'}
        ],
        'total_count': 21
    },
    'source_metadata': {
        'source': 'FDA Drug Database',
        'mcp_server': 'fda_mcp',
        'query_date': '2025-12-03',
        'query_params': {
            'search_term': 'GLP-1 receptor agonist',
            'search_type': 'general',
            'limit': 100
        },
        'data_count': 21,
        'data_type': 'fda_approved_drugs'
    },
    'summary': "Found 21 GLP-1 drugs (source: FDA Drug Database, 2025-12-03)"
}
# ✅ Clear source, reproducible, traceable
```

### Example 2: Report Inline Citations

**BEFORE** (No citations):
```markdown
The GLP-1 market is projected to reach $100B by 2030. Tirzepatide demonstrates
22% weight loss, superior to semaglutide's 15%. There are 156 Phase 3 trials
recruiting globally.
```
❌ Issues:
- No source for $100B projection (internal knowledge?)
- No citation for efficacy data (which trial?)
- No source for trial count (ClinicalTrials.gov?)

**AFTER** (Proper citations):
```markdown
The GLP-1 market is projected to reach $100B by 2030 [estimated from industry
analyst consensus, not real-time MCP data]. Tirzepatide demonstrates 22% weight
loss (Jastreboff et al., NEJM 2022, PMID: 35658024), superior to semaglutide's
15% (STEP-1 trial). There are 156 Phase 3 trials recruiting globally (source:
ClinicalTrials.gov, 2025-12-03).
```
✅ Benefits:
- Clear distinction: internal projection vs published data vs MCP data
- Reproducible: PMID and ClinicalTrials.gov query date provided
- Trustable: User knows exactly where each claim came from

### Example 3: Report Frontmatter

**BEFORE** (Incomplete):
```yaml
---
title: GLP-1 Competitive Landscape
date: 2025-12-03
analyst: competitive-landscape-analyst
---
```
❌ No source transparency

**AFTER** (Complete source metadata):
```yaml
---
title: GLP-1 Competitive Landscape
date: 2025-12-03
analyst: competitive-landscape-analyst
therapeutic_area: GLP-1 receptor agonists

data_sources_mcp_verified:
  - glp1_fda_drugs: 21 FDA-approved products (source: FDA Drug Database, date: 2025-12-03)
  - glp1_trials_phase3: 156 Phase 3 trials (source: ClinicalTrials.gov, date: 2025-12-03)
  - glp1_publications: 2 landmark publications verified (source: PubMed, date: 2025-12-03)
  - us_obesity_prevalence: 32.0% US adult obesity (source: CDC via Data Commons, date: 2021)

data_sources_internal_knowledge:
  - Market projections: $100B by 2030 [estimated from industry analyst consensus]
  - Clinical efficacy comparisons: Weight loss percentages [from published literature, not real-time]
  - BD valuations: Transaction ranges [from comparable deal precedents]

source_validation:
  mcp_verified_claims: 87
  analytical_insights: 34
  internal_knowledge: 12  # 9% of claims - below 20% threshold ✓

data_freshness:
  - ClinicalTrials.gov: 2025-12-03
  - FDA Database: 2025-12-03
  - PubMed: 2025-12-03
  - CDC (via Data Commons): 2021
---
```
✅ Benefits:
- Complete transparency on data sources
- Clear distinction MCP vs internal knowledge
- Metrics showing internal knowledge usage minimal
- Data freshness visible at a glance

---

## Open Questions and Decisions

### 1. Internal Knowledge Usage Threshold
**Question**: What's acceptable % of claims from internal knowledge?

**Options**:
- A: <10% (very strict, may be difficult for strategic insights)
- B: <20% (moderate, allows some analytical freedom)
- C: <30% (loose, may undermine trustability)

**Recommendation**: Start with <20%, tighten to <10% after Phase 3 migration

### 2. Citation Format Standardization
**Question**: Use academic citation format (Author, Year) or parenthetical source?

**Options**:
- A: Academic format: "Tirzepatide shows 22% weight loss (Jastreboff et al., 2022)"
- B: Parenthetical source: "Tirzepatide shows 22% weight loss (source: NEJM 2022, PMID: 35658024)"
- C: Hybrid: Use academic for publications, parenthetical for MCP data

**Recommendation**: Hybrid (Option C)
- Published literature: "Author et al., Journal Year, PMID: ###"
- MCP data: "(source: ClinicalTrials.gov, date: YYYY-MM-DD)"
- Internal knowledge: "[estimated from industry consensus]"

### 3. Source Metadata Storage
**Question**: Where to store source metadata for long-term traceability?

**Options**:
- A: Embedded in reports only (frontmatter)
- B: Separate source metadata log file (`.claude/.context/source-log.json`)
- C: Both (embedded + centralized log)

**Recommendation**: Option A (embedded in reports) for now
- Frontmatter provides transparency
- Reports are version controlled (git tracks history)
- Can add centralized log in Phase 5 if needed

### 4. Verification Enforcement
**Question**: Should source attribution verification be blocking (hard requirement)?

**Options**:
- A: Blocking: pharma-search-specialist CANNOT return skill without passing verification
- B: Warning: Verification warns but doesn't block (soft requirement)
- C: Optional: Verification is run manually (no enforcement)

**Recommendation**: Option A (blocking) for skills, Option B (warning) for reports
- Skills: Hard requirement (must pass verification to be added to library)
- Reports: Warning (allows analytical flexibility, but flags issues)

---

## References and Prior Art

### Industry Standards
- **PubMed Citation Format**: Author, Journal, Year, PMID
- **FDA Submissions**: Require source documentation for all claims
- **Academic Publications**: In-text citations + references section
- **SEC Filings**: Source attribution for financial data

### Internal References
- Anthropic: "Code Execution with MCP" pattern (98.7% context reduction)
- Anthropic: "Closing the Agentic Loop" (autonomous verification)
- CLAUDE.md: Current architecture documentation
- Skills library: 98 skills requiring migration

---

## Appendix: Implementation Checklist

### Documentation Updates
- [ ] `.claude/CLAUDE.md` - Add source citation principles section
- [ ] `.claude/agents/pharma-search-specialist.md` - Add source requirements
- [ ] `.claude/agents/competitive-landscape-analyst.md` - Add citation requirements
- [ ] `.claude/.context/templates/competitive-landscape-report.md` - Update frontmatter + citation standards
- [ ] `.claude/.context/templates/skill-frontmatter-template.yaml` - Add source_metadata return format
- [ ] `.claude/.context/code-examples/skills_library_pattern.md` - Add source metadata pattern

### Tool Creation
- [ ] `.claude/tools/verification/verify_source_attribution.py` - Source validation script
- [ ] `.claude/tools/migrate_skills_source_metadata.py` - Batch migration script
- [ ] Update `.claude/tools/init_skill.py` - Include source_metadata in template
- [ ] Update `.claude/tools/skill_discovery/strategy.py` - Check source_metadata in health checks

### Skills Migration (98 skills)
- [ ] Clinical trials skills (13)
- [ ] FDA drug skills (20)
- [ ] Financial skills (15)
- [ ] Patents skills (10)
- [ ] Publications skills (8)
- [ ] Disease/public health skills (12)
- [ ] Analytical skills (10)
- [ ] Specialized skills (10)

### Report Regeneration (10-15 reports)
- [ ] Identify reports requiring regeneration
- [ ] Regenerate with updated competitive-landscape-analyst
- [ ] Verify with `verify_source_attribution.py`
- [ ] Archive old reports

### Testing and Validation
- [ ] End-to-end test: User query → skill creation → report generation
- [ ] Measure citation quality metrics
- [ ] Verify 100% skills pass validation
- [ ] Verify >70% report claims cited
- [ ] Verify <20% internal knowledge usage

---

**Document Status**: Draft for review
**Next Steps**:
1. Review this plan with stakeholders
2. Approve source citation standards
3. Begin Phase 1 (documentation updates)
4. Establish timeline (6-week implementation)

**Contact**: For questions, see `.claude/CLAUDE.md` architecture documentation
