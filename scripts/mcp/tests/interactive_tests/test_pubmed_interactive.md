# PubMed MCP Interactive Test Script

**Purpose**: Validate PubMed MCP behavior, measure token usage, discover quirks, and enhance stub.

**MCP Server**: `pubmed-mcp`
**Tool Name**: `mcp__pubmed-mcp__pubmed_articles`
**Python Stub**: `scripts/mcp/servers/pubmed_mcp/__init__.py`

---

## Test Scenarios

### Test 1: Basic keyword search

**Goal**: Validate basic search works and measure token usage

**Test Code**:
```python
search_keywords(
    keywords="semaglutide diabetes",
    num_results=10
)
```

**Expected Behavior**:
- Returns articles with PMIDs
- Response size manageable
- May return fewer than 10 results (documented limitation)

---

### Test 2: Advanced search with date range

**Goal**: Test date filtering syntax

**Test Code**:
```python
search_advanced(
    query="obesity treatment",
    start_date="2023/01/01",
    end_date="2024/12/31",
    num_results=10
)
```

**Expected Behavior**:
- Results filtered to date range
- Date format YYYY/MM/DD works

---

### Test 3: Get article metadata by PMID

**Goal**: Validate retrieving specific article

**Test Code**:
```python
get_article_metadata(
    pmid="38000000"
)
```

**Expected Behavior**:
- Returns detailed article information
- Includes abstract, authors, citations

---

### Test 4: PDF download capability

**Goal**: Test PDF retrieval

**Test Code**:
```python
get_article_pdf(
    pmid="38000000"
)
```

**Expected Behavior**:
- Returns PDF URL or content
- May not work for all articles (access restrictions)

---

## Learning Focus

- Token usage per article
- Result count limitations
- Date filter syntax
- MeSH term effectiveness
- PDF availability patterns
