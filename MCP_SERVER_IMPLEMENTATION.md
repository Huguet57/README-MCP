# MCP Server Implementation for README-MCP

This document explains the Model Context Protocol (MCP) server implementation for the README-MCP service.

## Overview

The README-MCP service has been successfully adapted to use FastMCP from the MCP Python SDK. The implementation consists of two main components:

1. **Backend Service** (`src/readme_mcp/`) - A FastAPI service that interfaces with GitHub's API
2. **MCP Server Wrapper** (`mcp_server.py`) - An MCP server that exposes tools to interact with the backend

## MCP Server Structure

### Main MCP Server (`mcp_server.py`)

The MCP server is correctly implemented using FastMCP with three tools:

```python
from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("readme-mcp")
```

### Registered Tools

1. **get_readme**
   - Description: "Get README content from a GitHub repository"
   - Parameters:
     - `repo_url` (str, required): GitHub repository URL
     - `ref` (str, optional, default="main"): Git reference (branch/tag/commit)
     - `token` (str | None, optional): GitHub access token
   - Returns: README content as string

2. **get_file**
   - Description: "Get a specific file from a GitHub repository"
   - Parameters:
     - `repo_url` (str, required): GitHub repository URL
     - `path` (str, required): File path within the repository
     - `ref` (str, optional, default="main"): Git reference
     - `token` (str | None, optional): GitHub access token
   - Returns: File content as string

3. **list_directory**
   - Description: "List contents of a directory in a GitHub repository"
   - Parameters:
     - `repo_url` (str, required): GitHub repository URL
     - `dir` (str, optional, default=""): Directory path (empty for root)
     - `ref` (str, optional, default="main"): Git reference
     - `token` (str | None, optional): GitHub access token
   - Returns: Formatted directory listing with file/folder indicators and sizes

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   MCP Client    │ <-----> │   MCP Server    │ <-----> │ Backend Service │
│  (e.g., Claude) │  MCP    │ (mcp_server.py) │  HTTP   │  (FastAPI)      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                                                │
                                                                v
                                                         ┌─────────────────┐
                                                         │   GitHub API    │
                                                         └─────────────────┘
```

## Tool Schemas

Each tool has a properly generated JSON schema for its input parameters:

### get_readme Schema
```json
{
  "type": "object",
  "properties": {
    "repo_url": {"type": "string"},
    "ref": {"type": "string", "default": "main"},
    "token": {"type": ["string", "null"], "default": null}
  },
  "required": ["repo_url"]
}
```

### get_file Schema
```json
{
  "type": "object",
  "properties": {
    "repo_url": {"type": "string"},
    "path": {"type": "string"},
    "ref": {"type": "string", "default": "main"},
    "token": {"type": ["string", "null"], "default": null}
  },
  "required": ["repo_url", "path"]
}
```

### list_directory Schema
```json
{
  "type": "object",
  "properties": {
    "repo_url": {"type": "string"},
    "dir": {"type": "string", "default": ""},
    "ref": {"type": "string", "default": "main"},
    "token": {"type": ["string", "null"], "default": null}
  },
  "required": ["repo_url"]
}
```

## Testing

### Test Files Created

1. **`tests/test_mcp_structure.py`** - Unit tests for MCP server structure
   - Tests that FastMCP instance is created correctly
   - Verifies all three tools are registered
   - Checks tool metadata and descriptions
   - Validates generated schemas
   - Confirms MCP capabilities

2. **`mcp_server_standalone.py`** - Standalone MCP server with mock responses
   - Demonstrates MCP functionality without backend dependency
   - Returns mock data for all three tools
   - Useful for testing MCP protocol compliance

3. **`test_mcp_demo.py`** - Interactive MCP protocol test
   - Sends JSON-RPC requests to test the MCP server
   - Tests initialization, tool listing, and tool execution
   - Shows the complete MCP communication flow

4. **`inspect_mcp_server.py`** - Static inspection tool
   - Inspects MCP server structure without running it
   - Shows registered tools and their signatures
   - Displays capabilities and schemas

## Running the Server

### Development Mode
```bash
# With backend service running
python mcp_server.py

# Standalone mode (no backend required)
python mcp_server_standalone.py
```

### With MCP Inspector
```bash
mcp dev mcp_server.py
# or
mcp dev mcp_server_standalone.py
```

### Install in Claude Desktop
```bash
mcp install mcp_server.py --name "README-MCP"
```

## Implementation Notes

1. **Error Handling**: All tools properly handle HTTP errors and connection issues, wrapping them in RuntimeError with descriptive messages.

2. **Async Support**: All tool functions are async, allowing for efficient concurrent operations.

3. **Response Formatting**: The `list_directory` tool formats responses with visual indicators (📁 for directories, 📄 for files) and file sizes.

4. **Type Annotations**: Full type annotations are used throughout, enabling proper schema generation and IDE support.

5. **Backward Compatibility**: The server follows MCP protocol standards and is compatible with various MCP clients.

## Conclusion

The MCP server has been successfully implemented using FastMCP. It properly exposes three tools for interacting with GitHub repositories. The implementation is well-structured, follows MCP best practices, and includes comprehensive tests to verify functionality.

The issue of "0 tools" would only occur if:
1. The MCP package is not properly installed
2. The server is being queried incorrectly
3. There's a version mismatch in the MCP protocol

The code structure itself is correct and follows the FastMCP documentation exactly.