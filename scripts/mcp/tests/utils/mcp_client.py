"""MCP Client Utilities for Testing

Provides a simple interface to call MCP Python API stubs for testing purposes.
This uses the actual Python API stubs created in scripts/mcp/servers/.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any
import importlib

# Add servers directory to path
SERVERS_DIR = Path(__file__).parent.parent.parent / "servers"
sys.path.insert(0, str(SERVERS_DIR))


class MCPTestClient:
    """Test client that calls MCP Python API stubs"""

    def __init__(self, mcp_name: str, delay: float = 1.0):
        """
        Initialize MCP test client

        Args:
            mcp_name: Name of MCP server (e.g., 'fda-mcp', 'ct-gov-mcp')
            delay: Delay between calls in seconds (for rate limiting)
        """
        self.mcp_name = mcp_name
        self.delay = delay
        self.last_call_time = 0

        # Map MCP names to module names
        module_map = {
            'fda-mcp': 'fda_mcp',
            'ct-gov-mcp': 'ct_gov_mcp',
            'pubmed-mcp': 'pubmed_mcp',
            'opentargets-mcp-server': 'opentargets_mcp',
            'pubchem-mcp-server': 'pubchem_mcp',
            'datacommons-mcp': 'datacommons_mcp',
            'sec-mcp-server': 'sec_edgar_mcp',
            'patents-mcp-server': 'uspto_patents_mcp',
            'nlm-codes-mcp': 'nlm_codes_mcp',
            'who-mcp-server': 'who_mcp',
            'healthcare-mcp': 'healthcare_mcp',
            'financials-mcp-server': 'financials_mcp'
        }

        module_name = module_map.get(mcp_name)
        if not module_name:
            raise ValueError(f"Unknown MCP server: {mcp_name}")

        # Import the module
        try:
            self.module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Could not import {module_name}: {e}")

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via Python API stub

        Args:
            tool_name: Name of the function to call (e.g., 'lookup_drug', 'search_studies')
            params: Function parameters

        Returns:
            dict: Tool response or error information
        """
        # Rate limiting
        elapsed = time.time() - self.last_call_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        try:
            # Get the function from the module
            func = getattr(self.module, tool_name, None)
            if func is None:
                raise AttributeError(f"Function '{tool_name}' not found in {self.mcp_name}")

            # Call the function
            response = func(**params)

            result = {
                'success': True,
                'mcp': self.mcp_name,
                'tool': tool_name,
                'params': params,
                'response': response,
                'error': None,
                'timestamp': time.time()
            }

            self.last_call_time = time.time()
            return result

        except Exception as e:
            return {
                'success': False,
                'mcp': self.mcp_name,
                'tool': tool_name,
                'params': params,
                'response': None,
                'error': str(e),
                'timestamp': time.time()
            }


def get_test_client(mcp_name: str, delay: float = 1.0) -> MCPTestClient:
    """
    Factory function to get MCP test client

    Args:
        mcp_name: MCP server name (e.g., 'fda-mcp')
        delay: Delay between calls

    Returns:
        MCPTestClient instance
    """
    return MCPTestClient(mcp_name, delay)
