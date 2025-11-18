# PubChem MCP Interactive Test Script

**Purpose**: Validate PubChem MCP behavior, measure token usage, discover quirks, and enhance stub.

**MCP Server**: `pubchem-mcp-server`
**Tool Name**: `mcp__pubchem-mcp-server__pubchem`
**Python Stub**: `scripts/mcp/servers/pubchem_mcp/__init__.py`

---

## Test Scenarios

### Test 1: Search compounds by name

**Goal**: Validate basic compound search and measure token usage

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="search_compounds",
    query="aspirin",
    max_records=5
)
```

**Expected Behavior**:
- Returns CIDs for aspirin compounds
- Includes molecular formula and weight
- Response size manageable

---

### Test 2: Get compound info by CID

**Goal**: Validate detailed compound retrieval

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="get_compound_info",
    cid="2244"  # Aspirin CID
)
```

**Expected Behavior**:
- Returns comprehensive compound data
- Includes SMILES, InChI, properties
- Token usage for detailed view

---

### Test 3: Get compound properties

**Goal**: Test property-specific queries and token efficiency

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="get_compound_properties",
    cid="2244",
    properties=["MolecularWeight", "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount"]
)
```

**Expected Behavior**:
- Returns only requested properties
- More efficient than get_compound_info
- Clean structured response

---

### Test 4: Search similar compounds

**Goal**: Validate similarity search and token usage

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="search_similar_compounds",
    smiles="CC(=O)Oc1ccccc1C(=O)O",  # Aspirin SMILES
    threshold=90,
    max_records=10
)
```

**Expected Behavior**:
- Returns structurally similar compounds
- Threshold filtering works
- Response size reasonable for max_records

---

### Test 5: Get compound synonyms

**Goal**: Test synonym retrieval and token usage

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="get_compound_synonyms",
    cid="2244"
)
```

**Expected Behavior**:
- Returns list of synonyms (drug names, trade names)
- Token usage for synonym lists
- May be large for well-known drugs

---

### Test 6: Get safety data (GHS classifications)

**Goal**: Validate safety/hazard data retrieval

**Test Code**:
```python
mcp__pubchem-mcp-server__pubchem(
    method="get_safety_data",
    cid="2244"
)
```

**Expected Behavior**:
- Returns GHS classifications
- Hazard statements included
- Response structure validated

---

## Learning Focus

- Token usage per method type (search vs. detailed data)
- Response size for different query types
- max_records effectiveness
- Property filtering efficiency
- Synonym list sizes
- Safety data availability
