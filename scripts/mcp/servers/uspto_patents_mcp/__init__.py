"""USPTO Patents MCP Server - Python API

Provides Python functions for USPTO patent search and retrieval.
Data stays in execution environment - only summaries flow to model.

CRITICAL USPTO QUIRKS:
1. Boolean operators: AND, OR, NOT (case-sensitive)
2. Field-specific search: assignee:, inventor:, date:, title:
3. Date format: [YYYYMMDD TO YYYYMMDD] for ranges
4. Patent numbers: 8-digit format (e.g., "11234567")
5. Application numbers: Format with hyphens (e.g., "14/412,875")
6. Two patent databases: Public Search (granted + applications)
7. GUID: Unique document identifier for detailed retrieval
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def ppubs_search_patents(
    query: str,
    start: int = 0,
    limit: int = 100,
    sort: Optional[str] = None,
    default_operator: str = "OR",
    expand_plurals: bool = True,
    british_equivalents: bool = True
) -> Dict[str, Any]:
    """
    Search granted patents in USPTO Public Search

    Args:
        query: Search query using USPTO syntax

              BOOLEAN OPERATORS (case-sensitive):
              - AND - Both terms must appear
              - OR - Either term can appear (default)
              - NOT - Exclude term

              FIELD-SPECIFIC SEARCH:
              - assignee:"Company Name" - Patent owner
              - inventor:"Last, First" - Inventor name
              - title:"keyword" - In patent title
              - abstract:"keyword" - In abstract
              - claims:"keyword" - In claims
              - date:[YYYYMMDD TO YYYYMMDD] - Date range

              Examples:
              - Simple: "GLP-1 AND diabetes"
              - Assignee: 'assignee:"Novo Nordisk" AND GLP-1'
              - Date range: "GLP-1 AND date:[20200101 TO 20241231]"
              - Complex: '(GLP-1 OR glucagon) AND assignee:"Novo Nordisk" NOT review'

        start: Starting result position (0-based, default: 0)

        limit: Maximum results to return (1-1000, default: 100)

        sort: Sort order
             Values: "date_publ desc", "date_publ asc", etc.
             Default: "date_publ desc" (newest first)

        default_operator: Default boolean operator when not specified
                         Values: "OR" (default), "AND"

        expand_plurals: Include plural forms of search terms (default: True)

        british_equivalents: Include British spellings (default: True)

    Returns:
        dict: Patent search results

        Key fields:
        - guid: Document GUID (use for ppubs_get_full_document)
        - patentNumber: Patent number
        - patentTitle: Title
        - assigneeEntityName: Owner
        - inventorName: Inventors
        - filingDate: Application date
        - patentIssueDate: Grant date

    Examples:
        # Example 1: Basic keyword search
        results = ppubs_search_patents(
            query="GLP-1 diabetes",
            limit=50
        )

        # Extract patent numbers
        patents = []
        for result in results.get('results', []):
            patent_num = result.get('patentNumber')
            title = result.get('patentTitle')
            assignee = result.get('assigneeEntityName')
            issue_date = result.get('patentIssueDate')
            patents.append((patent_num, title, assignee, issue_date))

        print(f"Found {len(patents)} patents")
        for num, title, assignee, date in patents[:10]:
            print(f"{num} ({date}): {title}")
            print(f"  Owner: {assignee}")

        # Example 2: Company-specific search
        results = ppubs_search_patents(
            query='assignee:"Novo Nordisk" AND GLP-1',
            limit=100
        )

        # Example 3: Date-filtered search
        results = ppubs_search_patents(
            query="GLP-1 AND date:[20200101 TO 20241231]",
            limit=50
        )

        # Example 4: Complex boolean query
        results = ppubs_search_patents(
            query='(GLP-1 OR "glucagon receptor") AND assignee:"Eli Lilly" NOT antibody',
            limit=75
        )

        # Example 5: Title search
        results = ppubs_search_patents(
            query='title:"semaglutide"',
            limit=25
        )
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'ppubs_search_patents',
        'query': query,
        'start': start,
        'limit': limit,
        'default_operator': default_operator,
        'expand_plurals': expand_plurals,
        'british_equivalents': british_equivalents
    }

    if sort:
        params['sort'] = sort

    return client.call_tool('uspto_patents', params)


def ppubs_search_applications(
    query: str,
    start: int = 0,
    limit: int = 100,
    sort: Optional[str] = None,
    default_operator: str = "OR",
    expand_plurals: bool = True,
    british_equivalents: bool = True
) -> Dict[str, Any]:
    """
    Search published patent applications in USPTO Public Search

    Args:
        query: Search query (same syntax as ppubs_search_patents)
        start: Starting position (default: 0)
        limit: Maximum results (1-1000, default: 100)
        sort: Sort order
        default_operator: "OR" or "AND"
        expand_plurals: Include plurals (default: True)
        british_equivalents: Include British spellings (default: True)

    Returns:
        dict: Patent application search results

    Examples:
        # Search for pending applications
        results = ppubs_search_applications(
            query='assignee:"Novo Nordisk" AND semaglutide',
            limit=50
        )

        # Recent applications only
        results = ppubs_search_applications(
            query="GLP-1 AND date:[20230101 TO 20241231]",
            limit=100
        )
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'ppubs_search_applications',
        'query': query,
        'start': start,
        'limit': limit,
        'default_operator': default_operator,
        'expand_plurals': expand_plurals,
        'british_equivalents': british_equivalents
    }

    if sort:
        params['sort'] = sort

    return client.call_tool('uspto_patents', params)


def ppubs_get_full_document(
    guid: str,
    source_type: str = "USPAT"
) -> Dict[str, Any]:
    """
    Get full patent document by GUID

    Args:
        guid: Document unique identifier
             Get from search results

        source_type: Document type
                    Values:
                    - "USPAT" - Granted patents (default)
                    - "US-PGPUB" - Published applications

    Returns:
        dict: Full patent document with all sections

        Sections include:
        - Abstract
        - Claims
        - Description
        - Background
        - Summary
        - Detailed Description
        - Drawings

    Examples:
        # Get full patent from search result
        search_results = ppubs_search_patents(query="GLP-1", limit=1)
        first_result = search_results['results'][0]
        guid = first_result['guid']

        # Retrieve full document
        full_doc = ppubs_get_full_document(guid=guid)

        # Extract sections
        abstract = full_doc.get('abstract')
        claims = full_doc.get('claims')
        description = full_doc.get('description')

        print(f"Abstract: {abstract[:200]}...")
        print(f"\\nTotal claims: {len(claims)}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'ppubs_get_full_document',
        'guid': guid,
        'source_type': source_type
    }

    return client.call_tool('uspto_patents', params)


def ppubs_get_patent_by_number(
    patent_number: str
) -> Dict[str, Any]:
    """
    Get granted patent's full text by patent number

    Args:
        patent_number: Patent number (e.g., "11234567", "10123456")
                      Can be 7 or 8 digits

    Returns:
        dict: Full patent document

    Examples:
        # Get specific patent
        patent = ppubs_get_patent_by_number(patent_number="11234567")

        # Extract key information
        title = patent.get('title')
        abstract = patent.get('abstract')
        assignee = patent.get('assignee')
        inventors = patent.get('inventors', [])

        print(f"Title: {title}")
        print(f"Owner: {assignee}")
        print(f"Inventors: {', '.join(inventors)}")
        print(f"\\nAbstract:\\n{abstract}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'ppubs_get_patent_by_number',
        'patent_number': patent_number
    }

    return client.call_tool('uspto_patents', params)


def ppubs_download_patent_pdf(
    patent_number: str
) -> Dict[str, Any]:
    """
    Download granted patent as PDF

    Args:
        patent_number: Patent number

    Returns:
        dict: PDF download information

        May contain:
        - pdf_url: URL to PDF
        - pdf_data: Base64-encoded PDF content

    Examples:
        # Download patent PDF
        pdf_result = ppubs_download_patent_pdf(patent_number="11234567")

        if 'pdf_data' in pdf_result:
            import base64
            pdf_bytes = base64.b64decode(pdf_result['pdf_data'])
            with open('patent_11234567.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("PDF saved")
        elif 'pdf_url' in pdf_result:
            print(f"PDF available at: {pdf_result['pdf_url']}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'ppubs_download_patent_pdf',
        'patent_number': patent_number
    }

    return client.call_tool('uspto_patents', params)


def get_app_metadata(
    app_num: str
) -> Dict[str, Any]:
    """
    Get patent application metadata and status

    Args:
        app_num: U.S. Patent Application Number
                Format: "14412875" (no hyphens for API)
                Display format: "14/412,875"

    Returns:
        dict: Application metadata

        Key fields:
        - applicationNumber: Application number
        - title: Application title
        - status: Current status
        - filingDate: Filing date
        - inventors: Inventor list
        - assignee: Owner

    Examples:
        # Get application status
        app = get_app_metadata(app_num="14412875")

        title = app.get('title')
        status = app.get('status')
        filing_date = app.get('filingDate')
        assignee = app.get('assignee')

        print(f"Application: {title}")
        print(f"Status: {status}")
        print(f"Filed: {filing_date}")
        print(f"Owner: {assignee}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'get_app_metadata',
        'app_num': app_num
    }

    return client.call_tool('uspto_patents', params)


def search_applications(
    q: Optional[str] = None,
    offset: int = 0,
    limit: int = 25,
    sort: Optional[str] = None,
    facets: Optional[str] = None,
    fields: Optional[str] = None,
    filters: Optional[str] = None,
    range_filters: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search patent applications with query parameters

    Args:
        q: Search query string

        offset: Starting result position (default: 0)

        limit: Maximum results (default: 25)

        sort: Sort order

        facets: Fields to facet upon (comma-separated)

        fields: Fields to include in response (comma-separated)

        filters: Filter conditions

        range_filters: Range filter conditions

    Returns:
        dict: Application search results

    Examples:
        # Search with filters
        results = search_applications(
            q="GLP-1",
            limit=50,
            sort="filingDate desc"
        )

        # Faceted search
        results = search_applications(
            q="diabetes",
            facets="assignee,status",
            limit=100
        )
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'search_applications',
        'offset': offset,
        'limit': limit
    }

    if q:
        params['q'] = q
    if sort:
        params['sort'] = sort
    if facets:
        params['facets'] = facets
    if fields:
        params['fields'] = fields
    if filters:
        params['filters'] = filters
    if range_filters:
        params['range_filters'] = range_filters

    return client.call_tool('uspto_patents', params)


def get_app_transactions(
    app_num: str
) -> Dict[str, Any]:
    """
    Get transaction history for a patent application

    Shows all USPTO actions and applicant responses.

    Args:
        app_num: U.S. Patent Application Number

    Returns:
        dict: Transaction history

    Examples:
        # Get prosecution history
        transactions = get_app_transactions(app_num="14412875")

        # Analyze timeline
        for transaction in transactions.get('transactions', []):
            date = transaction.get('date')
            code = transaction.get('code')
            description = transaction.get('description')
            print(f"{date}: {code} - {description}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'get_app_transactions',
        'app_num': app_num
    }

    return client.call_tool('uspto_patents', params)


def get_app_continuity(
    app_num: str
) -> Dict[str, Any]:
    """
    Get continuity data (parent/child applications)

    Shows family relationships between applications.

    Args:
        app_num: U.S. Patent Application Number

    Returns:
        dict: Continuity data

        Shows:
        - Parent applications
        - Child applications (continuations, divisions, CIPs)
        - Priority claims

    Examples:
        # Get patent family
        continuity = get_app_continuity(app_num="14412875")

        parents = continuity.get('parents', [])
        children = continuity.get('children', [])

        print(f"Parent applications: {len(parents)}")
        print(f"Child applications: {len(children)}")

        for parent in parents:
            print(f"  Parent: {parent.get('applicationNumber')}")

        for child in children:
            print(f"  Child: {child.get('applicationNumber')} ({child.get('type')})")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'get_app_continuity',
        'app_num': app_num
    }

    return client.call_tool('uspto_patents', params)


def get_app_foreign_priority(
    app_num: str
) -> Dict[str, Any]:
    """
    Get foreign priority claims

    Shows priority claims from foreign patent applications.

    Args:
        app_num: U.S. Patent Application Number

    Returns:
        dict: Foreign priority data

    Examples:
        # Get foreign priorities
        priorities = get_app_foreign_priority(app_num="14412875")

        for priority in priorities.get('priorities', []):
            country = priority.get('country')
            app_num = priority.get('applicationNumber')
            filing_date = priority.get('filingDate')
            print(f"{country} Application {app_num} filed {filing_date}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'get_app_foreign_priority',
        'app_num': app_num
    }

    return client.call_tool('uspto_patents', params)


def get_app_attorney(
    app_num: str
) -> Dict[str, Any]:
    """
    Get attorney/agent information

    Args:
        app_num: U.S. Patent Application Number

    Returns:
        dict: Attorney information

    Examples:
        # Get attorney info
        attorney = get_app_attorney(app_num="14412875")

        name = attorney.get('name')
        registration = attorney.get('registrationNumber')
        firm = attorney.get('firm')

        print(f"Attorney: {name}")
        print(f"Registration: {registration}")
        print(f"Firm: {firm}")
    """
    client = get_client('patents-mcp-server')

    params = {
        'method': 'get_app_attorney',
        'app_num': app_num
    }

    return client.call_tool('uspto_patents', params)


__all__ = [
    'ppubs_search_patents',
    'ppubs_search_applications',
    'ppubs_get_full_document',
    'ppubs_get_patent_by_number',
    'ppubs_download_patent_pdf',
    'get_app_metadata',
    'search_applications',
    'get_app_transactions',
    'get_app_continuity',
    'get_app_foreign_priority',
    'get_app_attorney'
]
