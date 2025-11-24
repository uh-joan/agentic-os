# Pipeline Aggregator & Competitive Analyzer

**Skill Name**: `analyze_indication_pipeline`

**Category**: Competitive Intelligence / Pipeline Analytics

**Complexity**: Medium

**Purpose**: Aggregate clinical trials data for a given indication, providing both quantitative metrics (phase distribution, sponsor ranking) AND competitive analysis (differentiation, white space, threat levels) with rich visualizations.

---

## Overview

This skill transforms raw clinical trials data into actionable competitive intelligence by combining:
1. **Quantitative aggregation**: Counts, distributions, trends
2. **Competitive analysis**: Positioning, differentiation, gaps
3. **Visual insights**: Charts, matrices, timelines

**Use Cases**:
- Rapidly assess competitive landscape for BD target evaluation
- Identify white space opportunities (unmet needs, underserved segments)
- Forecast market entry timing and competitive intensity
- Support strategic planning with data-driven competitive insights

**Key Innovation**: Combines pharma-pipeline-tracking-analyst's quantitative focus with pharma-landscape-competitive-analyst's strategic insights in a single executable skill.

---

## Input Schema

```python
{
    "indication": str,                  # Required: Disease/condition (e.g., "Type 2 Diabetes", "NSCLC")
    "filters": {                        # Optional filters
        "phase": List[str],             # ["Phase 2", "Phase 3"] (default: all phases)
        "status": List[str],            # ["Recruiting", "Active, not recruiting"] (default: active only)
        "sponsors": List[str],          # ["Pfizer", "Merck"] (default: all sponsors)
        "mechanisms": List[str],        # ["GLP-1", "SGLT2"] (default: all mechanisms)
        "geography": List[str]          # ["United States", "China"] (default: global)
    },
    "analysis_options": {
        "include_white_space": bool,    # Identify unmet needs (default: True)
        "include_threat_scoring": bool, # Score competitive threats (default: True)
        "include_timeline_forecast": bool, # Predict launch timing (default: True)
        "visualization_format": str     # "matplotlib", "plotly", "ascii", "all" (default: "all")
    },
    "reference_program": {              # Optional: For competitive comparison
        "name": str,
        "phase": str,
        "mechanism": str,
        "efficacy_score": float,        # 0-100
        "convenience_score": float      # 0-100
    }
}
```

---

## Output Schema

```python
{
    "summary": {
        "indication": str,
        "total_programs": int,
        "active_phases": Dict[str, int],    # {"Phase 1": 45, "Phase 2": 78, ...}
        "top_sponsors": Dict[str, int],     # {"Pfizer": 12, "Merck": 8, ...}
        "mechanism_breakdown": Dict[str, int], # {"GLP-1": 15, "SGLT2": 8, ...}
        "launch_forecast": str              # "Peak launches: 2026-2028 (23 Phase 3 programs)"
    },
    "phase_distribution": {
        "counts": Dict[str, int],
        "percentages": Dict[str, float],
        "attrition_rates": {                # Phase transition success rates
            "Phase 1 → Phase 2": float,
            "Phase 2 → Phase 3": float,
            "Phase 3 → Approval": float
        }
    },
    "competitive_analysis": {
        "positioning_matrix": {             # 2D competitive map
            "axes": {"x": str, "y": str},   # e.g., {"x": "Efficacy", "y": "Convenience"}
            "programs": List[{
                "name": str,
                "sponsor": str,
                "position": {"x": float, "y": float},
                "quadrant": str             # "Leader", "Challenger", "Niche", "Laggard"
            }]
        },
        "differentiation_gaps": List[{      # White space opportunities
            "gap_type": str,                # "Mechanism", "Population", "Dosing"
            "description": str,
            "opportunity_size": str         # "High", "Moderate", "Low"
        }],
        "threat_levels": List[{             # Competitive threats
            "program": str,
            "sponsor": str,
            "threat_score": float,          # 0-100
            "urgency": str                  # "CRITICAL", "HIGH", "MODERATE", "LOW"
        }]
    },
    "timeline_analysis": {
        "launch_sequence": List[{           # Predicted market entry order
            "program": str,
            "sponsor": str,
            "expected_launch": str,         # YYYY-MM-DD
            "probability": float            # 0-1 (accounting for attrition)
        }],
        "peak_launch_period": {
            "start_year": int,
            "end_year": int,
            "program_count": int
        }
    },
    "mechanism_insights": {
        "mechanism_counts": Dict[str, int],
        "mechanism_success_rates": Dict[str, float],  # Historical PoS by mechanism
        "emerging_mechanisms": List[str],             # Mechanisms gaining traction
        "declining_mechanisms": List[str]              # Mechanisms being abandoned
    },
    "geographic_distribution": {
        "trial_counts_by_region": Dict[str, int],
        "regional_trends": str                        # e.g., "China expanding rapidly"
    },
    "visualizations": {                               # Generated charts (as file paths)
        "phase_funnel": str,                          # path/to/phase_funnel.png
        "positioning_matrix": str,                    # path/to/positioning_matrix.png
        "timeline_gantt": str,                        # path/to/timeline_gantt.png
        "mechanism_treemap": str,                     # path/to/mechanism_treemap.png
        "sponsor_market_share": str                   # path/to/sponsor_pie.png
    }
}
```

---

## Algorithm

### Step 1: Data Aggregation

```python
def aggregate_pipeline_data(indication: str, filters: Dict) -> Dict:
    """Aggregate trial counts across dimensions."""

    # Use existing get_clinical_trials skill
    from .claude.skills.clinical_trials_term_phase.scripts.get_clinical_trials import get_clinical_trials

    # Fetch all trials for indication
    trials_data = get_clinical_trials(term=indication, phase=None)

    # Parse markdown response into structured data
    trials = parse_ctgov_markdown(trials_data['trials_summary'])

    # Apply filters
    if filters.get('phase'):
        trials = [t for t in trials if t['phase'] in filters['phase']]
    if filters.get('status'):
        trials = [t for t in trials if t['status'] in filters['status']]
    if filters.get('sponsors'):
        trials = [t for t in trials if t['sponsor'] in filters['sponsors']]

    # Aggregate metrics
    aggregated = {
        "total_programs": len(trials),
        "active_phases": count_by_field(trials, 'phase'),
        "top_sponsors": count_by_field(trials, 'sponsor', top_n=10),
        "mechanism_breakdown": count_by_field(trials, 'mechanism'),
        "status_distribution": count_by_field(trials, 'status'),
        "geography_distribution": count_by_field(trials, 'location')
    }

    return aggregated, trials  # Return both summary and raw trial list
```

### Step 2: Phase Distribution Analysis

```python
def analyze_phase_distribution(trials: List[Dict]) -> Dict:
    """Calculate phase metrics and attrition rates."""

    phase_counts = {
        "Phase 1": len([t for t in trials if t['phase'] == 'Phase 1']),
        "Phase 2": len([t for t in trials if t['phase'] == 'Phase 2']),
        "Phase 3": len([t for t in trials if t['phase'] == 'Phase 3']),
        "Phase 4": len([t for t in trials if t['phase'] == 'Phase 4'])
    }

    total = sum(phase_counts.values())
    phase_percentages = {
        phase: (count / total * 100) if total > 0 else 0
        for phase, count in phase_counts.items()
    }

    # Calculate attrition rates (historical benchmarks)
    attrition_rates = {
        "Phase 1 → Phase 2": calculate_historical_attrition("Phase 1", "Phase 2", indication),
        "Phase 2 → Phase 3": calculate_historical_attrition("Phase 2", "Phase 3", indication),
        "Phase 3 → Approval": calculate_historical_attrition("Phase 3", "Approval", indication)
    }

    return {
        "counts": phase_counts,
        "percentages": phase_percentages,
        "attrition_rates": attrition_rates
    }
```

### Step 3: Competitive Positioning Matrix

```python
def generate_positioning_matrix(trials: List[Dict], axes: Dict = None) -> Dict:
    """Create 2D competitive positioning map."""

    # Default axes: Efficacy vs Convenience
    if axes is None:
        axes = {"x": "efficacy", "y": "convenience"}

    programs = []
    for trial in trials:
        # Extract or estimate metrics for positioning
        x_score = estimate_efficacy_score(trial)
        y_score = estimate_convenience_score(trial)

        # Assign quadrant
        quadrant = assign_quadrant(x_score, y_score, median_x, median_y)

        programs.append({
            "name": trial['title'],
            "sponsor": trial['sponsor'],
            "position": {"x": x_score, "y": y_score},
            "quadrant": quadrant
        })

    return {
        "axes": axes,
        "programs": programs
    }

def assign_quadrant(x, y, median_x, median_y):
    """Assign strategic quadrant based on position."""
    if x >= median_x and y >= median_y:
        return "Leader"         # High efficacy, high convenience
    elif x >= median_x and y < median_y:
        return "Niche"          # High efficacy, low convenience
    elif x < median_x and y >= median_y:
        return "Challenger"     # Low efficacy, high convenience
    else:
        return "Laggard"        # Low efficacy, low convenience
```

### Step 4: White Space Identification

```python
def identify_white_space(trials: List[Dict], market_context: Dict) -> List[Dict]:
    """Identify competitive gaps and opportunities."""

    gaps = []

    # Mechanism gaps
    all_mechanisms = set(t['mechanism'] for t in trials)
    validated_mechanisms = get_validated_mechanisms(indication)  # From FDA approvals
    untapped_mechanisms = validated_mechanisms - all_mechanisms

    if untapped_mechanisms:
        gaps.append({
            "gap_type": "Mechanism",
            "description": f"No trials for validated mechanisms: {', '.join(untapped_mechanisms)}",
            "opportunity_size": "High"
        })

    # Population gaps (e.g., pediatric, elderly)
    populations_covered = extract_populations(trials)
    underserved = ["Pediatric", "Elderly", "Renal impairment"] - populations_covered

    if underserved:
        gaps.append({
            "gap_type": "Population",
            "description": f"Underserved populations: {', '.join(underserved)}",
            "opportunity_size": "Moderate"
        })

    # Dosing gaps (e.g., oral formulation in injectable market)
    routes = set(extract_route_of_administration(t) for t in trials)
    if "Oral" not in routes and indication_suitable_for_oral(indication):
        gaps.append({
            "gap_type": "Dosing",
            "description": "No oral formulations (all injectable/IV)",
            "opportunity_size": "High"
        })

    # Biomarker gaps (precision medicine)
    biomarker_trials = [t for t in trials if has_biomarker_stratification(t)]
    biomarker_rate = len(biomarker_trials) / len(trials) * 100

    if biomarker_rate < 20:  # <20% using biomarkers
        gaps.append({
            "gap_type": "Precision Medicine",
            "description": f"Low biomarker adoption ({biomarker_rate:.0f}% of trials)",
            "opportunity_size": "Moderate"
        })

    return gaps
```

### Step 5: Timeline Forecast

```python
def forecast_launch_timeline(trials: List[Dict]) -> Dict:
    """Predict market entry sequence."""

    launch_sequence = []

    for trial in trials:
        if trial['phase'] in ['Phase 3', 'Phase 4']:
            # Estimate time to approval
            phase_duration = estimate_phase_duration(trial['phase'], trial['indication'])
            nda_duration = 10  # months (FDA review)

            months_to_launch = phase_duration + nda_duration
            expected_launch = add_months_to_date(trial['start_date'], months_to_launch)

            # Adjust for probability of success
            pos = get_phase_pos(trial['phase'], trial['indication'])

            launch_sequence.append({
                "program": trial['title'],
                "sponsor": trial['sponsor'],
                "expected_launch": expected_launch,
                "probability": pos
            })

    # Sort by expected launch date
    launch_sequence.sort(key=lambda x: x['expected_launch'])

    # Identify peak launch period
    launch_years = [datetime.fromisoformat(l['expected_launch']).year
                    for l in launch_sequence]
    peak_year = max(set(launch_years), key=launch_years.count)

    return {
        "launch_sequence": launch_sequence,
        "peak_launch_period": {
            "start_year": peak_year,
            "end_year": peak_year + 2,
            "program_count": launch_years.count(peak_year)
        }
    }
```

### Step 6: Threat Scoring

```python
def score_competitive_threats(trials: List[Dict], reference_program: Dict) -> List[Dict]:
    """Score each competitor program against reference."""

    if not reference_program:
        # No reference = rank by proximity to approval
        return rank_by_launch_proximity(trials)

    threats = []
    for trial in trials:
        # Use score_competitive_threat algorithm (from first skill)
        threat_result = score_competitive_threat(
            competitor_program=trial,
            own_program=reference_program,
            market_context={"crowding": len(trials), ...}
        )

        threats.append({
            "program": trial['title'],
            "sponsor": trial['sponsor'],
            "threat_score": threat_result['threat_score'],
            "urgency": threat_result['urgency']
        })

    # Sort by threat score (descending)
    threats.sort(key=lambda x: x['threat_score'], reverse=True)

    return threats
```

---

## Visualizations

### 1. Phase Distribution Funnel

```python
import matplotlib.pyplot as plt
import numpy as np

def visualize_phase_funnel(phase_counts: Dict, output_path: str):
    """Funnel chart showing pipeline attrition."""

    phases = ["Phase 1", "Phase 2", "Phase 3", "Approved"]
    counts = [phase_counts.get(p, 0) for p in phases]

    # Create inverted bar chart (funnel)
    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = np.arange(len(phases))
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']

    bars = ax.barh(y_pos, counts, color=colors, alpha=0.8)

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_width() + 2, i, f'{count} programs',
                va='center', fontsize=10)

    # Add attrition arrows
    attrition = [
        "37% attrition",  # Phase 1 → 2
        "31% attrition",  # Phase 2 → 3
        "42% attrition"   # Phase 3 → Approval
    ]

    for i in range(len(phases) - 1):
        ax.annotate('', xy=(counts[i+1], i+0.5), xytext=(counts[i], i+0.5),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
        ax.text(max(counts[i], counts[i+1]) / 2, i+0.6, attrition[i],
                fontsize=9, color='red', ha='center')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(phases)
    ax.set_xlabel('Number of Programs')
    ax.set_title('Pipeline Phase Distribution with Attrition', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

**Example Output**:
```
Pipeline Phase Distribution with Attrition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1      ████████████████████████████  145 programs
                      ↓ 37% attrition
Phase 2      ████████████████████  92 programs
                      ↓ 31% attrition
Phase 3      ███████████  63 programs
                      ↓ 42% attrition
Approved     ██████  37 programs
```

### 2. Competitive Positioning Matrix

```python
def visualize_positioning_matrix(programs: List[Dict], output_path: str):
    """2D scatter plot with quadrant labels."""

    fig, ax = plt.subplots(figsize=(12, 8))

    # Extract positions
    x_vals = [p['position']['x'] for p in programs]
    y_vals = [p['position']['y'] for p in programs]

    # Color by quadrant
    colors = {'Leader': 'green', 'Challenger': 'orange',
              'Niche': 'blue', 'Laggard': 'red'}
    point_colors = [colors[p['quadrant']] for p in programs]

    # Scatter plot
    scatter = ax.scatter(x_vals, y_vals, c=point_colors, s=100, alpha=0.7)

    # Add program labels
    for p in programs:
        ax.annotate(f"{p['sponsor']}\n{p['name'][:20]}...",
                    (p['position']['x'], p['position']['y']),
                    fontsize=8, ha='center')

    # Add quadrant lines
    median_x = np.median(x_vals)
    median_y = np.median(y_vals)

    ax.axvline(median_x, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(median_y, color='gray', linestyle='--', alpha=0.5)

    # Label quadrants
    ax.text(median_x + 15, median_y + 15, 'LEADERS', fontsize=12,
            fontweight='bold', color='green', ha='center')
    ax.text(median_x + 15, median_y - 15, 'NICHE', fontsize=12,
            fontweight='bold', color='blue', ha='center')
    ax.text(median_x - 15, median_y + 15, 'CHALLENGERS', fontsize=12,
            fontweight='bold', color='orange', ha='center')
    ax.text(median_x - 15, median_y - 15, 'LAGGARDS', fontsize=12,
            fontweight='bold', color='red', ha='center')

    ax.set_xlabel('Efficacy Score (0-100)', fontsize=12)
    ax.set_ylabel('Convenience Score (0-100)', fontsize=12)
    ax.set_title('Competitive Positioning Matrix', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

**Example Output**:
```
       Competitive Positioning Matrix
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  100 │        CHALLENGERS  │  LEADERS
      │                     │
   C  │    Lilly            │  Novo
   o  │    Orforglipron     │  Rybelsus
   n  │                     │
   v  │                     │  Pfizer
   e 50├─────────────────────┼──────────
   n  │                     │  Danuglipron
   i  │                     │
   e  │                     │
   n  │    LAGGARDS         │  NICHE
   c  │                     │
   e  │                     │
    0 └─────────────────────┴──────────
      0        50         100
            Efficacy Score
```

### 3. Launch Timeline Gantt Chart

```python
def visualize_launch_timeline(launch_sequence: List[Dict], output_path: str):
    """Gantt chart of predicted launches."""

    import pandas as pd
    import matplotlib.dates as mdates

    fig, ax = plt.subplots(figsize=(14, 8))

    # Prepare data
    programs = [l['program'][:30] + '...' for l in launch_sequence]
    dates = [datetime.fromisoformat(l['expected_launch']) for l in launch_sequence]
    probabilities = [l['probability'] for l in launch_sequence]

    # Create horizontal bars
    y_pos = np.arange(len(programs))

    for i, (date, prob) in enumerate(zip(dates, probabilities)):
        # Bar length = probability (wider = higher confidence)
        bar_start = date - timedelta(days=180 * prob)
        bar_end = date + timedelta(days=180 * prob)

        ax.barh(i, (bar_end - bar_start).days,
                left=mdates.date2num(bar_start),
                height=0.6,
                color='steelblue' if prob > 0.5 else 'lightcoral',
                alpha=0.7)

        # Add launch date marker
        ax.scatter(mdates.date2num(date), i, color='red', s=100, zorder=3)

        # Add probability label
        ax.text(mdates.date2num(date) + 30, i, f'{prob:.0%}',
                va='center', fontsize=8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(programs)
    ax.set_xlabel('Expected Launch Date', fontsize=12)
    ax.set_title('Competitive Launch Timeline Forecast', fontsize=14, fontweight='bold')

    # Format x-axis as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)

    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### 4. Mechanism Treemap

```python
import squarify

def visualize_mechanism_breakdown(mechanism_counts: Dict, output_path: str):
    """Treemap of mechanism distribution."""

    fig, ax = plt.subplots(figsize=(12, 8))

    mechanisms = list(mechanism_counts.keys())
    counts = list(mechanism_counts.values())

    # Create treemap
    colors = plt.cm.Set3(np.linspace(0, 1, len(mechanisms)))

    squarify.plot(sizes=counts,
                  label=[f"{m}\n{c} programs" for m, c in zip(mechanisms, counts)],
                  color=colors,
                  alpha=0.8,
                  text_kwargs={'fontsize':10, 'weight':'bold'})

    ax.set_title('Mechanism of Action Distribution', fontsize=14, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### 5. ASCII Terminal Output

```python
def print_ascii_summary(aggregated_data: Dict):
    """Terminal-friendly ASCII visualization."""

    print("""
┌─────────────────────────────────────────────────────────────────┐
│               PIPELINE COMPETITIVE INTELLIGENCE                 │
│                   Type 2 Diabetes - Global                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ TOTAL PROGRAMS: 337                                            │
│                                                                 │
│ PHASE DISTRIBUTION:                                            │
│   Phase 1:  145 (43%)  ██████████████████████░░░░░░░░░░░░░░   │
│   Phase 2:   92 (27%)  █████████████░░░░░░░░░░░░░░░░░░░░░░░   │
│   Phase 3:   63 (19%)  █████████░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│   Phase 4:   37 (11%)  █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ TOP MECHANISMS:                                                 │
│   1. GLP-1 agonist        67 programs (20%)                     │
│   2. SGLT2 inhibitor      45 programs (13%)                     │
│   3. DPP-4 inhibitor      38 programs (11%)                     │
│   4. Insulin analogue     32 programs ( 9%)                     │
│   5. Other               155 programs (46%)                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ TOP SPONSORS:                                                   │
│   1. Novo Nordisk         28 programs                           │
│   2. Eli Lilly            23 programs                           │
│   3. Sanofi               19 programs                           │
│   4. AstraZeneca          15 programs                           │
│   5. Boehringer Ingelheim 14 programs                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ LAUNCH FORECAST:                                                │
│   Peak Launches: 2026-2028                                     │
│   Phase 3 Programs: 63 (expected 36 approvals at 58% PoS)      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ WHITE SPACE OPPORTUNITIES:                                      │
│   • Oral GLP-1 formulations (only 1 approved, 8 in pipeline)   │
│   • Pediatric populations (only 5% of trials)                   │
│   • Weight loss + glycemic control dual indication              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ TOP COMPETITIVE THREATS:                                        │
│   1. Pfizer Danuglipron     [78/100] HIGH                       │
│   2. Lilly Orforglipron     [75/100] HIGH                       │
│   3. Novo CagriSema         [68/100] MODERATE                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
    """)
```

---

## Usage Examples

### Example 1: Basic Pipeline Aggregation

```python
from .claude.skills.pipeline_aggregator_analyzer.scripts.analyze_indication_pipeline import analyze_indication_pipeline

result = analyze_indication_pipeline(
    indication="Type 2 Diabetes",
    filters={
        "phase": ["Phase 2", "Phase 3"],
        "status": ["Recruiting", "Active, not recruiting"]
    },
    analysis_options={
        "include_white_space": True,
        "include_threat_scoring": False,  # No reference program
        "include_timeline_forecast": True,
        "visualization_format": "all"
    }
)

print(f"Total Programs: {result['summary']['total_programs']}")
print(f"Phase 3 Programs: {result['phase_distribution']['counts']['Phase 3']}")
print(f"Top Sponsor: {list(result['summary']['top_sponsors'].keys())[0]}")
```

**Output**:
```
Total Programs: 155
Phase 3 Programs: 63
Top Sponsor: Novo Nordisk (28 programs)

Visualizations saved:
- phase_funnel.png
- positioning_matrix.png
- timeline_gantt.png
- mechanism_treemap.png
```

### Example 2: Competitive Threat Analysis

```python
# With reference program for threat scoring
result = analyze_indication_pipeline(
    indication="Type 2 Diabetes",
    reference_program={
        "name": "Rybelsus",
        "phase": "Approved",
        "mechanism": "GLP-1 agonist (oral)",
        "efficacy_score": 85,
        "convenience_score": 75
    },
    analysis_options={
        "include_threat_scoring": True,
        "visualization_format": "ascii"
    }
)

# Print top threats
for threat in result['competitive_analysis']['threat_levels'][:5]:
    print(f"{threat['program']}: {threat['threat_score']}/100 [{threat['urgency']}]")
```

**Output**:
```
Pfizer Danuglipron: 78/100 [HIGH]
Lilly Orforglipron: 75/100 [HIGH]
Novo CagriSema: 68/100 [MODERATE]
Structure SR-GLP1: 52/100 [MODERATE]
Zealand Dapiglutide: 45/100 [LOW]
```

### Example 3: White Space Discovery

```python
result = analyze_indication_pipeline(
    indication="Non-Small Cell Lung Cancer",
    filters={"phase": ["Phase 3"]},
    analysis_options={"include_white_space": True}
)

# Print identified gaps
for gap in result['competitive_analysis']['differentiation_gaps']:
    print(f"[{gap['opportunity_size']} OPPORTUNITY] {gap['gap_type']}: {gap['description']}")
```

**Output**:
```
[High OPPORTUNITY] Mechanism: No trials for KRAS G12D inhibitors (validated target)
[Moderate OPPORTUNITY] Population: Underserved: Elderly, Brain metastases
[High OPPORTUNITY] Dosing: No oral formulations (all IV/injectable)
[Moderate OPPORTUNITY] Precision Medicine: Low biomarker adoption (18% of trials)
```

---

## Implementation Notes

### Dependencies
```bash
pip install pandas matplotlib seaborn plotly squarify
```

### File Structure
```
pipeline-aggregator-analyzer/
├── SKILL.md                               # This documentation
└── scripts/
    ├── analyze_indication_pipeline.py     # Main orchestrator
    ├── aggregation.py                     # Counting/grouping functions
    ├── competitive_analysis.py            # Positioning, white space
    ├── timeline_forecast.py               # Launch predictions
    ├── visualizations.py                  # All chart generation
    └── test_pipeline_analysis.py          # Unit tests
```

### Data Sources

This skill wraps around:
1. **`get_clinical_trials`** (existing skill) - Raw CT.gov data
2. **`score_competitive_threat`** (companion skill) - Threat scoring algorithm
3. **Historical benchmarks** - Phase transition rates, approval timelines

### Performance Optimization

- **Caching**: Store CT.gov results for 24 hours (data doesn't change frequently)
- **Parallel processing**: Use `multiprocessing` for large indication sets (1000+ trials)
- **Lazy visualization**: Only generate requested chart formats

### Edge Cases

1. **Small pipelines** (<10 programs): Skip statistical analyses, focus on descriptive
2. **Missing mechanism data**: Extract from trial title/abstract using NLP
3. **Ambiguous phases**: "Phase 1/2" counted as Phase 2 for conservative estimates
4. **Terminated trials**: Include in attrition calculations, exclude from launch forecast

---

## Future Enhancements

1. **ML-based efficacy prediction**: Train on historical trial outcomes to estimate efficacy scores
2. **Real-time monitoring**: Webhook integration with CT.gov for instant updates
3. **Interactive dashboards**: Plotly Dash web app for exploration
4. **Patent cliff integration**: Layer patent expiry data onto timeline forecast
5. **Combination therapy analysis**: Detect common combination partners
6. **Geographic heatmaps**: Visualize trial concentration by region

---

## References

- **Pipeline metrics**: BIO Clinical Development Success Rates 2006-2015
- **Competitive positioning**: BCG Growth-Share Matrix, GE-McKinsey Matrix
- **Timeline forecasting**: Tufts CSDD Outlook Report 2020
- **White space analysis**: Blue Ocean Strategy (Kim & Mauborgne)
