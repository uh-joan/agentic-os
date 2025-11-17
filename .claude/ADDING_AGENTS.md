# Adding New Subagents - Process Guide

Quick reference for adding analytical agents to the pharma research platform.

## 1. Define Agent Scope

**Decision Matrix:**
- Is it **data gathering** (executes MCP tools) → extend pharma-search-specialist capabilities
- Is it **analytical** (reads pre-gathered data) → create new subagent

**Agent Types:**
- Data Gathering: pharma-search-specialist (MCP tool orchestration)
- Analytical: epidemiology-analyst, patient-flow-modeler, uptake-dynamics-analyst, pricing-strategy-analyst, revenue-synthesizer, market-sizing-analyst, competitive-analyst, opportunity-identifier, strategy-synthesizer, comparable-analyst, npv-modeler, structure-optimizer, target-identifier, target-validator, target-druggability-assessor, target-hypothesis-synthesizer, safety-pharmacology-analyst, genetic-toxicology-analyst, toxicology-analyst, toxicologist-regulatory-strategist, rwe-study-designer, rwe-outcomes-analyst, rwe-analytics-strategist, regulatory-risk-analyst, regulatory-precedent-analyst, regulatory-pathway-analyst, regulatory-label-strategist, regulatory-adcomm-strategist

**Rule**: Analytical agents NEVER execute MCP tools directly. They read from `data_dump/`.

---

## 2. Check MCP Tool Coverage & Eliminate Data Gaps

**CRITICAL**: Before writing agent, verify MCP tools support the use case AND eliminate all data gaps.

### Step 2A: Initial Tool Mapping

**Process:**
1. List required data sources for agent's analytical tasks
2. Map to existing MCP servers in `.mcp.json`
3. Identify gaps

**Example (epidemiology-analyst):**

| Required Data | MCP Server | Status |
|---------------|------------|--------|
| Prevalence data | datacommons-mcp | ✅ |
| Disease burden | who-mcp-server | ✅ |
| Treatment patterns | healthcare-mcp (CMS) | ✅ (initially missed!) |
| Literature | pubmed-mcp | ✅ |
| Trial eligibility | ct-gov-mcp | ✅ |
| Label contraindications | fda-mcp | ✅ |
| Disease coding | nlm-codes-mcp | ✅ (initially missed!) |
| Biomarker prevalence | opentargets-mcp-server | ✅ (initially missed!) |
| Market validation | sec-mcp-server | ✅ (initially missed!) |

**Lesson Learned**: Don't just copy from reference agents. Review ENTIRE `.mcp.json` for relevant tools.

---

### Step 2B: Comprehensive Data Gap Analysis

**CRITICAL**: Verify agent can be self-sufficient with existing MCP tools and architecture.

**Methodology:**

**1. Read `.mcp.json` - Inventory Available Tools**
```bash
# List all 12 MCP servers:
ct-gov-mcp, nlm-codes-mcp, pubmed-mcp, fda-mcp, who-mcp-server,
sec-mcp-server, healthcare-mcp, financials-mcp-server, datacommons-mcp,
patents-mcp-server, opentargets-mcp-server, pubchem-mcp-server
```

**2. Map Agent Capabilities to MCP Tools**

Create comprehensive mapping table showing which tools provide which data:

**Example (market-sizing-analyst):**

| Agent Capability | Required Data | MCP Tools | Coverage |
|------------------|---------------|-----------|----------|
| **TAM** (Total Market) | Disease prevalence | datacommons-mcp, who-mcp-server, pubmed-mcp, healthcare-mcp | ✅ Full |
| **SAM** (Eligible Market) | Eligibility criteria | ct-gov-mcp, fda-mcp, healthcare-mcp, nlm-codes-mcp | ✅ Full |
| **SOM** (Obtainable Market) | Competitive landscape | sec-mcp-server, financials-mcp-server, ct-gov-mcp, fda-mcp | ✅ Full |

**3. Check for External Dependencies**

**RED FLAGS** (indicates data gaps):
- ❌ References to non-existent agents (e.g., "patient-flow-analyst" when only epidemiology-analyst exists)
- ❌ Expects input from non-existent directories (e.g., `temp/` when architecture uses `data_dump/`)
- ❌ Requires data not provided by any MCP server
- ❌ Depends on external APIs or manual data uploads

**VALIDATION CHECKLIST:**
- [ ] All upstream data sources exist (MCP servers OR other agents)
- [ ] Input directory exists in architecture (`data_dump/` yes, `temp/` no)
- [ ] No references to fictional agents/tools
- [ ] Agent can complete its task with available data

**4. Eliminate Data Gaps**

**If gaps found, use one of these strategies:**

**Strategy A: Map to Existing MCP Tools**
- Review `.mcp.json` comprehensively
- Identify alternative MCP servers that provide similar data
- Update agent to use available tools

**Example:**
```markdown
❌ BEFORE: "Requires patient-flow-analyst for eligibility data"
✅ AFTER: "Uses ct-gov-mcp (eligibility criteria) + fda-mcp (label restrictions) + healthcare-mcp (treatment patterns)"
```

**Strategy B: Leverage Existing Agents**
- Check if another agent (e.g., epidemiology-analyst) provides needed data
- Make agent flexible: "If epidemiology-analyst output exists, use it; otherwise build from scratch"

**Example:**
```markdown
**Step 3: SAM Calculation**
- **If epidemiology-analyst output exists**: Use eligibility funnel directly
- **If building from scratch**: Apply diagnosis rate → filter by severity → exclude contraindications
```

**Strategy C: Make Agent Self-Sufficient**
- Document how agent builds what it needs from raw MCP data
- Show fallback strategies if preferred data unavailable

**5. Document Tool Coverage**

Add section to agent showing comprehensive MCP coverage:

```markdown
## N. MCP Tool Coverage Summary

**Comprehensive [Agent Purpose] Requires:**

**For [Capability 1]:**
- ✅ tool-mcp-server-1 (data type)
- ✅ tool-mcp-server-2 (data type)

**For [Capability 2]:**
- ✅ tool-mcp-server-3 (data type)
[...]

**All 12 MCP servers reviewed** - No data gaps.
```

---

### Step 2C: Data Gap Examples & Solutions

**Case Study 1: market-sizing-analyst (Initially Had Gaps)**

**GAPS FOUND:**
- ❌ Referenced `patient-flow-analyst` (doesn't exist)
- ❌ Referenced `uptake-dynamics-analyst` (doesn't exist)
- ❌ Referenced `revenue-synthesizer` (doesn't exist)
- ❌ Expected input from `temp/` directory (doesn't exist in architecture)

**SOLUTION:**
- ✅ Rewrote to work with `data_dump/` (existing architecture)
- ✅ Mapped "patient flow" data to: ct-gov-mcp + fda-mcp + healthcare-mcp
- ✅ Mapped "uptake dynamics" data to: sec-mcp-server + financials-mcp-server
- ✅ Mapped "revenue" data to: sec-mcp-server + financials-mcp-server
- ✅ Made agent work standalone OR leverage epidemiology-analyst if available

**Case Study 2: epidemiology-analyst (Initially Incomplete)**

**GAPS FOUND:**
- ⚠️ Missed healthcare-mcp for real-world evidence
- ⚠️ Missed nlm-codes-mcp for disease coding
- ⚠️ Missed opentargets-mcp-server for biomarker data

**SOLUTION:**
- ✅ Reviewed all 12 MCP servers systematically
- ✅ Added CMS Medicare data integration (healthcare-mcp)
- ✅ Added ICD-10/11 coding support (nlm-codes-mcp)
- ✅ Added genetic variant prevalence (opentargets-mcp-server)

---

### Step 2D: Data Gap Verification Checklist

Before proceeding to Step 3 (Create Agent File), verify:

- [ ] **Listed all MCP servers** from `.mcp.json` (all 12)
- [ ] **Mapped agent capabilities** to specific MCP tools (comprehensive table)
- [ ] **Verified no external dependencies** (no fictional agents, APIs, manual uploads)
- [ ] **Checked input directory exists** (`data_dump/` yes, `temp/` no)
- [ ] **Documented tool coverage** in agent file (section 7 or 8)
- [ ] **Tested fallback strategies** (agent works if some data missing)
- [ ] **Reviewed existing agents** (epidemiology-analyst, pharma-search-specialist) for integration points
- [ ] **Eliminated all data gaps** (agent is self-sufficient)

**If any checkbox unchecked → STOP and fix gaps before writing agent file.**

---

## 3. Create Agent File

**Location**: `.claude/agents/[agent-name].md`

**Structure** (follow ui-ux-designer pattern, NOT narrative LSH pattern):

```markdown
---
name: agent-name
description: Brief description - Use PROACTIVELY for [use cases]
model: sonnet
tools:
  - Read
---

# Agent Name

**Core Function**: One-line summary

**Operating Principle**: Analyst vs gatherer distinction

---

## 1. Capability Domain 1

[Enumerated capabilities, not narrative]

---

## 2. Capability Domain 2

[...]

---

## N. Response Methodology

**Step 1**: [...]
**Step 2**: [...]
[...]

---

## Critical Rules

**DO:** [...]
**DON'T:** [...]

---

## Example Output Structure

[Concrete example with tables/formatting]

---

## Integration Notes

**Workflow:**
1-4 steps max

**Separation of concerns**: [...]
```

**Key Principles:**
- ✅ Enumerated capability domains (1, 2, 3...)
- ✅ Structured response methodology (Step 1, 2, 3...)
- ✅ Example output section
- ✅ Scannable (bullets, tables, not prose)
- ✅ Frontmatter with PROACTIVE trigger
- ❌ No narrative/essay style
- ❌ No bloat (use tables over bullet lists when possible)

---

## 4. Update Documentation

**Files to Update** (in order):

### A. `.claude/CLAUDE.md`
**Section**: Architecture → add agent to list
```markdown
**Agents**:
- `pharma-search-specialist`: Query → JSON plan → MCP execution → `data_dump/`
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `[new-agent]`: Reads `data_dump/` → [outputs]
```

**Section**: Execution Protocol → add invocation template
```markdown
### 4. Invoke Analytical Agents (If Needed)

**[new-agent]** - Brief description

Use for: [use cases]

Template:
"You are [agent-name]. Read .claude/agents/[agent-name].md.
[minimal invocation prompt]"
```

**Section**: Design Principles → update if needed (usually no change)

### B. `README.md`
**Section**: Architecture → update agent list
```markdown
**Agents:**
- `pharma-search-specialist`: Query → JSON plan → MCP tools → `data_dump/`
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `[new-agent]`: Reads `data_dump/` → [outputs]
```

**Section**: Agents → add new section
```markdown
### [new-agent]
Brief description. Input: `data_dump/` → Output: [...]

**Capabilities**: [list key capabilities in one line]
```

**Section**: Example Workflows → add if relevant
```markdown
### [New Workflow Type]
1. Step using MCP tools
2. Step using new agent
3. Output
```

### C. `.claude/settings.local.json` (if needed)
Add to permissions if agent needs special approval:
```json
"permissions": {
  "allow": [
    "Task(agent:[new-agent-name])"
  ]
}
```

---

## 5. Optimization Pass

**Before committing, review for bloat:**

### Check Data Sources Section
❌ **Bloated** (long bullets):
```markdown
**CMS Medicare Data**
- Actual diagnosis rates from claims data
- Treatment line distribution and switching patterns
- Geographic prevalence variations by state/region
- Age-stratified disease prevalence
[...10 more bullets]
```

✅ **Optimized** (table):
```markdown
| Source | Key Data |
|--------|----------|
| **CMS Medicare** ⭐ | Claims diagnosis, treatment switching, comorbidities |
```

### Check Integration Section
❌ **Bloated** (narrative):
```markdown
**Typical Workflow:**
The user first asks for market sizing. Then Claude Code invokes
the pharma-search-specialist agent which coordinates data gathering
from multiple sources including Data Commons for population data,
WHO for disease burden, CMS for treatment patterns...
```

✅ **Optimized** (steps):
```markdown
**Workflow:**
1. User asks for [goal]
2. `pharma-search-specialist` gathers → `data_dump/`
3. **This agent** analyzes → returns [output]
```

### Check Principles/Rules
❌ **Bloated** (verbose bullets):
```markdown
**Rigor Over Speed**
- Never fabricate data to fill gaps
- Explicitly state "data not available" when true
- Quantify uncertainty rather than presenting false precision
[3 more sections like this]
```

✅ **Optimized** (compact):
```markdown
- **Rigor**: Never fabricate data, quantify uncertainty, state gaps explicitly
```

**Rule**: If section >10 lines, can it be a table or one-liners?

---

## 6. Test Agent

**Verification checklist:**

1. [ ] Agent frontmatter has correct name, description, tools
2. [ ] All MCP tool references are correct (from `.mcp.json`)
3. [ ] No MCP tool execution (analytical agents are read-only)
4. [ ] Enumerated capability domains (not narrative)
5. [ ] Structured response methodology included
6. [ ] Example output section exists
7. [ ] Integration workflow documented (4 steps max)
8. [ ] Data sources use tables not long bullets
9. [ ] No bloat (check line count, compare to similar agents)
10. [ ] `.claude/CLAUDE.md` updated
11. [ ] `README.md` updated
12. [ ] Agent description is PROACTIVE ("Use PROACTIVELY for...")
13. [ ] **Data gaps eliminated** (all dependencies exist, no fictional agents/tools)
14. [ ] **MCP tool coverage documented** (section showing comprehensive mapping)
15. [ ] **Input directory verified** (uses `data_dump/` not `temp/` or other non-existent paths)

**Test invocation:**
```
"You are [agent-name]. Read .claude/agents/[agent-name].md.
Analyze data_dump/[test-folder]/ and [task]."
```

---

## 7. Commit

**Commit message template:**
```
Add [agent-name] analytical agent

[One-line description of agent capabilities]

- Created .claude/agents/[agent-name].md (N domains, M-step methodology)
- Updated .claude/CLAUDE.md (architecture, invocation template)
- Updated README.md (agent description, workflow example)
- Integrated with [X] MCP tools: [list]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Common Pitfalls

### 1. Data Gaps & External Dependencies
**Problem**: Agent references non-existent agents, tools, or data sources
**Solution**: Complete Step 2B-2D verification BEFORE writing agent file

**Critical Red Flags:**
- ❌ References to agents that don't exist (e.g., "patient-flow-analyst" when it's not in `.claude/agents/`)
- ❌ Input from non-existent directories (`temp/` when architecture uses `data_dump/`)
- ❌ Dependencies on external APIs or manual data uploads
- ❌ Assumptions about data without checking MCP server capabilities

**Example**: market-sizing-analyst initially had:
- Referenced 3 fictional upstream agents (patient-flow, uptake-dynamics, revenue-synthesizer)
- Expected `temp/` directory (doesn't exist in architecture)
- **Fix**: Mapped all capabilities to existing MCP servers + epidemiology-analyst integration

### 2. Incomplete MCP Tool Coverage
**Problem**: Copying data sources from reference agent without checking `.mcp.json`
**Solution**: Always review ALL 12 MCP servers, map required data to available tools

**Example**: epidemiology-analyst initially missed:
- healthcare-mcp (CMS real-world evidence) - **critical for treatment patterns**
- nlm-codes-mcp (disease coding)
- opentargets-mcp-server (biomarker prevalence)
- sec-mcp-server (market validation)

### 3. Structure Bloat
**Problem**: Using narrative/essay style like LSH agent
**Solution**: Follow ui-ux-designer pattern (enumerated domains, structured methodology)

### 4. Narrative Documentation
**Problem**: Adding verbose workflow descriptions to CLAUDE.md/README.md
**Solution**: Use tables, 1-4 step workflows, one-liners

### 5. Missing Frontmatter PROACTIVE Trigger
**Problem**: Agent isn't invoked automatically by Claude Code
**Solution**: Add "Use PROACTIVELY for [use cases]" in description

### 6. Analytical Agent Executing MCP Tools
**Problem**: Agent tries to call MCP tools directly
**Solution**: Clear "read-only" constraint, references to pharma-search-specialist for data gathering

---

## Future Agent Ideas

**Potential analytical agents:**

- **safety-signal-analyst**: Adverse event pattern detection, signal scoring, risk quantification
- **competitive-intelligence-analyst**: Pipeline comparison, market positioning, SWOT analysis
- **kol-identification-analyst**: Author network analysis, publication impact, geographic clustering
- **patent-landscape-analyst**: IP coverage analysis, freedom-to-operate, patent clustering
- **pricing-analyst**: Price benchmarking, reimbursement landscape, ICER modeling
- **regulatory-strategy-analyst**: Approval pathway analysis, precedent identification
- **clinical-trial-design-analyst**: Protocol optimization, endpoint selection, comparator analysis

**For each**: Map to MCP tools first, verify coverage, then build.

---

## Quick Reference

**Agent Creation Checklist:**
1. ✅ Define scope (analytical vs gathering)
2. ✅ **Map MCP tool coverage (check ALL 12 servers in `.mcp.json`)**
3. ✅ **Eliminate data gaps (verify no external dependencies, fictional agents, or non-existent directories)**
4. ✅ Create agent file (ui-ux structure, no bloat, include MCP coverage section)
5. ✅ Update CLAUDE.md (architecture, invocation)
6. ✅ Update README.md (agent list, workflow)
7. ✅ Optimization pass (tables, one-liners)
8. ✅ **Test data gap verification (15-point checklist)**
9. ✅ Test invocation
10. ✅ Commit with template message

**Critical Pre-Flight Checks (MUST pass before writing agent):**
- [ ] All 12 MCP servers reviewed for relevant data
- [ ] No references to non-existent agents/tools
- [ ] Input directory exists (`data_dump/` ✅, `temp/` ❌)
- [ ] Agent can complete task with available data (self-sufficient)
- [ ] MCP tool coverage table documented in agent file

**Files Modified (always):**
- `.claude/agents/[agent-name].md` (NEW)
- `.claude/CLAUDE.md` (2-3 sections)
- `README.md` (2-3 sections)

**Files Modified (sometimes):**
- `.claude/settings.local.json` (if special permissions needed)
