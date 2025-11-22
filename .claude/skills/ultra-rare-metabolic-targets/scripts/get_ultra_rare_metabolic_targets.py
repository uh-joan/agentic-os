import sys
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_diseases, get_disease_info, get_disease_targets, get_target_tractability

def get_ultra_rare_metabolic_targets(max_population=500):
    """Get genetic targets for ultra-rare metabolic diseases with small patient populations.
    
    Args:
        max_population (int): Maximum patient population size (default: 500)
    
    Returns:
        dict: Contains total diseases analyzed, targets found, and detailed results
    """
    print(f"Searching for ultra-rare metabolic diseases (population <{max_population})...")
    
    metabolic_terms = [
        "metabolic disorder",
        "inborn error of metabolism", 
        "lysosomal storage disease",
        "mitochondrial disease",
        "peroxisomal disorder"
    ]
    
    rare_diseases = []
    
    for term in metabolic_terms:
        try:
            result = search_diseases(term, page_size=100)
            diseases = result.get('diseases', [])
            
            for disease in diseases:
                disease_id = disease.get('id')
                disease_name = disease.get('name')
                
                try:
                    info = get_disease_info(disease_id)
                    db_xrefs = info.get('dbXrefs', [])
                    
                    has_omim = any('OMIM' in xref for xref in db_xrefs)
                    has_orphanet = any('Orphanet' in xref or 'ORPHA' in xref for xref in db_xrefs)
                    
                    name_lower = disease_name.lower()
                    ultra_rare_keywords = [
                        'deficiency', 'syndrome', 'atrophy', 'dystrophy',
                        'lysosomal', 'mitochondrial', 'peroxisomal',
                        'type i', 'type ii', 'type iii'
                    ]
                    
                    has_rare_keywords = any(keyword in name_lower for keyword in ultra_rare_keywords)
                    
                    if (has_omim or has_orphanet) and has_rare_keywords:
                        rare_diseases.append({
                            'id': disease_id,
                            'name': disease_name,
                            'omim': [x for x in db_xrefs if 'OMIM' in x],
                            'orphanet': [x for x in db_xrefs if 'Orphanet' in x or 'ORPHA' in x]
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error searching {term}: {e}")
            continue
    
    print(f"\nFound {len(rare_diseases)} ultra-rare metabolic diseases")
    
    all_targets = {}
    
    for disease in rare_diseases[:20]:
        disease_id = disease['id']
        disease_name = disease['name']
        
        try:
            targets_result = get_disease_targets(disease_id, page_size=50)
            associations = targets_result.get('associations', [])
            
            for assoc in associations:
                target = assoc.get('target', {})
                target_id = target.get('id')
                target_symbol = target.get('approvedSymbol')
                association_score = assoc.get('score', 0)
                
                if association_score < 0.5:
                    continue
                
                try:
                    tractability = get_target_tractability(target_id)
                    sm_tractability = tractability.get('smallMolecule', {}).get('topCategory', 'Unknown')
                    ab_tractability = tractability.get('antibody', {}).get('topCategory', 'Unknown')
                except:
                    sm_tractability = 'Unknown'
                    ab_tractability = 'Unknown'
                
                if target_symbol not in all_targets:
                    all_targets[target_symbol] = {
                        'target_id': target_id,
                        'symbol': target_symbol,
                        'name': target.get('approvedName', ''),
                        'diseases': [],
                        'max_score': association_score,
                        'sm_tractability': sm_tractability,
                        'ab_tractability': ab_tractability,
                        'disease_count': 0
                    }
                
                all_targets[target_symbol]['diseases'].append({
                    'name': disease_name,
                    'id': disease_id,
                    'score': association_score,
                    'omim': disease.get('omim', []),
                    'orphanet': disease.get('orphanet', [])
                })
                
                all_targets[target_symbol]['disease_count'] += 1
                all_targets[target_symbol]['max_score'] = max(
                    all_targets[target_symbol]['max_score'],
                    association_score
                )
                
        except Exception as e:
            print(f"Error getting targets for {disease_name}: {e}")
            continue
    
    sorted_targets = sorted(
        all_targets.values(),
        key=lambda x: (x['disease_count'], x['max_score']),
        reverse=True
    )
    
    summary = {
        'total_diseases_analyzed': len(rare_diseases),
        'total_unique_targets': len(all_targets),
        'high_priority_targets': len([t for t in sorted_targets if t['disease_count'] >= 3]),
        'druggable_targets': len([t for t in sorted_targets if 'Clinical' in t['sm_tractability']]),
        'top_targets': []
    }
    
    print(f"\n{'='*80}")
    print(f"GENETIC TARGETS FOR ULTRA-RARE METABOLIC DISEASES")
    print(f"{'='*80}")
    print(f"\nTotal diseases analyzed: {summary['total_diseases_analyzed']}")
    print(f"Total unique genetic targets: {summary['total_unique_targets']}")
    print(f"High-priority targets (3+ diseases): {summary['high_priority_targets']}")
    print(f"Clinically tractable targets: {summary['druggable_targets']}")
    
    print(f"\n{'='*80}")
    print(f"TOP 15 GENETIC TARGETS (by disease count and association score)")
    print(f"{'='*80}\n")
    
    for i, target in enumerate(sorted_targets[:15], 1):
        print(f"{i}. {target['symbol']} ({target['target_id']})")
        print(f"   Name: {target['name']}")
        print(f"   Associated diseases: {target['disease_count']}")
        print(f"   Max association score: {target['max_score']:.3f}")
        print(f"   Small molecule tractability: {target['sm_tractability']}")
        print(f"   Antibody tractability: {target['ab_tractability']}")
        print(f"   Diseases:")
        
        for disease in target['diseases'][:3]:
            omim_str = ', '.join(disease['omim']) if disease['omim'] else 'N/A'
            print(f"      - {disease['name']} (Score: {disease['score']:.3f})")
            print(f"        OMIM: {omim_str}")
        
        if len(target['diseases']) > 3:
            print(f"      ... and {len(target['diseases']) - 3} more diseases")
        print()
        
        summary['top_targets'].append({
            'symbol': target['symbol'],
            'target_id': target['target_id'],
            'disease_count': target['disease_count'],
            'max_score': target['max_score'],
            'sm_tractability': target['sm_tractability']
        })
    
    return {
        'summary': summary,
        'all_targets': sorted_targets,
        'rare_diseases': rare_diseases
    }

if __name__ == "__main__":
    result = get_ultra_rare_metabolic_targets(max_population=500)
    print(f"\n{'='*80}")
    print(f"Analysis complete. Found {result['summary']['total_unique_targets']} genetic targets.")
    print(f"{'='*80}")
