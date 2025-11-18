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
│   └── pharma-search-specialist.md     # Agent definition
├── .context/
│   ├── mcp-tool-guides/                # MCP server API documentation
│   │   ├── clinicaltrials.md           # CT.gov API (returns markdown)
│   │   ├── fda.md                      # FDA API (returns JSON)
│   │   ├── pubmed.md
│   │   └── [10 more servers...]
│   └── code-examples/                  # Code patterns (progressive disclosure)
│       ├── ctgov_markdown_parsing.md   # CT.gov pattern
│       ├── fda_json_parsing.md         # FDA pattern
│       ├── multi_server_query.md       # Combining servers
│       └── skills_library_pattern.md   # Skills library pattern
└── skills/                             # Reusable functions (built over time)
    ├── get_glp1_obesity_drugs.py
    ├── get_glp1_obesity_drugs.md
    └── [functions accumulate here...]

scripts/mcp/                            # MCP infrastructure
├── client.py                           # MCP client (spawns servers, manages JSON-RPC)
└── servers/                            # Python function stubs
    ├── fda_mcp/
    ├── ct_gov_mcp/
    └── [12 MCP servers...]
```

---

## pharma-search-specialist Agent

**Defined in**: `.claude/agents/pharma-search-specialist.md`

**Pattern**: User query → Read docs → Generate Python code → Claude Code executes

**Progressive Disclosure Flow**:
1. Identify query type (FDA? CT.gov? Multi-server?)
2. Read relevant tool guide: `.claude/.context/mcp-tool-guides/[server].md`
3. Read relevant code example: `.claude/.context/code-examples/[pattern].md`
4. Generate code following pattern
5. Code saves skill to `.claude/skills/`

**Example**:
- User: "How many Phase 3 obesity trials are recruiting in the US?"
- Agent reads: `clinicaltrials.md` + `ctgov_markdown_parsing.md`
- Agent generates Python code with CT.gov markdown parsing
- Agent executes code via Bash → gets: "36 trials"
- Agent returns: summary + skill code + documentation
- Main agent saves: `.claude/skills/get_us_phase3_obesity_recruiting_trials.py`

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

**Benefit**: Agent loads 0-2 examples per query instead of all examples always.

---

## Skills Library Pattern (Two-Phase)

Following Anthropic's pattern with two-phase persistence:

**Phase 1: Agent Execution**
1. **Define reusable function** that encapsulates logic
2. **Execute and display** summary
3. **Return skill code** to main agent (Python + Markdown)

**Phase 2: Main Agent Persistence**
4. **Save function** to `.claude/skills/[function_name].py` (Write tool)
5. **Save documentation** to `.claude/skills/[function_name].md` (Write tool)

**Why two-phase?**
- Sub-agents cannot directly persist files to filesystem
- Main agent has reliable Write tool access
- Clean separation: Agent executes, main agent persists

**Future reuse**:
```python
from .claude.skills.get_glp1_obesity_drugs import get_glp1_obesity_drugs
brands = get_glp1_obesity_drugs()
```

**Agent discovery**: Agent can read SKILL.md files to discover available capabilities.

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
