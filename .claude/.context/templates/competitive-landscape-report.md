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
data_sources:
  - {skill_name_1}: {data_count} records
  - {skill_name_2}: {data_count} records
keywords: [keyword1, keyword2, keyword3]
---
```

## Report Structure

### 1. Executive Summary (Required)

**Length**: 2-3 paragraphs maximum

**Content**:
- Market stage assessment (emerging/growth/mature)
- Key competitive dynamics summary
- Top 3 strategic implications
- Critical decision point or timeline

**Example**:
```markdown
# Executive Summary

The KRAS inhibitor market represents a highly dynamic emerging-to-growth stage therapeutic area with significant strategic opportunity. The stark contrast between 363 active clinical trials and only 2 FDA-approved drugs signals intense competition, high unmet need, and substantial development risk—but also indicates the market is far from saturated.

Key competitive dynamics include: (1) First-mover advantage window still open for non-G12C mutations, (2) 87% of KRAS mutations lack approved therapy, (3) High attrition expected (60-70% of 363 trials likely to fail). Strategic imperative: Act within 6-12 months to secure position in high-value mutations (G12D priority) before clinical data maturation drives valuations to prohibitive levels.

Critical window: 2025-2027 for market entry before consolidation.
```

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

Before finalizing report, ensure:

- [ ] Executive summary is concise (2-3 paragraphs max)
- [ ] Data sources are clearly documented with counts
- [ ] At least 3-5 actionable recommendations provided
- [ ] Each recommendation has timeline and decision criteria
- [ ] Specific examples cited (trial NCT IDs, company names, drug names)
- [ ] White space opportunities clearly identified
- [ ] Risk factors assessed (technical, clinical, commercial)
- [ ] Frontmatter metadata complete
- [ ] Report saved to `reports/competitive-landscape/YYYY-MM-DD_{therapeutic_area_slug}.md`

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
