import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubchem_mcp import get_compound_by_name, search_similar_compounds

def get_kras_inhibitor_scaffold_analysis():
    """Analyze structural similarity of KRAS inhibitor scaffolds.

    Uses sotorasib (LUMAKRAS) as reference compound to identify chemically
    similar structures via Tanimoto coefficient. Provides scaffold diversity
    analysis and IP/FTO insights.

    Returns:
        dict: Contains similarity distribution and strategic insights
    """

    print("\n" + "="*80)
    print("KRAS INHIBITOR SCAFFOLD ANALYSIS (Sotorasib Reference)")
    print("="*80 + "\n")

    try:
        # Step 1: Get sotorasib CID
        print("Retrieving sotorasib reference compound...")
        sotorasib_result = get_compound_by_name("sotorasib")

        if not sotorasib_result or 'cid' not in sotorasib_result:
            return {
                'error': 'Could not retrieve sotorasib CID',
                'summary': 'Failed to find reference compound'
            }

        sotorasib_cid = sotorasib_result['cid']
        print(f"✓ Sotorasib CID: {sotorasib_cid}\n")

        # Step 2: Similarity search
        print(f"Searching for structurally similar compounds (≥80% Tanimoto)...")
        similar_result = search_similar_compounds(
            cid=sotorasib_cid,
            threshold=80,
            max_records=100
        )

        if not similar_result or 'similar_compounds' not in similar_result:
            return {
                'reference_compound': {
                    'name': 'sotorasib',
                    'cid': sotorasib_cid
                },
                'total_similar_compounds': 0,
                'summary': 'No similar compounds found'
            }

        similar_compounds = similar_result['similar_compounds']
        print(f"✓ Found {len(similar_compounds)} similar compounds\n")

        # Step 3: Analyze similarity distribution
        similarity_distribution = {
            'high_similarity_90_100': 0,
            'medium_similarity_85_90': 0,
            'moderate_similarity_80_85': 0
        }

        detailed_compounds = []

        for compound in similar_compounds:
            cid = compound.get('CID')
            similarity = compound.get('similarity_score', 0)

            # Categorize by similarity tier
            if similarity >= 90:
                tier = 'high_similarity_90_100'
                tier_label = 'High (90-100%)'
            elif similarity >= 85:
                tier = 'medium_similarity_85_90'
                tier_label = 'Medium (85-90%)'
            else:
                tier = 'moderate_similarity_80_85'
                tier_label = 'Moderate (80-85%)'

            similarity_distribution[tier] += 1

            detailed_compounds.append({
                'cid': cid,
                'similarity_score': similarity,
                'similarity_tier': tier_label
            })

        # Sort by similarity score
        detailed_compounds.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Generate summary
        print("="*80)
        print("SIMILARITY DISTRIBUTION")
        print("="*80 + "\n")
        print(f"  High Similarity (90-100%):     {similarity_distribution['high_similarity_90_100']} compounds")
        print(f"  Medium Similarity (85-90%):    {similarity_distribution['medium_similarity_85_90']} compounds")
        print(f"  Moderate Similarity (80-85%):  {similarity_distribution['moderate_similarity_80_85']} compounds")
        print(f"\nTotal Similar Compounds: {len(similar_compounds)}")

        print("\n" + "="*80)
        print("IP/FTO STRATEGIC INSIGHTS")
        print("="*80 + "\n")

        insights = []

        # Assess chemical space crowding
        if similarity_distribution['high_similarity_90_100'] > 20:
            crowding = "highly crowded"
            insights.append("⚠️  Chemical space around sotorasib is HIGHLY CROWDED")
        elif similarity_distribution['high_similarity_90_100'] > 10:
            crowding = "moderately crowded"
            insights.append("⚠️  Chemical space around sotorasib is moderately crowded")
        else:
            crowding = "relatively open"
            insights.append("✓ Chemical space around sotorasib is relatively open")

        # High similarity IP risk
        high_sim = similarity_distribution['high_similarity_90_100']
        insights.append(f"• {high_sim} high-similarity compounds suggest established IP coverage")

        # Scaffold hopping opportunities
        moderate_sim = similarity_distribution['moderate_similarity_80_85']
        insights.append(f"• {moderate_sim} moderate-similarity compounds offer scaffold hopping opportunities")

        # Design-around strategy
        insights.append("• Consider exploring <80% similarity space for true structural novelty")

        for insight in insights:
            print(insight)

        print("\n" + "="*80)
        print("TOP 10 MOST SIMILAR COMPOUNDS")
        print("="*80 + "\n")
        print(f"{'CID':<15} {'Similarity':<12} {'Tier':<20}")
        print(f"{'-'*15} {'-'*12} {'-'*20}")

        for compound in detailed_compounds[:10]:
            print(f"{compound['cid']:<15} {compound['similarity_score']:<12.1f} {compound['similarity_tier']:<20}")

        print("\n" + "="*80 + "\n")

        summary_lines = [
            f"KRAS INHIBITOR SCAFFOLD ANALYSIS (Sotorasib Reference)",
            f"",
            f"Reference Compound: Sotorasib (CID {sotorasib_cid})",
            f"Similarity Threshold: 80% Tanimoto",
            f"",
            f"SIMILARITY DISTRIBUTION:",
            f"  High Similarity (90-100%):     {similarity_distribution['high_similarity_90_100']} compounds",
            f"  Medium Similarity (85-90%):    {similarity_distribution['medium_similarity_85_90']} compounds",
            f"  Moderate Similarity (80-85%):  {similarity_distribution['moderate_similarity_80_85']} compounds",
            f"",
            f"Total Similar Compounds: {len(similar_compounds)}",
            f"",
            f"IP/FTO STRATEGIC INSIGHTS:",
        ]

        summary_lines.extend([f"  {insight}" for insight in insights])

        return {
            'reference_compound': {
                'name': 'sotorasib',
                'cid': sotorasib_cid
            },
            'total_similar_compounds': len(similar_compounds),
            'similarity_distribution': similarity_distribution,
            'chemical_space_crowding': crowding,
            'similar_compounds': detailed_compounds,
            'summary': '\n'.join(summary_lines)
        }

    except Exception as e:
        return {
            'error': str(e),
            'summary': f'Error analyzing KRAS inhibitor scaffolds: {str(e)}'
        }

if __name__ == "__main__":
    result = get_kras_inhibitor_scaffold_analysis()
    if 'error' in result:
        print(f"ERROR: {result['error']}")
    else:
        print(result['summary'])
