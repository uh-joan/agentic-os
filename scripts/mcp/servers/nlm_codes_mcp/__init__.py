"""NLM Clinical Codes MCP Server - Python API

Provides Python functions for NLM Clinical Tables API medical coding and provider data.
Data stays in execution environment - only summaries flow to model.

CRITICAL NLM CLINICAL TABLES QUIRKS:
1. Unified tool: Single tool (nlm_ct_codes) with method parameter for all searches
2. Pagination: maxList (total results, 1-500) vs count (page size for pagination)
3. Offset: 0-based pagination offset (use with count parameter)
4. Field selection: searchFields, displayFields, extraFields for custom queries
5. additionalQuery: Elasticsearch syntax for advanced filtering (supports parentheses)
6. Boolean optimization: Complex parentheses expressions auto-optimized
7. Response format: Nested arrays [totalCount, ?, ?, results[]]
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, Union


def search_icd_10_cm(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search ICD-10-CM diagnosis codes

    ICD-10-CM is the U.S. clinical modification of the International Classification
    of Diseases, 10th Revision. Contains 70,000+ diagnosis codes.

    Args:
        terms: Search query string
              Examples: "hypertension", "diabetes", "S72" (femur fractures)

              Common searches:
              - Disease names: "pneumonia", "obesity", "cancer"
              - Code patterns: "E11" (diabetes codes), "I10" (hypertension)
              - Anatomical: "femur fracture", "lung disease"

        maxList: Maximum total results to return (1-500, default: 7)
                Different from count (page size)

        searchFields: Fields to search in (comma-separated)
                     Default: "code,name"
                     Options: "code", "name", or "code,name"

        displayFields: Fields to display in results
                      Default: "code,name"

        extraFields: Additional fields to include in response

        additionalQuery: Elasticsearch query for advanced filtering
                        Examples:
                        - Simple: None (search terms only)
                        - Code pattern: Use terms parameter instead

        offset: Starting result number for pagination (0-based, default: 0)

        count: Page size for pagination (1-500, default: 7)
              Use with offset for large result sets

    Returns:
        dict: ICD-10-CM search results

        Response structure:
        {
            "method": "icd-10-cm",
            "totalCount": 2466,
            "results": [
                {
                    "code": "S72.001A",
                    "name": "Fracture of unspecified part of neck of right femur, initial encounter"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for hypertension codes
        results = search_icd_10_cm(terms="hypertension", maxList=20)

        # Extract codes
        for item in results.get('results', []):
            code = item.get('code')
            name = item.get('name')
            print(f"{code}: {name}")

        # Example 2: Search femur fracture codes (S72)
        results = search_icd_10_cm(
            terms="S72",
            maxList=50
        )

        total = results.get('totalCount')
        print(f"Found {total} S72 codes")

        # Example 3: Paginated search for diabetes codes
        # First page
        page1 = search_icd_10_cm(
            terms="E11",
            count=20,
            offset=0
        )

        # Second page
        page2 = search_icd_10_cm(
            terms="E11",
            count=20,
            offset=20
        )

        # Example 4: Search in code field only
        results = search_icd_10_cm(
            terms="I10",
            searchFields="code",
            maxList=10
        )

        # Example 5: Get specific fields
        results = search_icd_10_cm(
            terms="diabetes",
            displayFields="code,name",
            maxList=15
        )
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'icd-10-cm',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_icd_11(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search ICD-11 codes (WHO International Classification of Diseases 2023)

    ICD-11 is the WHO's latest classification system with improved clinical detail
    and digital compatibility.

    Args:
        terms: Search query string
              Examples: "heart", "blood", "pneumonia", "1B12.0", "QB25"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search (default varies by method)

        displayFields: Fields to display

        extraFields: Additional fields

        additionalQuery: Advanced filtering
                        Examples:
                        - "type:stem" - Stem codes only
                        - "type:extension" - Extension codes only
                        - "chapter:1" - Specific chapter

        offset: Pagination offset (0-based, default: 0)

        count: Page size (1-500, default: 7)

    Returns:
        dict: ICD-11 search results

    Examples:
        # Search for heart conditions
        results = search_icd_11(terms="heart", maxList=15)

        # Filter for stem codes only
        results = search_icd_11(
            terms="pneumonia",
            additionalQuery="type:stem",
            maxList=20
        )

        # Search by ICD-11 code
        results = search_icd_11(terms="1B12.0", maxList=5)
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'icd-11',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_hcpcs(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search HCPCS Level II procedure and equipment codes

    Healthcare Common Procedure Coding System (HCPCS) codes for medical services,
    procedures, and equipment not covered by CPT codes.

    Args:
        terms: Search query string
              Examples: "wheelchair", "glucose", "insulin pump", "E0470"

              Common searches:
              - Equipment: "wheelchair", "walker", "oxygen"
              - Supplies: "glucose monitor", "test strips"
              - Drugs: "insulin", "chemotherapy"
              - Procedures: "injection", "infusion"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "code", "short_desc", "long_desc", "display"
                     Default: searches all

        displayFields: Fields to display
                      Default: "code,display"

        extraFields: Additional fields to include
                    Available fields:
                    - short_desc: Brief description
                    - long_desc: Detailed specifications
                    - add_dt: Date added
                    - term_dt: Termination date
                    - act_eff_dt: Effective date
                    - obsolete: Obsolete flag
                    - is_noc: Not otherwise classified flag

        additionalQuery: Advanced filtering
                        Examples:
                        - "is_noc:false" - Exclude generic NOC codes
                        - "obsolete:false" - Active codes only
                        - "code:E*" - All E codes (durable medical equipment)

        offset: Pagination offset (default: 0)

        count: Page size for pagination (default: 7)

    Returns:
        dict: HCPCS search results

        Response structure:
        {
            "method": "hcpcs-LII",
            "totalCount": 325,
            "results": [
                {
                    "code": "E0470",
                    "display": "Respiratory assist device, bi-level pressure",
                    "short_desc": "Respiratory assist device",
                    "long_desc": "Respiratory assist device, bi-level pressure capability..."
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for wheelchair codes
        results = search_hcpcs(terms="wheelchair", maxList=20)

        # Extract codes and descriptions
        for item in results.get('results', []):
            code = item.get('code')
            desc = item.get('display')
            print(f"{code}: {desc}")

        # Example 2: Search glucose monitoring equipment
        results = search_hcpcs(
            terms="glucose",
            maxList=30
        )

        # Example 3: Get detailed specifications
        results = search_hcpcs(
            terms="E0470",
            extraFields="short_desc,long_desc,act_eff_dt",
            maxList=5
        )

        for item in results.get('results', []):
            code = item.get('code')
            short = item.get('short_desc')
            long = item.get('long_desc')
            effective = item.get('act_eff_dt')
            print(f"{code}: {short}")
            print(f"  Details: {long}")
            print(f"  Effective: {effective}")

        # Example 4: Exclude NOC codes
        results = search_hcpcs(
            terms="wheelchair",
            additionalQuery="is_noc:false",
            maxList=25
        )

        # Example 5: Paginated search for all E codes (DME)
        page_size = 100
        offset = 0
        all_e_codes = []

        while True:
            page = search_hcpcs(
                terms="E",
                searchFields="code",
                count=page_size,
                offset=offset,
                maxList=500
            )

            results = page.get('results', [])
            all_e_codes.extend(results)

            if len(results) < page_size:
                break

            offset += page_size

        print(f"Total E codes: {len(all_e_codes)}")
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'hcpcs-LII',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_npi_organizations(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search National Provider Identifier (NPI) organization records

    Search healthcare organizations by NPI number, name, specialty, or location.
    Data from CMS National Plan and Provider Enumeration System (NPPES).

    Args:
        terms: Search query string
              Examples: "MAYO CLINIC", "cardiology", "1234567890" (NPI)

              Common searches:
              - Organization names: "Mayo Clinic", "Johns Hopkins"
              - Specialties: "cardiology", "oncology", "neurology"
              - NPI numbers: "1234567890"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "NPI", "name.full", "provider_type", "addr_practice.full"
                     Default: searches all

        displayFields: Fields to display
                      Default: "NPI,name.full,provider_type"

        extraFields: Additional fields to include
                    Available fields:
                    - name.last, name.first, name.middle
                    - provider_type
                    - addr_practice.line1, addr_practice.city, addr_practice.state
                    - addr_mailing.full
                    - other_ids
                    - licenses
                    - misc.auth_official.last
                    - misc.enumeration_date
                    - misc.last_update_date

        additionalQuery: Elasticsearch query for advanced filtering

                        CRITICAL: Supports complex boolean expressions with parentheses!
                        Tool auto-optimizes parentheses for API compatibility.

                        Simple filtering:
                        - "addr_practice.state:CA" - California providers
                        - "provider_type:Physician*" - Physician specialties

                        Boolean expressions:
                        - "gender:F AND addr_practice.state:CA"
                        - "cardiology OR neurology"

                        Complex parentheses (auto-optimized):
                        - "addr_practice.state:CA AND (addr_practice.city:\\"Los Angeles\\" OR addr_practice.city:\\"San Francisco\\")"
                        - "hospital OR medical AND (addr_practice.state:CA OR addr_practice.state:NY)"
                        - "(provider_type:Physician* OR provider_type:Nurse*) AND addr_practice.state:TX"

        offset: Pagination offset (default: 0)

        count: Page size (1-500, default: 7)

    Returns:
        dict: NPI organization search results

        Response structure:
        {
            "method": "npi-organizations",
            "totalCount": 156,
            "results": [
                {
                    "NPI": "1234567890",
                    "name.full": "Mayo Clinic",
                    "provider_type": "Cardiology",
                    "addr_practice.full": "200 First St SW, Rochester, MN 55905"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for cardiology organizations
        results = search_npi_organizations(
            terms="cardiology",
            maxList=20
        )

        for org in results.get('results', []):
            npi = org.get('NPI')
            name = org.get('name.full')
            specialty = org.get('provider_type')
            print(f"{name} ({npi}): {specialty}")

        # Example 2: Search California providers
        results = search_npi_organizations(
            terms="",
            additionalQuery="addr_practice.state:CA",
            maxList=50
        )

        # Example 3: Complex query with parentheses (auto-optimized)
        results = search_npi_organizations(
            terms="hospital OR medical",
            additionalQuery='addr_practice.state:CA AND (addr_practice.city:"Los Angeles" OR addr_practice.city:"San Francisco")',
            extraFields="provider_type,addr_practice.city,addr_practice.state,name.full,NPI",
            maxList=25
        )

        # Example 4: Get detailed organization info
        results = search_npi_organizations(
            terms="Mayo Clinic",
            extraFields="addr_practice.line1,addr_practice.city,addr_practice.state,misc.enumeration_date",
            maxList=5
        )

        for org in results.get('results', []):
            name = org.get('name.full')
            address = org.get('addr_practice.line1')
            city = org.get('addr_practice.city')
            state = org.get('addr_practice.state')
            enum_date = org.get('misc.enumeration_date')
            print(f"{name}")
            print(f"  {address}, {city}, {state}")
            print(f"  Enumeration Date: {enum_date}")

        # Example 5: Physician specialties in Texas
        results = search_npi_organizations(
            terms="",
            additionalQuery="provider_type:Physician* AND addr_practice.state:TX",
            maxList=100
        )

        # Group by specialty
        specialties = {}
        for org in results.get('results', []):
            specialty = org.get('provider_type', 'Unknown')
            specialties[specialty] = specialties.get(specialty, 0) + 1

        print("Texas Physician Specialties:")
        for specialty, count in sorted(specialties.items(), key=lambda x: x[1], reverse=True):
            print(f"  {specialty}: {count}")
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'npi-organizations',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_npi_individuals(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search National Provider Identifier (NPI) individual provider records

    Search individual healthcare providers by NPI number, name, specialty, or location.

    Args:
        terms: Search query string
              Examples: "john smith", "cardiologist", "1234567890" (NPI)

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "NPI", "name.full", "provider_type", "addr_practice.full"

        displayFields: Fields to display

        extraFields: Additional fields
                    Available fields (individuals):
                    - gender: "M" or "F"
                    - name.last, name.first, name.middle, name.credential
                    - All organization fields

        additionalQuery: Advanced filtering
                        Examples:
                        - "gender:M" - Male providers only
                        - "gender:F AND addr_practice.state:CA" - Female California providers
                        - "provider_type:Cardiologist AND gender:M"

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: NPI individual search results

    Examples:
        # Search for cardiologists
        results = search_npi_individuals(
            terms="cardiologist",
            maxList=20
        )

        # Search female physicians in California
        results = search_npi_individuals(
            terms="physician",
            additionalQuery="gender:F AND addr_practice.state:CA",
            extraFields="gender,name.full,provider_type,addr_practice.city",
            maxList=50
        )

        # Get provider credentials
        results = search_npi_individuals(
            terms="john smith",
            extraFields="name.credential,provider_type,gender",
            maxList=10
        )
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'npi-individuals',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_hpo_vocabulary(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search Human Phenotype Ontology (HPO) vocabulary

    Standardized vocabulary for phenotypic abnormalities in human disease.
    Over 13,000+ phenotype terms.

    Args:
        terms: Search query string
              Examples: "blood pressure", "seizure", "intellectual disability"

              Common phenotypes:
              - Cardiovascular: "hypertension", "arrhythmia"
              - Neurological: "seizure", "ataxia", "tremor"
              - Metabolic: "hypoglycemia", "acidosis"
              - Developmental: "developmental delay", "microcephaly"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "id" (HPO IDs like HP:0001871), "name", "synonym.term"
                     Default: "id,name,synonym.term"

        displayFields: Fields to display
                      Default: "id,name"

        extraFields: Additional fields
                    Available fields:
                    - definition: Phenotype definition
                    - def_xref: Definition cross-references
                    - created_by, creation_date
                    - comment
                    - is_obsolete
                    - replaced_by, consider
                    - alt_id: Alternative IDs
                    - synonym: Synonym terms
                    - is_a: Parent terms
                    - xref: Cross-references
                    - property: Additional properties

        additionalQuery: Advanced filtering
                        Examples:
                        - "is_obsolete:false" - Active terms only
                        - "id:HP\\:000*" - Specific HPO ID patterns
                        Note: Escape colons in IDs with backslash

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: HPO vocabulary search results

        Response structure:
        {
            "method": "hpo-vocabulary",
            "totalCount": 47,
            "results": [
                {
                    "id": "HP:0001871",
                    "name": "Abnormality of blood and blood-forming tissues",
                    "definition": "An abnormality of the hematopoietic system"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for blood pressure phenotypes
        results = search_hpo_vocabulary(
            terms="blood pressure",
            maxList=15
        )

        for phenotype in results.get('results', []):
            hpo_id = phenotype.get('id')
            name = phenotype.get('name')
            print(f"{hpo_id}: {name}")

        # Example 2: Get phenotype definitions
        results = search_hpo_vocabulary(
            terms="seizure",
            extraFields="definition,synonym",
            maxList=20
        )

        for phenotype in results.get('results', []):
            hpo_id = phenotype.get('id')
            name = phenotype.get('name')
            definition = phenotype.get('definition')
            print(f"{hpo_id}: {name}")
            print(f"  Definition: {definition}")

        # Example 3: Search by HPO ID pattern
        results = search_hpo_vocabulary(
            terms="HP:0001871",
            maxList=5
        )

        # Example 4: Exclude obsolete terms
        results = search_hpo_vocabulary(
            terms="intellectual disability",
            additionalQuery="is_obsolete:false",
            maxList=25
        )

        # Example 5: Get complete phenotype hierarchy
        results = search_hpo_vocabulary(
            terms="hypertension",
            extraFields="is_a,definition,xref",
            maxList=10
        )

        for phenotype in results.get('results', []):
            name = phenotype.get('name')
            parent = phenotype.get('is_a')
            xref = phenotype.get('xref')
            print(f"{name}")
            print(f"  Parent: {parent}")
            print(f"  Cross-refs: {xref}")
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'hpo-vocabulary',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_conditions(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search medical conditions from Regenstrief Institute

    Curated list of 2,400+ medical conditions with ICD-9/ICD-10 code mappings.

    Args:
        terms: Search query string
              Examples: "gastroenteritis", "diabetes", "hypertension"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "consumer_name", "primary_name", "word_synonyms",
                             "synonyms", "term_icd9_code", "term_icd9_text"
                     Default: searches all

        displayFields: Fields to display

        extraFields: Additional fields
                    Available fields:
                    - primary_name: Medical name
                    - consumer_name: Consumer-friendly name
                    - icd10cm_codes: ICD-10-CM codes
                    - icd10cm: ICD-10 descriptions
                    - term_icd9_code: ICD-9 code
                    - term_icd9_text: ICD-9 description
                    - word_synonyms: Word-level synonyms
                    - synonyms: Term synonyms
                    - info_link_data: External links
                    - key_id: Unique identifier

        additionalQuery: Advanced filtering
                        Examples:
                        - "term_icd9_code:558*" - Specific ICD-9 patterns
                        - "icd10cm_codes:*E11*" - ICD-10 code filtering

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: Medical conditions search results

        Response structure:
        {
            "method": "conditions",
            "totalCount": 38,
            "results": [
                {
                    "consumer_name": "Stomach flu",
                    "primary_name": "Gastroenteritis",
                    "term_icd9_code": "558.9",
                    "icd10cm_codes": "K52.9"
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for diabetes conditions
        results = search_conditions(
            terms="diabetes",
            maxList=20
        )

        for condition in results.get('results', []):
            consumer = condition.get('consumer_name')
            medical = condition.get('primary_name')
            icd10 = condition.get('icd10cm_codes')
            print(f"{consumer} ({medical}): {icd10}")

        # Example 2: Get ICD-9/ICD-10 mappings
        results = search_conditions(
            terms="hypertension",
            extraFields="term_icd9_code,term_icd9_text,icd10cm_codes,icd10cm",
            maxList=15
        )

        for condition in results.get('results', []):
            name = condition.get('primary_name')
            icd9_code = condition.get('term_icd9_code')
            icd9_text = condition.get('term_icd9_text')
            icd10_code = condition.get('icd10cm_codes')
            print(f"{name}")
            print(f"  ICD-9: {icd9_code} - {icd9_text}")
            print(f"  ICD-10: {icd10_code}")

        # Example 3: Search by ICD-9 code pattern
        results = search_conditions(
            terms="",
            additionalQuery="term_icd9_code:250*",
            maxList=50
        )

        # Example 4: Get synonyms
        results = search_conditions(
            terms="gastroenteritis",
            extraFields="word_synonyms,synonyms,info_link_data",
            maxList=10
        )

        for condition in results.get('results', []):
            name = condition.get('primary_name')
            synonyms = condition.get('synonyms')
            print(f"{name}")
            print(f"  Also known as: {synonyms}")
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'conditions',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_rx_terms(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search RxTerms drug interface terminology

    Drug name/route pairs with strengths and forms. Interface terminology
    for electronic health records.

    Args:
        terms: Search query string
              Examples: "arava", "articaine", "lisinopril", "metformin"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "DISPLAY_NAME" (drug name/route pairs),
                             "DISPLAY_NAME_SYNONYM" (synonyms)
                     Default: "DISPLAY_NAME,DISPLAY_NAME_SYNONYM"

        displayFields: Fields to display
                      Default: "DISPLAY_NAME"

        extraFields: Additional fields
                    Available fields:
                    - STRENGTHS_AND_FORMS: Available strengths/formulations
                    - RXCUIS: RxNorm concept IDs
                    - SXDG_RXCUI: Semantic clinical drug group RxCUI
                    - DISPLAY_NAME_SYNONYM: Alternative names

        additionalQuery: Advanced filtering

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: RxTerms search results

        Response structure:
        {
            "method": "rx-terms",
            "totalCount": 12,
            "results": [
                {
                    "DISPLAY_NAME": "lisinopril oral",
                    "STRENGTHS_AND_FORMS": "10 MG, 20 MG, 5 MG, 2.5 MG, 40 MG, 30 MG",
                    "RXCUIS": "314076,197884,..."
                },
                ...
            ]
        }

    Examples:
        # Example 1: Search for drug by name
        results = search_rx_terms(
            terms="lisinopril",
            maxList=15
        )

        for drug in results.get('results', []):
            name = drug.get('DISPLAY_NAME')
            print(f"Drug: {name}")

        # Example 2: Get strengths and formulations
        results = search_rx_terms(
            terms="metformin",
            extraFields="STRENGTHS_AND_FORMS,RXCUIS",
            maxList=20
        )

        for drug in results.get('results', []):
            name = drug.get('DISPLAY_NAME')
            strengths = drug.get('STRENGTHS_AND_FORMS')
            rxcuis = drug.get('RXCUIS')
            print(f"{name}")
            print(f"  Strengths: {strengths}")
            print(f"  RxCUIs: {rxcuis}")

        # Example 3: Search with synonyms
        results = search_rx_terms(
            terms="arava",
            extraFields="DISPLAY_NAME_SYNONYM,STRENGTHS_AND_FORMS",
            maxList=10
        )

        # Example 4: Get all formulations for a drug
        results = search_rx_terms(
            terms="insulin",
            extraFields="STRENGTHS_AND_FORMS,SXDG_RXCUI",
            maxList=50
        )

        # Group by route
        by_route = {}
        for drug in results.get('results', []):
            name = drug.get('DISPLAY_NAME', '')
            route = name.split()[-1] if name else 'Unknown'
            if route not in by_route:
                by_route[route] = []
            by_route[route].append(name)

        print("Insulin formulations by route:")
        for route, drugs in by_route.items():
            print(f"  {route}: {len(drugs)} formulations")
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'rx-terms',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_loinc_questions(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search LOINC Questions and Forms

    Logical Observation Identifiers Names and Codes (LOINC) for medical tests,
    measurements, and clinical observations.

    Args:
        terms: Search query string
              Examples: "walk", "blood pressure", "vital signs", "45593-1"

              Common searches:
              - Clinical observations: "blood pressure", "heart rate"
              - Lab tests: "glucose", "hemoglobin"
              - Assessments: "pain scale", "mobility"
              - LOINC codes: "45593-1"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search

        displayFields: Fields to display

        extraFields: Additional fields
                    Available fields:
                    - isCopyrighted: Copyright flag
                    - datatype: Question type (CNE=list, etc.)
                    - COMPONENT: Test component
                    - etc.

        additionalQuery: Advanced filtering
                        Examples:
                        - "isCopyrighted:false" - Exclude copyrighted items
                        - "datatype:CNE" - List questions only
                        - "COMPONENT:*pressure*" - Component filtering

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: LOINC search results

    Examples:
        # Search for blood pressure measurements
        results = search_loinc_questions(
            terms="blood pressure",
            maxList=20
        )

        # Exclude copyrighted LOINC items
        results = search_loinc_questions(
            terms="vital signs",
            additionalQuery="isCopyrighted:false",
            maxList=30
        )

        # Search by LOINC code
        results = search_loinc_questions(
            terms="45593-1",
            maxList=5
        )
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'loinc-questions',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_ncbi_genes(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search NCBI Genes (human gene information)

    Human gene information from NCBI's Gene dataset.

    Args:
        terms: Search query string
              Examples: "BRCA1", "TP53", "MTX", gene symbols or names

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search
                     Options: "Symbol" (gene symbols), gene names, descriptions

        displayFields: Fields to display

        extraFields: Additional fields
                    Available fields:
                    - chromosome: Chromosome location
                    - type_of_gene: Gene type (protein-coding, etc.)
                    - Symbol: Gene symbol
                    - description: Gene description

        additionalQuery: Advanced filtering
                        Examples:
                        - "chromosome:1" - Specific chromosome
                        - "type_of_gene:protein-coding" - Gene type
                        - "Symbol:BRCA*" - Symbol patterns

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: NCBI gene search results

    Examples:
        # Search for BRCA1 gene
        results = search_ncbi_genes(
            terms="BRCA1",
            maxList=10
        )

        # Get protein-coding genes on chromosome 1
        results = search_ncbi_genes(
            terms="",
            additionalQuery="chromosome:1 AND type_of_gene:protein-coding",
            extraFields="Symbol,chromosome,description",
            maxList=100
        )

        # Search by gene symbol pattern
        results = search_ncbi_genes(
            terms="",
            additionalQuery="Symbol:TP*",
            maxList=50
        )
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'ncbi-genes',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


def search_major_surgeries_implants(
    terms: str,
    maxList: int = 7,
    searchFields: Optional[str] = None,
    displayFields: Optional[str] = None,
    extraFields: Optional[str] = None,
    additionalQuery: Optional[str] = None,
    offset: int = 0,
    count: int = 7
) -> Dict[str, Any]:
    """
    Search major surgeries and implants

    280+ major surgical procedures and implants from Regenstrief Institute.

    Args:
        terms: Search query string
              Examples: "gastrostomy", "bypass", "implant", "gastrectomy"

              Common searches:
              - Procedures: "bypass", "resection", "replacement"
              - Implants: "pacemaker", "prosthesis", "stent"
              - Anatomical: "cardiac", "orthopedic", "vascular"

        maxList: Maximum results (1-500, default: 7)

        searchFields: Fields to search

        displayFields: Fields to display

        extraFields: Additional fields
                    Available fields:
                    - term_icd9_code: ICD-9 procedure code
                    - primary_name: Procedure name

        additionalQuery: Advanced filtering
                        Examples:
                        - "term_icd9_code:*" - Procedures with ICD-9 codes
                        - "primary_name:*bypass*" - Specific patterns

        offset: Pagination offset (default: 0)

        count: Page size (default: 7)

    Returns:
        dict: Surgery/implant search results

    Examples:
        # Search for bypass procedures
        results = search_major_surgeries_implants(
            terms="bypass",
            maxList=20
        )

        for procedure in results.get('results', []):
            name = procedure.get('primary_name')
            print(f"Procedure: {name}")

        # Get procedures with ICD-9 codes
        results = search_major_surgeries_implants(
            terms="gastrostomy",
            extraFields="term_icd9_code,primary_name",
            maxList=15
        )

        for procedure in results.get('results', []):
            name = procedure.get('primary_name')
            icd9 = procedure.get('term_icd9_code')
            print(f"{name}: ICD-9 {icd9}")

        # Search for cardiac procedures
        results = search_major_surgeries_implants(
            terms="cardiac",
            additionalQuery="term_icd9_code:*",
            maxList=50
        )
    """
    client = get_client('nlm-codes-mcp')

    params = {
        'method': 'major-surgeries-implants',
        'terms': terms,
        'maxList': maxList,
        'offset': offset,
        'count': count
    }

    if searchFields:
        params['searchFields'] = searchFields
    if displayFields:
        params['displayFields'] = displayFields
    if extraFields:
        params['extraFields'] = extraFields
    if additionalQuery:
        params['additionalQuery'] = additionalQuery

    return client.call_tool('nlm_ct_codes', params)


__all__ = [
    'search_icd_10_cm',
    'search_icd_11',
    'search_hcpcs',
    'search_npi_organizations',
    'search_npi_individuals',
    'search_hpo_vocabulary',
    'search_conditions',
    'search_rx_terms',
    'search_loinc_questions',
    'search_ncbi_genes',
    'search_major_surgeries_implants'
]
