# OpenTargets MCP Interactive Test Script

**Purpose**: Validate OpenTargets MCP behavior, measure token usage, discover quirks, and enhance stub.

**MCP Server**: `opentargets-mcp-server`
**Tool Name**: `mcp__opentargets-mcp-server__opentargets_info`
**Python Stub**: `scripts/mcp/servers/opentargets_mcp/__init__.py`

---

## Test Scenarios

### Test 1: Search targets by gene symbol

**Goal**: Validate gene target search and measure token usage

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="search_targets",
    query="GLP1R",
    size=5
)
```

**Expected Behavior**:
- Returns Ensembl gene IDs
- Includes approved symbols and names
- Clean JSON response

---

### Test 2: Search diseases by name

**Goal**: Validate disease search and EFO ID retrieval

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="search_diseases",
    query="type 2 diabetes",
    size=5
)
```

**Expected Behavior**:
- Returns EFO disease IDs
- Includes disease names and synonyms
- Response size manageable

---

### Test 3: Get target-disease associations

**Goal**: Validate association queries and evidence scores

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="get_target_disease_associations",
    targetId="ENSG00000112164",  # GLP1R gene
    minScore=0.3,
    size=10
)
```

**Expected Behavior**:
- Returns associations with scores
- Includes datatype evidence breakdown
- Score filtering works correctly

---

### Test 4: Get disease targets summary

**Goal**: Test disease-centric view and token usage

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="get_disease_targets_summary",
    diseaseId="EFO_0001360",  # Type 2 diabetes
    minScore=0.5,
    size=20
)
```

**Expected Behavior**:
- Returns ranked targets for disease
- High minScore filters effectively
- Response size reasonable

---

### Test 5: Get target details

**Goal**: Validate detailed target information retrieval

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="get_target_details",
    id="ENSG00000112164"  # GLP1R
)
```

**Expected Behavior**:
- Returns comprehensive target data
- Includes tractability and safety info
- Token usage for detailed view

---

### Test 6: Get disease details

**Goal**: Validate detailed disease information retrieval

**Test Code**:
```python
mcp__opentargets-mcp-server__opentargets_info(
    method="get_disease_details",
    id="EFO_0001360"  # Type 2 diabetes
)
```

**Expected Behavior**:
- Returns disease description and synonyms
- Therapeutic areas included
- Clean structured response

---

## Learning Focus

- Token usage per method type (search vs. details)
- Response structure and field availability
- Score filtering effectiveness
- ID format requirements (Ensembl vs. EFO)
- Evidence datatype breakdown richness
