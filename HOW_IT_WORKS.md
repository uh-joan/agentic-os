# How CLAUDE.md and scripts/ Work Together

## The Contradiction (CURRENT STATE)

**CLAUDE.md says**:
- Lines 5-10: "Agents generate **executable Python scripts**"
- Lines 6-7: "Claude Code saves scripts to `scripts/[domain]/` and executes via `python3 script.py`"

**Reality**:
- ❌ No agents currently generate Python scripts
- ✅ Scripts exist in `scripts/` but were manually written
- ✅ Planning agents (pharma-search-specialist) generate JSON plans, NOT scripts
- ✅ Analytical agents generate markdown, NOT scripts

## Current Architecture (ACTUAL)

### 1. Planning Agents → JSON Plans
```
User: "Find Phase 3 obesity trials"
  ↓
pharma-search-specialist agent
  ↓
JSON plan: [
  {step: 1, tool: "ct-gov-mcp", method: "search", params: {...}},
  {step: 2, tool: "ct-gov-mcp", method: "search", params: {...}}
]
  ↓
Claude Code executes each step (direct MCP calls)
  ↓
Saves to data_dump/YYYY-MM-DD_HHMMSS_ctgov_obesity/
```

**NOT**: Agent generates Python script

### 2. Analytical Agents → Markdown
```
User: "Analyze the obesity data"
  ↓
epidemiology-analyst agent
  ↓
Reads: data_dump/[folder]/
  ↓
Generates: Markdown analysis
  ↓
Claude Code saves to temp/epidemiology_analysis_*.md
```

**NOT**: Agent generates Python script

### 3. Manual Scripts (Existing in scripts/)

These are **pre-written utility scripts**, NOT agent-generated:

**scripts/analysis/obesity/obesity_pipeline_analysis.py**:
- Manually written Python script
- Makes MCP calls directly using `mcp.client`
- Used for reproducible analysis
- Can be run anytime: `python3 scripts/analysis/obesity/obesity_pipeline_analysis.py`

**scripts/mcp/client.py**:
- MCP client wrapper
- Provides `get_client()` function
- Used by manual scripts to call MCP tools

**scripts/utils/fda_query_validator.py**:
- FDA query optimization utility
- Adds count parameters to avoid token limits
- Used by Claude Code when making FDA queries

## What Should Happen (INTENDED DESIGN)

CLAUDE.md describes a **future vision** where:

1. **Code-Generating Agents** exist
2. User asks: "Analyze Phase 3 NASH programs"
3. Agent generates Python script on-the-fly
4. Claude Code saves to `scripts/competitive/nash/nash_phase3.py`
5. Claude Code executes: `python3 scripts/competitive/nash/nash_phase3.py`
6. Results displayed to user

**This was the competitive-specialist pattern you just deleted.**

## Current vs Intended

| Component | Current Reality | CLAUDE.md Says | Status |
|-----------|----------------|----------------|--------|
| **Planning Agents** | Generate JSON plans | Generate scripts | ❌ Mismatch |
| **Analytical Agents** | Generate markdown | Generate scripts | ❌ Mismatch |
| **scripts/ folder** | Manual utilities | Agent-generated | ❌ Mismatch |
| **Execution** | Direct MCP calls | Execute scripts | ❌ Mismatch |

## What scripts/ Actually Contains

```
scripts/
├── analysis/
│   ├── obesity/
│   │   ├── obesity_pipeline_analysis.py     # Manual script
│   │   └── obesity_active_pipeline_analysis.py
│   └── modules/                              # Shared functions
│       └── competitive.py
├── mcp/
│   ├── client.py                             # MCP wrapper
│   ├── queries/                              # Query helpers
│   ├── servers/                              # Server utilities
│   ├── examples/                             # Example scripts
│   └── tests/                                # Test suites
└── utils/
    └── fda_query_validator.py                # FDA optimization
```

**All manually written, NOT agent-generated.**

## How to Fix the Documentation

### Option 1: Update CLAUDE.md to Match Reality

Remove "code-first" claims, document actual pattern:

```markdown
## Agent Types

### 1. Planning Agents
**Pattern**: User query → JSON plan → Claude Code executes MCP → data_dump/

### 2. Analytical Agents
**Pattern**: Reads data_dump/ → Markdown analysis → temp/

## scripts/ Folder

Contains **manual utility scripts** for:
- MCP client wrappers (scripts/mcp/client.py)
- Reusable analysis scripts (scripts/analysis/)
- Testing utilities (scripts/mcp/tests/)
- Query validators (scripts/utils/)

These are NOT agent-generated, they are manually maintained.
```

### Option 2: Implement Code-First (Future)

Create agents that actually generate Python scripts:
- Requires building code-generating agent pattern
- Agent reads context, generates full Python script
- Claude Code saves to scripts/
- Claude Code executes script

**This was competitive-specialist (just deleted).**

### Option 3: Hybrid Approach (Recommended)

Keep both patterns:
- **Planning agents**: JSON plans (current, works well)
- **Manual scripts**: Utilities and reproducible analyses (current, useful)
- **Future**: Add code-generating agents when specific use case emerges

Update CLAUDE.md to clarify:
```markdown
## Execution Patterns

### 1. JSON Plans (Current - Planning Agents)
Agents generate JSON → Claude Code executes MCP queries

### 2. Manual Scripts (Current - Utilities)
Pre-written Python in scripts/ → Run when needed

### 3. Code Generation (Future - When Needed)
Agents generate Python → Claude Code saves and executes
```

## Recommendation

**Fix CLAUDE.md to match reality**:

1. Remove misleading "agents generate scripts" claims (lines 5-10)
2. Document actual JSON plan pattern for planning agents
3. Document actual markdown pattern for analytical agents
4. Clarify scripts/ contains manual utilities, NOT agent-generated code
5. Keep "code-first" as aspirational goal for future, but mark as "not implemented"

**Current CLAUDE.md is documentation fiction, not reality.**

## Example: How Obesity Analysis Actually Works Today

**User asks**: "Analyze obesity pipeline"

**What CLAUDE.md says happens**:
1. Agent generates `scripts/analysis/obesity/obesity_pipeline.py`
2. Claude Code executes script
3. Results displayed

**What actually happens**:
1. Claude Code runs **pre-existing** script: `scripts/analysis/obesity/obesity_pipeline_analysis.py`
2. Script makes MCP calls directly via `mcp.client`
3. Results displayed

**OR**:

1. pharma-search-specialist generates JSON plan
2. Claude Code executes MCP calls directly (no script generation)
3. Results saved to data_dump/
4. epidemiology-analyst reads data_dump/, generates markdown
5. Claude Code saves markdown to temp/

**No Python scripts are generated by agents in either case.**
