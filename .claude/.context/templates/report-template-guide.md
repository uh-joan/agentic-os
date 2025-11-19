# Report Template System

## Purpose

Report templates provide standardized structure for strategic analysis outputs. Templates ensure:

- ✅ Consistent formatting across analyses
- ✅ Complete coverage of required sections
- ✅ Actionable recommendations format
- ✅ Metadata for future reference
- ✅ Version-controlled strategic work products

## Available Templates

### `competitive-landscape-report.md`
- **Used by**: `competitive-landscape-analyst` agent
- **Purpose**: Competitive intelligence and pipeline analysis
- **Output location**: `reports/competitive-landscape/YYYY-MM-DD_{therapeutic_area}.md`
- **Key sections**: Executive summary, market analysis, pipeline dynamics, recommendations
- **Target length**: 4000-6000 words

### Future Templates (To Be Created)

- `clinical-strategy-report.md` - Clinical development strategy and trial design
- `regulatory-analysis-report.md` - Regulatory pathway and approval strategy
- `market-access-report.md` - Payer landscape and reimbursement strategy
- `publication-strategy-report.md` - Scientific communication and KOL engagement

## When to Use Templates

**Strategic agents should reference templates when**:
1. User explicitly requests formatted report
2. Analysis is substantial enough to warrant formal documentation (>2000 words)
3. Agent type has corresponding template available

**When NOT to use templates**:
- Quick queries requiring brief answers
- Exploratory questions without formal deliverable request
- Data collection without analysis

## Template Usage Pattern

### For Strategic Agents

1. **During analysis**: Keep template structure in mind but focus on content
2. **After analysis**: Format output following template sections
3. **Include frontmatter**: YAML metadata with data sources, date, etc.
4. **Return to main agent**: Main agent persists report using Write tool

### For Main Agent

1. **After strategic agent returns**: Format as markdown file
2. **Add frontmatter**: Populate YAML metadata
3. **Persist report**: `Write` tool → `reports/{agent_type}/YYYY-MM-DD_{topic_slug}.md`
4. **Confirm to user**: Show report path and summary

## Template Structure Standards

All templates should include:

### Required Sections
1. **YAML Frontmatter** - Metadata for future reference
2. **Executive Summary** - Concise (2-3 paragraphs) high-level takeaways
3. **Data Summary** - Transparency on sources and data quality
4. **Core Analysis** - Agent-specific analysis content
5. **Actionable Recommendations** - Prioritized list with timelines and criteria

### Optional Sections
- Appendix (methodology, limitations, glossary)
- Monitoring priorities (ongoing tracking items)
- Detailed examples (trial designs, financial models)

### Standard Elements
- **Tables**: Use GFM markdown tables for structured data
- **Lists**: Bulleted/numbered for readability
- **Emphasis**: **Bold** for key terms, *italic* for secondary emphasis
- **Code**: `inline code` for skill names, NCT IDs, drug names
- **Headings**: Clear hierarchy (H1 for title, H2 for main sections, H3 for subsections)

## Frontmatter Metadata Standards

All reports must include YAML frontmatter:

```yaml
---
title: {Full Report Title}
date: YYYY-MM-DD
analyst: {agent_name}
therapeutic_area: {therapeutic_area} (if applicable)
company_focus: {company_name} (optional)
data_sources:
  - {skill_name}: {data_count}
  - {skill_name}: {data_count}
keywords: [keyword1, keyword2, keyword3]
report_type: {competitive_landscape|clinical_strategy|regulatory_analysis|etc}
---
```

**Why metadata matters**:
- Future agents can parse and reference prior reports
- Git history shows evolution of analyses over time
- Search/discovery of relevant reports
- Audit trail for data sources used

## Report Persistence Pattern

### Step 1: Strategic Agent Returns Analysis
Agent returns markdown-formatted analysis following template structure.

### Step 2: Main Agent Formats Report
Main agent:
1. Adds YAML frontmatter with metadata
2. Validates all required sections present
3. Formats as proper markdown file

### Step 3: Main Agent Persists Report
```
reports/
├── competitive-landscape/
│   ├── 2025-11-19_kras-inhibitor-landscape.md
│   └── 2025-11-20_glp1-competitive-analysis.md
├── clinical-strategy/
│   └── 2025-11-18_nash-phase3-design.md
└── regulatory-analysis/
    └── 2025-11-17_rare-disease-pathway.md
```

### Step 4: Main Agent Confirms to User
```
✓ Report saved: reports/competitive-landscape/2025-11-19_kras-inhibitor-landscape.md

Summary: Comprehensive competitive landscape analysis of KRAS inhibitor
therapeutic area. Key finding: 363 trials vs 2 approved drugs indicates
emerging growth phase with significant opportunity in non-G12C mutations.

Top recommendation: Initiate aggressive G12D inhibitor scouting within 60 days.
```

## Quality Standards

Reports must meet these criteria:

### Content Quality
- [ ] Executive summary is actionable (not just descriptive)
- [ ] Data sources clearly documented with counts
- [ ] At least 3 actionable recommendations
- [ ] Each recommendation has timeline and decision criteria
- [ ] Specific examples cited (not vague generalities)
- [ ] Risk factors identified and assessed

### Format Quality
- [ ] Valid markdown (renders correctly)
- [ ] YAML frontmatter complete
- [ ] Heading hierarchy logical (no skipped levels)
- [ ] Tables formatted properly
- [ ] Code blocks used appropriately
- [ ] No broken links or references

### Completeness
- [ ] All required template sections present
- [ ] Data summary matches frontmatter metadata
- [ ] Recommendations are prioritized
- [ ] Report length appropriate for depth (>2000 words for strategic)

## Creating New Templates

When creating template for new agent type:

1. **Identify agent's core outputs**: What analyses does this agent produce?
2. **Define required sections**: What must every report include?
3. **Specify optional sections**: What's contextual?
4. **Document frontmatter**: What metadata is needed?
5. **Provide examples**: Show good report structure
6. **Set quality standards**: Word count, required elements, format rules
7. **Save to**: `.claude/.context/templates/{agent_type}-report.md`
8. **Update this guide**: Add to "Available Templates" section

## Template Discovery

**For agents**:
- Read `.claude/.context/templates/{agent_type}-report.md` for template
- Read this guide for general standards

**For humans**:
- Browse `.claude/.context/templates/` directory
- Read individual template files for agent-specific guidance

## Benefits of Template System

- ✅ **Consistency**: All reports follow same high-quality structure
- ✅ **Completeness**: Templates ensure no critical sections missed
- ✅ **Reusability**: Prior reports can be referenced by future agents
- ✅ **Professionalism**: Formatted reports ready for stakeholder sharing
- ✅ **Knowledge accumulation**: Git history shows strategic thinking evolution
- ✅ **Efficiency**: Agents know expected structure upfront

## Examples of Template Usage

### Example 1: Competitive Landscape Analysis
```
User: @agent-competitive-landscape-analyst "Analyze KRAS landscape"
  ↓
Main agent collects data (trials, FDA drugs)
  ↓
Main agent invokes competitive-landscape-analyst with data
  ↓
Strategic agent references competitive-landscape-report.md template
  ↓
Strategic agent returns formatted analysis following template
  ↓
Main agent adds frontmatter, persists to reports/competitive-landscape/
  ↓
User receives: summary + report path
```

### Example 2: Clinical Strategy (Future)
```
User: @agent-clinical-strategist "Design Phase 3 trial for rare disease"
  ↓
Strategic agent references clinical-strategy-report.md template
  ↓
Returns: Trial design recommendation following template structure
  ↓
Main agent persists to reports/clinical-strategy/
```

## Version Control

Reports are version controlled (not in .gitignore):

**Benefits**:
- Track evolution of strategic thinking
- Compare analyses over time (e.g., Q1 vs Q3 landscape)
- Audit trail for decisions made
- Share with team via git

**What NOT to commit**:
- Raw data dumps (use `data_dump/` folder, gitignored)
- Temporary analysis files
- Sensitive/confidential data

## Future Enhancements

Potential template system improvements:

1. **Automated frontmatter population** - Main agent auto-fills metadata
2. **Report comparison tool** - Diff two landscape reports to see changes
3. **Report search/index** - JSON index of all reports with metadata
4. **Template validation** - Script to check report follows template structure
5. **Multi-format export** - Convert markdown to PDF, DOCX, slides

These can be implemented as skills grow more sophisticated.
