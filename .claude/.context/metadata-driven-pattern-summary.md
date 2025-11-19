# Metadata-Driven Pattern - Summary

**Created**: 2025-01-18
**Pattern**: Metadata in agent YAML drives data collection, agent body stays pristine

---

## Core Insight

**Capabilities ≠ Data Requirements**

An agent can have 100+ capabilities but only need 4-6 core data sources:
- **Capabilities** = HOW the agent analyzes (methods, frameworks, synthesis techniques)
- **Data Requirements** = WHAT raw data the agent needs (sources, APIs)

### Example: competitive-landscape-analyst

**100+ Capabilities** including:
- Pipeline Intelligence & Tracking
- Clinical Trial Monitoring
- Financial & Investment Analysis
- Strategic Intelligence Synthesis
- Analytical Frameworks & Modeling
- Reporting & Communication
- Technology & Automation Tools
- Therapeutic Area Specialization
- Partnership & Deal Intelligence
- Risk Assessment & Early Warning
- Action Planning & Recommendations
- Behavioral Traits

**But Only 6 Core Data Types:**
1. Clinical trials (ClinicalTrials.gov)
2. FDA approved drugs
3. Company financials (SEC)
4. Patents (USPTO)
5. Publications (PubMed)
6. Partnership deals

---

## Metadata Structure

### Minimal Footprint (~25 lines)

```yaml
---
name: agent-name
data_requirements:
  always:  # Core data always collected
    - type: clinical_trials
      pattern: get_{therapeutic_area}_trials
      sources: [ct_gov_mcp]

    - type: approved_drugs
      pattern: get_{therapeutic_area}_fda_drugs
      sources: [fda_mcp]

  contextual:  # Optional data based on query
    - type: company_pipeline
      pattern: get_{company}_trials
      trigger: company_name_in_query
      sources: [ct_gov_mcp]

    - type: patents
      pattern: get_{therapeutic_area}_patents
      trigger: keywords("IP", "patent")
      sources: [uspto_patents_mcp]
      optional: true

inference_rules:
  therapeutic_area: Extract from query
  company: Extract if mentioned
  context_triggers: Analyze keywords
---
```

---

## Main Agent Logic (Generic)

Works for ANY strategic agent with metadata:

```python
def invoke_strategic_agent(agent_name, user_query):
    # 1. Read agent metadata
    metadata = read_yaml(f".claude/agents/{agent_name}.md")

    # 2. Infer parameters from query
    params = {
        'therapeutic_area': extract_therapeutic_area(user_query),
        'company': extract_company(user_query) if present else None
    }

    # 3. Collect always-required data
    data = {}
    for req in metadata['data_requirements']['always']:
        skill_name = req['pattern'].format(**params)
        data[req['type']] = get_or_create_and_execute_skill(skill_name)

    # 4. Collect contextual data (if triggered)
    for req in metadata['data_requirements']['contextual']:
        if should_trigger(req['trigger'], user_query, params):
            skill_name = req['pattern'].format(**params)
            data[req['type']] = get_or_create_and_execute_skill(skill_name)

    # 5. Invoke agent with data
    prompt = format_prompt_with_data(user_query, data)
    return Task(agent_name, prompt)
```

---

## Query Examples

### Query 1: "Analyze KRAS inhibitor competitive landscape"

**Inference**:
- therapeutic_area = "KRAS inhibitor"
- company = None
- keywords = []

**Skills determined**:
- ✓ get_kras_inhibitor_trials (always)
- ✓ get_kras_inhibitor_fda_drugs (always)
- ✗ Patents (no trigger)
- ✗ Financials (no trigger)

**Result**: 2 skills executed

---

### Query 2: "Analyze Pfizer's oncology pipeline with IP assessment"

**Inference**:
- therapeutic_area = "oncology"
- company = "Pfizer"
- keywords = ["IP"]

**Skills determined**:
- ✓ get_oncology_trials (always)
- ✓ get_oncology_fda_drugs (always)
- ✓ get_pfizer_trials (company triggered)
- ✓ get_oncology_patents (keyword "IP" triggered)
- ✗ Publications (no trigger)

**Result**: 4 skills executed

---

### Query 3: "What's the competitive landscape for GLP-1 obesity drugs including recent clinical publications?"

**Inference**:
- therapeutic_area = "GLP-1 obesity"
- company = None
- keywords = ["publications"]

**Skills determined**:
- ✓ get_glp1_obesity_trials (always)
- ✓ get_glp1_obesity_fda_drugs (always)
- ✓ get_glp1_obesity_pubmed (keyword "publications" triggered)
- ✗ Patents (no trigger)
- ✗ Financials (no trigger)

**Result**: 3 skills executed

---

## Benefits

### 🎯 Minimal Metadata
- 6 data sources support 100+ capabilities
- ~25 lines of YAML
- Easy to maintain

### 🧠 Smart Inference
- Same pattern, different parameters
- `get_{therapeutic_area}_trials` adapts to any query
- Contextual triggers add precision

### 🏗️ Agent Body Pristine
- No changes to capability descriptions
- Metadata separate from domain expertise
- Agent focuses on WHAT it can do, not HOW data is collected

### ⚡ Main Agent Generic
- Same logic works for all strategic agents
- No agent-specific code
- Read metadata → Infer → Collect → Invoke

### 🔄 Extensible
- Add new data sources = add to metadata
- Add new strategic agent = copy metadata template
- Add new capabilities = no metadata change needed (if using same data)

---

## Pattern vs. Alternatives

### ❌ Hardcoded Mappings
```python
# BAD: Agent-specific logic in main agent
if agent == "competitive-landscape-analyst":
    if "KRAS" in query:
        skills = ["get_kras_trials", "get_kras_drugs"]
```

### ❌ Agent Self-Discovery
```python
# BAD: Agent tells main agent what to do (violates sub-agent constraints)
agent.response = "I need get_kras_trials and get_kras_drugs"
```

### ✅ Metadata-Driven
```yaml
# GOOD: Declarative, generic, maintainable
data_requirements:
  always:
    - pattern: get_{therapeutic_area}_trials
```

---

## Implementation Checklist

- [ ] Add metadata to competitive-landscape-analyst.md (YAML only)
- [ ] Update CLAUDE.md with metadata-driven pattern documentation
- [ ] Main agent implements metadata reading logic
- [ ] Main agent implements parameter inference
- [ ] Main agent implements skill name pattern application
- [ ] Main agent implements contextual trigger evaluation
- [ ] Test with existing skills (fast path)
- [ ] Test with missing skills (creation path)
- [ ] Test with contextual triggers (optional data)
- [ ] Document pattern for future strategic agents

---

## Future Strategic Agents

Each new agent just needs metadata:

```yaml
# clinical-development-strategist.md
data_requirements:
  always:
    - pattern: get_{disease}_trial_designs
    - pattern: get_{disease}_endpoints
  contextual:
    - pattern: get_{disease}_regulatory_guidance
      trigger: keywords("regulatory", "FDA")

# market-access-strategist.md
data_requirements:
  always:
    - pattern: get_{drug_class}_pricing
    - pattern: get_{country}_reimbursement
  contextual:
    - pattern: get_{drug}_payer_coverage
      trigger: drug_name_in_query
```

Same main agent logic handles all of them!
