# FDA (openFDA) MCP Tool Guide

**MCP Server**: `fda-mcp`
**Tool Name**: `fda_info`
**Schema Version**: Auto-generated from MCP schema (2025-11-19)

---

## 🔴 CRITICAL: Count-First Pattern (MANDATORY)

**The FDA API will FAIL without the count parameter for general and adverse_events searches.**

### Why Count-First is Non-Negotiable

| Search Type | Without Count | With Count | Reduction |
|-------------|---------------|------------|-----------|
| `general` | 67,000 tokens → **FAILS** (exceeds 25k MCP limit) | 400 tokens → **WORKS** | **99.4%** |
| `adverse_events` | 50,000+ tokens → **FAILS** | 200 tokens → **WORKS** | **99.6%** |
| `label` | 110,000 tokens → **FAILS** | Use alternatives | **N/A** |

### ✅ CORRECT: Count-First Pattern

```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 50
}
```

**Returns**: Aggregated brand name counts (e.g., "OZEMPIC: 5", "WEGOVY: 3") - ~400 tokens

### ❌ WRONG: Query Without Count

```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "limit": 100
}
```

**Returns**: Full drug records with all fields - 67,000 tokens → **EXCEEDS MCP LIMIT → FAILS**

### Count Parameters by Search Type

```python
# General searches (MANDATORY)
count = "openfda.brand_name.exact"

# Adverse events (MANDATORY)
count = "patient.reaction.reactionmeddrapt.exact"

# Recalls - count optional (small dataset)
count = None  # OK for recalls

# Shortages - count optional (small dataset)
count = None  # OK for shortages
```

**Always use `.exact` suffix** for clean, deduplicated aggregations.

---

## Available Methods

### 1. `lookup_drug` - Drug Information
Search for drug approvals, labels, adverse events, recalls, and shortages.

### 2. `lookup_device` - Medical Device Information
Search for device registrations, approvals, recalls, and adverse events.

---

## Method 1: `lookup_drug` - Drug Information

### Required Parameters

- `method`: `"lookup_drug"` (required)
- `search_term`: Drug name, ingredient, or search query (required, 1-500 characters)

### Search Types

| Search Type | Purpose | Count Required? | Token Estimate |
|-------------|---------|-----------------|----------------|
| `general` | Drug approvals, products | **YES** | 400 with count |
| `label` | Drug labels, prescribing info | **BROKEN** | Use alternatives |
| `adverse_events` | FAERS safety reports | **YES** | 200 with count |
| `recalls` | Enforcement actions | No | ~1,400 per result |
| `shortages` | Supply chain issues | No | ~800 per result |

### Search Type 1: `general` - Drug Approvals & Products

**🔴 MANDATORY: Use count parameter**

```json
{
  "method": "lookup_drug",
  "search_term": "semaglutide",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 50
}
```

**Returns**:
```json
{
  "data": {
    "results": [
      {"term": "OZEMPIC", "count": 5},
      {"term": "WEGOVY", "count": 3},
      {"term": "RYBELSUS", "count": 2}
    ]
  }
}
```

**Response Structure**: `result['data']['results']` (nested)

**Common Count Fields**:
- `openfda.brand_name.exact` - Brand names
- `openfda.generic_name.exact` - Generic names
- `openfda.manufacturer_name.exact` - Manufacturers
- `products.marketing_status.exact` - Approval status

### Search Type 2: `label` - Drug Labels

**🔴 BROKEN: Label queries return 110k tokens (4.4x MCP limit)**

**DO NOT USE**:
```json
// ❌ BROKEN: Will fail
{
  "method": "lookup_drug",
  "search_term": "aspirin",
  "search_type": "label"
}
```

**Alternatives**:
1. Use count-first on `general` to get drug list
2. Query specific drugs with field selection (via Python wrapper alternatives)
3. See: `.claude/mcp/servers/fda_mcp/alternatives.py`

### Search Type 3: `adverse_events` - FAERS Safety Data

**🔴 MANDATORY: Use count parameter**

```json
{
  "method": "lookup_drug",
  "search_term": "semaglutide",
  "search_type": "adverse_events",
  "count": "patient.reaction.reactionmeddrapt.exact",
  "limit": 20
}
```

**Returns**: Top adverse event terms with occurrence counts

```json
{
  "data": {
    "results": [
      {"term": "NAUSEA", "count": 11180},
      {"term": "VOMITING", "count": 7205},
      {"term": "DIARRHOEA", "count": 6226}
    ]
  }
}
```

**Search Term Syntax**:
- General: `"semaglutide"`
- Field-specific: `"patient.drug.medicinalproduct:semaglutide"`

**Common Count Fields**:
- `patient.reaction.reactionmeddrapt.exact` - MedDRA reaction terms (most useful)
- `patient.drug.medicinalproduct.exact` - Drug names
- `serious.exact` - Serious event indicator

### Search Type 4: `recalls` - Enforcement Actions

**Count optional** (dataset typically < 50 records)

```json
{
  "method": "lookup_drug",
  "search_term": "semaglutide",
  "search_type": "recalls",
  "limit": 50
}
```

**Token estimate**: ~1,400 per result (manageable without count)

### Search Type 5: `shortages` - Supply Chain Issues

**Count optional** (dataset typically < 100 records)

```json
{
  "method": "lookup_drug",
  "search_term": "insulin",
  "search_type": "shortages",
  "limit": 50
}
```

**Token estimate**: ~800 per result (manageable without count)

---

## Search Term Strategies

### ✅ Search Terms That WORK

| Search Term | Type | Example Results | Notes |
|-------------|------|-----------------|-------|
| **GLP-1** | Mechanism | 13 brands | Broad mechanism term |
| **NSAID** | Class | 25+ brands | Anti-inflammatory class |
| **semaglutide** | Generic name | 3 products (OZEMPIC, WEGOVY, RYBELSUS) | Specific drug |
| **lisinopril** | Generic name | 19 products | ACE inhibitor |
| **atorvastatin** | Generic name | 31 products | Statin |
| **aspirin** | Generic name | Many products | Common drug |
| **ibuprofen** | Generic name | Many products | OTC drug |

### ❌ Search Terms That FAIL (404)

| Search Term | Why It Fails | Alternative |
|-------------|--------------|-------------|
| **ACE inhibitor** | Natural language class name | Search specific drugs: `lisinopril`, `enalapril`, `ramipril` |
| **beta blocker** | Natural language class name | Search specific drugs: `metoprolol`, `atenolol`, `carvedilol` |
| **statin** | Natural language class name | Search specific drugs: `atorvastatin`, `simvastatin`, `rosuvastatin` |
| **drug1 OR drug2** | OR operator not supported | Run parallel queries for each drug |

### Search Strategy Decision Tree

```
Start with specific drug name (always works)
    ↓
If need drug class:
    ↓
Try mechanism term (e.g., "GLP-1", "NSAID")
    ↓
If 404 error:
    ↓
Search individual drugs in parallel
    ↓
Combine results programmatically
```

### Field-Specific Search Syntax

**General searches**:
```json
{"search_term": "openfda.brand_name:OZEMPIC"}
```

**Adverse events**:
```json
{"search_term": "patient.drug.medicinalproduct:semaglutide"}
```

**Manufacturer**:
```json
{"search_term": "openfda.manufacturer_name:Pfizer"}
```

---

## Multiple Drugs Strategy

**🔴 OR operators DON'T WORK**

### ❌ WRONG: Using OR Operator
```json
{
  "search_term": "semaglutide OR liraglutide"
}
```
**Result**: 404 error

### ✅ CORRECT: Parallel Queries
```python
# Query 1
result1 = lookup_drug(
    search_term="semaglutide",
    search_type="general",
    count="openfda.brand_name.exact",
    limit=50
)

# Query 2
result2 = lookup_drug(
    search_term="liraglutide",
    search_type="general",
    count="openfda.brand_name.exact",
    limit=50
)

# Combine results programmatically
all_brands = {}
for item in result1['data']['results']:
    all_brands[item['term']] = item['count']
for item in result2['data']['results']:
    all_brands[item['term']] = all_brands.get(item['term'], 0) + item['count']
```

---

## Optional Parameters

### `limit` - Result Limit
```json
{
  "limit": 100  // 1-100, default: 10
}
```

**Usage**:
- With count queries: Higher limit = more aggregated terms
- Without count: Higher limit = more full records (token explosion)

### `pharm_class` - Pharmaceutical Class Filter
```json
{
  "pharm_class": "GLP-1 Agonist"
}
```

Filter results by pharmacological classification.

### `field_exists` - Field Existence Filter
```json
{
  "field_exists": "openfda.application_number"
}
```

Only return records where specified field exists.

### Field Selection Parameters

**🔴 WARNING: Field selection currently broken for some search types**

```json
{
  "fields_for_general": "openfda.brand_name,openfda.generic_name,products.marketing_status",
  "fields_for_adverse_events": "patient.reaction,serious",
  "fields_for_recalls": "recall_number,reason_for_recall",
  "fields_for_shortages": "product_names,shortage_status",
  "fields_for_label": "indications_and_usage,warnings"  // BROKEN
}
```

**Max length**: 1000 characters per field parameter

**Use cases**:
- Token reduction (70-90% savings on detail queries)
- Extract only needed fields
- Faster processing

**Note**: Works for some search types, broken for labels.

---

## Method 2: `lookup_device` - Medical Device Information

### Required Parameters

- `method`: `"lookup_device"` (required)
- `search_term`: Device name or search query (required)

### Device Search Types

| Search Type | Purpose |
|-------------|---------|
| `device_registration` | Registered device establishments |
| `device_pma` | Premarket approval (Class III devices) |
| `device_510k` | 510(k) clearances (Class II devices) |
| `device_udi` | Unique Device Identifiers |
| `device_recalls` | Device recall notices |
| `device_adverse_events` | MAUDE adverse events |
| `device_classification` | Device classifications |

### Device Search Examples

#### Device Registration
```json
{
  "method": "lookup_device",
  "search_term": "pacemaker",
  "search_type": "device_registration",
  "limit": 50
}
```

#### Device 510(k) Clearances
```json
{
  "method": "lookup_device",
  "search_term": "insulin pump",
  "search_type": "device_510k",
  "limit": 50
}
```

#### Device Adverse Events
```json
{
  "method": "lookup_device",
  "search_term": "pacemaker",
  "search_type": "device_adverse_events",
  "limit": 100
}
```

**Note**: Device queries generally don't require count-first pattern (smaller datasets).

---

## Response Format & Parsing

### Standard Response Structure

```json
{
  "data": {
    "results": [
      // Array of results
    ]
  },
  "metadata": {
    // Query metadata
  }
}
```

**🔴 CRITICAL**: Response is **nested** under `data.results`

### Parsing Count Results

```python
result = lookup_drug(
    search_term="GLP-1",
    search_type="general",
    count="openfda.brand_name.exact",
    limit=50
)

# Extract brand name counts
brands = {}
for item in result['data']['results']:
    brand = item.get('term', 'Unknown')
    count = item.get('count', 0)
    brands[brand] = count

# Sort by count
sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
```

### Parsing Full Records (Non-Count)

```python
result = lookup_drug(
    search_term="aspirin",
    search_type="recalls",
    limit=50
)

# Extract recalls
recalls = []
for item in result['data']['results']:
    recalls.append({
        'recall_number': item.get('recall_number', 'N/A'),
        'reason': item.get('reason_for_recall', 'N/A'),
        'status': item.get('status', 'N/A'),
        'product_description': item.get('product_description', 'N/A')
    })
```

### Safe Dictionary Access

**Always use `.get()` method** to avoid KeyError:

```python
# ❌ WRONG: Direct access
brand = result['openfda']['brand_name'][0]  # KeyError if field missing

# ✅ CORRECT: Safe access
openfda = result.get('openfda', {})
brand_names = openfda.get('brand_name', ['Unknown'])
brand = brand_names[0] if brand_names else 'Unknown'
```

**See**: `.claude/.context/code-examples/fda_json_parsing.md` for complete patterns.

---

## Common Use Cases

### 1. Find All Approved Drugs for a Condition

**Strategy**: Use indication field search (if available) or therapeutic class

```json
{
  "method": "lookup_drug",
  "search_term": "diabetes",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 100
}
```

**Note**: This searches across all FDA fields. For precision, search specific drug names known to treat the condition.

### 2. Get Safety Profile for a Drug

```json
{
  "method": "lookup_drug",
  "search_term": "semaglutide",
  "search_type": "adverse_events",
  "count": "patient.reaction.reactionmeddrapt.exact",
  "limit": 20
}
```

**Returns**: Top 20 adverse event types with occurrence counts.

### 3. Check for Active Recalls

```json
{
  "method": "lookup_drug",
  "search_term": "insulin",
  "search_type": "recalls",
  "limit": 50
}
```

### 4. Monitor Drug Shortages

```json
{
  "method": "lookup_drug",
  "search_term": "amoxicillin",
  "search_type": "shortages",
  "limit": 50
}
```

### 5. Find All Drugs by Manufacturer

```json
{
  "method": "lookup_drug",
  "search_term": "openfda.manufacturer_name:Pfizer",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 100
}
```

### 6. Compare Multiple Drugs (Parallel Queries)

```python
drugs = ["semaglutide", "liraglutide", "dulaglutide"]

results = {}
for drug in drugs:
    result = lookup_drug(
        search_term=drug,
        search_type="general",
        count="openfda.brand_name.exact",
        limit=50
    )
    results[drug] = result['data']['results']
```

---

## Best Practices

### ✅ DO

1. **Always use count-first for general and adverse_events**:
   ```json
   {"count": "openfda.brand_name.exact"}
   ```

2. **Use `.exact` suffix on count parameters**:
   ```json
   {"count": "openfda.brand_name.exact"}  // Clean aggregation
   ```

3. **Parse responses with `.get()` method**:
   ```python
   brand = result.get('openfda', {}).get('brand_name', ['Unknown'])[0]
   ```

4. **Handle nested response structure**:
   ```python
   results = response['data']['results']
   ```

5. **Use specific drug names for reliable results**:
   ```json
   {"search_term": "lisinopril"}  // Works
   ```

6. **Run parallel queries for multiple drugs**:
   ```python
   [query(drug1), query(drug2), query(drug3)]
   ```

### ❌ DON'T

1. **Don't skip count parameter for general/adverse_events**:
   ```json
   // ❌ WRONG: Will fail with token overflow
   {"search_term": "GLP-1", "search_type": "general"}
   ```

2. **Don't use OR operators**:
   ```json
   // ❌ WRONG: Returns 404
   {"search_term": "drug1 OR drug2"}
   ```

3. **Don't use natural language class names**:
   ```json
   // ❌ WRONG: Returns 404
   {"search_term": "beta blocker"}

   // ✅ CORRECT: Use specific drugs
   {"search_term": "metoprolol"}
   ```

4. **Don't use direct dictionary access**:
   ```python
   # ❌ WRONG: Raises KeyError
   brand = result['openfda']['brand_name'][0]

   # ✅ CORRECT: Use .get()
   brand = result.get('openfda', {}).get('brand_name', ['Unknown'])[0]
   ```

5. **Don't use label search type**:
   ```json
   // ❌ BROKEN: 110k tokens, exceeds limit
   {"search_type": "label"}
   ```

6. **Don't forget `.exact` suffix on counts**:
   ```json
   // ⚠️ INCONSISTENT: May work but unreliable
   {"count": "openfda.brand_name"}

   // ✅ CORRECT: Reliable aggregation
   {"count": "openfda.brand_name.exact"}
   ```

---

## Known Quirks & Limitations

### 1. Count-First Pattern Mandatory
- **General searches without count**: 67k tokens → FAILS
- **Adverse events without count**: 50k+ tokens → FAILS
- **Solution**: Always use count parameter
- **Exception**: Recalls and shortages (small datasets)

### 2. Label Queries Broken
- Single label query: 110k tokens (4.4x MCP limit)
- Field selection parameter broken
- **Solution**: Use alternatives in `.claude/mcp/servers/fda_mcp/alternatives.py`

### 3. OR Operators Not Supported
- `"drug1 OR drug2"` returns 404
- **Solution**: Run parallel queries, combine results programmatically

### 4. Natural Language Class Names Fail
- "ACE inhibitor", "beta blocker", "statin" → 404
- Mechanism terms sometimes work: "GLP-1", "NSAID"
- **Solution**: Use specific drug names

### 5. Nested Response Structure
- Results under `response['data']['results']`
- Different from some other APIs
- **Solution**: Always access via `['data']['results']`

### 6. Field-Specific Search Syntax
- Use colon notation: `"openfda.brand_name:DRUGNAME"`
- Different from boolean AND/OR
- **Solution**: Follow documented field syntax patterns

### 7. .exact Suffix Required for Clean Counts
- Without: May return inconsistent aggregations
- With: Clean, deduplicated counts
- **Solution**: Always use `.exact` for count fields

---

## Performance Optimization

### Token Reduction Strategies

#### 1. Count-First Pattern (99.4% reduction)
```json
// Without count: 67,000 tokens
{"search_term": "GLP-1", "search_type": "general"}

// With count: 400 tokens (99.4% reduction)
{"search_term": "GLP-1", "search_type": "general", "count": "openfda.brand_name.exact"}
```

#### 2. Field Selection (70-90% reduction)
```json
{
  "search_term": "aspirin",
  "search_type": "general",
  "fields_for_general": "openfda.brand_name,openfda.generic_name"
}
```

**Note**: Field selection currently broken for some search types.

#### 3. Precise Search Terms (Reduce result count)
```json
// Less precise: Returns 100+ products
{"search_term": "insulin"}

// More precise: Returns 3 products
{"search_term": "openfda.brand_name:OZEMPIC"}
```

#### 4. Appropriate Limits
```json
{
  "limit": 20  // Start small for count queries
}
```

Only increase limit if you need more aggregated terms.

---

## Quick Reference

| Task | Search Type | Count Required | Example |
|------|-------------|----------------|---------|
| Drug approvals | `general` | **YES** | `count="openfda.brand_name.exact"` |
| Drug labels | `label` | **BROKEN** | Use alternatives |
| Safety signals | `adverse_events` | **YES** | `count="patient.reaction.reactionmeddrapt.exact"` |
| Recalls | `recalls` | No | Simple query |
| Shortages | `shortages` | No | Simple query |
| Device registrations | `device_registration` | No | Simple query |
| Device clearances | `device_510k` | No | Simple query |
| Device approvals | `device_pma` | No | Simple query |
| Device adverse events | `device_adverse_events` | No | Simple query |

---

## Related Resources

- **JSON Parsing Pattern**: `.claude/.context/code-examples/fda_json_parsing.md`
- **Alternative Methods**: `.claude/mcp/servers/fda_mcp/alternatives.py`
- **Skills Library**: Check existing FDA skills for proven patterns
- **Official API Docs**: https://open.fda.gov/apis/

---

## FAQ: Common Issues & Solutions

### Q: Why does my query return 404?
**A:** FDA API has specific limitations:
- ❌ Broad class terms: "ACE inhibitor", "beta blocker", "statin"
- ❌ OR operators: "drug1 OR drug2"
- ✅ **Solution**: Use specific drug names or working mechanism terms ("GLP-1", "NSAID")

### Q: Why is my query failing with token overflow?
**A:** You forgot the count parameter!
- General/adverse_events without count: 50k-67k tokens → **FAILS**
- General/adverse_events with count: 200-400 tokens → **WORKS**
- **Always use count-first for these search types**

### Q: What's the difference between count and regular queries?
**A:**
- **Count query**: Returns aggregated counts (e.g., brand name list with counts) - minimal tokens
- **Regular query**: Returns full records (all fields, all products) - massive tokens
- **Strategy**: Count first (Step 1) → then get details if needed (Step 2)

### Q: When can I skip the count parameter?
**A:** Only for small datasets:
- Recalls (typically <50 records)
- Shortages (typically <100 records)
- Device queries (generally smaller)
- **All other searches**: Use count-first, no exceptions

### Q: How do I search for multiple drugs?
**A:** Run parallel queries:
```python
drugs = ["semaglutide", "liraglutide"]
results = []
for drug in drugs:
    result = lookup_drug(
        search_term=drug,
        search_type="general",
        count="openfda.brand_name.exact"
    )
    results.append(result)
```

### Q: Why do I need the .exact suffix?
**A:**
- Without `.exact`: May return inconsistent aggregations
- With `.exact`: Clean, deduplicated counts
- **Always use `.exact`** for count parameters

### Q: My adverse events query is too slow - what do I do?
**A:** Use count-first with reaction aggregation:
```json
{
  "search_term": "drugname",
  "search_type": "adverse_events",
  "count": "patient.reaction.reactionmeddrapt.exact",
  "limit": 20
}
```
Returns top 20 adverse event types - perfect for safety signal detection.

### Q: Can I search by indication/condition?
**A:** YES! Use the adverse events database `patient.drug.drugindication` field:

**✅ BREAKTHROUGH METHOD (Adverse Events Discovery)**:
```json
{
  "search_term": "patient.drug.drugindication:obesity",
  "search_type": "adverse_events",
  "count": "patient.drug.openfda.brand_name.exact",
  "limit": 100
}
```

**How It Works**:
- The `patient.drug.drugindication` field captures the condition for which a drug was prescribed when an adverse event was reported
- This provides real-world drug-indication relationships from actual prescriptions
- Returns drugs ranked by adverse event volume (proxy for prescribing frequency)

**Example Use Cases**:
- Find all obesity drugs: `patient.drug.drugindication:obesity`
- Find diabetes drugs: `patient.drug.drugindication:diabetes`
- Find cancer drugs: `patient.drug.drugindication:cancer`
- Find hypertension drugs: `patient.drug.drugindication:hypertension`

**Why This Works When Label Search Fails**:
- ❌ Label search: `indications_and_usage` field → 67k tokens → Exceeds MCP limit → FAILS
- ❌ Field selection: `fields_for_general` parameter → BROKEN → FAILS
- ✅ Adverse events: `drugindication` + count → 200 tokens → WORKS!

**Multi-Term Strategy** (Recommended):
```python
indication_terms = ["obesity", "weight control", "overweight"]
all_drugs = {}

for term in indication_terms:
    result = lookup_drug(
        search_term=f"patient.drug.drugindication:{term}",
        search_type="adverse_events",
        count="patient.drug.openfda.brand_name.exact",
        limit=100
    )
    # Aggregate results across all terms
```

**Filtering Tip**:
Results may include noise (drugs mentioned incidentally). Filter to drugs with:
- **Primary indication**: >=400 adverse events for the specific condition, OR
- **High ratio**: Condition-specific events >= 25% of total events

**Limitations**:
- Captures drugs prescribed for the indication (includes off-label use)
- Does NOT distinguish FDA-approved vs off-label (shows real-world usage)
- Only includes drugs with reported adverse events
- No direct link to approval status

**Alternative (Less Reliable)**:
- Try searching the condition term in general search (searches across all fields)
- Use specific drug names if you know them
- Use OpenTargets MCP for target-disease associations

---

**Last Updated**: Auto-generated from MCP schema - 2025-11-19
**Critical Pattern**: Count-first mandatory for general/adverse_events queries
