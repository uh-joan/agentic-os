# Agent Delegation Pattern - Implementation Plan

**Created**: 2025-01-18
**Updated**: 2025-01-18
**Status**: Ready to Implement
**Pattern**: Agent-driven delegation (agents tell main agent what to do)

---

## Key Constraint

**Claude Code Architecture**: Sub-agents cannot invoke other sub-agents via Task tool.
- Source: https://code.claude.com/docs/en/sub-agents.md
- Quote: "This prevents infinite nesting of agents (subagents cannot spawn other subagents)"

**Solution**: Delegation pattern - strategic agents return explicit requests to main agent.

---

## Delegation Pattern Architecture

### Three Layers (Agent-Driven Coordination)

```
Layer 1: Infrastructure Agents (Data Collection)
├─ pharma-search-specialist
│  ├─ Creates reusable skills
│  ├─ Saves to .claude/skills/
│  └─ Returns skill code to main agent
└─ (Future: Other data specialists)

Layer 2: Main Agent (Claude Code) - Fulfills Delegation Requests
├─ Receives user @agent-[name] invocations
├─ Invokes strategic agent (first time)
├─ Agent returns delegation request (if skills missing)
├─ Fulfills request:
│   ├─ Create missing skills (via Layer 1)
│   ├─ Execute skills
│   └─ Collect data
├─ Re-invokes strategic agent with data
└─ Returns insights to user

Layer 3: Strategic Agents (Intelligent Delegation + Analysis)
├─ competitive-landscape-analyst
├─ clinical-development-strategist
├─ market-access-strategist
└─ (Future strategic agents)
    ├─ First invocation:
    │   ├─ Read .claude/skills/ (discovery)
    │   ├─ Determine requirements (intelligence)
    │   └─ Return delegation request (if missing skills)
    ├─ Second invocation (with data):
    │   └─ Perform strategic analysis
    └─ Return insights
```

### Key Innovation: **Agents Determine Their Own Requirements**

No hardcoded mappings. Each agent knows what it needs based on the query.

---

## User Flow Examples (Metadata-Driven)

### Case 1: Skills Exist (Fast Path)

```
User: @agent-competitive-landscape-analyst "Analyze GLP-1 obesity landscape"
    ↓
Main Agent (Claude Code - Metadata-Driven)
    ├─ Read: competitive-landscape-analyst.md YAML metadata
    ├─ Infer from query:
    │   └─ therapeutic_area = "GLP-1 obesity"
    ├─ Apply patterns:
    │   ├─ get_{therapeutic_area}_trials → get_glp1_obesity_trials
    │   └─ get_{therapeutic_area}_fda_drugs → get_glp1_obesity_fda_drugs
    ├─ Check .claude/skills/:
    │   ├─ get_glp1_obesity_trials.py ✓ EXISTS
    │   └─ get_glp1_obesity_fda_drugs.py ✓ EXISTS
    ├─ Execute skills:
    │   ├─ Bash(python get_glp1_obesity_trials.py) → trials_data
    │   └─ Bash(python get_glp1_obesity_fda_drugs.py) → drugs_data
    ├─ Format prompt with data
    └─ Task(competitive-landscape-analyst, query + data)
        ↓
    competitive-landscape-analyst (unchanged body)
        └─ Analyze data → Return strategic insights

Timeline: ~20 seconds (skills already exist, just execute)
```

### Case 2: Skills Missing (Metadata-Driven Creation)

```
User: @agent-competitive-landscape-analyst "Analyze KRAS inhibitor landscape"
    ↓
Main Agent (Claude Code - Metadata-Driven)
    ├─ Read: competitive-landscape-analyst.md YAML metadata
    ├─ Infer from query:
    │   └─ therapeutic_area = "KRAS inhibitor"
    ├─ Apply patterns:
    │   ├─ get_{therapeutic_area}_trials → get_kras_inhibitor_trials
    │   └─ get_{therapeutic_area}_fda_drugs → get_kras_inhibitor_fda_drugs
    ├─ Check .claude/skills/:
    │   ├─ get_kras_inhibitor_trials.py ✗ MISSING
    │   └─ get_kras_inhibitor_fda_drugs.py ✗ MISSING
    ├─ Create missing skills:
    │   ├─ Task(pharma-search-specialist, "Create get_kras_inhibitor_trials")
    │   │   └─ Returns skill code
    │   ├─ Write(.claude/skills/get_kras_inhibitor_trials.py)
    │   ├─ Task(pharma-search-specialist, "Create get_kras_inhibitor_fda_drugs")
    │   │   └─ Returns skill code
    │   └─ Write(.claude/skills/get_kras_inhibitor_fda_drugs.py)
    ├─ Execute new skills:
    │   ├─ Bash(python get_kras_inhibitor_trials.py) → trials_data
    │   └─ Bash(python get_kras_inhibitor_fda_drugs.py) → drugs_data
    ├─ Format prompt with data
    └─ Task(competitive-landscape-analyst, query + data)
        ↓
    competitive-landscape-analyst (unchanged body)
        └─ Analyze data → Return strategic insights

Timeline: ~2 minutes (first time), ~20 seconds (subsequent reuse)
```

---

## Implementation Tasks

### 1. Create Strategic Agent Template

**File**: `.claude/.context/strategic-agent-template.md`

**Purpose**: Template for all Layer 3 strategic agents with delegation pattern

**Key Elements**:
- Capabilities-based structure
- Skills discovery logic (Read .claude/skills/)
- Delegation request format
- Analysis workflow (after data received)

**Tools Required**:
```yaml
tools:
  - Read  # For skills discovery and context
```

**Workflow Pattern**:
```markdown
## Your Workflow

### First Invocation (Discovery Phase)
1. Parse user query to determine data requirements
2. Read .claude/skills/ to discover available capabilities
3. Check if required skills exist
4. If missing:
   - Return delegation request to main agent
   - Specify exactly what skills needed and why
5. If exist:
   - Return execution request to main agent
   - Specify which skills to execute

### Second Invocation (Analysis Phase)
1. Receive collected data in prompt
2. Perform strategic analysis
3. Return insights and recommendations
```

### 2. Update competitive-landscape-analyst.md (Metadata Only)

**Changes**: Add YAML metadata at top (keep body 100% unchanged)

**Add to YAML frontmatter**:
```yaml
---
color: #10B981
name: competitive-landscape-analyst
description: ...
model: sonnet

# NEW: Data requirements metadata
data_requirements:
  # Core data (always collected for competitive analysis)
  always:
    - type: clinical_trials
      pattern: get_{therapeutic_area}_trials
      description: Clinical trial pipeline data
      sources: [ct_gov_mcp]

    - type: approved_drugs
      pattern: get_{therapeutic_area}_fda_drugs
      description: FDA approved drugs in therapeutic area
      sources: [fda_mcp]

  # Contextual data (collected based on query context)
  contextual:
    - type: company_pipeline
      pattern: get_{company}_trials
      trigger: company_name_in_query
      description: Specific competitor pipeline
      sources: [ct_gov_mcp]

    - type: patents
      pattern: get_{therapeutic_area}_patents
      trigger: keywords("IP", "patent", "freedom to operate")
      description: Patent landscape and IP positioning
      sources: [uspto_patents_mcp]
      optional: true

    - type: publications
      pattern: get_{therapeutic_area}_pubmed
      trigger: keywords("literature", "publications", "clinical data")
      description: Recent scientific publications
      sources: [pubmed_mcp]
      optional: true

    - type: financial_data
      pattern: get_{company}_sec_filings
      trigger: keywords("financial", "investment", "valuation", "R&D spending")
      description: Financial analysis and investment data
      sources: [sec_edgar_mcp]
      optional: true

# Inference rules for extracting parameters from queries
inference_rules:
  therapeutic_area: Extract disease/therapeutic area/drug class from query
  company: Extract company name if mentioned
  context_triggers: Analyze query intent for optional data needs
---
```

**Body of agent**: UNCHANGED - all capabilities stay exactly as-is

**Why this works**:
- 100+ capabilities described in body
- But only ~6 core data sources needed
- Capabilities = HOW agent analyzes (methods, frameworks)
- Data requirements = WHAT raw data needed (sources)
- Metadata stays small (~25 lines) while supporting all capabilities

### 3. Implement Main Agent Metadata-Driven Logic

**File**: `.claude/CLAUDE.md` update

**Add section**: "Metadata-Driven Data Collection Pattern"

**How it works**:
```markdown
## Metadata-Driven Data Collection Pattern

When user invokes strategic agent (@agent-[name]):

### Step 1: Read Agent Metadata
Main agent reads `.claude/agents/{agent_name}.md` YAML frontmatter:
- `data_requirements.always` - Core data always collected
- `data_requirements.contextual` - Optional data based on query
- `inference_rules` - How to extract parameters from query

### Step 2: Infer Parameters from Query
Parse user query using inference rules:
- Extract therapeutic_area (e.g., "KRAS inhibitor", "GLP-1", "Alzheimer's")
- Extract company name if mentioned
- Detect trigger keywords for contextual data

Example query: "Analyze KRAS inhibitor competitive landscape"
→ Inference: therapeutic_area="KRAS inhibitor", no company, no special keywords

### Step 3: Determine Required Skills
For each data requirement:
- Apply pattern template with inferred parameters
- `get_{therapeutic_area}_trials` → `get_kras_inhibitor_trials`
- `get_{therapeutic_area}_fda_drugs` → `get_kras_inhibitor_fda_drugs`
- Check contextual triggers (keywords, company presence)

### Step 4: Check/Create/Execute Skills
For each required skill:
1. Check if `.claude/skills/{skill_name}.py` exists
2. If missing:
   - Task(pharma-search-specialist, "Create {skill_name}")
   - Save returned skill (Write tool)
3. Execute skill (Bash)
4. Collect data

### Step 5: Invoke Agent with Data
Format prompt with collected data:
```
Analyze KRAS inhibitor competitive landscape.

Data available:
1. Clinical Trials: [data from get_kras_inhibitor_trials]
2. FDA Approved Drugs: [data from get_kras_inhibitor_fda_drugs]

Provide strategic analysis including competitive positioning,
market entry timing, and partnership opportunities.
```

Task(competitive-landscape-analyst, prompt_with_data)

### Step 6: Return Analysis
Agent analyzes data and returns strategic insights to user.

### Key Benefits
- ✅ Agent body unchanged (only metadata added)
- ✅ Main agent logic is generic (works for all strategic agents)
- ✅ Smart inference (same data source, different parameters)
- ✅ Contextual data collection (only when triggered)
- ✅ Small metadata footprint (~25 lines supports 100+ capabilities)
```

### 4. Document Skills Discovery Protocol

**File**: `.claude/skills/README.md` update

**Add**:
- Skills naming conventions
- Metadata format in .md files
- How agents discover skills

**Example**:
```markdown
## Skills Naming Convention

Pattern: `get_[therapeutic_area]_[data_type]_[specificity].py`

Examples:
- get_kras_fda_drugs.py
- get_alzheimers_phase2_trials_us.py
- get_glp1_obesity_trials_recruiting.py

## Discovery by Strategic Agents

Agents read .claude/skills/*.md files to:
1. Understand what data can be collected
2. Determine if existing skills meet requirements
3. Identify gaps for delegation requests

Each .md file contains:
- Purpose: What data the skill provides
- Returns: Data structure
- MCP Tools Used: Which servers/tools
- Example Output: Sample data
```

### 5. No Hardcoded Mappings Needed! 🎉

**Deleted**: skills-query-mapping.md (not needed)

**Why**: Strategic agents determine their own requirements dynamically.
- competitive-landscape-analyst decides what it needs for "KRAS landscape"
- clinical-development-strategist decides what it needs for "trial design"
- No central mapping file needed!

**This is the beauty of agent-driven delegation.**

### 6. Update pharma-search-specialist

**Changes**: None needed - already returns skill code to main agent

**Verify**: Two-phase persistence pattern working

---

## Testing Plan

### Test 1: Skills Exist (Fast Path)
```
User: @agent-competitive-landscape-analyst "Analyze GLP-1 obesity"
Expected:
- Main agent finds existing skills
- Executes directly
- Passes to analyst
- Returns insights in <1 min
```

### Test 2: Skills Missing (Full Orchestration)
```
User: @agent-competitive-landscape-analyst "Analyze KRAS landscape"
Expected:
- Main agent detects missing skills
- Invokes pharma-search-specialist 2-3 times
- Saves new skills
- Executes skills
- Passes to analyst
- Returns insights in <3 min
- Second query on same topic: <1 min
```

### Test 3: Multi-Source Analysis
```
User: @agent-competitive-landscape-analyst "Compare Pfizer vs Merck oncology pipelines"
Expected:
- Main agent identifies need for company-specific skills
- Creates: get_pfizer_trials, get_merck_trials
- Executes both
- Passes comparative data to analyst
- Returns competitive comparison
```

---

## Architecture Diagram (Delegation Pattern)

```
┌─────────────────────────────────────────────────────────────┐
│ USER                                                         │
│ @agent-competitive-landscape-analyst "Analyze KRAS"        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ TURN 1: Initial Invocation                                  │
│                                                              │
│ Main Agent → Task(competitive-landscape-analyst)            │
│                         ↓                                    │
│ competitive-landscape-analyst (Discovery Phase)             │
│ ├─ Read .claude/skills/                                     │
│ ├─ Determine: Need get_kras_fda_drugs.py ✗                  │
│ ├─ Determine: Need get_kras_trials.py ✗                     │
│ └─ Return delegation request:                               │
│    "Missing skills: get_kras_fda_drugs, get_kras_trials     │
│     Please create via pharma-search-specialist"             │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ TURN 2: Fulfillment                                         │
│                                                              │
│ Main Agent (Fulfills Request)                               │
│ ├─ Task(pharma-search-specialist, "get_kras_fda_drugs")     │
│ │   └─ Returns skill code                                   │
│ ├─ Write(.claude/skills/get_kras_fda_drugs.py)              │
│ ├─ Task(pharma-search-specialist, "get_kras_trials")        │
│ │   └─ Returns skill code                                   │
│ ├─ Write(.claude/skills/get_kras_trials.py)                 │
│ ├─ Bash(python get_kras_fda_drugs.py) → data1              │
│ ├─ Bash(python get_kras_trials.py) → data2                 │
│ └─ Task(competitive-landscape-analyst, data1 + data2)       │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ TURN 3: Analysis                                            │
│                                                              │
│ competitive-landscape-analyst (Analysis Phase)              │
│ ├─ Receives: FDA data + Trial data                          │
│ ├─ Analyze competitive positioning                          │
│ ├─ Generate strategic recommendations                       │
│ └─ Return insights to main agent                            │
│                         ↓                                    │
│ Main Agent → User (Strategic analysis)                      │
└─────────────────────────────────────────────────────────────┘

KEY: Agent determines requirements → Main agent fulfills → Agent analyzes
```

---

## Key Decisions

### ✅ Agent-Driven Delegation (Not Pre-Programmed Orchestration)
- **Why**: Agents know best what data they need for analysis
- **How**: Agents discover skills, return delegation requests to main agent
- **Benefit**: Zero hardcoded mappings, infinite extensibility

### ✅ Multi-Turn Conversation Pattern
- **Turn 1**: Agent discovers requirements, delegates to main
- **Turn 2**: Main fulfills (create skills, execute, collect data)
- **Turn 3**: Agent analyzes with data
- **Why**: Works within Claude Code sub-agent constraints

### ✅ Skills Library as Discovery Interface
- **Why**: Agents need to know what data collection is possible
- **How**: Read .claude/skills/*.md for capabilities
- **Format**: Structured metadata (Purpose, Returns, MCP Tools)

### ✅ Delegation Request Format
- **Structure**: Clear, explicit, actionable
- **Contains**: Required skills, why needed, execution instructions
- **Benefit**: Main agent can fulfill blindly (no interpretation needed)

---

## Benefits

### 🎯 Zero Hardcoding
- No query-to-skills mappings
- No pre-programmed data requirements
- Agents determine needs dynamically

### 🧠 Agent Intelligence
- Agents understand their own domain
- Smart skill discovery
- Contextual requirement determination

### 🔄 Self-Improving System
- Skills library grows organically
- Second queries 5-10x faster
- Accumulates institutional knowledge

### 🏗️ Infinite Extensibility
- Add new strategic agents without central coordination
- Each agent brings its own expertise
- No bottlenecks or coordination files

### 👁️ Transparent to User
- See delegation requests
- Understand what's being created
- Follow the multi-turn flow

### ⚡ Respects Constraints
- Works within Claude Code sub-agent limitations
- No sub-agent nesting attempts
- Main agent coordinates naturally

---

## Migration Path

### Phase 1: Strategic Agent Template
- Create template documentation
- Update competitive-landscape-analyst

### Phase 2: Main Agent Logic
- Document orchestration pattern in CLAUDE.md
- Create skills-query mapping guide

### Phase 3: Testing
- Test with existing skills (GLP-1)
- Test with missing skills (KRAS)
- Verify skills library growth

### Phase 4: Expand
- Add more strategic agents using template
- Build out skills library organically

---

## Success Metrics

- ✅ Strategic agent can analyze without data fetching code
- ✅ Main agent successfully coordinates skill creation
- ✅ Skills library grows with each new query
- ✅ Second query on same topic 5x faster
- ✅ User sees clean analysis, not orchestration complexity

---

## Open Questions

1. **Skill caching**: Should main agent cache executed skill results?
2. **Parallel execution**: Should main agent run skill creation in parallel?
3. **Error handling**: What if skill creation fails?
4. **Skill versioning**: How to handle skill updates?

---

## Next Steps

1. Review this plan with user
2. Get approval to proceed
3. Implement Phase 1 (templates)
4. Test with competitive-landscape-analyst
5. Iterate based on results
