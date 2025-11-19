# Pharmaceutical Research Intelligence Platform

## Core Architecture

**Pattern**: Code execution with MCP (Anthropic pattern + Two-phase persistence)

**How it works**:
1. User asks query (e.g., "What GLP-1 drugs are approved?")
2. pharma-search-specialist agent invoked
3. Agent reads relevant documentation via progressive disclosure:
   - `.claude/.context/mcp-tool-guides/[server].md` - API documentation
   - `.claude/.context/code-examples/[pattern].md` - Code patterns (on-demand)
4. Agent generates Python code following pattern
5. Agent executes code via Bash tool
6. Agent returns: summary + skill code + documentation
7. Main Claude Code agent saves files to `.claude/skills/` using Write tool
8. Summary shown to user, skills library grows

**Key Benefits**:
- ✅ **98.7% context reduction**: Raw data never enters model context (Anthropic measured: 150k → 2k tokens)
- ✅ **Progressive disclosure**: Load only docs/examples needed for current query
- ✅ **Skills library**: Build reusable function toolbox across sessions
- ✅ **Privacy**: Sensitive data stays in execution environment
- ✅ **Natural control flow**: Loops, conditionals, error handling in Python

**Reference**: https://www.anthropic.com/engineering/code-execution-with-mcp

---

## Directory Structure

```
.claude/
├── CLAUDE.md                           # This file - architecture overview
├── agents/
│   ├── pharma-search-specialist.md     # Infrastructure agent
│   └── competitive-landscape-analyst.md # Strategic agent
├── .context/
│   ├── mcp-tool-guides/                # MCP server API documentation
│   │   ├── clinicaltrials.md           # CT.gov API (returns markdown)
│   │   ├── fda.md                      # FDA API (returns JSON)
│   │   ├── pubmed.md
│   │   └── [10 more servers...]
│   ├── code-examples/                  # Code patterns (progressive disclosure)
│   │   ├── ctgov_markdown_parsing.md   # CT.gov pattern
│   │   ├── fda_json_parsing.md         # FDA pattern
│   │   ├── multi_server_query.md       # Combining servers
│   │   └── skills_library_pattern.md   # Skills library pattern
│   └── templates/                      # Report templates
│       ├── competitive-landscape-report.md
│       └── skill-frontmatter-template.yaml  # NEW: Skill YAML template
├── skills/                             # Reusable functions (Anthropic folder structure)
│   ├── index.json                      # Skills discovery index (v1.1)
│   │
│   ├── glp1-trials/                    # NEW: Folder structure (Anthropic format)
│   │   ├── SKILL.md                    # YAML frontmatter + documentation
│   │   └── scripts/
│   │       └── get_glp1_trials.py      # Executable function
│   │
│   ├── glp1-fda-drugs/                 # NEW: Folder structure
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── get_glp1_fda_drugs.py
│   │
│   └── get_old_skill.py                # OLD: Flat structure (being phased out)
│       get_old_skill.md                # OLD: Kept for backward compatibility
│
└── scripts/                            # Utilities
    ├── init_skill.py                   # NEW: Initialize new skill
    ├── package_skill.py                # NEW: Migrate flat to folder
    ├── discover_skills.py              # NEW: Find skills (both formats)
    ├── parse_skill_metadata.py         # NEW: Parse YAML frontmatter
    └── mcp/                            # MCP infrastructure
        ├── client.py                   # MCP client (spawns servers, manages JSON-RPC)
        └── servers/                    # Python function stubs
            ├── fda_mcp/
            ├── ct_gov_mcp/
            └── [12 MCP servers...]

reports/                                # Strategic analysis reports (version controlled)
├── competitive-landscape/
│   └── YYYY-MM-DD_therapeutic-area.md
├── clinical-strategy/
└── regulatory-analysis/
```

---

## Skills Library Format (v2.0)

### Migration to Anthropic Folder Structure

**Current State**: Hybrid (both formats supported)
- **v2.0 (Folder structure)**: New skills use Anthropic format
- **v1.0 (Flat structure)**: Legacy skills kept for compatibility

**Folder Structure (v2.0 - Current Standard)**:
```
skill-name/
├── SKILL.md              # YAML frontmatter + documentation
└── scripts/
    └── skill_function.py # Executable Python function
```

**Flat Structure (v1.0 - Deprecated)**:
```
skill_function.py         # Python function
skill_function.md         # Documentation
```

**Benefits of v2.0**:
- ✅ **Standardized metadata**: YAML frontmatter for discovery
- ✅ **Self-contained packages**: Easy to share/distribute
- ✅ **Clear boundaries**: Folder per skill
- ✅ **Anthropic alignment**: Follows industry conventions
- ✅ **Still code execution**: NOT instruction-based (maintains 98.7% efficiency)

**Skill Discovery**:
```bash
# Find all skills (both formats)
python3 .claude/scripts/discover_skills.py

# Find skills by pattern
python3 -c "from discover_skills import find_skill_by_pattern; print(find_skill_by_pattern('pagination'))"

# Find skills by MCP server
python3 -c "from discover_skills import find_skill_by_server; print(find_skill_by_server('ct_gov_mcp'))"
```

**Creating New Skills**:
```bash
# Initialize new skill in folder structure
python3 .claude/scripts/init_skill.py get_new_data --server ct_gov_mcp
```

**Migration Status** (Phase 3):
- Phase 1: YAML frontmatter added to all skills ✓
- Phase 2: Folder structure created for reference skills ✓
- Phase 3: Agent generates new folder format ← **Current**
- Phase 4: Complete migration (remaining skills) ← Next

---

## Agent Types

### Layer 1: Infrastructure Agents (Data Collection)

**pharma-search-specialist** - Creates reusable data collection skills

**Pattern**: User query → Read docs → Generate Python code → Claude Code executes

**Defined in**: `.claude/agents/pharma-search-specialist.md`

**Progressive Disclosure Flow**:
1. Identify query type (FDA? CT.gov? Multi-server?)
2. Read relevant tool guide: `.claude/.context/mcp-tool-guides/[server].md`
3. Read relevant code example: `.claude/.context/code-examples/[pattern].md`
4. Generate code following pattern
5. Return skill code to main agent

**Example**:
- User: "How many Phase 3 obesity trials are recruiting in the US?"
- Agent reads: `clinicaltrials.md` + `ctgov_markdown_parsing.md`
- Agent generates Python code with CT.gov markdown parsing
- Agent executes code via Bash → gets: "36 trials"
- Agent returns: summary + skill code + documentation
- Main agent saves: `.claude/skills/get_us_phase3_obesity_recruiting_trials.py`

---

### Layer 3: Strategic Agents (Analysis & Synthesis)

**competitive-landscape-analyst** - Competitive intelligence and strategic analysis

**Pattern**: Metadata-driven data collection → Strategic analysis

**Defined in**: `.claude/agents/competitive-landscape-analyst.md`

**How it works**:
1. User invokes: `@agent-competitive-landscape-analyst "Analyze KRAS landscape"`
2. Main agent reads agent metadata (data_requirements)
3. Main agent infers parameters from query (therapeutic_area = "KRAS")
4. Main agent applies skill patterns: `get_{therapeutic_area}_trials` → `get_kras_trials`
5. Main agent checks/creates/executes required skills
6. Main agent invokes strategic agent with collected data
7. Strategic agent performs analysis and returns insights

**Key Innovation**: Agent body describes 100+ capabilities, but only ~6 core data sources needed.
Metadata separates WHAT agent can analyze from HOW data is collected.

**Example**:
- User: "Analyze KRAS inhibitor competitive landscape"
- Main agent reads metadata → Needs: trials + FDA drugs
- Main agent creates skills (if missing) → Executes skills
- Main agent invokes analyst with data
- Analyst returns: competitive positioning, market timing, recommendations

---

## MCP Servers Available

**12 servers providing pharmaceutical intelligence**:

| Server | Purpose | Response Format |
|--------|---------|-----------------|
| `fda_mcp` | Drug labels, adverse events, recalls | JSON dict |
| `ct_gov_mcp` | ClinicalTrials.gov trials | **Markdown string** |
| `pubmed_mcp` | PubMed literature | JSON dict |
| `nlm_codes_mcp` | ICD-10/11, HCPCS, NPI codes | JSON dict |
| `who_mcp` | WHO health statistics | JSON dict |
| `sec_edgar_mcp` | SEC financial filings | JSON dict |
| `healthcare_mcp` | CMS Medicare data | JSON dict |
| `financials_mcp` | Yahoo Finance, FRED economic data | JSON dict |
| `datacommons_mcp` | Population/disease statistics | JSON dict |
| `opentargets_mcp` | Target validation, genetics | JSON dict |
| `pubchem_mcp` | Compound properties | JSON dict |
| `uspto_patents_mcp` | USPTO patents | JSON dict |

**Critical**: CT.gov is the ONLY server that returns markdown - all others return JSON.

**Documentation**: Each server has detailed API guide in `.claude/.context/mcp-tool-guides/`

---

## Progressive Disclosure System

### MCP Tool Guides (Always available)
Agent reads these to understand API parameters and response formats:
- `.claude/.context/mcp-tool-guides/clinicaltrials.md`
- `.claude/.context/mcp-tool-guides/fda.md`
- `.claude/.context/mcp-tool-guides/pubmed.md`
- [10 more...]

### Code Examples (Read on-demand)
Agent reads these ONLY when needed for current query:
- `.claude/.context/code-examples/ctgov_markdown_parsing.md` - CT.gov markdown parsing
- `.claude/.context/code-examples/fda_json_parsing.md` - FDA JSON parsing
- `.claude/.context/code-examples/multi_server_query.md` - Combining multiple servers
- `.claude/.context/code-examples/skills_library_pattern.md` - Skills library best practices
- `.claude/.context/code-examples/data_validation_pattern.md` - Data validation and error handling

**Benefit**: Agent loads 0-2 examples per query instead of all examples always.

### Pattern Discovery (Skills Evolution)
**NEW**: Agent discovers and reuses patterns from existing skills before creating new ones.

**How it works**:
1. User asks for new query (e.g., "Get ADC trials")
2. Agent checks `.claude/skills/` for similar implementations
3. Agent reads reference skill (e.g., `get_glp1_trials.py`)
4. Agent applies proven patterns (pagination, parsing, etc.)
5. Agent generates new skill following same structure

**Discovery methods**:
- **Index-based**: Read `.claude/skills/index.json` → Filter by server/pattern → Select best match
- **Directory-based**: List `.claude/skills/get_*_trials.py` → Identify similar → Read implementation

**Benefits**:
- ✅ **Quality**: Learn from battle-tested implementations (not theoretical examples)
- ✅ **Consistency**: All skills follow same patterns and conventions
- ✅ **Completeness**: Example: `get_glp1_trials.py` has pagination → new trials skills get it automatically
- ✅ **Efficiency**: Don't re-solve problems (pagination, parsing already working)

**Example pattern reuse**:
```
Query: "Get ADC trials"
↓
Agent checks: .claude/skills/get_*_trials.py
↓
Agent finds: get_glp1_trials.py (has pagination!)
↓
Agent reads: Pagination logic (lines 15-64)
↓
Agent applies: Same pattern to ADC query
↓
Result: All ADC trials (not just first 1000)
```

**Skills Index**: `.claude/skills/index.json` contains:
- Patterns demonstrated by each skill
- Best reference skills for each pattern category
- Technical details (pagination method, regex patterns)
- Quick discovery without reading all files

**Pattern Documentation**: `.claude/.context/code-examples/` includes:
- `ctgov_pagination_pattern.md` - Extracted from `get_glp1_trials.py`
- `fda_json_parsing.md` - FDA response handling
- `multi_server_query.md` - Combining multiple servers

---

## Skills Library Pattern (Two-Phase + Folder Structure)

Following Anthropic's pattern with two-phase persistence and folder structure:

**Phase 1: Agent Execution**
1. **Define reusable function** that encapsulates logic
2. **Execute and display** summary
3. **Return skill code in folder format** to main agent:
   - Skill folder name
   - SKILL.md (with YAML frontmatter)
   - Python script

**Phase 2: Main Agent Persistence**
4. **Extract components from response** (parse folder name and code blocks)
5. **Create folder structure** `.claude/skills/[skill-folder-name]/`
6. **Save SKILL.md** with frontmatter (Write tool)
7. **Create scripts/** subdirectory
8. **Save Python function** to `scripts/[function_name].py` (Write tool)
9. **Update index.json** with folder structure entry

**Why two-phase?**
- Sub-agents cannot directly persist files to filesystem
- Main agent has reliable Write tool access
- Clean separation: Agent executes, main agent persists

**Code extraction pattern**:
Sub-agent returns response with code blocks:
```
Found 363 ADC trials.

Python skill:
\```python
import sys
...
\```

Documentation:
\```markdown
# get_adc_trials
...
\```
```

Main agent extracts code blocks and saves files. If extraction fails, main agent can reconstruct from execution results.

### Skill File Standards

**Every skill must be both importable AND executable**:

```python
import sys
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_kras_inhibitor_trials():
    """Get KRAS inhibitor clinical trials across all phases.

    Returns:
        dict: Contains total_count and trials_summary
    """
    result = search(term="KRAS inhibitor", pageSize=100)
    # ... processing logic ...
    return {'total_count': count, 'trials_summary': result}

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    result = get_kras_inhibitor_trials()
    print(f"Total trials found: {result['total_count']}")
    print(result['trials_summary'])
```

**Benefits**:
- ✅ Importable: `from .claude.skills.kras_inhibitor_trials.scripts.get_kras_inhibitor_trials import get_kras_inhibitor_trials`
- ✅ Executable: `PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/kras-inhibitor-trials/scripts/get_kras_inhibitor_trials.py`
- ✅ Testable: Can run directly to validate data collection
- ✅ Debuggable: Easy to test individual skills in isolation

**Agent discovery**: Agent can read `.claude/skills/index.json` or skill .md files to discover available capabilities.

**Evolutionary**: Skills library grows over time, building higher-level abstractions.

---

## Data Output Strategy

### In-Memory Processing (Default)
- Code processes data in execution environment
- Only summary printed to conversation
- No files saved
- **98.7% token reduction benefit**

### File Persistence (Optional)
When user explicitly requests data export:
- Save to `data_dump/YYYY-MM-DD_[topic]/`
- Use for large datasets, expensive queries, reproducibility
- NOT version controlled (.gitignore)

**Rule**: Default to in-memory unless user requests export.

### Report Persistence (Strategic Analyses)
When strategic agents produce substantial analyses:
- Save to `reports/{agent_type}/YYYY-MM-DD_{topic}.md`
- Use templates from `.claude/.context/templates/`
- Version controlled (shows evolution over time)
- Includes YAML frontmatter with metadata

**Available templates**:
- `competitive-landscape-report.md` - Competitive intelligence (4000-6000 words)
- See `.claude/.context/templates/report-template-guide.md` for standards

**Report structure**:
```markdown
---
title: {Therapeutic Area} Competitive Landscape
date: YYYY-MM-DD
analyst: competitive-landscape-analyst
data_sources:
  - get_kras_inhibitor_trials: 363 trials
  - get_kras_inhibitor_fda_drugs: 2 drugs
---

# Executive Summary
[2-3 paragraphs]

# Data Summary
[Transparency on sources]

# Analysis
[Core strategic analysis]

# Actionable Recommendations
[Prioritized with timelines]
```

---

## Design Principles

### 1. Progressive Disclosure
- Load only MCP tool guides needed
- Load only code examples needed
- Don't load all 12 servers' docs upfront
- Agent decides what to read based on query

### 2. Skills Library
- Save reusable functions to `.claude/skills/`
- Build toolbox over time
- Future queries import and reuse
- Agent evolves expertise across sessions

### 3. In-Memory Processing
- Data processed in execution environment
- Never enters model context
- Only summaries flow to conversation
- Maximum token efficiency

### 4. Single Source of Truth
- MCP tool guides: API documentation
- Code examples: Patterns and best practices
- Skills library: Reusable implementations
- No duplication across files

### 5. Metadata-Driven Strategic Agents
- Strategic agents declare data needs via YAML metadata
- Main agent reads metadata and orchestrates data collection
- Agent body focuses on capabilities (WHAT), metadata specifies data (HOW)
- Small metadata footprint (~25 lines) supports 100+ capabilities

---

## Metadata-Driven Pattern (Layer 2: Main Agent Orchestration)

When user invokes strategic agent (`@agent-competitive-landscape-analyst`):

### Step 1: Read Agent Metadata
Main agent reads `.claude/agents/{agent_name}.md` YAML frontmatter:
```yaml
data_requirements:
  always:  # Core data always collected
    - type: clinical_trials
      pattern: get_{therapeutic_area}_trials
  contextual:  # Optional based on query
    - type: patents
      pattern: get_{therapeutic_area}_patents
      trigger: keywords("IP", "patent")
```

### Step 2: Infer Parameters from Query
Extract from user query:
- **therapeutic_area**: Disease/drug class/mechanism (e.g., "KRAS inhibitor", "GLP-1")
- **company**: Company name if mentioned (e.g., "Pfizer", "Merck")
- **keywords**: Trigger words for contextual data ("IP", "financial", "publications")

**Example**: "Analyze KRAS inhibitor competitive landscape"
→ therapeutic_area = "KRAS inhibitor", no company, no special keywords

### Step 3: Apply Skill Patterns
Transform patterns with inferred parameters:
- `get_{therapeutic_area}_trials` → `get_kras_inhibitor_trials`
- `get_{therapeutic_area}_fda_drugs` → `get_kras_inhibitor_fda_drugs`
- Contextual skills only added if triggers match

### Step 4: Check/Create/Execute Skills
For each required skill:
1. Check: Does `.claude/skills/{skill_name}.py` exist?
2. If missing: Task(pharma-search-specialist) → Create skill → Save with Write tool
3. Execute: Bash(PYTHONPATH=scripts:$PYTHONPATH python {skill_name}.py) → Collect data
4. Validate: Ensure data collection succeeded (non-empty results, expected format)

### Step 4.5: Show Data Collection Summary
Display summary to user for transparency:
```
Data Collection Complete:
✓ Clinical Trials: 363 KRAS inhibitor trials found
✓ FDA Approved Drugs: 2 approved (LUMAKRAS, KRAZATI)

Invoking competitive-landscape-analyst with collected data...
```

### Step 5: Invoke Strategic Agent with Data
Format prompt with collected data:
```
Analyze KRAS inhibitor competitive landscape.

Data available:
1. Clinical Trials: [execution results from get_kras_inhibitor_trials]
2. FDA Approved Drugs: [execution results from get_kras_inhibitor_fda_drugs]

Provide strategic analysis including competitive positioning,
market entry timing, partnership opportunities, and recommendations.
```

Task(competitive-landscape-analyst, prompt_with_data)

### Step 6: Persist Report and Return Analysis
After strategic agent returns analysis:
1. Save report to `reports/{agent_type}/YYYY-MM-DD_{therapeutic_area_slug}.md`
2. Use Write tool to persist analysis for future reference
3. Return summary to user

**Report Structure**:
```markdown
---
title: {Therapeutic Area} Competitive Landscape
date: YYYY-MM-DD
analyst: {agent_name}
therapeutic_area: {therapeutic_area}
data_sources:
  - {skill_1} ({data_count})
  - {skill_2} ({data_count})
---

[Strategic analysis content]
```

**Benefits**:
- ✅ Preserves strategic work product across sessions
- ✅ Version history via git (shows evolution of analyses)
- ✅ Shareable artifacts for stakeholders
- ✅ Future agents can reference prior analyses

### Key Benefits
- ✅ Strategic agent body unchanged (only metadata added)
- ✅ Main agent logic is generic (works for all strategic agents)
- ✅ Smart inference (same pattern, different parameters)
- ✅ Contextual data (only collected when triggered)
- ✅ Small metadata (~6 data sources support 100+ capabilities)

---

## Common Query Patterns

### FDA Query (JSON response)
1. Read: `.claude/.context/mcp-tool-guides/fda.md`
2. Read: `.claude/.context/code-examples/fda_json_parsing.md`
3. Generate code using `.get()` methods
4. Save skill

### CT.gov Query (Markdown response)
1. Read: `.claude/.context/mcp-tool-guides/clinicaltrials.md`
2. Read: `.claude/.context/code-examples/ctgov_markdown_parsing.md`
3. Generate code using regex parsing
4. Save skill

### Multi-Server Query
1. Read multiple tool guides
2. Read: `.claude/.context/code-examples/multi_server_query.md`
3. Generate code handling different response formats
4. Save skill

---

## Token Efficiency Comparison

| Method | Tokens | Pattern |
|--------|--------|---------|
| Direct MCP call | 60,000 | ❌ Raw data in context |
| Old scripts | 2,000 | ⚠️ Data flows through context |
| **Code execution + Progressive disclosure** | **500** | ✅ **98.7% reduction** |

---

## Quick Start

**User**: "What GLP-1 drugs are approved for obesity?"

**Agent flow**:
1. Identifies: FDA query
2. Reads: `fda.md` + `fda_json_parsing.md`
3. Generates Python code
4. Executes via Bash tool
5. Returns: summary + skill code + docs
6. Main agent saves: `.claude/skills/get_glp1_obesity_drugs.py`

**Context used**: ~500 tokens (tool guide + example + generated code + summary)

**Context saved**: ~59,500 tokens (full FDA JSON never enters context)

---

## Architecture Summary

```
User Query
    ↓
pharma-search-specialist agent
    ↓
Progressive Disclosure:
  - Read MCP tool guide (API docs)
  - Read code example (pattern)
    ↓
Generate Python code
    ↓
Execute code (Bash tool)
    ↓
Code execution:
  - Query MCP server
  - Process data in-memory
  - Print summary
    ↓
Agent returns:
  - Summary
  - Skill code (.py)
  - Documentation (.md)
    ↓
Main Claude Code agent
    ↓
Save skills (Write tool):
  - .claude/skills/[function].py
  - .claude/skills/[function].md
    ↓
Summary → User (500 tokens)
Skills library grows ✓
```

**Result**: 98.7% context reduction, progressive disclosure, evolutionary expertise, reliable persistence.
