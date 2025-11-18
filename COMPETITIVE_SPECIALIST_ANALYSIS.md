# Competitive-Specialist Analysis & Recommendations

## Q1: Frontmatter Format ❌ NEEDS FIX

**Current competitive-specialist.md** (INCORRECT):
```markdown
# competitive-specialist

**Role**: Code-Generating Competitive Intelligence Analyst
```

**pharma-search-specialist.md** (CORRECT):
```markdown
---
color: blue
name: pharma-search-specialist
description: Pharmaceutical search specialist - generates Python code for MCP queries
model: sonnet
tools:
  - Read
---

# pharma-search-specialist
```

**competitive-analyst.md** (CORRECT):
```markdown
---
color: emerald
name: competitive-analyst
description: Pharmaceutical competitive intelligence analyst - Use PROACTIVELY for competitive landscape mapping, pipeline threat assessment, market leader analysis
model: sonnet
tools:
  - Read
---

# Pharmaceutical Competitive Intelligence Analyst
```

### ❌ PROBLEM: competitive-specialist.md is missing frontmatter entirely

**Recommended Fix**:
```markdown
---
color: purple
name: competitive-specialist
description: Code-generating competitive analyst - generates Python scripts for competitive landscape analysis
model: sonnet
tools:
  - Read
---

# competitive-specialist

**Role**: Code-Generating Competitive Intelligence Analyst
[rest of content...]
```

**Why purple?** Distinguish from:
- blue (pharma-search-specialist - general data gathering)
- emerald (competitive-analyst - read-only analytical)
- Purple signals "code-generating specialist" tier

---

## Q2: Sub-Agent Decomposition ✅ YES - Multiple Opportunities

### Current Monolithic Structure

**competitive-specialist** currently covers:
1. ✅ Market structure analysis
2. ✅ Pipeline dynamics analysis (Phase 2/3)
3. ✅ Genetic biomarker competitive intelligence
4. ✅ Competitive timeline mapping
5. ✅ Competitive gaps analysis (white space, crowded segments)
6. ✅ Threat scoring (5-component rubric)
7. ✅ Differentiation deep dive (MOA, dosing, indication, safety)
8. ✅ Sponsor competitive strength assessment
9. ✅ Regulatory pathway context
10. ✅ Market sizing integration

### Proposed Sub-Agent Architecture

```
competitive-specialist (orchestrator)
├── pipeline-analyst (Phase 2/3 dynamics)
├── market-structure-analyst (current leaders, moats, concentration)
├── genetic-biomarker-analyst (precision medicine competitive intelligence)
├── threat-scorer (5-component rubric, approval probability)
├── differentiation-analyst (MOA, dosing, indication, safety)
└── gaps-analyst (white space, crowded segments, unmet needs)
```

### Detailed Sub-Agent Specifications

---

#### **1. pipeline-analyst** (Code-Generating)

**Scope**: Phase 2/3 program analysis, trial dynamics, enrollment tracking

**Atomic Functions** (new module: `scripts/analysis/modules/pipeline.py`):
```python
def assess_trial_phase_risk(phase: str) -> tuple[str, str, int]
def calculate_enrollment_velocity(target: int, enrolled: int, months_open: int) -> float
def estimate_completion_date(phase: str, enrolled: int, target: int, velocity: float) -> str
def score_trial_execution(enrollment_pct: float, sponsor_strength: int) -> tuple[float, str]
def calculate_phase_transition_probability(phase: str, moa_validated: bool, sponsor_strength: int) -> float
```

**Generated Script Output**:
- Phase 2 pipeline (count, MOAs, sponsors, timelines)
- Phase 3 pipeline (count, MOAs, sponsors, timelines)
- Enrollment velocity analysis
- Phase transition risk assessment
- Trial completion forecasts

**Example Query**: "Analyze Phase 2/3 pipeline for obesity"

---

#### **2. market-structure-analyst** (Code-Generating)

**Scope**: Current market leaders, competitive moats, market concentration, vulnerabilities

**Atomic Functions** (new module: `scripts/analysis/modules/market_structure.py`):
```python
def assess_market_concentration(competitors: list[dict]) -> tuple[str, str]
def score_competitive_moat(patent_years: int, differentiation: int, payer_access: int) -> tuple[float, str]
def identify_vulnerabilities(patent_expiry: str, safety_issues: bool, dosing_burden: int) -> list[str]
def calculate_market_share_stability(years_in_market: int, moat_score: float) -> str
def assess_switching_barriers(moat_type: str, payer_coverage: str) -> int
```

**Generated Script Output**:
- Market leader profiles (approval date, sales, market share)
- Competitive moat assessment (patent, clinical, payer, prescribing inertia)
- Market concentration analysis (monopoly/oligopoly/fragmented)
- Vulnerability identification (patent cliff, safety, convenience)

**Example Query**: "Analyze current obesity market structure"

---

#### **3. genetic-biomarker-analyst** (Code-Generating)

**Scope**: Precision medicine competitive intelligence, genetic patient selection, companion diagnostics

**Atomic Functions** (new module: `scripts/analysis/modules/genetic_biomarker.py`):
```python
def assess_genetic_enrichment_strategy(trial_design: str, biomarker: str) -> tuple[str, int]
def calculate_addressable_market_impact(total_prevalence: int, genetic_subset_pct: float) -> int
def score_companion_diagnostic_moat(cdx_required: bool, patent_term: int) -> tuple[float, str]
def identify_genetic_white_space(competitors: list[dict], mutations: list[str]) -> list[str]
def assess_precision_medicine_threat(genetic_enrichment: bool, phase: str, cdx: bool) -> str
```

**Generated Script Output**:
- Competitor genetic strategies (enrichment, CDx, all-comers)
- Genetic market segmentation (mutation-specific prevalence, crowding)
- Genetic white space opportunities (unaddressed mutations)
- Precision medicine threat assessment (high/moderate/low)
- HLA-defined market segments (when applicable)

**Example Query**: "Analyze genetic biomarker strategies in NSCLC competitive landscape"

**Data Sources**: OpenTargets MCP, ClinicalTrials.gov trial designs, PubMed genetic studies

---

#### **4. threat-scorer** (Code-Generating)

**Scope**: 5-component threat rubric, approval probability, launch timeline forecasting

**Atomic Functions** (already in `competitive.py`, expand):
```python
def score_threat_level(phase, sponsor_strength, differentiation, market_timing, genetic_precision) -> tuple[float, str]
def calculate_approval_probability(base_rate, sponsor_strength, validated_moa, genetic_precision) -> float
def assess_threat_timeline(phase: str) -> tuple[str, str]
def calculate_nda_submission_date(trial_completion: str, phase: str) -> str
def estimate_launch_date(nda_submission: str, priority_review: bool, breakthrough: bool) -> str
```

**Generated Script Output**:
- Threat scores for all Phase 2/3 programs (1-10 scale)
- 🔴 HIGH / 🟡 MODERATE / 🟢 LOW threat categorization
- Approval probability adjustments (sponsor, MOA, genetic precision)
- Launch timeline forecasts (trial completion → NDA → approval → launch)

**Example Query**: "Score competitive threats for obesity pipeline programs"

---

#### **5. differentiation-analyst** (Code-Generating)

**Scope**: MOA innovation, dosing/convenience, indication breadth, safety profiles

**Atomic Functions** (new module: `scripts/analysis/modules/differentiation.py`):
```python
def assess_moa_innovation(moa: str, precedent_exists: bool) -> str  # First-in-class, Best-in-class, Me-too
def score_patient_convenience(frequency: str, fasting: bool, route: str) -> tuple[int, str]
def calculate_indication_breadth_score(indications: list[str]) -> int
def assess_safety_differentiation(black_box: bool, discontinuation_rate: float, common_aes: list) -> tuple[int, str]
def calculate_differentiation_index(moa_score, convenience_score, breadth_score, safety_score) -> tuple[float, str]
```

**Generated Script Output**:
- MOA innovation spectrum (first-in-class, best-in-class, me-too)
- Patient convenience analysis (QD vs BID, fasting, administration)
- Indication breadth comparison matrix
- Safety profile differentiation (AEs, discontinuation, black box)
- Overall differentiation index

**Example Query**: "Analyze differentiation strategies in obesity pipeline"

---

#### **6. gaps-analyst** (Code-Generating)

**Scope**: White space identification, crowded segments, unmet needs

**Atomic Functions** (new module: `scripts/analysis/modules/gaps.py`):
```python
def identify_crowded_segments(competitors: list[dict], threshold: int = 5) -> list[dict]
def identify_white_space(unmet_needs: list[str], competitor_coverage: dict) -> list[dict]
def assess_segment_saturation(competitor_count: int, differentiation_erosion: bool) -> str
def score_opportunity_level(gap_type: str, competitor_count: int, unmet_need_severity: int) -> tuple[int, str]
def map_competitive_gaps(current_market: dict, pipeline: dict, unmet_needs: list) -> dict
```

**Generated Script Output**:
- Crowded segments (5+ competitors, price pressure evidence)
- White space opportunities (0-2 competitors, unmet needs)
- Efficacy gaps (no oral GLP-1 with obesity indication)
- Safety gaps (high AE burden, CV risk)
- Convenience gaps (fasting requirement, BID dosing)
- Genetic precision gaps (underserved mutations)
- Population gaps (pediatric, renal impairment)

**Example Query**: "Identify white space and crowded segments in diabetes market"

---

### Sub-Agent Orchestration Pattern

**Option A: Full Orchestrator** (competitive-specialist runs all sub-agents)
```python
# competitive-specialist generates orchestrator script
from analysis.modules.pipeline import assess_trial_phase_risk, calculate_enrollment_velocity
from analysis.modules.market_structure import assess_market_concentration, score_competitive_moat
from analysis.modules.genetic_biomarker import assess_genetic_enrichment_strategy
from analysis.modules.differentiation import assess_moa_innovation, score_patient_convenience
from analysis.modules.gaps import identify_white_space, identify_crowded_segments

def main():
    # Phase 1: Market Structure
    leaders = analyze_market_leaders()
    concentration = assess_market_concentration(leaders)

    # Phase 2: Pipeline Dynamics
    phase3_programs = analyze_phase3_pipeline()
    phase2_programs = analyze_phase2_pipeline()

    # Phase 3: Genetic Biomarker Analysis
    genetic_strategies = analyze_genetic_strategies()

    # Phase 4: Threat Scoring
    threats = score_all_threats(phase3_programs, phase2_programs)

    # Phase 5: Differentiation
    differentiation = analyze_differentiation(phase3_programs)

    # Phase 6: Gaps Analysis
    white_space = identify_white_space()
    crowded_segments = identify_crowded_segments()

    # Generate comprehensive report
    print_competitive_landscape_report()
```

**Option B: Modular Specialists** (invoke individually, compose manually)
```bash
# User can invoke specific sub-agents
python3 scripts/analysis/obesity/pipeline_dynamics.py
python3 scripts/analysis/obesity/market_structure.py
python3 scripts/analysis/obesity/genetic_biomarker_landscape.py
python3 scripts/analysis/obesity/threat_assessment.py
python3 scripts/analysis/obesity/differentiation_analysis.py
python3 scripts/analysis/obesity/gaps_analysis.py
```

**Recommendation: Hybrid Approach**
- **competitive-specialist** = Full orchestrator (generates comprehensive analysis)
- **Individual sub-agents** = Available for focused queries (pipeline-analyst, gaps-analyst, etc.)
- **Atomic functions** = Reusable across all agents (in modules/)

---

## Q3: Coverage Verification ✅ ALL CAPABILITIES COVERED

### Comprehensive Capability Mapping

| competitive-analyst.md Capability | competitive-specialist Coverage | Status |
|-----------------------------------|--------------------------------|--------|
| **1. Input Validation** | ❌ NOT IMPLEMENTED | 🟡 MISSING |
| **2. Current Market Structure Analysis** | ✅ Partially (via atomic functions) | 🟢 COVERED |
| **3. Pipeline Dynamics Analysis** | ✅ Phase distribution, sponsor breakdown | 🟢 COVERED |
| **4. Genetic Biomarker Competitive Intelligence** | ❌ NOT IMPLEMENTED | 🔴 **CRITICAL GAP** |
| **5. Competitive Timeline Mapping** | ✅ Via threat assessment | 🟢 COVERED |
| **6. Competitive Gaps Analysis** | ❌ NOT IMPLEMENTED | 🟡 MISSING |
| **7. Market Sizing Integration** | ❌ NOT IMPLEMENTED | 🟡 MISSING |
| **8. Regulatory Pathway Context** | ❌ NOT IMPLEMENTED | 🟡 MISSING |
| **9. Sponsor Competitive Strength** | ✅ Via sponsor breakdown | 🟢 COVERED |
| **10. Differentiation Deep Dive** | ❌ NOT IMPLEMENTED | 🟡 MISSING |
| **11. MCP Tool Coverage Summary** | ✅ Uses ct-gov-mcp | 🟢 COVERED |
| **12. Integration with Downstream Agents** | ❌ NOT DOCUMENTED | 🟡 MISSING |
| **13. Output Format** | ✅ Structured 7-section output | 🟢 COVERED |
| **14. Quality Control Checklist** | ❌ NOT IMPLEMENTED | 🟡 MISSING |

### Detailed Gap Analysis

---

#### 🔴 **CRITICAL GAP: Genetic Biomarker Competitive Intelligence**

**competitive-analyst.md Section 4** (163 lines, ~25% of total content):
- Genetic enrichment strategies (EGFR-mutant, HLA-B27+, all-comers)
- Companion diagnostic assessment (FDA-approved test, optional biomarker)
- Genetic market segmentation template
- Genetic white space opportunities
- HLA-defined market segmentation (HLA-B27+ AS, HLA-C*06:02+ psoriasis)
- Polygenic risk stratification
- Precision medicine threat scoring rubric

**Current competitive-specialist Coverage**: ❌ ZERO

**Impact**: This is 25% of competitive-analyst.md content and represents the most advanced competitive intelligence capability.

**Required Atomic Functions** (new module: `scripts/analysis/modules/genetic_biomarker.py`):
```python
def assess_genetic_enrichment_strategy(trial_design: str, biomarker: str) -> tuple[str, int]
def calculate_addressable_market_impact(total_prevalence: int, genetic_subset_pct: float) -> int
def score_companion_diagnostic_moat(cdx_required: bool, patent_term: int) -> tuple[float, str]
def identify_genetic_white_space(competitors: list[dict], mutations: list[str]) -> list[str]
def assess_precision_medicine_threat(genetic_enrichment: bool, phase: str, cdx: bool) -> str
def analyze_hla_market_segmentation(indication: str, hla_alleles: list[str]) -> dict
def calculate_polygenic_risk_impact(prs_threshold: float, population_pct: float) -> dict
```

**Required MCP Queries** (new module: `scripts/mcp/queries/opentargets.py`):
```python
def get_target_disease_associations(target_id: str, disease_id: str) -> dict
def search_genetic_variants(disease: str) -> list[dict]
def get_genetic_evidence_scores(gene: str, disease: str) -> dict
```

**Recommendation**: Build `genetic-biomarker-analyst` sub-agent as **priority** (highest differentiation value)

---

#### 🟡 **MISSING: Input Validation**

**competitive-analyst.md Section 1**:
- Required data sources checklist (FDA, CT.gov, PubMed)
- Optional enhancement data (Market sizing, OpenTargets, SEC)
- Validation criteria (recency <6 months, completeness ≥3 competitors, file existence)
- Error handling ("STALE DATA", "LIMITED INTELLIGENCE", "Missing required data_dump/")

**Current competitive-specialist Coverage**: ❌ NOT IMPLEMENTED

**Impact**: Low (generated scripts assume data availability)

**Recommendation**: Add validation functions to `scripts/analysis/modules/validation.py`:
```python
def validate_data_sources(required: list[str], optional: list[str]) -> tuple[bool, list[str]]
def check_data_recency(data_dump_path: str, max_age_months: int = 6) -> bool
def assess_data_completeness(competitors: list[dict], min_count: int = 3) -> tuple[bool, str]
```

**Priority**: LOW (nice-to-have, not critical for MVP)

---

#### 🟡 **MISSING: Competitive Gaps Analysis**

**competitive-analyst.md Section 6**:
- Unmet needs identification (efficacy, safety, convenience, genetic precision, population gaps)
- Crowded segments assessment (5+ competitors, price pressure, me-too saturation)
- White space opportunities (low competition, underserved, entry strategy)

**Current competitive-specialist Coverage**: ❌ NOT IMPLEMENTED (but `competitive_landscape.py` has manual logic)

**Impact**: MODERATE (critical for strategic decision-making)

**Required Atomic Functions** (new module: `scripts/analysis/modules/gaps.py`):
```python
def identify_unmet_needs(category: str, current_market: dict, pipeline: dict) -> list[dict]
def assess_segment_crowding(competitor_count: int, price_pressure: bool) -> tuple[str, str]
def identify_white_space(market: dict, pipeline: dict, unmet_needs: list) -> list[dict]
def score_opportunity_level(gap_type: str, competition: int, need_severity: int) -> tuple[int, str]
```

**Recommendation**: Build `gaps-analyst` sub-agent (MEDIUM priority)

---

#### 🟡 **MISSING: Differentiation Deep Dive**

**competitive-analyst.md Section 10**:
- MOA differentiation (first-in-class, best-in-class, me-too)
- Dosing & convenience (QD vs BID, fasting, patient preference hierarchy)
- Indication breadth (T2D, obesity, NASH, CKD, CV outcomes)
- Safety profile (black box, discontinuation rate, AE burden)

**Current competitive-specialist Coverage**: ❌ NOT IMPLEMENTED

**Impact**: MODERATE (important for positioning analysis)

**Required Atomic Functions** (new module: `scripts/analysis/modules/differentiation.py`):
```python
def assess_moa_innovation(moa: str, precedent_exists: bool) -> str
def score_patient_convenience(frequency: str, fasting: bool, route: str) -> tuple[int, str]
def calculate_indication_breadth_score(indications: list[str]) -> int
def assess_safety_differentiation(black_box, discontinuation_rate, common_aes) -> tuple[int, str]
```

**Recommendation**: Build `differentiation-analyst` sub-agent (MEDIUM priority)

---

#### 🟡 **MISSING: Regulatory Pathway Context**

**competitive-analyst.md Section 8**:
- Standard approval timelines (NDA, Priority Review, Accelerated, Breakthrough)
- Phase success rates (Phase 1→2: 63%, Phase 2→3: 31%, Phase 3→Approval: 58%)
- Approval probability adjustments (+10% top pharma, +5% validated MOA, +15% genetic precision)

**Current competitive-specialist Coverage**: ✅ **PARTIALLY** (via `calculate_approval_probability()` in competitive.py)

**Impact**: LOW (already have core function)

**Recommendation**: Document existing function, add to generated script template

---

#### 🟡 **MISSING: Market Sizing Integration**

**competitive-analyst.md Section 7**:
- Read `temp/market_sizing_*.md` if available
- Extract TAM/SAM/SOM
- Integrate into competitive implications

**Current competitive-specialist Coverage**: ❌ NOT IMPLEMENTED

**Impact**: LOW (separate agent responsibility - market-sizing-analyst)

**Recommendation**: Add optional integration logic to orchestrator script:
```python
if market_sizing_available:
    read_and_integrate_market_sizing()
else:
    print("Note: For detailed market sizing (TAM/SAM/SOM), see market-sizing-analyst output")
```

**Priority**: LOW (cross-agent integration, not core capability)

---

#### 🟡 **MISSING: Integration with Downstream Agents**

**competitive-analyst.md Section 12**:
- Data handoff to opportunity-identifier (gaps → white space, crowded → avoid)
- Data handoff to strategy-synthesizer (threats → defensive strategies, timeline → strategic timing)

**Current competitive-specialist Coverage**: ❌ NOT DOCUMENTED

**Impact**: LOW (architectural documentation, not code)

**Recommendation**: Document in `.claude/CLAUDE.md` under multi-agent workflows

**Priority**: LOW (documentation task)

---

#### 🟡 **MISSING: Quality Control Checklist**

**competitive-analyst.md Section 14**:
- Data validation checklist (data_dump/ folders, FDA, CT.gov, OpenTargets)
- Market structure analysis checklist (leaders, moats, vulnerabilities)
- Pipeline analysis checklist (Phase 3/2 profiling, differentiation matrix)
- Genetic biomarker analysis checklist (strategies, segmentation, opportunities, threat assessment)
- Threat assessment checklist (consistent scoring, justification, timeline mapping)
- Gaps analysis checklist (unmet needs, crowded segments, white space)
- Strategic clarity checklist (defensive, offensive, partnership/acquisition)

**Current competitive-specialist Coverage**: ❌ NOT IMPLEMENTED

**Impact**: LOW (quality assurance process, not code logic)

**Recommendation**: Add verification section to generated script template:
```python
def verify_analysis_completeness():
    """Verify all required sections are complete"""
    checks = {
        'market_overview': True,
        'pipeline_dynamics': True,
        'threat_assessment': True,
        'gaps_analysis': False  # Not implemented
    }
    return all(checks.values())
```

**Priority**: LOW (QA process, add incrementally)

---

### Missing Capabilities Summary

| Priority | Capability | Lines in competitive-analyst.md | Impact | Recommendation |
|----------|-----------|--------------------------------|--------|----------------|
| 🔴 **HIGH** | **Genetic Biomarker Intelligence** | ~163 lines (25%) | **CRITICAL** | Build `genetic-biomarker-analyst` sub-agent + atomic functions |
| 🟡 MEDIUM | Competitive Gaps Analysis | ~50 lines | MODERATE | Build `gaps-analyst` sub-agent + atomic functions |
| 🟡 MEDIUM | Differentiation Deep Dive | ~40 lines | MODERATE | Build `differentiation-analyst` sub-agent + atomic functions |
| 🟢 LOW | Input Validation | ~30 lines | LOW | Add validation functions to `scripts/analysis/modules/validation.py` |
| 🟢 LOW | Regulatory Pathway Context | ~20 lines | LOW | Document existing `calculate_approval_probability()` function |
| 🟢 LOW | Market Sizing Integration | ~15 lines | LOW | Add optional integration logic to orchestrator |
| 🟢 LOW | Downstream Agent Integration | ~20 lines | LOW | Document in `.claude/CLAUDE.md` |
| 🟢 LOW | Quality Control Checklist | ~50 lines | LOW | Add verification function to generated scripts |

**Total Coverage**: ~55% of competitive-analyst.md capabilities implemented

---

## Recommendations

### Immediate Actions

1. **FIX: Add frontmatter to competitive-specialist.md** ⚡ 5 minutes
   ```markdown
   ---
   color: purple
   name: competitive-specialist
   description: Code-generating competitive analyst - generates Python scripts for competitive landscape analysis
   model: sonnet
   tools:
     - Read
   ---
   ```

2. **BUILD: genetic-biomarker-analyst sub-agent** 🔴 **PRIORITY 1** (2-3 hours)
   - Create `scripts/analysis/modules/genetic_biomarker.py` with 7+ atomic functions
   - Create `scripts/mcp/queries/opentargets.py` with 3+ query functions
   - Create `.claude/agents/genetic-biomarker-analyst.md` agent spec
   - Generate example script: `scripts/analysis/nsclc/genetic_biomarker_landscape.py`
   - Test with NSCLC use case (EGFR, ALK, ROS1, KRAS mutations)

3. **BUILD: gaps-analyst sub-agent** 🟡 PRIORITY 2 (1-2 hours)
   - Create `scripts/analysis/modules/gaps.py` with 5+ atomic functions
   - Update `competitive_landscape.py` to use gaps functions
   - Create `.claude/agents/gaps-analyst.md` agent spec

4. **BUILD: differentiation-analyst sub-agent** 🟡 PRIORITY 3 (1-2 hours)
   - Create `scripts/analysis/modules/differentiation.py` with 5+ atomic functions
   - Update `competitive_landscape.py` to use differentiation functions
   - Create `.claude/agents/differentiation-analyst.md` agent spec

### Sub-Agent Architecture Decision

**RECOMMEND: Hybrid Approach**

**Tier 1: Orchestrator**
- `competitive-specialist` - Generates comprehensive competitive landscape analysis scripts

**Tier 2: Sub-Agents** (can be invoked individually or composed)
- `pipeline-analyst` - Phase 2/3 dynamics, trial tracking, completion forecasts
- `market-structure-analyst` - Current leaders, moats, concentration, vulnerabilities
- `genetic-biomarker-analyst` - Precision medicine competitive intelligence 🔴 **BUILD FIRST**
- `threat-scorer` - 5-component rubric, approval probability, launch forecasts
- `differentiation-analyst` - MOA, dosing, indication, safety differentiation 🟡
- `gaps-analyst` - White space, crowded segments, unmet needs 🟡

**Tier 3: Atomic Functions** (reusable across all agents)
- `scripts/analysis/modules/competitive.py` (existing - 15+ functions)
- `scripts/analysis/modules/pipeline.py` (new - 5+ functions)
- `scripts/analysis/modules/market_structure.py` (new - 5+ functions)
- `scripts/analysis/modules/genetic_biomarker.py` (new - 7+ functions) 🔴 **PRIORITY 1**
- `scripts/analysis/modules/differentiation.py` (new - 5+ functions) 🟡
- `scripts/analysis/modules/gaps.py` (new - 5+ functions) 🟡
- `scripts/analysis/modules/validation.py` (new - 3+ functions) 🟢

**Tier 4: MCP Queries** (atomic query functions)
- `scripts/mcp/queries/clinicaltrials.py` (existing - 7 functions)
- `scripts/mcp/queries/opentargets.py` (new - 3+ functions) 🔴 **PRIORITY 1**
- `scripts/mcp/queries/fda.py` (future - drug labels, approvals)
- `scripts/mcp/queries/pubmed.py` (future - literature analysis)

### Benefits of Sub-Agent Decomposition

✅ **Modularity**: Each sub-agent has single responsibility
✅ **Reusability**: Atomic functions shared across agents
✅ **Testability**: Individual functions and sub-agents can be unit tested
✅ **Flexibility**: Users can invoke full orchestrator OR specific sub-agents
✅ **Maintainability**: Changes to one sub-agent don't affect others
✅ **Scalability**: Easy to add new sub-agents (pricing-analyst, regulatory-analyst, etc.)
✅ **Composability**: Sub-agents can be combined in custom workflows

---

## Conclusion

### Q1: Frontmatter ❌ MISSING - Easy fix (5 minutes)
- Add YAML frontmatter to competitive-specialist.md matching pharma-search-specialist.md format
- Use `color: purple` to distinguish code-generating specialists

### Q2: Sub-Agent Decomposition ✅ YES - Highly Recommended
- 6 sub-agents identified (pipeline, market-structure, genetic-biomarker, threat-scorer, differentiation, gaps)
- Hybrid architecture: Full orchestrator + Individual sub-agents + Atomic functions
- Maximum modularity, reusability, testability, flexibility

### Q3: Capability Coverage ⚠️ 55% - Critical Gaps Identified
- 🔴 **CRITICAL GAP**: Genetic biomarker competitive intelligence (25% of competitive-analyst.md)
- 🟡 **MODERATE GAPS**: Gaps analysis, differentiation deep dive
- 🟢 **LOW PRIORITY**: Input validation, regulatory pathway (mostly covered), market sizing integration

**Next Steps**:
1. Fix frontmatter (5 min)
2. Build genetic-biomarker-analyst (2-3 hrs) 🔴 **HIGHEST PRIORITY**
3. Build gaps-analyst (1-2 hrs) 🟡
4. Build differentiation-analyst (1-2 hrs) 🟡
5. Document sub-agent architecture in `.claude/CLAUDE.md`
