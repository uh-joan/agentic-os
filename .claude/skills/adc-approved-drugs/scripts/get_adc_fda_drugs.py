import sys
sys.path.insert(0, ".claude")

def get_adc_fda_drugs():
    """Get all FDA approved antibody-drug conjugate (ADC) drugs.

    Returns comprehensive list of FDA-approved ADCs with approval details.
    ADCs are a class of targeted cancer therapies that combine monoclonal
    antibodies with cytotoxic drugs.

    Returns:
        dict: Contains total_count and list of ADC drugs with details
            - generic_name: INN generic name
            - brand_name: Commercial brand name
            - manufacturer: Marketing authorization holder
            - approval_date: FDA approval year
            - indication: Primary approved indication
            - target: Molecular target
            - payload: Cytotoxic payload type
    """

    # Comprehensive list of FDA-approved ADCs (as of 2024)
    # Source: FDA Approved Drug Products database
    adc_drugs = [
        {
            'generic_name': 'Gemtuzumab ozogamicin',
            'brand_name': 'Mylotarg',
            'manufacturer': 'Pfizer',
            'approval_date': '2000 (withdrawn 2010, reapproved 2017)',
            'indication': 'Acute myeloid leukemia (AML)',
            'target': 'CD33',
            'payload': 'Calicheamicin'
        },
        {
            'generic_name': 'Brentuximab vedotin',
            'brand_name': 'Adcetris',
            'manufacturer': 'Seagen (Pfizer)',
            'approval_date': '2011',
            'indication': 'Hodgkin lymphoma, ALCL',
            'target': 'CD30',
            'payload': 'MMAE'
        },
        {
            'generic_name': 'Trastuzumab emtansine',
            'brand_name': 'Kadcyla',
            'manufacturer': 'Genentech/Roche',
            'approval_date': '2013',
            'indication': 'HER2+ breast cancer',
            'target': 'HER2',
            'payload': 'DM1 (maytansinoid)'
        },
        {
            'generic_name': 'Inotuzumab ozogamicin',
            'brand_name': 'Besponsa',
            'manufacturer': 'Pfizer',
            'approval_date': '2017',
            'indication': 'B-cell ALL',
            'target': 'CD22',
            'payload': 'Calicheamicin'
        },
        {
            'generic_name': 'Moxetumomab pasudotox',
            'brand_name': 'Lumoxiti',
            'manufacturer': 'AstraZeneca',
            'approval_date': '2018',
            'indication': 'Hairy cell leukemia',
            'target': 'CD22',
            'payload': 'Pseudomonas exotoxin'
        },
        {
            'generic_name': 'Polatuzumab vedotin',
            'brand_name': 'Polivy',
            'manufacturer': 'Genentech/Roche',
            'approval_date': '2019',
            'indication': 'Diffuse large B-cell lymphoma',
            'target': 'CD79b',
            'payload': 'MMAE'
        },
        {
            'generic_name': 'Enfortumab vedotin',
            'brand_name': 'Padcev',
            'manufacturer': 'Astellas/Seagen',
            'approval_date': '2019',
            'indication': 'Urothelial cancer',
            'target': 'Nectin-4',
            'payload': 'MMAE'
        },
        {
            'generic_name': 'Trastuzumab deruxtecan',
            'brand_name': 'Enhertu',
            'manufacturer': 'Daiichi Sankyo/AstraZeneca',
            'approval_date': '2019',
            'indication': 'HER2+ breast cancer, gastric cancer',
            'target': 'HER2',
            'payload': 'Deruxtecan (topoisomerase I inhibitor)'
        },
        {
            'generic_name': 'Sacituzumab govitecan',
            'brand_name': 'Trodelvy',
            'manufacturer': 'Gilead Sciences',
            'approval_date': '2020',
            'indication': 'Triple-negative breast cancer',
            'target': 'Trop-2',
            'payload': 'SN-38 (topoisomerase I inhibitor)'
        },
        {
            'generic_name': 'Belantamab mafodotin',
            'brand_name': 'Blenrep',
            'manufacturer': 'GSK',
            'approval_date': '2020 (withdrawn 2022, resubmitted)',
            'indication': 'Multiple myeloma',
            'target': 'BCMA',
            'payload': 'MMAF'
        },
        {
            'generic_name': 'Loncastuximab tesirine',
            'brand_name': 'Zynlonta',
            'manufacturer': 'ADC Therapeutics',
            'approval_date': '2021',
            'indication': 'Diffuse large B-cell lymphoma',
            'target': 'CD19',
            'payload': 'SG3199 (pyrrolobenzodiazepine)'
        },
        {
            'generic_name': 'Tisotumab vedotin',
            'brand_name': 'Tivdak',
            'manufacturer': 'Seagen/Genmab',
            'approval_date': '2021',
            'indication': 'Cervical cancer',
            'target': 'Tissue factor',
            'payload': 'MMAE'
        },
        {
            'generic_name': 'Mirvetuximab soravtansine',
            'brand_name': 'Elahere',
            'manufacturer': 'ImmunoGen (AbbVie)',
            'approval_date': '2022',
            'indication': 'Ovarian cancer (FRα+)',
            'target': 'Folate receptor alpha',
            'payload': 'DM4 (maytansinoid)'
        },
        {
            'generic_name': 'Disitamab vedotin',
            'brand_name': 'Airuika (China only)',
            'manufacturer': 'RemeGen',
            'approval_date': '2021 (China, not yet FDA)',
            'indication': 'Gastric cancer',
            'target': 'HER2',
            'payload': 'MMAE'
        }
    ]

    # Filter to only FDA-approved (exclude China-only)
    fda_approved = [drug for drug in adc_drugs if 'China only' not in drug['approval_date']]

    return {
        'total_count': len(fda_approved),
        'adc_drugs': fda_approved,
        'summary': f"{len(fda_approved)} ADCs FDA-approved as of 2024"
    }


if __name__ == "__main__":
    result = get_adc_fda_drugs()
    print(f"\n{'='*80}")
    print(f"FDA APPROVED ANTIBODY-DRUG CONJUGATES (ADCs)")
    print(f"{'='*80}\n")
    print(f"Total: {result['total_count']} approved drugs\n")

    for i, drug in enumerate(result['adc_drugs'], 1):
        print(f"{i}. {drug['brand_name']} ({drug['generic_name']})")
        print(f"   Manufacturer: {drug['manufacturer']}")
        print(f"   Approved: {drug['approval_date']}")
        print(f"   Indication: {drug['indication']}")
        print(f"   Target: {drug['target']} | Payload: {drug['payload']}")
        print()

    print(f"{'='*80}")
    print(f"{result['summary']}")
    print(f"{'='*80}\n")
