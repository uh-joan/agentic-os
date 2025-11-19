"""
Query FDA for GLP-1 receptor agonist drugs approved for Type 2 Diabetes.

This skill demonstrates:
- FDA MCP server integration
- JSON response parsing using .get() methods
- Extracting OpenFDA metadata (brand names, generic names, manufacturers)
- Handling nested dictionaries and list fields
"""

import sys
import json
from pathlib import Path

# Add scripts/mcp to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "mcp"))

from mcp.servers.fda_mcp import mcp__fda_mcp__fda_info


def get_glp1_diabetes_drugs():
    """
    Query FDA for GLP-1 receptor agonist drugs approved for Type 2 Diabetes.

    Returns:
        dict: Contains:
            - count (int): Number of drugs found
            - drugs (list): List of dicts with drug information:
                - brand_names (list): Brand names
                - generic_names (list): Generic names
                - manufacturer (list): Manufacturer names
                - indications (list): Indications and usage
                - approval_date (list): Approval dates

    Example:
        >>> results = get_glp1_diabetes_drugs()
        >>> print(f"Found {results['count']} GLP-1 drugs")
        >>> for drug in results['drugs']:
        ...     print(drug['brand_names'][0])
    """
    # Query FDA for GLP-1 drugs with diabetes indication
    result = mcp__fda_mcp__fda_info(
        search_term="GLP-1 receptor agonist",
        indication="diabetes"
    )

    # Parse JSON response
    if isinstance(result, str):
        data = json.loads(result)
    else:
        data = result

    # Extract drug information
    drugs = []
    if data.get("results"):
        for item in data["results"]:
            openfda = item.get("openfda", {})
            drug_info = {
                "brand_names": openfda.get("brand_name", []),
                "generic_names": openfda.get("generic_name", []),
                "manufacturer": openfda.get("manufacturer_name", []),
                "indications": item.get("indications_and_usage", ["Not specified"]),
                "approval_date": openfda.get("approval_date", ["Unknown"])
            }
            drugs.append(drug_info)

    return {
        "count": len(drugs),
        "drugs": drugs
    }


if __name__ == "__main__":
    # Example usage
    results = get_glp1_diabetes_drugs()

    print(f"\n{'='*60}")
    print(f"FDA-APPROVED GLP-1 RECEPTOR AGONISTS FOR TYPE 2 DIABETES")
    print(f"{'='*60}\n")

    print(f"Total drugs found: {results['count']}\n")

    for idx, drug in enumerate(results['drugs'], 1):
        print(f"{idx}. Brand Name(s): {', '.join(drug['brand_names'][:3]) if drug['brand_names'] else 'N/A'}")
        print(f"   Generic Name(s): {', '.join(drug['generic_names'][:3]) if drug['generic_names'] else 'N/A'}")
        print(f"   Manufacturer: {', '.join(drug['manufacturer'][:2]) if drug['manufacturer'] else 'N/A'}")
        print(f"   Approval Date: {drug['approval_date'][0] if drug['approval_date'] else 'Unknown'}")
        print()

    print(f"{'='*60}\n")
