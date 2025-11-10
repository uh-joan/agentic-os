# Performance Optimization Strategies

> **Recovered from LSH commit 3e02457 (Oct 9, 2025)**
> Token optimization and performance strategies for efficient MCP database queries.

## PERFORMANCE OPTIMIZATION PRINCIPLES

### Universal Rules (Apply to ALL MCPs)
1. **Count First, Details Later**: Start with aggregated counts before retrieving full records if the tool allows
2. **Field Selection**: Explicitly specify only required fields - reduces tokens by 70-90%
3. **Date Filtering**: Use date ranges to limit historical data
4. **Pagination**: Use limits and offsets for large result sets
5. **Caching Strategy**: Note when data is static vs dynamic

### Token Usage Benchmarks
- FDA FAERS with counts: 90% token reduction
- ClinicalTrials with field limits: 70% token reduction
- PubMed with abstracts only: 80% token reduction
- SEC with section targeting: 85% token reduction

### Query Sequencing Strategy
1. **Broad counts** → Identify areas of interest
2. **Filtered queries** → Narrow to relevant subset
3. **Detailed retrieval** → Get full records for final set
4. **Cross-validation** → Verify with other databases

## DATABASE-SPECIFIC OPTIMIZATIONS

### FDA (fda_info tool)

#### Count-First Pattern (MANDATORY)
```json
// Step 1: Count to understand landscape
{
  "method": "lookup_drug",
  "search_term": "openfda.brand_name:DRUGNAME",
  "count": "application_number",
  "limit": 10
}

// Step 2: Retrieve specific application details
{
  "method": "lookup_drug",
  "search_term": "application_number:BLA123456",
  "search_type": "general",
  "limit": 1
}
```

#### Field Selection Pattern
```json
{
  "method": "lookup_drug",
  "search_term": "semaglutide",
  "fields_for_general": "openfda.brand_name,openfda.application_number,products.marketing_status",
  "limit": 100
}
```

**Token savings**: 70-85% reduction vs full response

### ClinicalTrials.gov (ct_gov_studies tool)

#### Field Limitation
```json
{
  "method": "search",
  "condition": "diabetes",
  "status": "RECRUITING",
  "fields": ["NCTId", "BriefTitle", "Phase", "CompletionDate"],
  "limit": 100
}
```

**Token savings**: 60-75% reduction vs full trial records

#### Status Filtering
- ALWAYS specify status: `["RECRUITING", "ACTIVE_NOT_RECRUITING"]`
- Avoid: Querying all statuses then filtering client-side
- Benefit: 50%+ reduction in result volume

### PubMed (pubmed_articles tool)

#### Abstract-Only Retrieval
```json
{
  "method": "search_keywords",
  "keywords": "semaglutide diabetes",
  "num_results": 50,
  "fields": ["Title", "Abstract", "PMID", "PubDate"]
}
```

**Token savings**: 80% reduction vs full text

#### MeSH Term Precision
- Use: `"Diabetes Mellitus, Type 2"[MeSH]` (controlled vocabulary)
- Avoid: `diabetes type 2` (free text, more noise)
- Benefit: 40-60% reduction in irrelevant results

### SEC EDGAR (sec-edgar tool)

#### Section Targeting
```json
{
  "method": "get_company_submissions",
  "cik_or_ticker": "PFE",
  "form_type": "10-K",
  "sections": ["Item 1", "Item 7"]  // Business + MD&A only
}
```

**Token savings**: 85-90% reduction vs full 10-K

#### Date Range Filtering
```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```

**Benefit**: Limit to relevant fiscal periods

## OPTIMIZATION PATTERNS BY USE CASE

### Pattern 1: Quick Status Check
**Goal**: Fast validation of basic facts
**Strategy**: Count queries only, minimal fields
**Budget**: 100-200 tokens
```
FDA count → ClinicalTrials count → PubMed count
```

### Pattern 2: Targeted Deep Dive
**Goal**: Comprehensive data on specific entity
**Strategy**: Count → Filter → Full retrieve for 1-3 items
**Budget**: 1,000-2,000 tokens
```
Count (10%) → Filter (20%) → Details (70%)
```

### Pattern 3: Competitive Landscape
**Goal**: Multi-entity comparison across databases
**Strategy**: Parallel count queries → Selective deep dives
**Budget**: 5,000-10,000 tokens
```
Parallel counts (500) → Top 5 entities (4,500) → Cross-validation (1,000)
```

### Pattern 4: Exploratory Research
**Goal**: Discover unknowns, identify patterns
**Strategy**: Broad → Narrow → Deep across multiple databases
**Budget**: 10,000-20,000 tokens
```
Pass 1: Broad (2,000) → Pass 2: Filtered (6,000) → Pass 3: Deep (10,000) → Validate (2,000)
```

## ANTI-PATTERNS (AVOID)

### ❌ Retrieve-Then-Filter
**Wrong**:
```
1. Fetch all trials (no filters)
2. Filter client-side for Phase 3
```

**Right**:
```
1. Query with phase="PHASE3" filter
```

**Impact**: 10x token waste

### ❌ Full-Text-First
**Wrong**:
```
1. Get full PubMed articles
2. Extract abstracts client-side
```

**Right**:
```
1. Request abstracts only in query
```

**Impact**: 5x token waste

### ❌ Sequential Count Queries
**Wrong**:
```
Count FDA → Wait → Count CT.gov → Wait → Count PubMed
```

**Right**:
```
Parallel count queries across all databases
```

**Impact**: 3x time waste

### ❌ No Field Selection
**Wrong**:
```json
{
  "method": "lookup_drug",
  "search_term": "aspirin"
  // No fields specified = full response
}
```

**Right**:
```json
{
  "method": "lookup_drug",
  "search_term": "aspirin",
  "fields_for_general": "openfda.brand_name,products.marketing_status"
}
```

**Impact**: 8x token waste

### ❌ FDA Without Count Parameter (CRITICAL)
**Wrong**:
```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "limit": 100
}
```
**Result**: 67,000 tokens → EXCEEDS 25k MCP limit → QUERY FAILS

**Right**:
```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 50
}
```
**Result**: 400 tokens → Returns 13 brand names successfully

**Impact**: 99.4% token reduction, prevents query failure

## PERFORMANCE MONITORING

### Metrics to Track
- **Tokens per data point**: Lower is better
- **Query reuse rate**: Higher is better (caching)
- **Refinement iterations**: Fewer is better (good planning)
- **Cross-validation rate**: Higher is better (data quality)

### Optimization Checklist
Before executing any query:
- [ ] Can I use a count query first?
- [ ] Can I limit fields to only what's needed?
- [ ] Can I add date range filters?
- [ ] Can I use status/type filters?
- [ ] Can I paginate instead of bulk retrieve?
- [ ] Can I run parallel queries?
- [ ] Have I reviewed similar past queries for patterns?

### Red Flags
- Token usage >5,000 for simple status check
- Multiple queries retrieving same data
- Full-text retrieval when summaries suffice
- Client-side filtering of large result sets
- Sequential execution when parallel possible
- No reuse of intermediate results

## CACHING STRATEGIES

### Static Data (cache aggressively)
- FDA approvals (change monthly at most)
- Patent expiry dates (fixed)
- Historical trial results (immutable)
- SEC annual reports (immutable once filed)

### Dynamic Data (cache cautiously)
- Active trial recruitment status (changes weekly)
- Stock prices (changes constantly)
- Adverse event reports (updated continuously)
- Preprint/publication status (changes daily)

### Cache Invalidation
- FDA: 30-day cache
- ClinicalTrials: 7-day cache for active trials
- PubMed: 1-day cache for recent publications
- SEC: Immutable for past filings, 1-day for recent

## TOKEN BUDGET ALLOCATION EXAMPLES

### $10 Budget (~100,000 tokens)
- 10% exploration: 10,000 tokens
- 30% filtering: 30,000 tokens
- 50% detail retrieval: 50,000 tokens
- 10% validation: 10,000 tokens

### $1 Budget (~10,000 tokens)
- Focus on count queries and summaries
- 1-2 detailed retrievals maximum
- No exhaustive validation
- Document coverage limitations

### Unlimited Budget
- Still apply optimization principles
- Validate extensively across sources
- Retrieve historical context
- Build comprehensive entity graphs
- But: Avoid waste - efficiency matters for speed too
