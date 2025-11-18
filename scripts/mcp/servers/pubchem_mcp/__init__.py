"""PubChem MCP Server - Python API

Provides Python functions for PubChem compound and chemical property data.
Data stays in execution environment - only summaries flow to model.

🔴 CRITICAL: USE ALTERNATIVES FOR BROKEN METHODS
See scripts/mcp/servers/pubchem_mcp/alternatives.py for working alternatives:
- get_safety_data_alternative() - Replaces broken safety data (99.998% token savings)
- search_similar_compounds_alternative() - Replaces broken similarity search (FIXES 400 error)
- get_ghs_classification_summary() - Minimal GHS codes (<500 tokens)

Full documentation: scripts/mcp/servers/ALTERNATIVES_README.md

TOKEN USAGE MEASUREMENTS:
- search_compounds: ~200 tokens ✅ Excellent
- get_compound_properties: ~150 tokens ✅ Excellent (RECOMMENDED)
- get_compound_info: ~3,000 tokens ⚠️ Use properties instead
- get_compound_synonyms: ~6,000 tokens ⚠️ Large for popular drugs
- get_safety_data: 21,900,000 tokens 🔴 UNUSABLE (exceeds MCP limit)
  → USE ALTERNATIVE: get_safety_data_alternative() returns 500-2,000 tokens
- search_similar_compounds: ❌ BROKEN (returns 400 error)
  → USE ALTERNATIVE: search_similar_compounds_alternative() FIXES this

BEST PRACTICES:
1. ✅ Use get_compound_properties instead of get_compound_info (95% token savings)
2. ✅ Limit max_records for searches (default 5-10)
3. ❌ DO NOT use get_safety_data - USE get_safety_data_alternative() instead
4. ❌ DO NOT use search_similar_compounds - USE search_similar_compounds_alternative() instead
5. ⚠️ Be cautious with synonyms for popular drugs (can be 6k+ tokens)

CRITICAL PUBCHEM QUIRKS:
1. CID (Compound ID): Primary identifier for all lookups
2. Search workflow: Name → CID → Properties (two-step)
3. SMILES: Use for exact structure matching
4. InChI: Alternative structure identifier
5. max_records: Default 100, max 10000
6. Response format: JSON with nested property data
7. 🔴 get_safety_data is BROKEN - returns 21.9M tokens (876x over limit)
   → SOLUTION: Use alternatives.py with field selection
8. ❌ search_similar_compounds is BROKEN - returns 400 error
   → SOLUTION: Use alternatives.py with FastSimilarity API
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, Union, List


def search_compounds(
    query: str,
    search_type: str = "name",
    max_records: int = 100
) -> Dict[str, Any]:
    """
    Search for compounds by name, CAS number, or formula

    Args:
        query: Search query
               - Name: "aspirin", "semaglutide", "ibuprofen"
               - CAS: "50-78-2" (aspirin CAS number)
               - Formula: "C9H8O4" (aspirin formula)
               - SMILES: "CC(=O)Oc1ccccc1C(=O)O"

        search_type: Type of search (default: "name")
                    Values: "name", "smiles", "inchi", "sdf", "cid", "formula"

        max_records: Maximum results (1-10000, default: 100)

    Returns:
        dict: PubChem API response with compound matches

        Key fields:
        - CID: PubChem Compound ID (use for get_compound_info)
        - MolecularFormula: Chemical formula
        - MolecularWeight: Molecular weight
        - IUPACName: IUPAC systematic name

    Examples:
        # Search by name
        results = search_compounds(query="aspirin", max_records=10)

        # Extract CIDs
        cids = []
        for compound in results.get('data', []):
            cid = compound.get('CID')
            formula = compound.get('MolecularFormula')
            mw = compound.get('MolecularWeight')
            print(f"CID {cid}: {formula}, MW={mw}")
            cids.append(cid)

        # Search by CAS number
        results = search_compounds(query="50-78-2", search_type="name")

        # Search by SMILES (exact structure)
        results = search_compounds(
            query="CC(=O)Oc1ccccc1C(=O)O",
            search_type="smiles"
        )
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'search_compounds',
        'query': query,
        'search_type': search_type,
        'max_records': max_records
    }

    return client.call_tool('pubchem', params)


def get_compound_info(
    cid: Union[str, int]
) -> Dict[str, Any]:
    """
    Get detailed information for a specific compound

    Args:
        cid: PubChem Compound ID
             Get from search_compounds()
             Can be string or integer (e.g., "2244" or 2244)

    Returns:
        dict: Detailed compound information

        Key fields:
        - CID: PubChem Compound ID
        - MolecularFormula: Chemical formula
        - MolecularWeight: Molecular weight
        - CanonicalSMILES: SMILES notation
        - InChI: InChI identifier
        - IUPACName: IUPAC name
        - Title: Common name
        - Description: Compound description

    Examples:
        # Get aspirin details (CID 2244)
        compound = get_compound_info(cid="2244")

        # Extract properties
        cid = compound.get('CID')
        formula = compound.get('MolecularFormula')
        mw = compound.get('MolecularWeight')
        smiles = compound.get('CanonicalSMILES')
        iupac = compound.get('IUPACName')

        print(f"CID: {cid}")
        print(f"Formula: {formula}")
        print(f"MW: {mw}")
        print(f"SMILES: {smiles}")
        print(f"IUPAC: {iupac}")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'get_compound_info',
        'cid': str(cid)
    }

    return client.call_tool('pubchem', params)


def search_by_smiles(
    smiles: str,
    threshold: int = 90
) -> Dict[str, Any]:
    """
    Search for similar compounds using SMILES structure

    Args:
        smiles: SMILES notation of query molecule
                Example: "CC(=O)Oc1ccccc1C(=O)O" (aspirin)

        threshold: Similarity threshold (0-100, default: 90)
                  Higher = more similar structures

    Returns:
        dict: Compounds with structural similarity

    Examples:
        # Find compounds similar to aspirin
        results = search_by_smiles(
            smiles="CC(=O)Oc1ccccc1C(=O)O",
            threshold=85
        )

        # Process similar structures
        for compound in results.get('data', []):
            cid = compound.get('CID')
            similarity = compound.get('Similarity')
            print(f"CID {cid}: {similarity}% similar")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'search_by_smiles',
        'smiles': smiles,
        'threshold': threshold
    }

    return client.call_tool('pubchem', params)


def get_compound_synonyms(
    cid: Union[str, int]
) -> Dict[str, Any]:
    """
    Get all names and synonyms for a compound

    Args:
        cid: PubChem Compound ID

    Returns:
        dict: List of compound names and synonyms

    Examples:
        # Get all names for aspirin (CID 2244)
        synonyms = get_compound_synonyms(cid="2244")

        # Extract names
        names = synonyms.get('Synonyms', [])
        print(f"Found {len(names)} names:")
        for name in names[:10]:  # Show first 10
            print(f"  - {name}")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'get_compound_synonyms',
        'cid': str(cid)
    }

    return client.call_tool('pubchem', params)


def get_compound_properties(
    cid: Union[str, int],
    properties: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get molecular properties for a compound

    Args:
        cid: PubChem Compound ID

        properties: Specific properties to retrieve (optional)
                   If None, returns common drug-like properties
                   Examples: ["MolecularWeight", "XLogP", "TPSA", "HBondDonorCount"]

    Returns:
        dict: Molecular properties

        Common properties:
        - MolecularWeight: Molecular weight (Da)
        - XLogP: Lipophilicity (partition coefficient)
        - TPSA: Topological polar surface area (Ų)
        - HBondDonorCount: Hydrogen bond donors
        - HBondAcceptorCount: Hydrogen bond acceptors
        - RotatableBondCount: Rotatable bonds
        - Complexity: Structural complexity score

    Examples:
        # Get all properties for aspirin
        props = get_compound_properties(cid="2244")

        # Extract drug-likeness properties
        mw = props.get('MolecularWeight')
        logp = props.get('XLogP')
        tpsa = props.get('TPSA')
        hbd = props.get('HBondDonorCount')
        hba = props.get('HBondAcceptorCount')

        print(f"MW: {mw} Da")
        print(f"LogP: {logp}")
        print(f"TPSA: {tpsa} Ų")
        print(f"H-bond donors: {hbd}")
        print(f"H-bond acceptors: {hba}")

        # Check Lipinski's Rule of 5
        lipinski_pass = (
            mw <= 500 and
            logp <= 5 and
            hbd <= 5 and
            hba <= 10
        )
        print(f"Lipinski compliant: {lipinski_pass}")

        # Get specific properties
        props = get_compound_properties(
            cid="2244",
            properties=["MolecularWeight", "XLogP", "TPSA"]
        )
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'get_compound_properties',
        'cid': str(cid)
    }

    if properties:
        params['properties'] = properties

    return client.call_tool('pubchem', params)


def search_similar_compounds(
    smiles: str,
    threshold: int = 90,
    max_records: int = 100
) -> Dict[str, Any]:
    """
    Find structurally similar compounds (Tanimoto similarity)

    Args:
        smiles: SMILES notation of query molecule

        threshold: Tanimoto similarity threshold (0-100, default: 90)
                  90-100: Very similar
                  70-90: Similar
                  50-70: Moderately similar

        max_records: Maximum results (1-10000, default: 100)

    Returns:
        dict: Similar compounds with similarity scores

    Examples:
        # Find very similar compounds
        results = search_similar_compounds(
            smiles="CC(=O)Oc1ccccc1C(=O)O",
            threshold=90,
            max_records=50
        )

        # Analyze similarity distribution
        similarities = []
        for compound in results.get('data', []):
            cid = compound.get('CID')
            score = compound.get('TanimotoSimilarity')
            similarities.append((cid, score))

        similarities.sort(key=lambda x: x[1], reverse=True)
        print(f"Top 10 most similar:")
        for cid, score in similarities[:10]:
            print(f"  CID {cid}: {score:.2f}% similar")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'search_similar_compounds',
        'smiles': smiles,
        'threshold': threshold,
        'max_records': max_records
    }

    return client.call_tool('pubchem', params)


def get_3d_conformers(
    cid: Union[str, int],
    conformer_type: str = "3d"
) -> Dict[str, Any]:
    """
    Get 3D conformer data for a compound

    Args:
        cid: PubChem Compound ID

        conformer_type: Type of conformer (default: "3d")
                       Values: "3d", "2d"

    Returns:
        dict: 3D structural conformer data

    Examples:
        # Get 3D conformers
        conformers = get_3d_conformers(cid="2244")

        # Extract coordinates
        coords_3d = conformers.get('Conformers', [])
        print(f"Found {len(coords_3d)} 3D conformers")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'get_3d_conformers',
        'cid': str(cid),
        'conformer_type': conformer_type
    }

    return client.call_tool('pubchem', params)


def analyze_stereochemistry(
    cid: Union[str, int]
) -> Dict[str, Any]:
    """
    Analyze stereochemistry and chirality of a compound

    Args:
        cid: PubChem Compound ID

    Returns:
        dict: Stereochemistry analysis

        Key fields:
        - StereocentersCount: Number of stereocenters
        - DefinedStereocenters: Defined chiral centers
        - UndefinedStereocenters: Undefined chiral centers

    Examples:
        # Analyze chirality
        stereo = analyze_stereochemistry(cid="2244")

        stereocenters = stereo.get('StereocentersCount')
        defined = stereo.get('DefinedStereocenters')
        undefined = stereo.get('UndefinedStereocenters')

        print(f"Stereocenters: {stereocenters}")
        print(f"Defined: {defined}")
        print(f"Undefined: {undefined}")
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'analyze_stereochemistry',
        'cid': str(cid)
    }

    return client.call_tool('pubchem', params)


def get_safety_data(
    cid: Union[str, int]
) -> Dict[str, Any]:
    """
    🔴 CRITICAL WARNING: This method is UNUSABLE

    Returns 21.9 MILLION tokens - 876x over MCP limit (25k)
    Query will ALWAYS FAIL - DO NOT USE

    Issue: Method has no parameters to limit response size or select fields.
    Returns entire safety database for compound.

    Status: Broken - waiting for MCP server fix to add field selection

    Token Usage: 21,900,000 tokens 🔴 (EXCEEDS LIMIT)

    DO NOT USE THIS METHOD until it is fixed by the MCP server maintainer.

    ----

    Get safety and hazard information for a compound

    Args:
        cid: PubChem Compound ID

    Returns:
        dict: Safety and GHS classification data

        Key fields:
        - GHSClassification: GHS hazard classes
        - Hazards: Safety hazards
        - Precautions: Safety precautions

    Examples:
        # 🔴 DO NOT USE - Will fail with token limit
        # safety = get_safety_data(cid="2244")
        pass
    """
    client = get_client('pubchem-mcp-server')

    params = {
        'method': 'get_safety_data',
        'cid': str(cid)
    }

    return client.call_tool('pubchem', params)


__all__ = [
    'search_compounds',
    'get_compound_info',
    'search_by_smiles',
    'get_compound_synonyms',
    'get_compound_properties',
    'search_similar_compounds',
    'get_3d_conformers',
    'analyze_stereochemistry',
    'get_safety_data'
]
