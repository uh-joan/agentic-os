# Company Pipeline Web Scraper

**Skill Name**: `scrape_company_pipeline`

**Category**: Data Collection / Web Scraping

**Complexity**: High

**Purpose**: Automatically extract drug pipeline data from pharmaceutical company websites, capturing programs not yet in ClinicalTrials.gov (preclinical, discovery) and company-specific status updates.

---

## Overview

Pharmaceutical companies maintain pipeline pages on their websites with structured tables/lists of development programs. This skill scrapes that data to:
- **Fill gaps in public databases**: Preclinical, discovery programs not in CT.gov
- **Get company perspective**: Internal status, strategic focus, nomenclature
- **Real-time updates**: Latest pipeline changes before press releases

**Key Challenge**: Most pipeline pages are JavaScript-rendered (React, Angular) requiring Playwright/Selenium, not simple HTML parsing.

**Use Cases**:
- BD target screening (identify early-stage assets)
- Competitive intelligence (track competitor R&D focus)
- Portfolio analysis (map company's therapeutic area strategy)
- Deal sourcing (find assets suitable for licensing/acquisition)

---

## Input Schema

```python
{
    "company": str,                     # Required: Company name (e.g., "Pfizer", "Merck")
    "scrape_config": {
        "include_preclinical": bool,    # Include discovery/preclinical programs (default: True)
        "include_approved": bool,       # Include marketed drugs (default: False)
        "therapeutic_areas": List[str], # Filter by TA (default: all TAs)
        "min_phase": str               # Minimum phase to include (default: "Discovery")
    },
    "output_options": {
        "format": str,                  # "json", "csv", "markdown" (default: "json")
        "include_metadata": bool,       # Include scrape timestamp, source URL (default: True)
        "deduplicate": bool            # Remove duplicate entries (default: True)
    }
}
```

---

## Output Schema

```python
{
    "company": str,
    "scrape_metadata": {
        "scraped_at": str,              # ISO timestamp
        "source_url": str,              # Pipeline page URL
        "scraper_version": str,
        "success": bool,
        "warnings": List[str]           # Any parsing issues
    },
    "pipeline": List[{
        "program_name": str,            # Drug name or code
        "indication": str,              # Target disease
        "therapeutic_area": str,        # Oncology, CNS, etc.
        "phase": str,                   # "Discovery", "Preclinical", "Phase 1", etc.
        "mechanism": str,               # MOA (if available)
        "modality": str,                # Small molecule, biologic, etc.
        "route": str,                   # Oral, IV, SC, etc. (if available)
        "partnered": bool,              # Collaboration/licensing
        "partner": str,                 # Partner company (if applicable)
        "designations": List[str],      # ["Breakthrough", "Orphan", "Fast Track"]
        "next_milestone": str,          # Expected next event (if available)
        "notes": str                    # Additional details
    }],
    "summary_stats": {
        "total_programs": int,
        "by_phase": Dict[str, int],     # {"Phase 1": 15, "Phase 2": 23, ...}
        "by_therapeutic_area": Dict[str, int]
    }
}
```

---

## Algorithm

### Step 1: Company URL Mapping

```python
# Company pipeline URL database
COMPANY_PIPELINE_URLS = {
    "Pfizer": {
        "url": "https://www.pfizer.com/science/drug-product-pipeline",
        "scraper_strategy": "react_spa",
        "table_selector": "div.pipeline-table",
        "last_verified": "2025-01-01"
    },
    "Merck": {
        "url": "https://www.merck.com/research/pipeline/",
        "scraper_strategy": "static_html",
        "table_selector": "table.pipeline-grid",
        "last_verified": "2025-01-01"
    },
    "Roche": {
        "url": "https://www.roche.com/research-and-development/our-pipeline",
        "scraper_strategy": "react_spa",
        "table_selector": "div[data-component='PipelineTable']",
        "last_verified": "2025-01-01"
    },
    # ... 50+ major pharmas
}

def get_company_config(company: str) -> Dict:
    """Look up scraping configuration for company."""

    # Try exact match
    if company in COMPANY_PIPELINE_URLS:
        return COMPANY_PIPELINE_URLS[company]

    # Try fuzzy match (handle "Pfizer Inc." vs "Pfizer")
    for key in COMPANY_PIPELINE_URLS:
        if company.lower() in key.lower() or key.lower() in company.lower():
            return COMPANY_PIPELINE_URLS[key]

    # Fallback: Search engine query
    return {
        "url": search_google_for_pipeline(company),
        "scraper_strategy": "auto_detect",
        "last_verified": None
    }
```

### Step 2: Playwright-Based Scraping

```python
from playwright.sync_api import sync_playwright
import time

def scrape_with_playwright(url: str, selector: str) -> str:
    """Render JavaScript and extract content."""

    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to pipeline page
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for content to load (JavaScript rendering)
            page.wait_for_selector(selector, timeout=10000)

            # Additional wait for dynamic content
            time.sleep(2)

            # Extract HTML
            content = page.content()

            browser.close()
            return content

        except Exception as e:
            browser.close()
            raise ScrapingError(f"Failed to load {url}: {e}")
```

### Step 3: Intelligent Parsing (Multiple Strategies)

```python
def parse_pipeline_page(html_content: str, strategy: str) -> List[Dict]:
    """Parse HTML based on detected strategy."""

    if strategy == "react_spa":
        return parse_react_pipeline(html_content)
    elif strategy == "static_html":
        return parse_static_html_pipeline(html_content)
    elif strategy == "pdf_table":
        return parse_pdf_pipeline(html_content)
    else:
        return auto_detect_and_parse(html_content)

def parse_react_pipeline(html: str) -> List[Dict]:
    """Parse React-rendered pipeline tables."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    # Common React patterns
    pipeline_rows = soup.find_all(['tr', 'div'], class_=lambda x: x and 'pipeline' in x.lower())

    programs = []
    for row in pipeline_rows:
        program = {
            "program_name": extract_text(row, ['data-drug-name', 'title', 'h3', 'h4']),
            "indication": extract_text(row, ['data-indication', 'indication', 'disease']),
            "phase": extract_text(row, ['data-phase', 'phase', 'stage']),
            "therapeutic_area": extract_text(row, ['data-ta', 'therapeutic-area']),
            "mechanism": extract_text(row, ['data-moa', 'mechanism']),
        }

        # Skip if missing critical fields
        if program["program_name"] and program["phase"]:
            programs.append(program)

    return programs

def extract_text(element, possible_selectors: List[str]) -> str:
    """Try multiple CSS selectors to extract text."""

    for selector in possible_selectors:
        # Try as attribute
        if element.has_attr(selector):
            return element[selector]

        # Try as nested element
        nested = element.find(class_=selector) or element.find(selector)
        if nested:
            return nested.get_text(strip=True)

    return ""
```

### Step 4: Data Normalization

```python
def normalize_pipeline_data(raw_programs: List[Dict]) -> List[Dict]:
    """Standardize fields across companies."""

    normalized = []

    for program in raw_programs:
        # Standardize phase naming
        phase = standardize_phase(program.get('phase', 'Unknown'))

        # Extract designations from text
        designations = extract_designations(
            program.get('notes', '') + ' ' + program.get('program_name', '')
        )

        # Detect partnerships
        partnered = any(keyword in program.get('notes', '').lower()
                       for keyword in ['licensed', 'collaboration', 'partnered', 'with'])

        normalized.append({
            "program_name": clean_drug_name(program.get('program_name', '')),
            "indication": program.get('indication', ''),
            "therapeutic_area": standardize_ta(program.get('therapeutic_area', '')),
            "phase": phase,
            "mechanism": program.get('mechanism', ''),
            "modality": infer_modality(program),
            "route": program.get('route', ''),
            "partnered": partnered,
            "partner": extract_partner(program.get('notes', '')),
            "designations": designations,
            "next_milestone": program.get('next_milestone', ''),
            "notes": program.get('notes', '')
        })

    return normalized

def standardize_phase(raw_phase: str) -> str:
    """Map company-specific phase names to standard."""

    phase_mapping = {
        "research": "Discovery",
        "discovery": "Discovery",
        "lead optimization": "Discovery",
        "preclinical": "Preclinical",
        "pre-clinical": "Preclinical",
        "phase i": "Phase 1",
        "phase 1": "Phase 1",
        "phase ii": "Phase 2",
        "phase 2": "Phase 2",
        "phase iii": "Phase 3",
        "phase 3": "Phase 3",
        "nda": "NDA Filed",
        "bla": "BLA Filed",
        "submitted": "Regulatory Submission",
        "approved": "Approved",
        "marketed": "Approved"
    }

    for key, standard in phase_mapping.items():
        if key in raw_phase.lower():
            return standard

    return raw_phase  # Return as-is if no match
```

### Step 5: Deduplication & Validation

```python
def deduplicate_programs(programs: List[Dict]) -> List[Dict]:
    """Remove duplicate entries (same drug, indication, phase)."""

    seen = set()
    unique = []

    for program in programs:
        # Create unique key
        key = (
            program['program_name'].lower(),
            program['indication'].lower(),
            program['phase']
        )

        if key not in seen:
            seen.add(key)
            unique.append(program)

    return unique

def validate_pipeline_data(programs: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Validate and flag suspicious entries."""

    valid_programs = []
    warnings = []

    for program in programs:
        # Check for required fields
        if not program['program_name']:
            warnings.append(f"Missing program name, skipping entry")
            continue

        if not program['phase']:
            warnings.append(f"{program['program_name']}: Missing phase, defaulting to Unknown")
            program['phase'] = "Unknown"

        # Check for gibberish (common scraping error)
        if len(program['program_name']) < 3 or not any(c.isalpha() for c in program['program_name']):
            warnings.append(f"Suspicious program name: {program['program_name']}, skipping")
            continue

        valid_programs.append(program)

    return valid_programs, warnings
```

---

## Error Handling & Fallbacks

### Fallback Strategies

```python
def scrape_company_pipeline_with_fallbacks(company: str) -> Dict:
    """Try multiple scraping strategies in order."""

    strategies = [
        ("playwright", scrape_with_playwright),
        ("selenium", scrape_with_selenium),     # Backup if Playwright fails
        ("static_html", scrape_with_requests),  # Fallback for simple pages
        ("pdf_extract", scrape_from_pdf)        # Some companies use PDF pipeline docs
    ]

    errors = []

    for strategy_name, strategy_func in strategies:
        try:
            result = strategy_func(company)
            if result['pipeline']:  # Success if any programs extracted
                result['scraper_strategy_used'] = strategy_name
                return result
        except Exception as e:
            errors.append(f"{strategy_name}: {str(e)}")

    # All strategies failed
    return {
        "success": False,
        "company": company,
        "pipeline": [],
        "errors": errors,
        "recommendation": "Manual review required - website may have restructured"
    }
```

### Rate Limiting & Politeness

```python
import time
from functools import wraps

# Rate limiter decorator
last_request_time = {}

def rate_limit(min_delay_seconds: float = 2.0):
    """Ensure minimum delay between requests to same domain."""

    def decorator(func):
        @wraps(func)
        def wrapper(url: str, *args, **kwargs):
            domain = extract_domain(url)

            # Check last request time for this domain
            if domain in last_request_time:
                elapsed = time.time() - last_request_time[domain]
                if elapsed < min_delay_seconds:
                    time.sleep(min_delay_seconds - elapsed)

            # Execute request
            result = func(url, *args, **kwargs)

            # Update last request time
            last_request_time[domain] = time.time()

            return result
        return wrapper
    return decorator

@rate_limit(min_delay_seconds=3.0)  # 3 seconds between requests
def scrape_with_playwright(url: str, selector: str):
    # ... scraping logic ...
    pass
```

---

## Visualization & Output

### Terminal Output (ASCII Table)

```python
def print_pipeline_summary(result: Dict):
    """Pretty print pipeline in terminal."""

    from tabulate import tabulate

    print(f"\n{'='*80}")
    print(f"  {result['company']} Pipeline Summary")
    print(f"  Scraped: {result['scrape_metadata']['scraped_at']}")
    print(f"  Source: {result['scrape_metadata']['source_url']}")
    print(f"{'='*80}\n")

    # Pipeline table
    headers = ["Program", "Indication", "Phase", "TA", "Mechanism"]
    rows = []

    for program in result['pipeline'][:20]:  # Top 20
        rows.append([
            program['program_name'][:30],
            program['indication'][:30],
            program['phase'],
            program['therapeutic_area'][:15],
            program['mechanism'][:25]
        ])

    print(tabulate(rows, headers=headers, tablefmt="grid"))

    # Summary stats
    print(f"\nTotal Programs: {result['summary_stats']['total_programs']}")
    print("\nBy Phase:")
    for phase, count in sorted(result['summary_stats']['by_phase'].items(),
                              key=lambda x: phase_order(x[0])):
        print(f"  {phase:20} {count:3} programs")
```

**Example Output**:
```
================================================================================
  Pfizer Pipeline Summary
  Scraped: 2025-01-24T10:30:00Z
  Source: https://www.pfizer.com/science/drug-product-pipeline
================================================================================

+----------------------------+---------------------------+-----------+---------------+-------------------------+
| Program                    | Indication                | Phase     | TA            | Mechanism               |
+============================+===========================+===========+===============+=========================+
| PF-07321332               | COVID-19                  | Phase 3   | Infectious    | SARS-CoV-2 protease     |
+----------------------------+---------------------------+-----------+---------------+-------------------------+
| Vyndaqel                  | ATTR Cardiomyopathy       | Approved  | Cardiovascular| TTR stabilizer          |
+----------------------------+---------------------------+-----------+---------------+-------------------------+
| PF-06939999               | Duchenne MD               | Phase 3   | Neurology     | Myostatin inhibitor     |
+----------------------------+---------------------------+-----------+---------------+-------------------------+

Total Programs: 68

By Phase:
  Discovery             12 programs
  Preclinical            8 programs
  Phase 1               15 programs
  Phase 2               18 programs
  Phase 3               12 programs
  Approved               3 programs
```

---

## Usage Examples

### Example 1: Basic Company Pipeline Scrape

```python
from .claude.skills.scrape_company_pipeline.scripts.scrape_company_pipeline import scrape_company_pipeline

result = scrape_company_pipeline(
    company="Pfizer",
    scrape_config={
        "include_preclinical": True,
        "include_approved": False,
        "min_phase": "Phase 1"
    },
    output_options={
        "format": "json",
        "deduplicate": True
    }
)

print(f"Total programs: {len(result['pipeline'])}")
print(f"Phase 3 programs: {result['summary_stats']['by_phase']['Phase 3']}")

# Save to file
with open('pfizer_pipeline.json', 'w') as f:
    json.dump(result, f, indent=2)
```

### Example 2: Multi-Company Batch Scraping

```python
companies = ["Pfizer", "Merck", "Roche", "Novartis", "GSK"]

all_pipelines = {}

for company in companies:
    print(f"Scraping {company}...")
    result = scrape_company_pipeline(company)

    if result['scrape_metadata']['success']:
        all_pipelines[company] = result['pipeline']
        print(f"  ✓ {len(result['pipeline'])} programs")
    else:
        print(f"  ✗ Failed: {result['scrape_metadata']['warnings']}")

    time.sleep(5)  # Be polite

# Aggregate analysis
total_programs = sum(len(p) for p in all_pipelines.values())
print(f"\nTotal programs across {len(all_pipelines)} companies: {total_programs}")
```

### Example 3: Oncology Pipeline Focus

```python
result = scrape_company_pipeline(
    company="Bristol Myers Squibb",
    scrape_config={
        "therapeutic_areas": ["Oncology", "Hematology"],
        "min_phase": "Phase 2"
    }
)

# Filter for IO combinations
io_programs = [
    p for p in result['pipeline']
    if 'PD-1' in p['mechanism'] or 'PD-L1' in p['mechanism'] or 'CTLA-4' in p['mechanism']
]

print(f"IO programs: {len(io_programs)}")
for program in io_programs:
    print(f"  {program['program_name']}: {program['indication']} ({program['phase']})")
```

---

## Implementation Notes

### Dependencies

```bash
# Core scraping
pip install playwright beautifulsoup4 lxml

# Install Playwright browsers
playwright install chromium

# Optional (fallbacks)
pip install selenium requests tabulate
```

### File Structure

```
scrape-company-pipeline/
├── SKILL.md                           # This documentation
├── config/
│   └── company_urls.json              # URL mapping database
└── scripts/
    ├── scrape_company_pipeline.py     # Main entry point
    ├── scrapers/
    │   ├── playwright_scraper.py      # Playwright strategy
    │   ├── static_html_scraper.py     # Simple requests strategy
    │   └── pdf_scraper.py             # PDF extraction strategy
    ├── parsers/
    │   ├── react_parser.py            # Parse React SPA tables
    │   ├── table_parser.py            # Generic HTML table parser
    │   └── normalization.py           # Data cleaning/standardization
    ├── utils/
    │   ├── rate_limiter.py            # Polite scraping
    │   └── validation.py              # Data quality checks
    └── test_scraping.py               # Unit tests
```

### Configuration File Example

```json
{
  "companies": {
    "Pfizer": {
      "pipeline_url": "https://www.pfizer.com/science/drug-product-pipeline",
      "scraper_type": "react_spa",
      "selectors": {
        "table": "div.pipeline-table",
        "row": "tr[data-pipeline-item]",
        "fields": {
          "name": "td:nth-child(1)",
          "indication": "td:nth-child(2)",
          "phase": "td:nth-child(3)",
          "ta": "td:nth-child(4)"
        }
      },
      "last_verified": "2025-01-15",
      "notes": "Uses React, needs JavaScript rendering"
    }
  }
}
```

### Maintenance Strategy

**Critical**: Pharma websites change frequently. Implement:

1. **Version control for selectors**: Track selector changes over time
2. **Automated health checks**: Weekly cron job to test all scrapers
3. **Fallback notification**: Alert when scraper fails (Slack, email)
4. **Community updates**: GitHub repo for selector contributions

```python
def health_check_scrapers():
    """Test all company scrapers weekly."""

    failed = []
    for company, config in COMPANY_PIPELINE_URLS.items():
        try:
            result = scrape_company_pipeline(company)
            if not result['scrape_metadata']['success'] or len(result['pipeline']) == 0:
                failed.append(company)
        except Exception as e:
            failed.append(f"{company}: {e}")

    if failed:
        send_alert(f"Scrapers failing: {', '.join(failed)}")
```

---

## Legal & Ethical Considerations

### Terms of Service Compliance

- **robots.txt**: Always respect `robots.txt` directives
- **Rate limiting**: 2-5 seconds between requests (be polite)
- **User-Agent**: Identify as research tool, provide contact email
- **Attribution**: Cite source URLs in output

```python
# Respectful User-Agent
headers = {
    'User-Agent': 'PharmaResearchBot/1.0 (+mailto:research@example.com)'
}
```

### Fair Use

- **Public data only**: Only scrape publicly accessible pipeline pages
- **No circumvention**: Don't bypass logins, paywalls, or CAPTCHAs
- **Academic/research use**: Document use case as competitive intelligence research
- **No redistribution**: Don't republish scraped data commercially

---

## Future Enhancements

1. **ML-based selector discovery**: Train model to auto-detect table structures
2. **Historical tracking**: Store snapshots to track pipeline changes over time
3. **NLP enrichment**: Extract additional context from press releases
4. **API wrappers**: For companies that provide official APIs (rare)
5. **Multi-language support**: Scrape non-English company sites (China, Japan)
6. **Image-based extraction**: OCR for pipeline infographics (PDFs, images)

---

## Troubleshooting

### Common Issues

**Issue 1**: "Selector not found" error
- **Cause**: Company changed website structure
- **Fix**: Update `company_urls.json` selectors, test with browser DevTools

**Issue 2**: Empty pipeline returned
- **Cause**: JavaScript not fully loaded, selector too specific
- **Fix**: Increase `wait_for_selector` timeout, use broader selectors

**Issue 3**: Rate limit / IP blocked
- **Cause**: Too many requests, scraped too aggressively
- **Fix**: Increase delay between requests, use rotating proxies (last resort)

**Issue 4**: Incorrect phase parsing
- **Cause**: Company uses non-standard phase naming
- **Fix**: Update `standardize_phase()` mapping dictionary

---

## References

- **Playwright Documentation**: https://playwright.dev/python/
- **Web Scraping Ethics**: https://toscrape.com/
- **robots.txt Spec**: https://www.robotstxt.org/
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/
