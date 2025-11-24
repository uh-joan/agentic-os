#!/usr/bin/env python3
"""
Update index.json to:
1. Remove 20 archived clinical trial skills
2. Add new generic clinical-trials skill
3. Update skill counts
"""

import json
import sys

# List of archived skill folders (moved to archive/clinical-trials-replaced/)
ARCHIVED_FOLDERS = [
    "glp1-trials",
    "adc-trials",
    "alzheimers-all-trials",
    "braf-inhibitor-trials",
    "egfr-inhibitor-trials",
    "kras-inhibitor-trials",
    "rheumatoid-arthritis-trials",
    "pd1-checkpoint-trials",
    "cart-bcell-malignancies-trials",
    "checkpoint-inhibitor-combinations",
    "covid-antiviral-trials-recent",
    "metabolic-trial-endpoints",
    "oncology-trials-geographic-comparison",
    "checkpoint-inhibitor-combination-therapies",
    "heart-failure-phase3-trials",
    "kras-g12d-phase2-trials",
    "phase2-alzheimers-trials-us",
    "us-phase3-obesity-recruiting-trials",
    "glp1-obesity-phase3-recruiting-trials",
    "us-china-oncology-trial-comparison"
]

# New generic skill entry
NEW_GENERIC_SKILL = {
    "name": "get_clinical_trials",
    "structure": "folder",
    "folder": "clinical-trials",
    "skill_md": "clinical-trials/SKILL.md",
    "script": "clinical-trials/scripts/get_clinical_trials.py",
    "has_frontmatter": True,
    "description": "Generic skill to get clinical trials for ANY therapeutic area, drug, or condition with optional phase filtering",
    "function_signature": "get_clinical_trials(term: str, phase: str = None) -> dict",
    "servers_used": ["ct_gov_mcp"],
    "patterns_demonstrated": [
        "pagination",
        "markdown_parsing",
        "status_aggregation",
        "phase_filtering",
        "generic_parameterization"
    ],
    "category": "clinical-trials",
    "complexity": "medium",
    "is_generic": True,
    "replaces_skills": ARCHIVED_FOLDERS
}

def main():
    index_path = ".claude/skills/index.json"

    print("Loading index.json...")
    with open(index_path, 'r') as f:
        index = json.load(f)

    print(f"Current skill count: {len(index['skills'])}")

    # Remove archived skills
    original_count = len(index['skills'])
    index['skills'] = [
        skill for skill in index['skills']
        if skill.get('folder') not in ARCHIVED_FOLDERS
    ]
    removed_count = original_count - len(index['skills'])

    print(f"Removed {removed_count} archived skills")
    print(f"Remaining skills: {len(index['skills'])}")

    # Add new generic skill at the beginning (high priority)
    index['skills'].insert(0, NEW_GENERIC_SKILL)
    print(f"Added generic clinical-trials skill")
    print(f"New skill count: {len(index['skills'])}")

    # Update counts
    index['migration_status']['folder_skills_count'] = len(index['skills'])
    index['last_updated'] = "2025-11-24"

    # Save updated index
    print(f"\nSaving updated index.json...")
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    print("✓ Index updated successfully!")
    print(f"\nSummary:")
    print(f"  - Archived skills: {removed_count}")
    print(f"  - Added generic skills: 1")
    print(f"  - Net change: {1 - removed_count}")
    print(f"  - Total skills: {len(index['skills'])}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
