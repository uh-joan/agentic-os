# Code Examples (Progressive Disclosure)

This directory contains **code pattern examples** for the pharma-search-specialist agent to read **on-demand**.

## Purpose

Following Anthropic's progressive disclosure pattern:
> "Load only the tools needed for the current query"

Applied to examples:
> "Load only the EXAMPLE needed for the current query type"

## Benefits

**Context Efficiency**:
- Agent loads 0 examples by default
- Reads only 1-2 relevant examples per query
- **85% reduction** in example loading (vs all-in-prompt)

**Maintainability**:
- Single source of truth per pattern
- Easy to add new examples (just add file)
- No duplication across agent prompt and CLAUDE.md

**Flexibility**:
- Examples can be detailed without bloating prompts
- Can reference other examples and tool guides
- Easy to evolve patterns over time

## Available Examples

### Single-Server Patterns

**`fda_json_parsing.md`**
- When: FDA drug/device queries
- Response format: JSON dict
- Pattern: `.get()` methods
- Example: Search for GLP-1 drugs

**`ctgov_markdown_parsing.md`**
- When: ClinicalTrials.gov queries
- Response format: Markdown string (CRITICAL!)
- Pattern: Regex parsing
- Example: Count Phase 3 obesity trials

### Multi-Server Patterns

**`multi_server_query.md`**
- When: Combining data from multiple sources
- Pattern: Handle different response formats
- Example: FDA drugs + CT.gov trials landscape

### Best Practices

**`skills_library_pattern.md`**
- When: Every query!
- Pattern: Save reusable functions to `.claude/skills/`
- Shows: Complete skills library implementation

## Usage Pattern

**Agent workflow**:
1. Identify query type (FDA? CT.gov? Multi-server?)
2. Read relevant tool guide from `.claude/.context/mcp-tool-guides/`
3. Read relevant code example from THIS directory
4. Generate code following pattern
5. Save skill to `.claude/skills/`

**Example**:
- Query: "How many Phase 3 obesity trials?"
- Agent reads: `clinicaltrials.md` + `ctgov_markdown_parsing.md`
- Agent generates code with regex parsing
- Total files read: 2 (not 15+)

## Adding New Examples

To add a new example:

1. Create `[pattern_name].md` in this directory
2. Follow this structure:

```markdown
# [Pattern Name]

## When to Use This Example
[Description of when this pattern applies]

## Critical: Response Format
[JSON? Markdown? Key quirks?]

## Complete Working Example
\`\`\`python
[Full working code that agent can adapt]
\`\`\`

## Key Patterns
[Extractable patterns from the example]

## Parameter Reference
[Link to relevant tool guide]
```

3. Reference in pharma-search-specialist.md under "Code Examples"

## File Organization

```
code-examples/
├── README.md (this file)
├── fda_json_parsing.md           # FDA pattern
├── ctgov_markdown_parsing.md     # CT.gov pattern
├── multi_server_query.md         # Multi-server pattern
└── skills_library_pattern.md     # Skills library pattern
```

## Token Savings

**Without progressive disclosure**:
- All examples in agent prompt = ~10,000 tokens
- Loaded every query, regardless of relevance
- 85% waste for single-server queries

**With progressive disclosure**:
- Agent reads 1-2 examples = ~1,500 tokens
- Only loads what's needed
- **85% reduction** + enables more detailed examples

Combined with code execution pattern:
- **98.7% total context reduction** (per Anthropic's measurements)
