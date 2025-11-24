import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_adverse_events

def get_cart_adverse_events_comparison():
    """Compare adverse event profiles for all 6 FDA-approved CAR-T cell therapies.

    Analyzes cytokine release syndrome (CRS), neurotoxicity/ICANS, and serious
    adverse events to identify safety differentiation opportunities.

    Returns:
        dict: Comparative analysis across all 6 CAR-T products
    """

    # Define the 6 approved CAR-T products
    cart_products = {
        'Kymriah': {
            'generic': 'tisagenlecleucel',
            'company': 'Novartis',
            'indication': 'B-cell ALL, DLBCL'
        },
        'Yescarta': {
            'generic': 'axicabtagene ciloleucel',
            'company': 'Kite/Gilead',
            'indication': 'LBCL'
        },
        'Tecartus': {
            'generic': 'brexucabtagene autoleucel',
            'company': 'Kite/Gilead',
            'indication': 'MCL'
        },
        'Breyanzi': {
            'generic': 'lisocabtagene maraleucel',
            'company': 'BMS',
            'indication': 'LBCL'
        },
        'Abecma': {
            'generic': 'idecabtagene vicleucel',
            'company': 'BMS/bluebird bio',
            'indication': 'Multiple Myeloma'
        },
        'Carvykti': {
            'generic': 'ciltacabtagene autoleucel',
            'company': 'J&J/Legend',
            'indication': 'Multiple Myeloma'
        }
    }

    results = {}
    comparison_data = []

    print(f"Analyzing adverse events for {len(cart_products)} CAR-T products...\n")

    for product_name, product_info in cart_products.items():
        print(f"Fetching data for {product_name} ({product_info['generic']})...")

        # Search by both brand and generic name
        search_query = f'patient.drug.medicinalproduct:"{product_info["generic"]}" OR patient.drug.medicinalproduct:"{product_name}"'

        try:
            ae_result = search_adverse_events(
                search=search_query,
                limit=500
            )

            if not ae_result or 'results' not in ae_result:
                print(f"  No adverse event data found for {product_name}")
                results[product_name] = {
                    'total_reports': 0,
                    'error': 'No data found'
                }
                continue

            reports = ae_result.get('results', [])
            total_reports = len(reports)

            # Key adverse events of interest for CAR-T
            crs_count = 0
            neurotoxicity_count = 0
            icans_count = 0
            serious_count = 0
            death_count = 0
            hospitalization_count = 0

            all_reactions = {}

            for report in reports:
                patient = report.get('patient', {})

                # Check for serious outcomes
                if 'serious' in report and report['serious'] == '1':
                    serious_count += 1

                if report.get('seriousnessdeath', '0') == '1':
                    death_count += 1
                if report.get('seriousnesshospitalization', '0') == '1':
                    hospitalization_count += 1

                # Analyze reactions
                reactions_list = patient.get('reaction', [])
                for reaction in reactions_list:
                    reaction_term = reaction.get('reactionmeddrapt', '').lower()
                    if reaction_term:
                        all_reactions[reaction_term] = all_reactions.get(reaction_term, 0) + 1

                        # Count CRS-related events
                        if 'cytokine release syndrome' in reaction_term or 'crs' in reaction_term:
                            crs_count += 1

                        # Count neurotoxicity/ICANS events
                        if 'neurotoxicity' in reaction_term or 'icans' in reaction_term or \
                           'encephalopathy' in reaction_term or 'confusional state' in reaction_term:
                            neurotoxicity_count += 1
                            if 'icans' in reaction_term:
                                icans_count += 1

            top_reactions = sorted(all_reactions.items(), key=lambda x: x[1], reverse=True)[:10]

            product_data = {
                'total_reports': total_reports,
                'crs_count': crs_count,
                'neurotoxicity_count': neurotoxicity_count,
                'icans_count': icans_count,
                'serious_count': serious_count,
                'death_count': death_count,
                'hospitalization_count': hospitalization_count,
                'top_reactions': top_reactions,
                'company': product_info['company'],
                'indication': product_info['indication']
            }

            # Calculate rates
            if total_reports > 0:
                product_data['crs_rate'] = round((crs_count / total_reports) * 100, 2)
                product_data['neurotoxicity_rate'] = round((neurotoxicity_count / total_reports) * 100, 2)
                product_data['serious_rate'] = round((serious_count / total_reports) * 100, 2)
                product_data['death_rate'] = round((death_count / total_reports) * 100, 2)
            else:
                product_data['crs_rate'] = 0
                product_data['neurotoxicity_rate'] = 0
                product_data['serious_rate'] = 0
                product_data['death_rate'] = 0

            results[product_name] = product_data
            comparison_data.append((product_name, product_data))

            print(f"  ✓ {total_reports} reports, CRS: {crs_count}, Neurotoxicity: {neurotoxicity_count}")

        except Exception as e:
            print(f"  Error fetching data for {product_name}: {str(e)}")
            results[product_name] = {
                'total_reports': 0,
                'error': str(e)
            }

    print("\nAnalysis complete!\n")

    # Generate comparison summary
    summary = generate_comparison_summary(comparison_data)

    return {
        'individual_products': results,
        'comparison_data': comparison_data,
        'summary': summary
    }


def generate_comparison_summary(comparison_data):
    """Generate formatted comparison summary"""

    summary = f"""
{'='*80}
CAR-T ADVERSE EVENTS COMPARATIVE ANALYSIS
{'='*80}

"""

    # Overall comparison table
    summary += "PRODUCT COMPARISON:\n"
    summary += f"{'Product':<15} {'Company':<20} {'Reports':<10} {'CRS %':<10} {'Neuro %':<10} {'Serious %':<10}\n"
    summary += "-" * 80 + "\n"

    for product_name, data in sorted(comparison_data, key=lambda x: x[1].get('total_reports', 0), reverse=True):
        if 'error' not in data:
            summary += f"{product_name:<15} "
            summary += f"{data.get('company', 'N/A'):<20} "
            summary += f"{data.get('total_reports', 0):<10} "
            summary += f"{data.get('crs_rate', 0):<10.1f} "
            summary += f"{data.get('neurotoxicity_rate', 0):<10.1f} "
            summary += f"{data.get('serious_rate', 0):<10.1f}\n"

    summary += "\nKEY FINDINGS:\n"

    # Find products with highest/lowest rates
    valid_products = [(n, d) for n, d in comparison_data if 'error' not in d and d.get('total_reports', 0) > 0]

    if valid_products:
        # CRS rates
        crs_sorted = sorted(valid_products, key=lambda x: x[1].get('crs_rate', 0), reverse=True)
        if crs_sorted:
            summary += f"- Highest CRS rate: {crs_sorted[0][0]} ({crs_sorted[0][1]['crs_rate']:.1f}%)\n"
            if len(crs_sorted) > 1:
                summary += f"- Lowest CRS rate: {crs_sorted[-1][0]} ({crs_sorted[-1][1]['crs_rate']:.1f}%)\n"

        # Neurotoxicity rates
        neuro_sorted = sorted(valid_products, key=lambda x: x[1].get('neurotoxicity_rate', 0), reverse=True)
        if neuro_sorted:
            summary += f"- Highest Neurotoxicity rate: {neuro_sorted[0][0]} ({neuro_sorted[0][1]['neurotoxicity_rate']:.1f}%)\n"
            if len(neuro_sorted) > 1:
                summary += f"- Lowest Neurotoxicity rate: {neuro_sorted[-1][0]} ({neuro_sorted[-1][1]['neurotoxicity_rate']:.1f}%)\n"

    summary += """
CLINICAL SIGNIFICANCE:
- CRS and neurotoxicity are the most common serious adverse events with CAR-T
- Rates vary by product, likely reflecting differences in construct design and patient population
- Real-world data (FAERS) may differ from controlled trial settings
- Consider institutional experience and supportive care protocols in risk assessment

LIMITATIONS:
- FAERS data represents voluntary reporting and may not reflect true incidence
- Reporting biases exist (more likely to report serious/unusual events)
- Patient populations and indications differ across products
- Data should be interpreted alongside clinical trial results and real-world studies
"""

    return summary


if __name__ == "__main__":
    result = get_cart_adverse_events_comparison()
    print(result['summary'])

    # Print detailed results for each product
    print("\n" + "="*80)
    print("DETAILED RESULTS BY PRODUCT")
    print("="*80 + "\n")

    for product_name, data in result['individual_products'].items():
        if 'error' not in data and data.get('total_reports', 0) > 0:
            print(f"\n{product_name} ({data['company']}):")
            print(f"  Indication: {data['indication']}")
            print(f"  Total Reports: {data['total_reports']}")
            print(f"  CRS Events: {data['crs_count']} ({data['crs_rate']}%)")
            print(f"  Neurotoxicity Events: {data['neurotoxicity_count']} ({data['neurotoxicity_rate']}%)")
            print(f"  Serious Events: {data['serious_count']} ({data['serious_rate']}%)")
            print(f"  Deaths: {data['death_count']} ({data['death_rate']}%)")
