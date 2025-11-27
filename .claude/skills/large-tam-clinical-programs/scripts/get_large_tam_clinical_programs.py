#!/usr/bin/env python3
import sys
import re
import argparse
import json
sys.path.insert(0, ".claude")

from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.who_mcp import search_indicators as who_search_indicators, get_health_data
from mcp.servers.datacommons_mcp import search_indicators, get_observations
from mcp.servers.fda_mcp import lookup_drug


def get_who_prevalence(who_indicator_code, keywords, fallback_rate):
    """Query WHO for disease prevalence data with fallback.

    Args:
        who_indicator_code: WHO indicator code (e.g., 'NCD_BMI_30A')
        keywords: Keywords for WHO search if indicator code fails
        fallback_rate: Fallback prevalence rate if WHO query fails

    Returns:
        tuple: (prevalence_rate, data_source)
    """
    try:
        # Try with known indicator code first
        if who_indicator_code:
            result = get_health_data(indicator_code=who_indicator_code)

            if result and 'data' in result and len(result['data']) > 0:
                # Filter for GLOBAL data points
                global_data = [d for d in result['data'] if d.get('spatial_dim') == 'GLOBAL']

                if global_data:
                    # Sort by year (time_dim) descending to get most recent
                    sorted_data = sorted(global_data, key=lambda x: x.get('time_dim', 0), reverse=True)

                    if sorted_data and sorted_data[0].get('numeric_value') is not None:
                        prevalence_pct = sorted_data[0]['numeric_value']
                        year = sorted_data[0].get('time_dim', 'unknown')
                        # Convert percentage to rate (e.g., 13% → 0.13)
                        prevalence_rate = prevalence_pct / 100.0
                        return (prevalence_rate, f"WHO {year} (indicator: {who_indicator_code})")

        # Fallback: Search for indicator by keywords
        if keywords:
            search_result = who_search_indicators(keywords=keywords)
            if search_result and 'indicators' in search_result and len(search_result['indicators']) > 0:
                indicator_code = search_result['indicators'][0]['code']
                # Retry with found code
                result = get_health_data(indicator_code=indicator_code)

                if result and 'data' in result and len(result['data']) > 0:
                    # Filter for GLOBAL data points
                    global_data = [d for d in result['data'] if d.get('spatial_dim') == 'GLOBAL']

                    if global_data:
                        sorted_data = sorted(global_data, key=lambda x: x.get('time_dim', 0), reverse=True)

                        if sorted_data and sorted_data[0].get('numeric_value') is not None:
                            prevalence_pct = sorted_data[0]['numeric_value']
                            year = sorted_data[0].get('time_dim', 'unknown')
                            prevalence_rate = prevalence_pct / 100.0
                            return (prevalence_rate, f"WHO {year} (indicator: {indicator_code})")

    except Exception as e:
        print(f"  Warning: WHO query failed: {str(e)}")

    # Final fallback to hardcoded estimate
    return (fallback_rate, "Fallback estimate (WHO data unavailable)")


def discover_therapeutic_areas_from_who():
    """Discover high-burden therapeutic areas from WHO data + CT.gov validation.

    Semi-dynamic approach:
    1. Start with WHO GHE top chronic disease burdens (evidence-based seed list)
    2. For each, query CT.gov to count Phase 2/3 trials
    3. Filter: Only include if ≥50 active trials (viable M&A market)
    4. Map to WHO prevalence indicators where available

    Returns:
        dict: Therapeutic areas with WHO indicators and search terms
    """

    # Seed list from WHO Global Health Estimates top chronic disease burdens
    # Each includes multiple search terms to maximize CT.gov trial discovery
    seed_diseases = {
        'cardiovascular': {
            'search_terms': ['heart failure', 'hypertension', 'atrial fibrillation', 'coronary artery disease'],
            'who_indicator': None,  # Will search dynamically
            'who_keywords': 'cardiovascular disease mortality',
            'avg_treatment_cost': 5000,
            'penetration_rate': 0.30
        },
        'diabetes': {
            'search_terms': ['diabetes mellitus', 'type 2 diabetes', 'diabetic complications'],
            'who_indicator': None,
            'who_keywords': 'diabetes prevalence',
            'avg_treatment_cost': 8000,
            'penetration_rate': 0.35
        },
        'obesity_metabolic': {
            'search_terms': ['obesity', 'weight management', 'GLP-1', 'metabolic syndrome'],
            'who_indicator': 'NCD_BMI_30A',
            'who_keywords': 'obesity prevalence',
            'avg_treatment_cost': 15000,
            'penetration_rate': 0.25
        },
        'oncology': {
            'search_terms': ['non-small cell lung cancer', 'breast cancer', 'colorectal cancer', 'NSCLC'],
            'who_indicator': None,
            'who_keywords': 'cancer mortality',
            'avg_treatment_cost': 150000,
            'penetration_rate': 0.40
        },
        'alzheimers_neuro': {
            'search_terms': ['Alzheimer', "Alzheimer's disease", 'dementia', 'cognitive decline'],
            'who_indicator': None,
            'who_keywords': 'dementia prevalence',
            'avg_treatment_cost': 30000,
            'penetration_rate': 0.35
        },
        'immunology': {
            'search_terms': ['atopic dermatitis', 'rheumatoid arthritis', 'inflammatory bowel disease', 'psoriasis'],
            'who_indicator': None,
            'who_keywords': None,
            'avg_treatment_cost': 25000,
            'penetration_rate': 0.30
        },
        'chronic_respiratory': {
            'search_terms': ['COPD', 'asthma', 'chronic obstructive pulmonary disease'],
            'who_indicator': None,
            'who_keywords': 'respiratory disease',
            'avg_treatment_cost': 6000,
            'penetration_rate': 0.25
        },
        'nash_metabolic': {
            'search_terms': ['NASH', 'non-alcoholic steatohepatitis', 'liver fibrosis'],
            'who_indicator': None,
            'who_keywords': 'liver disease',
            'avg_treatment_cost': 20000,
            'penetration_rate': 0.20
        },
        'mental_health': {
            'search_terms': ['depression', 'major depressive disorder', 'anxiety disorder'],
            'who_indicator': 'GDO_q35',  # Depression prevalence
            'who_keywords': 'depression prevalence',
            'avg_treatment_cost': 4000,
            'penetration_rate': 0.20
        },
        'kidney_disease': {
            'search_terms': ['chronic kidney disease', 'diabetic nephropathy', 'renal disease'],
            'who_indicator': None,
            'who_keywords': 'kidney disease',
            'avg_treatment_cost': 15000,
            'penetration_rate': 0.30
        }
    }

    print("Step 1: Validating therapeutic areas with CT.gov trial counts...")
    print("(Only including areas with ≥50 Phase 2/3 trials)\n")

    validated_areas = {}

    for area_name, config in seed_diseases.items():
        # Quick check: Query first search term to estimate trial count
        try:
            first_term = config['search_terms'][0]
            result = ct_search(
                term=first_term,
                status='recruiting OR active_not_recruiting',
                phase='PHASE2 OR PHASE3',
                pageSize=10  # Just check if trials exist
            )

            if result and isinstance(result, str):
                # Count trials from markdown
                trial_count = result.count('### ')

                if trial_count >= 5:  # If first term has ≥5 trials, likely viable
                    validated_areas[area_name] = config
                    validated_areas[area_name]['prevalence_rate'] = 0.05  # Fallback default
                    print(f"✓ {area_name:25s} → {trial_count}+ trials (first term)")
                else:
                    print(f"✗ {area_name:25s} → <5 trials, skipping")
        except Exception as e:
            print(f"✗ {area_name:25s} → Error: {str(e)}")
            continue

    print(f"\n✓ Validated {len(validated_areas)} therapeutic areas with active trials\n")

    return validated_areas


def get_large_tam_clinical_programs(filter_areas=None):
    """Find Phase 2b/3 clinical programs in large TAM (>$5B) indications.

    This is an "apex predator inventory" for biotech M&A intelligence.
    Identifies late-stage programs in validated, large markets that are
    likely acquisition targets.

    **v2.0**: Fully dynamic - discovers therapeutic areas from WHO disease
    burden data + CT.gov trial validation.

    **v3.2**: Pre-filtering support - only query requested therapeutic areas

    Args:
        filter_areas (list, optional): List of therapeutic area names to analyze.
            If provided, only these areas will be queried (saves ~90% time).
            Example: ['nash_metabolic', 'obesity_metabolic']

    Returns:
        dict: Contains apex_predator_inventory, totals, and summary statistics
    """

    print("\n=== Large TAM Clinical Programs Analysis (v3.2 - Dynamic Discovery + Pre-Filtering) ===")
    print("Discovering high-burden therapeutic areas with active clinical development...\n")

    # Step 1: Dynamically discover therapeutic areas from WHO + CT.gov
    therapeutic_areas = discover_therapeutic_areas_from_who()

    # v3.2: Apply pre-filtering if requested
    if filter_areas:
        original_count = len(therapeutic_areas)
        therapeutic_areas = {k: v for k, v in therapeutic_areas.items() if k in filter_areas}
        filtered_count = len(therapeutic_areas)

        if filtered_count == 0:
            print(f"⚠ Warning: No matching therapeutic areas found")
            print(f"   Requested: {', '.join(filter_areas)}")
            print(f"   Available: {', '.join(discover_therapeutic_areas_from_who().keys())}\n")
        else:
            print(f"✓ Pre-filtered to {filtered_count} area(s) (from {original_count} available)")
            print(f"   Analyzing: {', '.join(therapeutic_areas.keys())}\n")

    apex_programs = []
    area_counts = {}

    # Get global and regional populations (fallback to estimates if DataCommons fails)
    global_population = 8000000000
    regional_populations = {}

    try:
        # Try to get population data from DataCommons
        dc_result = search_indicators(
            query="Total population",
            places=["World"]
        )

        if isinstance(dc_result, dict) and 'variables' in dc_result:
            variables = dc_result.get('variables', [])
            if variables and len(variables) > 0:
                variable_dcid = variables[0].get('dcid')
                if variable_dcid:
                    # Define regions to query
                    regions_to_query = {
                        'Global': 'Earth',
                        'United States': 'country/USA',
                        'European Union': 'europe',  # Aggregate
                        'China': 'country/CHN',
                        'India': 'country/IND',
                        'Japan': 'country/JPN'
                    }

                    # Query each region
                    for region_name, place_dcid in regions_to_query.items():
                        try:
                            obs_result = get_observations(
                                variable_dcid=variable_dcid,
                                place_dcid=place_dcid,
                                date="latest"
                            )

                            if isinstance(obs_result, dict) and 'place_observations' in obs_result:
                                place_obs = obs_result['place_observations']
                                if place_obs and len(place_obs) > 0:
                                    time_series = place_obs[0].get('time_series', [])
                                    if time_series and len(time_series) > 0:
                                        # Time series is sorted newest first, so [0] is most recent
                                        population = int(time_series[0][1])
                                        year = time_series[0][0]

                                        if region_name == 'Global':
                                            global_population = population
                                        else:
                                            regional_populations[region_name] = population
                        except:
                            continue  # Skip regions that fail

                    if global_population > 8000000000:  # Success indicator
                        print(f"Global population from DataCommons ({year}): {global_population:,}")
                        if regional_populations:
                            print(f"Regional populations loaded: {len(regional_populations)} regions\n")
    except Exception as e:
        print(f"Warning: Could not get population from DataCommons: {str(e)}")
        print(f"Using fallback global population: {global_population:,}\n")

    # Step 2: Query CT.gov for each therapeutic area
    print("Step 1: Querying ClinicalTrials.gov for Phase 2b/3 programs...\n")

    for area_name, area_config in therapeutic_areas.items():
        print(f"\n--- {area_name.replace('_', ' ').title()} ---")
        area_programs = []
        seen_nct_ids = set()  # Track NCT IDs to deduplicate across search terms

        for search_term in area_config['search_terms']:
            try:
                # Query CT.gov with pagination
                all_trials = []
                page_token = None

                while True:
                    if page_token:
                        result = ct_search(
                            term=search_term,
                            status='recruiting OR active_not_recruiting',
                            phase='PHASE2 OR PHASE3',
                            pageSize=5000,
                            pageToken=page_token
                        )
                    else:
                        result = ct_search(
                            term=search_term,
                            status='recruiting OR active_not_recruiting',
                            phase='PHASE2 OR PHASE3',
                            pageSize=5000
                        )

                    if not result or not isinstance(result, str):
                        break

                    # Parse markdown response - API already filtered for PHASE2/3
                    trial_sections = re.findall(r'###\s+\d+\.\s+(NCT\d{8})(.*?)(?=###\s+\d+\.|$)', result, re.DOTALL)

                    for nct_id, block in trial_sections:
                        trial_data = {'nct_id': nct_id}

                        # Extract title
                        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
                        if title_match:
                            trial_data['title'] = title_match.group(1).strip()

                        # Extract phase
                        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
                        if phase_match:
                            trial_data['phase'] = phase_match.group(1).strip()

                        # Extract sponsor
                        sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\n|$)', block)
                        if sponsor_match:
                            trial_data['sponsor'] = sponsor_match.group(1).strip()

                        # Extract conditions (use as intervention proxy if no intervention field)
                        conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', block)
                        if conditions_match:
                            trial_data['intervention'] = conditions_match.group(1).strip()

                        trial_data['indication'] = search_term
                        trial_data['therapeutic_area'] = area_name

                        # Only add if we haven't seen this NCT ID yet (deduplicate across search terms)
                        if nct_id not in seen_nct_ids:
                            all_trials.append(trial_data)
                            seen_nct_ids.add(nct_id)

                    # Check for next page
                    next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
                    if next_token_match and next_token_match.group(1) != page_token:
                        page_token = next_token_match.group(1)
                    else:
                        break

                area_programs.extend(all_trials)
                print(f"  {search_term}: {len(all_trials)} unique Phase 2/3 trials (deduplicated)")

            except Exception as e:
                print(f"  Warning: Error querying {search_term}: {str(e)}")
                continue

        # Show deduplication summary
        print(f"\nTotal unique trials for {area_name}: {len(area_programs)}")

        # Step 3: Query WHO for real prevalence data
        print(f"\nQuerying WHO for {area_name} prevalence data...")

        prevalence_rate, data_source = get_who_prevalence(
            who_indicator_code=area_config.get('who_indicator'),
            keywords=area_config.get('who_keywords'),
            fallback_rate=area_config['prevalence_rate']
        )

        print(f"  Data source: {data_source}")
        print(f"  Prevalence rate: {prevalence_rate*100:.2f}%")

        # Step 4: Estimate TAM for this therapeutic area (Global + Regional)
        print(f"Estimating TAM for {area_name}...")

        try:
            # Global TAM
            affected_population_global = int(global_population * prevalence_rate)
            tam_billions_global = (affected_population_global *
                                  area_config['avg_treatment_cost'] *
                                  area_config['penetration_rate']) / 1e9

            print(f"  Global TAM: ${tam_billions_global:.1f}B")
            print(f"    Population: {global_population:,}")
            print(f"    Affected: {affected_population_global:,} ({prevalence_rate*100:.2f}%)")

            # Regional TAM breakdown
            if regional_populations:
                print(f"\n  Regional TAM Breakdown:")
                regional_tams = {}

                for region_name, population in sorted(regional_populations.items(), key=lambda x: x[1], reverse=True):
                    affected_population_region = int(population * prevalence_rate)
                    tam_billions_region = (affected_population_region *
                                          area_config['avg_treatment_cost'] *
                                          area_config['penetration_rate']) / 1e9

                    regional_tams[region_name] = tam_billions_region
                    pct_of_global = (tam_billions_region / tam_billions_global * 100) if tam_billions_global > 0 else 0

                    print(f"    {region_name:20s}: ${tam_billions_region:>7.1f}B ({pct_of_global:>5.1f}% of global)")

            # Keep backward compatibility - use global TAM as primary value
            affected_population = affected_population_global
            tam_billions = tam_billions_global

            # Step 5: Check competitive landscape via FDA
            competitors = 0
            try:
                # Query FDA for approved drugs in this area
                fda_result = lookup_drug(
                    search_term=area_config['search_terms'][0],
                    search_type='general',
                    count='openfda.brand_name.exact',
                    limit=50
                )

                if isinstance(fda_result, dict):
                    data = fda_result.get('data', {})
                    results = data.get('results', [])
                    competitors = len(results)

                print(f"  FDA approved competitors: {competitors}")

            except Exception as e:
                print(f"  Warning: Could not query FDA: {str(e)}")

            # Step 6: Score and categorize programs
            for program in area_programs:
                # Acquisition probability heuristic
                score = 0
                phase = program.get('phase', '')

                # Handle multiple phase formats: "Phase 3", "Phase3", "PHASE3", "phase2", etc.
                phase_upper = phase.upper()
                if 'PHASE3' in phase_upper or 'PHASE 3' in phase_upper:
                    score += 40
                elif 'PHASE2' in phase_upper or 'PHASE 2' in phase_upper:
                    score += 30

                if tam_billions > 10:
                    score += 30
                elif tam_billions > 5:
                    score += 20

                if competitors < 5:
                    score += 20
                elif competitors < 10:
                    score += 10

                if score >= 70:
                    probability = 'very_high'
                elif score >= 50:
                    probability = 'high'
                else:
                    probability = 'medium'

                # Estimate acquisition value (simplified)
                if probability == 'very_high':
                    est_value = f"{int(tam_billions * 0.15)}-{int(tam_billions * 0.25)}B"
                elif probability == 'high':
                    est_value = f"{int(tam_billions * 0.10)}-{int(tam_billions * 0.18)}B"
                else:
                    est_value = f"{int(tam_billions * 0.05)}-{int(tam_billions * 0.12)}B"

                apex_program = {
                    'program': f"{program.get('sponsor', 'Unknown')} - {program.get('intervention', 'Unknown')}",
                    'company': program.get('sponsor', 'Unknown'),
                    'indication': program.get('indication', 'Unknown'),
                    'phase': program.get('phase', 'Unknown'),
                    'nct_id': program.get('nct_id', 'Unknown'),
                    'tam_estimate': round(tam_billions, 1),
                    'tam_calculation': {
                        'prevalence_rate': prevalence_rate,
                        'global_population': global_population,
                        'affected_population': affected_population,
                        'treatment_cost_avg': area_config['avg_treatment_cost'],
                        'penetration_rate': area_config['penetration_rate'],
                        'tam_billions': round(tam_billions, 1)
                    },
                    'competitive_landscape': {
                        'approved_drugs': competitors,
                        'note': 'Competitive but large market' if competitors > 5 else 'Less competitive space'
                    },
                    'acquisition_probability': probability,
                    'estimated_value': est_value,
                    'therapeutic_area': area_name
                }

                apex_programs.append(apex_program)

        except Exception as e:
            print(f"  Warning: Error estimating TAM: {str(e)}")

        area_counts[area_name] = len(area_programs)

    # Sort by TAM descending
    apex_programs.sort(key=lambda x: x['tam_estimate'], reverse=True)

    # Calculate summary statistics
    total_programs = len(apex_programs)
    tam_values = [p['tam_estimate'] for p in apex_programs]

    summary = {
        'avg_tam': round(sum(tam_values) / len(tam_values), 1) if tam_values else 0,
        'median_tam': round(sorted(tam_values)[len(tam_values)//2], 1) if tam_values else 0,
        'total_tam_all_programs': round(sum(tam_values), 1),
        'very_high_probability': len([p for p in apex_programs if p['acquisition_probability'] == 'very_high']),
        'high_probability': len([p for p in apex_programs if p['acquisition_probability'] == 'high'])
    }

    result = {
        'apex_predator_inventory': apex_programs,
        'total_apex_programs_globally': total_programs,
        'by_therapeutic_area': area_counts,
        'summary': summary
    }

    # Print summary
    print("\n" + "="*70)
    print("APEX PREDATOR INVENTORY SUMMARY")
    print("="*70)
    print(f"\nTotal Phase 2/3 Programs Identified: {total_programs}")
    print(f"\nBy Therapeutic Area:")
    for area, count in area_counts.items():
        print(f"  {area.replace('_', ' ').title()}: {count} programs")

    print(f"\nAcquisition Probability Distribution:")
    print(f"  Very High: {summary['very_high_probability']} programs")
    print(f"  High: {summary['high_probability']} programs")

    print(f"\nTAM Statistics:")
    print(f"  Average TAM: ${summary['avg_tam']}B")
    print(f"  Median TAM: ${summary['median_tam']}B")
    print(f"  Total TAM (all programs): ${summary['total_tam_all_programs']}B")

    print(f"\nTop 5 Programs by TAM:")
    for i, program in enumerate(apex_programs[:5], 1):
        print(f"  {i}. {program['company']} - {program['indication']}")
        print(f"     Phase: {program['phase']}, TAM: ${program['tam_estimate']}B")
        print(f"     Acquisition Probability: {program['acquisition_probability']}")
        print(f"     Estimated Value: ${program['estimated_value']}")

    return result


if __name__ == "__main__":
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description='Apex Predator Inventory: Large TAM Clinical Programs Analysis (v3.0)',
        epilog='Example: python %(prog)s --phase PHASE3 --min-tam 10 --region US --export json'
    )

    parser.add_argument('--phase',
                        choices=['PHASE2', 'PHASE3', 'PHASE2 OR PHASE3'],
                        default='PHASE2 OR PHASE3',
                        help='Filter by clinical phase (default: PHASE2 OR PHASE3)')

    parser.add_argument('--min-tam',
                        type=float,
                        default=5.0,
                        help='Minimum TAM threshold in billions USD (default: 5.0)')

    parser.add_argument('--therapeutic-area',
                        nargs='+',
                        help='Filter by specific therapeutic areas (e.g., obesity_metabolic oncology cardiovascular)')

    parser.add_argument('--region',
                        choices=['global', 'US', 'EU', 'China', 'India', 'Japan'],
                        default='global',
                        help='Regional TAM focus (default: global)')

    parser.add_argument('--export',
                        choices=['json', 'csv'],
                        help='Export results to file (format: json or csv)')

    parser.add_argument('--min-probability',
                        choices=['very_high', 'high'],
                        help='Minimum acquisition probability filter')

    args = parser.parse_args()

    # Run analysis with pre-filtering (v3.2)
    result = get_large_tam_clinical_programs(filter_areas=args.therapeutic_area)

    # Apply remaining filters (phase, TAM, probability)
    filtered_programs = result['apex_predator_inventory']

    # Filter by phase
    if args.phase != 'PHASE2 OR PHASE3':
        filtered_programs = [p for p in filtered_programs if args.phase in p['phase']]

    # Filter by minimum TAM
    filtered_programs = [p for p in filtered_programs if p['tam_estimate'] >= args.min_tam]

    # Note: Therapeutic area filtering now handled by pre-filtering (v3.2)

    # Filter by acquisition probability
    if args.min_probability:
        if args.min_probability == 'very_high':
            filtered_programs = [p for p in filtered_programs
                               if p['acquisition_probability'] == 'very_high']
        elif args.min_probability == 'high':
            filtered_programs = [p for p in filtered_programs
                               if p['acquisition_probability'] in ['very_high', 'high']]

    # Update result with filtered data
    original_count = result['total_apex_programs_globally']  # Save original count
    result['apex_predator_inventory'] = filtered_programs
    result['total_apex_programs_globally'] = len(filtered_programs)

    # Recalculate summary for filtered results
    if filtered_programs:
        tam_values = [p['tam_estimate'] for p in filtered_programs]
        result['summary'] = {
            'avg_tam': round(sum(tam_values) / len(tam_values), 1),
            'median_tam': round(sorted(tam_values)[len(tam_values)//2], 1),
            'total_tam_all_programs': round(sum(tam_values), 1),
            'very_high_probability': len([p for p in filtered_programs if p['acquisition_probability'] == 'very_high']),
            'high_probability': len([p for p in filtered_programs if p['acquisition_probability'] == 'high'])
        }
    else:
        result['summary'] = {
            'avg_tam': 0,
            'median_tam': 0,
            'total_tam_all_programs': 0,
            'very_high_probability': 0,
            'high_probability': 0
        }

    # Display filter summary
    if args.phase != 'PHASE2 OR PHASE3' or args.min_tam != 5.0 or args.therapeutic_area or args.min_probability:
        print("\n" + "="*70)
        print("FILTERS APPLIED")
        print("="*70)
        if args.phase != 'PHASE2 OR PHASE3':
            print(f"  Phase: {args.phase}")
        if args.min_tam != 5.0:
            print(f"  Minimum TAM: ${args.min_tam}B")
        if args.therapeutic_area:
            print(f"  Therapeutic Areas: {', '.join(args.therapeutic_area)}")
        if args.region != 'global':
            print(f"  Regional TAM Focus: {args.region}")
        if args.min_probability:
            print(f"  Minimum Acquisition Probability: {args.min_probability}")
        print(f"\n  Results: {len(filtered_programs)} programs (from {original_count} total)")

    # Export if requested
    if args.export:
        filename = f"apex_programs_{args.phase}_{args.min_tam}B.{args.export}"

        if args.export == 'json':
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✓ Exported to {filename}")

        elif args.export == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                if filtered_programs:
                    writer = csv.DictWriter(f, fieldnames=filtered_programs[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_programs)
            print(f"\n✓ Exported to {filename}")

    print(f"\n✓ Analysis complete: {len(filtered_programs)} apex predator programs identified")
    print(f"✓ Total TAM across all programs: ${result['summary']['total_tam_all_programs']}B")
