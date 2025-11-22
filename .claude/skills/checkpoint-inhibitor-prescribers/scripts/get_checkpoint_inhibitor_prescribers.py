import sys
sys.path.insert(0, ".claude")
from mcp.servers.healthcare_mcp import search_medicare_part_d
from collections import defaultdict

def get_checkpoint_inhibitor_prescribers():
    """Identify top prescribers of checkpoint inhibitor immunotherapies.

    Aggregates Medicare Part D claims across KEYTRUDA, OPDIVO, TECENTRIQ,
    and IMFINZI to find high-volume oncology/hematology KOLs.

    Returns:
        dict: Contains prescriber rankings and specialty distribution
    """

    print("\n" + "="*120)
    print("CHECKPOINT INHIBITOR PRESCRIBER ANALYSIS (Medicare Part D)")
    print("="*120 + "\n")

    checkpoint_inhibitors = ["KEYTRUDA", "OPDIVO", "TECENTRIQ", "IMFINZI"]

    # Aggregate all prescribers by NPI
    all_prescribers = defaultdict(lambda: {
        'npi': None,
        'name': None,
        'specialty': None,
        'city': None,
        'state': None,
        'total_claims': 0,
        'total_cost': 0.0,
        'drugs': {}
    })

    try:
        for drug_name in checkpoint_inhibitors:
            print(f"Querying Medicare Part D for {drug_name}...")

            result = search_medicare_part_d(
                brand_name=drug_name,
                limit=1000
            )

            if not result or 'results' not in result:
                print(f"  ⚠️  No data found for {drug_name}")
                continue

            records = result['results']
            print(f"  ✓ Found {len(records)} prescriber records for {drug_name}\n")

            for record in records:
                npi = record.get('Prscrbr_NPI')
                if not npi:
                    continue

                # Extract prescriber info
                first_name = record.get('Prscrbr_First_Name', '')
                last_name = record.get('Prscrbr_Last_Name', '')
                full_name = f"{first_name} {last_name}".strip()
                specialty = record.get('Prscrbr_Type', 'Unknown')
                city = record.get('Prscrbr_City', 'Unknown')
                state = record.get('Prscrbr_State_Abrvtn', 'Unknown')

                # Extract claims and cost
                total_claims = int(record.get('Tot_Clms', 0))
                total_drug_cost = float(record.get('Tot_Drug_Cst', 0.0))

                # Aggregate by NPI
                prescriber = all_prescribers[npi]
                prescriber['npi'] = npi
                prescriber['name'] = full_name if full_name else prescriber.get('name')
                prescriber['specialty'] = specialty if specialty != 'Unknown' else prescriber.get('specialty', 'Unknown')
                prescriber['city'] = city if city != 'Unknown' else prescriber.get('city', 'Unknown')
                prescriber['state'] = state if state != 'Unknown' else prescriber.get('state', 'Unknown')
                prescriber['total_claims'] += total_claims
                prescriber['total_cost'] += total_drug_cost

                # Track per-drug claims
                prescriber['drugs'][drug_name] = {
                    'claims': total_claims,
                    'cost': total_drug_cost
                }

        print("="*120)
        print("AGGREGATING PRESCRIBER DATA")
        print("="*120 + "\n")

        # Convert to list and sort by total claims
        prescribers_list = [p for p in all_prescribers.values() if p['total_claims'] > 0]
        prescribers_list.sort(key=lambda x: x['total_claims'], reverse=True)

        print(f"Total unique prescribers found: {len(prescribers_list)}\n")

        # Analyze specialty distribution
        specialty_counts = defaultdict(int)
        for prescriber in prescribers_list:
            specialty = prescriber['specialty']
            specialty_counts[specialty] += 1

        # Analyze geographic distribution
        state_counts = defaultdict(int)
        for prescriber in prescribers_list:
            state = prescriber['state']
            state_counts[state] += 1

        # Filter for oncology/hematology specialists
        oncology_keywords = ['ONCOLOGY', 'HEMATOLOGY', 'ONCOLOGIST', 'HEMATOLOGIST']
        oncology_prescribers = [
            p for p in prescribers_list
            if any(keyword in p['specialty'].upper() for keyword in oncology_keywords)
        ]

        print("="*120)
        print("SPECIALTY DISTRIBUTION")
        print("="*120 + "\n")

        # Top specialties
        top_specialties = sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for specialty, count in top_specialties:
            pct = 100 * count / len(prescribers_list)
            print(f"  {specialty:<50} {count:>6} prescribers ({pct:>5.1f}%)")

        print(f"\n  Total Oncology/Hematology Specialists: {len(oncology_prescribers)} ({100*len(oncology_prescribers)/len(prescribers_list):.1f}%)")

        print("\n" + "="*120)
        print("TOP STATES BY PRESCRIBER COUNT")
        print("="*120 + "\n")

        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for state, count in top_states:
            print(f"  {state:<30} {count:>6} prescribers")

        # Analyze multi-drug prescribing
        multi_drug_patterns = {
            1: 0,
            2: 0,
            3: 0,
            4: 0
        }

        for prescriber in prescribers_list:
            drug_count = len(prescriber['drugs'])
            multi_drug_patterns[drug_count] += 1

        print("\n" + "="*120)
        print("MULTI-DRUG PRESCRIBING PATTERNS")
        print("="*120 + "\n")

        for num_drugs, count in sorted(multi_drug_patterns.items()):
            pct = 100 * count / len(prescribers_list)
            if num_drugs == 4:
                print(f"  Using all 4 checkpoint inhibitors:      {count:>6} prescribers ({pct:>5.1f}%)")
            else:
                print(f"  Using {num_drugs} checkpoint inhibitor(s):         {count:>6} prescribers ({pct:>5.1f}%)")

        print("\n" + "="*120)
        print("TOP 25 PRESCRIBERS BY TOTAL CLAIM VOLUME")
        print("="*120 + "\n")

        print(f"{'Rank':<6} {'NPI':<12} {'Name':<30} {'Specialty':<30} {'State':<6} {'Claims':>8} {'Cost':>12}")
        print(f"{'-'*6} {'-'*12} {'-'*30} {'-'*30} {'-'*6} {'-'*8} {'-'*12}")

        for i, prescriber in enumerate(prescribers_list[:25], 1):
            name = (prescriber['name'][:28] + '..') if len(prescriber['name']) > 30 else prescriber['name']
            specialty = (prescriber['specialty'][:28] + '..') if len(prescriber['specialty']) > 30 else prescriber['specialty']
            cost_millions = prescriber['total_cost'] / 1_000_000

            print(f"{i:<6} {prescriber['npi']:<12} {name:<30} {specialty:<30} {prescriber['state']:<6} {prescriber['total_claims']:>8} ${cost_millions:>10.2f}M")

        print("\n" + "="*120 + "\n")

        # Generate summary
        summary_lines = [
            "CHECKPOINT INHIBITOR PRESCRIBER ANALYSIS (Medicare Part D)",
            "",
            "OVERALL METRICS:",
            f"  Total Prescribers: {len(prescribers_list):,}",
            f"  Oncology/Hematology Specialists: {len(oncology_prescribers):,} ({100*len(oncology_prescribers)/len(prescribers_list):.1f}%)",
            f"  Drugs Analyzed: {', '.join(checkpoint_inhibitors)}",
            "",
            "TOP 10 PRESCRIBERS BY CLAIM VOLUME:",
        ]

        for i, prescriber in enumerate(prescribers_list[:10], 1):
            summary_lines.append(f"  {i}. {prescriber['name']} ({prescriber['specialty']}) - {prescriber['total_claims']} claims, ${prescriber['total_cost']/1_000_000:.2f}M")

        summary_lines.extend([
            "",
            "SPECIALTY DISTRIBUTION:",
        ])

        for specialty, count in top_specialties[:5]:
            pct = 100 * count / len(prescribers_list)
            summary_lines.append(f"  {specialty}: {count} prescribers ({pct:.1f}%)")

        summary_lines.extend([
            "",
            "TOP STATES BY PRESCRIBER COUNT:",
        ])

        for state, count in top_states[:5]:
            summary_lines.append(f"  {state}: {count} prescribers")

        return {
            'total_prescribers': len(prescribers_list),
            'oncology_prescriber_count': len(oncology_prescribers),
            'top_prescribers': prescribers_list[:100],
            'specialty_distribution': dict(top_specialties),
            'geographic_distribution': dict(top_states),
            'multi_drug_patterns': multi_drug_patterns,
            'summary': '\n'.join(summary_lines)
        }

    except Exception as e:
        return {
            'error': str(e),
            'summary': f'Error analyzing checkpoint inhibitor prescribers: {str(e)}'
        }

if __name__ == "__main__":
    result = get_checkpoint_inhibitor_prescribers()
    if 'error' in result:
        print(f"ERROR: {result['error']}")
    else:
        print(result['summary'])
