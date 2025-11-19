# Anthropic Code Execution with MCP - Complete Analysis

**Source**: https://www.anthropic.com/engineering/code-execution-with-mcp

**Purpose**: This document contains a comprehensive analysis of Anthropic's best practices for code execution with MCP, used to ensure our implementation aligns with their recommended patterns.

---

## Executive Summary

**Core Innovation**: Present MCP servers as **code APIs** rather than direct tool calls, enabling agents to write code that processes data locally before returning results to the model.

**Key Benefits**:
- **98.7% token reduction** (150,000 → 2,000 tokens in their example)
- **Progressive disclosure**: Load only needed tools
- **Natural control flow**: Loops, conditionals in code vs. agent iterations
- **Privacy**: Sensitive data stays in execution environment
- **State persistence**: Use filesystem across executions

**Trade-off**: Requires secure execution environment with sandboxing, resource limits, monitoring

---

## 1. Token Reduction Mechanism

### The Problem (Without Code Execution)

**Scenario**: Retrieve Google Drive document, attach to Salesforce record

**Token Flow**:
1. Tool definition for `gdrive.getDocument`: ~5,000 tokens
2. Tool definition for `salesforce.updateRecord`: ~5,000 tokens
3. Call `gdrive.getDocument` → returns 2-hour transcript
4. Transcript content: ~50,000 tokens (in context)
5. Call `salesforce.updateRecord` → passes transcript again
6. Transcript content again: ~50,000 tokens (in context)

**Total**: ~110,000+ tokens for simple 2-tool operation

### The Solution (With Code Execution)

**Code Written by Agent**:
```typescript
import * as gdrive from './servers/google-drive';
import * as salesforce from './servers/salesforce';

const transcript = (await gdrive.getDocument({
  documentId: 'abc123'
})).content;
await salesforce.updateRecord({
  objectType: 'SalesMeeting',
  recordId: '00Q5f000001abcXYZ',
  data: { Notes: transcript }
});
console.log('Transcript attached successfully');
```

**Token Flow**:
1. Agent writes code: ~500 tokens
2. Code executes: transcript stays in execution environment (0 tokens to model)
3. Console output: ~50 tokens

**Total**: ~550 tokens

**Reduction**: 110,000 → 550 = **99.5% savings**

### Data Filtering Example

**Without Code Execution**:
```
TOOL: gdrive.getSheet(sheetId: 'abc123')
RESULT: [10,000 rows × ~50 tokens/row = 500,000 tokens in context]
AGENT: *filters manually* → 5 pending orders
```

**With Code Execution**:
```typescript
const allRows = await gdrive.getSheet({ sheetId: 'abc123' });
const pendingOrders = allRows.filter(row => row["Status"] === 'pending');
console.log(`Found ${pendingOrders.length} pending orders`);
console.log(pendingOrders.slice(0, 5)); // Only first 5 for review
```

**Result**: Model sees 5 rows instead of 10,000

**Quote**: "The agent sees five rows instead of 10,000. Similar patterns work for aggregations, joins across multiple data sources, or extracting specific fields."

---

## 2. Skills Library Pattern

### Exact Pattern from Article

**Location**: `./skills/` directory

**Example Skill**:
```typescript
// In ./skills/save-sheet-as-csv.ts
import * as gdrive from './servers/google-drive';

export async function saveSheetAsCsv(sheetId: string) {
  const data = await gdrive.getSheet({ sheetId });
  const csv = data.map(row => row.join(',')).join('\n');
  await fs.writeFile(`./workspace/sheet-${sheetId}.csv`, csv);
  return `./workspace/sheet-${sheetId}.csv`;
}
```

**Usage in Future Execution**:
```typescript
import { saveSheetAsCsv } from './skills/save-sheet-as-csv';
const csvPath = await saveSheetAsCsv('abc123');
```

### Skills Definition Files

**Enhancement**: Create `SKILL.md` file alongside skill code

**Purpose**: "This evolves the agent's toolbox of higher-level capabilities"

**Pattern**: Agent builds **reusable, importable functions** from working code, creating persistent expertise across sessions

---

## 3. Progressive Disclosure

### The Problem (Traditional Approach)

Loading all tool definitions upfront:
- 12 MCP servers × ~5,000 tokens/server = 60,000 tokens
- Most tools never used in a given task
- Wastes context on irrelevant tools

### Solution 1: Filesystem Navigation

**Directory Structure**:
```
servers/
├── google-drive/
│   ├── getDocument.ts
│   ├── getSheet.ts
│   └── index.ts
├── salesforce/
│   ├── updateRecord.ts
│   ├── query.ts
│   └── index.ts
└── slack/
    ├── postMessage.ts
    └── index.ts
```

**Agent Behavior**:
1. List `./servers/` directory
2. Find `google-drive` and `salesforce`
3. Read only those specific tool files
4. Load definitions on-demand

**Quote**: "listing the `./servers/` directory to find available servers (like `google-drive` and `salesforce`), then reading the specific tool files it needs."

### Solution 2: Search Tool

**Function**: `search_tools(query: string, detail_level: 'name' | 'name_description' | 'full')`

**Detail Levels**:
- `name`: Just function names (minimal tokens)
- `name_description`: Names + brief descriptions
- `full`: Complete definitions with schemas

**Use Case**: Agent searches for "spreadsheet" → finds `gdrive.getSheet` → loads only that tool's full definition

---

## 4. Control Flow Optimization

### Without Code Execution (Agent Loop)

```
AGENT: Call slack.getChannelHistory
MCP: Returns messages
AGENT: Check if "deployment complete" exists
AGENT: Not found, call sleep tool for 5 seconds
MCP: Sleep complete
AGENT: Call slack.getChannelHistory again
MCP: Returns messages
AGENT: Check if "deployment complete" exists
... [repeats many times]
```

**Problems**:
- Multiple round-trips to model
- High latency (time to first token for each iteration)
- Token cost multiplies with iterations

### With Code Execution (Natural Loop)

```typescript
let found = false;
while (!found) {
  const messages = await slack.getChannelHistory({ channel: 'C123456' });
  found = messages.some(m => m.text.includes('deployment complete'));
  if (!found) await new Promise(r => setTimeout(r, 5000));
}
console.log('Deployment notification received');
```

**Benefits**:
- Single model invocation
- Loop executes in environment (no context cost)
- Immediate conditional evaluation (no token-to-first-token latency)

**Quote**: "This approach is more efficient than alternating between MCP tool calls and sleep commands through the agent loop... it saves on time to first token latency: rather than having to wait for a model to evaluate an if-statement, the agent can let the code execution environment do this."

---

## 5. Data Filtering and Privacy

### PII Protection Example

**Code**:
```typescript
const sheet = await gdrive.getSheet({ sheetId: 'abc123' });
for (const row of sheet.rows) {
  await salesforce.updateRecord({
    objectType: 'Lead',
    recordId: row.salesforceId,
    data: {
      Email: row.email,
      Phone: row.phone,
      Name: row.name
    }
  });
}
console.log(`Updated ${sheet.rows.length} leads`);
```

**Automatic Tokenization**: MCP client intercepts and tokenizes:
- Real data flows to Salesforce: `john@example.com`, `555-1234`
- Tokenized data shown to model: `[EMAIL_1]`, `[PHONE_1]`

**Model sees only**: `"Updated 150 leads"`

**Quote**: "The MCP client intercepts and tokenizes sensitive data (`[EMAIL_1]`, `[PHONE_1]`, etc.), allowing real data to flow to Salesforce while preventing model exposure."

### Aggregation Example

**Scenario**: Analyze 10,000 sales records

**Code**:
```typescript
const records = await salesforce.query({
  query: 'SELECT Amount, Stage FROM Opportunity LIMIT 10000'
});

const summary = records.reduce((acc, r) => {
  acc[r.Stage] = (acc[r.Stage] || 0) + r.Amount;
  return acc;
}, {});

console.log('Revenue by stage:', summary);
```

**Model sees**: `{ "Prospecting": 500000, "Negotiation": 1200000, "Closed Won": 3400000 }`

**Not seen**: 10,000 individual records (500,000+ tokens)

---

## 6. Architecture and Implementation

### Server Wrapper Pattern

**File**: `./servers/google-drive/getDocument.ts`

```typescript
import { callMCPTool } from "../../../client.js";

interface GetDocumentInput {
  documentId: string;
}

interface GetDocumentResponse {
  content: string;
}

export async function getDocument(input: GetDocumentInput):
  Promise<GetDocumentResponse> {
  return callMCPTool<GetDocumentResponse>('google_drive__get_document', input);
}
```

**Key Features**:
- TypeScript types for autocomplete and validation
- Imports like normal code: `import * as gdrive from './servers/google-drive'`
- Single `callMCPTool` wrapper handles all MCP protocol details

### State Persistence Pattern

**First Execution**:
```typescript
const leads = await salesforce.query({
  query: 'SELECT Id, Email FROM Lead LIMIT 1000'
});
const csvData = leads.map(l => `${l.Id},${l.Email}`).join('\n');
await fs.writeFile('./workspace/leads.csv', csvData);
```

**Later Execution** (different session):
```typescript
const saved = await fs.readFile('./workspace/leads.csv', 'utf-8');
// Process saved data
```

**Benefit**: Expensive operations don't need to repeat across sessions

---

## 7. Best Practices (Exact from Article)

1. **Represent MCP servers as code APIs** with typed interfaces
2. **Use progressive disclosure** to load only necessary tool definitions
3. **Filter and transform large datasets** before returning to model
4. **Implement familiar control flow patterns** (loops, conditionals) in code
5. **Leverage filesystem access** for state persistence across executions
6. **Create reusable skills** from working code implementations
7. **Include SKILL.md documentation** for agent reference
8. **Use console.log() to control** what the model sees
9. **Apply tokenization to sensitive data** automatically through MCP client

---

## 8. Warnings and Caveats

### Critical Infrastructure Requirements

**Quote**: "Code execution introduces its own complexity. Running agent-generated code requires a secure execution environment with appropriate sandboxing, resource limits, and monitoring. These infrastructure requirements add operational overhead and security considerations that direct tool calls avoid."

### When to Use Code Execution

**Use when**:
- Working with large datasets (>1,000 records)
- Multiple sequential tool calls needed
- Loops or conditional logic required
- Privacy-sensitive data processing
- Complex transformations/aggregations

**Don't use when**:
- Single, simple tool call
- Small data volumes (<100 records)
- Cannot implement secure sandboxing
- Infrastructure overhead not justified

**Quote**: "The benefits of code execution—reduced token costs, lower latency, and improved tool composition—should be weighed against these implementation costs."

---

## 9. Validation from Industry

**Cloudflare Research**: Independently developed similar pattern called "Code Mode"

**Implication**: This is a general best practice, not Anthropic-specific

---

## 10. Comparison Summary

| Aspect | Direct Tool Calls | Code Execution |
|--------|------------------|----------------|
| **Token Usage** | 150,000 tokens | 2,000 tokens (98.7% reduction) |
| **Tool Loading** | All upfront | On-demand |
| **Intermediate Results** | Flow through context | Stay in execution environment |
| **Control Flow** | Agent iterations | Natural code loops |
| **Data Filtering** | Manual, post-retrieval | In-code, pre-return |
| **State** | Lost between calls | Filesystem persistence |
| **Privacy** | Manual redaction | Automatic tokenization |
| **Complexity** | Simple (no sandbox) | High (requires secure environment) |

---

## 11. Key Quotes

> "agents can load only the tools they need and process data in the execution environment before passing results back to the model."

> "The agent sees five rows instead of 10,000. Similar patterns work for aggregations, joins across multiple data sources, or extracting specific fields."

> "This approach is more efficient than alternating between MCP tool calls and sleep commands through the agent loop."

> "This evolves the agent's toolbox of higher-level capabilities."

> "Code execution introduces its own complexity... These infrastructure requirements add operational overhead and security considerations that direct tool calls avoid."

---

## 12. Implementation Checklist

For any code execution with MCP implementation, verify:

- [ ] MCP servers wrapped as importable code APIs
- [ ] Skills saved to `./skills/` directory
- [ ] Skills are reusable functions (not complete scripts)
- [ ] Agent can import skills in future executions
- [ ] Progressive disclosure implemented (filesystem or search)
- [ ] Data filtering happens in code, not after return
- [ ] Control flow uses native code constructs
- [ ] Only summaries/filtered results logged to console
- [ ] State persistence via filesystem when needed
- [ ] Secure execution environment with sandboxing
- [ ] Resource limits and monitoring in place

---

**Last Updated**: 2025-11-18
**Purpose**: Reference for maintaining alignment with Anthropic's recommended patterns
