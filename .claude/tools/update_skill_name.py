#!/usr/bin/env python3
"""Update index.json with new folder name: clinical-trials-term-phase"""

import json

index_path = ".claude/skills/index.json"

with open(index_path, 'r') as f:
    index = json.load(f)

# Find and update the generic clinical trials skill
for skill in index['skills']:
    if skill.get('name') == 'get_clinical_trials':
        skill['folder'] = 'clinical-trials-term-phase'
        skill['skill_md'] = 'clinical-trials-term-phase/SKILL.md'
        skill['script'] = 'clinical-trials-term-phase/scripts/get_clinical_trials.py'
        print(f"✓ Updated skill: {skill['name']}")
        print(f"  New folder: {skill['folder']}")
        break

# Save
with open(index_path, 'w') as f:
    json.dump(index, f, indent=2)

print("✓ Index updated successfully!")
