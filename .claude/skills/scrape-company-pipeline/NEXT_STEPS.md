# Next Steps for scrape-company-pipeline Skill

## Current Status (2025-11-24)

✅ **Completed**:
- Web scraping fallback strategy implemented and tested
- Direct MCP execution pattern validated (NO agent invocation)
- Successfully tested on BeOne Medicines (29 molecules, 370+ programs)
- Successfully tested on Novo Nordisk (38 programs across 4 phases)
- pdfplumber dependency installed
- AGENT_PATTERN.md and SKILL.md updated with PDF-first strategy
- Schema v2.0 design documented

⏳ **Remaining Work**:
- PDF parsing implementation (primary strategy)
- Integration of PDF parsing with web scraping fallback
- End-to-end testing with PDF parsing

---

## Priority 1: Implement PDF Parsing Strategy

### Goal
Extract study-level data (study numbers, regional submissions) from pipeline PDFs when available.

### Implementation Plan

#### 1. PDF Detection (Already Working)
```javascript
// Check for PDF links - DONE
mcp__playwright-mcp__browser_evaluate(() => {
    const pdfLinks = [];
    const allLinks = document.querySelectorAll('a[href*=".pdf"]');
    allLinks.forEach(link => {
        if (link.href.toLowerCase().includes('pipeline')) {
            pdfLinks.push({ url: link.href, text: link.textContent });
        }
    });
    return { foundPDF: pdfLinks.length > 0, pdfLinks };
})
```

#### 2. PDF Download & Parsing (TODO)
```python
import requests
import pdfplumber
from io import BytesIO
import re

def parse_pipeline_pdf(pdf_url):
    """Download and parse pipeline PDF to extract study-level data.

    Returns:
        list: Programs with study numbers, regions, indications
    """
    # Download PDF
    response = requests.get(pdf_url)
    pdf_file = BytesIO(response.content)

    programs = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # Parse study numbers
            # Pattern: "Sonrotoclax 101", "303-JP", "Study 201"
            study_pattern = r'\b(\d{3}(?:-[A-Z]{2})?)\b'

            # Parse lines for program data
            lines = text.split('\n')
            current_program = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for study number
                study_match = re.search(study_pattern, line)

                # Check for phase
                phase_match = re.search(r'Phase\s+(\d|1/2)', line, re.IGNORECASE)

                # Build program entry
                if study_match or phase_match:
                    # Extract data and create program entry
                    pass

    return programs
```

#### 3. Integration with Web Scraping (TODO)
```python
# Main execution flow
def scrape_company_pipeline(company_url):
    # Step 1: Navigate to page
    navigate(company_url)

    # Step 2: Check for PDF
    pdf_check = check_for_pdf_links()

    # Step 3: Choose strategy
    if pdf_check['foundPDF']:
        print("✓ PDF found - using PDF parsing (primary strategy)")
        pdf_url = pdf_check['pdfLinks'][0]['url']
        programs = parse_pipeline_pdf(pdf_url)
        strategy = "pdf_parsing"
    else:
        print("✓ No PDF found - using web scraping (fallback)")
        programs = extract_from_webpage()
        strategy = "web_scraping"

    # Step 4: Format results
    return format_schema_v2(programs, strategy)
```

---

## Priority 2: Testing & Validation

### Test Cases

#### Test 1: BeOne Medicines (PDF Available)
- **URL**: https://beonemedicines.com/science/pipeline/
- **PDF**: Clinical-Pipeline_2025-November-5.pdf
- **Expected**: 70+ studies with study numbers (101, 201, 303-JP, etc.)
- **Current**: 29 molecules (web scraping)
- **Target Accuracy**: >90% match with PDF ground truth

#### Test 2: Novo Nordisk (No PDF)
- **URL**: https://www.novonordisk.com/science-and-technology/r-d-pipeline.html
- **PDF**: None
- **Expected**: 38 programs (web scraping fallback)
- **Status**: ✅ Already working
- **Target Accuracy**: 100% (already achieved)

#### Test 3: Multi-Company Validation
- Test on 3-5 additional companies
- Measure accuracy vs official sources
- Document edge cases and parsing quirks

---

## Priority 3: Production Readiness

### Documentation
- [ ] Update SKILL.md with complete examples showing both strategies
- [ ] Add PDF parsing code examples to AGENT_PATTERN.md
- [ ] Create troubleshooting guide for PDF parsing failures
- [ ] Document company-specific PDF formats

### Error Handling
- [ ] Graceful fallback when PDF parsing fails
- [ ] Retry logic for network failures
- [ ] Validation of extracted data quality
- [ ] Clear error messages for debugging

### Performance
- [ ] Benchmark PDF parsing vs web scraping speed
- [ ] Cache PDF downloads for repeat queries
- [ ] Optimize regex patterns for study number extraction

---

## Schema v2.0 Comparison

### Current (Web Scraping Only)
```json
{
  "program_name": "Zanubrutinib",
  "study_number": "",           // ❌ MISSING
  "indication": "TN CLL/SLL",
  "phase": "Approved",
  "mechanism": "BTK Inhibitor",
  "therapeutic_area": "Hematologic Malignancies",
  "region": "",                 // ❌ MISSING
  "notes": ""
}
```

### Target (PDF Parsing)
```json
{
  "program_name": "Sonrotoclax",
  "study_number": "101",        // ✅ FROM PDF
  "indication": "B-cell malignancies",
  "phase": "Phase 1",
  "mechanism": "BCL2 Inhibitor",
  "therapeutic_area": "Hematologic Malignancies",
  "region": "",                 // ✅ FROM PDF (if available)
  "notes": ""
}
```

**Impact**: 26 programs → 70+ studies (170% increase in data completeness)

---

## Technical Challenges

### Challenge 1: PDF Format Variations
**Problem**: Each company uses different PDF layouts
**Solution**:
- Start with pdfplumber text extraction (most flexible)
- Add company-specific parsing logic if needed
- Fallback to web scraping if PDF format unrecognized

### Challenge 2: Study Number Extraction
**Problem**: Study numbers appear in various formats
- Standalone: "101", "201"
- With region: "303-JP", "204-CN"
- With prefix: "Study 101"
- In text: "evaluates 101 in..."

**Solution**: Multiple regex patterns with priority ordering
```python
patterns = [
    r'Study\s+(\d{3}(?:-[A-Z]{2})?)',  # "Study 101", "Study 303-JP"
    r'\b(\d{3}-[A-Z]{2})\b',            # "303-JP" (regional)
    r'\b(\d{3})\b'                       # "101" (standalone)
]
```

### Challenge 3: Deduplication
**Problem**: Same molecule appears multiple times in PDF
**Solution**: Composite key (molecule + study_number + indication + phase)

---

## Success Metrics

### Quantitative
- ✅ **Accuracy**: >90% match with official PDFs
- ✅ **Completeness**: Extract 70+ studies (vs 26 molecules)
- ✅ **Study Numbers**: Capture 95%+ of study identifiers
- ✅ **Regional Info**: Capture 80%+ of regional submissions

### Qualitative
- ✅ **Direct Execution**: No agent invocation (validated)
- ✅ **Fallback Strategy**: Graceful degradation to web scraping
- ✅ **Maintainability**: Clear parsing logic with comments
- ✅ **User Experience**: Fast execution, clear error messages

---

## Timeline Estimate

- **PDF Parsing Implementation**: 2-3 hours
- **BeOne Medicines Validation**: 1 hour
- **Multi-Company Testing**: 2-3 hours
- **Documentation & Polish**: 1 hour
- **Total**: 6-9 hours

---

## Reference Files

### Key Documentation
- `.claude/skills/scrape-company-pipeline/SKILL.md` - Skill overview
- `.claude/skills/scrape-company-pipeline/AGENT_PATTERN.md` - Execution pattern
- `.claude/skills/scrape-company-pipeline/SCHEMA_V2_ENHANCEMENTS.md` - v2.0 design
- `.claude/skills/scrape-company-pipeline/config/company_urls.json` - Company URLs

### Test Artifacts
- `.playwright-mcp/beone_pipeline_fullpage.png` - BeOne page screenshot
- Previous session validation: BeOne PDF had 70+ studies vs 26 extracted in v1.0

---

## Notes

### pdfplumber Installation
- Successfully installed via: `pip3 install --break-system-packages pdfplumber`
- Dependencies: Pillow, pypdfium2, pdfminer.six, cryptography, cffi

### Architecture Validation
- ✅ Direct MCP execution works (no pharma-search-specialist needed)
- ✅ Web scraping extracts molecule-level data successfully
- ✅ PDF URLs detected automatically
- ⏳ PDF parsing implementation pending

### User Feedback
- User corrected twice: "do not invoke the search specialist, run mcp yourself"
- Emphasized importance of dependency installation working properly
- Approved use of `--break-system-packages` for pip install
