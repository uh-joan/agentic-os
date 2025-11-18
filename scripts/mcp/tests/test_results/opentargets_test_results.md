# OpenTargets MCP Test Results

**Test Date**: 2025-11-18
**MCP Server**: opentargets-mcp-server
**Tool**: mcp__opentargets-mcp-server__opentargets_info
**Python Stub**: scripts/mcp/servers/opentargets_mcp/__init__.py

---

## Executive Summary

✅ **6 tests executed successfully**
✅ **MONDO IDs validated** - Diseases use MONDO format (not just EFO)
✅ **Token usage measured** - Efficient searches, larger detail queries
✅ **Rich association data** - Comprehensive evidence scores and target rankings

---

## Test Results

### Test 1: Search targets ✅

**Query**:
```python
search_targets(
    query="GLP1R",
    size=5
)
```

**Response**: 1 target found (ENSG00000112164)
**Token Estimate**: ~180 tokens

**Validation**:
- ✅ Returns Ensembl gene ID correctly
- ✅ Includes approved symbol and description
- ✅ Clean JSON structure
- ✅ Response compact and efficient

**Learning**: Search queries are token-efficient (~180 tokens)

---

### Test 2: Search diseases ✅

**Query**:
```python
search_diseases(
    query="type 2 diabetes",
    size=5
)
```

**Response**: 1 disease found (MONDO_0005148)
**Token Estimate**: ~250 tokens

**Validation**:
- ✅ Returns MONDO ID (not EFO as documented)
- ✅ Includes disease name and description
- ✅ Clean structured response

**CRITICAL FINDING**: Disease IDs use MONDO format (e.g., "MONDO_0005148"), not just EFO format. Stub documentation needs update.

---

### Test 3: Get target-disease associations ✅

**Query**:
```python
get_target_disease_associations(
    targetId="ENSG00000112164",
    minScore=0.3,
    size=10
)
```

**Response**: 25 associations returned (more than size=10 requested)
**Token Estimate**: ~1,350 tokens

**Validation**:
- ✅ Returns association scores (range 0.76 to 0.33)
- ✅ Includes both MONDO and EFO disease IDs in results
- ✅ minScore filter works (all scores ≥ 0.3)
- ⚠️ Returned 25 results despite size=10 (API returns all above threshold)

**Learning**:
- Rich association data with ~1,350 tokens for 25 associations
- Size parameter may be overridden by score filtering
- Both MONDO and EFO IDs appear in association results

---

### Test 4: Get disease targets summary ✅

**Query**:
```python
get_disease_targets_summary(
    diseaseId="MONDO_0005148",
    minScore=0.5,
    size=20
)
```

**Response**: 25 targets returned (totalTargets: 9,761)
**Token Estimate**: ~2,550 tokens

**Validation**:
- ✅ Returns ranked targets (top score: 0.86)
- ✅ Includes summary metadata (totalTargets count)
- ✅ Both summary and fullResults provided
- ✅ minScore filter effective (all ≥ 0.5)

**Learning**:
- Comprehensive response with ~2,550 tokens
- Provides both summary view and full results
- Excellent for target prioritization

---

### Test 5: Get target details ✅

**Query**:
```python
get_target_details(
    id="ENSG00000112164"
)
```

**Response**: Basic target information
**Token Estimate**: ~160 tokens

**Validation**:
- ✅ Returns target ID, symbol, name, biotype
- ⚠️ No tractability data in response
- ⚠️ No safety liabilities in response
- ✅ Compact response

**Learning**:
- Basic details are compact (~160 tokens)
- Tractability/safety data may require specific query parameters or not available for all targets
- Much simpler than documented examples suggest

---

### Test 6: Get disease details ✅

**Query**:
```python
get_disease_details(
    id="MONDO_0005148"
)
```

**Response**: Disease information
**Token Estimate**: ~220 tokens

**Validation**:
- ✅ Returns disease ID, name, description
- ⚠️ No synonyms in response
- ⚠️ No therapeutic areas in response
- ✅ Clean structure

**Learning**:
- Basic details are compact (~220 tokens)
- Additional fields (synonyms, therapeutic areas) may require specific query parameters or not available in this endpoint

---

## Token Measurements

| Query Type | Tokens | Notes |
|------------|--------|-------|
| search_targets | ~180 | Very efficient |
| search_diseases | ~250 | Efficient |
| get_target_disease_associations | ~1,350 | Rich data (25 associations) |
| get_disease_targets_summary | ~2,550 | Comprehensive (25 targets) |
| get_target_details | ~160 | Basic info only |
| get_disease_details | ~220 | Basic info only |

---

## Key Findings

### CRITICAL: Disease ID Format

**Discovery**: Diseases use **MONDO format** (e.g., "MONDO_0005148"), not just EFO format

**Impact**:
- Stub documentation says "EFO IDs (e.g., EFO_0000305)"
- Actual responses use MONDO IDs
- Both MONDO and EFO IDs appear in association results

**Action**: Update stub to document MONDO as primary ID format, with EFO also supported

---

### Size Parameter Behavior

**Discovery**: API may return more results than size parameter when score filtering is applied

**Example**: Requested size=10 with minScore=0.3, received 25 results

**Action**: Document that size parameter may be overridden by score thresholds

---

### Response Richness Varies

**Discovery**: Detail endpoints return less data than documented examples

**Observed**:
- target_details: No tractability or safety data
- disease_details: No synonyms or therapeutic areas

**Possible Causes**:
- Data not available for all targets/diseases
- Requires specific query parameters
- Stub examples may be aspirational

**Action**: Document actual response structure, note optional fields

---

## Stub Enhancement Needs

1. ✅ Add token measurements to quirks
2. ✅ Update disease ID format documentation (MONDO primary, EFO secondary)
3. ✅ Document size parameter override behavior
4. ✅ Note that detail responses may be simpler than examples
5. ✅ Clarify that tractability/safety data is optional
