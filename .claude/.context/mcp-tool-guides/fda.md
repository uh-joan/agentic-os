# FDA Database (mcp__fda-mcp__fda_info)

## When to use
- Drug approvals: Find FDA approval status, dates, indications
- Safety data: Adverse event reports (FAERS)
- Drug recalls: Enforcement actions, voluntary recalls
- Drug shortages: Supply chain issues
- Label information: Prescribing information, warnings

## Methods
```json
{
  "method": "lookup_drug",
  "search_type": "general",     // Drug information & approvals
  "search_type": "label",        // Prescribing information
  "search_type": "adverse_events", // Safety signals
  "search_type": "recalls",      // Recall notices
  "search_type": "shortages"     // Supply issues
}
```

## Parameter patterns

### Simple drug search
```json
{
  "method": "lookup_drug",
  "search_term": "drug_name",
  "search_type": "general",
  "limit": 100
}
```

### Field-specific search
```json
{
  "method": "lookup_drug",
  "search_term": "openfda.brand_name:DRUGNAME",
  "fields_for_general": "openfda.brand_name,products.marketing_status",
  "search_type": "general"
}
```

### Adverse events
```json
{
  "method": "lookup_drug",
  "search_term": "patient.drug.medicinalproduct:drugname",
  "search_type": "adverse_events",
  "limit": 100
}
```

## Key response fields
- `openfda.brand_name` - Brand name(s) as array
- `openfda.generic_name` - Generic name
- `openfda.application_number` - NDA/BLA number
- `products.marketing_status` - Approval status
- `products.dosage_form` - Formulation type
- `products.route` - Administration route

## Optimization rules

### CRITICAL: Count-First Pattern (MANDATORY)
**ALWAYS use count parameter first** - this is non-negotiable for FDA queries.

#### ✅ CORRECT: Count-first pattern
```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "count": "openfda.brand_name.exact",
  "limit": 50
}
```
**Result**: ~400 tokens, returns 13 brand names

#### ❌ WRONG: Full query without count
```json
{
  "method": "lookup_drug",
  "search_term": "GLP-1",
  "search_type": "general",
  "limit": 100
}
```
**Result**: 67,000 tokens (EXCEEDS 25k MCP LIMIT - query will FAIL)

### Count Parameter Patterns
- **General searches**: `count="openfda.brand_name.exact"`
- **Adverse events**: `count="patient.reaction.reactionmeddrapt.exact"`
- **Skip count only for**: recalls, shortages (small datasets)

### Search Term Strategies

#### Tested Search Terms (Use These)

| Search Term | Status | Results | Notes |
|-------------|--------|---------|-------|
| **GLP-1** | ✅ WORKS | 13 brands | Mechanism-based term |
| **NSAID** | ✅ WORKS | 25+ brands | Class-based term |
| **lisinopril** | ✅ WORKS | 19 products | Specific drug name |
| **atorvastatin** | ✅ WORKS | 31 products | Specific drug name |
| **semaglutide** | ✅ WORKS | 3 products | Specific drug name |
| **aspirin** | ✅ WORKS | Many products | Generic term |
| **ibuprofen** | ✅ WORKS | Many products | Generic term |

| Search Term | Status | Error | Alternative |
|-------------|--------|-------|-------------|
| **ACE inhibitor** | ❌ 404 | Not Found | Search "lisinopril", "enalapril", "ramipril" separately |
| **beta blocker** | ❌ 404 | Not Found | Search "metoprolol", "atenolol", "carvedilol" separately |
| **statin** | ❌ 404 | Not Found | Search "atorvastatin", "simvastatin", "rosuvastatin" separately |
| **drug1 OR drug2** | ❌ 404 | OR not supported | Run parallel queries for drug1 and drug2 |

#### Strategy Guidelines
- ✅ **Try mechanism-based terms first**: "GLP-1", "NSAID" (often work)
- ✅ **Use specific drug names**: Always works - "lisinopril", "aspirin"
- ✅ **Search generic names**: "ibuprofen" better than "Advil"
- ❌ **Avoid OR operators**: FDA API doesn't support them
- ❌ **Avoid natural language**: "beta blocker" fails, "metoprolol" works

#### For Multiple Drugs in Same Class
Run parallel count queries, then combine results:
```json
// ❌ WRONG: OR operator fails
{"search_term": "lisinopril OR enalapril"}

// ✅ RIGHT: Parallel queries
[
  {"search_term": "lisinopril", "count": "openfda.brand_name.exact"},
  {"search_term": "enalapril", "count": "openfda.brand_name.exact"},
  {"search_term": "ramipril", "count": "openfda.brand_name.exact"}
]
```

### Token Savings
- Count-first: **99.4% token reduction** (400 vs 67,000 tokens)
- With field selection: **70-90% reduction** on detail queries

## FAQ: Common API Issues & Solutions

### Q: Why does my search return "404 - Not Found"?
**A:** FDA API has specific limitations:
- ❌ **Broad class terms may not work**: "ACE inhibitor", "beta blocker", "statin" → 404
- ❌ **OR operators don't work**: "drug1 OR drug2" → 404
- ✅ **Solution**: Use specific drug names (e.g., "lisinopril", "atorvastatin") or broad mechanism terms that work (e.g., "GLP-1", "NSAID")

**Working broad terms (tested)**:
- "GLP-1" ✅ (returns 13 brands)
- "NSAID" ✅ (returns 25+ brands)

**Non-working broad terms**:
- "ACE inhibitor" ❌ (returns 404)
- "beta blocker" ❌ (returns 404)
- "statin" ❌ (returns 404)

**Workaround**: Search specific drug names like "lisinopril", "metoprolol", "atorvastatin"

### Q: Why is my query exceeding token limits?
**A:** You forgot the count parameter!
- ❌ Without count: Full FDA response = 50,000-67,000 tokens → **FAILS** (exceeds 25k MCP limit)
- ✅ With count: Aggregated response = 400-1,000 tokens → **WORKS**

**Always use count-first for FDA queries** - it's non-negotiable.

### Q: What's the difference between count and regular queries?
**A:**
- **Count query**: Returns aggregated counts (e.g., "OZEMPIC: 1", "WEGOVY: 1") - minimal tokens
- **Regular query**: Returns full drug records (approval dates, sponsors, formulations, etc.) - massive tokens
- **Strategy**: Count first (Step 1) → then retrieve specific items (Step 2)

### Q: When should I skip the count parameter?
**A:** Only for small datasets:
- Recalls (typically <50 records)
- Shortages (typically <100 records)
- **All other searches**: Use count-first, no exceptions

### Q: How do I search for multiple drugs?
**A:** Run parallel count queries, don't use OR:
```json
// ❌ WRONG: Will return 404
{"search_term": "semaglutide OR liraglutide"}

// ✅ RIGHT: Run separately in parallel
[
  {"search_term": "semaglutide", "count": "openfda.brand_name.exact"},
  {"search_term": "liraglutide", "count": "openfda.brand_name.exact"}
]
```

### Q: Why do I need the .exact suffix on count parameters?
**A:**
- `"count": "openfda.brand_name"` → May return inconsistent aggregations
- `"count": "openfda.brand_name.exact"` → Returns clean, deduplicated counts
- **Always use .exact** for count aggregations

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
This returns top 20 adverse event types by frequency - perfect for safety signal detection.
