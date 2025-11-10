# Adding New Subagents - Process Guide

Quick reference for adding analytical agents to the pharma research platform.

## 1. Define Agent Scope

**Decision Matrix:**
- Is it **data gathering** (executes MCP tools) → extend pharma-search-specialist capabilities
- Is it **analytical** (reads pre-gathered data) → create new subagent

**Agent Types:**
- Data Gathering: pharma-search-specialist (MCP tool orchestration)
- Analytical: epidemiology-analyst, [future: safety-analyst, competitive-analyst, etc.]

**Rule**: Analytical agents NEVER execute MCP tools directly. They read from `data_dump/`.

---

## 2. Check MCP Tool Coverage

**CRITICAL**: Before writing agent, verify MCP tools support the use case.

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

### 1. MCP Tool Gaps
**Problem**: Copying data sources from reference agent without checking `.mcp.json`
**Solution**: Always review full MCP server list, map required data to available tools

**Example**: epidemiology-analyst initially missed:
- healthcare-mcp (CMS real-world evidence) - **critical for treatment patterns**
- nlm-codes-mcp (disease coding)
- opentargets-mcp-server (biomarker prevalence)
- sec-mcp-server (market validation)

### 2. Structure Bloat
**Problem**: Using narrative/essay style like LSH agent
**Solution**: Follow ui-ux-designer pattern (enumerated domains, structured methodology)

### 3. Narrative Documentation
**Problem**: Adding verbose workflow descriptions to CLAUDE.md/README.md
**Solution**: Use tables, 1-4 step workflows, one-liners

### 4. Missing Frontmatter PROACTIVE Trigger
**Problem**: Agent isn't invoked automatically by Claude Code
**Solution**: Add "Use PROACTIVELY for [use cases]" in description

### 5. Analytical Agent Executing MCP Tools
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
2. ✅ Map MCP tool coverage (check `.mcp.json`)
3. ✅ Create agent file (ui-ux structure, no bloat)
4. ✅ Update CLAUDE.md (architecture, invocation)
5. ✅ Update README.md (agent list, workflow)
6. ✅ Optimization pass (tables, one-liners)
7. ✅ Test invocation
8. ✅ Commit with template message

**Files Modified (always):**
- `.claude/agents/[agent-name].md` (NEW)
- `.claude/CLAUDE.md` (2-3 sections)
- `README.md` (2-3 sections)

**Files Modified (sometimes):**
- `.claude/settings.local.json` (if special permissions needed)
