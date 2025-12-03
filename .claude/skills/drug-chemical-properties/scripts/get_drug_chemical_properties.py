import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubchem_mcp import get_compound_properties, search_compounds
from typing import List, Optional

def get_drug_chemical_properties(drug_names: Optional[List[str]] = None):
    """Get comprehensive chemical properties for specified drugs from PubChem.

    Note: PubChem API requires specific drug names (not drug classes).
    Drug class searches (e.g., 'oral anticoagulants', 'SGLT2 inhibitors')
    are not supported by the PubChem search API.

    Args:
        drug_names: List of specific drug names (e.g., ['warfarin', 'aspirin']).
                   If None, defaults to major anticoagulants (warfarin, rivaroxaban, apixaban).

    Returns:
        dict: Contains total_compounds, compounds_retrieved, and detailed property data

    Examples:
        # Default anticoagulants
        result = get_drug_chemical_properties()

        # Specific drug list
        result = get_drug_chemical_properties(['semaglutide', 'liraglutide'])
        result = get_drug_chemical_properties(['aspirin'])
        result = get_drug_chemical_properties(['metformin', 'empagliflozin', 'canagliflozin'])
    """

    # Default to major anticoagulants if no drugs specified
    if drug_names is None:
        drug_names = ["Warfarin", "Rivaroxaban", "Apixaban"]

    properties = [
        "MolecularFormula", "MolecularWeight", "CanonicalSMILES",
        "InChI", "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount"
    ]

    results = []

    # Name-based search - need to find CIDs first
    print(f"\nRetrieving chemical properties for {len(drug_names)} drug(s)...\n")

    for drug_name in drug_names:
        print(f"Looking up {drug_name}...")

        # Step 1: Search PubChem to find CID
        try:
            search_result = search_compounds(query=drug_name, max_records=1)

            # Extract CID from PubChem search response
            # Response format: {'details': {'PropertyTable': {'Properties': [{'CID': 2244, ...}]}}}
            if not isinstance(search_result, dict):
                print(f"  ⚠️  Invalid search response for {drug_name}")
                continue

            if 'details' not in search_result:
                print(f"  ⚠️  No results found for {drug_name}")
                continue

            details = search_result['details']
            if 'PropertyTable' not in details or 'Properties' not in details['PropertyTable']:
                print(f"  ⚠️  No compound data for {drug_name}")
                continue

            properties_list = details['PropertyTable']['Properties']
            if not properties_list or len(properties_list) == 0:
                print(f"  ⚠️  No compounds found for {drug_name}")
                continue

            # Get CID from first result
            compound_data = properties_list[0]
            cid = compound_data.get('CID')

            if not cid:
                print(f"  ⚠️  No CID found for {drug_name}")
                continue

            print(f"  Found CID: {cid}")

        except Exception as e:
            print(f"  ❌ Error searching for {drug_name}: {str(e)}")
            continue

        # Step 2: Get chemical properties for the CID
        try:
            # Pass properties as list, not comma-separated string
            response = get_compound_properties(
                cid=str(cid),
                properties=properties
            )

            # Extract properties from PropertyTable.Properties[0]
            if response and "PropertyTable" in response:
                prop_data = response["PropertyTable"]["Properties"][0]
                results.append({
                    "name": drug_name,
                    "cid": cid,
                    "molecular_formula": prop_data.get("MolecularFormula", "N/A"),
                    "molecular_weight": prop_data.get("MolecularWeight", "N/A"),
                    "canonical_smiles": prop_data.get("ConnectivitySMILES", "N/A"),
                    "inchi": prop_data.get("InChI", "N/A"),
                    "xlogp": prop_data.get("XLogP", "N/A"),
                    "tpsa": prop_data.get("TPSA", "N/A"),
                    "h_bond_donors": prop_data.get("HBondDonorCount", "N/A"),
                    "h_bond_acceptors": prop_data.get("HBondAcceptorCount", "N/A")
                })
                print(f"  ✓ Retrieved properties successfully")
            else:
                print(f"  ⚠️  No properties found in response")

        except Exception as e:
            print(f"  ❌ Error retrieving properties for {drug_name}: {str(e)}")
    
    return {
        "total_compounds": len(results),
        "compounds_retrieved": [r["name"] for r in results],
        "data": results
    }

if __name__ == "__main__":
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        # All arguments are drug names
        drug_names = sys.argv[1:]
        print(f"Analyzing {len(drug_names)} user-specified drug(s): {', '.join(drug_names)}")
        result = get_drug_chemical_properties(drug_names)
    else:
        # Default to anticoagulants
        print("No drugs specified - using default anticoagulants (warfarin, rivaroxaban, apixaban)")
        result = get_drug_chemical_properties()

    print(f"\n{'='*80}")
    print(f"DRUG CHEMICAL PROPERTIES ANALYSIS")
    print(f"{'='*80}")
    print(f"\nTotal compounds retrieved: {result['total_compounds']}")

    for compound in result['data']:
        print(f"\n{compound['name']} (CID: {compound['cid']})")
        print(f"  Formula: {compound['molecular_formula']}, MW: {compound['molecular_weight']} g/mol")
        print(f"  XLogP: {compound['xlogp']}, TPSA: {compound['tpsa']} Ų")
        print(f"  H-bond donors: {compound['h_bond_donors']}, H-bond acceptors: {compound['h_bond_acceptors']}")

    print(f"\n{'='*80}")
