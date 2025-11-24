#!/usr/bin/env python3
"""
Scrape pharmaceutical company pipeline data from company websites.

This skill extracts drug pipeline information from pharma company websites,
capturing programs not yet in ClinicalTrials.gov (preclinical, discovery).
"""

import sys
import os
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse

# Try importing scraping libraries with graceful fallbacks
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Warning: BeautifulSoup not installed. Install with: pip install beautifulsoup4")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. Install with: pip install requests")

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    # Playwright is optional - will fallback to requests


# Configuration paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config", "company_urls.json")


def load_config() -> Dict:
    """Load company URL configuration."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def get_company_config(company: str, config: Dict) -> Optional[Dict]:
    """
    Look up scraping configuration for company.

    Args:
        company: Company name (e.g., "Pfizer", "BeOne Medicines")
        config: Full configuration dictionary

    Returns:
        Company configuration or None if not found
    """
    companies = config.get('companies', {})

    # Try exact match
    if company in companies:
        return companies[company]

    # Try case-insensitive match
    for key in companies:
        if company.lower() == key.lower():
            return companies[key]

    # Try fuzzy match (company name contained in or contains key)
    for key in companies:
        if company.lower() in key.lower() or key.lower() in company.lower():
            return companies[key]

    return None


def scrape_with_playwright(url: str, timeout: int = 30000) -> str:
    """
    Scrape JavaScript-rendered page using Playwright.

    Args:
        url: Target URL
        timeout: Timeout in milliseconds

    Returns:
        HTML content
    """
    if not HAS_PLAYWRIGHT:
        raise ImportError("Playwright not installed. Install with: pip install playwright && playwright install chromium")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate and wait for network idle
            page.goto(url, wait_until="networkidle", timeout=timeout)

            # Additional wait for dynamic content
            time.sleep(2)

            content = page.content()
            browser.close()
            return content

        except PlaywrightTimeoutError as e:
            browser.close()
            raise TimeoutError(f"Page load timeout for {url}: {e}")
        except Exception as e:
            browser.close()
            raise Exception(f"Playwright error for {url}: {e}")


def scrape_with_requests(url: str, user_agent: str, timeout: int = 30) -> str:
    """
    Scrape static HTML page using requests.

    Args:
        url: Target URL
        user_agent: User-Agent header
        timeout: Timeout in seconds

    Returns:
        HTML content
    """
    if not HAS_REQUESTS:
        raise ImportError("requests not installed. Install with: pip install requests")

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_html_content(html: str, url: str) -> List[Dict]:
    """
    Auto-detect and parse pipeline data from HTML.

    This is a generic parser that tries common patterns.

    Args:
        html: HTML content
        url: Source URL (for context)

    Returns:
        List of programs extracted
    """
    if not HAS_BS4:
        raise ImportError("BeautifulSoup not installed. Install with: pip install beautifulsoup4 lxml")

    soup = BeautifulSoup(html, 'html.parser')
    programs = []

    # Strategy 1: Look for HTML tables
    tables = soup.find_all('table')
    for table in tables:
        # Check if table looks like a pipeline (has relevant keywords in headers)
        headers_text = ' '.join([th.get_text().lower() for th in table.find_all('th')])
        if any(keyword in headers_text for keyword in ['drug', 'compound', 'program', 'phase', 'indication', 'disease']):
            programs.extend(parse_table(table))

    # Strategy 2: Look for div/article structures with pipeline-like classes
    pipeline_containers = soup.find_all(['div', 'article', 'section'],
                                        class_=lambda x: x and any(word in str(x).lower()
                                        for word in ['pipeline', 'product', 'program', 'asset']))

    for container in pipeline_containers:
        # Look for repeated elements (cards, rows)
        items = container.find_all(['div', 'article'], recursive=False)
        if len(items) > 2:  # At least 3 items suggests a list
            for item in items:
                program = extract_program_from_element(item)
                if program and program.get('program_name'):
                    programs.append(program)

    # Strategy 3: Look for lists (ul, ol) with pipeline items
    lists = soup.find_all(['ul', 'ol'])
    for lst in lists:
        items = lst.find_all('li')
        if len(items) > 2:
            for item in items:
                program = extract_program_from_element(item)
                if program and program.get('program_name'):
                    programs.append(program)

    return programs


def parse_table(table) -> List[Dict]:
    """Parse HTML table into program dictionaries."""
    programs = []

    # Get headers
    headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
    if not headers:
        # Try first row as headers
        first_row = table.find('tr')
        if first_row:
            headers = [td.get_text(strip=True).lower() for td in first_row.find_all(['td', 'th'])]

    # Map headers to field names
    field_map = {
        'program_name': ['drug', 'compound', 'program', 'name', 'product', 'molecule'],
        'indication': ['indication', 'disease', 'condition', 'target'],
        'phase': ['phase', 'stage', 'development', 'status'],
        'therapeutic_area': ['therapeutic area', 'ta', 'area', 'therapy area', 'therapeutic'],
        'mechanism': ['mechanism', 'moa', 'mode of action', 'target', 'pathway']
    }

    header_mapping = {}
    for field, keywords in field_map.items():
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in keywords):
                if field not in header_mapping:  # Take first match
                    header_mapping[field] = i

    # Parse rows
    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue

        program = {}
        for field, col_idx in header_mapping.items():
            if col_idx < len(cells):
                program[field] = cells[col_idx].get_text(strip=True)

        # If no header mapping, use positional fallback
        if not program and len(cells) >= 3:
            program = {
                'program_name': cells[0].get_text(strip=True),
                'indication': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                'phase': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                'therapeutic_area': cells[3].get_text(strip=True) if len(cells) > 3 else '',
            }

        if program.get('program_name'):
            programs.append(program)

    return programs


def extract_program_from_element(element) -> Dict:
    """Extract program data from a generic HTML element."""
    program = {
        'program_name': '',
        'indication': '',
        'phase': '',
        'therapeutic_area': '',
        'mechanism': '',
        'notes': ''
    }

    # Look for headings (program name)
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b']:
        heading = element.find(tag)
        if heading:
            program['program_name'] = heading.get_text(strip=True)
            break

    # Get all text content
    text = element.get_text(separator=' ', strip=True)

    # Try to extract phase with regex
    phase_match = re.search(r'(Phase\s+[I1-3]+|Preclinical|Discovery|NDA|BLA|Approved)', text, re.IGNORECASE)
    if phase_match:
        program['phase'] = phase_match.group(1)

    # Look for indication keywords
    indication_keywords = ['indication', 'disease', 'condition', 'for']
    for keyword in indication_keywords:
        if keyword in text.lower():
            # Try to extract text after keyword
            parts = text.lower().split(keyword)
            if len(parts) > 1:
                potential_indication = parts[1].split('.')[0].split(',')[0].strip()
                if len(potential_indication) > 3 and len(potential_indication) < 100:
                    program['indication'] = potential_indication[:100]
                    break

    # Store full text as notes
    program['notes'] = text[:200] if len(text) > 200 else text

    return program


def standardize_phase(raw_phase: str, phase_mappings: Dict) -> str:
    """Standardize phase naming across companies."""
    if not raw_phase:
        return "Unknown"

    raw_lower = raw_phase.lower().strip()

    # Check mappings
    if raw_lower in phase_mappings:
        return phase_mappings[raw_lower]

    # Direct return if already standard
    standard_phases = ["Discovery", "Preclinical", "Phase 1", "Phase 2", "Phase 3",
                      "Phase 1/2", "Phase 2/3", "NDA Filed", "BLA Filed",
                      "Regulatory Submission", "Approved"]

    for std_phase in standard_phases:
        if std_phase.lower() in raw_lower:
            return std_phase

    return raw_phase  # Return as-is if no match


def deduplicate_programs(programs: List[Dict]) -> List[Dict]:
    """Remove duplicate entries."""
    seen = set()
    unique = []

    for program in programs:
        key = (
            program.get('program_name', '').lower().strip(),
            program.get('indication', '').lower().strip(),
            program.get('phase', '').strip()
        )

        if key[0] and key not in seen:  # Must have program name
            seen.add(key)
            unique.append(program)

    return unique


def validate_programs(programs: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Validate and flag suspicious entries."""
    valid = []
    warnings = []

    for program in programs:
        # Check for required fields
        name = program.get('program_name', '').strip()
        if not name:
            warnings.append("Missing program name, skipping entry")
            continue

        # Check for gibberish
        if len(name) < 2 or not any(c.isalnum() for c in name):
            warnings.append(f"Suspicious program name: {name}, skipping")
            continue

        # Default missing phase
        if not program.get('phase'):
            program['phase'] = "Unknown"
            warnings.append(f"{name}: Missing phase, defaulting to Unknown")

        valid.append(program)

    return valid, warnings


def compute_summary_stats(programs: List[Dict]) -> Dict:
    """Compute summary statistics."""
    by_phase = {}
    by_ta = {}

    for program in programs:
        phase = program.get('phase', 'Unknown')
        ta = program.get('therapeutic_area', 'Unknown')

        by_phase[phase] = by_phase.get(phase, 0) + 1
        by_ta[ta] = by_ta.get(ta, 0) + 1

    return {
        'total_programs': len(programs),
        'by_phase': by_phase,
        'by_therapeutic_area': by_ta
    }


def scrape_company_pipeline(
    company: str,
    scrape_config: Optional[Dict] = None,
    output_options: Optional[Dict] = None
) -> Dict:
    """
    Scrape pharmaceutical company pipeline from website.

    Args:
        company: Company name (e.g., "Pfizer", "BeOne Medicines")
        scrape_config: Optional configuration for scraping
        output_options: Optional output formatting options

    Returns:
        Dictionary containing pipeline data and metadata
    """
    # Load configuration
    config = load_config()
    company_config = get_company_config(company, config)

    if not company_config:
        return {
            'success': False,
            'company': company,
            'error': f"Company '{company}' not found in configuration",
            'recommendation': "Add company to config/company_urls.json or check spelling"
        }

    # Get scraping parameters
    url = company_config['pipeline_url']
    scraper_type = company_config.get('scraper_type', 'auto_detect')
    global_config = config.get('scraper_config', {})
    user_agent = global_config.get('user_agent', 'PharmaResearchBot/1.0')
    timeout = global_config.get('timeout_seconds', 30)

    # Initialize result
    result = {
        'company': company,
        'scrape_metadata': {
            'scraped_at': datetime.utcnow().isoformat() + 'Z',
            'source_url': url,
            'scraper_version': '1.0.0',
            'success': False,
            'warnings': []
        },
        'pipeline': [],
        'summary_stats': {}
    }

    # Attempt scraping with fallback strategies
    html_content = None
    strategies_tried = []

    # Try Playwright first for react_spa or auto_detect
    if scraper_type in ['react_spa', 'auto_detect'] and HAS_PLAYWRIGHT:
        try:
            strategies_tried.append('playwright')
            print(f"Attempting Playwright scrape of {url}...")
            html_content = scrape_with_playwright(url, timeout * 1000)
            result['scrape_metadata']['strategy_used'] = 'playwright'
        except Exception as e:
            result['scrape_metadata']['warnings'].append(f"Playwright failed: {str(e)}")

    # Fallback to requests
    if not html_content and HAS_REQUESTS:
        try:
            strategies_tried.append('requests')
            print(f"Attempting requests scrape of {url}...")
            html_content = scrape_with_requests(url, user_agent, timeout)
            result['scrape_metadata']['strategy_used'] = 'requests'
        except Exception as e:
            result['scrape_metadata']['warnings'].append(f"Requests failed: {str(e)}")

    if not html_content:
        result['error'] = f"All scraping strategies failed: {', '.join(strategies_tried)}"
        return result

    # Parse content
    try:
        print(f"Parsing HTML content ({len(html_content)} bytes)...")
        programs = parse_html_content(html_content, url)

        # Standardize phases
        phase_mappings = config.get('phase_mappings', {})
        for program in programs:
            if 'phase' in program:
                program['phase'] = standardize_phase(program['phase'], phase_mappings)

        # Deduplicate
        if output_options and output_options.get('deduplicate', True):
            programs = deduplicate_programs(programs)

        # Validate
        programs, warnings = validate_programs(programs)
        result['scrape_metadata']['warnings'].extend(warnings)

        # Store results
        result['pipeline'] = programs
        result['summary_stats'] = compute_summary_stats(programs)
        result['scrape_metadata']['success'] = True

    except Exception as e:
        result['error'] = f"Parsing failed: {str(e)}"
        result['scrape_metadata']['warnings'].append(f"Parser error: {str(e)}")

    return result


def print_pipeline_summary(result: Dict):
    """Pretty print pipeline summary to terminal."""
    print(f"\n{'='*80}")
    print(f"  {result['company']} Pipeline Summary")
    print(f"  Scraped: {result['scrape_metadata']['scraped_at']}")
    print(f"  Source: {result['scrape_metadata']['source_url']}")
    print(f"{'='*80}\n")

    if not result['scrape_metadata']['success']:
        print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
        return

    # Print programs
    programs = result['pipeline'][:20]  # Top 20
    if programs:
        print(f"{'Program':<30} {'Indication':<30} {'Phase':<15}")
        print(f"{'-'*30} {'-'*30} {'-'*15}")
        for program in programs:
            name = program.get('program_name', '')[:29]
            indication = program.get('indication', '')[:29]
            phase = program.get('phase', '')[:14]
            print(f"{name:<30} {indication:<30} {phase:<15}")

    # Print stats
    stats = result['summary_stats']
    print(f"\n📊 Total Programs: {stats['total_programs']}")

    if stats['by_phase']:
        print("\n📈 By Phase:")
        for phase, count in sorted(stats['by_phase'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {phase:25} {count:3} programs")

    # Warnings
    if result['scrape_metadata'].get('warnings'):
        print(f"\n⚠️  Warnings ({len(result['scrape_metadata']['warnings'])}):")
        for warning in result['scrape_metadata']['warnings'][:5]:
            print(f"  - {warning}")


# Make skill executable standalone
if __name__ == "__main__":
    # Test with BeOne Medicines
    company = "BeOne Medicines" if len(sys.argv) < 2 else sys.argv[1]

    print(f"Scraping {company} pipeline...")
    result = scrape_company_pipeline(company)

    # Print summary
    print_pipeline_summary(result)

    # Save to JSON
    output_file = f"{company.lower().replace(' ', '_')}_pipeline.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Full results saved to: {output_file}")
