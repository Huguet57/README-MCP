# MCP Server for README-MCP

This MCP (Model Context Protocol) server provides tools for AI assistants to interact with GitHub repositories, specifically for fetching README files, retrieving specific files, and listing directory contents.

## Architecture

The project consists of two components:

1. **Backend FastAPI Service** (`src/readme_mcp/`): Handles the actual GitHub API interactions
2. **MCP Server Wrapper** (`mcp_server.py`): Exposes the backend functionality as MCP tools

## MCP Tools

The server exposes three tools:

### 1. `get_readme`
Fetches the README content from a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL (e.g., `https://github.com/owner/repo`)
- `ref` (optional): Git reference (branch, tag, or commit) - defaults to "main"
- `token` (optional): GitHub access token for private repositories

**Returns:** The decoded README content as a string

### 2. `get_file`
Retrieves a specific file from a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL
- `path` (required): Path to the file within the repository
- `ref` (optional): Git reference - defaults to "main"
- `token` (optional): GitHub access token

**Returns:** The file content as a string

### 3. `list_directory`
Lists the contents of a directory in a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL
- `dir` (optional): Directory path (empty string for root) - defaults to ""
- `ref` (optional): Git reference - defaults to "main"
- `token` (optional): GitHub access token

**Returns:** Formatted directory listing with file/folder indicators and sizes

## Setup and Usage

### Prerequisites

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Start the backend service:
   ```bash
   uv run uvicorn readme_mcp.main:app --reload
   ```

### Running the MCP Server

Once the backend is running, you can start the MCP server:

```bash
uv run python mcp_server.py
```

### Testing with MCP Inspector

To test the server with the MCP Inspector:

```bash
uv run mcp dev mcp_server.py
```

### Installing in Claude Desktop

To install the server in Claude Desktop:

```bash
uv run mcp install mcp_server.py --name "GitHub README MCP"
```

## Example Usage

When connected to an AI assistant, you can use natural language to interact with the tools:

- "Get the README from the Flask repository"
- "Show me the setup.py file from pallets/flask"
- "List the contents of the src directory in the Flask repo"

## Testing

Run the tests to verify the MCP server structure:

```bash
uv run pytest tests/test_mcp_server.py -v
```

## How It Works

1. The MCP server (`mcp_server.py`) uses FastMCP to define tools
2. Each tool makes HTTP requests to the backend FastAPI service
3. The backend service handles GitHub API interactions
4. Results are formatted and returned to the AI assistant

This architecture separates concerns:
- The backend handles GitHub API complexity, rate limiting, and caching
- The MCP server provides a clean interface for AI assistants
- The two components can be deployed and scaled independently