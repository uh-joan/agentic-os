# MCP Comprehensive Test Strategy

## Test Objectives

1. **Validate MCP connectivity** - Ensure all 12 MCPs are accessible
2. **Verify method signatures** - Confirm all documented methods exist and work
3. **Test parameter handling** - Validate required/optional parameters
4. **Validate response formats** - Ensure responses match documented structures
5. **Discover edge cases** - Find quirks, limitations, error conditions
6. **Identify stub enhancements** - Document learnings to improve Python stubs

## Test Levels

### Level 1: Smoke Tests (Quick validation)
- Single method call per MCP
- Minimal parameters
- Basic response validation
- **Goal**: Confirm MCP is alive and responding

### Level 2: Method Coverage Tests
- All methods per MCP
- Standard parameters
- Response structure validation
- **Goal**: Verify all documented methods work

### Level 3: Parameter Variation Tests
- Required vs optional parameters
- Edge case values (empty, max, special chars)
- Parameter combinations
- **Goal**: Discover parameter quirks

### Level 4: Response Analysis Tests
- Detailed response inspection
- Field availability checks
- Data type validation
- **Goal**: Enhance stub documentation

### Level 5: Error Handling Tests
- Invalid parameters
- Missing required fields
- Rate limiting behavior
- **Goal**: Document error patterns

## Test Structure

```
scripts/mcp/tests/
├── TEST_STRATEGY.md          # This file
├── test_runner.py             # Main test orchestrator
├── test_results/              # Test output directory
│   ├── {timestamp}_summary.md
│   ├── {timestamp}_detailed.json
│   └── {timestamp}_learnings.md
├── test_suites/
│   ├── test_fda_mcp.py
│   ├── test_ct_gov_mcp.py
│   ├── test_pubmed_mcp.py
│   ├── test_opentargets_mcp.py
│   ├── test_pubchem_mcp.py
│   ├── test_datacommons_mcp.py
│   ├── test_sec_edgar_mcp.py
│   ├── test_uspto_patents_mcp.py
│   ├── test_nlm_codes_mcp.py
│   ├── test_who_mcp.py
│   ├── test_healthcare_mcp.py
│   └── test_financials_mcp.py
└── utils/
    ├── mcp_client.py          # MCP connection utilities
    ├── validators.py          # Response validators
    └── reporters.py           # Test result reporters
```

## Test Execution Strategy

### Phase 1: Smoke Tests (5-10 minutes)
Run one test per MCP to validate basic connectivity.

### Phase 2: Full Method Coverage (30-60 minutes)
Test all methods with standard parameters.

### Phase 3: Deep Dive (2-4 hours)
Parameter variations, edge cases, error handling.

### Phase 4: Analysis & Enhancement (1-2 hours)
Review results, document learnings, enhance stubs.

## Expected Learnings

### Documentation Enhancements
- Missing parameters discovered during testing
- Undocumented response fields
- Additional quirks and edge cases
- Better example queries

### Stub Improvements
- Additional helper functions
- Better parameter validation
- Enhanced error messages
- More comprehensive examples

### Tool Guide Updates
- Correction of outdated information
- New best practices
- Performance optimization tips
- Common pitfall warnings

## Success Criteria

✅ All 12 MCPs respond successfully
✅ All documented methods are callable
✅ Response structures match documentation
✅ At least 5 learnings per MCP documented
✅ Stubs enhanced based on test findings

## Test Data Strategy

### Test Queries by Domain

**Pharma/Biotech:**
- Drug: "semaglutide", "GLP-1"
- Condition: "diabetes", "obesity"
- Gene: "BRCA1", "TP53"
- Company: "Novo Nordisk", "Pfizer"

**Financial:**
- Stock: "AAPL", "TSLA"
- Economic: "GDP", "unemployment"
- Country: "USA", "China"

**Geographic:**
- US: "California, USA", "New York City, USA"
- International: "Paris, France", "Tokyo, Japan"

**Medical Coding:**
- ICD-10: "E11" (diabetes), "I10" (hypertension)
- HCPCS: "99213" (office visit), "27447" (knee replacement)
- NPI: "1234567890"

## Risk Mitigation

### Rate Limiting
- Add delays between tests (1-2 seconds)
- Respect API limits (FDA, FRED, etc.)
- Use test mode where available

### Data Sensitivity
- No PII in test queries
- Public data only
- Respect terms of service

### Error Recovery
- Continue on individual test failures
- Log all errors for analysis
- Provide partial results if needed

## Output Format

### Summary Report (Markdown)
```markdown
# MCP Test Results - {timestamp}

## Overall Status
- ✅ Passed: 45/50 tests
- ⚠️  Warnings: 3/50 tests
- ❌ Failed: 2/50 tests

## By MCP Server
| MCP | Tests | Passed | Failed | Learnings |
|-----|-------|--------|--------|-----------|
| FDA | 5 | 5 | 0 | 3 |
...
```

### Detailed Results (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "total_tests": 50,
  "passed": 45,
  "failed": 2,
  "warnings": 3,
  "mcps": {
    "fda-mcp": {
      "tests": [...],
      "learnings": [...]
    }
  }
}
```

### Learnings Report (Markdown)
```markdown
# MCP Test Learnings - {timestamp}

## FDA MCP
### Learning 1: Count parameter critical
- **Discovery**: Without count parameter, response exceeds 25k tokens
- **Impact**: Query fails silently
- **Stub Enhancement**: Add validation for count parameter
...
```
