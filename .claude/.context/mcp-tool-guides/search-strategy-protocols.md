# Search Strategy Protocols

> **Recovered from LSH commit 3e02457 (Oct 9, 2025)**
> These strategic protocols were lost during optimization but contain valuable execution guidance for comprehensive pharmaceutical intelligence searches.

## COGNITIVE ENHANCEMENT DIRECTIVES

### Thinking Modes (Use Throughout Analysis)
- **"think"**: Apply to routine database selection and query construction
- **"think hard"**: Apply when analyzing token optimization trade-offs or cross-database correlations
- **"think harder"**: Apply for complex safety signal patterns or competitive intelligence synthesis
- **"ultrathink"**: Apply when designing novel multi-database workflows or resolving contradictory data sources

### When to Invoke Deep Reasoning
- Before executing multi-step workflows: Ultrathink the optimal database sequence
- During query optimization: Think hard about field selection vs information completeness trade-offs
- When encountering contradictions: Think harder about source reliability and data provenance
- For novel user requests: Ultrathink whether existing workflow patterns apply or new approach needed

## EXECUTION PROTOCOL (MANDATORY WORKFLOW)

### Phase 1: EXPLORE (10% time budget)
**Think hard about user intent and required data sources**
1. Parse user request to identify:
   - Primary entity (drug, company, indication, investigator)
   - Information dimensions needed (clinical, regulatory, financial, safety)
   - Geographic/temporal scope
   - Depth vs breadth trade-off
2. Map to optimal database selection:
   - Clinical: ClinicalTrials.gov, PubMed
   - Regulatory: FDA databases (approvals, FAERS, orange book)
   - Financial: SEC EDGAR, Yahoo Finance, FRED
   - Population: Data Commons, WHO, CMS
3. Identify potential data gaps and cross-validation needs
4. Estimate token budget allocation across databases

### Phase 2: PLAN (20% time budget)
**Ultrathink the complete search strategy before execution**
1. Design query sequence with dependencies:
   - Parallel queries (can run simultaneously)
   - Sequential queries (depend on prior results)
   - Conditional queries (triggered by findings)
2. Set token budgets per database:
   - Count queries: 5-10% of budget
   - Filtered queries: 30-40% of budget
   - Detailed retrieval: 50-60% of budget
3. Define success criteria:
   - Minimum data points required
   - Cross-validation checkpoints
   - Stopping conditions (sufficient data vs diminishing returns)
4. Document search strategy for reproducibility
5. Identify fallback strategies for each query

### Phase 3: EXECUTE (60% time budget)
**Think about real-time optimization during execution**
1. Start with count/aggregation queries (validate assumptions)
2. Refine based on initial results:
   - Adjust date ranges if volume too high/low
   - Add filters if noise detected
   - Expand scope if insufficient data
3. Run targeted queries with field selection
4. Monitor token usage and adjust remaining queries
5. Execute cross-validation queries from alternative sources
6. Document deviations from plan with rationale

### Phase 4: VALIDATE (10% time budget)
**Think harder about result quality and completeness**
1. Cross-reference findings across databases:
   - Do clinical trial results align with FDA approvals?
   - Do safety signals match literature reports?
   - Do financial metrics correlate with pipeline events?
2. Identify contradictions and investigate causes:
   - Data source coverage differences
   - Timing lags (trial results vs publications)
   - Entity mapping issues (drug names, company names)
3. Assess confidence levels per finding:
   - High: Confirmed across 3+ sources
   - Medium: Confirmed across 2 sources
   - Low: Single source, requires validation
4. Document information gaps and recommend follow-up searches

## ITERATIVE REFINEMENT PROTOCOL (AUTO-APPLY)

### Pass 1: Broad Discovery (10% token budget)
**Think about maximizing information gain with minimal tokens**
- Execute count queries only: `count="field_name"` for all databases
- Identify high-density data sources (most relevant results per token)
- Map data distribution (temporal, geographic, sponsor, indication)
- **Success criteria**: Understand data landscape and prioritize deep dives
- **If insufficient**: Broaden search terms, reduce filters

### Pass 2: Filtered Targeting (30% token budget)
**Think hard about balancing precision and recall**
- Apply date ranges, status filters, field selection based on Pass 1
- Retrieve summary-level details (titles, key dates, sponsors, outcomes)
- Cross-check entity mappings (drug names, company IDs, trial NCT numbers)
- **Success criteria**: Narrow to relevant subset (20-30% of original count)
- **If insufficient**: Relax filters incrementally, check synonyms/variations

### Pass 3: Deep Detail Retrieval (60% token budget)
**Think about completeness vs token efficiency**
- Fetch full records for final filtered set
- Extract detailed fields (protocols, endpoints, financial metrics, adverse event details)
- Build entity relationship graphs (investigators, institutions, sponsors)
- **Success criteria**: Complete data for synthesis and reporting
- **If insufficient**: Prioritize most critical entities, defer less important details

### Refinement Loop (Iterate if needed)
**Ultrathink whether iteration improves results significantly**
- **Trigger conditions**: Contradictory findings, data gaps >30%, low confidence
- **Action**: Adjust query parameters (synonyms, broader/narrower terms, adjacent time periods)
- **Stopping conditions**: Diminishing returns (<10% new info per iteration), token budget exhausted
- **Document**: Number of iterations and optimization insights for future searches

## HOW TO USE THESE PROTOCOLS

### For Simple Searches (single database, known entity)
- Skip elaborate protocols
- Use basic 3-step: Count → Filter → Retrieve
- Apply performance optimization rules from `performance-optimization.md`

### For Complex Searches (multi-database, novel analysis)
- Follow 4-phase execution protocol rigorously
- Use 3-pass iterative refinement
- Apply cognitive directives at each decision point
- Cross-validate with patterns from `cross-database-integration.md`

### For Uncertain Searches (ambiguous entity, exploratory)
- Start with Phase 1 EXPLORE (double the time budget to 20%)
- Use "ultrathink" mode extensively
- Execute Pass 1 (Broad Discovery) across all candidate databases
- Reassess strategy after initial findings

## TOKEN BUDGET EXAMPLES

### Small Search (1,000 tokens available)
- Phase 1 EXPLORE: 100 tokens
- Phase 2 PLAN: 200 tokens
- Phase 3 EXECUTE: 600 tokens
- Phase 4 VALIDATE: 100 tokens

### Medium Search (5,000 tokens available)
- Pass 1 Broad Discovery: 500 tokens (count queries)
- Pass 2 Filtered Targeting: 1,500 tokens (summary data)
- Pass 3 Deep Detail: 3,000 tokens (full records)

### Large Search (20,000 tokens available)
- Multi-database coordinated execution
- Apply both 4-phase protocol AND 3-pass refinement
- Reserve 2,000 tokens for cross-validation
- Reserve 1,000 tokens for unexpected refinement iterations

## SUCCESS METRICS

Track and report:
- **Token efficiency**: Information gained per token spent
- **Coverage**: % of requested information dimensions satisfied
- **Confidence**: % of findings confirmed across multiple sources
- **Gaps**: Documented information dimensions that remain incomplete
- **Optimization**: Token savings from count-first and field selection strategies
