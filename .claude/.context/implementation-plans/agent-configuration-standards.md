# Agent Configuration Standards

## Purpose

This document defines configuration standards for all agents in the Pharmaceutical Research Intelligence Platform, with emphasis on source attribution requirements, verification processes, and the metadata-driven pattern.

---

## Agent Architecture Overview

The platform uses a **two-layer agent architecture**:

### Layer 1: Infrastructure Agents (Data Collection)
- **Purpose**: Create reusable data collection skills
- **Example**: `pharma-search-specialist`
- **Pattern**: User query → Generate Python code → Execute → Return skill code
- **Output**: Skills with 100% MCP-verified data
- **Verification**: Automatic (verify_source_attribution.py)

### Layer 3: Strategic Agents (Analysis & Synthesis)
- **Purpose**: Strategic analysis and synthesis
- **Example**: `competitive-landscape-analyst`
- **Pattern**: Metadata-driven data collection → Strategic analysis → Report generation
- **Output**: Reports with >70% MCP-verified data, <20% internal knowledge
- **Verification**: Manual (verify_report_attribution.py)

**Key Principle**: Infrastructure agents collect data, strategic agents analyze and synthesize.

---

## Source Attribution Requirements

### Universal Requirements (All Agents)

**1. Prefer MCP-Verified Data Over Internal Knowledge**
- Always attempt to collect data from MCP servers first
- Use internal knowledge only when MCP data unavailable
- Explicitly label internal knowledge with citations

**2. Source Citation Formats**

| Source Type | Citation Format | Example |
|-------------|----------------|---------|
| MCP-Verified | `(source: ServerName, YYYY-MM-DD)` | `(source: ClinicalTrials.gov, 2025-12-03)` |
| Published Literature | `(Author et al., Journal Year, PMID: ID)` | `(Jastreboff et al., NEJM 2022, PMID: 35658024)` |
| Analytical Insight | `[analysis based on ServerName data]` | `[analysis based on ClinicalTrials.gov data]` |
| Internal Knowledge | `[estimated from industry consensus]` | `[estimated from industry analyst consensus]` |

**3. Required Metadata Sections**

All outputs must include:
- **Skills**: `source_metadata` dict with 6 required fields
- **Reports**: `data_sources_mcp_verified` and `data_sources_internal_knowledge` frontmatter sections

---

## Infrastructure Agent Configuration

### Example: pharma-search-specialist

**File Location**: `.claude/agents/pharma-search-specialist.md`

**Required Sections**:

#### 1. Agent Metadata (YAML Frontmatter)
```yaml
---
name: pharma-search-specialist
description: Generates Python code to query MCP servers and create reusable skills
model: sonnet
color: #3B82F6
---
```

#### 2. Source Attribution Requirements
Must include comprehensive instructions on:
- Return structure: `{'data': {...}, 'source_metadata': {...}, 'summary': '...'}`
- Required source_metadata fields (6 fields)
- Citation format for summary strings
- Datetime import requirement
- JSON output requirement

#### 3. Code Standards (Phase 3 Migration Pattern)
Must specify:
- **A. Datetime Import**: `from datetime import datetime` (required)
- **B. No Print Statements**: Comment out all print() in production code
- **C. JSON Output**: `if __name__ == "__main__": print(json.dumps(result, indent=2))`
- **D. Error Returns**: ALL return statements must include source_metadata
- **E. Verification**: Skills must pass verify_source_attribution.py

#### 4. Closed-Loop Verification
Must include verification workflow:
```bash
python3 .claude/tools/verification/verify_source_attribution.py \
  --type skill \
  --execution-output "$(cat /tmp/output.json)" \
  --json
```

**Expected Result**: `{"valid": true, "errors": [], "warnings": []}`

#### 5. Progressive Disclosure Instructions
Must reference:
- MCP tool guides: `.claude/.context/mcp-tool-guides/[server].md`
- Code examples: `.claude/.context/code-examples/[pattern].md`
- Reference skills: Strategy system provides reference patterns

### Verification Requirements for Infrastructure Agents

**Automatic Verification** (agent runs during skill creation):
1. Execution successful (exit code 0, no exceptions)
2. Data retrieved (count > 0)
3. Source metadata present (all 6 fields)
4. JSON output valid (parseable)
5. No print statements (clean JSON)

**Failure Response**:
- Self-correct (max 3 attempts)
- Never ask user to validate
- Return only verified skills

---

## Strategic Agent Configuration

### Example: competitive-landscape-analyst

**File Location**: `.claude/agents/competitive-landscape-analyst.md`

**Required Sections**:

#### 1. Agent Metadata with Data Requirements (YAML Frontmatter)

```yaml
---
name: competitive-landscape-analyst
description: Monitor, analyze, and synthesize competitive drug development pipeline intelligence
model: sonnet
color: #10B981

# REQUIRED: Metadata-driven data collection
data_requirements:
  # Core data (always collected)
  always:
    - type: clinical_trials
      pattern: get_{therapeutic_area}_trials
      description: Clinical trial pipeline data across all phases
      sources: [ct_gov_mcp]

    - type: approved_drugs
      pattern: get_{therapeutic_area}_fda_drugs
      description: FDA approved drugs in therapeutic area
      sources: [fda_mcp]

  # Contextual data (collected based on query keywords)
  contextual:
    - type: patents
      pattern: get_{therapeutic_area}_patents
      trigger: keywords("IP", "patent", "freedom to operate")
      description: Patent landscape and IP positioning
      sources: [uspto_patents_mcp]
      optional: true

    - type: publications
      pattern: get_{therapeutic_area}_pubmed
      trigger: keywords("literature", "publications", "clinical data")
      description: Recent scientific publications
      sources: [pubmed_mcp]
      optional: true

# REQUIRED: Inference rules for parameter extraction
inference_rules:
  therapeutic_area: Extract disease/therapeutic area/drug class from query
  company: Extract company name if explicitly mentioned
  context_triggers: Analyze query for keywords indicating optional data
---
```

**Critical**: `data_requirements` metadata is how the main agent knows which skills to collect before invoking strategic agent.

#### 2. Source Citation Requirements (Comprehensive)

Must include sections on:

**A. Distinguish Data Types (MANDATORY)**:
- Category A: MCP-Verified Data (PREFERRED)
- Category B: Analytical Insights (DERIVED FROM MCP)
- Category C: Internal Knowledge (MINIMIZE - <20%)

**B. Always Try MCP Data First (MANDATORY)**:
- Decision tree: Can I get from MCP? → Can I derive from MCP? → Only then use internal knowledge

**C. Frontmatter Source Metadata (REQUIRED)**:
```yaml
data_sources_mcp_verified:
  - skill_name: Description (source: SourceName, date: YYYY-MM-DD)

data_sources_internal_knowledge:
  - Category: Description [estimated from source]

source_validation:
  mcp_verified_claims: N
  analytical_insights: N
  internal_knowledge: N  # Should be <20% of total
```

**D. Inline Citations (EVERY MAJOR CLAIM)**:
- All factual claims must have source citations
- Tables/figures must have source attribution
- Target >70% of major claims cited

**E. Internal Knowledge Constraint**:
- Target: <20% of claims use internal knowledge
- Preferred: <10% internal knowledge usage
- Process: Check MCP availability before using internal knowledge

**F. Citation Quality Checklist**:
- [ ] Frontmatter has complete data_sources_mcp_verified list
- [ ] >70% of major claims have inline citations
- [ ] Internal knowledge usage <20%
- [ ] MCP sources include query dates
- [ ] Published literature includes PMID/DOI

#### 3. Report Verification (MANDATORY POST-GENERATION)

Must include verification workflow:

**Step-by-step Process**:
1. Save report to `reports/{agent_type}/YYYY-MM-DD_{topic}.md`
2. Run verification tool:
   ```bash
   python3 .claude/tools/verification/verify_report_attribution.py \
     --report reports/{agent_type}/YYYY-MM-DD_{topic}.md \
     --json
   ```
3. Parse results and act:
   - ✅ PASS (valid: true): Return report to user
   - ❌ FAIL (valid: false): Fix errors and re-verify (max 2 iterations)

**Verification Thresholds**:
- MCP-Verified Data: >70% (preferred >80%)
- Internal Knowledge: <20% (preferred <10%)
- Published Literature: >10% (when available)

**Action on Failure**:
- If internal_percentage >20%: Identify claims that can be backed by MCP data
- Run additional skills to collect missing data
- Replace internal knowledge claims with MCP-verified data
- Re-verify report

**DO NOT** return unverified reports to user.

#### 4. Report Writing Standards

Must specify concise format:
- Target: 1500-2500 words (3000 max)
- Bullet points over paragraphs
- Tables over text
- Lead with conclusions
- No verbose filler

### Verification Requirements for Strategic Agents

**Manual Verification** (agent runs before returning report):
1. Report saved to filesystem
2. Verification tool executed
3. Metrics validated:
   - internal_percentage <20%
   - mcp_percentage >70%
   - total_citations >50 (for comprehensive reports)
4. Frontmatter complete (data_sources sections)
5. Inline citations present (>70% of claims)

**Failure Response**:
- Iterate max 2 times to fix
- If still failing: Escalate to user with diagnostic info
- Never return unverified report

---

## Main Agent Orchestration Pattern

### Metadata-Driven Data Collection Flow

**Step 0: Pre-Flight Skill Discovery (MANDATORY)**

Before invoking any agent or collecting data:

1. **Infer Parameters**:
   ```python
   # Extract from user query:
   therapeutic_area = "GLP-1"
   data_type = "trials"
   servers = ["ct_gov_mcp"]
   ```

2. **Run Strategy Check**:
   ```bash
   python3 .claude/tools/skill_discovery/strategy.py \
     --skill "get_glp1_trials" \
     --therapeutic-area "GLP-1" \
     --data-type "trials" \
     --servers "ct_gov_mcp" \
     --query "Get GLP-1 trials" \
     --json
   ```

3. **Execute Strategy**:
   - **REUSE**: Execute existing skill, skip agent invocation
   - **ADAPT**: Read reference skill, invoke pharma-search-specialist with adaptation context
   - **CREATE**: Read reference pattern, invoke pharma-search-specialist with creation context

**Step 1-4: For Strategic Agent Invocations**

1. **Read Agent Metadata**: Extract `data_requirements` from agent frontmatter
2. **Infer Parameters**: Extract therapeutic_area, company, keywords from query
3. **Apply Skill Patterns**: Transform patterns with parameters
   - `get_{therapeutic_area}_trials` → `get_kras_inhibitor_trials`
4. **Check/Create/Execute Skills**: Use strategy system for each required skill

**Step 5-6: Invoke and Persist**

5. **Invoke Strategic Agent**: Provide collected MCP data in prompt
6. **Persist Report**: Agent saves report and runs verification before returning

### Benefits of Metadata-Driven Pattern

✅ **Small footprint**: 6 data sources support 100+ agent capabilities
✅ **Generic orchestration**: Main agent logic works for all strategic agents
✅ **Smart inference**: Same pattern, different parameters
✅ **Contextual data**: Only collected when triggered by keywords
✅ **Zero duplication**: Strategy system prevents duplicate skill creation

---

## Adding New Agents

### For Infrastructure Agents (Data Collection)

**Use Case**: Create specialized data collection agent for non-MCP data sources or complex workflows.

**Steps**:
1. Copy `pharma-search-specialist.md` as template
2. Update agent metadata (name, description, model, color)
3. Specify data sources and return patterns
4. Include source attribution requirements (Section 2)
5. Include code standards (Section 6 from pharma-search-specialist)
6. Include verification workflow
7. Test with sample query
8. Verify skill output passes verify_source_attribution.py

**Required Sections**:
- Source Attribution Requirements
- Return Structure (data + source_metadata + summary)
- Code Standards for Verification
- Closed-Loop Verification Instructions

### For Strategic Agents (Analysis & Synthesis)

**Use Case**: Create domain-specific strategic analyst (e.g., regulatory-strategy-analyst, market-access-analyst).

**Steps**:
1. **Copy Template**: Use `competitive-landscape-analyst.md` as starting point

2. **Define Data Requirements** (YAML frontmatter):
   ```yaml
   data_requirements:
     always:
       - type: {data_type}
         pattern: get_{param}_{data_type}
         description: {purpose}
         sources: [{mcp_servers}]

     contextual:
       - type: {optional_data_type}
         pattern: get_{param}_{optional_data_type}
         trigger: keywords("{keyword1}", "{keyword2}")
         optional: true
   ```

3. **Define Inference Rules**:
   ```yaml
   inference_rules:
     parameter_name: Extraction instructions from query
   ```

4. **Add Source Citation Requirements** (copy from competitive-landscape-analyst lines 62-167)

5. **Add Report Verification Section** (copy from competitive-landscape-analyst lines 169-227)

6. **Customize Capabilities**: List domain-specific analytical capabilities

7. **Define Report Standards**: Specify output format, word count, structure

8. **Test Full Workflow**:
   - Invoke agent with sample query
   - Verify data collection works
   - Verify report generation includes citations
   - Verify report passes verify_report_attribution.py

**Required Sections**:
- data_requirements (YAML metadata)
- inference_rules (YAML metadata)
- Source Citation Requirements (7 subsections)
- Report Verification (MANDATORY POST-GENERATION)
- Report Writing Standards

### Common Pitfalls for New Agents

**❌ Missing data_requirements metadata**:
- Main agent won't know which skills to collect
- Agent will use >80% internal knowledge

**❌ No verification section**:
- Reports will not be validated
- Internal knowledge may exceed 20%

**❌ Vague inference rules**:
- Main agent can't extract parameters from queries
- Skill patterns won't be applied correctly

**❌ No citation format examples**:
- Agent won't know how to cite sources
- Reports will fail verification

---

## Verification Tool Integration

### For Infrastructure Agents

**Tool**: `verify_source_attribution.py`

**Invocation**:
```bash
python3 .claude/tools/verification/verify_source_attribution.py \
  --type skill \
  --execution-output "$(cat /tmp/output.json)" \
  --json
```

**Checks**:
- source_metadata present
- All 6 required fields populated
- query_date in ISO 8601 format (YYYY-MM-DD)
- data_count matches actual data
- JSON output valid

**Auto-Approval**:
Add to Claude Code configuration:
```bash
Bash(python3 .claude/tools/verification/verify_source_attribution.py:*)
```

### For Strategic Agents

**Tool**: `verify_report_attribution.py`

**Invocation**:
```bash
python3 .claude/tools/verification/verify_report_attribution.py \
  --report reports/{agent_type}/YYYY-MM-DD_{topic}.md \
  --json
```

**Checks**:
- Frontmatter has data_sources_mcp_verified section
- Inline citations present (>70% of major claims)
- Internal knowledge usage <20%
- MCP-verified + published data >70%
- Tables/figures have source attribution

**Output**:
```json
{
  "valid": true|false,
  "errors": [...],
  "warnings": [...],
  "metrics": {
    "total_citations": N,
    "mcp_verified": N,
    "internal_knowledge": N,
    "mcp_percentage": X.X,
    "internal_percentage": Y.Y
  },
  "recommendations": [...]
}
```

**Agent Response**:
- If valid: Return report to user
- If invalid: Fix errors, re-verify (max 2 iterations)
- If still invalid after 2 iterations: Escalate to user

---

## Best Practices

### 1. Progressive Disclosure (Infrastructure Agents)
- Read only MCP tool guides needed for current query
- Read only code examples needed for current pattern
- Don't load all 13 servers' documentation upfront
- Agent decides what to read based on query analysis

### 2. Metadata-Driven Configuration (Strategic Agents)
- Keep data_requirements in YAML frontmatter, not agent body
- Use `always` for core data, `contextual` for optional data
- Define clear trigger keywords for contextual data
- Keep metadata small (~6 data sources support 100+ capabilities)

### 3. Source Citation Discipline (All Agents)
- Always try MCP data first before internal knowledge
- Explicitly label ALL internal knowledge claims
- Include query dates in all MCP citations
- Include PMID/DOI for all published literature

### 4. Verification Rigor (All Agents)
- Infrastructure agents: Verify every skill before saving
- Strategic agents: Verify every report before returning
- Never skip verification for "quick analyses"
- Use verification metrics to improve future outputs

### 5. Concise Communication (Strategic Agents)
- Target 1500-2500 words for reports (3000 max)
- Bullet points over paragraphs
- Tables over text
- Lead with conclusions
- Cut verbose filler

### 6. Error Handling (All Agents)
- Infrastructure agents: Self-correct up to 3 attempts
- Strategic agents: Iterate up to 2 times on verification failure
- Always provide diagnostic information on escalation
- Never return unverified outputs

### 7. Strategy System Integration (All Agents)
- Always run strategy check before skill creation
- Reuse existing skills when available (REUSE strategy)
- Adapt patterns from reference skills (ADAPT strategy)
- Create with proven patterns (CREATE strategy)
- Trigger keywords enable intent-specific skill matching

---

## Configuration Checklist

### For Infrastructure Agents
- [ ] Agent metadata (name, description, model, color)
- [ ] Source attribution requirements section
- [ ] Return structure specification (data + source_metadata + summary)
- [ ] Code standards section (datetime import, no prints, JSON output, error handling)
- [ ] Verification workflow section
- [ ] Progressive disclosure instructions
- [ ] Example interactions
- [ ] Test with sample query
- [ ] Verify skill passes verify_source_attribution.py

### For Strategic Agents
- [ ] Agent metadata (name, description, model, color)
- [ ] data_requirements (always + contextual)
- [ ] inference_rules (parameter extraction)
- [ ] Source citation requirements (7 subsections)
- [ ] Report verification section (MANDATORY POST-GENERATION)
- [ ] Report writing standards
- [ ] Capabilities section
- [ ] Example interactions
- [ ] Test full workflow (data collection → analysis → report → verification)
- [ ] Verify report passes verify_report_attribution.py with <20% internal knowledge

---

## Maintenance and Evolution

### When to Update Agent Configuration

**Infrastructure Agents**:
- New MCP server added → Update progressive disclosure instructions
- New verification check added → Update verification workflow section
- New code pattern established → Update code standards section

**Strategic Agents**:
- New data source needed → Add to data_requirements metadata
- New analysis capability → Add to capabilities section (no metadata change)
- Verification thresholds changed → Update verification section

### Versioning and Documentation

**Agent Files**:
- Version controlled in `.claude/agents/`
- Changes tracked via git commits
- Breaking changes require update to all dependent workflows

**Configuration Guides**:
- Version controlled in `.claude/.context/implementation-plans/`
- Updated when standards evolve
- Reference from agent files (single source of truth)

**Examples**:
- Version controlled in `.claude/.context/examples/`
- Updated when new patterns emerge
- Demonstrate both good and bad practices

### Quality Metrics

Track agent quality over time:

**Infrastructure Agents**:
- Skills created per session
- Verification pass rate (target: >95%)
- Self-correction success rate
- Time to verified skill

**Strategic Agents**:
- Reports generated per session
- Verification pass rate (target: >90%)
- Internal knowledge usage (target: <15% average)
- MCP-verified data usage (target: >75% average)

---

## References

- **Implementation Plan**: `.claude/.context/implementation-plans/source-attribution-implementation-plan.md`
- **Migration Guide**: `.claude/.context/implementation-plans/source-attribution-migration-guide.md`
- **Invocation Examples**: `.claude/.context/examples/agent-invocation-examples.md`
- **Skill Verification Tool**: `.claude/tools/verification/verify_source_attribution.py`
- **Report Verification Tool**: `.claude/tools/verification/verify_report_attribution.py`
- **Strategy System**: `.claude/tools/skill_discovery/strategy.py`
- **Index-Based Discovery**: `.claude/.context/implementation-plans/index-based-skill-discovery.md`

---

*Document created: 2025-12-03*
*Status: Phase 4.4 - Agent Configuration Standards Complete*
*Version: 1.0*
