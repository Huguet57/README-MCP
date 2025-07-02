# README-MCP Service

A Model Context Protocol (MCP) server and FastAPI service for retrieving GitHub repository documentation. This service provides both a REST API and MCP tools for AI assistants to access README files, specific files, and directory listings from GitHub repositories.

## Features

- **MCP Server**: Exposes tools for AI assistants via the Model Context Protocol
- **REST API**: Direct HTTP endpoints for programmatic access
- **GitHub Integration**: Fetch README files, arbitrary files, and directory listings
- **Secure**: URL validation, path traversal protection, and optional authentication

## Architecture

The service consists of two main components:

1. **MCP Server** (`mcp_server.py`): Provides tools for AI assistants using FastMCP
2. **FastAPI Backend** (`src/readme_mcp/`): REST API that interfaces with GitHub

## Quick Start

### Install Dependencies

```bash
# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Running the Services

#### 1. Start the FastAPI Backend

```bash
# Run the development server
uv run uvicorn readme_mcp.main:app --reload --host 0.0.0.0 --port 8000

# Or use the dev script
uv run python scripts/dev.py
```

#### 2. Run the MCP Server

```bash
# Run MCP server (requires backend to be running)
uv run python mcp_server.py

# Or use the standalone version (no backend required)
uv run python mcp_server_standalone.py
```

### Testing with MCP Inspector

```bash
# Test the MCP server with the inspector
mcp dev mcp_server.py

# Or test the standalone version
mcp dev mcp_server_standalone.py
```

### Install in Claude Desktop

```bash
mcp install mcp_server.py --name "README-MCP"
```

## MCP Tools

The MCP server exposes three tools:

### 1. `get_readme`
Retrieves the README file from a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL
- `ref` (optional): Git reference (branch/tag/commit), defaults to "main"
- `token` (optional): GitHub access token for private repos

### 2. `get_file`
Retrieves a specific file from a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL
- `path` (required): File path within the repository
- `ref` (optional): Git reference, defaults to "main"
- `token` (optional): GitHub access token

### 3. `list_directory`
Lists the contents of a directory in a GitHub repository.

**Parameters:**
- `repo_url` (required): GitHub repository URL
- `dir` (optional): Directory path (empty for root)
- `ref` (optional): Git reference, defaults to "main"
- `token` (optional): GitHub access token

## REST API Endpoints

### POST /readme

Retrieve the README file from a GitHub repository.

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "ref": "main",
  "token": "optional_github_token"
}
```

**Response:**
```json
{
  "content": "# Repository Title\n\nDescription...",
  "name": "README.md",
  "path": "README.md", 
  "sha": "abc123...",
  "size": 1639,
  "encoding": "base64",
  "download_url": "https://raw.githubusercontent.com/..."
}
```

### POST /file

Retrieve a specific file from a GitHub repository.

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "path": "src/main.py",
  "ref": "main",
  "token": "optional_github_token"
}
```

### POST /ls

List directory contents from a GitHub repository.

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "dir": "src",
  "ref": "main",
  "token": "optional_github_token"
}
```

## Example Usage

### Using the MCP Server with Claude

Once installed in Claude Desktop, you can use natural language:

```
"Get the README from github.com/pallets/flask"
"Show me the setup.py file from github.com/django/django"
"List the files in the docs directory of github.com/python/cpython"
```

### Using the REST API

```bash
# Get README
curl -X POST "http://localhost:8000/readme" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "ref": "main"
  }'

# Get specific file
curl -X POST "http://localhost:8000/file" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "path": "setup.py"
  }'

# List directory
curl -X POST "http://localhost:8000/ls" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "dir": "src"
  }'
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_mcp_structure.py -v
uv run pytest tests/test_mcp_server.py -v

# Test the example
uv run python run_example.py
```

## Security Features

- URL validation against GitHub repository format
- Path traversal protection
- Input validation with Pydantic
- Optional authentication token support
- Rate limiting inherited from GitHub API

## Deployment

See the `deploy/` directory for deployment configurations:
- `kubernetes.yaml` - Kubernetes deployment
- `cloud-run.yaml` - Google Cloud Run
- `digitalocean.yaml` - DigitalOcean App Platform
- `docker-compose.yml` - Docker Compose setup

## Development

For detailed development information, see:
- `DEVELOPMENT.md` - Development plan and architecture
- `MCP_SERVER_IMPLEMENTATION.md` - MCP server implementation details
- `PROJECT_STRUCTURE.md` - Project file structure