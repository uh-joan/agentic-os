# MCP Tool Guides - Complete Documentation

> **Status**: Comprehensive documentation recovered from LSH commit 3e02457 (Oct 9, 2025)
> **Last Updated**: November 10, 2025

## Overview

This directory contains complete pharmaceutical intelligence search documentation, including both **tool-specific guides** (basic usage) and **strategic protocols** (execution methodology) that were previously separated during optimization.

## Documentation Structure

### 📘 Tool-Specific Guides (Basic Usage)
Individual database documentation with parameter patterns and optimization rules:

| File | Database | Key Features |
|------|----------|--------------|
| `fda.md` | FDA Drug Database | Approvals, safety, labels, recalls |
| `clinicaltrials.md` | ClinicalTrials.gov | Trial status, recruitment, results |
| `pubmed.md` | PubMed Literature | Publications, MeSH terms, citations |
| `sec-edgar.md` | SEC Filings | 10-K/Q, 8-K, pipeline disclosures |
| `datacommons.md` | Population Data | Demographics, epidemiology, geography |
| `uspto-patents.md` | Patent Database | Patent search, FTO analysis, assignments |
| `opentargets.md` | Target Validation | Genetic evidence, disease associations |
| `pubchem.md` | Compound Properties | Chemical structure, ADME, safety alerts |

**Use these when**: You need specific query syntax or response field information for a database.

### 🎯 Strategic Protocols (Advanced)
Comprehensive execution methodologies recovered from historical documentation:

| File | Purpose | Use When |
|------|---------|----------|
| `search-strategy-protocols.md` | Cognitive directives, 4-phase execution, 3-pass refinement | Planning complex multi-database searches |
| `search-workflows.md` | Complete workflow templates (833 lines) | Need proven patterns for common scenarios |
| `performance-optimization.md` | Token efficiency, query patterns, anti-patterns | Optimizing costs and speed |
| `cross-database-integration.md` | Entity linking, timeline alignment, triangulation | Connecting data across sources |
| `quality-control.md` | QC checklists, confidence criteria, audit trails | Ensuring result quality and reliability |

**Use these when**: You need strategic guidance for workflow design, optimization, or validation.

## Quick Start Guide

### For Simple Queries
1. Read relevant tool-specific guide (e.g., `fda.md`)
2. Use parameter examples directly
3. Apply basic optimization (count-first, field selection)

### For Complex Searches
1. Start with `search-strategy-protocols.md` → Read 4-phase execution protocol
2. Review `search-workflows.md` → Find similar workflow template
3. Apply `performance-optimization.md` → Optimize token budget
4. Use tool-specific guides → Construct actual queries
5. Apply `cross-database-integration.md` → Link entities across sources
6. Follow `quality-control.md` → Validate results

### For Novel/Exploratory Searches
1. **Phase 1 EXPLORE** (search-strategy-protocols.md): Use "ultrathink" mode to map strategy
2. **Pass 1 Broad Discovery** (search-strategy-protocols.md): Execute count queries across all candidate databases
3. Review similar workflows (search-workflows.md) for inspiration
4. Design custom workflow using tool guides
5. Apply cross-validation patterns (cross-database-integration.md)

## Documentation History

### October 9, 2025 - Comprehensive Version (Commit 3e02457)
- **File**: LSH `.claude/agents/pharma-search-specialist.md` (1,646 lines)
- **Content**: All tool guides + strategic protocols in single file
- **Token cost**: ~1,500 additional tokens per invocation

### November 9, 2025 - Optimization Split (Commit b08e6ff)
- **Change**: Extracted tool guides to separate files
- **Created**: 8 tool-specific guides (454 lines total)
- **Lost**: Strategic protocols (cognitive directives, execution protocols, workflows)
- **Savings**: 26% reduction in agent file size

### November 10, 2025 - Recovery (This Update)
- **Recovered**: All strategic protocols from commit 3e02457
- **Added**: 5 strategic protocol files (comprehensive documentation)
- **Result**: Best of both worlds - organized structure + complete guidance

## File Descriptions

### search-strategy-protocols.md
**What it contains**:
- **Cognitive Enhancement Directives**: "think", "think hard", "ultrathink" protocols
- **4-Phase Execution Protocol**: EXPLORE (10%) → PLAN (20%) → EXECUTE (60%) → VALIDATE (10%)
- **3-Pass Iterative Refinement**: Broad Discovery (10%) → Filtered Targeting (30%) → Deep Detail (60%)
- **Token Budget Allocation**: Guidelines for different search complexity levels

**When to use**:
- Planning multi-database searches
- Need structured methodology
- Allocating token budgets
- Handling complex/uncertain queries

**Key sections**:
- Cognitive directives (when to invoke deep reasoning)
- Phase-by-phase execution workflow
- Iterative refinement protocol with success criteria
- Token budget examples (small/medium/large searches)

### search-workflows.md
**What it contains** (833 lines):
- Workflow 1: Comprehensive Drug Profile Search
- Workflow 2: Competitive Pipeline Analysis
- Workflow 3: KOL Identification and Mapping
- Workflow 4: Market Access Intelligence
- Workflow 5: Safety Signal Detection
- Workflow 6: Financial Impact Assessment
- Workflow 7: Patent Landscape Analysis
- Workflow 8: Clinical Trial Monitoring
- Workflow 9: Company Pipeline Intelligence
- Workflow 10: Indication Expansion Opportunities
- And many more specific workflow templates...

**When to use**:
- Need proven workflow template
- Starting similar search pattern
- Reference for query sequencing
- Learning best practices

**Key patterns**:
- Count-first strategies
- Sequential query dependencies
- Parallel execution opportunities
- Cross-validation checkpoints

### performance-optimization.md
**What it contains**:
- Universal optimization rules (count-first, field selection, date filtering)
- Token usage benchmarks (FDA 90% reduction, CT.gov 70%, etc.)
- Database-specific patterns
- Anti-patterns to avoid
- Query sequencing strategies
- Caching guidelines

**When to use**:
- Optimizing token costs
- Improving query speed
- Debugging slow queries
- Maximizing efficiency

**Key metrics**:
- FDA FAERS: 90% token reduction with counts
- ClinicalTrials: 70% reduction with field limits
- PubMed: 80% reduction with abstracts only
- SEC: 85% reduction with section targeting

### cross-database-integration.md
**What it contains**:
- Entity linking strategies (drugs, companies, diseases, investigators, geography)
- Timeline alignment patterns
- Data triangulation workflows
- Contradiction resolution protocols
- Entity relationship graph construction

**When to use**:
- Linking data across databases
- Validating findings
- Resolving contradictions
- Building comprehensive profiles

**Key mappings**:
- Drug: Brand → Generic → INN → ATC → NDC
- Company: Subsidiary → Parent → Ticker → CIK
- Disease: Clinical → ICD-10 → ICD-11 → MeSH
- Investigator: Name → ORCID → NPI → Institution

### quality-control.md
**What it contains**:
- Pre-search quality checks
- During-search monitoring
- Post-search validation
- Confidence level criteria
- Audit trail requirements
- Escalation protocols

**When to use**:
- Before delivering results
- Assessing data quality
- Assigning confidence levels
- Creating audit trails

**Confidence criteria**:
- **High (✅)**: 3+ sources, authoritative, recent, no contradictions
- **Medium (⚠️)**: 2 sources, some lag, minor inconsistencies
- **Low (❌)**: Single source, quality concerns, outdated
- **Unknown (🔍)**: No data or unresolved contradictions

## Usage Patterns by Role

### For Search Execution (Primary Use)
**You need**:
1. Tool-specific guides (parameter syntax)
2. Performance optimization (efficiency)
3. Quality control (validation)

**Workflow**:
```
Query Planning → Tool Guide → Optimize → Execute → Validate → Deliver
```

### For Strategic Planning (Secondary Use)
**You need**:
1. Search strategy protocols (methodology)
2. Search workflows (templates)
3. Cross-database integration (coordination)

**Workflow**:
```
Analyze Request → Select Protocol → Adapt Workflow → Sequence Queries → Integrate Results
```

### For Research/Learning (Tertiary Use)
**Read in order**:
1. README.md (this file - overview)
2. search-strategy-protocols.md (methodology)
3. Tool-specific guides (2-3 relevant databases)
4. search-workflows.md (examples)
5. performance-optimization.md (efficiency)
6. cross-database-integration.md (integration)
7. quality-control.md (standards)

## Common Scenarios

### Scenario 1: "Find FDA approval status for Drug X"
**Files needed**: `fda.md`, `performance-optimization.md`
**Protocol**: Simple, use count-first pattern
**Workflow**:
```
1. Check fda.md for lookup_drug syntax
2. Use count parameter (per performance-optimization.md)
3. Retrieve specific application details
4. Cross-reference with SEC filing (optional)
```

### Scenario 2: "Analyze competitive landscape for Indication Y"
**Files needed**: All tool guides, `search-strategy-protocols.md`, `search-workflows.md`, `cross-database-integration.md`
**Protocol**: Complex, use 4-phase + 3-pass
**Workflow**:
```
1. Read Workflow 2 in search-workflows.md (Competitive Pipeline Analysis)
2. Follow 4-phase protocol from search-strategy-protocols.md
3. Query CT.gov, PubMed, SEC (per tool guides)
4. Apply cross-database integration patterns
5. Validate per quality-control.md
```

### Scenario 3: "Identify KOLs for Drug Z"
**Files needed**: `pubmed.md`, `clinicaltrials.md`, `cross-database-integration.md`, `search-workflows.md`
**Protocol**: Moderate complexity
**Workflow**:
```
1. Read Workflow 3 in search-workflows.md (KOL Identification)
2. Query PubMed for authors (per pubmed.md)
3. Query CT.gov for PIs (per clinicaltrials.md)
4. Link investigators (per cross-database-integration.md)
5. Build network graph
```

## Best Practices

### DO ✅
- Always start with count queries for unknown result volumes
- Use field selection to reduce tokens by 70-90%
- Cross-validate key findings across 2+ sources
- Document confidence levels for all claims
- Follow established workflows for common scenarios
- Apply cognitive directives for novel queries
- Track token budgets and optimize

### DON'T ❌
- Execute full-text queries before understanding volume
- Request all fields when only a few are needed
- Trust single-source findings without validation
- Deliver results without confidence assessment
- Invent workflows when templates exist
- Skip thinking modes on complex queries
- Ignore token budget constraints

## Maintenance

### When to Update These Guides
- MCP server adds new methods/parameters
- Database schemas change significantly
- New optimization patterns discovered
- Workflow templates prove ineffective
- Quality issues emerge systematically

### How to Contribute Updates
1. Document specific issue or improvement
2. Test proposed change thoroughly
3. Update relevant guide file(s)
4. Add note to CHANGELOG section
5. Cross-reference with related guides

### Version Control
- All guides recovered from LSH commit 3e02457 (Oct 9, 2025)
- Current as of November 10, 2025
- Check git history for evolution
- See `TOOL_DOCUMENTATION_HISTORY.md` in LSH repo for full archaeological record

## Support & Questions

### For MCP Tool Issues
- Check tool-specific guide first
- Review common errors in quality-control.md
- Consult performance-optimization.md for efficiency issues

### For Workflow Design Questions
- Start with search-workflows.md for templates
- Apply search-strategy-protocols.md for methodology
- Use cross-database-integration.md for multi-source queries

### For Quality/Validation Concerns
- Follow quality-control.md checklists
- Apply confidence criteria rigorously
- Document contradictions and gaps

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE: When to Use Which Guide                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Need query syntax?              → Tool-specific guide       │
│ Need optimization tips?         → performance-optimization  │
│ Need workflow template?         → search-workflows          │
│ Need execution methodology?     → search-strategy-protocols │
│ Need entity linking?            → cross-database-integration│
│ Need quality validation?        → quality-control           │
│                                                              │
│ OPTIMIZATION PRIORITIES (apply in order):                   │
│ 1. Count-first (90% token savings)                          │
│ 2. Field selection (70-90% savings)                         │
│ 3. Date filtering (variable savings)                        │
│ 4. Status filtering (50%+ volume reduction)                 │
│                                                              │
│ QUALITY PRIORITIES (check before delivery):                 │
│ 1. Multi-source validation (2+ sources)                     │
│ 2. Confidence levels assigned (High/Med/Low)                │
│ 3. Contradictions resolved                                  │
│ 4. Data gaps documented                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## License & Attribution

These guides were originally developed in the LSH pharmaceutical intelligence project (commit 3e02457, Oct 9, 2025) and recovered for the agentic-os project on November 10, 2025. The content represents accumulated knowledge from pharmaceutical intelligence workflows and MCP database optimization experiments.
