# Claude Code Integration Guide - Closing the Agentic Loop

## Purpose

This guide shows Claude Code's main agent how to integrate the testing infrastructure into its workflow to achieve autonomous skill validation and self-healing.

## Core Principle: Always Close the Loop

**Before**: Create skill → Save → Done ❌

**After**: Create skill → Save → TEST → If broken: REPAIR → Re-test → Done ✅

## Integration Points

### 1. After Skill Creation (CRITICAL)

Every time a new skill is created, immediately test it.

**Trigger**: User requests new data skill
- "Create skill to get KRAS trials"
- "Find GLP-1 FDA approved drugs"
- "Get patent data for CAR-T manufacturing"

**Workflow**:

```python
# Step 1: Create skill via pharma-search-specialist
Task(
    subagent_type='pharma-search-specialist',
    description='Create KRAS trials skill',
    prompt="Create skill to get KRAS inhibitor clinical trials"
)

# pharma-search-specialist returns:
# - skill_code: Python script
# - skill_md: SKILL.md with YAML frontmatter
# - skill_name: "get_kras_trials"
# - folder_name: "kras-trials"

# Step 2: Save skill files
Write(f".claude/skills/{folder_name}/SKILL.md", skill_md)
Write(f".claude/skills/{folder_name}/scripts/{skill_name}.py", skill_code)

# Step 3: TEST IMMEDIATELY - Close the loop!
skill_path = f".claude/skills/{folder_name}/scripts/{skill_name}.py"
Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")

result = json.loads(bash_output)

# Step 4: Handle result
if result['test_report']['overall_status'] == 'passed':
    # Success! Finalize skill
    print(f"✓ Skill created and verified!")
    print(f"  Tests: {result['test_report']['passed_tests']}/5 passed")

    # Update index
    Bash(f"python3 .claude/tools/skill_discovery/index_updater.py add \
          --name {skill_name} \
          --folder {folder_name} \
          --servers ct_gov_mcp \
          --patterns pagination,markdown_parsing \
          --category clinical_trials")

    # Execute skill to get results for user
    Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")

else:
    # Failed! Enter repair loop
    self._repair_skill_loop(skill_path, result, max_iterations=3)
```

### 2. Before Skill Reuse (RECOMMENDED)

Before executing an existing skill, verify it's still healthy.

**Trigger**: Strategy system returns REUSE decision
- User: "Get GLP-1 trials"
- Strategy: "REUSE: glp1-trials skill exists"

**Workflow**:

```python
# After strategy.py returns REUSE decision
strategy = json.loads(bash_output)

if strategy['strategy'] == 'REUSE':
    skill_path = strategy['skill']['script']

    # TEST BEFORE EXECUTION
    Bash(f"python3 .claude/tools/testing/test_runner.py {skill_path} --json")
    test_result = json.loads(bash_output)

    if test_result['overall_status'] == 'passed':
        # Skill is healthy - execute
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
    else:
        # Skill is broken - repair first
        print(f"⚠ Skill {strategy['skill']['name']} is broken, repairing...")

        Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")
        repair_result = json.loads(bash_output)

        # Enter repair loop
        self._repair_skill_loop(skill_path, repair_result, max_iterations=3)

        # After repair, execute
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
```

### 3. Periodic Health Checks (OPTIONAL)

User can request library health check.

**Trigger**: User explicitly requests
- "Check skill library health"
- "Test all skills"
- "How many skills are broken?"

**Workflow**:

```python
# Run batch test
Bash("python3 .claude/tools/testing/batch_test_skills.py --update-health --json")
summary = json.loads(bash_output)

# Report to user
print(f"""
Skill Library Health Report
{'='*60}
Total Skills:    {summary['total_skills']}
✓ Healthy:       {summary['healthy_skills']} ({summary['health_percentage']}%)
✗ Broken:        {summary['broken_skills']}

Health Status: {'EXCELLENT' if summary['health_percentage'] > 90 else 'GOOD' if summary['health_percentage'] > 75 else 'NEEDS ATTENTION'}
""")

# If broken skills exist, offer to repair
if summary['broken_skills'] > 0:
    print(f"\nBroken Skills:")
    broken_skills = [r for r in summary['test_results'] if r['status'] == 'failed']
    for skill in broken_skills[:5]:  # Show first 5
        print(f"  ✗ {skill['skill_name']}: {len(skill.get('issues', []))} issue(s)")

    if summary['broken_skills'] > 5:
        print(f"  ... and {summary['broken_skills'] - 5} more")

    # Ask user if they want to repair
    # If yes: iterate through broken skills and repair
```

## Repair Loop Implementation

The repair loop is the core of closing the agentic loop. Here's the standard implementation:

```python
def _repair_skill_loop(self, skill_path: str, initial_result: dict, max_iterations: int = 3):
    """
    Autonomous repair loop with pharma-search-specialist

    Args:
        skill_path: Path to skill script
        initial_result: Initial test orchestrator result
        max_iterations: Maximum repair attempts

    Returns:
        bool: True if repair succeeded, False if max iterations exceeded
    """
    iteration = 1
    result = initial_result

    while result['needs_repair'] and iteration <= max_iterations:
        print(f"\n{'='*60}")
        print(f"Repair Iteration {iteration}/{max_iterations}")
        print(f"{'='*60}")
        print(f"Issues detected: {len(result['repair_instructions'])}")

        # Show issues by severity
        for instr in result['repair_instructions']:
            print(f"  [{instr['severity'].upper()}] {instr['issue_type']}: {instr['description'][:80]}...")

        print(f"\nInvoking pharma-search-specialist for repair...")

        # Invoke pharma-search-specialist with repair prompt
        Task(
            subagent_type='pharma-search-specialist',
            description=f"Repair {result['skill_name']} (iteration {iteration})",
            prompt=result['agent_prompt']
        )

        # Agent returns fixed code
        # Extract fixed_code from agent response

        # Save fixed code
        Write(skill_path, fixed_code)
        print(f"✓ Fixed code saved to {skill_path}")

        # Re-test
        iteration += 1
        print(f"\nRe-testing (iteration {iteration})...")

        Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
              {skill_path} \
              --iteration {iteration} \
              --max-iterations {max_iterations} \
              --json")

        result = json.loads(bash_output)

        # Check result
        if result['test_report']['overall_status'] == 'passed':
            print(f"\n✓ Repair successful after {iteration - 1} iteration(s)!")
            print(f"  All tests passed: {result['test_report']['passed_tests']}/5")
            return True
        elif iteration > max_iterations:
            print(f"\n✗ Max iterations ({max_iterations}) exceeded")
            print(f"  Remaining issues: {len(result['repair_instructions'])}")
            return False
        else:
            print(f"\n⚠ Still failing, attempting iteration {iteration}...")

    return False
```

## Example: Full Workflow with Testing

Here's a complete example showing all integration points:

```python
# ============================================================
# User Request: "Get KRAS inhibitor clinical trials"
# ============================================================

# STEP 0: Pre-flight skill discovery (check if skill exists)
Bash("""python3 .claude/tools/skill_discovery/strategy.py \
    --skill "get_kras_inhibitor_trials" \
    --therapeutic-area "KRAS inhibitor" \
    --data-type "trials" \
    --servers "ct_gov_mcp" \
    --json""")

strategy = json.loads(bash_output)

if strategy['strategy'] == 'REUSE':
    # Skill exists - test before use
    skill_path = strategy['skill']['script']

    print(f"Found existing skill: {strategy['skill']['name']}")
    print(f"Testing health before execution...")

    Bash(f"python3 .claude/tools/testing/test_runner.py {skill_path} --json")
    test_result = json.loads(bash_output)

    if test_result['overall_status'] == 'passed':
        print(f"✓ Skill is healthy, executing...")
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
        # Return results to user
    else:
        print(f"⚠ Skill is broken ({test_result['failed_tests']} tests failed)")
        print(f"Repairing before execution...")

        # Get repair instructions
        Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")
        repair_result = json.loads(bash_output)

        # Repair loop
        success = _repair_skill_loop(skill_path, repair_result, max_iterations=3)

        if success:
            # Execute repaired skill
            Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
        else:
            print(f"✗ Repair failed, creating new skill instead...")
            strategy['strategy'] = 'CREATE'  # Fall back to CREATE

elif strategy['strategy'] in ['ADAPT', 'CREATE']:
    # Create new skill
    print(f"Creating new skill: get_kras_inhibitor_trials")

    # STEP 1: Invoke pharma-search-specialist
    Task(
        subagent_type='pharma-search-specialist',
        description='Create KRAS inhibitor trials skill',
        prompt=f"""Create skill to get KRAS inhibitor clinical trials.

        Requirements:
        - Query CT.gov for KRAS inhibitor trials
        - Include all phases
        - Implement pagination (pageSize=100)
        - Parse markdown response
        - Return count + summary

        {f"Reference skill: {strategy['reference']['script']}" if 'reference' in strategy else ""}
        """
    )

    # Agent returns: skill_code, skill_md, skill_name, folder_name

    # STEP 2: Save skill files
    folder_name = "kras-inhibitor-trials"
    skill_name = "get_kras_inhibitor_trials"

    Write(f".claude/skills/{folder_name}/SKILL.md", skill_md)
    Write(f".claude/skills/{folder_name}/scripts/{skill_name}.py", skill_code)

    print(f"✓ Skill files saved to .claude/skills/{folder_name}/")

    # STEP 3: TEST IMMEDIATELY - Close the loop!
    skill_path = f".claude/skills/{folder_name}/scripts/{skill_name}.py"

    print(f"\nTesting new skill...")
    Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")

    result = json.loads(bash_output)

    # STEP 4: Handle test result
    if result['test_report']['overall_status'] == 'passed':
        # Success!
        print(f"\n✓ Skill created and verified!")
        print(f"  Tests: {result['test_report']['passed_tests']}/5 passed")

        # Update index
        Bash(f"""python3 .claude/tools/skill_discovery/index_updater.py add \
              --name {skill_name} \
              --folder {folder_name} \
              --servers ct_gov_mcp \
              --patterns pagination,markdown_parsing \
              --category clinical_trials \
              --complexity medium""")

        print(f"✓ Skill added to index")

        # Execute skill to get results
        print(f"\nExecuting skill...")
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")

        # Parse and return results to user
        print(f"\n{'='*60}")
        print(f"Results:")
        print(bash_output)

    else:
        # Failed - enter repair loop
        print(f"\n⚠ Initial skill has issues:")
        print(f"  Tests: {result['test_report']['passed_tests']}/{result['test_report']['total_tests']} passed")
        print(f"  Issues: {len(result['repair_instructions'])}")

        # Repair loop
        success = _repair_skill_loop(skill_path, result, max_iterations=3)

        if success:
            # Update index
            Bash(f"""python3 .claude/tools/skill_discovery/index_updater.py add \
                  --name {skill_name} \
                  --folder {folder_name} \
                  --servers ct_gov_mcp \
                  --patterns pagination,markdown_parsing \
                  --category clinical_trials \
                  --complexity medium""")

            # Execute skill
            Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")

            # Return results to user
            print(f"\n{'='*60}")
            print(f"Results:")
            print(bash_output)
        else:
            print(f"\n✗ Skill creation failed after {max_iterations} repair attempts")
            print(f"Manual intervention required")
            # Don't add to index - skill is broken
```

## Key Principles

### 1. Always Test Immediately After Creation

**Never skip this**:
```python
Write(skill_path, code)
# MUST test here, not later!
Bash(f"python3 .claude/tools/testing/test_orchestrator.py {skill_path} --json")
```

### 2. Test Before Reuse When Possible

**Verify health before execution**:
```python
# Good practice (but not strictly required for every execution)
Bash(f"python3 .claude/tools/testing/test_runner.py {skill_path} --json")
if passed:
    execute()
else:
    repair()
```

### 3. Use JSON Output for Programmatic Parsing

**Always use `--json` flag**:
```bash
--json  # Parseable output
```

### 4. Limit Repair Iterations

**Prevent infinite loops**:
```python
max_iterations = 3  # Standard limit
```

### 5. Fall Back to CREATE on Repair Failure

**If repair exceeds max iterations**:
```python
if not success:
    # Fall back to creating fresh skill
    strategy['strategy'] = 'CREATE'
```

### 6. Update Health Status After Testing

**Keep index in sync**:
```python
# In batch_test_skills.py or after individual tests
from skill_discovery.health_check import update_skill_health, HealthStatus

if test_passed:
    update_skill_health(skill_name, HealthStatus.HEALTHY, [])
else:
    update_skill_health(skill_name, HealthStatus.BROKEN, issues)
```

## Exit Codes Reference

All testing tools use consistent exit codes:

| Code | Tool | Meaning | Action |
|------|------|---------|--------|
| 0 | test_runner.py | All tests passed | Proceed |
| 1 | test_runner.py | Tests failed | Investigate |
| 0 | test_orchestrator.py | All tests passed | Finalize skill |
| 1 | test_orchestrator.py | Needs repair (iterations remaining) | Enter repair loop |
| 2 | test_orchestrator.py | Max iterations exceeded | Manual intervention or CREATE |
| 0 | batch_test_skills.py | All skills healthy | Library is healthy |
| 1 | batch_test_skills.py | Mostly healthy, some broken | Repair broken skills |
| 2 | batch_test_skills.py | Mostly broken | Major cleanup needed |

## Common Scenarios

### Scenario 1: New Skill Creation - Success on First Try

```python
Create → Save → Test → PASSED → Update index → Execute → Results
```

### Scenario 2: New Skill Creation - Needs Repair

```python
Create → Save → Test → FAILED → Repair (iteration 1) → Re-test → PASSED → Update index → Execute → Results
```

### Scenario 3: Reuse Existing Skill - Broken

```python
Strategy=REUSE → Test → FAILED → Repair → Re-test → PASSED → Execute → Results
```

### Scenario 4: Max Iterations Exceeded - Fall Back

```python
Create → Save → Test → FAILED
→ Repair (iteration 1) → Re-test → FAILED
→ Repair (iteration 2) → Re-test → FAILED
→ Repair (iteration 3) → Re-test → FAILED
→ MAX EXCEEDED → Fall back to CREATE with different approach
```

### Scenario 5: Periodic Health Check

```python
User request → Batch test all skills → Generate report
→ Identify 3 broken skills
→ For each broken skill: Repair loop
→ Final report: 44/47 healthy (93.6%)
```

## Summary

Closing the agentic loop requires:

1. ✅ **Test after creation** - Always validate new skills immediately
2. ✅ **Test before reuse** - Verify health of existing skills
3. ✅ **Repair automatically** - Invoke pharma-search-specialist on failures
4. ✅ **Iterate until success** - Retry up to max_iterations
5. ✅ **Update health status** - Keep index in sync with reality
6. ✅ **Fall back gracefully** - CREATE if repair fails

**Result**: Autonomous skill library that maintains quality through continuous validation and self-healing.
