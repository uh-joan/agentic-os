# Pharmaceutical Research Intelligence

## Architecture

**Multi-agent pattern**: Data gathering + analytical agents

**Agents**:
- `pharma-search-specialist`: Query → JSON plan → MCP execution → `data_dump/`
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels

## MCP Servers (see .mcp.json)

- **ct-gov-mcp**: ClinicalTrials.gov trial data
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO, medical coding)
- **pubmed-mcp**: PubMed biomedical literature
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
- **who-mcp-server**: WHO Global Health Observatory data
- **sec-mcp-server**: SEC EDGAR financial filings
- **healthcare-mcp**: CMS Medicare provider data
- **financials-mcp-server**: Yahoo Finance, FRED economic data
- **datacommons-mcp**: Population/disease stats
- **patents-mcp-server**: USPTO patent search
- **opentargets-mcp-server**: Target validation, genetics
- **pubchem-mcp-server**: Compound properties, ADME

**Tool specs**: `.claude/.context/mcp-tool-guides/` (clinicaltrials.md, fda.md, pubmed.md, etc.)

## pharma-search-specialist

**Role**: Query analysis → JSON execution plan (no execution)
**Input**: User query
**Output**: JSON with execution_plan array (step, tool, method, params, token_budget)
**Tools**: Read only (reads `.claude/.context/mcp-tool-guides/`)

See `.claude/agents/pharma-search-specialist.md` for plan format and examples.

## Execution Protocol

### 1. Classify Query Complexity

**Simple** (single database, <5 steps):
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

**Complex** (multi-database, >5 steps):
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis
- Keywords: "competitive", "landscape", "compare", "analyze market", "identify leaders"

**Uncertain/Exploratory**:
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research
- Keywords: "explore", "discover", "what are all", "map the space"

### 2. Invoke Specialist

Use the template matching the complexity classification from Step 1.

**For simple queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read relevant tool guide from .claude/.context/mcp-tool-guides/ (e.g., fda.md, clinicaltrials.md).
Read performance-optimization.md and apply count-first + field selection.
Return ONLY JSON execution plan."
```

**For complex queries** (multi-database, competitive analysis, workflows):
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read search-strategy-protocols.md (4-phase execution).
Read search-workflows.md (find similar workflow template).
Read performance-optimization.md (token efficiency - MANDATORY count-first for FDA).
Read cross-database-integration.md (if linking entities).
Read relevant tool guides (fda.md for FDA queries, clinicaltrials.md for CT.gov, pubmed.md for PubMed).
Return ONLY JSON execution plan."
```

**For uncertain/exploratory queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Apply 'ultrathink' mode from search-strategy-protocols.md.
Read search-workflows.md for inspiration.
Read quality-control.md for validation criteria.
Read performance-optimization.md (MANDATORY count-first for FDA).
Read relevant tool guides (fda.md, clinicaltrials.md, pubmed.md, etc.).
Design custom workflow. Return ONLY JSON execution plan."
```

### 3. Execute Plan
Parse JSON → execute each step → save to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/` → present findings

### 4. Invoke Analytical Agents (If Needed)

**epidemiology-analyst** - Prevalence modeling, segmentation, eligibility funnels

Use for: Market sizing, drug-eligible population estimates, patient segmentation

Template:
```
"You are epidemiology-analyst. Read .claude/agents/epidemiology-analyst.md.
Analyze data_dump/[folder]/ and return prevalence model, segmentation, eligibility funnel."
```

## File Structure

**data_dump/**: Raw MCP results (query.json, results.json, summary.md, metadata.json)
**.claude/.context/mcp-tool-guides/**: Tool documentation (DO NOT MODIFY)

## Token Efficiency

**Critical**: Task calls carry full conversation history (~50k tokens per call).

**Best Practices**:
1. Keep specialist prompts minimal (use template above)
2. After receiving execution plan, consider clearing context if conversation is long
3. Limit MCP results (max 50-100 records per query)
4. Use count/pagination before fetching large datasets

## Design Principles

1. **Multi-agent**: Data gathering (pharma-search-specialist) + analytical (epidemiology-analyst)
2. **Separation of concerns**: Gathering vs analysis, no MCP execution by analysts
3. **Token optimization**: Conservative limits, pagination, count strategies
4. **Audit trail**: All results saved to data_dump/
5. **Agent constraints**: Read-only tools for analysts
