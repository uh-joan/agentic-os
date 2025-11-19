# Strategic Agent Template

**Purpose**: Reusable template for creating new strategic agents with metadata-driven data collection

**Pattern**: Agent body focuses on capabilities (WHAT), metadata specifies data needs (HOW)

---

## Template Structure

```yaml
---
color: #HEX_COLOR
name: agent-name
description: Brief description for agent selection UI. Use PROACTIVELY for [key scenarios].
model: sonnet

# Data Requirements: Metadata-driven data collection
data_requirements:
  # Core data (always collected for this agent)
  always:
    - type: data_type_1
      pattern: get_{parameter}_data_source
      description: What this data provides
      sources: [mcp_server_name]

    - type: data_type_2
      pattern: get_{parameter}_other_source
      description: What this data provides
      sources: [mcp_server_name]

  # Contextual data (collected based on query context)
  contextual:
    - type: optional_data_1
      pattern: get_{parameter}_optional_source
      trigger: keywords("keyword1", "keyword2", "keyword3")
      description: What this optional data provides
      sources: [mcp_server_name]
      optional: true

    - type: optional_data_2
      pattern: get_{company}_company_specific
      trigger: company_name_in_query
      description: What this company-specific data provides
      sources: [mcp_server_name]
      optional: true

# Inference rules for parameter extraction from queries
inference_rules:
  parameter: Extract [what to extract] from query
  company: Extract company name if explicitly mentioned
  context_triggers: Analyze query for keywords indicating need for optional data sources
---

You are a [domain] expert specializing in [specific expertise areas].

## Purpose
[High-level purpose of this agent - what strategic value it provides]

## Capabilities

### Category 1
- Capability 1
- Capability 2
- Capability 3

### Category 2
- Capability 4
- Capability 5
- Capability 6

[... additional capability categories ...]

## Behavioral Traits
- Trait 1
- Trait 2
- Trait 3

## Knowledge Base
- Knowledge area 1
- Knowledge area 2
- Knowledge area 3

## Response Approach
1. **Step 1** - Description
2. **Step 2** - Description
3. **Step 3** - Description
[... additional steps ...]

## Example Interactions
- "Example query 1"
- "Example query 2"
- "Example query 3"

Focus on [key deliverables and approach].
```

---

## Examples for Different Agent Types

### Example 1: Clinical Development Strategist

```yaml
data_requirements:
  always:
    - type: trial_designs
      pattern: get_{disease}_trial_designs
      description: Trial design patterns and endpoints across disease area
      sources: [ct_gov_mcp]

    - type: regulatory_guidance
      pattern: get_{disease}_fda_guidance
      description: FDA guidance documents and regulatory precedents
      sources: [fda_mcp]

  contextual:
    - type: endpoints_analysis
      pattern: get_{disease}_endpoint_data
      trigger: keywords("endpoints", "outcomes", "biomarkers")
      description: Endpoint selection and validation data
      sources: [ct_gov_mcp, pubmed_mcp]
      optional: true

    - type: competitor_protocols
      pattern: get_{company}_protocols
      trigger: company_name_in_query
      description: Specific competitor protocol intelligence
      sources: [ct_gov_mcp]
      optional: true

inference_rules:
  disease: Extract disease/indication from query
  company: Extract company name if explicitly mentioned
  context_triggers: Analyze query for endpoint, regulatory, or protocol focus
```

### Example 2: Market Access Strategist

```yaml
data_requirements:
  always:
    - type: pricing_data
      pattern: get_{drug_class}_pricing
      description: Pricing data across drug class and competitors
      sources: [healthcare_mcp, sec_edgar_mcp]

    - type: reimbursement_landscape
      pattern: get_{country}_reimbursement
      description: Payer policies and coverage decisions
      sources: [healthcare_mcp]

  contextual:
    - type: health_economics
      pattern: get_{disease}_heor_data
      trigger: keywords("cost-effectiveness", "QALY", "ICER", "budget impact")
      description: Health economics and outcomes research data
      sources: [pubmed_mcp, who_mcp]
      optional: true

    - type: specific_payer
      pattern: get_{payer}_coverage_policies
      trigger: payer_name_in_query
      description: Specific payer coverage policies
      sources: [healthcare_mcp]
      optional: true

inference_rules:
  drug_class: Extract drug class/therapeutic area from query
  country: Extract country/region if mentioned, default to US
  payer: Extract payer name if explicitly mentioned
  context_triggers: Analyze query for health economics focus
```

### Example 3: Regulatory Strategy Analyst

```yaml
data_requirements:
  always:
    - type: approval_precedents
      pattern: get_{indication}_fda_approvals
      description: Historical approval decisions and precedents
      sources: [fda_mcp]

    - type: regulatory_pathway
      pattern: get_{indication}_pathway_data
      description: Available regulatory pathways and requirements
      sources: [fda_mcp, ct_gov_mcp]

  contextual:
    - type: advisory_committee
      pattern: get_{indication}_adcomm_history
      trigger: keywords("AdComm", "advisory committee", "panel")
      description: Advisory committee meeting history and decisions
      sources: [fda_mcp]
      optional: true

    - type: global_approvals
      pattern: get_{indication}_global_approvals
      trigger: keywords("EMA", "PMDA", "global", "international")
      description: International regulatory approvals and strategies
      sources: [fda_mcp]  # Could expand to EMA/PMDA servers
      optional: true

inference_rules:
  indication: Extract indication/drug class from query
  regulatory_region: Extract region if mentioned, default to FDA
  context_triggers: Analyze query for advisory committee or global focus
```

---

## Metadata Design Guidelines

### 1. Always Data (Core Requirements)

**When to include in `always`:**
- Data absolutely required for agent to provide value
- Data needed for 80%+ of queries
- Data that defines the agent's core function

**Typical size**: 2-4 core data types

**Example pattern**:
```yaml
always:
  - type: foundational_data
    pattern: get_{primary_parameter}_core_source
    sources: [primary_mcp_server]
```

### 2. Contextual Data (Optional)

**When to include in `contextual`:**
- Data that enhances analysis for specific query types
- Data triggered by keywords or entity mentions
- Data that's expensive/slow to collect

**Triggers**:
- `keywords("word1", "word2")` - Query contains specific terms
- `company_name_in_query` - Company entity detected
- `payer_name_in_query` - Payer entity detected
- `drug_name_in_query` - Drug entity detected

**Example pattern**:
```yaml
contextual:
  - type: enhancement_data
    pattern: get_{parameter}_optional_source
    trigger: keywords("specific", "focus", "area")
    optional: true
```

### 3. Skill Name Patterns

**Best practices**:
- Use `{parameter}` placeholders that will be extracted from query
- Common parameters: `{disease}`, `{drug_class}`, `{therapeutic_area}`, `{company}`, `{country}`
- Patterns should be specific enough to be unique
- Patterns should match actual skill naming conventions

**Examples**:
```yaml
# Good - specific and clear
pattern: get_{disease}_phase3_trials

# Good - multiple parameters
pattern: get_{company}_{therapeutic_area}_pipeline

# Avoid - too vague
pattern: get_{thing}_data
```

### 4. Data Source Specification

**Format**: `sources: [server1_mcp, server2_mcp]`

**Available MCP servers**:
- `ct_gov_mcp` - ClinicalTrials.gov
- `fda_mcp` - FDA data
- `pubmed_mcp` - PubMed literature
- `sec_edgar_mcp` - SEC filings
- `healthcare_mcp` - CMS Medicare data
- `nlm_codes_mcp` - Medical coding
- `who_mcp` - WHO health statistics
- `uspto_patents_mcp` - Patent data
- `opentargets_mcp` - Target validation
- `pubchem_mcp` - Chemical data
- `financials_mcp` - Financial data
- `datacommons_mcp` - Population statistics

### 5. Inference Rules

**Purpose**: Guide main agent on how to extract parameters from queries

**Format**:
```yaml
inference_rules:
  parameter_name: How to extract this parameter
```

**Examples**:
```yaml
inference_rules:
  therapeutic_area: Extract disease/drug class/mechanism from query
  company: Extract company name if explicitly mentioned
  phase: Extract clinical phase if specified, otherwise infer from context
  geography: Extract country/region if mentioned, default to US
```

---

## Agent Body Guidelines

### 1. Keep Body Pristine

**DO**:
- Focus on capabilities and expertise
- Describe analysis methods and frameworks
- Specify behavioral traits and approach
- Provide example interactions

**DON'T**:
- Reference specific data collection methods
- Hardcode skill names or data sources
- Mix data requirements with capabilities

### 2. Capability Organization

**Recommended structure**:
```markdown
## Capabilities

### Domain Knowledge Category 1
- Specific capability
- Related capability
- Advanced capability

### Technical Skills Category
- Analytical method
- Framework application
- Tool usage

### Strategic Capabilities
- Synthesis ability
- Recommendation generation
- Decision support
```

**Target**: 80-120+ capabilities across 8-12 categories

### 3. Behavioral Traits

**Define how agent operates**:
- Decision-making approach
- Communication style
- Risk tolerance
- Objectivity vs. advocacy
- Proactive vs. reactive

### 4. Response Approach

**Provide step-by-step methodology**:
1. Assessment step
2. Analysis step
3. Synthesis step
4. Recommendation step
5. Communication step

---

## Checklist for New Strategic Agents

- [ ] Choose descriptive `name` following `[domain]-[specialty]-[role]` pattern
- [ ] Write compelling `description` for agent selection (mention proactive use cases)
- [ ] Define 2-4 `always` data requirements (core data)
- [ ] Define 0-4 `contextual` data requirements (optional enhancements)
- [ ] Create skill name `pattern`s with clear `{parameter}` placeholders
- [ ] Specify correct `sources` (MCP server names)
- [ ] Write `inference_rules` for all parameters used in patterns
- [ ] Write agent body with 80-120+ capabilities
- [ ] Organize capabilities into 8-12 logical categories
- [ ] Define behavioral traits and response approach
- [ ] Include 6-8 example interactions
- [ ] Test metadata extraction with sample queries
- [ ] Verify skill naming patterns match pharma-search-specialist conventions

---

## Common Patterns

### Pattern: Company-Specific Analysis
```yaml
contextual:
  - type: company_pipeline
    pattern: get_{company}_{therapeutic_area}_pipeline
    trigger: company_name_in_query
```

### Pattern: Geographic Scope
```yaml
inference_rules:
  geography: Extract country/region if mentioned, default to US

always:
  - type: regional_data
    pattern: get_{geography}_{data_type}
    sources: [relevant_mcp]
```

### Pattern: Multi-Source Data
```yaml
always:
  - type: comprehensive_analysis
    pattern: get_{therapeutic_area}_landscape
    description: Combines trial, approval, and market data
    sources: [ct_gov_mcp, fda_mcp, healthcare_mcp]
```

### Pattern: Tiered Detail
```yaml
always:
  - type: overview_data
    pattern: get_{area}_overview

contextual:
  - type: deep_dive_data
    pattern: get_{area}_detailed_analysis
    trigger: keywords("detailed", "comprehensive", "deep dive")
```

---

## Testing Your Agent

### 1. Metadata Validation
- Can main agent parse YAML?
- Are all `{parameters}` defined in `inference_rules`?
- Do `sources` reference valid MCP servers?

### 2. Query Testing
Create test queries covering:
- Core always-data scenario
- Each contextual trigger
- Multi-parameter inference
- Edge cases (missing parameters)

**Example test set**:
```
# Core data only
"Analyze [therapeutic_area] landscape"

# Company trigger
"Analyze [company]'s pipeline in [therapeutic_area]"

# Keyword trigger
"Analyze [therapeutic_area] with detailed [keyword] analysis"

# Multi-trigger
"Analyze [company]'s [therapeutic_area] pipeline including [keyword1] and [keyword2]"
```

### 3. Skill Pattern Testing
- Do generated skill names match pharma-search-specialist conventions?
- Are skill names unique and descriptive?
- Do patterns adapt to different parameters?

---

## Maintenance

### When to Update Metadata

**Add to `always`**:
- New core data source becomes foundational
- Agent cannot provide value without it

**Add to `contextual`**:
- New optional enhancement identified
- New keyword trigger pattern emerges

**Update `patterns`**:
- Skill naming conventions change
- New parameter types needed

**Update `inference_rules`**:
- New parameter extraction logic needed
- Edge cases discovered

### Agent Body Updates

Agent body can evolve independently:
- Add new capabilities without metadata changes (if using same data sources)
- Refine behavioral traits
- Expand example interactions
- Improve response approach

**Rule**: Only update metadata when data requirements change, not when capabilities expand.

---

## Summary

**Metadata-driven pattern enables**:
- ✅ Small metadata footprint (~25 lines)
- ✅ Large capability set (100+ items)
- ✅ Generic main agent orchestration
- ✅ Smart parameter inference
- ✅ Contextual data collection
- ✅ Agent body stays pristine
- ✅ Reusable template for all strategic agents

**Key insight**: Capabilities ≠ Data Requirements

An agent with 100 capabilities might only need 6 data sources because capabilities describe HOW to analyze (methods, frameworks, synthesis), while data requirements specify WHAT raw data is needed (sources, APIs).
