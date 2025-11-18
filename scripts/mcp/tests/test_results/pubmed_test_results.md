# PubMed MCP Test Results

**Test Date**: 2025-11-18
**MCP Server**: pubmed-mcp
**Tool**: mcp__pubmed-mcp__pubmed_articles
**Python Stub**: scripts/mcp/servers/pubmed_mcp/__init__.py

---

## Executive Summary

✅ **3 tests executed successfully**
✅ **Result count limitation confirmed** - Requested 5, got 3 (documented quirk)
✅ **JSON format validated** - Clean, structured responses
✅ **Token usage measured** - ~750 tokens per article with abstract

---

## Test Results

### Test 1: Basic keyword search ✅

**Query**:
```python
search_keywords(
    keywords="semaglutide diabetes",
    num_results=5
)
```

**Response**: 3 articles (not 5 requested)
**Token Estimate**: ~2,250 tokens (750 per article)

**Validation**:
- ✅ JSON format (not markdown)
- ✅ Confirmed result limitation (3 of 5 requested)
- ✅ Full abstracts included
- ⚠️  Fewer results than requested (documented limitation)

**Learning**: Result count limitation is real - request conservatively

---

### Test 2: Advanced search with date filter ✅

**Query**:
```python
search_advanced(
    query="obesity treatment",
    start_date="2024/01/01",
    end_date="2024/12/31",
    num_results=5
)
```

**Response**: 2 articles
**Results Quality**: ⚠️  Not obesity-related (search too broad)

**Validation**:
- ✅ Date filter syntax works (YYYY/MM/DD)
- ✅ Returns 2024 articles
- ⚠️  Search precision needs improvement (use MeSH terms)

**Learning**: Use MeSH terms for precise searches

---

### Test 3: Get article metadata ✅

**Query**:
```python
get_article_metadata(pmid="41251033")
```

**Response**: Complete article metadata
**Token Estimate**: ~750 tokens

**Validation**:
- ✅ Full article details returned
- ✅ Same structure as search results
- ✅ Includes abstract, authors, keywords

---

## Token Measurements

| Query Type | Tokens | Notes |
|------------|--------|-------|
| Per article (with abstract) | ~750 | Full metadata |
| Search (3 articles) | ~2,250 | Includes abstracts |

---

## Stub Enhancements

- ✅ Result limitation already documented
- ✅ Token usage measured
- ✅ Date format confirmed (YYYY/MM/DD)

---

## Key Finding

**Result count limitation is significant** - Users should request conservative numbers (10-20) and expect partial returns.
