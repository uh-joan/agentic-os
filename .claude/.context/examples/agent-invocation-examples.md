# Agent Invocation Examples with Source Attribution

## Purpose

This document provides example prompts for invoking agents in the Pharmaceutical Research Intelligence Platform, demonstrating proper source attribution expectations and patterns.

---

## Infrastructure Agent: pharma-search-specialist

### Pattern: Direct Data Collection

The pharma-search-specialist agent creates reusable skills that return MCP-verified data with source metadata.

#### Example 1: Clinical Trials Query

**User Prompt**:
```
Get all Phase 3 GLP-1 receptor agonist trials for obesity
```

**Main Agent Flow**:
1. Runs strategy check: `python3 .claude/tools/skill_discovery/strategy.py --skill "glp1_obesity_phase3_trials" --therapeutic-area "GLP-1" --data-type "trials" --servers "ct_gov_mcp" --json`
2. If REUSE: Executes existing skill
3. If CREATE: Invokes pharma-search-specialist

**pharma-search-specialist Output**:
- Returns skill code with source_metadata
- Skill passes verification automatically
- Main agent saves skill to `.claude/skills/`

**Expected Result**:
```python
{
    'data': {
        'total_trials': 156,
        'trials_summary': [...]
    },
    'source_metadata': {
        'source': 'ClinicalTrials.gov',
        'mcp_server': 'ct_gov_mcp',
        'query_date': '2025-12-03',
        'query_params': {
            'term': 'GLP-1 receptor agonist',
            'condition': 'obesity',
            'phase': 'PHASE3'
        },
        'data_count': 156,
        'data_type': 'clinical_trials'
    },
    'summary': 'Found 156 Phase 3 GLP-1 trials (source: ClinicalTrials.gov, 2025-12-03)'
}
```

#### Example 2: FDA Drug Query

**User Prompt**:
```
Which GLP-1 drugs are FDA approved for weight management?
```

**Main Agent Flow**:
1. Strategy check identifies reuse opportunity or creates new skill
2. Invokes pharma-search-specialist if needed

**Expected Result**:
```python
{
    'data': {
        'approved_drugs': [
            {'drug_name': 'Wegovy', 'approval_date': '2021-06-04'},
            {'drug_name': 'Saxenda', 'approval_date': '2014-12-23'}
        ],
        'total_count': 2
    },
    'source_metadata': {
        'source': 'FDA Drug Database',
        'mcp_server': 'fda_mcp',
        'query_date': '2025-12-03',
        'query_params': {
            'search_terms': ['GLP-1', 'weight management'],
            'search_type': 'label'
        },
        'data_count': 2,
        'data_type': 'fda_approved_drugs'
    },
    'summary': 'Found 2 FDA-approved GLP-1 drugs for weight management (source: FDA Drug Database, 2025-12-03)'
}
```

#### Example 3: Multi-Server Query

**User Prompt**:
```
Get all anti-amyloid antibody publications from 2020-2024
```

**Main Agent Flow**:
1. Strategy check identifies PubMed query with temporal chunking
2. Invokes pharma-search-specialist with reference skill pattern

**Expected Result**:
```python
{
    'data': {
        'publications': [...],
        'total_count': 487,
        'temporal_breakdown': {
            '2020': 89,
            '2021': 102,
            '2022': 118,
            '2023': 95,
            '2024': 83
        }
    },
    'source_metadata': {
        'source': 'PubMed',
        'mcp_server': 'pubmed_mcp',
        'query_date': '2025-12-03',
        'query_params': {
            'keywords': 'anti-amyloid antibody',
            'start_date': '2020/01/01',
            'end_date': '2024/12/31',
            'num_results': 500
        },
        'data_count': 487,
        'data_type': 'publications'
    },
    'summary': 'Found 487 anti-amyloid antibody publications (source: PubMed, 2025-12-03)'
}
```

---

## Strategic Agent: competitive-landscape-analyst

### Pattern: Metadata-Driven Data Collection → Strategic Analysis

The competitive-landscape-analyst requires MCP-verified data and produces reports with proper source attribution.

#### Example 1: Full Competitive Landscape Analysis

**User Prompt**:
```
@agent-competitive-landscape-analyst "Analyze the KRAS inhibitor competitive landscape"
```

**Main Agent Flow**:

1. **Read Metadata**: Extract data_requirements from agent
   ```yaml
   data_requirements:
     always:
       - type: clinical_trials
         pattern: get_{therapeutic_area}_trials
       - type: approved_drugs
         pattern: get_{therapeutic_area}_fda_drugs
   ```

2. **Infer Parameters**:
   - therapeutic_area = "KRAS inhibitor"
   - Required skills: get_kras_inhibitor_trials, get_kras_inhibitor_fda_drugs

3. **Strategy Check & Execute**:
   ```bash
   # For each required skill
   python3 .claude/tools/skill_discovery/strategy.py \
     --skill "get_kras_inhibitor_trials" \
     --therapeutic-area "KRAS inhibitor" \
     --data-type "trials" \
     --servers "ct_gov_mcp" \
     --json
   ```

4. **Collect Data**:
   - Execute get_kras_inhibitor_trials → 363 trials
   - Execute get_kras_inhibitor_fda_drugs → 2 drugs

5. **Data Summary** (shown to user):
   ```
   Data Collection Complete:
   ✓ Clinical Trials: 363 KRAS inhibitor trials found (source: ClinicalTrials.gov, 2025-12-03)
   ✓ FDA Approved Drugs: 2 approved drugs (source: FDA Drug Database, 2025-12-03)

   Invoking competitive-landscape-analyst with collected data...
   ```

6. **Invoke Strategic Agent**:
   ```
   Analyze KRAS inhibitor competitive landscape.

   Data available:
   1. Clinical Trials: [363 trials from get_kras_inhibitor_trials]
   2. FDA Approved Drugs: [2 drugs from get_kras_inhibitor_fda_drugs]

   Provide strategic analysis including competitive positioning, market entry timing,
   partnership opportunities, and actionable recommendations.
   ```

7. **Agent Returns Report** (with inline citations):
   ```markdown
   ---
   title: KRAS Inhibitor Competitive Landscape
   date: 2025-12-03
   analyst: competitive-landscape-analyst
   therapeutic_area: KRAS inhibitor
   data_sources_mcp_verified:
     - get_kras_inhibitor_trials: 363 clinical trials (source: ClinicalTrials.gov, date: 2025-12-03)
     - get_kras_inhibitor_fda_drugs: 2 FDA-approved drugs (source: FDA Drug Database, date: 2025-12-03)

   data_sources_internal_knowledge:
     - Market size estimates: $5-8B by 2030 [estimated from industry analyst consensus]

   source_validation:
     mcp_verified_claims: 87
     analytical_insights: 34
     internal_knowledge: 8
   ---

   # Executive Summary
   - 363 active trials vs 2 approved drugs indicate nascent but rapidly evolving market (**source**: ClinicalTrials.gov, 2025-12-03)
   - High competitive intensity: 45 unique sponsors across 363 trials [analysis based on ClinicalTrials.gov data]
   - Strategic window closing: 87% of mutations lack therapy, but 156 Phase 3 trials underway (**source**: ClinicalTrials.gov, 2025-12-03)
   - Entry timing critical: 6-12 month window for G12D positioning before market consolidation

   # Market Overview
   - **Current approvals**: 2 drugs (LUMAKRAS for G12C, KRAZATI for G12C) (**source**: FDA Drug Database, 2025-12-03)
   - **Pipeline intensity**: 363 trials across all phases (**source**: ClinicalTrials.gov, 2025-12-03)
     - Phase 1: 141 trials (39%)
     - Phase 2: 166 trials (46%)
     - Phase 3: 56 trials (15%)
   - **Mutation coverage**: G12C (2 approved), G12D (23 trials), G12V (18 trials) (**source**: ClinicalTrials.gov, 2025-12-03)

   # Competitive Positioning
   [Analysis with proper citations...]

   # Actionable Recommendations
   1. **Accelerate G12D program** → Timeline: 6 months → Success Metric: IND filing Q2 2026
   2. **Secure combination partnerships** → Timeline: 3 months → Success Metric: 2 partnerships signed
   3. **Build clinical infrastructure** → Timeline: 4 months → Success Metric: 15 trial sites activated
   ```

8. **Report Verification** (agent runs automatically):
   ```bash
   python3 .claude/tools/verification/verify_report_attribution.py \
     --report reports/competitive-landscape/2025-12-03_kras-inhibitor-landscape.md \
     --json
   ```

   Expected result:
   ```json
   {
     "valid": true,
     "metrics": {
       "total_citations": 129,
       "mcp_verified": 87,
       "internal_knowledge": 8,
       "mcp_percentage": 67.4,
       "internal_percentage": 6.2
     }
   }
   ```

9. **Save Report**:
   - Write to `reports/competitive-landscape/2025-12-03_kras-inhibitor-landscape.md`
   - Return summary to user

#### Example 2: Company-Specific Analysis

**User Prompt**:
```
@agent-competitive-landscape-analyst "What is Pfizer's obesity pipeline?"
```

**Main Agent Flow**:

1. **Infer Parameters**:
   - therapeutic_area = "obesity"
   - company = "Pfizer"
   - Triggers: company_name_in_query → get_pfizer_trials

2. **Strategy Check & Execute**:
   - get_obesity_trials (always)
   - get_obesity_fda_drugs (always)
   - get_pfizer_trials (contextual - company mentioned)

3. **Data Summary**:
   ```
   Data Collection Complete:
   ✓ Obesity Trials: 1,247 active trials (source: ClinicalTrials.gov, 2025-12-03)
   ✓ Obesity FDA Drugs: 7 approved drugs (source: FDA Drug Database, 2025-12-03)
   ✓ Pfizer Trials: 89 Pfizer-sponsored trials (source: ClinicalTrials.gov, 2025-12-03)

   Invoking competitive-landscape-analyst with collected data...
   ```

4. **Report Output** (with proper citations):
   ```markdown
   # Pfizer Obesity Pipeline Analysis

   ## Pipeline Summary
   - **Total Pfizer obesity trials**: 89 trials (**source**: ClinicalTrials.gov, 2025-12-03)
   - **Phase breakdown**:
     - Phase 1: 23 trials
     - Phase 2: 41 trials
     - Phase 3: 25 trials
   - **Market context**: 1,247 total obesity trials indicate high competitive intensity (**source**: ClinicalTrials.gov, 2025-12-03)

   ## Competitive Position
   - Pfizer represents 7.1% of obesity trial activity [calculated from ClinicalTrials.gov data]
   - 7 FDA-approved obesity drugs on market (**source**: FDA Drug Database, 2025-12-03)
   [...]
   ```

#### Example 3: IP-Focused Analysis (Contextual Data Trigger)

**User Prompt**:
```
@agent-competitive-landscape-analyst "Analyze GLP-1 competitive landscape with focus on IP and patent position"
```

**Main Agent Flow**:

1. **Infer Parameters**:
   - therapeutic_area = "GLP-1"
   - Triggers detected: keywords("IP", "patent") → get_glp1_patents (contextual)

2. **Strategy Check & Execute**:
   - get_glp1_trials (always)
   - get_glp1_fda_drugs (always)
   - get_glp1_patents (contextual - triggered by keywords)

3. **Data Summary**:
   ```
   Data Collection Complete:
   ✓ GLP-1 Trials: 2,156 active trials (source: ClinicalTrials.gov, 2025-12-03)
   ✓ GLP-1 FDA Drugs: 21 approved drugs (source: FDA Drug Database, 2025-12-03)
   ✓ GLP-1 Patents: 487 active patents (source: USPTO, 2025-12-03)

   Invoking competitive-landscape-analyst with collected data...
   ```

4. **Report Output** (with patent citations):
   ```markdown
   # GLP-1 Competitive Landscape: IP Analysis

   ## Market Overview
   - 2,156 active trials demonstrate high competitive intensity (**source**: ClinicalTrials.gov, 2025-12-03)
   - 21 FDA-approved drugs with established market (**source**: FDA Drug Database, 2025-12-03)
   - 487 active patents covering compositions, formulations, indications (**source**: USPTO, 2025-12-03)

   ## IP Landscape
   - **Core composition patents**: 127 patents on GLP-1 peptide structures (**source**: USPTO, 2025-12-03)
   - **Formulation patents**: 203 patents on delivery systems (**source**: USPTO, 2025-12-03)
   - **Indication patents**: 157 patents on specific therapeutic uses (**source**: USPTO, 2025-12-03)
   [...]
   ```

---

## Anti-Patterns: What NOT to Do

### ❌ Bad Example 1: No Source Citations

**Bad Report**:
```markdown
# GLP-1 Market Analysis

The GLP-1 market is worth $50B annually and growing at 25% CAGR.
There are over 100 drugs in development with 15 in Phase 3.
Semaglutide shows 20% weight loss in clinical trials.
```

**Why Bad**: Zero source citations. Cannot verify any claims. Violates <20% internal knowledge threshold.

**Good Report**:
```markdown
# GLP-1 Market Analysis

- **Market size**: $50B annually (estimated, 2024) [internal knowledge from industry analyst consensus]
- **Pipeline**: 156 drugs in development across all phases (**source**: ClinicalTrials.gov, 2025-12-03)
  - Phase 3: 56 trials (**source**: ClinicalTrials.gov, 2025-12-03)
- **Semaglutide efficacy**: 20.9% mean weight loss at 68 weeks (Wilding et al., NEJM 2021, PMID: 33567185)
```

### ❌ Bad Example 2: No Data Collection for Strategic Agent

**Bad Invocation**:
```
@agent-competitive-landscape-analyst "Tell me about KRAS inhibitors"
```

**Why Bad**: Strategic agent invoked without data collection. Agent will use >80% internal knowledge.

**Good Invocation**:
```
# Step 1: Strategy check (automatic)
python3 .claude/tools/skill_discovery/strategy.py --skill "get_kras_inhibitor_trials" ...

# Step 2: Execute skills
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/kras-inhibitor-trials/scripts/get_kras_inhibitor_trials.py
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/kras-inhibitor-fda-drugs/scripts/get_kras_inhibitor_fda_drugs.py

# Step 3: Invoke strategic agent WITH data
@agent-competitive-landscape-analyst "Analyze KRAS inhibitors"
[Data automatically provided to agent]
```

### ❌ Bad Example 3: Missing Verification

**Bad Workflow**:
```
1. Generate report
2. Return to user (DONE)
```

**Why Bad**: No verification that report meets <20% internal knowledge threshold.

**Good Workflow**:
```
1. Generate report
2. Save report to reports/competitive-landscape/YYYY-MM-DD_topic.md
3. Run verification tool:
   python3 .claude/tools/verification/verify_report_attribution.py --report ... --json
4. Parse results:
   - If valid: Return to user
   - If invalid: Fix errors, re-verify (max 2 iterations)
5. Return verified report to user
```

---

## Quick Reference

### Infrastructure Agent (pharma-search-specialist)
- **Purpose**: Create reusable data collection skills
- **Input**: User query for specific data
- **Output**: Skill code with source_metadata + summary
- **Verification**: Automatic (verify_source_attribution.py)
- **Source Type**: MCP-Verified Data (100%)

### Strategic Agent (competitive-landscape-analyst)
- **Purpose**: Strategic analysis and synthesis
- **Input**: User query + MCP-verified data (automatically collected)
- **Output**: Report with inline citations + frontmatter source metadata
- **Verification**: Manual (verify_report_attribution.py) before returning report
- **Source Mix**: >70% MCP-Verified, <20% Internal Knowledge

---

## Verification Thresholds Summary

| Metric | Skills | Reports |
|--------|--------|---------|
| **MCP-Verified Data** | 100% (required) | >70% (target >80%) |
| **Analytical Insights** | 0% (return raw data) | 20-30% (derived from MCP) |
| **Internal Knowledge** | 0% (not allowed) | <20% (target <10%) |
| **Published Literature** | 0% (use PubMed skill) | >10% (when available) |

---

## Common Questions

**Q: When should I invoke pharma-search-specialist vs using existing skills?**
A: Always run strategy check first (`strategy.py`). It will tell you if skill exists (REUSE) or needs creation (CREATE).

**Q: How do I know which skills the strategic agent needs?**
A: Read agent metadata (`data_requirements` section). Main agent automatically collects these.

**Q: What if verification fails on a report?**
A: Iterate max 2 times: identify claims using internal knowledge → run skills to get MCP data → replace claims → re-verify.

**Q: Can I skip verification for quick analyses?**
A: No. Verification is mandatory. It ensures trustability and compliance.

**Q: What if MCP data doesn't exist for a claim?**
A: Use internal knowledge and explicitly label it: `[estimated from industry consensus]`. Keep under 20% total.

---

*Document created: 2025-12-03*
*Status: Phase 4.3 - Agent Invocation Examples Complete*
