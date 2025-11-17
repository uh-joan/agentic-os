# Create Plan Command

**Purpose**: Use search-orchestrator to analyze project context files and generate a comprehensive Task Master workflow with proper dependencies and agent delegations.

**Usage**: `/create-plan`

**Prerequisites**:
- Context files must exist (run `/primer` first if not present):
  - `project-brief.md`
  - `user-profile.md`
  - `PROJECT_WORKFLOW.md`
  - `.claude/project-context.md`

---

## Workflow

### Step 1: Validate Context Files
Verify that all required context files exist and are readable:
- `project-brief.md` (root directory)
- `user-profile.md` (root directory)
- `PROJECT_WORKFLOW.md` (root directory)
- `.claude/project-context.md` (.claude/ directory)

If any files are missing, prompt the user to run `/primer` first.

### Step 2: Invoke search-orchestrator
Invoke the search-orchestrator agent with the project context files.

**Prompt**:
```
Analyze these project context files and create a comprehensive workflow plan:

Context files available:
- project-brief.md: Strategic question, lead compounds, decision criteria, stakeholder expectations
- user-profile.md: Decision maker profile, technical depth, presentation preferences
- PROJECT_WORKFLOW.md: 5-phase workflow structure with database requirements
- .claude/project-context.md: Agent-facing decision framework

Create a complete search plan following your standard JSON format with:
1. **mcp_queries**: All data gathering tasks (PubChem, PubMed, ClinicalTrials.gov, FDA, OpenTargets, Data Commons queries)
2. **specialist_delegations**: All analysis tasks needed (target validation, SAR analysis, DMPK profiling, competitive analysis, etc.)
3. **synthesis_plan**: Final compilation and report generation

Mark each query with priority ("core" vs "supplementary") and specify exact query parameters.
```

The agent will return a comprehensive JSON plan with both data gathering queries and specialist analysis delegations.

### Step 3: Parse Workflow Plan
Extract from the search-orchestrator JSON response and map to Task Master tasks:

**From `mcp_queries` array** → Data gathering tasks:
- Extract: query_id, priority, tool, method, params, purpose
- Agent: pharma-search-specialist (all data gathering uses this agent)
- Dependencies: Empty array `[]` (Phase 1 tasks have no dependencies)
- Output location: `data_dump/YYYYMMDD_HHMMSS_[database]_[query]/`

**From `specialist_delegations` array** → Analysis tasks:
- Extract: agent name, input_needed, reason, timing
- Agent: Specified specialist agent (pharma-medicinal-chemist, pharma-target-validator, etc.)
- Dependencies: Task IDs of data gathering tasks that provide required input
- Output location: `temp/[analysis_name].md`

**From `synthesis_plan`** → Final compilation task:
- Extract: agent_chain (usually ends with pharma-report-compiler)
- Dependencies: All analysis task IDs
- Output location: `reports/[project_name]_YYYYMMDD.md`

**Task Count**:
- Data gathering: Count of `mcp_queries` array length
- Analysis: Count of `specialist_delegations` array length
- Compilation: 1 task (from `synthesis_plan`)
- Total: Sum of all tasks

### Step 4: Clear Existing Task Master Tasks
Before creating new tasks:
1. Get current Task Master tasks
2. If tasks exist, ask user for confirmation to clear them
3. Remove all existing tasks if confirmed

### Step 5: Create Task Master Tasks
**CRITICAL**: Write tasks directly to `.taskmaster/tasks/tasks.json` to bypass Task Master's AI interpretation.

**Process**:
1. Read the current `.taskmaster/tasks/tasks.json` file
2. Clear existing tasks array or create new empty structure if needed
3. For each task in the orchestrator plan:
   - Create a task object with exact delegation format (see below)
   - Add to the tasks array
4. Update the `metadata.updated` timestamp to current ISO datetime
5. Write the updated JSON back to `.taskmaster/tasks/tasks.json`
6. **CRITICAL**: Run `task-master generate` to create individual task markdown files in `.taskmaster/tasks/` directory

**Why this approach**:
- Task Master's `add_task` and `update_task` commands use AI to interpret prompts, which adds unwanted "implementation" language
- Writing directly to JSON bypasses AI interpretation completely
- Tasks get the EXACT agent delegation format specified
- `task-master generate` syncs the JSON to individual markdown files without AI processing

**For each task**:
- Determine task type from orchestrator plan (data_gathering or analysis)
- Extract task title, description, and details from workflow plan
- **CRITICAL**: Use correct agent delegation format based on task type:
  - **Data gathering tasks** → `**AGENT DELEGATION**: Invoke pharma-search-specialist agent`
  - **Analysis tasks** → `**AGENT DELEGATION**: Invoke [pharma-medicinal-chemist/pharma-dmpk-adme-profiler/pharma-landscape-competitive-analyst/pharma-report-compiler] agent`
- Identify dependencies based on:
  - Input data requirements (analysis tasks depend on data gathering tasks that produce needed data)
  - Phase sequencing (later phases depend on earlier phases)
  - Agent delegation chains (synthesis tasks depend on analysis tasks)
- Set priority based on critical path analysis
- Map to output locations:
  - Data gathering → `data_dump/YYYYMMDD_HHMMSS_[source]/`
  - Analysis/synthesis → `temp/[analysis_name].md`
  - Final compilation → `reports/[project_name]_YYYYMMDD.md`

**Task Object Structure** (write this exact JSON structure):
```json
{
  "id": [task_number],
  "title": "[Task title from orchestrator plan]",
  "description": "[Brief description mentioning agent name]",
  "status": "pending",
  "dependencies": [array of prerequisite task IDs],
  "priority": "high|medium|low",
  "details": "[EXACT agent delegation format from section below]",
  "testStrategy": "",
  "subtasks": []
}
```

**Task Creation Guidelines**:
- Independent tasks: Empty dependencies array `[]`
- Dependent tasks: Set dependencies array with prerequisite task IDs
- Agent delegation tasks: Use EXACT format in details field (no AI interpretation)
- NO subtasks (keep subtasks array empty `[]`)

**CRITICAL - Agent Delegation Format**:
All task details must use explicit agent invocation syntax following the atomic architecture:

**For Data Gathering Tasks** (PubChem, PubMed, ClinicalTrials.gov, etc.):
```
**AGENT DELEGATION**: Invoke pharma-search-specialist agent

Provide the agent with these parameters:
- Database: [PubChem/PubMed/ClinicalTrials.gov/etc.]
- Method: [search_compounds/search_by_smiles/etc.]
- Query: [specific search parameters]
- Purpose: [why this search is needed]

The agent will:
1. Execute the MCP database query
2. Return structured results to Claude Code
3. Claude Code will save results to data_dump/YYYYMMDD_HHMMSS_[source]/
```

**For Analysis/Synthesis Tasks** (competitive analysis, target validation, etc.):
```
**AGENT DELEGATION**: Invoke [agent-name] agent

Provide the agent with:
- Input data: Read from [data_dump/folder/ or temp/file.md]
- Analysis type: [competitive analysis/target validation/etc.]
- Expected output: [specific deliverables]

The agent will:
1. Read specified input files
2. Perform analysis
3. Return plain text markdown to Claude Code
4. Claude Code will save results to temp/[analysis_name].md
```

**Example - Complete Task JSON for Data Gathering**:
```json
{
  "id": 1,
  "title": "Profile Sotorasib via PubChem",
  "description": "Retrieve physicochemical properties for sotorasib using pharma-search-specialist",
  "status": "pending",
  "dependencies": [],
  "priority": "high",
  "details": "**AGENT DELEGATION**: Invoke pharma-search-specialist agent\n\nProvide the agent with these parameters:\n- Database: PubChem\n- Method: search_compounds\n- Query: sotorasib\n- Purpose: Map sotorasib (AMG 510, Lumakras) to CID for property retrieval\n\nThe agent will:\n1. Execute PubChem search_compounds query\n2. Return CID and basic compound info to Claude Code\n3. Claude Code will save results to data_dump/YYYYMMDD_HHMMSS_pubchem_sotorasib/\n\nExpected properties: Molecular weight, LogP, TPSA, HBD/HBA, rotatable bonds, CNS MPO score",
  "testStrategy": "",
  "subtasks": []
}
```

**Example - Complete Task JSON for Analysis**:
```json
{
  "id": 13,
  "title": "Comparative SAR Analysis for Resistance Coverage",
  "description": "Analyze resistance mutation coverage (Y96D/H95D) across RMC leads using pharma-medicinal-chemist",
  "status": "pending",
  "dependencies": [1, 2, 3, 4, 5, 7, 8],
  "priority": "high",
  "details": "**AGENT DELEGATION**: Invoke pharma-medicinal-chemist agent\n\nProvide the agent with:\n- Input data: Read from data_dump/ folders (Tasks 1-5: compound profiles, Task 7: KRAS structure, Task 8: resistance SAR literature)\n- Analysis type: Comparative SAR analysis for resistance mutation coverage (Y96D/H95D)\n- Expected output: SAR analysis comparing RMC-6292/6293/6294 resistance coverage with structural rationale\n\nThe agent will:\n1. Read PubChem compound data for all 5 compounds\n2. Read KRAS protein structure data (Y96D/H95D positions)\n3. Read structural biology literature on resistance mechanisms\n4. Perform comparative SAR analysis\n5. Return plain text markdown SAR analysis to Claude Code\n6. Claude Code will save results to temp/sar_analysis_resistance_coverage.md",
  "testStrategy": "",
  "subtasks": []
}
```

### Step 6: Summary Report
Provide a comprehensive summary:

**Project Overview**:
- Project name and strategic question
- Decision maker and timeline
- Key decision criteria

**Task Master Workflow**:
- Total tasks created
- Task breakdown by phase
- Dependency graph overview
- Estimated duration

**Key Files**:
- Context files and their purposes
- Expected output locations (data_dump/, temp/, reports/)

**Next Steps**:
- How to view tasks: `task-master get-tasks`
- How to start execution: Begin with Phase 1 tasks
- How to track progress: Use task status updates

---

## Example Usage

```bash
/create-plan
```

**Expected Output**:
```
✅ Validated context files (all 4 present)
✅ Invoked search-orchestrator
✅ Parsed search plan (17 MCP queries, 5 phases)
✅ Cleared existing Task Master tasks (10 removed)
✅ Created 17 new Task Master tasks

📋 Project Overview:
- Project: KRAS G12C Next-Generation Lead Optimization
- Decision: Which lead (RMC-6292/6293/6294) advances to IND-enabling studies?
- Stakeholder: Adrian Gill, Ph.D., EVP Discovery Chemistry (Revolution Medicines)
- Timeline: Q1 2026 decision (IND filing Q3 2026)

📊 Task Master Workflow:
- Phase 1: Data Gathering (7 tasks, no dependencies)
  * PubChem queries (3 tasks)
  * OpenTargets queries (2 tasks)
  * ClinicalTrials.gov queries (2 tasks)
- Phase 2: Target Validation (1 task, depends on tasks 3-4)
  * pharma-target-validator synthesis
- Phase 3: Resistance SAR & DMPK (3 tasks, depends on Phase 1)
  * PubMed SAR queries (2 tasks)
  * pharma-dmpk-adme-profiler analysis (1 task)
- Phase 4: Medicinal Chemistry (3 tasks, depends on Phase 3)
  * PubChem chemical space (1 task)
  * PubMed optimization strategies (1 task)
  * pharma-medicinal-chemist recommendation (1 task)
- Phase 5: Competitive Positioning & Compilation (3 tasks, depends on Phase 4)
  * PubMed competitive data (1 task)
  * pharma-landscape-competitive-analyst (1 task)
  * pharma-report-compiler final report (1 task)

Total: 17 tasks
Estimated Duration: 2.5-3.5 hours

📁 Key Context Files:
- project-brief.md (7,908 bytes): Strategic scenario, decision criteria
- user-profile.md (12,869 bytes): Adrian Gill profile, expectations
- PROJECT_WORKFLOW.md (25,937 bytes): 5-phase workflow guide
- .claude/project-context.md (17,758 bytes): Agent-facing framework

📂 Expected Outputs:
- data_dump/: Raw MCP database query results (timestamped folders)
- temp/: Intermediate analysis outputs (markdown files)
- reports/: Final executive decision document

🎯 Next Steps:
1. View tasks: Use Task Master `list` command
2. Start Phase 1: Execute tasks 1-7 (data gathering)
3. Track progress: Update task status as you complete each phase
4. Phase dependencies: Complete Phase 1 before starting Phase 2

➡️  Ready to begin! Start with Phase 1 tasks (1-7) to gather data.
```

---

## Error Handling

**Missing Context Files**:
```
❌ Error: Context files not found
- Missing: project-brief.md, user-profile.md

➡️  Run `/primer <source_file>` first to create context files
```

**search-orchestrator Failure**:
```
❌ Error: search-orchestrator failed to generate search plan

Troubleshooting:
1. Check that context files contain sufficient detail
2. Verify PROJECT_WORKFLOW.md has 5-phase structure
3. Re-run `/primer` with more detailed source file
```

**Task Master Conflict**:
```
⚠️  Warning: 10 existing Task Master tasks found

Options:
1. Clear and create new tasks (recommended)
2. Append to existing tasks (may cause conflicts)
3. Cancel (keep existing tasks)

Enter choice [1/2/3]: _
```

---

## Notes

- This command requires context files created by `/primer`
- Existing Task Master tasks will be cleared (with confirmation)
- The search-orchestrator uses AI to create the optimal search plan
- Task dependencies are automatically set based on the search plan
- Phase 1 tasks have no dependencies (can be executed in any order)
- Specialist agent tasks (Phases 2-5) have sequential dependencies

---

## Related Commands

- `/primer` - Initialize project context files from source document
