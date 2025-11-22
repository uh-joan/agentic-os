import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_adverse_events

def get_semaglutide_adverse_events():
    """Get adverse event reports for semaglutide from FDA FAERS.

    Returns:
        dict: Contains total_count, top_reactions, demographics, and severity data
    """

    result = search_adverse_events(
        search='patient.drug.medicinalproduct:"semaglutide"',
        limit=1000
    )

    if not result or 'results' not in result:
        return {
            'total_count': 0,
            'summary': 'No adverse event data found for semaglutide'
        }

    reports = result.get('results', [])
    total_count = len(reports)

    reactions = {}
    serious_outcomes = {}
    age_groups = {}
    gender_counts = {'Male': 0, 'Female': 0, 'Unknown': 0}

    key_concerns = {
        'muscle_loss': 0,
        'gallbladder': 0,
        'pancreatitis': 0,
        'nausea': 0,
        'vomiting': 0,
        'diarrhea': 0
    }

    for report in reports:
        patient = report.get('patient', {})

        if 'patientonsetage' in patient:
            age = float(patient['patientonsetage'])
            if age < 18:
                age_group = '<18'
            elif age < 45:
                age_group = '18-44'
            elif age < 65:
                age_group = '45-64'
            else:
                age_group = '65+'
            age_groups[age_group] = age_groups.get(age_group, 0) + 1

        gender_code = patient.get('patientsex', '0')
        gender_map = {'1': 'Male', '2': 'Female', '0': 'Unknown'}
        gender = gender_map.get(gender_code, 'Unknown')
        gender_counts[gender] += 1

        if 'serious' in report and report['serious'] == '1':
            outcomes = report.get('seriousnessdeath', '0') == '1' and 'Death' or \
                      report.get('seriousnesshospitalization', '0') == '1' and 'Hospitalization' or \
                      report.get('seriousnesslifethreatening', '0') == '1' and 'Life-threatening' or \
                      report.get('seriousnessdisabling', '0') == '1' and 'Disability' or 'Other serious'
            serious_outcomes[outcomes] = serious_outcomes.get(outcomes, 0) + 1

        reactions_list = patient.get('reaction', [])
        for reaction in reactions_list:
            reaction_term = reaction.get('reactionmeddrapt', '').lower()
            if reaction_term:
                reactions[reaction_term] = reactions.get(reaction_term, 0) + 1

                if 'muscle' in reaction_term or 'sarcopenia' in reaction_term or 'atrophy' in reaction_term:
                    key_concerns['muscle_loss'] += 1
                if 'gallbladder' in reaction_term or 'cholelithiasis' in reaction_term or 'cholecystitis' in reaction_term:
                    key_concerns['gallbladder'] += 1
                if 'pancreatitis' in reaction_term or 'pancrea' in reaction_term:
                    key_concerns['pancreatitis'] += 1
                if 'nausea' in reaction_term:
                    key_concerns['nausea'] += 1
                if 'vomiting' in reaction_term:
                    key_concerns['vomiting'] += 1
                if 'diarrhea' in reaction_term or 'diarrhoea' in reaction_term:
                    key_concerns['diarrhea'] += 1

    top_reactions = sorted(reactions.items(), key=lambda x: x[1], reverse=True)[:20]

    summary = f"""
SEMAGLUTIDE ADVERSE EVENTS ANALYSIS
====================================

Total Reports: {total_count:,}

TOP 20 REPORTED ADVERSE EVENTS:
"""
    for i, (reaction, count) in enumerate(top_reactions, 1):
        pct = (count / total_count) * 100
        summary += f"{i:2d}. {reaction.title():40s} {count:5d} ({pct:5.1f}%)\n"

    summary += f"""
KEY SAFETY CONCERNS:
- Muscle Mass Loss:        {key_concerns['muscle_loss']:5d} reports
- Gallbladder Issues:      {key_concerns['gallbladder']:5d} reports
- Pancreatitis:            {key_concerns['pancreatitis']:5d} reports
- Nausea:                  {key_concerns['nausea']:5d} reports
- Vomiting:                {key_concerns['vomiting']:5d} reports
- Diarrhea:                {key_concerns['diarrhea']:5d} reports

PATIENT DEMOGRAPHICS:
Gender Distribution:
"""
    for gender, count in gender_counts.items():
        pct = (count / total_count) * 100
        summary += f"  {gender:10s}: {count:5d} ({pct:5.1f}%)\n"

    if age_groups:
        summary += "\nAge Distribution:\n"
        for age_group in ['<18', '18-44', '45-64', '65+']:
            count = age_groups.get(age_group, 0)
            if count > 0:
                pct = (count / total_count) * 100
                summary += f"  {age_group:10s}: {count:5d} ({pct:5.1f}%)\n"

    if serious_outcomes:
        summary += "\nSERIOUS OUTCOMES:\n"
        for outcome, count in sorted(serious_outcomes.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_count) * 100
            summary += f"  {outcome:20s}: {count:5d} ({pct:5.1f}%)\n"

    summary += """
INTERPRETATION:
- Data represents post-market surveillance reports (not incidence rates)
- Reporting bias exists (more likely to report serious/unusual events)
- Consider temporal trends and comparator data for full risk assessment
"""

    return {
        'total_count': total_count,
        'top_reactions': top_reactions,
        'key_concerns': key_concerns,
        'demographics': {
            'gender': gender_counts,
            'age_groups': age_groups
        },
        'serious_outcomes': serious_outcomes,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_semaglutide_adverse_events()
    print(result['summary'])
