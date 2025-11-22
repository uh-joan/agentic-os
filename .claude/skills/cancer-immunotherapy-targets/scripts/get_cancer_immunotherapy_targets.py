import sys
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_targets

def get_cancer_immunotherapy_targets():
    """Find validated targets for cancer immunotherapy beyond PD-1/PD-L1.
    
    Returns:
        dict: Contains total_count, targets summary, and detailed data
    """
    
    # Search for immunotherapy-related targets in cancer
    immunotherapy_terms = [
        "immune checkpoint",
        "T cell activation", 
        "immunotherapy",
        "cytotoxic T lymphocyte",
        "natural killer cell",
        "tumor immunology"
    ]
    
    all_targets = []
    target_ids_seen = set()
    
    print("Searching Open Targets for cancer immunotherapy targets...")
    
    for term in immunotherapy_terms:
        print(f"\nQuerying: {term}")
        try:
            result = search_targets(query=term, size=50)
            
            if result and 'data' in result:
                targets = result['data'].get('search', {}).get('targets', [])
                
                for target in targets:
                    target_id = target.get('id', '')
                    
                    # Skip PD-1 (PDCD1) and PD-L1 (CD274)
                    if target_id in ['ENSG00000188389', 'ENSG00000120217']:
                        continue
                    
                    if target_id in target_ids_seen:
                        continue
                    
                    target_ids_seen.add(target_id)
                    
                    approved_symbol = target.get('approvedSymbol', 'N/A')
                    approved_name = target.get('approvedName', 'N/A')
                    
                    tractability = target.get('tractability', {})
                    antibody_tractable = tractability.get('antibody', {}).get('topCategory', 'Unknown')
                    small_molecule_tractable = tractability.get('smallMolecule', {}).get('topCategory', 'Unknown')
                    
                    diseases = []
                    if 'associatedDiseases' in target:
                        disease_data = target['associatedDiseases'].get('rows', [])
                        cancer_diseases = [
                            d.get('disease', {}).get('name', '') 
                            for d in disease_data[:5]
                            if 'cancer' in d.get('disease', {}).get('name', '').lower() or
                               'carcinoma' in d.get('disease', {}).get('name', '').lower() or
                               'tumor' in d.get('disease', {}).get('name', '').lower()
                        ]
                        diseases = cancer_diseases[:3]
                    
                    safety = target.get('safety', {})
                    clinical_precedence = 'Yes' if safety.get('adverseEffects', []) else 'Limited'
                    
                    target_info = {
                        'id': target_id,
                        'symbol': approved_symbol,
                        'name': approved_name,
                        'antibody_tractability': antibody_tractable,
                        'small_molecule_tractability': small_molecule_tractable,
                        'cancer_indications': diseases if diseases else ['Not specified'],
                        'clinical_precedence': clinical_precedence,
                        'search_term': term
                    }
                    
                    all_targets.append(target_info)
                    
                print(f"  Found {len(targets)} targets for '{term}'")
                
        except Exception as e:
            print(f"  Error querying '{term}': {str(e)}")
            continue
    
    unique_targets = {t['id']: t for t in all_targets}.values()
    
    sorted_targets = sorted(
        unique_targets,
        key=lambda x: (
            x['clinical_precedence'] == 'Yes',
            'Clinical' in x['antibody_tractability'],
            len(x['cancer_indications'])
        ),
        reverse=True
    )
    
    total_targets = len(sorted_targets)
    
    antibody_tractable = sum(1 for t in sorted_targets 
                             if 'Clinical' in t['antibody_tractability'])
    small_mol_tractable = sum(1 for t in sorted_targets 
                              if 'Clinical' in t['small_molecule_tractability'])
    clinical_precedence_count = sum(1 for t in sorted_targets 
                                    if t['clinical_precedence'] == 'Yes')
    
    summary_lines = [
        f"\n{'='*80}",
        f"CANCER IMMUNOTHERAPY TARGETS (Beyond PD-1/PD-L1)",
        f"{'='*80}",
        f"\nTotal validated targets found: {total_targets}",
        f"Antibody tractable (Clinical Precedence): {antibody_tractable}",
        f"Small molecule tractable (Clinical Precedence): {small_mol_tractable}",
        f"Targets with clinical precedence: {clinical_precedence_count}",
        f"\n{'='*80}",
        f"\nTOP 15 PRIORITY TARGETS:",
        f"{'='*80}\n"
    ]
    
    for idx, target in enumerate(sorted_targets[:15], 1):
        summary_lines.extend([
            f"\n{idx}. {target['symbol']} ({target['id']})",
            f"   Name: {target['name']}",
            f"   Antibody Tractability: {target['antibody_tractability']}",
            f"   Small Molecule Tractability: {target['small_molecule_tractability']}",
            f"   Clinical Precedence: {target['clinical_precedence']}",
            f"   Cancer Indications: {', '.join(target['cancer_indications'][:3])}",
            f"   Identified via: {target['search_term']}"
        ])
    
    summary = '\n'.join(summary_lines)
    
    return {
        'total_count': total_targets,
        'targets': sorted_targets,
        'summary': summary,
        'statistics': {
            'total_targets': total_targets,
            'antibody_tractable': antibody_tractable,
            'small_molecule_tractable': small_mol_tractable,
            'clinical_precedence': clinical_precedence_count
        }
    }

if __name__ == "__main__":
    result = get_cancer_immunotherapy_targets()
    print(result['summary'])
    print(f"\n\nTotal targets available for detailed analysis: {result['total_count']}")
