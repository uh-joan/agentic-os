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
│       └── skill-frontmatter-template.yaml
├── skills/                             # Reusable functions
│   ├── index.json                      # Skills discovery index
│   │
│   ├── glp1-trials/                    # Folder structure (Anthropic format)
│   │   ├── SKILL.md                    # YAML frontmatter + documentation
│   │   └── scripts/
│   │       └── get_glp1_trials.py      # Executable function
│   │
│   ├── glp1-fda-drugs/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── get_glp1_fda_drugs.py
│   │
│   └── [Some legacy flat-structure skills for backward compatibility]
│
├── tools/                              # Platform utilities
│   ├── skill_discovery/                # Index-based skill discovery
│   │   ├── index_query.py              # Level 1: Fast index queries
│   │   ├── health_check.py             # Level 2: Health verification
│   │   ├── semantic_matcher.py         # Level 3: Semantic matching
│   │   ├── strategy.py                 # Level 4: Strategy decisions
│   │   └── index_updater.py            # Index maintenance
│   ├── verification/                   # Closed-loop verification
│   │   └── verify_skill.py             # Autonomous skill verification
│   ├── init_skill.py                   # Initialize new skill
│   ├── package_skill.py                # Migrate flat to folder
│   ├── discover_skills.py              # Find skills (both formats)
│   └── parse_skill_metadata.py         # Parse YAML frontmatter
│
└── mcp/                                # MCP infrastructure
    ├── client.py                       # MCP client (spawns servers, manages JSON-RPC)
    └── servers/                        # Python function stubs
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

## Skills Architecture

### Folder Structure

Skills use Anthropic's folder format for modularity and discoverability:

```
skill-name/
├── SKILL.md              # YAML frontmatter + documentation
└── scripts/
    └── skill_function.py # Executable Python function
```

**Benefits**:
- ✅ **Standardized metadata**: YAML frontmatter enables intelligent discovery
- ✅ **Self-contained packages**: Easy to share and distribute
- ✅ **Code execution**: Maintains 98.7% token efficiency (not instruction-based)
- ✅ **Both importable and executable**: Skills can be imported or run standalone

**Note**: Some legacy flat-structure skills (`.py` + `.md` pairs) exist for backward compatibility.

### Discovery & Strategy

Skills are discovered through a four-level intelligent system:

**Level 1: Index Query** (`.claude/tools/skill_discovery/index_query.py`)
- Fast lookup in `index.json` without filesystem scanning
- Filter by server, category, pattern, complexity
- < 100ms query time

**Level 2: Health Check** (`.claude/tools/skill_discovery/health_check.py`)
- Verify files exist and are executable
- Syntax validation (Python compiles)
- Structure validation (folder format, frontmatter)
- Import testing (dependencies available)

**Level 3: Semantic Matching** (`.claude/tools/skill_discovery/semantic_matcher.py`)
- Find skills matching intent, not just exact names
- Score by therapeutic area, data type, patterns
- Identify reuse/adaptation opportunities

**Level 4: Strategy Decision** (`.claude/tools/skill_discovery/strategy.py`)
- **REUSE**: Healthy skill exists, use as-is
- **ADAPT**: Similar skill exists, fork and modify
- **CREATE**: No match, create from reference pattern
- Automatic fallback on execution failure

**Index Maintenance** (`.claude/tools/skill_discovery/index_updater.py`)
- Automatic updates when skills created/modified
- Health status tracking
- Filesystem consistency validation

**Benefits**:
- ✅ **Fast**: Index query vs directory scanning
- ✅ **Reliable**: Health checks detect broken skills before execution
- ✅ **Intelligent**: Semantic matching finds non-obvious reuse opportunities
- ✅ **Self-healing**: Automatic strategy fallback on failure

### Two-Phase Persistence Pattern

Following Anthropic's pattern for reliable skill creation:

**Phase 1: Agent Execution**
1. pharma-search-specialist generates Python code
2. Executes code via Bash tool
3. Verifies results with closed-loop validation
4. Returns skill code (folder name, SKILL.md, Python script)

**Phase 2: Main Agent Persistence**
5. Main agent extracts components from response
6. Creates folder structure in `.claude/skills/`
7. Saves SKILL.md with YAML frontmatter (Write tool)
8. Creates `scripts/` subdirectory
9. Saves Python function (Write tool)
10. Updates `index.json` (via index_updater.py)

**Why two-phase?**
- Sub-agents cannot directly persist files to filesystem
- Main agent has reliable Write tool access
- Clean separation: Sub-agent executes, main agent persists

### Skill File Standards

**Every skill must be both importable AND executable**:

```python
import sys
sys.path.insert(0, ".claude")
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

**Usage**:
- **Import**: `from .claude.skills.kras_trials.scripts.get_kras_inhibitor_trials import get_kras_inhibitor_trials`
- **Execute**: `PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/kras-trials/scripts/get_kras_inhibitor_trials.py`
- **Test**: Run directly to validate data collection
- **Debug**: Easy to test individual skills in isolation

**Discovery**: Agent reads `.claude/skills/index.json` to discover available capabilities.

**Evolution**: Skills library grows over time, building higher-level abstractions.

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

## Verification Infrastructure (Closing the Agentic Loop)

**Purpose**: Autonomous skill verification to ensure completeness and correctness

**Reference**: https://www.pulsemcp.com/posts/closing-the-agentic-loop-mcp-use-case

### Verification Script

**Location**: `.claude/tools/verification/verify_skill.py`

**Usage** (by pharma-search-specialist agent):
```bash
python3 .claude/tools/verification/verify_skill.py \
  --bash-output "$(execution output)" \
  --execution-output "$(python stdout)" \
  --server-type ct_gov \
  --json
```

**Verification Checks**:
1. **Execution**: Code runs without errors (exit code 0, no exceptions)
2. **Data Retrieved**: Query returned results (count > 0)
3. **Pagination**: All records retrieved (no truncation)
4. **Executable**: Skill runs standalone (has `if __name__ == "__main__":`)
5. **Schema**: Data format valid (required fields present)

**Auto-Approval Required**:
The verification script must be pre-approved for pharma-search-specialist agent to run autonomously.

Add to Claude Code configuration:
```bash
Bash(python3 .claude/tools/verification/verify_skill.py:*)
```

### Agent Integration

The pharma-search-specialist agent MUST:
1. Execute Python code via Bash tool
2. Run verification checks on results
3. Self-correct if any check fails (max 3 attempts)
4. Return only verified, complete skill code
5. Never ask user to validate results

This enables "closing the agentic loop" - the agent autonomously verifies task completion without requiring user validation.

---

## Progressive Disclosure

The agent loads only the documentation and examples needed for the current query, not everything upfront.

### MCP Tool Guides
Agent reads these to understand API parameters and response formats:
- `.claude/.context/mcp-tool-guides/clinicaltrials.md`
- `.claude/.context/mcp-tool-guides/fda.md`
- `.claude/.context/mcp-tool-guides/pubmed.md`
- [10 more servers...]

### Code Examples (On-Demand)
Agent reads these ONLY when needed:
- `ctgov_markdown_parsing.md` - CT.gov markdown parsing
- `fda_json_parsing.md` - FDA JSON parsing
- `multi_server_query.md` - Combining multiple servers
- `skills_library_pattern.md` - Skills library best practices
- `data_validation_pattern.md` - Data validation and error handling

### Reference Skills (Pattern Reuse)
Agent discovers and reuses patterns from existing skills:

1. User asks for new data (e.g., "Get ADC trials")
2. Strategy system determines best approach (REUSE/ADAPT/CREATE)
3. If ADAPT or CREATE: Agent reads reference skill for patterns
4. Agent applies proven patterns (pagination, parsing, etc.)
5. New skill follows same structure as reference

**Example**:
```
Query: "Get ADC trials"
↓
Strategy: CREATE (no ADC skill exists)
↓
Reference: get_glp1_trials (has pagination, markdown parsing)
↓
Agent reads: Pagination logic from reference
↓
Agent applies: Same pattern to ADC query
↓
Result: Complete ADC trials skill with pagination
```

**Benefits**:
- ✅ Load 0-2 examples per query (not all examples always)
- ✅ Learn from battle-tested implementations (not just theory)
- ✅ Consistency across all skills (same patterns, conventions)
- ✅ Completeness inherited (reference has pagination → new skill gets it)

**Reference**: Implementation details in `.claude/.context/implementation-plans/index-based-skill-discovery.md`

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
- `competitive-landscape-report.md` - Competitive intelligence (1500-2500 words, concise format)
- See `.claude/.context/templates/report-template-guide.md` for standards

**Report structure**:
```markdown
---
title: {Therapeutic Area} Competitive Landscape
date: YYYY-MM-DD
analyst: competitive-landscape-analyst
therapeutic_area: {therapeutic_area}

# SOURCE METADATA (REQUIRED)
data_sources_mcp_verified:
  - get_kras_inhibitor_trials: 363 trials (source: ClinicalTrials.gov, date: 2025-12-03)
  - get_kras_inhibitor_fda_drugs: 2 drugs (source: FDA Drug Database, date: 2025-12-03)

data_sources_internal_knowledge:
  - Market size estimates: $5-8B by 2030 [estimated from industry analyst consensus]

source_validation:
  mcp_verified_claims: 87
  analytical_insights: 34
  internal_knowledge: 8  # Target: <20% of total claims
---

# Executive Summary
[2-3 paragraphs with inline citations]

# Data Summary
[Transparency on sources with query dates]

# Analysis
[Core strategic analysis with >70% MCP-verified citations]

# Actionable Recommendations
[Prioritized with timelines and success metrics]
```

**Source Attribution Requirements**:
- >70% of major claims must cite MCP-verified data
- <20% of claims can use internal knowledge
- All claims must have inline citations: `(**source**: ClinicalTrials.gov, 2025-12-03)`
- Reports must pass `verify_report_attribution.py` before being returned to user

**Verification Workflow**:
```bash
# After generating report, agent runs:
python3 .claude/tools/verification/verify_report_attribution.py \
  --report reports/competitive-landscape/YYYY-MM-DD_{topic}.md \
  --json

# Expected result: {"valid": true, "errors": [], "metrics": {...}}
# If valid: false, agent fixes errors and re-verifies (max 2 iterations)
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

### 6. Source Citation and Data Provenance
- Every output must be traceable to authoritative data sources
- Prefer MCP-verified data over internal knowledge
- Clear distinction between data types (MCP data vs analysis vs internal knowledge)
- Complete source metadata enables reproducibility and trustability

---

## Source Citation and Data Provenance

**Core Principle**: Every output—reports, agent responses, skill results—must be traceable to authoritative data sources.

### Source Hierarchy (Trustability Order)

**1. MCP-Verified Data (MOST TRUSTABLE)**
- Data retrieved from MCP servers (ClinicalTrials.gov, FDA, PubMed, SEC, WHO, CDC, etc.)
- Always includes: source name, query date, query parameters
- Citation format: `(source: ClinicalTrials.gov, 2025-12-03)`
- Use: Preferred for ALL factual claims

**2. Published Literature (HIGH TRUSTABILITY)**
- Peer-reviewed publications from PubMed
- Always includes: Author, journal, year, PMID/DOI
- Citation format: `(Jastreboff et al., NEJM 2022, PMID: 35658024)`
- Use: Clinical efficacy, trial results, scientific evidence

**3. Analytical Insights (DERIVED, MODERATE TRUSTABILITY)**
- Calculations, synthesis, or analysis derived from MCP data
- Citation format: `[analysis based on ClinicalTrials.gov data]`
- Use: Patterns, trends, comparisons synthesized from MCP data

**4. Internal Knowledge (LOWEST TRUSTABILITY - MINIMIZE)**
- Industry consensus, market projections, estimates from training data
- Citation format: `[estimated from industry consensus]` or `[internal knowledge]`
- Use: ONLY when MCP data unavailable, always explicitly labeled
- Constraint: Should be <20% of claims in any report

### Source Attribution Standards

**Skills**:
- Every skill returns `source_metadata` dict with: source, mcp_server, query_date, query_params, data_count, data_type
- Verified by `verify_source_attribution.py` before adding to library
- Summary includes source citation

**Agents**:
- pharma-search-specialist: Generates skills with source metadata (mandatory)
- competitive-landscape-analyst: Cites sources inline in reports (every major claim)
- All agents: Prefer MCP data over internal knowledge, explicitly label internal knowledge

**Reports**:
- Frontmatter: Complete `data_sources_mcp_verified` and `data_sources_internal_knowledge` sections
- Inline citations: Every major claim (>70%) cited with source
- Tables/figures: Source attribution in caption or footer
- Source validation metrics: Track MCP-verified claims vs internal knowledge usage

### Benefits

✅ **Trustability**: Every claim traceable to authoritative source
✅ **Reproducibility**: Query parameters enable re-execution of data collection
✅ **Transparency**: Clear distinction between MCP data, analysis, and internal knowledge
✅ **Scientific rigor**: Follows academic citation standards (author-year-PMID for literature)
✅ **Compliance**: Audit trail for regulatory/legal requirements
✅ **Quality control**: Automated verification prevents unsourced claims from entering reports

---

## Metadata-Driven Pattern (Layer 2: Main Agent Orchestration)

### Step 0: Pre-Flight Skill Discovery (MANDATORY for Data Queries)

**Before invoking pharma-search-specialist or collecting data**, run intelligent strategy check to avoid duplicate skill creation.

#### For Direct Data Queries

When user asks for data (not strategic analysis):
- "Get Abbott segment financials"
- "Find EGFR inhibitor trials"
- "Get GLP-1 FDA approved drugs"

**MANDATORY workflow**:

1. **Infer parameters from query**:
```python
# Extract from user query:
# - skill_name: Descriptive name for the skill
# - therapeutic_area: Disease/drug class/topic
# - data_type: trials | fda_drugs | patents | publications
# - servers: comma-separated MCP servers needed

# Examples:
"Get GLP-1 trials" →
  skill_name = "glp1_trials"
  therapeutic_area = "GLP-1"
  data_type = "trials"
  servers = "ct_gov_mcp"

"Find orphan drugs expected to be approved" →
  skill_name = "orphan_drug_upcoming_approvals"
  therapeutic_area = "orphan drugs"
  data_type = "fda_drugs"
  servers = "fda_mcp"

"Get EGFR inhibitor trials" →
  skill_name = "egfr_inhibitor_trials"
  therapeutic_area = "EGFR inhibitor"
  data_type = "trials"
  servers = "ct_gov_mcp"
```

2. **Run strategy check**:
```bash
python3 .claude/tools/skill_discovery/strategy.py \
  --skill '{inferred_skill_name}' \
  --therapeutic-area '{therapeutic_area}' \
  --data-type {trials|fda_drugs|patents|publications} \
  --servers {comma_separated_servers} \
  --query '{original_user_query}' \
  --json
```

**CRITICAL**: Always include `--query` with the original user query. This enables trigger keyword matching to identify intent-specific skills like `companies-by-moa` when user asks "which companies are working on..."

3. **Parse strategy result and act**:

**REUSE Strategy** (skill exists and is healthy):
```python
# Execute existing skill directly
Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {strategy['skill']['script']}")

# Parse and return results to user
# DO NOT invoke pharma-search-specialist
# Skill already exists - no new code needed!
```

**ADAPT/CREATE Strategy** (needs new skill):
```python
# Invoke pharma-search-specialist WITH strategy context
Task(
    subagent_type='pharma-search-specialist',
    prompt=f"""Strategy decision: {strategy['strategy']}

    {f"Reference skill: {strategy['reference']['script']}" if 'reference' in strategy else ""}
    {f"Patterns to reuse: {strategy['reference']['patterns_demonstrated']}" if 'reference' in strategy else ""}

    User Query: {user_query}

    {strategy.get('reason', '')}
    """
)
```

**Benefits**:
- ✅ **Zero duplication**: Existing skills reused automatically
- ✅ **80% faster**: Skip agent invocation when skill exists
- ✅ **Consistency**: Parameterized skills handle variations
- ✅ **Quality**: Reference skills validated by strategy system

**Example Flow**:
```
User: "Which companies are working on GLP-1 receptor agonists in obesity?"
↓
Step 0: Infer parameters:
  skill_name = "glp1_obesity_companies"
  therapeutic_area = "GLP-1"
  data_type = "trials"
  servers = "ct_gov_mcp"
  original_query = "Which companies are working on GLP-1 receptor agonists in obesity?"
↓
Run strategy.py:
  python3 .claude/tools/skill_discovery/strategy.py \
    --skill "glp1_obesity_companies" \
    --therapeutic-area "GLP-1" \
    --data-type "trials" \
    --servers "ct_gov_mcp" \
    --query "Which companies are working on GLP-1 receptor agonists in obesity?" \
    --json
↓
Trigger keyword detected: "companies working on" (score: 15)
Returns: REUSE strategy + companies-by-moa skill
↓
Execute: python3 .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py 'GLP-1 receptor agonist' 'obesity'
↓
Return results to user
↓
Result: Correct skill identified via trigger keywords, no pharma-search-specialist invoked!
```

#### For Strategic Agent Invocations

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

### Step 4: Check/Create/Execute Skills (Index-Based Strategy)

For each required skill, use intelligent strategy decision.

**Two Interfaces Available**:
- **CLI** (Bash tool): Use for standalone strategy checks before agent invocation
- **Python API** (Import): Use for programmatic integration in strategic agents

**Step 4.1: Determine Strategy**

*Using Python API (recommended for strategic agents):*
```python
from skill_discovery.strategy import determine_skill_strategy, SkillRequirements

strategy = determine_skill_strategy(
    skill_name='get_kras_inhibitor_trials',
    requirements=SkillRequirements(
        therapeutic_area='KRAS inhibitor',
        data_type='trials',
        servers=['ct_gov_mcp']
    )
)
```

*Using CLI (for Bash tool calls):*
```bash
python3 .claude/tools/skill_discovery/strategy.py \
  --skill "get_kras_inhibitor_trials" \
  --therapeutic-area "KRAS inhibitor" \
  --data-type "trials" \
  --servers "ct_gov_mcp" \
  --json
```

**Step 4.2: Execute Strategy**

- **REUSE** (`strategy.strategy == SkillStrategy.REUSE`):
  ```python
  # Skill exists and is healthy - use as-is
  Bash(f"PYTHONPATH=.claude:$PYTHONPATH python .claude/skills/{strategy.skill['script']}")

  # Validate execution
  if exit_code != 0 or result_count == 0:
      # Mark skill as broken and retry with CREATE strategy
      update_skill_health(skill_name, HealthStatus.BROKEN, ["Execution failed"])
      strategy = determine_skill_strategy(skill_name, requirements)
  ```

- **ADAPT** (`strategy.strategy == SkillStrategy.ADAPT`):
  ```python
  if "migrate structure" in strategy.action_plan:
      # Case A: Skill needs migration (flat → folder)
      Bash("python3 .claude/tools/package_skill.py {skill_name}")
      update_skill_health(skill_name, HealthStatus.HEALTHY, [])

  else:
      # Case B: Fork similar skill for new therapeutic area
      # Read reference skill
      Read(f".claude/skills/{strategy.skill['script']}")

      # Task pharma-search-specialist to adapt
      Task(
          subagent_type='pharma-search-specialist',
          prompt=f"""Create {skill_name} by adapting {strategy.skill['name']}.

          Reference skill: .claude/skills/{strategy.skill['script']}
          New parameters: {requirements.therapeutic_area}
          Reuse patterns: {strategy.skill['patterns_demonstrated']}
          """
      )

  # Execute adapted skill
  Bash(f"PYTHONPATH=.claude:$PYTHONPATH python .claude/skills/{new_skill_script}")

  # Update index with new skill
  Bash(f"python3 .claude/tools/skill_discovery/index_updater.py add ...")
  ```

- **CREATE** (`strategy.strategy == SkillStrategy.CREATE`):
  ```python
  # No matching skill - create from reference pattern
  # Read reference skill for pattern reuse
  Read(f".claude/skills/{strategy.reference['script']}")

  # Task pharma-search-specialist with reference
  Task(
      subagent_type='pharma-search-specialist',
      prompt=f"""Create new skill: {skill_name}

      Requirements: {requirements}
      Reference pattern: {strategy.reference['name']}
      Patterns to include: {strategy.reference['patterns_demonstrated']}

      Follow reference implementation for:
      - Pagination approach
      - Response parsing
      - Error handling
      - Return format
      """
  )

  # pharma-search-specialist returns skill code (with verification via closed loop)
  # Main agent saves files
  Write(f".claude/skills/{folder_name}/SKILL.md", skill_md_content)
  Write(f".claude/skills/{folder_name}/scripts/{skill_name}.py", script_content)

  # Update index (CRITICAL!)
  Bash(f"""python3 .claude/tools/skill_discovery/index_updater.py add \
      --name {skill_name} \
      --folder {folder_name} \
      --servers {','.join(servers)} \
      --patterns {','.join(patterns)} \
      --category {category} \
      --complexity {complexity}
  """)

  # Execute newly created skill
  Bash(f"PYTHONPATH=.claude:$PYTHONPATH python .claude/skills/{folder_name}/scripts/{skill_name}.py")
  ```

**Step 4.3: Validate Data Collection**
```python
# Parse execution output
result = parse_execution_output(bash_output)

if result['success'] and result['count'] > 0:
    print(f"✓ {skill_name}: {result['count']} records collected")
else:
    # Execution failed - mark skill health and retry
    update_skill_health(skill_name, HealthStatus.BROKEN, [result['error']])

    # Retry with CREATE strategy (start fresh)
    strategy = determine_skill_strategy(skill_name, requirements)
    # ... execute CREATE strategy ...
```

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
