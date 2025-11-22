import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubchem_mcp import get_compound_properties

def get_anticoagulant_chemical_properties():
    """Get comprehensive chemical properties for anticoagulant drugs from PubChem."""
    compounds = [
        {"name": "Warfarin", "cid": 54678486},
        {"name": "Rivaroxaban", "cid": 9875401},
        {"name": "Apixaban", "cid": 10182969}
    ]
    
    properties = [
        "MolecularFormula", "MolecularWeight", "CanonicalSMILES",
        "InChI", "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount"
    ]
    
    results = []
    for compound in compounds:
        try:
            response = get_compound_properties(
                cid=str(compound["cid"]),
                properties=",".join(properties)
            )
            
            if response and "PropertyTable" in response:
                prop_data = response["PropertyTable"]["Properties"][0]
                results.append({
                    "name": compound["name"],
                    "cid": compound["cid"],
                    "molecular_formula": prop_data.get("MolecularFormula", "N/A"),
                    "molecular_weight": prop_data.get("MolecularWeight", "N/A"),
                    "canonical_smiles": prop_data.get("CanonicalSMILES", "N/A"),
                    "inchi": prop_data.get("InChI", "N/A"),
                    "xlogp": prop_data.get("XLogP", "N/A"),
                    "tpsa": prop_data.get("TPSA", "N/A"),
                    "h_bond_donors": prop_data.get("HBondDonorCount", "N/A"),
                    "h_bond_acceptors": prop_data.get("HBondAcceptorCount", "N/A")
                })
        except Exception as e:
            print(f"Error retrieving data for {compound['name']}: {str(e)}")
    
    return {
        "total_compounds": len(results),
        "compounds_retrieved": [r["name"] for r in results],
        "data": results
    }

if __name__ == "__main__":
    result = get_anticoagulant_chemical_properties()
    print(f"\nAnticoagulant Chemical Properties: {result['total_compounds']} compounds")
    for compound in result['data']:
        print(f"\n{compound['name']} (CID: {compound['cid']})")
        print(f"  Formula: {compound['molecular_formula']}, MW: {compound['molecular_weight']} g/mol")
        print(f"  XLogP: {compound['xlogp']}, TPSA: {compound['tpsa']} Ų")
