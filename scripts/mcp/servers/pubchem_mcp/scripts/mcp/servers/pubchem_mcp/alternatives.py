"""PubChem MCP Alternative Methods

Provides working alternatives for broken PubChem MCP methods.
These bypass the MCP and call PubChem REST API directly with proper field selection.

USE THESE INSTEAD OF:
- get_safety_data (broken - returns 21.9M tokens)
- search_similar_compounds (broken - returns 400 error)
"""

import requests
from typing import Dict, Any, List, Optional


def get_safety_data_alternative(
    cid: str,
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get GHS safety data for a compound using PubChem REST API directly.

    This is a working alternative to the broken get_safety_data MCP method.

    Args:
        cid: PubChem Compound ID
        fields: Optional list of sections to return
                Default: ['GHS Classification', 'Hazards', 'Precautions']

    Returns:
        dict with safety information (manageable size)

    Token Usage: ~500-2000 tokens (vs 21.9M from broken method)

    Examples:
        # Get all safety sections
        safety = get_safety_data_alternative(cid="2244")

        # Get specific sections only
        safety = get_safety_data_alternative(
            cid="2244",
            fields=['GHS Classification', 'Hazards']
        )
    """

    if fields is None:
        fields = ['GHS Classification', 'Hazards', 'Precautions']

    # Use PubChem REST API with section filtering
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract only safety-related sections
        result = {
            'cid': cid,
            'sections': []
        }

        if 'Record' in data:
            sections = data['Record'].get('Section', [])

            # Recursively search for safety sections
            def find_sections(sections_list, target_headings):
                found = []
                for section in sections_list:
                    heading = section.get('TOCHeading', '')
                    if any(target in heading for target in target_headings):
                        found.append({
                            'heading': heading,
                            'information': section.get('Information', [])
                        })
                    # Recurse into subsections
                    if 'Section' in section:
                        found.extend(find_sections(section['Section'], target_headings))
                return found

            result['sections'] = find_sections(sections, fields)

        result['token_estimate'] = len(str(result)) // 4  # Rough estimate
        result['source'] = 'PubChem REST API (direct)'

        return result

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'cid': cid,
            'message': 'Failed to fetch safety data from PubChem API'
        }


def search_similar_compounds_alternative(
    smiles: str,
    threshold: int = 90,
    max_records: int = 10
) -> Dict[str, Any]:
    """
    Search for similar compounds using PubChem REST API directly.

    This is a working alternative to the broken search_similar_compounds MCP method.

    Args:
        smiles: SMILES string of query molecule
        threshold: Tanimoto similarity threshold (0-100)
        max_records: Maximum compounds to return

    Returns:
        dict with similar compounds and similarity scores

    Token Usage: ~100-500 tokens per compound

    Examples:
        # Search for compounds similar to aspirin
        results = search_similar_compounds_alternative(
            smiles="CC(=O)Oc1ccccc1C(=O)O",
            threshold=90,
            max_records=10
        )
    """

    import urllib.parse

    # URL encode SMILES
    encoded_smiles = urllib.parse.quote(smiles)

    # Use PubChem FastSimilarity API
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastsimilarity_2d/smiles/{encoded_smiles}/cids/JSON"

    params = {
        'Threshold': threshold,
        'MaxRecords': max_records
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        cids = data.get('IdentifierList', {}).get('CID', [])

        # Get basic info for each CID
        results = []
        for cid in cids[:max_records]:
            try:
                info_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
                info_response = requests.get(info_url, timeout=10)
                info_response.raise_for_status()
                info_data = info_response.json()

                if 'PropertyTable' in info_data:
                    props = info_data['PropertyTable']['Properties'][0]
                    results.append({
                        'CID': cid,
                        'MolecularFormula': props.get('MolecularFormula'),
                        'MolecularWeight': props.get('MolecularWeight'),
                        'IUPACName': props.get('IUPACName')
                    })
            except:
                results.append({'CID': cid})

        return {
            'query_smiles': smiles,
            'threshold': threshold,
            'total_found': len(cids),
            'returned': len(results),
            'compounds': results,
            'source': 'PubChem REST API (direct)',
            'token_estimate': len(str(results)) // 4
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'query_smiles': smiles,
            'message': 'Failed to search similar compounds via PubChem API'
        }


def get_ghs_classification_summary(cid: str) -> Dict[str, Any]:
    """
    Get a minimal GHS classification summary (< 500 tokens).

    Ultra-efficient alternative when you only need GHS codes.

    Args:
        cid: PubChem Compound ID

    Returns:
        dict with just GHS codes and basic hazards

    Token Usage: ~200-500 tokens

    Example:
        # Just get GHS classification
        ghs = get_ghs_classification_summary(cid="2244")
        print(ghs['ghs_codes'])  # ['H302', 'H318', etc.]
    """

    safety_data = get_safety_data_alternative(cid, fields=['GHS Classification'])

    # Extract just the codes
    ghs_codes = []
    for section in safety_data.get('sections', []):
        for info in section.get('information', []):
            value = info.get('Value', {})
            if 'StringWithMarkup' in value:
                text = value['StringWithMarkup'][0].get('String', '')
                # Extract H-codes (e.g., H302, H318)
                import re
                codes = re.findall(r'H\d+', text)
                ghs_codes.extend(codes)

    return {
        'cid': cid,
        'ghs_codes': list(set(ghs_codes)),  # Unique codes
        'hazard_count': len(set(ghs_codes)),
        'source': 'PubChem REST API (minimal)',
        'token_estimate': len(str(ghs_codes)) // 4
    }


# Export all alternative functions
__all__ = [
    'get_safety_data_alternative',
    'search_similar_compounds_alternative',
    'get_ghs_classification_summary'
]
