# Pharmaceutical Research Intelligence Platform

AI-powered pharmaceutical research system using Claude Code with specialized MCP servers for drug discovery, clinical trials, regulatory data, and competitive intelligence.

## Architecture

Multi-agent system: data gathering + analytical modeling

**Agents:**
- `pharma-search-specialist`: Query → JSON plan → MCP tools → `data_dump/`
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels

**Workflow:** Query → pharma-search-specialist (gathers data) → epidemiology-analyst (analyzes) → results

## MCP Servers

The platform integrates 12 specialized MCP servers (see `.mcp.json`):

### Core Pharmaceutical Data
- **ct-gov-mcp**: ClinicalTrials.gov trial data
  - Tool: `mcp__ct-gov-mcp__ct_gov_studies`
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
  - Tool: `mcp__fda-mcp__fda_info`
- **pubmed-mcp**: PubMed biomedical literature
  - Tool: `mcp__pubmed-mcp__pubmed_articles`

### Medical Coding & Standards
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO)
  - Tool: `mcp__nlm-codes-mcp__nlm_ct_codes`
- **who-mcp-server**: WHO Global Health Observatory data
  - Tool: `mcp__who-mcp-server__who-health`

### Chemistry & Biology
- **pubchem-mcp-server**: Compound properties, ADME data
  - Tool: `mcp__pubchem-mcp-server__pubchem`
- **opentargets-mcp-server**: Target validation, gene-drug-disease associations
  - Tool: `mcp__opentargets-mcp-server__opentargets_info`

### Financial & Legal
- **sec-mcp-server**: SEC EDGAR financial filings
  - Tool: `mcp__sec-mcp-server__sec-edgar`
- **patents-mcp-server**: USPTO patent search
  - Tool: `mcp__patents-mcp-server__uspto_patents`
- **financials-mcp-server**: Yahoo Finance stock data + FRED economic indicators
  - Tool: `mcp__financials-mcp-server__financial-intelligence`

### Healthcare Systems
- **healthcare-mcp**: CMS Medicare provider data
  - Tool: `mcp__healthcare-mcp__cms_search_providers`
- **datacommons-mcp**: Population statistics, disease demographics
  - Tools: `mcp__datacommons-mcp__search_indicators`, `mcp__datacommons-mcp__get_observations`

## Quick Start

### 1. Query the System

```bash
# Example queries:
"FDA-approved GLP-1 drugs"
"Clinical trials for Alzheimer's disease in Phase 3"
"Adverse events for atorvastatin"
"Competitive landscape for JAK inhibitors"
```

### 2. System Flow

1. **Classify query** (simple, complex, or exploratory)
2. **Invoke specialist agent** using appropriate template
3. **Receive execution plan** (JSON format)
4. **Execute MCP tool calls** sequentially
5. **Save results** to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/`

### 3. Results Structure

Each query creates a timestamped directory in `data_dump/`:

```
data_dump/2025-11-10_183054_fda_baricitinib/
├── query.json         # Original query parameters
├── results.json       # Raw MCP response
├── summary.md         # Human-readable summary
└── metadata.json      # Execution metadata
```

## Query Complexity Classification

### Simple Queries (single database, <5 steps)
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

### Complex Queries (multi-database, >5 steps)
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis

### Exploratory Queries
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research

## Documentation

### Core Documentation
- **`.claude/CLAUDE.md`**: Architecture overview and execution protocols
- **`.claude/agents/pharma-search-specialist.md`**: Agent specification and examples
- **`.mcp.json`**: MCP server configuration

### Tool Guides (`.claude/.context/mcp-tool-guides/`)
- **fda.md**: FDA database queries (drugs, adverse events, recalls)
- **clinicaltrials.md**: ClinicalTrials.gov search patterns
- **pubmed.md**: PubMed literature searches
- **sec-edgar.md**: SEC financial filings
- **datacommons.md**: Population and disease statistics
- **opentargets.md**: Target validation queries
- **pubchem.md**: Chemical compound searches
- **uspto-patents.md**: Patent search strategies

### Strategy Protocols (`.claude/.context/`)
- **performance-optimization.md**: Token efficiency, count-first strategies
- **search-strategy-protocols.md**: 4-phase execution, cognitive directives
- **search-workflows.md**: Proven workflow templates
- **cross-database-integration.md**: Entity linking across sources
- **quality-control.md**: Validation criteria, confidence levels

## Key Features

### Token Optimization
- **Count-first strategy**: Reduces FDA queries from 67K → 400 tokens (99.4% savings)
- **Field selection**: 70-90% token reduction on detail queries
- **Conservative limits**: Max 50-100 records per query
- **Pagination support**: For large datasets

### Data Quality
- **Audit trail**: All queries and results saved
- **Metadata tracking**: Timestamps, parameters, token usage
- **Validation steps**: Quality checks on multi-step workflows
- **Source transparency**: Original MCP responses preserved

### Intelligence Capabilities
- **Multi-database synthesis**: Link entities across FDA, ClinicalTrials.gov, PubMed
- **Competitive analysis**: Pipeline comparison, market positioning
- **Safety monitoring**: Adverse event detection and trending
- **Target validation**: Gene-drug-disease associations

## Example Workflows

### Drug Safety Analysis
1. FDA general search (count-first) → identify products
2. FDA adverse events (aggregated) → safety signals
3. PubMed literature → clinical evidence
4. ClinicalTrials.gov → ongoing trials

### Competitive Landscape
1. ClinicalTrials.gov → pipeline programs by sponsor
2. FDA approvals → marketed products
3. SEC EDGAR → R&D spend, financial health
4. Patents → IP protection timeline

### Target Validation
1. OpenTargets → gene-disease associations
2. PubMed → mechanism literature
3. ClinicalTrials.gov → clinical validation
4. PubChem → tool compounds

### Epidemiological Analysis (using epidemiology-analyst)
1. Data Commons + WHO + CMS → prevalence data gathering
2. PubMed → severity distribution studies
3. ClinicalTrials.gov → eligibility criteria patterns
4. FDA + CMS → contraindication prevalence
5. Epidemiology-analyst → eligibility funnel modeling
6. Output: Drug-eligible population estimate with sensitivity analysis

## Agents

### pharma-search-specialist
Data gathering coordinator. Input: query → Output: JSON execution plan with MCP tool calls

### epidemiology-analyst
Prevalence modeling and market sizing. Input: `data_dump/` → Output: Models, segmentation, eligibility funnels

**Capabilities**: Age-standardization, severity segmentation, biomarker stratification, eligibility funnels, sensitivity analysis, CMS real-world evidence integration

## Design Principles

1. **Multi-agent**: Data gathering + analytical agents, optimized roles
2. **Separation**: No MCP execution by analytical agents
3. **Token optimization**: Conservative limits, pagination, count-first
4. **Audit trail**: All results → data_dump/
5. **Modular**: Easy to add MCP servers and agents

## Contributing

**New MCP Servers:**
1. Add to `.mcp.json`
2. Create tool guide in `.claude/.context/mcp-tool-guides/`
3. Update `.claude/CLAUDE.md`, `README.md`, `.claude/settings.local.json`

**New Agents:**
1. Create in `.claude/agents/` (follow `epidemiology-analyst.md` structure)
2. Use frontmatter, enumerated capability domains, response methodology, example output
3. Update `.claude/CLAUDE.md` and `README.md`
