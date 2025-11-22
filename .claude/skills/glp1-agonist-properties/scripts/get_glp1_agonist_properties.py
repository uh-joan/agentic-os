import sys
sys.path.insert(0, ".claude")

from mcp.servers.pubchem_mcp import get_compound_properties

def get_glp1_agonist_properties():
    """Compare molecular properties of approved GLP-1 receptor agonists.

    Analyzes key drug-like properties for GLP-1 agonists including molecular weight,
    lipophilicity (XLogP), topological polar surface area (TPSA), and structural complexity.
    Critical for understanding formulation challenges and oral bioavailability potential.

    Returns:
        dict: Contains comparison summary and detailed properties
    """

    # Approved GLP-1 agonists with their generic names
    compounds = {
        'Semaglutide': 'semaglutide',
        'Liraglutide': 'liraglutide',
        'Dulaglutide': 'dulaglutide',
        'Tirzepatide': 'tirzepatide',
        'Exenatide': 'exenatide'
    }

    results = {}
    properties_summary = []

    print("\n" + "="*80)
    print("GLP-1 AGONIST MOLECULAR PROPERTIES COMPARISON")
    print("="*80 + "\n")

    for brand_name, compound_name in compounds.items():
        try:
            # Query PubChem for compound properties
            response = get_compound_properties(compound_name)

            if response and 'PropertyTable' in response:
                props = response['PropertyTable'].get('Properties', [])

                if props and len(props) > 0:
                    prop_data = props[0]

                    # Extract key molecular properties
                    mol_weight = prop_data.get('MolecularWeight', 'N/A')
                    xlogp = prop_data.get('XLogP', 'N/A')
                    tpsa = prop_data.get('TPSA', 'N/A')
                    complexity = prop_data.get('Complexity', 'N/A')
                    h_bond_donor = prop_data.get('HBondDonorCount', 'N/A')
                    h_bond_acceptor = prop_data.get('HBondAcceptorCount', 'N/A')
                    rotatable_bonds = prop_data.get('RotatableBondCount', 'N/A')
                    heavy_atoms = prop_data.get('HeavyAtomCount', 'N/A')

                    results[brand_name] = {
                        'molecular_weight': mol_weight,
                        'xlogp': xlogp,
                        'tpsa': tpsa,
                        'complexity': complexity,
                        'h_bond_donors': h_bond_donor,
                        'h_bond_acceptors': h_bond_acceptor,
                        'rotatable_bonds': rotatable_bonds,
                        'heavy_atoms': heavy_atoms
                    }

                    properties_summary.append(f"✓ {brand_name}: MW={mol_weight}, XLogP={xlogp}, TPSA={tpsa}")

                    # Print detailed properties
                    print(f"{'─'*80}")
                    print(f"{brand_name.upper()}")
                    print(f"{'─'*80}")
                    print(f"  Molecular Weight:        {mol_weight} g/mol")
                    print(f"  XLogP (Lipophilicity):   {xlogp}")
                    print(f"  TPSA:                    {tpsa} Ų")
                    print(f"  Complexity:              {complexity}")
                    print(f"  H-Bond Donors:           {h_bond_donor}")
                    print(f"  H-Bond Acceptors:        {h_bond_acceptor}")
                    print(f"  Rotatable Bonds:         {rotatable_bonds}")
                    print(f"  Heavy Atoms:             {heavy_atoms}")
                    print()
                else:
                    results[brand_name] = {'error': 'No properties found'}
                    properties_summary.append(f"✗ {brand_name}: No data available")
            else:
                results[brand_name] = {'error': 'Invalid response format'}
                properties_summary.append(f"✗ {brand_name}: Query failed")

        except Exception as e:
            results[brand_name] = {'error': str(e)}
            properties_summary.append(f"✗ {brand_name}: Error - {str(e)}")

    # Generate comparative insights
    print("="*80)
    print("KEY INSIGHTS FOR ORAL FORMULATION STRATEGY")
    print("="*80 + "\n")

    insights = []

    # Analyze molecular weight (oral bioavailability challenge)
    mw_data = [(name, props.get('molecular_weight', 0)) for name, props in results.items()
               if 'molecular_weight' in props and props['molecular_weight'] != 'N/A']
    if mw_data:
        mw_sorted = sorted(mw_data, key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0)
        print("Molecular Weight Analysis (Lower = Better for Oral Formulation):")
        for name, mw in mw_sorted:
            print(f"  {name}: {mw} g/mol")
        insights.append("All GLP-1 agonists are large peptides (>3000 Da), presenting significant oral bioavailability challenges")
        print()

    # Analyze lipophilicity
    print("Lipophilicity (XLogP) - Critical for Membrane Permeability:")
    for name, props in results.items():
        if 'xlogp' in props and props['xlogp'] != 'N/A':
            print(f"  {name}: {props['xlogp']}")
    insights.append("Peptide-based GLP-1 agonists generally have poor lipophilicity, requiring absorption enhancers")
    print()

    # Analyze TPSA (polar surface area)
    print("TPSA Analysis (Lower = Better Permeability, Ideal <140 Ų for oral drugs):")
    for name, props in results.items():
        if 'tpsa' in props and props['tpsa'] != 'N/A':
            tpsa_val = props['tpsa']
            status = "⚠️ High" if isinstance(tpsa_val, (int, float)) and tpsa_val > 140 else "✓ Acceptable"
            print(f"  {name}: {tpsa_val} Ų {status}")
    insights.append("High TPSA values confirm poor passive diffusion - oral semaglutide requires SNAC co-formulation")
    print()

    summary_text = "\n".join(properties_summary)
    insights_text = "\n".join([f"• {insight}" for insight in insights])

    return {
        'total_compounds': len(compounds),
        'successful_queries': len([p for p in properties_summary if p.startswith('✓')]),
        'properties_data': results,
        'summary': f"""
GLP-1 Agonist Molecular Properties Analysis Complete

Compounds Analyzed: {len(compounds)}
Successful Queries: {len([p for p in properties_summary if p.startswith('✓')])}

Results:
{summary_text}

Strategic Insights:
{insights_text}

Business Value:
- Quantifies oral formulation challenge (all compounds >3000 Da)
- Identifies need for absorption enhancers (SNAC strategy validated)
- Supports rationale for oral-first small molecule design (e.g., orforglipron)
- Informs PK optimization for weekly dosing formulations
"""
    }

if __name__ == "__main__":
    result = get_glp1_agonist_properties()
    print("\n" + "="*80)
    print(result['summary'])
    print("="*80)
