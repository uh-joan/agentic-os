# MCP Testing Approach

## Challenge

The Python API stubs in `scripts/mcp/servers/` call `get_client()` from the MCP SDK, which requires:
1. MCP servers to be running
2. Claude Code's MCP integration layer
3. Proper authentication and configuration

These stubs are designed to be called **within Claude Code's execution environment** where the MCP SDK is available.

## Solution: Interactive Testing via Claude Code

Instead of automated unit tests that mock MCP responses, we'll use **interactive testing** where Claude Code actually calls the MCP tools and validates their behavior.

### Testing Workflow

1. **Test Suite Prompts**: For each MCP, create a test suite prompt that Claude Code can execute
2. **Claude Code Executes**: Claude Code calls the actual MCP tools
3. **Validation & Learning**: Claude Code validates responses and documents learnings
4. **Stub Enhancement**: Based on learnings, Claude Code updates the Python stubs

### Example Test Execution

```python
# Claude Code executes this in its environment
from fda_mcp import lookup_drug

# Test 1: With count parameter (token-efficient)
result_with_count = lookup_drug(
    search_term="semaglutide",
    search_type="general",
    count="openfda.brand_name.exact"
)

# Validate: Response should be small (<5k tokens)
# Learning: Count parameter reduces 67k→400 tokens

# Test 2: Without count parameter (demonstrates problem)
result_without_count = lookup_drug(
    search_term="aspirin",
    search_type="general",
    limit=5
)

# Validate: Response may exceed token limits
# Learning: WITHOUT count, responses can hit 25k MCP limit
```

### Test Suite Structure

```
scripts/mcp/tests/
├── TESTING_README.md               # This file
├── TEST_STRATEGY.md                 # Overall strategy
├── interactive_tests/
│   ├── test_fda_interactive.md      # FDA test script for Claude Code
│   ├── test_ct_gov_interactive.md   # CT.gov test script
│   ├── test_pubmed_interactive.md   # PubMed test script
│   └── ...                          # One per MCP
└── test_results/
    ├── fda_test_results.md          # Results + learnings
    ├── fda_stub_enhancements.md     # Stub updates based on learnings
    └── ...
```

### Interactive Test Format

Each `test_*_interactive.md` file contains:

1. **Test scenarios** - What to test
2. **Expected behavior** - What should happen
3. **Validation criteria** - How to verify
4. **Learning template** - What to document
5. **Enhancement checklist** - Potential stub improvements

### Running Tests

User says: "Run FDA MCP tests"

Claude Code:
1. Reads `interactive_tests/test_fda_interactive.md`
2. Executes each test scenario by calling actual MCP tools
3. Validates responses against criteria
4. Documents learnings in `test_results/fda_test_results.md`
5. Identifies stub enhancements needed
6. Updates `fda_mcp/__init__.py` if improvements identified
7. Documents enhancements in `test_results/fda_stub_enhancements.md`

## Benefits of Interactive Testing

✅ **Real MCP calls**: Tests actual behavior, not mocks
✅ **Token measurement**: Can measure actual response sizes
✅ **Discovery-focused**: Finds quirks and edge cases
✅ **Immediate enhancement**: Can update stubs right away
✅ **Documentation**: Produces both learnings and stub improvements

## Automated vs Interactive

| Aspect | Automated Tests | Interactive Tests |
|--------|-----------------|-------------------|
| Execution | Run automatically | Claude Code executes |
| MCP Connection | Requires mocking | Uses real MCPs |
| Token Efficiency | Can't measure | Measures actual tokens |
| Learning | Limited to assertions | Open-ended discovery |
| Enhancement | Manual process | Immediate stub updates |
| Best For | Regression testing | Initial validation & learning |

## Next Steps

Convert the test infrastructure to interactive test scripts:

1. Keep TEST_STRATEGY.md (test levels, domains, criteria)
2. Keep utils/validators.py (validation logic)
3. Keep utils/reporters.py (result formatting)
4. **Replace** automated test suites with interactive test scripts
5. Create template for interactive test execution
