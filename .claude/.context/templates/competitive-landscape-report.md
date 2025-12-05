# Competitive Landscape Report Template

Use this template when generating competitive landscape analysis reports.

## Frontmatter

```markdown
---
title: {Therapeutic Area} Competitive Landscape Analysis
date: YYYY-MM-DD
analyst: competitive-landscape-analyst
therapeutic_area: {therapeutic_area}
company_focus: {company_name} (optional)

# SOURCE METADATA (REQUIRED - See Source Citation Standards below)
data_sources_mcp_verified:
  - {skill_name}: {data_description} (source: {SourceName}, date: YYYY-MM-DD)
  - Example: glp1_trials: 156 Phase 3 trials (source: ClinicalTrials.gov, date: 2025-12-03)
  - Example: glp1_fda_drugs: 21 approved drugs (source: FDA Drug Database, date: 2025-12-03)

data_sources_internal_knowledge:
  - {knowledge_type}: {description} [internal source/estimation basis]
  - Example: Market projections: $100B by 2030 [estimated from industry analyst consensus]
  - Example: Clinical efficacy data: Weight loss percentages [from published literature, not real-time]

source_validation:
  mcp_verified_claims: {count}  # Claims backed by MCP data
  analytical_insights: {count}   # Claims derived from MCP data
  internal_knowledge: {count}    # Claims from training data (target: <20% of total)

data_freshness:
  - ClinicalTrials.gov: YYYY-MM-DD
  - FDA Database: YYYY-MM-DD
  - PubMed: YYYY-MM-DD (if used)
  - SEC EDGAR: YYYY-MM-DD (if used)

keywords: [keyword1, keyword2, keyword3]
---
```

## Source Citation Standards (MANDATORY)

Every report must follow these citation principles to meet verification thresholds:

### Citation Thresholds (ENFORCED BY VERIFICATION)

**CRITICAL REQUIREMENTS**:
- **MCP-Verified Data**: >70% of major claims (target: >80%)
- **Internal Knowledge**: <20% of major claims (target: <10%)
- **Published Literature**: >10% when available
- **Analytical Insights**: Derived from MCP data, not internal knowledge

**What This Means**:
- For every 10 major claims in your report, at least 7 must cite MCP data
- No more than 2 claims can use internal knowledge/estimates
- Before using internal knowledge, ask: "Can I get this from an MCP server?"

### Inline Citation Formats

**1. MCP-Verified Data** (PREFERRED - Use for >70% of claims):
```markdown
"156 Phase 3 GLP-1 trials are currently recruiting (**source**: ClinicalTrials.gov, 2025-12-03)"
"21 GLP-1 drugs approved by FDA (**source**: FDA Drug Database, 2025-12-03)"
"Amgen leads with 89 active trials (**source**: ClinicalTrials.gov, 2025-12-03)"
```

**2. Published Literature** (HIGH VALUE):
```markdown
"Tirzepatide demonstrated 22.5% mean weight loss (Jastreboff et al., NEJM 2022, PMID: 35658024)"
"Semaglutide reduced MACE by 20% in cardiovascular outcomes trial (SELECT trial, 2023)"
```

**3. Analytical Insight** (DERIVED from MCP data, not internal knowledge):
```markdown
"High attrition expected given 60% historical completion rate [analysis based on ClinicalTrials.gov data]"
"Market concentration increasing with top 3 sponsors controlling 68% of trials [calculated from ClinicalTrials.gov data]"
```

**4. Internal Knowledge** (MINIMIZE - <20% total, <10% preferred):
```markdown
"GLP-1 market projected at $100B by 2030 [estimated from industry analyst consensus, not real-time MCP data]"
"Typical Phase 3 development costs $50-100M [industry benchmark, not company-specific MCP data]"
```

**IMPORTANT**: Always try to find MCP data first. Only use internal knowledge when MCP servers don't have the data.

### Tables and Figures

Always include source in caption or footer:

**Example with footer**:
```markdown
**Table 1**: GLP-1 Trial Distribution by Phase
| Phase | Count | % |
|-------|-------|---|
| Phase 3 | 156 | 68% |
| Phase 4 | 73 | 32% |

**Source**: ClinicalTrials.gov (query date: 2025-12-03)
```

**Example with source column**:
```markdown
| Drug | Efficacy | Source |
|------|----------|--------|
| Tirzepatide | 22.5% weight loss | Jastreboff et al., NEJM 2022, PMID: 35658024 |
| Semaglutide | 14.9% weight loss | Wilding et al., NEJM 2021, PMID: 33567185 |
```

### Verification Workflow (MANDATORY POST-GENERATION)

After generating report, you MUST verify it meets standards:

**Step 1: Save Report**
```bash
# Save to reports/competitive-landscape/YYYY-MM-DD_{topic}.md
```

**Step 2: Run Verification**
```bash
python3 .claude/tools/verification/verify_report_attribution.py \
  --report reports/competitive-landscape/YYYY-MM-DD_{topic}.md \
  --json
```

**Step 3: Parse Results**

**✅ PASS** (valid: true):
```json
{
  "valid": true,
  "metrics": {
    "total_citations": 87,
    "mcp_verified": 68,
    "internal_knowledge": 12,
    "mcp_percentage": 78.2,
    "internal_percentage": 13.8
  }
}
```
→ Report meets standards, return to user

**❌ FAIL** (valid: false):
```json
{
  "valid": false,
  "errors": ["Internal knowledge usage (45.2%) exceeds 20% threshold"],
  "metrics": {
    "total_citations": 62,
    "mcp_verified": 23,
    "internal_knowledge": 28,
    "internal_percentage": 45.2
  }
}
```
→ Fix errors, re-verify (max 2 iterations)

**Step 4: Fix Common Failures**

**Problem**: Internal knowledge >20%
**Solution**:
1. Identify claims using `[estimated from...]` or `[internal knowledge]`
2. Check if MCP data available (run additional skills if needed)
3. Replace internal knowledge claims with MCP-verified data
4. Re-run verification

**Problem**: Missing frontmatter sections
**Solution**:
1. Add `data_sources_mcp_verified` section with all skills used
2. Add `data_sources_internal_knowledge` section with any estimates
3. Add `source_validation` metrics
4. Re-run verification

**DO NOT** return unverified reports to user. Verification is part of the report generation process.

## Report Structure

### 1. Executive Summary (Required)

**Length**: 2-3 paragraphs maximum

**Content**:
- Market stage assessment (emerging/growth/mature)
- Key competitive dynamics summary
- Top 3 strategic implications
- Critical decision point or timeline

**Example** (with proper inline citations):
```markdown
# Executive Summary

The KRAS inhibitor market represents a highly dynamic emerging-to-growth stage therapeutic area with significant strategic opportunity. The stark contrast between 363 active clinical trials (**source**: ClinicalTrials.gov, 2025-12-03) and only 2 FDA-approved drugs (**source**: FDA Drug Database, 2025-12-03) signals intense competition, high unmet need, and substantial development risk—but also indicates the market is far from saturated.

Key competitive dynamics include: (1) First-mover advantage window still open for non-G12C mutations—87% of KRAS mutations lack approved therapy [analysis based on FDA and ClinicalTrials.gov data], (2) High competitive intensity with 45 unique sponsors across 363 trials (**source**: ClinicalTrials.gov, 2025-12-03), (3) High attrition expected based on 60% historical completion rate [analysis based on ClinicalTrials.gov trial status data]. Strategic imperative: Act within 6-12 months to secure position in high-value mutations (G12D priority) before clinical data maturation drives valuations to prohibitive levels [estimated timing from industry M&A patterns].

Critical window: 2025-2027 for market entry before consolidation [estimated from trial timelines and approval predictions].
```

**Note**: This example shows 70% MCP-verified data (5 MCP citations) vs 30% internal knowledge (2 estimates), meeting the >70% threshold.

### 2. Data Summary (Required)

**Purpose**: Provide transparency on data collection and validate conclusions

**Format**: Structured tables or bullet points

**Example**:
```markdown
# Data Summary

## Clinical Trials Pipeline
- **Total trials**: 363 KRAS inhibitor trials (ClinicalTrials.gov)
- **Data source**: `get_kras_inhibitor_trials` skill
- **Collection date**: 2025-11-19

**Trial Status Breakdown**:
| Status | Count | % of Total |
|--------|-------|------------|
| Recruiting | 145 | 40% |
| Completed | 89 | 25% |
| Active, not recruiting | 67 | 18% |
| Terminated | 34 | 9% |
| Other | 28 | 8% |

## FDA Approved Drugs
- **Total approved**: 2 KRAS G12C inhibitors
- **Data source**: `get_kras_inhibitor_fda_drugs` skill
- **Drugs identified**:
  1. LUMAKRAS (Sotorasib) - Amgen
  2. KRAZATI (Adagrasib) - Mirati Therapeutics
```

### 3. Market Analysis (Required)

**Sections**:
- Market maturity assessment
- Competitive positioning of key players
- Pipeline density analysis
- White space identification

**Key Questions to Answer**:
- What stage is the market? (Emerging/Growth/Mature)
- Who are the leaders and fast followers?
- Where are the gaps (indications, mutations, modalities)?
- What does trial volume tell us about competitive intensity?

### 4. Pipeline Dynamics (Required)

**Sections**:
- Trial success/failure patterns
- Differentiation strategies observed
- Combination therapy trends
- Geographic expansion patterns

**Include**:
- Specific trial examples (NCT IDs, companies, designs)
- Attrition analysis (terminated trials, reasons)
- Emerging trends (biomarkers, endpoints, patient selection)

### 5. Strategic Implications for BD (Required)

**Sections**:
- Partnership opportunities (early vs late stage)
- Acquisition target characteristics
- Risk assessment (technical, clinical, commercial)
- Market entry timing and barriers

**Format**: Actionable insights with decision criteria

**Example**:
```markdown
## Strategic Implications for BD

### Partnership Opportunities

**Early-Stage Partnerships (Preclinical - Phase 1)**
- **Target Profile**: Novel mutations (G12D, G12V, pan-KRAS)
- **Structure**: Option agreements, co-development with milestones
- **Rationale**: Lower upfront cost, multiple shots on goal
- **Risk**: High attrition (70-80%), longer time to revenue

**Late-Stage Partnerships (Phase 2/3)**
- **Target Profile**: Demonstrated efficacy in underserved mutations
- **Structure**: Co-commercialization, regional licensing
- **Rationale**: De-risked efficacy, near-term revenue
- **Risk**: Higher upfront costs, limited differentiation window
```

### 6. Actionable Recommendations (Required)

**Format**: Prioritized list (Top 3-5 priorities)

**Each recommendation must include**:
- Priority level (Critical/High/Medium)
- Specific actions to take
- Timeline for action
- Decision criteria
- Success metrics

**Example**:
```markdown
# Actionable Recommendations

## Priority 1: INITIATE AGGRESSIVE G12D INHIBITOR SCOUTING (CRITICAL)

**Rationale**:
- Largest unmet need (40% pancreatic, 15% CRC = ~60,000 US patients/year)
- No approved therapies (blue ocean opportunity)
- First-to-market advantage substantial

**Actions**:
1. Identify all Phase 1/2 G12D programs globally (estimate: 10-15 programs)
2. Request meetings with top 3 programs within 60 days
3. Prepare term sheets for Phase 2 co-development or acquisition

**Decision Criteria**:
- ORR >30% in Phase 1 data
- Safety profile compatible with combinations
- Composition of matter patents extending beyond 2035

**Timeline**: Secure deal within 6-9 months

**Success Metrics**:
- Deal signed by Q2 2026
- Program enters Phase 3 by Q4 2026
```

### 7. Trial Monitoring Priorities (Optional)

**Purpose**: Specific trials/programs to track for competitive intelligence

**Format**: Tiered priority list

**Example**:
```markdown
# Trial Monitoring Priorities

## Tier 1 (Weekly Updates)
- NCT12345678: Company X G12D inhibitor Phase 2 (interim data expected Q2 2026)
- NCT87654321: Company Y pan-KRAS Phase 1 (PoC data expected Q3 2026)

## Tier 2 (Monthly Updates)
- All G12V inhibitor trials
- KRAS + checkpoint inhibitor combinations

## Tier 3 (Quarterly Updates)
- G12C "me-too" programs
- KRAS resistance mechanism studies
```

### 8. Appendix (Optional)

**Sections**:
- Methodology notes
- Data limitations
- Assumptions made
- Source skills and collection dates
- Glossary of terms

---

## Template Variables

When generating report, replace these placeholders:

| Variable | Description | Example |
|----------|-------------|---------|
| `{therapeutic_area}` | Disease/drug class/mechanism | "KRAS inhibitor", "GLP-1 agonist" |
| `{company_name}` | Specific company if focus | "Pfizer", "Merck" (optional) |
| `{skill_name_1}` | Data collection skill used | "get_kras_inhibitor_trials" |
| `{data_count}` | Number of records collected | "363 trials", "2 approved drugs" |
| `YYYY-MM-DD` | Report generation date | "2025-11-19" |
| `{keyword1}` | Search/topic keywords | "KRAS", "G12C", "targeted therapy" |

---

## Report Quality Checklist

### Content Requirements
- [ ] Executive summary is concise (2-3 paragraphs max)
- [ ] Data sources are clearly documented with counts
- [ ] At least 3-5 actionable recommendations provided
- [ ] Each recommendation has timeline and decision criteria
- [ ] Specific examples cited (trial NCT IDs, company names, drug names)
- [ ] White space opportunities clearly identified
- [ ] Risk factors assessed (technical, clinical, commercial)
- [ ] Frontmatter metadata complete
- [ ] Report saved to `reports/competitive-landscape/YYYY-MM-DD_{therapeutic_area_slug}.md`

### Source Attribution Requirements (MANDATORY)
- [ ] Frontmatter includes complete `data_sources_mcp_verified` section
- [ ] Frontmatter includes `data_sources_internal_knowledge` section (if any)
- [ ] Frontmatter includes `source_validation` metrics (mcp_verified_claims, internal_knowledge counts)
- [ ] >70% of major claims have inline citations with MCP sources
- [ ] All tables and figures have source attribution (footer or column)
- [ ] Internal knowledge usage <20% (count internal knowledge vs total claims)
- [ ] MCP sources include query dates (YYYY-MM-DD format)
- [ ] Published literature includes PMID or DOI when cited

### Verification Requirements (MANDATORY)
- [ ] Report saved to filesystem before verification
- [ ] Verification tool executed: `python3 .claude/tools/verification/verify_report_attribution.py --report {path} --json`
- [ ] Verification result: `valid: true` (no errors)
- [ ] Verification metrics reviewed: `internal_percentage < 20%`, `mcp_percentage > 70%`
- [ ] If verification failed: Errors fixed and re-verified (max 2 iterations)
- [ ] Verification passing before returning report to user

**CRITICAL**: Do NOT return report to user until verification passes. Verification is not optional.

---

## Word Count Guidelines

**Philosophy**: Complete but concise. Avoid verbose explanations and bloated content.

| Section | Target Length | Focus |
|---------|---------------|-------|
| Executive Summary | 150-300 words | Key insights only |
| Data Summary | 100-200 words | Tables preferred over text |
| Market Analysis | 400-600 words | Bullet points, not paragraphs |
| Pipeline Dynamics | 400-600 words | Highlight key patterns |
| Strategic Implications | 500-800 words | Actionable insights |
| Recommendations | 300-500 words | Prioritized list format |
| **Total Report** | **1500-2500 words** | **Complete, not comprehensive** |

**Maximum**: 3000 words for complex multi-therapeutic analyses

**Style Requirements**:
- Use bullet points over paragraphs
- Tables over text where possible
- One sentence per insight (no elaboration unless critical)
- No redundant context or background filler
- Assume reader has domain expertise
- Lead with conclusions, not explanations

---

## Output Format

Reports should be valid markdown with:
- YAML frontmatter
- GitHub-flavored markdown tables
- Clear heading hierarchy (H1 → H2 → H3)
- Code blocks for examples where appropriate
- Bulleted/numbered lists for readability
- **Bold** for emphasis on key terms
- `inline code` for skill names, trial IDs, drug names
