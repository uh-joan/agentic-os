# MCP Code Execution

**Implementation of code execution pattern from Anthropic's article:**
https://www.anthropic.com/engineering/code-execution-with-mcp

## Overview

Instead of calling MCP tools directly (which loads tool definitions and results into context), agents write Python code that calls MCP servers as code APIs. Data processing happens in the execution environment, and only summaries return to the model.

## Benefits

### Context Efficiency
- **Before**: 60,000 tokens per FDA query (raw JSON)
- **After**: 500 tokens per query (summary only)
- **Savings**: 99% context reduction

### Progressive Disclosure
- Load only tools needed for current task
- No upfront loading of all tool definitions

### Privacy
- Sensitive data stays in execution environment
- Never enters model context

### Control Flow
- Loops, conditionals, error handling in familiar Python
- No tool call chains through model

## Architecture

```
Agent writes Python code
        ↓
Code execution environment (Python)
        ↓
MCP client wrapper (scripts/mcp/client.py)
        ↓
MCP servers (stdio processes)
```

## Usage

### 1. Import MCP Server Functions

```python
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.ct_gov_mcp import search
from mcp.servers.pubmed_mcp import search_keywords
```

### 2. Call Tools in Execution Environment

```python
# Query FDA
results = lookup_drug(
    search_term="obesity",
    search_type="general",
    limit=100
)

# Process data (stays in environment)
brands = set()
for result in results.get('data', {}).get('results', []):
    openfda = result.get('openfda', {})
    brands.update(openfda.get('brand_name', []))

# Return only summary
print(f"Found {len(brands)} unique brands")
```

### 3. Data Never Enters Model Context

Raw FDA JSON (60k tokens) → Execution environment → Summary (500 tokens) → Model

## Available MCP Servers

### FDA (`mcp.servers.fda_mcp`)
```python
from mcp.servers.fda_mcp import lookup_drug

results = lookup_drug(
    search_term="semaglutide",
    search_type="general",
    limit=10
)
```

### ClinicalTrials.gov (`mcp.servers.ct_gov_mcp`)
```python
from mcp.servers.ct_gov_mcp import search

results = search(
    condition="obesity",
    phase="PHASE3",
    status="recruiting",
    location="United States",
    pageSize=100
)
```

### PubMed (`mcp.servers.pubmed_mcp`)
```python
from mcp.servers.pubmed_mcp import search_keywords

results = search_keywords(
    keywords="GLP-1 agonist obesity",
    num_results=50
)
```

## Example

See `scripts/mcp/examples/obesity_drugs_analysis.py` for a complete example:

```bash
python3 scripts/mcp/examples/obesity_drugs_analysis.py
```

Output:
```
FDA APPROVED DRUGS:
  Brands: OZEMPIC, RYBELSUS, WEGOVY
  Routes: ORAL (1), SUBCUTANEOUS (2)

CLINICAL TRIALS (Obesity + Semaglutide, Recruiting):
  Total trials found: 67

CONTEXT EFFICIENCY:
  Raw data would be: ~50,000 tokens
  Summary returned: ~500 tokens
  Savings: 99%
```

## Implementation Details

### MCP Client Wrapper (`scripts/mcp/client.py`)
- Spawns MCP server as subprocess
- Communicates via JSON-RPC over stdio
- Handles initialization and tool calls
- Manages server lifecycle

### Server Stubs (`scripts/mcp/servers/`)
- Python modules for each MCP server
- Type-annotated function interfaces
- Auto-imported by agent-generated code

### Execution Environment
- Python 3.x with sys.path configured
- Sandboxed (future: Docker container)
- Filesystem access for intermediate results

## Migration from Direct MCP Calls

### Old Pattern (Direct Tool Calls)
```json
{
  "tool": "mcp__fda-mcp__fda_info",
  "params": {"search_term": "obesity", "limit": 100}
}
```
→ Returns 60k tokens into context

### New Pattern (Code Execution)
```python
from mcp.servers.fda_mcp import lookup_drug

results = lookup_drug(search_term="obesity", limit=100)
brands = [b for r in results['data']['results']
          for b in r.get('openfda', {}).get('brand_name', [])]
print(f"Brands: {', '.join(set(brands))}")
```
→ Returns 100 tokens

## Best Practices

1. **Process data in execution environment**
   - Filter, aggregate, transform before returning
   - Don't pass raw API responses to model

2. **Use natural control flow**
   - Loops for pagination
   - Conditionals for error handling
   - Try/except for robustness

3. **Return concise summaries**
   - Key metrics only
   - Top-N results
   - Statistical aggregates

4. **Save intermediate results**
   - Use filesystem for complex workflows
   - Enable resumption and debugging

## Future Enhancements

- [ ] Docker-based execution environment
- [ ] Resource limits (CPU, memory, timeout)
- [ ] Network sandboxing
- [ ] Auto-generate stubs from MCP introspection
- [ ] Support for more MCP servers
- [ ] Tokenization layer for PII protection
