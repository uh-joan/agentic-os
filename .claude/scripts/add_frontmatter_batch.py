#!/usr/bin/env python3
"""Batch add YAML frontmatter to existing skills."""

from pathlib import Path
import json
import re

# Skill metadata mapping
SKILL_METADATA = {
    "get_glp1_fda_drugs": {
        "name": "get_glp1_fda_drugs",
        "description": "Get FDA approved GLP-1 drugs with deduplication by active ingredient. Returns comprehensive drug metadata including manufacturer, application info, and indications. Use when analyzing FDA-approved GLP-1 therapeutics, market landscape, or drug development milestones. Keywords: GLP-1, semaglutide, tirzepatide, FDA approval, drug labels, obesity drugs, diabetes drugs.",
        "category": "drug-discovery",
        "mcp_servers": ["fda_mcp"],
        "patterns": ["fda_json_parsing", "drug_deduplication", "metadata_extraction"],
        "data_scope": {"total_results": 21, "geographical": "US", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2-3 seconds"
    },
    "get_kras_inhibitor_trials": {
        "name": "get_kras_inhibitor_trials",
        "description": "Get KRAS inhibitor clinical trials from ClinicalTrials.gov. Basic implementation without pagination (may miss trials if >1000 results). Use when analyzing KRAS inhibitor pipeline, competitive landscape. Consider upgrading to pagination pattern for complete data. Keywords: KRAS, KRAS G12C, oncology, cancer, targeted therapy, clinical trials.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["basic_ct_gov_search", "markdown_parsing"],
        "data_scope": {"total_results": 363, "geographical": "Global", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_kras_inhibitor_fda_drugs": {
        "name": "get_kras_inhibitor_fda_drugs",
        "description": "Get FDA approved KRAS inhibitor drugs with metadata. Returns drug labels, approval dates, and manufacturer information. Use when analyzing approved KRAS therapeutics or regulatory milestones. Keywords: KRAS, KRAS G12C, sotorasib, adagrasib, LUMAKRAS, KRAZATI, FDA approval, oncology drugs.",
        "category": "drug-discovery",
        "mcp_servers": ["fda_mcp"],
        "patterns": ["fda_json_parsing", "drug_metadata_extraction"],
        "data_scope": {"total_results": 2, "geographical": "US", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~1-2 seconds"
    },
    "get_glp1_diabetes_drugs": {
        "name": "get_glp1_diabetes_drugs",
        "description": "Get GLP-1 drugs specifically for diabetes indication from FDA database. Filters by diabetes indication to distinguish from obesity-focused GLP-1s. Use when analyzing diabetes therapeutics market or indication-specific development. Keywords: GLP-1, diabetes, type 2 diabetes, FDA approval, diabetes drugs.",
        "category": "drug-discovery",
        "mcp_servers": ["fda_mcp"],
        "patterns": ["fda_json_parsing", "indication_filtering"],
        "data_scope": {"total_results": "varies", "geographical": "US", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_covid19_vaccine_trials_recruiting": {
        "name": "get_covid19_vaccine_trials_recruiting",
        "description": "Get currently recruiting COVID-19 vaccine clinical trials from ClinicalTrials.gov. Filters by recruiting status to show active enrollment opportunities. Use when analyzing active COVID-19 vaccine development or enrollment landscape. Keywords: COVID-19, vaccine, recruiting, clinical trials, active trials.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["ct_gov_status_filtering", "vaccine_trial_search"],
        "data_scope": {"total_results": "varies", "geographical": "Global", "temporal": "Current"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_phase2_alzheimers_trials_us": {
        "name": "get_phase2_alzheimers_trials_us",
        "description": "Get Phase 2 Alzheimer's disease trials in the United States from ClinicalTrials.gov. Filters by phase and geography for targeted pipeline analysis. Use when analyzing mid-stage Alzheimer's development pipeline or US-specific trial activity. Keywords: Alzheimer's, Phase 2, United States, neurology, dementia, clinical trials.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["ct_gov_phase_filtering", "geographic_filtering"],
        "data_scope": {"total_results": "varies", "geographical": "US", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_us_phase3_obesity_recruiting_trials": {
        "name": "get_us_phase3_obesity_recruiting_trials",
        "description": "Get Phase 3 obesity trials recruiting in the United States from ClinicalTrials.gov. Combines multiple filters (phase, status, location) for precise pipeline analysis. Use when analyzing late-stage obesity drug development or US recruitment opportunities. Keywords: obesity, Phase 3, recruiting, United States, weight loss, clinical trials.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["ct_gov_multi_filter", "phase_status_location_filtering"],
        "data_scope": {"total_results": "varies", "geographical": "US", "temporal": "Current"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_adc_trials": {
        "name": "get_adc_trials",
        "description": "Get antibody-drug conjugate (ADC) clinical trials from ClinicalTrials.gov with full pagination support. Retrieves complete dataset across all phases and statuses. Use when analyzing ADC pipeline, competitive landscape, or targeted oncology therapeutic development. Handles large result sets via pagination. Keywords: ADC, antibody-drug conjugate, oncology, targeted therapy, clinical trials, cancer.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["pagination", "markdown_parsing", "multi_page_data_collection"],
        "data_scope": {"total_results": 363, "geographical": "Global", "temporal": "All time"},
        "complexity": "medium",
        "execution_time": "~3-4 seconds"
    },
    "get_braf_inhibitor_trials": {
        "name": "get_braf_inhibitor_trials",
        "description": "Get BRAF inhibitor clinical trials from ClinicalTrials.gov. Returns trials for BRAF-targeted oncology therapeutics across all phases. Use when analyzing BRAF inhibitor pipeline, melanoma/cancer therapeutics, or targeted therapy development. Keywords: BRAF, BRAF V600E, melanoma, oncology, targeted therapy, clinical trials.",
        "category": "clinical-trials",
        "mcp_servers": ["ct_gov_mcp"],
        "patterns": ["basic_ct_gov_search", "markdown_parsing"],
        "data_scope": {"total_results": "varies", "geographical": "Global", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    },
    "get_braf_inhibitor_fda_drugs": {
        "name": "get_braf_inhibitor_fda_drugs",
        "description": "Get FDA approved BRAF inhibitor drugs with comprehensive metadata. Returns drug labels, approval dates, indications, and manufacturer information for BRAF-targeted therapeutics. Use when analyzing approved BRAF inhibitors, regulatory milestones, or melanoma/oncology drug landscape. Keywords: BRAF, BRAF V600E, dabrafenib, vemurafenib, encorafenib, FDA approval, melanoma drugs.",
        "category": "drug-discovery",
        "mcp_servers": ["fda_mcp"],
        "patterns": ["fda_json_parsing", "drug_metadata_extraction"],
        "data_scope": {"total_results": "varies", "geographical": "US", "temporal": "All time"},
        "complexity": "simple",
        "execution_time": "~2 seconds"
    }
}

def add_frontmatter_to_skill(skill_name: str):
    """Add YAML frontmatter to a skill .md file."""
    md_path = Path(f".claude/skills/{skill_name}.md")

    if not md_path.exists():
        print(f"  ✗ {skill_name}.md not found")
        return False

    content = md_path.read_text()

    # Check if already has frontmatter
    if content.startswith('---\n'):
        print(f"  ⊙ {skill_name}.md already has frontmatter")
        return True

    metadata = SKILL_METADATA.get(skill_name)
    if not metadata:
        print(f"  ✗ No metadata defined for {skill_name}")
        return False

    # Build frontmatter
    frontmatter = f"""---
name: {metadata['name']}
description: >
  {metadata['description']}
category: {metadata['category']}
mcp_servers:
"""
    for server in metadata['mcp_servers']:
        frontmatter += f"  - {server}\n"

    frontmatter += "patterns:\n"
    for pattern in metadata['patterns']:
        frontmatter += f"  - {pattern}\n"

    frontmatter += f"""data_scope:
  total_results: {metadata['data_scope']['total_results']}
  geographical: {metadata['data_scope']['geographical']}
  temporal: {metadata['data_scope']['temporal']}
created: 2025-11-19
last_updated: 2025-11-19
complexity: {metadata['complexity']}
execution_time: {metadata['execution_time']}
token_efficiency: ~99% reduction vs raw data
---

"""

    # Prepend frontmatter to existing content
    new_content = frontmatter + content
    md_path.write_text(new_content)

    print(f"  ✓ {skill_name}.md updated with frontmatter")
    return True

def main():
    """Add frontmatter to all skills."""
    print("Adding YAML frontmatter to skills...\n")

    skills_to_update = list(SKILL_METADATA.keys())
    success_count = 0

    for skill_name in skills_to_update:
        if add_frontmatter_to_skill(skill_name):
            success_count += 1

    print(f"\n✓ Updated {success_count}/{len(skills_to_update)} skills")

    # Test parser
    print("\nTesting frontmatter parser...")
    import sys
    sys.path.insert(0, '.claude/scripts')
    from parse_skill_metadata import get_all_skill_metadata

    skills = get_all_skill_metadata()
    print(f"✓ Parser found {len(skills)} skills with valid frontmatter")

    for name, meta in sorted(skills.items()):
        category = meta.get('category', 'unknown')
        complexity = meta.get('complexity', 'unknown')
        print(f"  - {name}: {category} ({complexity})")

if __name__ == "__main__":
    main()
