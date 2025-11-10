# Quality Control Checklist

> **Recovered from LSH commit 3e02457 (Oct 9, 2025)**
> Quality control standards for pharmaceutical intelligence searches.

## PRE-SEARCH QUALITY CHECKS

### Query Design Review
Before executing any database query:
- [ ] **Clarity**: Is the search objective clearly defined?
- [ ] **Scope**: Is the geographic/temporal scope appropriate?
- [ ] **Entities**: Are entity identifiers standardized?
- [ ] **Filters**: Are filters specific enough to avoid noise?
- [ ] **Fields**: Are only necessary fields requested?
- [ ] **Token budget**: Is token allocation reasonable for task?

### Database Selection Review
- [ ] **Coverage**: Do selected databases cover required dimensions?
- [ ] **Relevance**: Is each database necessary for the question?
- [ ] **Redundancy**: Are we checking multiple sources for validation?
- [ ] **Gaps**: Have we identified known data gaps upfront?

### Optimization Review
- [ ] **Count-first**: Will we use count queries where applicable?
- [ ] **Field selection**: Are fields limited to essentials?
- [ ] **Date ranges**: Are date filters applied appropriately?
- [ ] **Status filters**: Are we using database-native filters?
- [ ] **Pagination**: Is pagination strategy defined for large results?

## DURING-SEARCH QUALITY CHECKS

### Execution Monitoring
As queries execute:
- [ ] **Token tracking**: Monitor actual vs budgeted token usage
- [ ] **Result volumes**: Check if result counts match expectations
- [ ] **Error handling**: Document any errors and fallback strategies
- [ ] **Refinement triggers**: Note when/why query refinements occur
- [ ] **Time tracking**: Monitor query execution time

### Intermediate Validation
After each major query:
- [ ] **Result sanity check**: Do results pass basic reasonableness test?
- [ ] **Entity verification**: Are entity names/IDs consistent?
- [ ] **Null handling**: Are missing data points expected or errors?
- [ ] **Format validation**: Is response structure as expected?

## POST-SEARCH QUALITY CHECKS

### Data Completeness
- [ ] **Coverage achieved**: Did we get data for all requested dimensions?
- [ ] **Minimum thresholds**: Did we meet minimum data point requirements?
- [ ] **Gap documentation**: Are data gaps clearly documented?
- [ ] **Source attribution**: Is every data point traceable to source?

### Data Quality
- [ ] **Accuracy**: Are there obvious errors or outliers?
- [ ] **Consistency**: Do related data points align logically?
- [ ] **Timeliness**: Is data current enough for the use case?
- [ ] **Completeness**: Are required fields populated?

### Cross-Validation
- [ ] **Multi-source confirmation**: Are key findings confirmed across 2+ databases?
- [ ] **Contradiction identification**: Have we found and documented disagreements?
- [ ] **Contradiction resolution**: Have contradictions been investigated and explained?
- [ ] **Confidence assessment**: Are confidence levels assigned to findings?

### Token Efficiency
- [ ] **Budget adherence**: Did we stay within token budget?
- [ ] **Optimization success**: Did count-first and field selection work?
- [ ] **Waste identification**: Were any queries unnecessarily large?
- [ ] **Efficiency metrics**: What was information gained per token?

## DELIVERABLE QUALITY CHECKS

### Reporting Standards
Before delivering results:
- [ ] **Executive summary**: Clear 2-3 sentence summary of findings
- [ ] **Key findings**: Bullet points for main discoveries
- [ ] **Confidence levels**: Each finding labeled High/Medium/Low confidence
- [ ] **Source citations**: Every claim has database + query reference
- [ ] **Methodology**: Search strategy and databases used are documented
- [ ] **Limitations**: Data gaps and coverage issues noted
- [ ] **Contradictions**: Any disagreements between sources explained
- [ ] **Next steps**: Recommended follow-up searches identified

### Data Export Standards
If exporting raw data:
- [ ] **Format consistency**: All exports use consistent field names
- [ ] **Metadata inclusion**: Timestamp, database, query parameters included
- [ ] **Completeness**: Full raw responses preserved
- [ ] **Reproducibility**: Query parameters saved for replication
- [ ] **Documentation**: README or summary explains data structure

## CONFIDENCE LEVEL CRITERIA

### High Confidence (✅)
**Criteria**:
- Confirmed across 3+ independent sources
- Official/authoritative sources (FDA, SEC, CT.gov)
- Recent data (<6 months old)
- No contradictions found
- Expected data patterns observed

**Example**: FDA approval date (verified in FDA database, SEC filing, company website)

### Medium Confidence (⚠️)
**Criteria**:
- Confirmed across 2 sources
- Some sources lag (6-12 months old)
- Minor inconsistencies explained
- Reasonable inference from available data

**Example**: Trial completion date (CT.gov says "completed", company mentions in 10-Q, but no results posted yet)

### Low Confidence (❌)
**Criteria**:
- Single source only
- Data quality concerns
- Significant contradictions
- Extrapolation required
- Outdated data (>12 months)

**Example**: Pipeline stage (mentioned in old press release, not in official filings)

### Unknown/No Data (🔍)
**Criteria**:
- No data found in any source
- Contradictory data cannot be resolved
- Out of scope for available databases

**Example**: Pre-clinical compound not yet in clinical trials

## COMMON QUALITY ISSUES

### Issue 1: Entity Name Variations
**Problem**: Drug has multiple names, queries miss some
**Detection**: Lower-than-expected result counts
**Resolution**: Use entity mapping strategies (see `cross-database-integration.md`)
**Prevention**: Start with standardized identifiers (UNII, CIK, ORCID)

### Issue 2: Date Range Misalignment
**Problem**: Query date range doesn't match event timing
**Detection**: Zero results when data should exist
**Resolution**: Expand date range, check for timezone issues
**Prevention**: Use broad dates initially, then narrow

### Issue 3: Field Selection Too Narrow
**Problem**: Critical fields omitted, requiring re-query
**Detection**: Insufficient data for analysis
**Resolution**: Re-query with additional fields (token cost)
**Prevention**: Review field schemas before execution

### Issue 4: Over-Aggregation
**Problem**: Count queries too high-level, lose important detail
**Detection**: Need to break down aggregate numbers
**Resolution**: Run more granular queries
**Prevention**: Design query hierarchy upfront

### Issue 5: Geographic Scope Errors
**Problem**: Query scope doesn't match question
**Detection**: Results include wrong regions or miss key regions
**Resolution**: Add/refine geographic filters
**Prevention**: Clarify geographic scope in query planning

### Issue 6: Status Filter Misapplication
**Problem**: Wrong status codes or missing active statuses
**Detection**: Expected entities missing from results
**Resolution**: Check status code definitions, broaden if needed
**Prevention**: Review status taxonomies per database

## AUDIT TRAIL REQUIREMENTS

Every search should produce audit trail with:

### 1. Query Log
```
Timestamp: 2025-11-10T14:30:00Z
Database: FDA fda_info
Method: lookup_drug
Parameters: {search_term: "semaglutide", search_type: "general"}
Results: 4 applications found
Tokens: 350 used
```

### 2. Decision Log
```
Decision: Use count-first strategy for FDA query
Rationale: Unknown result volume, optimize tokens
Outcome: Saved 85% tokens vs direct retrieval
```

### 3. Refinement Log
```
Initial query: status="recruiting"
Results: 500 trials (too many)
Refinement: Added phase="PHASE3"
Results: 45 trials (manageable)
```

### 4. Validation Log
```
Finding: "Semaglutide approved for diabetes"
Source 1: FDA (approved 2017-12-05)
Source 2: SEC 8-K (announced 2017-12-06)
Source 3: ClinicalTrials.gov (results posted 2017-11)
Confidence: High (3 sources agree)
```

## ESCALATION CRITERIA

### When to Flag for Review
Escalate search results if:
- [ ] Contradictions cannot be resolved
- [ ] Data quality issues affect >20% of findings
- [ ] Token budget exceeded by >50%
- [ ] Key data sources unavailable/errored
- [ ] Confidence levels mostly Low
- [ ] Critical information gaps identified
- [ ] Timeline inconsistencies suggest data errors
- [ ] Novel patterns detected (not matching known workflows)

### Review Protocol
1. **Document issue**: Specific problem statement
2. **Show evidence**: Query results and contradictions
3. **Propose solutions**: Alternative strategies
4. **Estimate impact**: Token and time requirements
5. **Request guidance**: Clarify requirements or approve refinement

## QUALITY METRICS TRACKING

### Per-Search Metrics
- **Token efficiency**: Information points per 1,000 tokens
- **Coverage rate**: % of requested dimensions satisfied
- **Validation rate**: % of findings confirmed across sources
- **Confidence distribution**: % High vs Medium vs Low
- **Gap rate**: % of searches with significant data gaps
- **Error rate**: % of queries that failed or needed refinement

### Target Benchmarks
- Token efficiency: >5 information points per 1,000 tokens
- Coverage rate: >85% of dimensions
- Validation rate: >60% of findings
- Confidence: >50% High confidence
- Gap rate: <25% of searches
- Error rate: <15% of queries

### Continuous Improvement
Track metrics over time to:
- Identify systematic issues
- Refine query templates
- Improve database selection
- Optimize token budgets
- Share best practices

## FINAL CHECKLIST (Use Before Delivery)

- [ ] All requested information dimensions addressed
- [ ] Key findings clearly summarized
- [ ] Confidence levels assigned and documented
- [ ] Sources cited for all claims
- [ ] Contradictions identified and resolved/explained
- [ ] Data gaps acknowledged with recommendations
- [ ] Token usage reported and within budget
- [ ] Methodology documented for reproducibility
- [ ] Quality issues flagged if present
- [ ] Next steps recommended
- [ ] Audit trail complete
- [ ] Deliverables formatted consistently
