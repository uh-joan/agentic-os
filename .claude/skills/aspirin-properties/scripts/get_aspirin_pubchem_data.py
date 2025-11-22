import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubchem_mcp import get_compound_properties

def get_aspirin_pubchem_data():
    """Get molecular properties and chemical data for aspirin from PubChem.
    
    Returns:
        dict: Contains compound properties
    """
    result = get_compound_properties(
        compound_name="aspirin",
        properties=["MolecularFormula", "MolecularWeight", "CanonicalSMILES", "InChI", "InChIKey", "XLogP", "TPSA", "Complexity", "HBondDonorCount", "HBondAcceptorCount", "RotatableBondCount", "ExactMass", "MonoisotopicMass"]
    )
    
    if not result or 'PropertyTable' not in result:
        return {'success': False, 'error': 'No data found for aspirin'}
    
    properties = result['PropertyTable']['Properties'][0]
    
    compound_data = {
        'cid': properties.get('CID'),
        'molecular_formula': properties.get('MolecularFormula'),
        'molecular_weight': properties.get('MolecularWeight'),
        'canonical_smiles': properties.get('CanonicalSMILES'),
        'xlogp': properties.get('XLogP'),
        'tpsa': properties.get('TPSA'),
        'complexity': properties.get('Complexity')
    }
    
    summary = f"""Aspirin (PubChem CID: {compound_data['cid']})
Formula: {compound_data['molecular_formula']}
Weight: {compound_data['molecular_weight']} g/mol
LogP: {compound_data['xlogp']}
TPSA: {compound_data['tpsa']} Ų
SMILES: {compound_data['canonical_smiles']}"""
    
    return {'success': True, 'compound_data': compound_data, 'summary': summary}

if __name__ == "__main__":
    result = get_aspirin_pubchem_data()
    print(result['summary'])
