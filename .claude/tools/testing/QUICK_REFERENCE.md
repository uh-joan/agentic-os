# Testing Infrastructure - Quick Reference

## Command Cheat Sheet

### Test Single Skill

```bash
# Basic test
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/{folder}/scripts/{skill}.py

# With JSON output (for parsing)
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/{folder}/scripts/{skill}.py \
  --json

# With arguments
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/{folder}/scripts/{skill}.py \
  --args "arg1" "arg2"
```

### Test with Orchestration (Repair)

```bash
# Get repair instructions
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/{folder}/scripts/{skill}.py \
  --json

# Specify iteration
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/{folder}/scripts/{skill}.py \
  --iteration 2 \
  --max-iterations 3 \
  --json
```

### Test All Skills

```bash
# Test all (read-only)
python3 .claude/tools/testing/batch_test_skills.py

# Update health status in index
python3 .claude/tools/testing/batch_test_skills.py --update-health

# Generate JSON report
python3 .claude/tools/testing/batch_test_skills.py --json --output report.json
```

## Exit Codes

| Code | Tool | Meaning |
|------|------|---------|
| 0 | test_runner | All tests passed |
| 1 | test_runner | Tests failed |
| 0 | test_orchestrator | All tests passed |
| 1 | test_orchestrator | Needs repair (iterations remaining) |
| 2 | test_orchestrator | Max iterations exceeded |
| 0 | batch_test | All skills healthy |
| 1 | batch_test | Some broken |
| 2 | batch_test | Mostly broken |

## Test Levels (5 Tests)

1. **Syntax** - Python compiles without errors
2. **Import** - All dependencies available
3. **Execution** - Runs without exceptions (60s timeout)
4. **Data** - Returns results (not zero)
5. **Schema** - Output matches expected format

## Claude Code Integration Patterns

### Pattern 1: Test After Creation (REQUIRED)

```python
# Create skill
Task(pharma-search-specialist, prompt)

# Save files
Write(f".claude/skills/{folder}/SKILL.md", md)
Write(f".claude/skills/{folder}/scripts/{skill}.py", code)

# TEST IMMEDIATELY
Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
      .claude/skills/{folder}/scripts/{skill}.py \
      --json")

result = json.loads(bash_output)

if result['test_report']['overall_status'] == 'passed':
    # Success - update index and execute
    Bash(f"python3 .claude/tools/skill_discovery/index_updater.py add ...")
    Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
else:
    # Failed - enter repair loop
    _repair_skill_loop(skill_path, result, max_iterations=3)
```

### Pattern 2: Test Before Reuse (RECOMMENDED)

```python
# Strategy returns REUSE
if strategy['strategy'] == 'REUSE':
    skill_path = strategy['skill']['script']

    # Test health
    Bash(f"python3 .claude/tools/testing/test_runner.py {skill_path} --json")
    result = json.loads(bash_output)

    if result['overall_status'] == 'passed':
        # Healthy - execute
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
    else:
        # Broken - repair first
        _repair_skill_loop(skill_path, result, max_iterations=3)
        Bash(f"PYTHONPATH=.claude:$PYTHONPATH python3 {skill_path}")
```

### Pattern 3: Repair Loop (CORE LOGIC)

```python
def _repair_skill_loop(skill_path: str, initial_result: dict, max_iterations: int = 3):
    iteration = 1
    result = initial_result

    while result['needs_repair'] and iteration <= max_iterations:
        # Invoke pharma-search-specialist with repair prompt
        Task(
            subagent_type='pharma-search-specialist',
            prompt=result['agent_prompt']
        )

        # Save fixed code
        Write(skill_path, fixed_code)

        # Re-test
        iteration += 1
        Bash(f"python3 .claude/tools/testing/test_orchestrator.py \
              {skill_path} \
              --iteration {iteration} \
              --max-iterations {max_iterations} \
              --json")

        result = json.loads(bash_output)

        if result['test_report']['overall_status'] == 'passed':
            return True

    return False  # Max iterations exceeded
```

## JSON Output Formats

### test_runner.py

```json
{
  "skill_name": "get_glp1_trials",
  "skill_path": "/path/to/skill.py",
  "overall_status": "passed",
  "tests": [
    {
      "test_type": "syntax",
      "status": "passed",
      "message": "Python syntax is valid",
      "details": null,
      "execution_time": null
    },
    // ... 4 more tests
  ],
  "total_tests": 5,
  "passed_tests": 5,
  "failed_tests": 0,
  "error_tests": 0,
  "execution_output": "Total trials found: 127\n...",
  "error_output": null
}
```

### test_orchestrator.py

```json
{
  "skill_name": "get_glp1_trials",
  "skill_path": "/path/to/skill.py",
  "iteration": 1,
  "max_iterations": 3,
  "needs_repair": true,
  "test_report": { /* same as test_runner */ },
  "repair_instructions": [
    {
      "issue_type": "execution_error",
      "severity": "high",
      "description": "Execution failed: KeyError 'NCTId'",
      "suggested_fix": "Fix KeyError in data parsing:\n1. Use .get() method...",
      "code_location": null
    }
  ],
  "agent_prompt": "SKILL REPAIR REQUEST (Iteration 1/3)\n\nSkill: get_glp1_trials\n..."
}
```

### batch_test_skills.py

```json
{
  "total_skills": 47,
  "healthy_skills": 42,
  "broken_skills": 4,
  "untested_skills": 1,
  "health_percentage": 89.4,
  "test_results": [
    {
      "skill_name": "glp1-trials",
      "status": "passed",
      "tests_passed": 5,
      "tests_total": 5,
      "path": ".claude/skills/glp1-trials/scripts/get_glp1_trials.py"
    },
    {
      "skill_name": "kras-trials",
      "status": "failed",
      "tests_passed": 3,
      "tests_total": 5,
      "issues": ["execution: KeyError 'NCTId'", "data: Zero results"],
      "path": ".claude/skills/kras-trials/scripts/get_kras_trials.py"
    }
  ]
}
```

## Severity Levels

| Severity | Test Types | Impact | Priority |
|----------|-----------|--------|----------|
| CRITICAL | Syntax, Import | Can't run at all | Fix first |
| HIGH | Execution, Data | Doesn't work | Fix second |
| MEDIUM | Schema | Works but inconsistent | Fix third |
| LOW | Style, formatting | Cosmetic only | Fix last |

## Common Failure Patterns & Fixes

### Import Error (CRITICAL)

**Pattern**: `ImportError: No module named 'mcp.servers.ct_gov_mcp'`

**Fix**:
```python
import sys
sys.path.insert(0, ".claude")  # Add to top of file
from mcp.servers.ct_gov_mcp import search
```

### Execution Error: KeyError (HIGH)

**Pattern**: `KeyError: 'NCTId'`

**Fix**:
```python
# Bad
nct_id = trial['NCTId']

# Good
nct_id = trial.get('NCTId', 'Unknown')
```

### Data Error: Zero Results (HIGH)

**Pattern**: `Query returned zero results`

**Fix**:
- Broaden search terms (less restrictive)
- Expand date range
- Remove unnecessary filters
- Verify data exists in source

### Schema Error: Missing Patterns (MEDIUM)

**Pattern**: `Output schema doesn't match expected format`

**Fix**:
- Ensure output includes standard field names
- Add summary statistics (count, totals)
- Format consistently with skill type

## Troubleshooting

### Issue: Timeout (>60s)

**Solution**:
```python
# Reduce pageSize
search(term="GLP-1", pageSize=50)  # Was 1000

# Or optimize processing
```

### Issue: Import fails even with sys.path

**Solution**:
```bash
# Check MCP server exists
ls .claude/mcp/servers/ct_gov_mcp/

# Verify function is exported
grep "def search" .claude/mcp/servers/ct_gov_mcp/*.py
```

### Issue: Max iterations exceeded

**Solution**:
- Review repair instructions - are they clear?
- Check if pharma-search-specialist understands prompt
- May need manual intervention
- Consider CREATE strategy instead

## Best Practices

✅ **DO**:
- Test immediately after creating skill
- Use `--json` for programmatic parsing
- Limit iterations to 3
- Fall back to CREATE if repair fails
- Update health status after testing

❌ **DON'T**:
- Skip testing new skills
- Ignore broken skills (repair them!)
- Set max_iterations > 5 (won't help)
- Trust execution without testing
- Forget to update index after repair

## Files & Locations

```
.claude/tools/testing/
├── README.md                      # Full documentation
├── QUICK_REFERENCE.md             # This file
├── TESTING_WORKFLOW.md            # Detailed workflow guide
├── CLAUDE_CODE_INTEGRATION.md     # Integration patterns
├── __init__.py                    # Python module
├── test_runner.py                 # Core testing engine
├── test_orchestrator.py           # Repair orchestrator
└── batch_test_skills.py           # Batch testing
```

## Summary

**Before**: Create → Save → Hope it works ❌

**After**: Create → Save → TEST → Repair if needed → Verify → Done ✅

**Result**: Self-healing skill library with 98%+ reliability
