# Agent-Centric Code Organization

## Design Principle

**Each agent owns its domain**: functions + queries + examples

```
scripts/
├── competitive/              ← competitive-specialist domain
│   ├── functions.py          ← Atomic analysis functions (13 functions)
│   ├── queries.py            ← MCP query wrappers (6 functions)
│   └── examples/             ← Generated example scripts
│       └── obesity_landscape.py
├── epidemiology/             ← Future: epidemiology-analyst domain
│   ├── functions.py
│   ├── queries.py
│   └── examples/
├── pricing/                  ← Future: pricing-strategy-analyst domain
│   ├── functions.py
│   ├── queries.py
│   └── examples/
└── mcp/
    └── client.py             ← Shared MCP client only
```

## Benefits

✅ **Agent-centric**: Mirrors `.claude/agents/` structure
✅ **Domain ownership**: competitive-specialist owns everything in `scripts/competitive/`
✅ **Easy discovery**: "Where are competitive functions?" → `scripts/competitive/functions.py`
✅ **Clear boundaries**: No confusion about what goes where
✅ **Scalable**: Add new agent → add new directory
✅ **Self-contained**: Each agent directory has everything needed

## Structure Pattern

**Every agent directory follows the same pattern**:

```
scripts/{agent-name}/
├── functions.py    ← Atomic domain logic functions
├── queries.py      ← MCP query wrappers for this domain
└── examples/       ← Generated scripts (organized by use case, not therapeutic area)
    ├── example1.py
    └── example2.py
```

**No therapeutic area subdirectories**. Examples are organized by **agent**, not indication.

### Example: competitive-specialist

```
scripts/competitive/
├── functions.py              ← 13 atomic functions
│   ├── calculate_competitive_intensity()
│   ├── assess_market_maturity()
│   ├── score_threat_level()
│   └── ...
├── queries.py                ← 6 MCP query functions
│   ├── get_trial_count()
│   ├── get_phase_distribution()
│   ├── get_sponsor_breakdown()
│   └── ...
└── examples/                 ← Generated scripts
    ├── obesity_landscape.py
    ├── diabetes_landscape.py (future)
    └── nash_landscape.py (future)
```

**Generated script imports**:
```python
from competitive.functions import (
    calculate_competitive_intensity,
    assess_market_maturity,
    score_threat_level
)
from competitive.queries import (
    get_trial_count,
    get_phase_distribution
)
```

## Migration from Old Structure

### Before (Module-centric)

```
scripts/
├── analysis/
│   ├── modules/              ← Generic, unclear
│   │   └── competitive.py
│   └── obesity/              ← Organized by therapeutic area
│       └── competitive_landscape.py
└── mcp/
    └── queries/
        └── clinicaltrials.py
```

**Problems**:
- ❌ `modules/` - What kind of modules?
- ❌ `obesity/` - Scripts scattered by therapeutic area
- ❌ No clear agent ownership
- ❌ Hard to find: "Where are competitive functions?" → search multiple directories

### After (Agent-centric)

```
scripts/
├── competitive/              ← Clear agent ownership
│   ├── functions.py          ← All competitive logic
│   ├── queries.py            ← All competitive queries
│   └── examples/             ← All competitive examples
│       └── obesity_landscape.py
└── mcp/
    └── client.py             ← Shared infrastructure only
```

**Benefits**:
- ✅ Clear ownership: competitive-specialist owns `scripts/competitive/`
- ✅ Easy discovery: Everything in one place
- ✅ No scattering: Examples grouped by agent, not therapeutic area
- ✅ Scalable: Add agent → add directory

## Future Agent Directories

Following the same pattern:

### epidemiology/ (future)
```python
# scripts/epidemiology/functions.py
def calculate_prevalence(incidence_rate, duration):
def segment_population(total_population, risk_factors):
def build_eligibility_funnel(prevalence, exclusion_criteria):

# scripts/epidemiology/queries.py
def get_disease_prevalence(disease, country):
def get_population_data(country, age_range):

# scripts/epidemiology/examples/obesity_prevalence.py
from epidemiology.functions import calculate_prevalence
from epidemiology.queries import get_disease_prevalence
```

### pricing/ (future)
```python
# scripts/pricing/functions.py
def calculate_irp_price(reference_countries, basket_weights):
def optimize_launch_sequence(countries, price_targets):
def assess_payer_willingness_to_pay(qaly_gain, budget_impact):

# scripts/pricing/queries.py
def get_reference_prices(drug_name, countries):
def get_reimbursement_decisions(drug_name, country):

# scripts/pricing/examples/obesity_drug_pricing.py
from pricing.functions import calculate_irp_price
from pricing.queries import get_reference_prices
```

## Import Patterns

**Standard import pattern for generated scripts**:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(script_dir))

# Import from agent domain
from {agent-name}.functions import (
    function1,
    function2
)
from {agent-name}.queries import (
    query1,
    query2
)
```

**Example** (competitive-specialist):
```python
from competitive.functions import (
    calculate_competitive_intensity,
    assess_market_maturity
)
from competitive.queries import (
    get_trial_count,
    get_phase_distribution
)
```

## File Naming Conventions

### functions.py
- **Always** `functions.py` (singular pattern for consistency)
- Contains all atomic domain logic functions
- No external dependencies except standard library

### queries.py
- **Always** `queries.py` (singular)
- Contains all MCP query wrappers for this domain
- Depends on `mcp.client`

### examples/
- **Descriptive names**: `{use_case}_{scope}.py`
- Examples:
  - `obesity_landscape.py` - Obesity competitive landscape
  - `diabetes_pipeline.py` - Diabetes pipeline analysis
  - `nash_threats.py` - NASH threat assessment
- **NOT** organized by therapeutic area subdirectories
- All examples for one agent live in that agent's `examples/` folder

## Current State

### ✅ Implemented

**competitive-specialist**:
```
scripts/competitive/
├── functions.py              ✅ 13 atomic functions
├── queries.py                ✅ 6 MCP query functions
└── examples/
    └── obesity_landscape.py  ✅ Working example (tested)
```

**Status**: Fully implemented, tested, documented

### 🔜 Future Agents

Following the same pattern when built:

- `scripts/epidemiology/` - epidemiology-analyst
- `scripts/pricing/` - pricing-strategy-analyst
- `scripts/revenue/` - revenue-synthesizer
- `scripts/market_sizing/` - market-sizing-analyst
- `scripts/opportunity/` - opportunity-identifier
- `scripts/strategy/` - strategy-synthesizer

## Documentation Alignment

### .claude/agents/ ↔ scripts/

```
.claude/agents/competitive-specialist.md
    ↓ documents
scripts/competitive/
    ├── functions.py
    ├── queries.py
    └── examples/
```

**One-to-one mapping**: Each agent file in `.claude/agents/` corresponds to one directory in `scripts/`

## Testing

**Test generated scripts**:
```bash
# Run from project root
python3 scripts/competitive/examples/obesity_landscape.py

# Expected: 7-section competitive analysis output
# Competitive Intensity: 1595/1000 (EXTREMELY INTENSE)
# Phase 3 Programs: 90 (HIGH threats)
# GLP-1 Trials: 88 active (mechanism saturation)
```

**Test functions directly**:
```python
from competitive.functions import calculate_competitive_intensity

score = calculate_competitive_intensity(
    recruiting_count=1496,
    phase3_count=90,
    leading_moa_count=88
)
# Returns: 1594.8 (EXTREMELY INTENSE)
```

**Test queries directly**:
```python
from competitive.queries import get_trial_count

count = get_trial_count('obesity', location='United States')
# Returns: 5665
```

## Key Principles

1. **Agent ownership**: Each agent owns its directory completely
2. **Atomic functions**: All domain logic in `functions.py`
3. **MCP abstraction**: All data queries in `queries.py`
4. **Examples not by therapeutic area**: Organized by agent, not indication
5. **Consistent structure**: Every agent follows the same pattern
6. **Self-contained**: Each agent directory is independent
7. **Scalable**: Add agent = add directory (no restructuring)

## Comparison: Old vs New

| Aspect | Old (Module-centric) | New (Agent-centric) |
|--------|---------------------|---------------------|
| **Organization** | By file type (modules, queries, therapeutic area) | By agent (competitive, epidemiology, pricing) |
| **Discovery** | Search multiple directories | Single directory per agent |
| **Ownership** | Unclear (shared modules) | Clear (agent owns directory) |
| **Scalability** | Requires restructuring | Add directory |
| **Alignment** | Disconnected from .claude/agents/ | Mirrors .claude/agents/ |
| **Examples** | Scattered by therapeutic area | Grouped by agent |

## Conclusion

**Agent-centric organization**:
- ✅ Mirrors `.claude/agents/` structure
- ✅ Clear domain ownership
- ✅ Easy to navigate
- ✅ Scalable (add agent → add directory)
- ✅ Self-contained (everything in one place)
- ✅ Consistent pattern across all agents

**Every agent follows the same simple structure**:
```
scripts/{agent-name}/
├── functions.py
├── queries.py
└── examples/
```

Clean. Simple. Scalable.
