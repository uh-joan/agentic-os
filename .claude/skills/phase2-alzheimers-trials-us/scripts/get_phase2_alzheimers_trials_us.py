"""
Find Phase 2 clinical trials for Alzheimer's disease actively recruiting in the United States.

This function queries ClinicalTrials.gov and returns detailed information about trials
including sponsors, enrollment, and start dates.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'code' / 'agentic-os' / 'scripts'))
from mcp.servers.ct_gov_mcp import ct_gov_studies

def get_phase2_alzheimers_trials_us():
    """
    Find Phase 2 clinical trials for Alzheimer's disease that are actively recruiting in the United States.

    Returns:
        dict: Summary statistics and list of trials with key information
            - total_trials: Number of trials found
            - unique_sponsors: Number of unique sponsors
            - total_enrollment: Total planned enrollment across all trials
            - trials: List of trial dictionaries with nct_id, title, sponsor, phase, status, etc.
            - sponsor_list: Sorted list of unique sponsors
    """

    result = ct_gov_studies(
        query="Alzheimer's disease",
        phase="PHASE2",
        status="RECRUITING",
        location="United States"
    )

    trials = []
    trial_blocks = result.split('\n## Study: ')

    for block in trial_blocks[1:]:
        trial = {}

        nct_match = re.search(r'NCT\d+', block)
        if nct_match:
            trial['nct_id'] = nct_match.group()

        title_match = re.search(r'^(.+?)\n', block)
        if title_match:
            trial['title'] = title_match.group(1).replace(trial.get('nct_id', ''), '').strip()

        sponsor_match = re.search(r'\*\*Sponsor:\*\* (.+)', block)
        if sponsor_match:
            trial['sponsor'] = sponsor_match.group(1).strip()

        phase_match = re.search(r'\*\*Phase:\*\* (.+)', block)
        if phase_match:
            trial['phase'] = phase_match.group(1).strip()

        status_match = re.search(r'\*\*Status:\*\* (.+)', block)
        if status_match:
            trial['status'] = status_match.group(1).strip()

        conditions_match = re.search(r'\*\*Conditions:\*\* (.+)', block)
        if conditions_match:
            trial['conditions'] = conditions_match.group(1).strip()

        start_match = re.search(r'\*\*Start Date:\*\* (.+)', block)
        if start_match:
            trial['start_date'] = start_match.group(1).strip()

        enrollment_match = re.search(r'\*\*Enrollment:\*\* (.+)', block)
        if enrollment_match:
            trial['enrollment'] = enrollment_match.group(1).strip()

        trials.append(trial)

    unique_sponsors = set(t.get('sponsor', 'Unknown') for t in trials)
    total_enrollment = 0

    for trial in trials:
        enrollment_str = trial.get('enrollment', '0')
        enrollment_num = re.search(r'\d+', enrollment_str)
        if enrollment_num:
            total_enrollment += int(enrollment_num.group())

    return {
        'total_trials': len(trials),
        'unique_sponsors': len(unique_sponsors),
        'total_enrollment': total_enrollment,
        'trials': trials,
        'sponsor_list': sorted(unique_sponsors)
    }
