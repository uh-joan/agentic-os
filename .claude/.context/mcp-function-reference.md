# MCP Server Function Reference

**Purpose**: Authoritative reference for all available functions across MCP servers

**Last Updated**: 2025-11-29

**Status**: ✅ Validated against actual MCP server implementations

---

## Table of Contents

1. [FDA MCP](#fda-mcp)
2. [PubMed MCP](#pubmed-mcp)
3. [ClinicalTrials.gov MCP](#clinicaltrialsgov-mcp)
4. [WHO MCP](#who-mcp)
5. [Open Targets MCP](#open-targets-mcp)
6. [PubChem MCP](#pubchem-mcp)
7. [SEC EDGAR MCP](#sec-edgar-mcp)
8. [Healthcare (CMS) MCP](#healthcare-cms-mcp)
9. [Financials MCP](#financials-mcp)
10. [Data Commons MCP](#data-commons-mcp)
11. [NLM Codes MCP](#nlm-codes-mcp)
12. [USPTO Patents MCP](#uspto-patents-mcp)

---

## FDA MCP

**Server**: `fda-mcp`
**Import Path**: `from mcp.servers.fda_mcp import *`

### Available Functions

```python
# Drug Information
lookup_drug(search_term: str, search_type: str, **kwargs) -> Dict[str, Any]
```

**Search Types**:
- `"general"` - Drug approvals, products (COUNT REQUIRED)
- `"label"` - Drug labels (BROKEN - use alternatives)
- `"adverse_events"` - FAERS safety data (COUNT REQUIRED)
- `"recalls"` - Enforcement actions (count optional)
- `"shortages"` - Supply chain issues (count optional)

**Critical Parameters**:
- `count` - MANDATORY for `general` and `adverse_events`
- `limit` - Maximum 100 results

**Common Count Fields**:
- General: `"openfda.brand_name.exact"`
- Adverse Events: `"patient.reaction.reactionmeddrapt.exact"`

**Response Structure**:
- Nested: `result['data']['results']`
- Format: `[{"term": "TERM", "count": 123}, ...]`

### Examples

```python
# ✅ CORRECT: Adverse events with count
result = lookup_drug(
    search_term='semaglutide',
    search_type='adverse_events',
    count='patient.reaction.reactionmeddrapt.exact',
    limit=100
)
data = result['data']['results']  # Nested structure

# ✅ CORRECT: General search with count
result = lookup_drug(
    search_term='GLP-1',
    search_type='general',
    count='openfda.brand_name.exact',
    limit=50
)

# ❌ WRONG: Missing count parameter
result = lookup_drug(
    search_term='semaglutide',
    search_type='adverse_events'
)  # FAILS - count is mandatory!

# ❌ WRONG: Non-existent function
from mcp.servers.fda_mcp import search_adverse_events  # ImportError!
```

---

## PubMed MCP

**Server**: `pubmed-mcp`
**Import Path**: `from mcp.servers.pubmed_mcp import *`

### Available Functions

```python
# Basic Search
search_keywords(keywords: str, num_results: int = 10) -> Union[List, Dict]

# Advanced Search
search_advanced(
    term: Optional[str] = None,
    author: Optional[str] = None,
    journal: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_results: int = 10
) -> Union[List, Dict]

# Article Metadata
get_article_metadata(pmid: Union[str, int]) -> Dict[str, Any]

# PDF Download
get_article_pdf(pmid: Union[str, int]) -> Dict[str, Any]
```

**Response Format**: Returns either a list directly OR a dict with 'articles' key

**Critical Notes**:
- MCP may return fewer results than `num_results` requested
- Date format: `"YYYY/MM/DD"`
- Maximum `num_results`: 100

### Examples

```python
# ✅ CORRECT: Basic search
result = search_keywords(
    keywords="semaglutide obesity",
    num_results=10
)

# Handle both response formats
if isinstance(result, list):
    articles = result
else:
    articles = result.get('articles', [])

# ✅ CORRECT: Advanced search with date filter
result = search_advanced(
    term="GLP-1 agonist",
    journal="N Engl J Med",
    start_date="2023/01/01",
    end_date="2024/12/31",
    num_results=20
)

# ❌ WRONG: Non-existent function
from mcp.servers.pubmed_mcp import search  # ImportError!

# ❌ WRONG: Wrong date format
search_advanced(start_date="2024-01-01")  # Must be 2024/01/01
```

---

## ClinicalTrials.gov MCP

**Server**: `ct-gov-mcp`
**Import Path**: `from mcp.servers.ct_gov_mcp import search`

### Available Functions

```python
# Search Clinical Trials
search(
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    term: Optional[str] = None,
    **kwargs
) -> str  # Returns MARKDOWN string!
```

**Critical Notes**:
- Returns MARKDOWN, not JSON!
- Must parse with regex
- Use `pageSize` (not `limit`) for pagination
- Maximum `pageSize`: 1000

### Examples

```python
# ✅ CORRECT: Basic search
result = search(
    term="KRAS inhibitor",
    pageSize=100
)

# Parse markdown response
import re
nct_ids = re.findall(r'NCT\d{8}', result)

# ✅ CORRECT: Complex search
result = search(
    condition="obesity",
    intervention="semaglutide",
    status="recruiting",
    phase="PHASE3",
    pageSize=500
)

# ❌ WRONG: Treating as JSON
trials = result.get('trials')  # AttributeError - result is string!

# ❌ WRONG: Using wrong function name
from mcp.servers.ct_gov_mcp import ct_gov_studies  # ImportError!
```

---

## WHO MCP

**Server**: `who-mcp`
**Import Path**: `from mcp.servers.who_mcp import *`

### Available Functions

```python
# Health Data Query
get_health_data(indicator_code: str, **kwargs) -> Dict[str, Any]

# Country-Specific Data
get_country_data(
    country_code: str,
    indicator_code: str,
    **kwargs
) -> Dict[str, Any]

# Cross-Table Query
get_cross_table(**kwargs) -> Dict[str, Any]

# Dimensions
get_dimensions() -> Dict[str, Any]
get_dimension_codes(dimension_code: str) -> Dict[str, Any]

# Search
search_indicators(keywords: str) -> Dict[str, Any]
```

### Examples

```python
# ✅ CORRECT: Get health data
result = get_health_data(
    indicator_code="WHOSIS_000001",  # Life expectancy
    filter="SpatialDim eq 'USA'"
)

# ✅ CORRECT: Country data
result = get_country_data(
    country_code="USA",
    indicator_code="CVD_DEATHS"
)

# ❌ WRONG: Non-existent function
from mcp.servers.who_mcp import get_health_statistics  # ImportError!
```

---

## Open Targets MCP

**Server**: `opentargets-mcp-server`
**Import Path**: `from mcp.servers.opentargets_mcp import *`

### Available Functions

```python
# Search
search_targets(query: str, size: int = 25) -> Dict[str, Any]
search_diseases(query: str, size: int = 25) -> Dict[str, Any]

# Associations
get_target_disease_associations(
    targetId: str,
    diseaseId: Optional[str] = None,
    minScore: float = 0.0,
    size: int = 50
) -> Dict[str, Any]

get_disease_targets_summary(
    diseaseId: str,
    minScore: float = 0.0,
    size: int = 50
) -> Dict[str, Any]

# Details
get_target_details(id: str) -> Dict[str, Any]
get_disease_details(id: str) -> Dict[str, Any]
```

### Examples

```python
# ✅ CORRECT: Search for targets
result = search_targets(
    query="KRAS",
    size=10
)

# ✅ CORRECT: Get associations
result = get_target_disease_associations(
    targetId="ENSG00000133703",
    diseaseId="EFO_0000305",
    minScore=0.5
)
```

---

## PubChem MCP

**Server**: `pubchem-mcp-server`
**Import Path**: `from mcp.servers.pubchem_mcp import *`

### Available Functions

```python
# Search
search_compounds(query: str, **kwargs) -> Dict[str, Any]
search_by_smiles(smiles: str, **kwargs) -> Dict[str, Any]
search_similar_compounds(smiles: str, threshold: int = 90) -> Dict[str, Any]

# Get Details
get_compound_info(cid: Union[int, str]) -> Dict[str, Any]
get_compound_synonyms(cid: Union[int, str]) -> Dict[str, Any]
get_compound_properties(cid: Union[int, str]) -> Dict[str, Any]

# Structure
get_3d_conformers(cid: Union[int, str]) -> Dict[str, Any]
analyze_stereochemistry(cid: Union[int, str]) -> Dict[str, Any]

# Assay
get_assay_info(aid: int) -> Dict[str, Any]

# Safety
get_safety_data(cid: Union[int, str]) -> Dict[str, Any]

# Batch
batch_compound_lookup(cids: List[int], operation: str = "property") -> Dict[str, Any]
```

---

## SEC EDGAR MCP

**Server**: `sec-mcp-server`
**Import Path**: `from mcp.servers.sec_edgar_mcp import *`

### Available Functions

```python
# Company Search
search_companies(query: str) -> Dict[str, Any]
get_company_cik(ticker: str) -> Dict[str, Any]

# Company Data
get_company_submissions(cik_or_ticker: str) -> Dict[str, Any]
get_company_facts(cik_or_ticker: str) -> Dict[str, Any]
get_company_concept(
    cik_or_ticker: str,
    taxonomy: str,
    tag: str
) -> Dict[str, Any]

# Frames
get_frames_data(taxonomy: str, tag: str, unit: str, frame: str) -> Dict[str, Any]

# Filtering
filter_filings(
    filings: List[Dict],
    form_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10
) -> List[Dict]
```

---

## Healthcare (CMS) MCP

**Server**: `healthcare-mcp`
**Import Path**: `from mcp.servers.healthcare_mcp import cms_search_providers`

### Available Functions

```python
# CMS Provider Search
cms_search_providers(
    dataset_type: str,  # Required
    **kwargs
) -> Dict[str, Any]
```

**Dataset Types**:
- `"geography_and_service"`
- `"provider_and_service"`
- `"provider"`

---

## Financials MCP

**Server**: `financials-mcp-server`
**Import Path**: `from mcp.servers.financials_mcp import financial_intelligence`

### Available Functions

```python
# Financial Intelligence
financial_intelligence(
    method: str,
    symbol: str = "",
    **kwargs
) -> Dict[str, Any]
```

**Methods**:
- Stock: `"stock_profile"`, `"stock_summary"`, `"stock_pricing"`, etc.
- Economic: `"economic_indicators"`, `"market_indices"`
- FRED: `"fred_series_search"`, `"fred_series_data"`, etc.

---

## Data Commons MCP

**Server**: `datacommons-mcp`
**Import Path**: `from mcp.servers.datacommons_mcp import *`

### Available Functions

```python
# Search
search_indicators(
    query: str,
    places: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]

# Get Data
get_observations(
    variable_dcid: str,
    place_dcid: str,
    date: str = "latest",
    **kwargs
) -> Dict[str, Any]
```

---

## NLM Codes MCP

**Server**: `nlm-codes-mcp`
**Import Path**: `from mcp.servers.nlm_codes_mcp import nlm_ct_codes`

### Available Functions

```python
# Clinical Coding Search
nlm_ct_codes(
    method: str,
    terms: str,
    **kwargs
) -> Dict[str, Any]
```

**Methods**:
- `"icd-10-cm"` - ICD-10 diagnosis codes
- `"icd-11"` - ICD-11 codes
- `"hcpcs-LII"` - HCPCS Level II procedure codes
- `"npi-organizations"` - NPI organization records
- `"npi-individuals"` - NPI individual provider records
- `"hpo-vocabulary"` - HPO phenotype terms
- `"conditions"` - Medical conditions
- `"rx-terms"` - Drug terminology

---

## USPTO Patents MCP

**Server**: `patents-mcp-server`
**Import Path**: `from mcp.servers.uspto_patents_mcp import *`

### Available Functions

```python
# USPTO Search
ppubs_search_patents(query: str, **kwargs) -> Dict[str, Any]
ppubs_search_applications(query: str, **kwargs) -> Dict[str, Any]
ppubs_get_full_document(guid: str, source_type: str) -> Dict[str, Any]
ppubs_get_patent_by_number(patent_number: Union[str, int]) -> Dict[str, Any]
ppubs_download_patent_pdf(patent_number: Union[str, int]) -> bytes

# Google Patents Search
google_search_patents(query: str, **kwargs) -> Dict[str, Any]
google_get_patent(publication_number: str) -> Dict[str, Any]
google_get_patent_claims(publication_number: str) -> Dict[str, Any]
google_get_patent_description(publication_number: str) -> Dict[str, Any]
google_search_by_inventor(inventor_name: str, **kwargs) -> Dict[str, Any]
google_search_by_assignee(assignee_name: str, **kwargs) -> Dict[str, Any]
google_search_by_cpc(cpc_code: str, **kwargs) -> Dict[str, Any]
```

---

## Common Import Errors & Fixes

### ❌ Common Mistakes

```python
# PubMed
from mcp.servers.pubmed_mcp import search  # ❌ Does not exist!
from mcp.servers.pubmed_mcp import search_keywords  # ✅ Correct

# FDA
from mcp.servers.fda_mcp import search_adverse_events  # ❌ Does not exist!
from mcp.servers.fda_mcp import lookup_drug  # ✅ Correct (with search_type='adverse_events')

# WHO
from mcp.servers.who_mcp import get_health_statistics  # ❌ Does not exist!
from mcp.servers.who_mcp import get_health_data  # ✅ Correct

# CT.gov
from mcp.servers.ct_gov_mcp import ct_gov_studies  # ❌ Does not exist!
from mcp.servers.ct_gov_mcp import search  # ✅ Correct
```

### ✅ Validation Checklist

Before creating a skill:

1. **Check this reference** - Verify function exists
2. **Verify import path** - Use exact import from this document
3. **Check parameters** - Use correct parameter names
4. **Validate response format** - Some return JSON, CT.gov returns markdown
5. **Test imports** - Run `python3 -c "from mcp.servers.X import Y"` to verify

---

## Quick Reference Table

| Server | Common Functions | Response Format | Special Notes |
|--------|------------------|-----------------|---------------|
| `fda_mcp` | `lookup_drug` | JSON (nested) | Count required for general/adverse_events |
| `pubmed_mcp` | `search_keywords`, `search_advanced` | List or Dict | Variable result counts |
| `ct_gov_mcp` | `search` | **Markdown string** | Must parse with regex |
| `who_mcp` | `get_health_data`, `get_country_data` | JSON | Indicator codes required |
| `opentargets_mcp` | `search_targets`, `get_target_disease_associations` | JSON | Ensembl/EFO IDs |
| `pubchem_mcp` | `search_compounds`, `get_compound_info` | JSON | CID-based queries |
| `sec_edgar_mcp` | `get_company_submissions`, `get_company_facts` | JSON | CIK or ticker |
| `healthcare_mcp` | `cms_search_providers` | JSON | Dataset type required |
| `financials_mcp` | `financial_intelligence` | JSON | Method-based routing |
| `datacommons_mcp` | `search_indicators`, `get_observations` | JSON | Place DCIDs |
| `nlm_codes_mcp` | `nlm_ct_codes` | JSON | Method-based routing |
| `uspto_patents_mcp` | `google_search_patents`, `ppubs_search_patents` | JSON | Two API backends |

---

## Usage Guidelines

1. **Always check this reference before creating a new skill**
2. **Never guess function names** - verify against this document
3. **Test imports early** - catch import errors before execution
4. **Follow response format** - JSON vs markdown parsing
5. **Respect parameter constraints** - count requirements, limits, etc.

---

**Document Status**: ✅ Validated against MCP server implementations (2025-11-29)

**Report Issues**: Update this document when discovering new functions or deprecations
