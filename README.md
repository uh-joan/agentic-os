# Pharmaceutical Research Intelligence Platform

AI-powered pharmaceutical research system using **Claude Code** with specialized **MCP servers** for drug discovery, clinical trials, regulatory data, and competitive intelligence.

Built on Anthropic's **code execution with MCP pattern** for 98.7% context reduction.

---

## Core Architecture

**Pattern**: Code Execution with MCP (Model Context Protocol)

### How It Works

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
  - .claude/skills/[skill-name]/SKILL.md
  - .claude/skills/[skill-name]/scripts/[function].py
    ↓
Summary → User (500 tokens)
Skills library grows ✓
```

### Key Benefits

- **98.7% context reduction**: Raw data never enters model context (150k → 2k tokens)
- **Progressive disclosure**: Load only docs/examples needed for current query
- **Skills library**: Build reusable function toolbox across sessions
- **Privacy**: Sensitive data stays in execution environment
- **Natural control flow**: Loops, conditionals, error handling in Python

**Reference**: [Anthropic Engineering Blog](https://www.anthropic.com/engineering/code-execution-with-mcp)

---

## Agent System

### Layer 1: Infrastructure Agent (Data Collection)

**pharma-search-specialist** - Creates reusable data collection skills

- **Pattern**: User query → Read docs → Generate Python code → Execute → Return skill
- **Output**: Summary + Python skill + Documentation
- **Location**: `.claude/agents/pharma-search-specialist.md`

**Example Flow**:
```
User: "How many Phase 3 obesity trials are recruiting in the US?"
    ↓
Agent reads: clinicaltrials.md + ctgov_markdown_parsing.md
    ↓
Agent generates Python code with CT.gov markdown parsing
    ↓
Agent executes → "36 trials found"
    ↓
Agent returns: summary + skill code + docs
    ↓
Main agent saves: .claude/skills/us-phase3-obesity-recruiting-trials/
```

### Layer 2: Strategic Agent (Analysis & Synthesis)

**competitive-landscape-analyst** - Competitive intelligence and strategic analysis

- **Pattern**: Metadata-driven data collection → Strategic analysis
- **Input**: Collected data from skills execution
- **Output**: Strategic report with competitive positioning, recommendations
- **Location**: `.claude/agents/competitive-landscape-analyst.md`

**Example Flow**:
```
User: "Analyze KRAS inhibitor competitive landscape"
    ↓
Main agent reads agent metadata → Needs: trials + FDA drugs
    ↓
Main agent checks/creates/executes required skills
    ↓
Main agent invokes analyst with collected data
    ↓
Analyst returns: competitive positioning, market timing, recommendations
    ↓
Report saved: reports/competitive-landscape/YYYY-MM-DD_kras-inhibitor.md
```

---

## Skills Library (v2.0)

**Current Skills** (13 active):

### Clinical Trials (CT.gov)
- `adc-trials` - Antibody-drug conjugate trials with pagination
- `braf-inhibitor-trials` - BRAF inhibitor trials
- `covid19-vaccine-trials-recruiting` - COVID-19 vaccine trials
- `glp1-trials` - GLP-1 trials (1803 trials, full pagination)
- `kras-inhibitor-trials` - KRAS inhibitor trials
- `phase2-alzheimers-trials-us` - Phase 2 Alzheimer's trials (US)
- `rheumatoid-arthritis-trials` - Rheumatoid arthritis trials
- `us-phase3-obesity-recruiting-trials` - Phase 3 obesity trials

### FDA Drugs
- `braf-inhibitor-fda-drugs` - FDA approved BRAF inhibitors
- `glp1-diabetes-drugs` - GLP-1 drugs for diabetes
- `glp1-fda-drugs` - FDA approved GLP-1 drugs (21 drugs, deduplication)
- `kras-inhibitor-fda-drugs` - FDA approved KRAS inhibitors
- `rheumatoid-arthritis-fda-drugs` - FDA approved RA drugs

### Folder Structure (Anthropic Format)

```
.claude/skills/
├── index.json                          # Skills discovery index (v2.0)
├── README.md                           # Skills library documentation
└── [skill-name]/                       # Each skill is self-contained
    ├── SKILL.md                        # YAML frontmatter + documentation
    └── scripts/
        └── [function_name].py          # Executable Python function
```

### Skills Discovery

```bash
# Find all skills
python3 .claude/scripts/discover_skills.py

# Find skills by pattern (e.g., pagination)
python3 -c "from discover_skills import find_skill_by_pattern; print(find_skill_by_pattern('pagination'))"

# Find skills by MCP server
python3 -c "from discover_skills import find_skill_by_server; print(find_skill_by_server('ct_gov_mcp'))"
```

### Creating New Skills

```bash
# Initialize new skill in folder structure
python3 .claude/scripts/init_skill.py get_new_data --server ct_gov_mcp
```

---

## MCP Servers

The platform integrates **12 specialized MCP servers**:

### Core Pharmaceutical Data
- **ct-gov-mcp**: ClinicalTrials.gov trial data (returns **markdown**)
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
- **pubmed-mcp**: PubMed biomedical literature

### Medical Coding & Standards
- **nlm-codes-mcp**: ICD-10/11, HCPCS, NPI, HPO medical codes
- **who-mcp-server**: WHO Global Health Observatory data

### Chemistry & Biology
- **pubchem-mcp-server**: Compound properties, ADME data
- **opentargets-mcp-server**: Target validation, gene-drug-disease associations

### Financial & Legal
- **sec-mcp-server**: SEC EDGAR financial filings
- **patents-mcp-server**: USPTO patent search
- **financials-mcp-server**: Yahoo Finance + FRED economic indicators

### Healthcare Systems
- **healthcare-mcp**: CMS Medicare provider data
- **datacommons-mcp**: Population statistics, disease demographics

**Documentation**: Each server has detailed API guide in `.claude/.context/mcp-tool-guides/`

---

## Quick Start

### 1. Simple Query

```bash
# Example queries:
"What GLP-1 drugs are approved for diabetes?"
"How many KRAS inhibitor trials are ongoing?"
"Get FDA adverse events for baricitinib"
```

**System Flow**:
1. pharma-search-specialist agent invoked
2. Agent reads relevant MCP tool guide + code example
3. Agent generates Python code
4. Code executes via Bash tool
5. Summary displayed, skill saved to `.claude/skills/`

### 2. Strategic Analysis

```bash
# Example:
"Analyze BRAF inhibitor competitive landscape"
```

**System Flow**:
1. Main agent reads competitive-landscape-analyst metadata
2. Main agent identifies required data: trials + FDA drugs
3. Main agent checks/creates/executes skills
4. Main agent invokes strategic agent with collected data
5. Strategic agent returns analysis
6. Report saved to `reports/competitive-landscape/`

---

## Token Efficiency

| Method | Tokens | Efficiency |
|--------|--------|-----------|
| Direct MCP call | 60,000 | ❌ Raw data in context |
| Old scripts | 2,000 | ⚠️ Data flows through context |
| **Code execution + MCP** | **500** | ✅ **98.7% reduction** |

**How it works**:
- Data processed in execution environment (Python)
- Only summary enters model context
- Raw responses never loaded into conversation

---

## Progressive Disclosure System

### MCP Tool Guides (Always available)
Agent reads these to understand API parameters:
- `.claude/.context/mcp-tool-guides/clinicaltrials.md`
- `.claude/.context/mcp-tool-guides/fda.md`
- `.claude/.context/mcp-tool-guides/pubmed.md`
- [9 more...]

### Code Examples (Read on-demand)
Agent reads ONLY when needed:
- `.claude/.context/code-examples/ctgov_markdown_parsing.md`
- `.claude/.context/code-examples/fda_json_parsing.md`
- `.claude/.context/code-examples/multi_server_query.md`
- `.claude/.context/code-examples/skills_library_pattern.md`

**Benefit**: Load 0-2 examples per query instead of all examples always.

### Pattern Discovery (Skills Evolution)
Agent discovers and reuses patterns from existing skills:
1. User asks for new query (e.g., "Get ADC trials")
2. Agent checks `.claude/skills/` for similar implementations
3. Agent reads reference skill (e.g., `get_glp1_trials.py`)
4. Agent applies proven patterns (pagination, parsing)
5. Agent generates new skill following same structure

**Skills Index**: `.claude/skills/index.json` contains:
- Patterns demonstrated by each skill
- Best reference skills for each pattern
- Quick discovery without reading all files

---

## Directory Structure

```
.claude/
├── CLAUDE.md                           # Architecture documentation
├── .context/                           # Documentation & guides
│   ├── code-examples/                  # Code patterns (7 patterns)
│   ├── mcp-tool-guides/                # MCP server docs (12 servers)
│   ├── templates/                      # Report templates
│   └── planning-archives/              # Historical planning docs
├── agents/                             # Agent definitions (2 agents)
│   ├── pharma-search-specialist.md
│   └── competitive-landscape-analyst.md
├── scripts/                            # Utility scripts (11 utilities)
│   ├── discover_skills.py
│   ├── init_skill.py
│   ├── package_skill.py
│   └── mcp/                            # MCP infrastructure
│       ├── client.py                   # MCP client
│       └── servers/                    # Python function stubs (12 servers)
└── skills/                             # Skills library (13 skills)
    ├── index.json                      # Skills discovery index
    ├── README.md
    └── [skill-folders]/                # Anthropic folder structure

reports/                                # Strategic analysis reports
├── competitive-landscape/
│   └── YYYY-MM-DD_therapeutic-area.md
├── clinical-strategy/
└── regulatory-analysis/
```

---

## Design Principles

1. **Code Execution Pattern**: Anthropic's proven pattern for 98.7% token reduction
2. **Progressive Disclosure**: Load only docs/examples needed for current query
3. **Skills Library**: Reusable functions that grow over time
4. **In-Memory Processing**: Data processed in execution environment, never in context
5. **Metadata-Driven**: Strategic agents declare data needs via YAML frontmatter
6. **Single Source of Truth**: No duplication across documentation files

---

## Data Output Strategy

### In-Memory Processing (Default)
- Code processes data in execution environment
- Only summary printed to conversation
- No files saved
- **98.7% token reduction benefit**

### Skills Persistence (Always)
- All data collection functions saved to `.claude/skills/`
- Folder structure: `skill-name/SKILL.md` + `scripts/function.py`
- YAML frontmatter for discovery
- Reusable across sessions

### Report Persistence (Strategic Analyses)
- Strategic agent reports saved to `reports/{agent_type}/`
- Version controlled (shows evolution over time)
- YAML frontmatter with metadata
- Templates in `.claude/.context/templates/`

**Rule**: Default to in-memory unless user requests export or strategic analysis.

---

## Example Workflows

### 1. Drug Discovery Query
```
Query: "What GLP-1 drugs are approved?"
    ↓
pharma-search-specialist reads: fda.md + fda_json_parsing.md
    ↓
Generates Python code using FDA MCP server
    ↓
Executes → "21 unique GLP-1 drugs found"
    ↓
Saves skill: .claude/skills/glp1-fda-drugs/
    ↓
User sees: Summary (500 tokens)
```

### 2. Clinical Trials Analysis
```
Query: "How many KRAS inhibitor trials?"
    ↓
pharma-search-specialist reads: clinicaltrials.md + ctgov_markdown_parsing.md
    ↓
Generates Python code with CT.gov markdown parsing
    ↓
Executes → "363 trials found"
    ↓
Saves skill: .claude/skills/kras-inhibitor-trials/
    ↓
User sees: Summary with trial breakdown
```

### 3. Competitive Landscape Analysis
```
Query: "@agent-competitive-landscape-analyst Analyze BRAF inhibitors"
    ↓
Main agent reads analyst metadata → Needs: trials + FDA drugs
    ↓
Main agent checks skills:
  - .claude/skills/braf-inhibitor-trials/ exists ✓
  - .claude/skills/braf-inhibitor-fda-drugs/ exists ✓
    ↓
Main agent executes both skills → Collects data
    ↓
Main agent invokes competitive-landscape-analyst with data
    ↓
Analyst returns: strategic analysis (4000-6000 words)
    ↓
Report saved: reports/competitive-landscape/YYYY-MM-DD_braf-inhibitor.md
    ↓
User sees: Executive summary + full report link
```

---

## Key Features

### Token Optimization
- **Count-first strategy**: Check dataset size before fetching details
- **Field selection**: Only request needed fields (70-90% token reduction)
- **Conservative limits**: Max 50-100 records per query
- **Pagination support**: For large datasets (e.g., GLP-1 trials: 1803 results)

### Skills Evolution
- **Pattern discovery**: Agent learns from existing skills
- **Battle-tested code**: Reuse proven implementations (pagination, parsing)
- **Consistent structure**: All skills follow same format
- **Easy discovery**: Index-based search by pattern/server/category

### Data Quality
- **Audit trail**: All skill executions tracked
- **Metadata**: YAML frontmatter in SKILL.md files
- **Version controlled**: Skills + reports in git
- **Source transparency**: MCP responses processed transparently

---

## Contributing

### New MCP Servers

1. Add to `.mcp.json`
2. Create tool guide in `.claude/.context/mcp-tool-guides/`
3. Update `.claude/CLAUDE.md` and `README.md`

### New Skills

Skills are created automatically by pharma-search-specialist agent, but you can also:

```bash
# Initialize new skill manually
python3 .claude/scripts/init_skill.py get_new_data --server ct_gov_mcp
```

### New Agents

1. Create in `.claude/agents/` (follow existing structure)
2. Use YAML frontmatter for metadata
3. Define data requirements in `data_requirements` section
4. Update `.claude/CLAUDE.md` and `README.md`

---

## License

[Your License Here]

---

## Links

- **Anthropic Code Execution Pattern**: https://www.anthropic.com/engineering/code-execution-with-mcp
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Claude Code**: https://claude.com/claude-code
