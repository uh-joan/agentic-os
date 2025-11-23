# Agentic Research Platform

AI agents that turn research questions into executable Python code, query 12+ specialized data sources, and build a reusable skills library that grows smarter over time.

Built on Anthropic's **code execution with MCP** pattern for token efficiency.

**Quick example:** *"What are the top diabetes drugs by market share?"* → Agent generates Python → Queries FDA + financial APIs → Returns analysis + saves reusable skill.

---

## Key Features

- 🤖 **Generates & executes Python code** (not prompt-based queries)
- 📊 **12 data sources**: Clinical trials, FDA, PubMed, Patents, SEC filings, WHO, medical codes, financial markets
- 🔄 **Self-improving skills library**: Each query creates reusable functions
- ⚡ **More token-efficient** than direct API calls
- 🎯 **End-to-end workflows**: Data collection → Strategic analysis
- 🧠 **Intelligent skill discovery**: Automatic reuse, adaptation, and pattern learning

---

## Data Sources

| Domain | Sources |
|--------|---------|
| **Healthcare** | ClinicalTrials.gov (500K+ trials), FDA (drug labels, adverse events), PubMed (35M+ papers), Open Targets (genetics), PubChem (110M+ compounds) |
| **Medical Coding** | ICD-10/11, HCPCS, NPI, HPO vocabularies |
| **Financial** | SEC EDGAR (filings), Yahoo Finance (stocks), FRED (economic indicators) |
| **Patents** | USPTO + Google Patents (90M+ patents, 11 countries) |
| **Public Health** | WHO Global Health Observatory, Data Commons (demographics), CMS Medicare |

Each source has detailed API guides in `.claude/.context/mcp-tool-guides/`

---

## How It Works

```
User Query → Agent reads API docs → Generates Python code → Executes →
Returns summary (500 tokens) + Saves skill → Skill reusable forever
```

**Token efficiency:** Raw API response stays in execution environment (never enters context).
**Result:** 150K tokens → 2K tokens (98.7% reduction, measured by Anthropic).

---

## Example Queries

### Healthcare
```
"How many Phase 3 obesity trials are recruiting?"
"FDA adverse events for SGLT2 inhibitors"
"GLP-1 drug competitive landscape"
```

### Financial
```
"Abbott segment revenue from SEC filings"
"Biotech M&A deals over $1B since 2020"
"Eli Lilly stock vs clinical trial outcomes"
```

### Public Health
```
"Cardiovascular disease burden by country"
"Cardiologists per capita in Texas"
"Diabetes prevalence trends (OECD)"
```

### Patents & Research
```
"CRISPR patents filed in 2024"
"PubMed: checkpoint inhibitor combinations"
"Antibody-drug conjugate patent landscape"
```

### Multi-Domain
```
"Alzheimer's intelligence: burden + trials + drugs + genetics + market"
"Company X due diligence: financials + pipeline + patents + publications"
```

---

## Agent System

### pharma-search-specialist
**Infrastructure agent** - Creates reusable data collection skills
**Pattern:** Query → Read docs → Generate Python → Execute → Save skill

### competitive-landscape-analyst
**Strategic agent** - Competitive intelligence reports
**Pattern:** Collect data (via skills) → Analyze → Strategic recommendations
**Output:** Saved to `reports/competitive-landscape/YYYY-MM-DD_topic.md`

**Example reports:**
- [Eli Lilly's $1 Trillion Path](reports/competitive-landscape/2025-11-23_eli-lilly-1trillion-milestone.md) - *GLP-1 obesity market dynamics and patent landscape analysis*
- [Obesity Drug Market Intelligence](reports/competitive-landscape/2025-11-23_obesity-drug-market-comprehensive.md) - *Comprehensive competitive analysis across clinical, regulatory, and market dimensions*

**More agents planned**: 80+ across discovery, clinical development, regulatory, medical affairs, market access, financial analysis, public health, and IP research.

---

## Skills Library

**Current:** 68 reusable data collection functions across:
- Clinical trials, FDA drugs, adverse events
- Medical coding (ICD-10/11, HCPCS, NPI)
- Literature search, target validation, compound properties
- Financial data, SEC filings, economic indicators
- Patents, healthcare providers, disease statistics

**Structure:**
```
.claude/skills/
├── index.json                    # Fast discovery index
└── skill-name/
    ├── SKILL.md                  # YAML metadata + docs
    └── scripts/function.py       # Executable Python
```

**Discovery:** 4-level system (index query → health check → semantic matching → strategy)
**Strategy:** REUSE existing → ADAPT similar → CREATE new

---

## Directory Structure

```
.claude/
├── CLAUDE.md                     # Architecture documentation
├── agents/                       # Agent definitions (2 active, 80+ planned)
├── .context/
│   ├── mcp-tool-guides/          # API docs (12 servers)
│   └── code-examples/            # Code patterns (7 patterns)
├── skills/                       # Skills library (68 skills)
│   └── index.json                # Discovery index
├── tools/
│   └── skill_discovery/          # 4-level discovery system
└── mcp/
    ├── client.py                 # MCP client (JSON-RPC)
    └── servers/                  # Python wrappers (12 servers)

reports/                          # Strategic analysis (version controlled)
└── competitive-landscape/
```

---

## Design Principles

1. **Code Execution Pattern** - Anthropic's 98.7% token reduction pattern
2. **Progressive Disclosure** - Load only docs needed for current query
3. **Skills Library** - Reusable functions that grow organically
4. **In-Memory Processing** - Data never enters model context
5. **Intelligent Discovery** - Automatic pattern reuse and adaptation

---

## Contributing

### Add New Skills
Just ask the agent: `"Get [data] from [source]"`
Agent creates, validates, and saves the skill automatically.

### Add New MCP Servers
1. Add to `.mcp.json`
2. Create Python wrapper in `.claude/mcp/servers/`
3. Write API guide in `.claude/.context/mcp-tool-guides/`

### Add New Agents
1. Create definition in `.claude/agents/[name].md`
2. Use YAML frontmatter for metadata
3. Define data requirements
4. Follow existing patterns

### Request New Agents
[Open an issue](https://github.com/uh-joan/pharma-agentic-os/issues/new) describing:
- Use case and problem solved
- Required data sources
- Expected outputs
- Target domain

---

## Links

- **Anthropic Code Execution Pattern**: https://www.anthropic.com/engineering/code-execution-with-mcp