#!/usr/bin/env python3
"""
MCP Client Wrapper - Communicates with MCP servers via stdio

Enables code execution pattern from Anthropic's article:
https://www.anthropic.com/engineering/code-execution-with-mcp

Usage:
    from mcp.client import get_client

    client = get_client('fda-mcp')
    result = client.call_tool('lookup_drug', {'search_term': 'obesity'})
"""

import json
import subprocess
import os
from typing import Dict, Any, Optional
from pathlib import Path


class MCPClient:
    """Client for communicating with an MCP server via stdio"""

    def __init__(self, server_name: str, config: dict):
        """
        Initialize MCP client for a specific server

        Args:
            server_name: Name of the MCP server
            config: Server configuration from .mcp.json
        """
        self.server_name = server_name
        self.config = config
        self.process = None
        self._request_id = 0
        self._start_server()

    def _start_server(self):
        """Start the MCP server process"""
        command = [self.config['command']] + self.config.get('args', [])
        env = os.environ.copy()
        env.update(self.config.get('env', {}))

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )

        # Wait for server to initialize (if configured)
        # Some servers (like patents-mcp-server) need time to load dependencies
        startup_delay = self.config.get('startup_delay', 0)
        if startup_delay > 0:
            import time
            time.sleep(startup_delay)

        # Initialize connection
        self._send_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'mcp-code-execution',
                'version': '1.0.0'
            }
        })

        # Send initialized notification (required by MCP protocol)
        # This is a notification (no response expected)
        initialized_notification = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        }
        self.process.stdin.write(json.dumps(initialized_notification) + '\n')
        self.process.stdin.flush()

    def _send_request(self, method: str, params: dict) -> dict:
        """Send JSON-RPC request to MCP server"""
        self._request_id += 1
        request = {
            'jsonrpc': '2.0',
            'id': self._request_id,
            'method': method,
            'params': params
        }

        # Send request
        request_json = json.dumps(request) + '\n'
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
        except BrokenPipeError as e:
            # Capture stderr for debugging
            stderr_output = ""
            if self.process.stderr:
                try:
                    # Non-blocking read of available stderr
                    import select
                    if select.select([self.process.stderr], [], [], 0)[0]:
                        stderr_output = self.process.stderr.read()
                except:
                    pass

            print(f"[MCP CLIENT ERROR] Subprocess stderr: {stderr_output}")
            raise

        # Read response (skip non-JSON lines like debug output)
        max_attempts = 10
        response_line = None

        for _ in range(max_attempts):
            line = self.process.stdout.readline()
            if not line:
                raise Exception(f"No response from MCP server {self.server_name}")

            line = line.strip()
            if not line:
                continue

            # Try to parse as JSON - skip non-JSON lines (debug output)
            try:
                response = json.loads(line)
                response_line = line
                break
            except json.JSONDecodeError:
                # This is likely debug output, skip it and try next line
                continue

        if not response_line:
            raise Exception(f"No valid JSON response from MCP server {self.server_name} after {max_attempts} attempts")

        # Check for errors
        if 'error' in response:
            raise Exception(f"MCP error: {response['error']}")

        return response.get('result', {})

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call an MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result (dict if JSON, str if text/markdown)
        """
        result = self._send_request('tools/call', {
            'name': tool_name,
            'arguments': arguments
        })

        # Extract content from MCP response
        if isinstance(result, dict) and 'content' in result:
            content = result['content']
            if isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict):
                    # Handle different content types
                    if 'text' in first_content:
                        text = first_content['text']
                        # Try to parse as JSON
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            # Return as text (markdown, etc.)
                            return {'text': text, 'format': 'text'}
                    elif 'data' in first_content:
                        return first_content['data']

        return result

    def list_tools(self) -> list:
        """List available tools from this MCP server"""
        result = self._send_request('tools/list', {})
        return result.get('tools', [])

    def close(self):
        """Close the MCP server connection"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


# Global client registry
_clients = {}
_config = None


def load_config():
    """Load MCP configuration from .mcp.json"""
    global _config
    if _config is None:
        # Find project root by looking for .mcp.json
        current = Path(__file__).resolve()
        while current != current.parent:
            config_path = current / '.mcp.json'
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)
                    _config = data.get('mcpServers', {})
                return _config
            current = current.parent

        # Fallback: check current working directory
        config_path = Path.cwd() / '.mcp.json'
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                _config = data.get('mcpServers', {})
        else:
            raise FileNotFoundError(f"Could not find .mcp.json in project tree")
    return _config


def get_client(server_name: str) -> MCPClient:
    """
    Get or create an MCP client for the specified server

    Args:
        server_name: Name of the MCP server (e.g., 'fda-mcp')

    Returns:
        MCPClient instance
    """
    if server_name not in _clients:
        config = load_config()
        if server_name not in config:
            raise ValueError(f"Unknown MCP server: {server_name}")

        _clients[server_name] = MCPClient(server_name, config[server_name])

    return _clients[server_name]


def close_all():
    """Close all MCP client connections"""
    for client in _clients.values():
        client.close()
    _clients.clear()
