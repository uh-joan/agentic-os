# Installing Playwright MCP Server

This skill requires the Microsoft Playwright MCP server for web scraping JavaScript-rendered pharmaceutical pipeline pages.

## Prerequisites

- Node.js (v18 or later)
- npm or npx

## Installation Steps

### 1. Install Playwright MCP Server

The Playwright MCP server is installed via npx (no manual installation needed):

```bash
# Test installation
npx @playwright/mcp --help
```

### 2. Verify .mcp.json Configuration

Ensure `.mcp.json` includes the playwright-mcp server:

```json
{
  "mcpServers": {
    "playwright-mcp": {
      "command": "npx",
      "args": [
        "@playwright/mcp"
      ],
      "env": {}
    }
  }
}
```

This has already been added to the configuration.

### 3. Restart Claude Code

After adding the configuration, restart Claude Code to load the Playwright MCP server:

1. Exit Claude Code completely
2. Relaunch Claude Code
3. The Playwright MCP server will start automatically

### 4. Verify MCP Tools Available

You can verify the Playwright MCP tools are available by asking Claude Code:

```
What MCP tools are available from playwright-mcp?
```

Expected tools:
- `playwright_navigate` - Navigate browser to URL
- `playwright_screenshot` - Take page screenshot
- `playwright_click` - Click on element
- `playwright_fill` - Fill form input
- `playwright_evaluate` - Execute JavaScript
- `playwright_content` - Get page HTML content

## Usage in Skills

### For pharma-search-specialist Agent

When creating web scraping skills, the pharma-search-specialist agent will generate code that uses these MCP tools directly through Claude Code's MCP integration.

Example pattern:
```python
# Agent-generated code will use available MCP tools during execution
# Example flow:
# 1. Navigate to pipeline URL using playwright_navigate
# 2. Wait for page load
# 3. Get page content using playwright_content
# 4. Parse HTML with BeautifulSoup
```

### Snapshot Capability

The key advantage of Playwright MCP is snapshot support for complex dynamic pipelines:

```
Use playwright_screenshot to capture page state
→ Useful for debugging scraping issues
→ Can verify JavaScript rendering completed
→ Visual confirmation of page structure
```

## Troubleshooting

### Issue: Playwright MCP not found

**Error**: `Server 'playwright-mcp' not found`

**Fix**:
1. Verify `.mcp.json` configuration is correct
2. Restart Claude Code
3. Check npx can run: `npx @playwrighthq/mcp-server --help`

### Issue: Chromium browser not found

**Error**: `Browser not found`

**Fix**: Playwright will auto-download browsers on first use. If issues persist:
```bash
npx playwright install chromium
```

### Issue: Permission errors

**Error**: `EACCES: permission denied`

**Fix**: Check npm permissions or use nvm to manage Node.js locally:
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use Node.js
nvm install 18
nvm use 18
```

## Alternative: Playwright MCP from Source

If you need to customize the Playwright MCP server:

```bash
# Clone Microsoft's Playwright MCP server
git clone https://github.com/microsoft/playwright-mcp.git
cd playwright-mcp

# Install dependencies
npm install

# Build
npm run build

# Update .mcp.json to point to local build
"playwright-mcp": {
  "command": "node",
  "args": ["/path/to/playwright-mcp/dist/index.js"]
}
```

## References

- **Playwright MCP GitHub**: https://github.com/microsoft/playwright-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Playwright Docs**: https://playwright.dev/
