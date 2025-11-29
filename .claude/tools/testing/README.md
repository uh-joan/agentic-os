# Skill Testing Infrastructure - Closing the Agentic Loop

## Overview

Autonomous skill validation and self-healing system that closes the agentic loop through:

1. **Automated Testing** - Comprehensive validation (syntax, imports, execution, data, schema)
2. **Intelligent Analysis** - Root cause detection and repair guidance
3. **Agent Integration** - Seamless pharma-search-specialist invocation for repairs
4. **Iterative Verification** - Retry until success or max iterations
5. **Health Tracking** - Integration with skill discovery system

**Result**: Self-healing skill library with autonomous quality assurance.

## Quick Start

### Test a Single Skill

```bash
# Run tests
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/glp1-trials/scripts/get_glp1_trials.py

# Exit code 0 = passed, 1 = failed
```

### Test with Self-Healing

```bash
# Run orchestrator (generates repair instructions)
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py \
  --json

# If failed, repair prompt is in output['agent_prompt']
# Claude Code invokes pharma-search-specialist with this prompt
# Re-test with --iteration 2
```

### Test All Skills

```bash
# Test entire library
python3 .claude/tools/testing/batch_test_skills.py

# Update health status in index
python3 .claude/tools/testing/batch_test_skills.py --update-health

# Generate JSON report
python3 .claude/tools/testing/batch_test_skills.py --json --output health_report.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Claude Code Main Agent                     │
│                                                              │
│  Workflow:                                                   │
│  1. Run test_orchestrator.py                                │
│  2. Parse failure analysis                                  │
│  3. Invoke pharma-search-specialist with repair prompt      │
│  4. Save fixed code                                         │
│  5. Re-test (iteration++)                                   │
│  6. Repeat until success or max iterations                  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ├────────────────┐
                             ▼                ▼
                  ┌──────────────────┐  ┌─────────────────────┐
                  │ Test Orchestrator│  │ pharma-search-      │
                  │                  │  │   specialist        │
                  │ • Analyzes fails │  │                     │
                  │ • Generates      │  │ • Reads skill       │
                  │   repair prompts │  │ • Analyzes issues   │
                  │ • Tracks iters   │  │ • Generates fix     │
                  └──────────────────┘  │ • Returns code      │
                             │           └─────────────────────┘
                             ▼
                  ┌──────────────────┐
                  │   Test Runner    │
                  │                  │
                  │ 1. Syntax ✓      │
                  │ 2. Import ✓      │
                  │ 3. Execution ✓   │
                  │ 4. Data ✓        │
                  │ 5. Schema ✓      │
                  └──────────────────┘
                             │
                             ▼
                  ┌──────────────────┐
                  │  Health Check    │
                  │                  │
                  │ • Update status  │
                  │ • Track issues   │
                  │ • Index sync     │
                  └──────────────────┘
```

## Components

### 1. test_runner.py - Core Testing Engine

**Purpose**: Execute comprehensive tests on individual skills

**Five-Level Test Suite**:

1. **Syntax Test** - Python code compiles without errors
   - Uses `ast.parse()` to validate syntax
   - Detects: Missing colons, brackets, indentation errors
   - Exit on failure (can't proceed if syntax is broken)

2. **Import Test** - All dependencies available
   - Loads module with `importlib`
   - Tests MCP server imports
   - Detects: Missing modules, incorrect import paths
   - Exit on failure (can't execute without imports)

3. **Execution Test** - Skill runs without exceptions
   - Runs skill in subprocess with 60s timeout
   - Sets PYTHONPATH for MCP imports
   - Detects: Runtime errors, exceptions, crashes
   - Captures stdout/stderr for analysis

4. **Data Test** - Query returns results (not zero)
   - Parses execution output
   - Checks for "0 results" patterns
   - Detects: Overly restrictive queries, empty datasets
   - Validates data was actually collected

5. **Schema Test** - Output matches expected format
   - Infers skill type from name (trials, fda_drugs, patents, etc.)
   - Checks for expected field patterns
   - Detects: Malformed output, missing fields

**Usage**:
```bash
# Basic test
python3 .claude/tools/testing/test_runner.py path/to/skill.py

# With arguments
python3 .claude/tools/testing/test_runner.py path/to/skill.py --args "arg1" "arg2"

# JSON output (for programmatic use)
python3 .claude/tools/testing/test_runner.py path/to/skill.py --json
```

**Exit Codes**:
- `0`: All tests passed
- `1`: Some tests failed

**Output Format**:
```
============================================================
Test Report: skill_name
============================================================
Path: /path/to/skill.py
Overall Status: PASSED | FAILED | ERROR
Tests: X/5 passed
============================================================

1. [✓] SYNTAX: Python syntax is valid
2. [✓] IMPORT: All imports successful
3. [✓] EXECUTION: Skill executed successfully
   Execution time: 2.34s
4. [✓] DATA: Data returned successfully
   Details: {"output_length": 1523}
5. [✓] SCHEMA: Output schema matches expected format
   Details: {"matched_patterns": ["NCT", "Phase", "Status"]}
```

### 2. test_orchestrator.py - Self-Healing Orchestrator

**Purpose**: Orchestrate testing with intelligent failure analysis

**Capabilities**:
- Runs test_runner.py
- Analyzes test failures by type
- Generates detailed repair instructions
- Creates repair prompt for pharma-search-specialist
- Tracks iteration count (prevents infinite loops)

**Failure Analysis Engine**:

Each test failure is analyzed to generate specific repair instructions:

**Syntax Errors**:
```python
issue_type: "syntax_error"
severity: "critical"
suggested_fix: "Fix syntax error in the Python code. Ensure proper
                indentation, closing brackets, and valid Python syntax."
code_location: Line number from error
```

**Import Errors**:
```python
issue_type: "import_error"
severity: "critical"
suggested_fix:
  - MCP imports: "Fix MCP import path. Ensure sys.path includes .claude..."
  - Missing modules: "Install missing dependency: {module}..."
  - Other: "Fix import error. Review all import statements..."
```

**Execution Errors** (with pattern matching):
```python
KeyError → "Use .get() method instead of direct dictionary access..."
IndexError → "Check list length before accessing indices..."
AttributeError → "Validate object type before accessing attributes..."
TypeError → "Validate data types before operations..."
Connection/timeout → "Add retry logic with exponential backoff..."
API errors → "Verify API parameters, add rate limiting..."
```

**Data Errors**:
```python
No output → "Ensure print() statements output results..."
Zero results → "Query parameters too restrictive - try broader search..."
```

**Schema Errors**:
```python
Missing patterns → "Output schema doesn't match expected format.
                    Expected: NCT, Phase, Status
                    Matched: <none>
                    Ensure output includes standard field names..."
```

**Usage**:
```bash
# Run orchestration
python3 .claude/tools/testing/test_orchestrator.py path/to/skill.py

# Specify iteration and max
python3 .claude/tools/testing/test_orchestrator.py path/to/skill.py \
  --iteration 2 \
  --max-iterations 3

# JSON output (for Claude Code integration)
python3 .claude/tools/testing/test_orchestrator.py path/to/skill.py --json
```

**Exit Codes**:
- `0`: All tests passed
- `1`: Needs repair (iterations remaining)
- `2`: Max iterations exceeded

**Output Format**:
```
============================================================
Test Orchestration Summary
============================================================
Skill: skill_name
Path: path/to/skill.py
Iteration: 1/3
Status: FAILED
Tests: 2/5 passed
============================================================

REPAIR NEEDED: 3 issue(s) detected

1. [CRITICAL] import_error
   Description: Import failed: No module named 'mcp.servers.ct_gov_mcp'
   Suggested Fix: Fix MCP import path. Ensure:
   1. Import uses correct path: `from mcp.servers.{server}_mcp import {function}`
   2. sys.path includes .claude directory: `sys.path.insert(0, ".claude")`
   3. MCP server exists in .claude/mcp/servers/

2. [HIGH] execution_error
   Execution failed with exit code 1

3. [MEDIUM] schema_validation_error
   Output schema doesn't match expected format

NEXT STEP: Invoke pharma-search-specialist with repair prompt

============================================================
AGENT REPAIR PROMPT
============================================================
SKILL REPAIR REQUEST (Iteration 1/3)

Skill: skill_name
Path: path/to/skill.py
Test Status: failed
Tests: 2/5 passed

ISSUES DETECTED:
[Detailed issue list with suggested fixes...]

EXECUTION OUTPUT:
[Last 1000 chars of stdout...]

ERROR OUTPUT:
[Last 1000 chars of stderr...]

TASK:
Read the skill file at {path} and fix ALL issues listed above.

REQUIREMENTS:
1. Fix critical issues first (syntax, imports)
2. Fix high-severity issues (execution, data)
3. Fix medium-severity issues (schema)
4. Ensure skill is executable standalone
5. Add error handling and defensive programming
6. Test locally before returning code

Return the complete fixed skill code ready to save to {path}.
```

### 3. batch_test_skills.py - Library Health Scanner

**Purpose**: Test all skills and generate health report

**Capabilities**:
- Loads skills from index.json
- Tests each skill sequentially
- Updates health status in index
- Generates comprehensive report
- Provides summary statistics

**Usage**:
```bash
# Test all skills (read-only)
python3 .claude/tools/testing/batch_test_skills.py

# Update health status in index
python3 .claude/tools/testing/batch_test_skills.py --update-health

# Generate JSON report
python3 .claude/tools/testing/batch_test_skills.py --json

# Save to file
python3 .claude/tools/testing/batch_test_skills.py --output health_report.json
```

**Exit Codes**:
- `0`: All skills healthy
- `1`: Mostly healthy, some broken
- `2`: Mostly broken

**Output Format**:
```
Testing 47 skills...

1/47 [TEST] glp1-trials... ✓ PASSED (5/5)
2/47 [TEST] kras-trials... ✗ FAILED (3/5)
3/47 [TEST] fda-glp1-drugs... ✓ PASSED (5/5)
...

============================================================
Skill Library Health Report
============================================================
Total Skills:    47
✓ Healthy:       42 (89.4%)
✗ Broken:        4 (8.5%)
○ Untested:      1 (2.1%)
============================================================

FAILED SKILLS:

✗ kras-trials
  Path: .claude/skills/kras-trials/scripts/get_kras_trials.py
  Issues:
    - execution: KeyError 'NCTId' in response parsing
    - data: Query returned zero results

✗ patent-search
  Path: .claude/skills/patent-search/scripts/search_patents.py
  Issues:
    - execution: Connection timeout after 60s

...
```

## Claude Code Integration

### Pattern 1: Test After Creation (Recommended)

**Always test new skills immediately after creation**:

```python
# User: "Create skill to get KRAS trials"

# Step 1: Create skill via pharma-search-specialist
Task(
    subagent_type='pharma-search-specialist',
    description='Create KRAS trials skill',
    prompt="Create skill to get KRAS inhibitor clinical trials"
)

# Agent returns: skill_code, skill_md

# Step 2: Save skill files
Write(".claude/skills/kras-trials/SKILL.md", skill_md)
Write(".claude/skills/kras-trials/scripts/get_kras_trials.py", skill_code)

# Step 3: TEST IMMEDIATELY (close the loop)
Bash("python3 .claude/tools/testing/test_orchestrator.py \
      .claude/skills/kras-trials/scripts/get_kras_trials.py \
      --json")

result = json.loads(bash_output)

# Step 4a: If passed - finalize
if result['test_report']['overall_status'] == 'passed':
    print(f"✓ Skill created and verified!")
    print(f"  Tests: {result['test_report']['passed_tests']}/5 passed")

    # Update index
    Bash("python3 .claude/tools/skill_discovery/index_updater.py add \
          --name kras-trials --folder kras-trials ...")

# Step 4b: If failed - repair iteratively
else:
    iteration = 1
    max_iterations = 3

    while result['needs_repair'] and iteration < max_iterations:
        print(f"Iteration {iteration}: {len(result['repair_instructions'])} issues detected")
        print(f"Invoking pharma-search-specialist for repair...")

        # Invoke agent with repair prompt
        Task(
            subagent_type='pharma-search-specialist',
            description=f'Repair KRAS trials skill (iteration {iteration})',
            prompt=result['agent_prompt']
        )

        # Agent returns: fixed_code

        # Save fixed code
        Write(".claude/skills/kras-trials/scripts/get_kras_trials.py", fixed_code)

        # Re-test
        iteration += 1
        Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
              .claude/skills/kras-trials/scripts/get_kras_trials.py \
              --iteration {iteration} \
              --json")

        result = json.loads(bash_output)

    # Final status
    if result['test_report']['overall_status'] == 'passed':
        print(f"✓ Skill repaired successfully after {iteration} iteration(s)!")

        # Update index
        Bash("python3 .claude/tools/skill_discovery/index_updater.py add ...")
    else:
        print(f"✗ Max iterations ({max_iterations}) exceeded")
        print(f"  Manual intervention required")
        print(f"  Remaining issues: {len(result['repair_instructions'])}")
```

### Pattern 2: Test Before Reuse

**Verify skill health before execution**:

```python
# User: "Run the GLP-1 trials skill"

skill_path = ".claude/skills/glp1-trials/scripts/get_glp1_trials.py"

# Step 1: Test skill health
Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")
result = json.loads(bash_output)

# Step 2a: If healthy - execute
if result['test_report']['overall_status'] == 'passed':
    print("Skill is healthy, executing...")
    Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")

# Step 2b: If broken - repair first
else:
    print(f"Skill has {len(result['repair_instructions'])} issues, repairing first...")

    # Repair workflow (same as Pattern 1, Step 4b)
    # ...

    # After repair succeeds, execute
    Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
```

### Pattern 3: Periodic Health Check

**Maintain library quality over time**:

```python
# User: "Check skill library health"

# Run batch test
Bash("python3 .claude/tools/testing/batch_test_skills.py --update-health --json")
summary = json.loads(bash_output)

# Report summary
print(f"Skill Library Health:")
print(f"  ✓ Healthy: {summary['healthy_skills']}/{summary['total_skills']} ({summary['health_percentage']}%)")
print(f"  ✗ Broken: {summary['broken_skills']}")

# If broken skills exist, offer to repair
if summary['broken_skills'] > 0:
    print(f"\nBroken skills:")
    for result in summary['test_results']:
        if result['status'] == 'failed':
            print(f"  - {result['skill_name']}: {len(result.get('issues', []))} issue(s)")

    # User decides whether to repair all or skip
    # If repair: iterate through broken skills and apply Pattern 1 workflow
```

## Test Case Definitions

### Clinical Trials Skills

**Pattern**: Query CT.gov for specific therapeutic area/phase

**Expected Behavior**:
- ✅ Imports `from mcp.servers.ct_gov_mcp import search`
- ✅ Uses markdown parsing (CT.gov returns markdown string)
- ✅ Implements pagination (pageSize parameter)
- ✅ Returns > 0 trials (unless data truly doesn't exist)
- ✅ Output includes: NCT ID, Phase, Status, Sponsor

**Schema Patterns**: `['NCT', 'Phase', 'Status', 'Sponsor']`

**Common Failures**:
- Markdown parsing breaks on unexpected format → Use regex patterns
- Pagination not implemented → Results truncated at default limit
- Query too restrictive → Zero results (broaden search terms)

**Example**:
```python
def get_glp1_trials():
    result = search(
        term="GLP-1 receptor agonist",
        phase="PHASE3",
        pageSize=100
    )
    # Parse markdown response...
    return {'total_count': count, 'trials_summary': result}
```

### FDA Drug Skills

**Pattern**: Query FDA for approved drugs by search term

**Expected Behavior**:
- ✅ Imports `from mcp.servers.fda_mcp import lookup`
- ✅ Uses JSON parsing (FDA returns dict)
- ✅ Uses `.get()` for safe field access (not `[]`)
- ✅ Returns > 0 drugs
- ✅ Output includes: Application, Product, Approval Date, Status

**Schema Patterns**: `['Application', 'Product', 'Approval', 'Date']`

**Common Failures**:
- KeyError from direct dict access → Use `.get()` method
- Wrong search_type → Use 'label' for drug names
- Missing field handling → Check if field exists before access

**Example**:
```python
def get_glp1_fda_drugs():
    result = lookup(
        search_term="semaglutide",
        search_type="label"
    )
    # Safe JSON parsing with .get()...
    return {'total_count': count, 'drugs': result}
```

### Patent Skills

**Pattern**: Query USPTO for patents by term

**Expected Behavior**:
- ✅ Imports `from mcp.servers.uspto_patents_mcp import search`
- ✅ Handles pagination for large result sets
- ✅ Returns > 0 patents
- ✅ Output includes: Patent #, Publication Date, Inventor, Assignee

**Schema Patterns**: `['Patent', 'Publication', 'Inventor', 'Assignee']`

**Common Failures**:
- Query syntax errors → Review USPTO query syntax
- Pagination issues → Implement offset/limit properly
- Missing assignee/inventor → Use `.get()` with defaults

### Publication Skills

**Pattern**: Query PubMed for publications

**Expected Behavior**:
- ✅ Imports `from mcp.servers.pubmed_mcp import search`
- ✅ Date filtering implemented correctly
- ✅ Returns > 0 publications
- ✅ Output includes: PMID, Title, Authors, Journal

**Schema Patterns**: `['PMID', 'Title', 'Author', 'Journal']`

**Common Failures**:
- Query too narrow → Broaden search terms
- Missing metadata → Handle optional fields
- Date format issues → Validate date strings

### Financial Skills

**Pattern**: Query SEC/Yahoo Finance for financial data

**Expected Behavior**:
- ✅ Imports correct MCP server
- ✅ Handles company ticker/CIK resolution
- ✅ Returns financial data
- ✅ Output includes: Revenue, Company, Symbol/CIK

**Schema Patterns**: `['Revenue', 'Symbol', 'Company', 'Price']`

**Common Failures**:
- Company not found → Validate ticker/CIK
- Missing data → Not all companies report segments
- Type conversion → String vs number handling

## Health Check Integration

The testing system integrates with `.claude/tools/skill_discovery/health_check.py`:

```python
from skill_discovery.health_check import update_skill_health, HealthStatus

# After testing
if test_passed:
    update_skill_health(skill_name, HealthStatus.HEALTHY, [])
else:
    issues = [f"{test}: {message}" for test, message in failures]
    update_skill_health(skill_name, HealthStatus.BROKEN, issues)
```

**Benefits**:
- ✅ Strategy system excludes broken skills from REUSE
- ✅ Health status visible in index queries
- ✅ Tracking skill quality over time
- ✅ Automatic failover to CREATE strategy when skill broken

**Health Status States**:
- `HEALTHY`: All tests passed, safe to use
- `BROKEN`: Tests failed, needs repair
- `UNKNOWN`: Not tested yet

## Troubleshooting

### Issue: Import errors persist after repair

**Symptoms**:
```
ImportError: No module named 'mcp.servers.ct_gov_mcp'
```

**Solutions**:
1. Check `.claude/mcp/servers/` directory structure
2. Verify `sys.path.insert(0, ".claude")` at top of skill
3. Check for typos in server name (ct_gov_mcp vs ct-gov-mcp)
4. Verify MCP server file exists and has correct function exports

### Issue: Execution timeout (>60s)

**Symptoms**:
```
ERROR: Execution timeout (>60s)
```

**Solutions**:
1. Optimize query - reduce pageSize from 1000 to 100
2. Add pagination with smaller batches
3. Remove expensive operations (heavy processing)
4. Increase timeout in test_runner.py (line ~142)

### Issue: Zero results but query is valid

**Symptoms**:
```
FAILED: Query returned zero results
```

**Solutions**:
1. Expand search terms (less restrictive)
2. Broaden date range or remove date filters
3. Remove unnecessary filters
4. Verify data exists in source (try broader query manually)
5. Check for typos in search terms

### Issue: Schema validation fails

**Symptoms**:
```
FAILED: Output schema doesn't match expected format
Expected patterns: ['NCT', 'Phase']
Matched patterns: []
```

**Solutions**:
1. Check skill type inference (trials vs fda_drugs vs patents)
2. Review expected patterns for skill type
3. Ensure output includes standard field names
4. Add custom schema for non-standard skills

### Issue: Max iterations exceeded

**Symptoms**:
```
Exit code 2: Max iterations exceeded
```

**Solutions**:
1. Review repair instructions - are they clear enough?
2. Check if pharma-search-specialist understands the prompt
3. Manual intervention may be needed for complex issues
4. Increase max_iterations if repairs are working but slow

## Best Practices

### 1. Always Test After Creation

**Never skip testing new skills**:
```python
# ✓ Good
Create skill → Save → TEST → Update index

# ✗ Bad
Create skill → Save → Update index (no test!)
```

### 2. Test Before Reuse

**Verify health before execution**:
```python
# ✓ Good
Test skill → If healthy: execute, else: repair

# ✗ Bad
Execute skill directly (might be broken)
```

### 3. Batch Test Periodically

**Maintain library quality**:
```bash
# Weekly health check
python3 .claude/tools/testing/batch_test_skills.py --update-health
```

### 4. Use JSON Output for Automation

**Programmatic integration**:
```bash
# ✓ Good - parseable output
--json

# ✗ Bad - human-readable only
# (default text output)
```

### 5. Limit Iterations

**Prevent infinite loops**:
```python
# ✓ Good
max_iterations = 3  # Reasonable limit

# ✗ Bad
max_iterations = 10  # Too many, likely won't help
```

### 6. Prioritize Critical Fixes

**Fix in order of severity**:
1. CRITICAL: Syntax, imports (can't run without these)
2. HIGH: Execution, data (skill doesn't work)
3. MEDIUM: Schema (skill works but output inconsistent)
4. LOW: Style, formatting (cosmetic)

## Summary

The skill testing infrastructure provides:

✅ **Automated Testing** - 5-level validation (syntax → schema)
✅ **Intelligent Analysis** - Root cause detection + repair guidance
✅ **Agent Integration** - Seamless pharma-search-specialist invocation
✅ **Iterative Repair** - Retry until success (max 3 iterations)
✅ **Health Tracking** - Integration with skill discovery
✅ **Batch Operations** - Library-wide health scanning

**Result**: Self-healing skill library that autonomously maintains quality through closed-loop testing and repair.
