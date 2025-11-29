#!/usr/bin/env python3
"""
Add sample queries section to all SKILL.md files.

Generates 3 contextually appropriate queries for each skill based on:
- Skill name, description, category
- Data type (trials, FDA drugs, patents, etc.)
- Therapeutic area patterns

Usage:
    python3 .claude/tools/add_sample_queries.py [--dry-run]
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Skill directory
SKILLS_DIR = Path(".claude/skills")
INDEX_FILE = SKILLS_DIR / "index.json"


def load_index() -> List[Dict]:
    """Load skills index."""
    with open(INDEX_FILE, 'r') as f:
        data = json.load(f)
        return data.get('skills', [])


def parse_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    """
    Parse YAML frontmatter from SKILL.md content.

    Returns:
        (metadata_dict, markdown_content)
    """
    # Check for YAML frontmatter
    if not content.startswith('---'):
        return None, content

    # Find end of frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    try:
        metadata = yaml.safe_load(parts[1])
        markdown_content = parts[2].strip()
        return metadata, markdown_content
    except yaml.YAMLError:
        return None, content


def extract_context(name: str, description: str) -> Dict[str, Optional[str]]:
    """
    Extract context from skill name and description.

    Returns:
        Dict with keys: therapeutic_area, company, drug_class, disease, specific_term
    """
    context = {
        'therapeutic_area': None,
        'company': None,
        'drug_class': None,
        'disease': None,
        'specific_term': None
    }

    # Therapeutic area patterns
    ta_patterns = {
        r'glp[-\s]?1(\s+agonist)?': 'GLP-1 receptor agonist',
        r'kras(\s+inhibitor)?': 'KRAS inhibitor',
        r'braf(\s+inhibitor)?': 'BRAF inhibitor',
        r'egfr(\s+inhibitor)?': 'EGFR inhibitor',
        r'btk(\s+inhibitor)?': 'BTK inhibitor',
        r'pd[-\s]?1(\s+antibody|\s+inhibitor)?': 'PD-1 checkpoint inhibitor',
        r'pd[-\s]?l1(\s+antibody|\s+inhibitor)?': 'PD-L1 checkpoint inhibitor',
        r'cart[-\s]?t?(\s+therapy)?': 'CAR-T cell therapy',
        r'adc': 'antibody-drug conjugate',
        r'bispecific(\s+antibody)?': 'bispecific antibody',
        r'crispr': 'CRISPR gene editing',
    }

    # Disease patterns
    disease_patterns = {
        r'diabetes(\s+mellitus)?': 'diabetes',
        r'obesity': 'obesity',
        r'alzheimer': 'Alzheimer\'s disease',
        r'cardiovascular': 'cardiovascular disease',
        r'hypertension': 'hypertension',
        r'rheumatoid\s+arthritis': 'rheumatoid arthritis',
        r'nsclc': 'non-small cell lung cancer',
        r'melanoma': 'melanoma',
        r'heart\s+failure': 'heart failure',
    }

    # Company patterns (from name or description)
    company_patterns = [
        r'pfizer', r'merck', r'novartis', r'roche', r'genentech',
        r'bristol\s+myers\s+squibb', r'bms', r'abbvie', r'amgen',
        r'novo\s+nordisk', r'eli\s+lilly', r'johnson\s+.?\s+johnson',
        r'gsk', r'glaxosmithkline', r'sanofi', r'astrazeneca',
        r'regeneron', r'gilead', r'biogen', r'vertex'
    ]

    name_lower = name.lower()
    desc_lower = description.lower() if description else ""
    combined = f"{name_lower} {desc_lower}"

    # Extract therapeutic area
    for pattern, ta in ta_patterns.items():
        if re.search(pattern, combined):
            context['therapeutic_area'] = ta
            break

    # Extract disease
    for pattern, disease in disease_patterns.items():
        if re.search(pattern, combined):
            context['disease'] = disease
            break

    # Extract company
    for pattern in company_patterns:
        match = re.search(pattern, combined)
        if match:
            context['company'] = match.group(0).title().replace('Bms', 'Bristol Myers Squibb')
            break

    # Extract specific terms from name (last resort)
    # e.g., "novo_nordisk_patents" → "Novo Nordisk"
    if not context['therapeutic_area'] and not context['disease']:
        # Try to extract meaningful term from name
        clean_name = name.replace('get_', '').replace('extract_', '').replace('_', ' ')
        # Remove common suffixes
        for suffix in ['trials', 'fda drugs', 'patents', 'publications', 'codes', 'data']:
            clean_name = clean_name.replace(suffix, '').strip()
        if clean_name:
            context['specific_term'] = clean_name

    return context


def generate_queries(skill: Dict, metadata: Optional[Dict]) -> List[str]:
    """
    Generate 3 contextually appropriate sample queries.

    Args:
        skill: Skill metadata from index.json
        metadata: Parsed YAML frontmatter from SKILL.md

    Returns:
        List of 3 query strings
    """
    name = skill.get('name', '')
    # Prefer description from YAML frontmatter (more detailed)
    description = metadata.get('description', '') if metadata else ''
    if not description:
        description = skill.get('description', '')
    category = metadata.get('category', '') if metadata else skill.get('category', '')
    servers = metadata.get('mcp_servers', []) if metadata else skill.get('servers_used', [])

    # Extract context
    context = extract_context(name, description)
    ta = context['therapeutic_area']
    disease = context['disease']
    company = context['company']
    specific = context['specific_term']

    # Use most specific context available
    topic = ta or disease or specific or "this area"

    queries = []

    # Strategy: Generate queries based on skill patterns

    # Pattern 1: FDA drugs
    if 'fda' in name.lower() or 'fda_mcp' in servers:
        if topic != "this area":
            queries.append(f"What {topic} drugs are FDA approved?")
            queries.append(f"Show me all approved {topic} medications")
            queries.append(f"Get the list of FDA-approved drugs for {topic}")
        else:
            queries.append("What drugs are FDA approved for this indication?")
            queries.append("Show me approved medications in this therapeutic area")
            queries.append("Get FDA-approved drugs for this condition")

    # Pattern 2: Clinical trials
    elif 'trial' in name.lower() or 'ct_gov_mcp' in servers:
        if topic != "this area":
            queries.append(f"What clinical trials are running for {topic}?")
            queries.append(f"Find active {topic} trials")
            queries.append(f"Show me the clinical development landscape for {topic}")
        else:
            queries.append("What clinical trials are running in this area?")
            queries.append("Find active trials for this indication")
            queries.append("Show me the clinical trial landscape")

    # Pattern 3: Patents
    elif 'patent' in name.lower() or 'uspto_patents_mcp' in servers:
        if topic != "this area":
            queries.append(f"What patents exist for {topic}?")
            queries.append(f"Show me the IP landscape for {topic}")
            queries.append(f"Find {topic} patents")
        else:
            queries.append("What patents exist in this space?")
            queries.append("Show me the IP landscape")
            queries.append("Find relevant patents")

    # Pattern 4: Publications/Literature
    elif 'publication' in name.lower() or 'paper' in name.lower() or 'pubmed_mcp' in servers:
        if topic != "this area":
            queries.append(f"What are the recent publications on {topic}?")
            queries.append(f"Find scientific literature about {topic}")
            queries.append(f"Show me research papers on {topic}")
        else:
            queries.append("What are recent publications in this area?")
            queries.append("Find scientific literature on this topic")
            queries.append("Show me research papers")

    # Pattern 5: Company/Competitive
    elif 'compan' in name.lower() or category == 'competitive-intelligence':
        if company:
            # Company-specific queries
            queries.append(f"What is {company}'s pipeline?")
            queries.append(f"Show me {company}'s clinical trials")
            queries.append(f"Analyze {company}'s competitive position")
        elif topic != "this area":
            queries.append(f"Which companies are working on {topic}?")
            queries.append(f"Show me the competitive landscape for {topic}")
            queries.append(f"Who's developing {topic} therapies?")
        else:
            queries.append("Which companies are working on this?")
            queries.append("Show me the competitive landscape")
            queries.append("Who's developing therapies in this space?")

    # Pattern 6: ICD codes
    elif 'icd' in name.lower() or 'code' in name.lower():
        if topic != "this area":
            queries.append(f"What are the ICD-10 codes for {topic}?")
            queries.append(f"Get diagnostic codes for {topic}")
            queries.append(f"Show me billing codes for {topic}")
        else:
            queries.append("What are the ICD-10 codes for this condition?")
            queries.append("Get diagnostic codes")
            queries.append("Show me billing codes")

    # Pattern 7: Target/Genetics
    elif 'target' in name.lower() or 'genetic' in name.lower() or 'opentargets_mcp' in servers:
        if topic != "this area":
            queries.append(f"What are the genetic targets for {topic}?")
            queries.append(f"Show me therapeutic targets for {topic}")
            queries.append(f"Find validated targets in {topic}")
        else:
            queries.append("What are the genetic targets for this disease?")
            queries.append("Show me therapeutic targets")
            queries.append("Find validated targets")

    # Pattern 8: Catalysts/Events
    elif 'catalyst' in name.lower() or 'pdufa' in name.lower():
        if topic != "this area":
            queries.append(f"What are upcoming catalysts for {topic}?")
            queries.append(f"Show me PDUFA dates for {topic} drugs")
            queries.append(f"Find clinical trial readouts in {topic}")
        else:
            queries.append("What are upcoming catalysts in this space?")
            queries.append("Show me PDUFA dates")
            queries.append("Find upcoming clinical trial readouts")

    # Pattern 9: Financial/Company data
    elif 'financial' in name.lower() or 'revenue' in name.lower() or 'sec' in name.lower():
        if company:
            queries.append(f"What are {company}'s financials?")
            queries.append(f"Show me {company}'s R&D spending")
            queries.append(f"Get {company}'s revenue breakdown")
        elif topic != "this area":
            queries.append(f"What are the financials for companies in {topic}?")
            queries.append(f"Show me R&D spending on {topic}")
            queries.append(f"Get revenue data for {topic} companies")
        else:
            queries.append("What are the company financials?")
            queries.append("Show me R&D spending")
            queries.append("Get revenue data")

    # Pattern 10: Disease burden/Epidemiology
    elif 'burden' in name.lower() or 'prevalence' in name.lower() or 'population' in name.lower():
        if topic != "this area":
            queries.append(f"What's the disease burden for {topic}?")
            queries.append(f"Show me prevalence data for {topic}")
            queries.append(f"Get epidemiology statistics for {topic}")
        else:
            queries.append("What's the disease burden?")
            queries.append("Show me prevalence data")
            queries.append("Get epidemiology statistics")

    # Default fallback based on description
    if len(queries) < 3:
        # Generic queries based on name
        base_name = name.replace('get_', '').replace('_', ' ')
        queries = [
            f"Get {base_name} data",
            f"Show me {base_name} information",
            f"Find {base_name} details",
        ]

    return queries[:3]  # Ensure exactly 3 queries


def insert_sample_queries(content: str, metadata: Optional[Dict], skill: Dict) -> str:
    """
    Insert Sample Queries section into SKILL.md content.

    Args:
        content: Full file content (frontmatter + markdown)
        metadata: Parsed YAML frontmatter
        skill: Skill metadata from index.json

    Returns:
        Updated content with Sample Queries section
    """
    # Check if Sample Queries already exists
    if '## Sample Queries' in content:
        print(f"  ⏭️  Sample Queries section already exists, skipping")
        return content

    # Generate queries
    queries = generate_queries(skill, metadata)

    # Build Sample Queries section
    queries_section = "\n## Sample Queries\n\n"
    queries_section += "Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:\n\n"

    for i, query in enumerate(queries, 1):
        queries_section += f"{i}. `@agent-pharma-search-specialist {query}`\n"

    queries_section += "\n"

    # Find insertion point: after main heading
    # Pattern: # skill_name\n\n (then maybe description or ## Purpose)

    # Split into frontmatter and markdown
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = f"---{parts[1]}---"
            markdown = parts[2]
        else:
            frontmatter = ""
            markdown = content
    else:
        frontmatter = ""
        markdown = content

    # Find first heading
    lines = markdown.strip().split('\n')
    insert_idx = 0

    for i, line in enumerate(lines):
        # Find main heading (# skill_name)
        if line.startswith('# '):
            # Insert after heading and any blank lines
            insert_idx = i + 1
            # Skip blank lines after heading
            while insert_idx < len(lines) and lines[insert_idx].strip() == '':
                insert_idx += 1
            break

    # Insert the section
    lines.insert(insert_idx, queries_section)

    # Reconstruct content
    updated_markdown = '\n'.join(lines)

    if frontmatter:
        return f"{frontmatter}\n{updated_markdown}"
    else:
        return updated_markdown


def process_skill(skill: Dict, dry_run: bool = False) -> bool:
    """
    Process a single skill: read SKILL.md, add queries, save.

    Returns:
        True if updated, False if skipped
    """
    skill_md_path = Path(skill.get('skill_md', ''))
    if not skill_md_path or not (SKILLS_DIR / skill_md_path).exists():
        print(f"  ⚠️  SKILL.md not found: {skill_md_path}")
        return False

    full_path = SKILLS_DIR / skill_md_path

    # Read current content
    with open(full_path, 'r') as f:
        content = f.read()

    # Parse frontmatter
    metadata, _ = parse_frontmatter(content)

    # Insert Sample Queries
    updated_content = insert_sample_queries(content, metadata, skill)

    # Check if changed
    if updated_content == content:
        return False

    # Save (unless dry run)
    if not dry_run:
        with open(full_path, 'w') as f:
            f.write(updated_content)
        print(f"  ✅ Updated: {skill_md_path}")
    else:
        print(f"  🔍 Would update: {skill_md_path}")
        # Show sample queries for dry run
        queries = generate_queries(skill, metadata)
        for i, query in enumerate(queries, 1):
            print(f"      {i}. {query}")

    return True


def main():
    """Main execution."""
    import sys

    dry_run = '--dry-run' in sys.argv

    print("=" * 80)
    print("ADD SAMPLE QUERIES TO SKILLS")
    print("=" * 80)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    # Load index
    skills = load_index()
    print(f"📚 Found {len(skills)} skills in index\n")

    # Process each skill
    updated_count = 0
    skipped_count = 0

    for skill in skills:
        name = skill.get('name', 'unknown')
        print(f"Processing: {name}")

        if process_skill(skill, dry_run):
            updated_count += 1
        else:
            skipped_count += 1
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Updated: {updated_count} skills")
    print(f"⏭️  Skipped: {skipped_count} skills")
    print()

    if dry_run:
        print("🔍 This was a dry run. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
