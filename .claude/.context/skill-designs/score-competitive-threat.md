# Competitive Threat Scoring Algorithm

**Skill Name**: `score_competitive_threat`

**Category**: Strategic Analysis / Competitive Intelligence

**Complexity**: Medium

**Purpose**: Quantify competitive threat severity using multi-criteria scoring to prioritize competitive responses and inform strategic decisions.

---

## Overview

This skill provides a quantitative framework for assessing competitive threats from pipeline programs. It combines multiple factors (probability of success, timeline proximity, market overlap, differentiation) into a single threat score (0-100) with actionable urgency levels.

**Use Cases**:
- Prioritize competitive monitoring resources
- Trigger acceleration decisions for internal programs
- Inform BD target selection (acquire to block competitor)
- Guide defensive strategies (pricing, partnerships, label expansion)

---

## Input Schema

```python
{
    "competitor_program": {
        "name": str,                    # Drug name
        "sponsor": str,                 # Company name
        "indication": str,              # Target disease
        "mechanism": str,               # MOA
        "phase": str,                   # "Phase 1", "Phase 2", "Phase 3", "NDA"
        "timeline": {
            "phase_start_date": str,    # ISO format YYYY-MM-DD
            "expected_approval": str,   # ISO format YYYY-MM-DD (estimated)
            "years_to_launch": float    # Years until market entry
        },
        "clinical_data": {
            "efficacy": float,          # 0-100 scale (relative to standard)
            "safety_score": float,      # 0-100 scale (100 = excellent safety)
            "patient_convenience": float # 0-100 scale (dosing, administration)
        },
        "market_position": {
            "target_population": int,   # Eligible patients
            "pricing_expected": float   # Expected annual cost
        },
        "regulatory": {
            "breakthrough": bool,       # FDA Breakthrough designation
            "orphan": bool,            # Orphan drug status
            "fast_track": bool         # Fast Track designation
        }
    },
    "own_program": {
        # Same schema as competitor_program
        # Used for differentiation gap analysis
    },
    "market_context": {
        "current_standard": str,        # Current SOC drug
        "market_size": float,           # TAM in $M
        "crowding": int,                # Number of competitors in pipeline
        "unmet_need_severity": str      # "high", "moderate", "low"
    }
}
```

---

## Output Schema

```python
{
    "threat_score": float,              # 0-100 composite score
    "urgency": str,                     # "CRITICAL", "HIGH", "MODERATE", "LOW"
    "factors_breakdown": {
        "probability_of_success": {
            "score": float,             # 0-100
            "weight": float,            # 0.30
            "contribution": float       # score × weight
        },
        "timeline_proximity": {
            "score": float,             # 0-100 (higher = closer launch)
            "weight": float,            # 0.25
            "contribution": float
        },
        "market_overlap": {
            "score": float,             # 0-100 (patient population overlap)
            "weight": float,            # 0.25
            "contribution": float
        },
        "differentiation_gap": {
            "score": float,             # 0-100 (lower = more differentiated from us)
            "weight": float,            # 0.20
            "contribution": float
        }
    },
    "threat_drivers": List[str],        # Top 3 factors driving high threat
    "response_recommendations": {
        "immediate_actions": List[str], # If CRITICAL urgency
        "monitoring_actions": List[str], # If HIGH/MODERATE urgency
        "contingency_plans": List[str]  # Strategic options
    },
    "competitive_advantages": List[str], # Areas where we maintain edge
    "vulnerabilities": List[str]        # Areas where competitor superior
}
```

---

## Algorithm

### Step 1: Calculate Factor Scores (0-100 scale)

#### Factor 1: Probability of Success (PoS)
```python
def calculate_pos_score(program):
    """Base PoS from phase + adjustments."""

    # Base PoS by phase (industry benchmarks)
    base_pos = {
        "Phase 1": 15,
        "Phase 2": 30,
        "Phase 3": 60,
        "NDA": 85
    }

    pos = base_pos[program["phase"]]

    # Adjustments
    if program["regulatory"]["breakthrough"]:
        pos += 10
    if program["regulatory"]["orphan"]:
        pos += 15
    if program["regulatory"]["fast_track"]:
        pos += 5

    # Novel mechanism penalty (no precedent)
    if is_novel_mechanism(program["mechanism"]):
        pos -= 10

    return min(100, max(0, pos))
```

#### Factor 2: Timeline Proximity
```python
def calculate_timeline_score(years_to_launch):
    """Convert time-to-launch to urgency score."""

    # Inverse relationship: Closer = Higher threat
    if years_to_launch <= 1:
        return 100  # Imminent launch
    elif years_to_launch <= 2:
        return 80   # Near-term threat
    elif years_to_launch <= 3:
        return 60   # Medium-term
    elif years_to_launch <= 5:
        return 40   # Longer-term
    else:
        return 20   # Distant threat
```

#### Factor 3: Market Overlap
```python
def calculate_overlap_score(competitor, own_program):
    """Patient population overlap."""

    # Indication overlap
    if competitor["indication"] == own_program["indication"]:
        indication_overlap = 100
    elif same_therapeutic_area(competitor, own_program):
        indication_overlap = 60  # Adjacent indications
    else:
        indication_overlap = 20  # Different TAs

    # Population overlap
    comp_pop = competitor["market_position"]["target_population"]
    own_pop = own_program["market_position"]["target_population"]

    overlap_patients = min(comp_pop, own_pop) / max(comp_pop, own_pop)

    return indication_overlap * overlap_patients
```

#### Factor 4: Differentiation Gap
```python
def calculate_differentiation_score(competitor, own_program):
    """How similar is competitor to our program? (Higher = Less differentiated = Greater threat)"""

    # Clinical profile similarity
    efficacy_gap = abs(competitor["clinical_data"]["efficacy"] -
                      own_program["clinical_data"]["efficacy"])
    safety_gap = abs(competitor["clinical_data"]["safety_score"] -
                    own_program["clinical_data"]["safety_score"])
    convenience_gap = abs(competitor["clinical_data"]["patient_convenience"] -
                         own_program["clinical_data"]["patient_convenience"])

    # Average gap (lower gap = more similar = higher threat)
    avg_gap = (efficacy_gap + safety_gap + convenience_gap) / 3

    # Invert: Low gap → High score (threat)
    similarity_score = 100 - avg_gap

    # Mechanism similarity
    if competitor["mechanism"] == own_program["mechanism"]:
        mechanism_penalty = 20  # Me-too drug = higher threat
    else:
        mechanism_penalty = 0

    return min(100, similarity_score + mechanism_penalty)
```

### Step 2: Weighted Composite Scoring

```python
def calculate_threat_score(competitor, own_program, market_context):
    """Combine factors with weights."""

    # Calculate individual factor scores
    pos_score = calculate_pos_score(competitor)
    timeline_score = calculate_timeline_score(
        competitor["timeline"]["years_to_launch"]
    )
    overlap_score = calculate_overlap_score(competitor, own_program)
    diff_score = calculate_differentiation_score(competitor, own_program)

    # Weights (must sum to 1.0)
    weights = {
        "pos": 0.30,        # Success probability most important
        "timeline": 0.25,   # Urgency matters
        "overlap": 0.25,    # Market conflict
        "diff": 0.20        # Similarity
    }

    # Weighted sum
    threat_score = (
        pos_score * weights["pos"] +
        timeline_score * weights["timeline"] +
        overlap_score * weights["overlap"] +
        diff_score * weights["diff"]
    )

    # Market context adjustments
    if market_context["crowding"] > 5:
        threat_score *= 0.9  # Crowded market, diluted threat

    if market_context["unmet_need_severity"] == "high":
        threat_score *= 1.1  # High unmet need = room for multiple winners

    return min(100, max(0, threat_score))
```

### Step 3: Assign Urgency Level

```python
def assign_urgency(threat_score):
    """Map score to actionable urgency."""

    if threat_score >= 80:
        return "CRITICAL"  # Immediate action required
    elif threat_score >= 60:
        return "HIGH"      # Close monitoring, contingency planning
    elif threat_score >= 40:
        return "MODERATE"  # Routine monitoring
    else:
        return "LOW"       # Awareness only
```

### Step 4: Generate Response Recommendations

```python
def generate_recommendations(threat_score, urgency, competitor, own_program):
    """Actionable recommendations based on threat level."""

    recommendations = {
        "immediate_actions": [],
        "monitoring_actions": [],
        "contingency_plans": []
    }

    if urgency == "CRITICAL":
        recommendations["immediate_actions"] = [
            f"Accelerate {own_program['name']} development (compress Phase 3 timeline)",
            f"Initiate BD discussions to acquire competitor or blocking assets",
            f"Prepare defensive label expansion (additional indications)",
            f"Secure key KOL relationships before competitor launch"
        ]

    elif urgency == "HIGH":
        recommendations["monitoring_actions"] = [
            f"Weekly monitoring of {competitor['name']} trial progress",
            f"Track enrollment rates and interim data disclosures",
            f"Monitor FDA correspondence (REMS, Advisory Committee scheduling)"
        ]
        recommendations["contingency_plans"] = [
            "Prepare competitive response pricing strategy",
            "Develop differentiated medical affairs messaging",
            "Evaluate partnership/co-promotion options"
        ]

    elif urgency == "MODERATE":
        recommendations["monitoring_actions"] = [
            f"Quarterly review of {competitor['sponsor']} pipeline updates",
            f"Monitor conference presentations and publications"
        ]

    return recommendations
```

---

## Visualization

### Threat Score Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ COMPETITIVE THREAT ASSESSMENT                           │
│ Competitor: Pfizer - Danuglipron (Oral GLP-1)          │
│ Our Program: Novo - Rybelsus (Oral GLP-1)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ THREAT SCORE: 78/100  ████████████████████░░  [HIGH]  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ FACTOR BREAKDOWN:                                       │
│                                                         │
│ PoS (30%):           85/100  ████████████████████░     │
│ Timeline (25%):      80/100  ████████████████████      │
│ Overlap (25%):       90/100  ██████████████████████    │
│ Differentiation(20%): 50/100 ██████████░░░░░░░░░░     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ THREAT DRIVERS:                                         │
│ 1. High patient overlap (90%) - T2D same indication    │
│ 2. Near-term launch (1.5 years) - Phase 3 enrolling    │
│ 3. Differentiation: BID dosing, no fasting (superior)  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ IMMEDIATE ACTIONS:                                      │
│ • Accelerate Rybelsus convenience messaging            │
│ • Prepare QD dosing differentiation strategy           │
│ • Monitor Pfizer Phase 3 enrollment (10K patients)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Multi-Program Threat Heat Map

```python
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_threat_landscape(competitors: List[Dict]):
    """Heat map of threat scores across multiple competitors."""

    # Create matrix: Competitors × Factors
    data = []
    for comp in competitors:
        data.append([
            comp["threat_score"],
            comp["factors"]["pos"],
            comp["factors"]["timeline"],
            comp["factors"]["overlap"],
            comp["factors"]["diff"]
        ])

    # Heat map
    plt.figure(figsize=(10, 6))
    sns.heatmap(data,
                annot=True,
                fmt=".0f",
                cmap="RdYlGn_r",  # Red = High threat
                xticklabels=["Overall", "PoS", "Timeline", "Overlap", "Diff"],
                yticklabels=[c["name"] for c in competitors])
    plt.title("Competitive Threat Landscape")
    plt.tight_layout()
    plt.savefig("threat_heatmap.png")
```

---

## Usage Examples

### Example 1: Phase 3 Direct Competitor

```python
from .claude.skills.score_competitive_threat.scripts.score_competitive_threat import score_competitive_threat

competitor = {
    "name": "Danuglipron",
    "sponsor": "Pfizer",
    "indication": "Type 2 Diabetes",
    "mechanism": "GLP-1 receptor agonist",
    "phase": "Phase 3",
    "timeline": {
        "phase_start_date": "2024-01-15",
        "expected_approval": "2027-06-01",
        "years_to_launch": 1.5
    },
    "clinical_data": {
        "efficacy": 85,  # HbA1c reduction comparable
        "safety_score": 80,
        "patient_convenience": 90  # BID, no fasting
    },
    "market_position": {
        "target_population": 30000000,
        "pricing_expected": 12000
    },
    "regulatory": {
        "breakthrough": False,
        "orphan": False,
        "fast_track": True
    }
}

own_program = {
    "name": "Rybelsus",
    "sponsor": "Novo Nordisk",
    # ... similar structure
}

market_context = {
    "current_standard": "Injectable GLP-1s",
    "market_size": 25000,  # $25B TAM
    "crowding": 3,  # Rybelsus + 2 competitors
    "unmet_need_severity": "moderate"
}

result = score_competitive_threat(competitor, own_program, market_context)

print(f"Threat Score: {result['threat_score']}/100")
print(f"Urgency: {result['urgency']}")
print(f"Top Threat Drivers: {result['threat_drivers']}")
```

**Output**:
```
Threat Score: 78/100
Urgency: HIGH
Top Threat Drivers: ['High patient overlap (90%)', 'Near-term launch (1.5 years)', 'Superior convenience (BID, no fasting)']

Immediate Actions:
- Accelerate Rybelsus convenience messaging
- Prepare QD dosing differentiation strategy
- Monitor Pfizer Phase 3 enrollment closely
```

### Example 2: Batch Threat Scoring

```python
def prioritize_competitive_threats(competitors: List[Dict], own_program: Dict):
    """Score and rank all competitors."""

    threats = []
    for comp in competitors:
        result = score_competitive_threat(comp, own_program, market_context)
        threats.append({
            "competitor": comp["name"],
            "sponsor": comp["sponsor"],
            "threat_score": result["threat_score"],
            "urgency": result["urgency"]
        })

    # Sort by threat score (descending)
    threats_sorted = sorted(threats, key=lambda x: x["threat_score"], reverse=True)

    return threats_sorted

# Prioritized monitoring list
top_threats = prioritize_competitive_threats(all_competitors, rybelsus)
```

---

## Implementation Notes

### Dependencies
```bash
pip install numpy pandas matplotlib seaborn
```

### File Structure
```
score-competitive-threat/
├── SKILL.md                    # This documentation
└── scripts/
    ├── score_competitive_threat.py  # Main algorithm
    ├── visualization.py             # Plotting functions
    └── test_scoring.py              # Unit tests
```

### Edge Cases

1. **Missing clinical data**: Use industry averages for phase/indication
2. **Multiple indications**: Score each indication separately, take max threat
3. **Combination therapies**: Score against each component of our portfolio
4. **Generic/biosimilar threats**: Different scoring model (price erosion focus)

### Validation

Test against known competitive scenarios:
- **Keytruda vs Opdivo** (2014-2016): Should score HIGH (actual fierce competition)
- **Opdivo + Yervoy vs Keytruda mono** (2016): Should score MODERATE (differentiated)
- **Tecentriq vs Keytruda** (2016): Should score HIGH (direct PD-L1 competition)

---

## Future Enhancements

1. **Machine learning**: Train on historical competitive outcomes to refine weights
2. **Patent cliff integration**: Factor in loss of exclusivity timelines
3. **Pricing power modeling**: Incorporate payer coverage and reimbursement risk
4. **Real-time updates**: API integration with ClinicalTrials.gov for live monitoring
5. **Portfolio-level threats**: Score threat to entire franchise, not just one drug

---

## References

- **Phase transition probabilities**: BIO Clinical Development Success Rates 2006-2015
- **Development timelines**: Tufts CSDD Outlook Report 2020
- **Competitive dynamics**: Porter's Five Forces framework
- **Threat assessment**: McKinsey Competitive Intelligence methodology
