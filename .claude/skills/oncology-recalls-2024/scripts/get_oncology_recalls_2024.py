import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_enforcement_reports
import json
from datetime import datetime

def get_oncology_recalls_2024():
    """Get oncology drug recalls from 2024 with detailed information.
    
    Returns:
        dict: Contains total count, recalls data, and summary by classification
    """
    all_recalls = []
    skip = 0
    limit = 100
    
    print("Searching FDA enforcement reports for oncology drug recalls in 2024...")
    
    while True:
        # Search for drug recalls in 2024 related to oncology/cancer
        result = search_enforcement_reports(
            search='product_description:(cancer OR oncology OR chemotherapy OR tumor OR leukemia OR lymphoma) AND recall_initiation_date:[20240101 TO 20241231] AND product_type:"Drugs"',
            limit=limit,
            skip=skip
        )
        
        if not result or 'results' not in result or not result['results']:
            break
            
        all_recalls.extend(result['results'])
        
        # Check if we have more results
        if len(result['results']) < limit:
            break
            
        skip += limit
        print(f"Retrieved {len(all_recalls)} recalls so far...")
    
    # Process and categorize recalls
    classification_summary = {}
    recall_details = []
    
    for recall in all_recalls:
        classification = recall.get('classification', 'Unknown')
        classification_summary[classification] = classification_summary.get(classification, 0) + 1
        
        detail = {
            'recall_number': recall.get('recall_number', 'N/A'),
            'product_description': recall.get('product_description', 'N/A'),
            'reason_for_recall': recall.get('reason_for_recall', 'N/A'),
            'classification': classification,
            'recalling_firm': recall.get('recalling_firm', 'N/A'),
            'recall_initiation_date': recall.get('recall_initiation_date', 'N/A'),
            'status': recall.get('status', 'N/A'),
            'distribution_pattern': recall.get('distribution_pattern', 'N/A')
        }
        recall_details.append(detail)
    
    # Sort by recall initiation date (most recent first)
    recall_details.sort(key=lambda x: x['recall_initiation_date'], reverse=True)
    
    # Generate summary
    summary = f"""
ONCOLOGY DRUG RECALLS - 2024
============================

Total Recalls: {len(all_recalls)}

By Classification:
"""
    
    for classification in sorted(classification_summary.keys()):
        summary += f"  Class {classification}: {classification_summary[classification]} recalls\n"
    
    summary += "\nRecent Recalls:\n"
    summary += "-" * 80 + "\n"
    
    for i, recall in enumerate(recall_details[:10], 1):
        summary += f"\n{i}. {recall['product_description']}\n"
        summary += f"   Recall #: {recall['recall_number']}\n"
        summary += f"   Date: {recall['recall_initiation_date']}\n"
        summary += f"   Reason: {recall['reason_for_recall']}\n"
        summary += f"   Classification: Class {recall['classification']}\n"
        summary += f"   Firm: {recall['recalling_firm']}\n"
        summary += f"   Status: {recall['status']}\n"
        summary += "-" * 80 + "\n"
    
    if len(recall_details) > 10:
        summary += f"\n... and {len(recall_details) - 10} more recalls\n"
    
    return {
        'total_count': len(all_recalls),
        'classification_summary': classification_summary,
        'recall_details': recall_details,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_oncology_recalls_2024()
    print(result['summary'])
    print(f"\nFull data contains {result['total_count']} recalls with detailed information")
