# MCP Code Execution Architecture

## Overview

Implementation of the code execution pattern from Anthropic's article "Code execution with MCP: Building more efficient agents".

**Goal**: Enable agents to write code that calls MCP tools, rather than calling tools directly.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Agent (pharma-search-specialist)                                │
│ - Writes Python/TypeScript code                                 │
│ - Imports MCP server modules                                    │
│ - Calls tools as functions                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Code Execution Environment (Python)                             │
│ - Executes agent-generated code                                 │
│ - Provides MCP client wrapper                                   │
│ - Sandboxed execution                                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ MCP Client Wrapper (mcp_client.py)                              │
│ - Communicates with MCP servers via stdio                       │
│ - Translates function calls → MCP tool calls                    │
│ - Returns results to execution environment                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ MCP Servers (stdio processes)                                   │
│ - fda-mcp, ct-gov-mcp, pubmed-mcp, etc.                        │
│ - Run as child processes                                        │
│ - Communicate via JSON-RPC over stdio                           │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
scripts/
├── mcp/
│   ├── client.py              # MCP client wrapper (stdio communication)
│   ├── servers/
│   │   ├── fda_mcp/
│   │   │   ├── __init__.py
│   │   │   ├── lookup_drug.py
│   │   │   └── ...
│   │   ├── ct_gov_mcp/
│   │   │   ├── __init__.py
│   │   │   ├── search.py
│   │   │   └── ...
│   │   ├── pubmed_mcp/
│   │   │   ├── __init__.py
│   │   │   ├── search_keywords.py
│   │   │   └── ...
│   │   └── ...
│   └── generate_stubs.py      # Auto-generates server stubs
```

## Agent Workflow

### Old Pattern (Direct MCP Calls)
```json
{
  "step": 1,
  "tool": "mcp__fda-mcp__fda_info",
  "method": "lookup_drug",
  "params": {"search_term": "obesity", "limit": 100}
}
```
→ Returns 60k tokens → Context explosion

### New Pattern (Code Execution)
```python
# Agent writes this code:
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.ct_gov_mcp import search

# Query FDA for obesity drugs
fda_results = lookup_drug(
    search_term="obesity",
    search_type="general",
    limit=100
)

# Analyze in execution environment
brands = set()
manufacturers = {}
for result in fda_results['results']:
    openfda = result.get('openfda', {})
    for brand in openfda.get('brand_name', []):
        brands.add(brand)
    sponsor = result.get('sponsor_name', 'Unknown')
    manufacturers[sponsor] = manufacturers.get(sponsor, 0) + 1

# Query ClinicalTrials.gov
ct_results = search(
    condition="obesity",
    status="recruiting",
    location="United States",
    pageSize=50
)

# Return only summary
print(f"FDA: {len(brands)} unique brands")
print(f"Top manufacturer: {max(manufacturers, key=manufacturers.get)}")
print(f"Clinical trials: {len(ct_results['studies'])} recruiting")
```
→ Returns ~500 tokens → 99% context reduction

## Implementation Components

### 1. MCP Client Wrapper (`scripts/mcp/client.py`)

Provides Python interface to MCP servers:

```python
import subprocess
import json

class MCPClient:
    def __init__(self, server_name: str, config: dict):
        self.server_name = server_name
        self.process = subprocess.Popen(
            [config['command']] + config['args'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=config.get('env', {})
        )

    def call_tool(self, tool_name: str, params: dict):
        # JSON-RPC call to MCP server
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        self.process.stdin.write(json.dumps(request).encode() + b'\n')
        self.process.stdin.flush()

        response = json.loads(self.process.stdout.readline())
        return response['result']
```

### 2. Auto-Generated Server Stubs (`scripts/mcp/servers/`)

Each MCP server gets a Python module:

```python
# scripts/mcp/servers/fda_mcp/lookup_drug.py
from mcp.client import get_client

def lookup_drug(
    search_term: str,
    search_type: str = "general",
    limit: int = 25,
    **kwargs
):
    """
    Search FDA drug database

    Args:
        search_term: Drug name, active ingredient, or condition
        search_type: Type of search (general, label, adverse_events, etc.)
        limit: Maximum results (1-100)

    Returns:
        dict: FDA API response with drug records
    """
    client = get_client('fda-mcp')
    return client.call_tool('lookup_drug', {
        'search_term': search_term,
        'search_type': search_type,
        'limit': limit,
        **kwargs
    })
```

### 3. Stub Generator (`scripts/mcp/generate_stubs.py`)

Reads MCP server tool definitions and generates Python stubs:

```python
# Introspect MCP servers
# Generate Python modules from tool schemas
# Create __init__.py files with imports
```

### 4. Updated pharma-search-specialist

Agent now generates Python code instead of JSON plans:

```markdown
## Output Format

Return Python code that:
1. Imports required MCP server functions
2. Calls tools and processes data
3. Returns only summary statistics

Example:
```python
from mcp.servers.fda_mcp import lookup_drug

results = lookup_drug(search_term="obesity", limit=100)
brands = set(b for r in results['results']
             for b in r.get('openfda', {}).get('brand_name', []))
print(f"Found {len(brands)} unique brands")
```
```

## Benefits

1. **Context Efficiency**: Data never enters model context
   - Before: 60k tokens per query
   - After: 500 tokens per query
   - Savings: 99%

2. **Progressive Disclosure**: Load only tools needed
   - Before: All tool definitions upfront
   - After: Import only what's needed

3. **Privacy**: Sensitive data stays in execution environment
   - PII never touches model
   - Can implement tokenization layer

4. **Control Flow**: Natural programming constructs
   - Loops, conditionals, error handling
   - No chained tool calls through model

5. **State Persistence**: Filesystem access
   - Save intermediate results
   - Build reusable skills

## Security Considerations

- Sandboxed execution environment
- Resource limits (CPU, memory, timeout)
- Network restrictions
- Filesystem access controls
- MCP server process isolation

## Next Steps

1. Implement MCP client wrapper (stdio communication)
2. Generate server stubs from tool definitions
3. Update pharma-search-specialist prompt
4. Test with obesity query workflow
5. Document patterns and best practices
