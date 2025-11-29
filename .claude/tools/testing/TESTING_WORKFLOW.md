# Skill Testing Workflow - Closing the Agentic Loop

## Overview

This testing infrastructure enables autonomous skill validation and self-healing through a closed-loop process:

1. **Test** skill execution
2. **Detect** failures automatically
3. **Analyze** root cause
4. **Repair** via pharma-search-specialist
5. **Verify** fix works
6. **Iterate** until success or max attempts

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Claude Code Main Agent                 │
│                                                      │
│  Orchestrates test → repair → verify loop           │
└─────────────────────────────────────────────────────┘
                         │
                         ├──────────────────┐
                         ▼                  ▼
              ┌──────────────────┐   ┌─────────────────┐
              │ Test Orchestrator│   │ pharma-search-  │
              │                  │   │   specialist    │
              │ - Runs tests     │   │                 │
              │ - Analyzes fails │   │ - Reads skill   │
              │ - Generates      │   │ - Fixes issues  │
              │   repair prompts │   │ - Returns code  │
              └──────────────────┘   └─────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Test Runner    │
              │                  │
              │ - Syntax test    │
              │ - Import test    │
              │ - Execution test │
              │ - Data test      │
              │ - Schema test    │
              └──────────────────┘
```

## Tools

### 1. test_runner.py

**Purpose**: Execute comprehensive tests on individual skills

**Tests performed**:
- ✅ **Syntax**: Python code compiles without errors
- ✅ **Import**: All dependencies available
- ✅ **Execution**: Skill runs without exceptions (60s timeout)
- ✅ **Data**: Query returns results (not zero)
- ✅ **Schema**: Output matches expected format for skill type

**Usage**:
```bash
# Test a skill
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/glp1-trials/scripts/get_glp1_trials.py

# Test with arguments
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py \
  --args "GLP-1" "obesity"

# JSON output
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/glp1-trials/scripts/get_glp1_trials.py \
  --json
```

**Exit codes**:
- 0: All tests passed
- 1: Some tests failed

**Output**:
```
============================================================
Test Report: get_glp1_trials
============================================================
Path: /path/to/get_glp1_trials.py
Overall Status: PASSED
Tests: 5/5 passed
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

### 2. test_orchestrator.py

**Purpose**: Orchestrate testing with intelligent failure analysis

**Capabilities**:
- Runs test_runner.py
- Analyzes test failures
- Generates detailed repair instructions
- Creates repair prompt for pharma-search-specialist
- Tracks iteration count

**Usage**:
```bash
# Run orchestration
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py

# Specify iteration
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py \
  --iteration 2 \
  --max-iterations 3

# JSON output
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py \
  --json
```

**Exit codes**:
- 0: All tests passed
- 1: Needs repair (iterations remaining)
- 2: Max iterations exceeded

**Output**:
```
============================================================
Test Orchestration Summary
============================================================
Skill: get_data
Path: .claude/skills/broken-skill/scripts/get_data.py
Iteration: 1/3
Status: FAILED
Tests: 2/5 passed
============================================================

REPAIR NEEDED: 3 issue(s) detected

1. [CRITICAL] import_error
   Import failed: No module named 'mcp.servers.ct_gov_mcp'

2. [HIGH] execution_error
   Execution failed with exit code 1

3. [MEDIUM] schema_validation_error
   Output schema doesn't match expected format

NEXT STEP: Invoke pharma-search-specialist with repair prompt

============================================================
AGENT REPAIR PROMPT
============================================================
SKILL REPAIR REQUEST (Iteration 1/3)

Skill: get_data
Path: .claude/skills/broken-skill/scripts/get_data.py
Test Status: failed
Tests: 2/5 passed

ISSUES DETECTED:

1. [CRITICAL] import_error
   Description: Import failed: No module named 'mcp.servers.ct_gov_mcp'
   Suggested Fix: Fix MCP import path. Ensure:
   1. Import uses correct path: `from mcp.servers.{server}_mcp import {function}`
   2. sys.path includes .claude directory: `sys.path.insert(0, ".claude")`
   3. MCP server exists in .claude/mcp/servers/

...
```

## Workflow for Claude Code Agent

### Pattern 1: Test Existing Skill

**User request**: "Test the GLP-1 trials skill"

**Agent workflow**:

```python
# Step 1: Run orchestrator
Bash("python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/glp1-trials/scripts/get_glp1_trials.py \
  --json")

# Step 2: Parse result
result = json.loads(bash_output)

# Step 3a: If passed - report success
if result['test_report']['overall_status'] == 'passed':
    print(f"✓ Skill {result['skill_name']} is healthy!")
    print(f"  Tests: {result['test_report']['passed_tests']}/{result['test_report']['total_tests']} passed")

# Step 3b: If failed - close the loop
elif result['needs_repair'] and result['iteration'] < result['max_iterations']:
    print(f"Skill {result['skill_name']} failed {result['test_report']['failed_tests']} tests.")
    print(f"Invoking pharma-search-specialist to repair...")

    # Invoke pharma-search-specialist with repair prompt
    Task(
        subagent_type='pharma-search-specialist',
        description='Repair failing skill',
        prompt=result['agent_prompt']
    )

    # Agent returns fixed code
    # Save fixed code
    Write(result['skill_path'], agent_response_code)

    # Re-test (iteration 2)
    Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
      {result['skill_path']} \
      --iteration 2 \
      --json")

    # Parse result again
    result2 = json.loads(bash_output)

    # If still failing, iterate again (up to max_iterations)
    while result2['needs_repair'] and result2['iteration'] < result2['max_iterations']:
        # Repeat repair cycle
        ...
```

### Pattern 2: Test All Skills

**User request**: "Test all skills in the library"

**Agent workflow**:

```python
# Step 1: Discover all skills
Bash("python3 .claude/tools/skill_discovery/index_query.py --json")
skills = json.loads(bash_output)['skills']

# Step 2: Test each skill
failed_skills = []
for skill in skills:
    script_path = f".claude/skills/{skill['folder']}/scripts/{skill['name']}.py"

    # Run orchestrator
    Bash(f"python3 .claude/tools/testing/test_orchestrator.py {script_path} --json")
    result = json.loads(bash_output)

    if result['needs_repair']:
        failed_skills.append(result)

# Step 3: Report summary
print(f"Tested {len(skills)} skills")
print(f"✓ {len(skills) - len(failed_skills)} passed")
print(f"✗ {len(failed_skills)} failed")

# Step 4: Repair failed skills (batch or sequential)
for failed in failed_skills:
    # Invoke repair workflow (Pattern 1, Step 3b)
    ...
```

### Pattern 3: Test After Creation

**User request**: "Create skill to get KRAS trials"

**Agent workflow**:

```python
# Step 1: Create skill via pharma-search-specialist
Task(
    subagent_type='pharma-search-specialist',
    prompt="Create skill to get KRAS inhibitor clinical trials"
)

# Step 2: Save skill code
Write(".claude/skills/kras-trials/SKILL.md", skill_md)
Write(".claude/skills/kras-trials/scripts/get_kras_trials.py", skill_code)

# Step 3: TEST IMMEDIATELY (close the loop)
Bash("python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/kras-trials/scripts/get_kras_trials.py \
  --json")

result = json.loads(bash_output)

# Step 4a: If passed - update index and report
if result['test_report']['overall_status'] == 'passed':
    Bash("python3 .claude/tools/skill_discovery/index_updater.py add ...")
    print(f"✓ Skill created and verified!")

# Step 4b: If failed - repair before finalizing
elif result['needs_repair']:
    print(f"Initial skill has issues. Repairing...")

    # Invoke pharma-search-specialist with repair prompt
    Task(
        subagent_type='pharma-search-specialist',
        prompt=result['agent_prompt']
    )

    # Save fixed code
    Write(result['skill_path'], agent_response_code)

    # Re-test
    Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
      {result['skill_path']} \
      --iteration 2 \
      --json")

    # Continue until verified or max iterations
```

## Test Case Definitions

### Test Cases by Skill Type

#### Clinical Trials Skills

**Example**: `get_glp1_trials.py`

**Expected**:
- ✅ Calls `ct_gov_mcp` search
- ✅ Parses markdown response
- ✅ Returns > 0 trials
- ✅ Output includes: NCT ID, Phase, Status, Sponsor
- ✅ Handles pagination (pageSize parameter)

**Common failures**:
- Markdown parsing breaks on unexpected format
- Pagination not implemented (truncated results)
- Query too restrictive (zero results)

#### FDA Drug Skills

**Example**: `get_glp1_fda_drugs.py`

**Expected**:
- ✅ Calls `fda_mcp` lookup
- ✅ Parses JSON response
- ✅ Returns > 0 drugs
- ✅ Output includes: Application, Product, Approval Date
- ✅ Uses `.get()` for safe field access

**Common failures**:
- KeyError from direct dict access
- Wrong search_type (label vs general)
- Missing field handling

#### Patent Skills

**Example**: `get_glp1_patents.py`

**Expected**:
- ✅ Calls `uspto_patents_mcp` search
- ✅ Returns > 0 patents
- ✅ Output includes: Patent #, Publication Date, Inventor, Assignee
- ✅ Handles large result sets

**Common failures**:
- Query syntax errors
- Pagination issues
- Missing assignee/inventor data

#### Publication Skills

**Example**: `get_glp1_publications.py`

**Expected**:
- ✅ Calls `pubmed_mcp` search
- ✅ Returns > 0 publications
- ✅ Output includes: PMID, Title, Authors, Journal
- ✅ Date filtering works correctly

**Common failures**:
- Query too narrow (zero results)
- Missing metadata fields
- Date format issues

#### Financial Skills

**Example**: `get_company_segment_financials.py`

**Expected**:
- ✅ Calls `sec_edgar_mcp` or `financials_mcp`
- ✅ Returns financial data
- ✅ Output includes: Revenue, Company, Segment
- ✅ Handles missing data gracefully

**Common failures**:
- Company ticker/CIK resolution
- Missing financial data (not all companies report segments)
- Type conversion errors (string vs number)

## Integration with Health Check

The testing system integrates with the health check system:

```python
# After testing, update skill health status
from skill_discovery.health_check import update_skill_health, HealthStatus

# If tests pass
if test_report.overall_status == 'passed':
    update_skill_health(skill_name, HealthStatus.HEALTHY, [])

# If tests fail
else:
    issues = [f"{t.test_type}: {t.message}" for t in test_report.tests if t.status == 'failed']
    update_skill_health(skill_name, HealthStatus.BROKEN, issues)
```

This enables:
- ✅ Strategy system knows which skills are broken
- ✅ Broken skills excluded from REUSE strategy
- ✅ Health status visible in index queries
- ✅ Tracking skill quality over time

## Best Practices

### 1. Test After Creation

**Always test new skills immediately**:
```python
# Create skill
Task(pharma-search-specialist, prompt)

# Save skill
Write(skill_path, code)

# TEST IMMEDIATELY
Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")
```

### 2. Test Before Reuse

**Verify skill health before execution**:
```python
# Before running skill
Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")

if result['test_report']['overall_status'] == 'passed':
    # Safe to run
    Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
else:
    # Repair first
    ...
```

### 3. Batch Testing

**Test all skills periodically**:
```bash
# Test all skills, generate health report
python3 .claude/tools/testing/batch_test_skills.py --update-health
```

### 4. CI/CD Integration

**Run tests on skill changes**:
- Pre-commit hook: Test modified skills
- PR validation: Test all skills
- Nightly: Full skill library validation

## Exit Codes Summary

All testing tools use consistent exit codes:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All tests passed | Skill is healthy, safe to use |
| 1 | Tests failed, repair available | Invoke repair workflow |
| 2 | Max iterations exceeded | Manual intervention needed |

## Troubleshooting

### Issue: Import errors persist after repair

**Solution**:
1. Check `.claude/mcp/servers/` structure
2. Verify sys.path configuration
3. Check for circular imports

### Issue: Execution timeout (>60s)

**Solution**:
1. Optimize query (reduce pageSize)
2. Add pagination with smaller batches
3. Increase timeout in test_runner.py

### Issue: Zero results but query is valid

**Solution**:
1. Expand search terms (less restrictive)
2. Broaden date range
3. Remove unnecessary filters
4. Verify data exists in source

### Issue: Schema validation fails unexpectedly

**Solution**:
1. Check skill type inference
2. Review expected patterns
3. Customize schema for non-standard skills

## Summary

The testing infrastructure closes the agentic loop through:

1. **Automated testing** - Comprehensive validation of all skill aspects
2. **Intelligent analysis** - Root cause detection and repair guidance
3. **Agent integration** - Seamless pharma-search-specialist invocation
4. **Iterative repair** - Retry until success or max attempts
5. **Health tracking** - Integration with skill discovery system

**Result**: Self-healing skill library with autonomous quality assurance.
