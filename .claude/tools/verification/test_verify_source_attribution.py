#!/usr/bin/env python3
"""
Test suite for verify_source_attribution.py

Tests various scenarios to ensure the verification tool works correctly.
"""

import json
import sys
from pathlib import Path
from verify_source_attribution import SourceAttributionValidator


def test_skill_validation():
    """Test skill validation scenarios."""
    print("=== Testing Skill Validation ===\n")

    validator = SourceAttributionValidator()
    passed = 0
    failed = 0

    # Test 1: Missing source_metadata
    print("Test 1: Missing source_metadata...")
    result = validator.validate_skill_output(json.dumps({
        "drugs": [],
        "total_count": 0
    }))
    if not result['valid'] and 'source_metadata' in str(result['errors']):
        print("  ✅ PASS: Correctly detected missing source_metadata")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected missing source_metadata")
        failed += 1

    # Test 2: Complete valid source_metadata
    print("\nTest 2: Complete valid source_metadata...")
    valid_output = {
        "data": {"drugs": [], "total_count": 0},
        "source_metadata": {
            "source": "FDA Drug Database",
            "mcp_server": "fda_mcp",
            "query_date": "2025-12-03",
            "query_params": {"search_term": "test"},
            "data_count": 0,
            "data_type": "fda_approved_drugs"
        },
        "summary": "Found 0 drugs (source: FDA Drug Database, 2025-12-03)"
    }
    result = validator.validate_skill_output(json.dumps(valid_output))
    if result['valid']:
        print("  ✅ PASS: Accepted valid source_metadata")
        passed += 1
    else:
        print(f"  ❌ FAIL: Should have accepted valid source_metadata")
        print(f"     Errors: {result['errors']}")
        failed += 1

    # Test 3: Missing required fields
    print("\nTest 3: Missing required fields...")
    incomplete_output = {
        "data": {},
        "source_metadata": {
            "source": "FDA Drug Database",
            "mcp_server": "fda_mcp"
            # Missing: query_date, query_params, data_count, data_type
        },
        "summary": "Test"
    }
    result = validator.validate_skill_output(json.dumps(incomplete_output))
    if not result['valid'] and 'Missing required' in str(result['errors']):
        print("  ✅ PASS: Correctly detected missing fields")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected missing fields")
        failed += 1

    # Test 4: Invalid date format
    print("\nTest 4: Invalid date format...")
    invalid_date = valid_output.copy()
    invalid_date['source_metadata']['query_date'] = "12/03/2025"  # Wrong format
    result = validator.validate_skill_output(json.dumps(invalid_date))
    if not result['valid'] and 'date format' in str(result['errors']).lower():
        print("  ✅ PASS: Correctly detected invalid date format")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected invalid date format")
        failed += 1

    # Test 5: Unrecognized MCP server
    print("\nTest 5: Unrecognized MCP server...")
    invalid_server = valid_output.copy()
    invalid_server['source_metadata']['mcp_server'] = "unknown_mcp"
    result = validator.validate_skill_output(json.dumps(invalid_server))
    if 'Unrecognized mcp_server' in str(result['warnings']):
        print("  ✅ PASS: Warning for unrecognized MCP server")
        passed += 1
    else:
        print("  ❌ FAIL: Should have warned about unrecognized MCP server")
        failed += 1

    # Test 6: data_count not integer
    print("\nTest 6: data_count not integer...")
    invalid_count = valid_output.copy()
    invalid_count['source_metadata']['data_count'] = "10"  # String instead of int
    result = validator.validate_skill_output(json.dumps(invalid_count))
    if not result['valid'] and 'data_count must be integer' in str(result['errors']):
        print("  ✅ PASS: Correctly detected non-integer data_count")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected non-integer data_count")
        failed += 1

    # Test 7: Summary missing source citation
    print("\nTest 7: Summary missing source citation...")
    no_source_summary = valid_output.copy()
    no_source_summary['summary'] = "Found 0 drugs"  # No source mention
    result = validator.validate_skill_output(json.dumps(no_source_summary))
    if "doesn't include 'source:'" in str(result['warnings']):
        print("  ✅ PASS: Warning for missing source in summary")
        passed += 1
    else:
        print("  ❌ FAIL: Should have warned about missing source in summary")
        failed += 1

    print(f"\n{'='*50}")
    print(f"Skill Validation Tests: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")

    return failed == 0


def test_report_validation():
    """Test report validation scenarios."""
    print("=== Testing Report Validation ===\n")

    # Create test report files
    test_dir = Path("/tmp/test_reports")
    test_dir.mkdir(exist_ok=True)

    validator = SourceAttributionValidator()
    passed = 0
    failed = 0

    # Test 1: Missing frontmatter
    print("Test 1: Missing frontmatter...")
    no_frontmatter = test_dir / "no_frontmatter.md"
    no_frontmatter.write_text("# Report\n\nSome content")
    result = validator.validate_report_file(no_frontmatter)
    if not result['valid'] and 'frontmatter' in str(result['errors']).lower():
        print("  ✅ PASS: Correctly detected missing frontmatter")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected missing frontmatter")
        failed += 1

    # Test 2: Missing data_sources_mcp_verified
    print("\nTest 2: Missing data_sources_mcp_verified...")
    no_mcp_sources = test_dir / "no_mcp_sources.md"
    no_mcp_sources.write_text("""---
title: Test Report
date: 2025-12-03
---

# Report

Content here.
""")
    result = validator.validate_report_file(no_mcp_sources)
    if not result['valid'] and 'data_sources_mcp_verified' in str(result['errors']):
        print("  ✅ PASS: Correctly detected missing data_sources_mcp_verified")
        passed += 1
    else:
        print("  ❌ FAIL: Should have detected missing data_sources_mcp_verified")
        failed += 1

    # Test 3: Complete valid report
    print("\nTest 3: Complete valid report...")
    valid_report = test_dir / "valid_report.md"
    valid_report.write_text("""---
title: Test Report
date: 2025-12-03

data_sources_mcp_verified:
  - test_skill: 100 trials (source: ClinicalTrials.gov, date: 2025-12-03)

data_sources_internal_knowledge:
  - Market estimates [from industry consensus]

source_validation:
  mcp_verified_claims: 50
  analytical_insights: 20
  internal_knowledge: 5
---

# Test Report

This is a properly cited report with many citations.

Phase 3 trials are recruiting (source: ClinicalTrials.gov, 2025-12-03).
Drug A was approved in 2020 (source: FDA Drug Database, 2025-12-03).
Study shows 20% efficacy (Smith et al., NEJM 2022, PMID: 12345).
Analysis suggests high attrition [analysis based on ClinicalTrials.gov data].
Market is growing rapidly (source: ClinicalTrials.gov, 2025-12-03).

| Drug | Status | Source |
|------|--------|--------|
| Drug A | Approved | FDA Database |

**Source**: FDA Drug Database (2025-12-03)
""")
    result = validator.validate_report_file(valid_report)
    if result['valid']:
        print("  ✅ PASS: Accepted valid report")
        print(f"     Citation %: {result['stats']['citation_percentage']}")
        passed += 1
    else:
        print(f"  ❌ FAIL: Should have accepted valid report")
        print(f"     Errors: {result['errors']}")
        failed += 1

    # Test 4: Low citation percentage
    print("\nTest 4: Low citation percentage...")
    low_citations = test_dir / "low_citations.md"
    low_citations.write_text("""---
title: Test Report
date: 2025-12-03

data_sources_mcp_verified:
  - test_skill: 100 trials (source: ClinicalTrials.gov, date: 2025-12-03)

data_sources_internal_knowledge:
  - None
---

# Test Report

This report has many claims without citations.
The market is growing. Companies are investing heavily.
New trials are starting. Approvals are expected soon.
Competition is intense. Partnerships are forming.
Innovation continues. Results are promising.
Development timelines are shortening. Success rates improving.
""")
    result = validator.validate_report_file(low_citations)
    if 'Low citation percentage' in str(result['warnings']):
        print("  ✅ PASS: Warning for low citation percentage")
        print(f"     Citation %: {result['stats']['citation_percentage']}")
        passed += 1
    else:
        print("  ❌ FAIL: Should have warned about low citation percentage")
        failed += 1

    # Test 5: High internal knowledge usage
    print("\nTest 5: High internal knowledge usage...")
    high_internal = test_dir / "high_internal.md"
    high_internal.write_text("""---
title: Test Report
date: 2025-12-03

data_sources_mcp_verified:
  - test_skill: 100 trials (source: ClinicalTrials.gov, date: 2025-12-03)

data_sources_internal_knowledge:
  - Market projections [estimated]
  - Pricing data [estimated]
---

# Test Report

Market is $100B [estimated from industry consensus].
Pricing is $1000-1500 [estimated from public data].
Growth rate is 15% [estimated from analyst reports].
""")
    result = validator.validate_report_file(high_internal)
    if 'High internal knowledge usage' in str(result['warnings']):
        print("  ✅ PASS: Warning for high internal knowledge usage")
        print(f"     Internal %: {result['stats']['internal_percentage']}")
        passed += 1
    else:
        print("  ❌ FAIL: Should have warned about high internal knowledge")
        failed += 1

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

    print(f"\n{'='*50}")
    print(f"Report Validation Tests: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")

    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print(" Source Attribution Verification Test Suite")
    print("="*60 + "\n")

    skill_pass = test_skill_validation()
    report_pass = test_report_validation()

    print("="*60)
    if skill_pass and report_pass:
        print("✅ ALL TESTS PASSED")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
