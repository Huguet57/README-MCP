# Project Structure

This document describes the organized file structure of the README-MCP project.

## Directory Layout

```
readme-mcp/
├── src/
│   └── readme_mcp/          # Main application package
│       ├── __init__.py      # Package initialization
│       ├── main.py          # FastAPI application and endpoints
│       ├── api.py           # API endpoint handlers
│       ├── github_client.py # GitHub API client
│       └── models.py        # Pydantic models
├── tests/                   # Test files
│   ├── __init__.py          # Test package init
│   ├── test_readme.py       # Unit tests for endpoints
│   ├── test_mcp_server.py   # MCP server protocol tests
│   ├── test_mcp_simple.py   # Simple MCP functionality tests
│   ├── test_mcp_protocol.py # MCP protocol compliance tests
│   ├── test_mcp_structure.py # MCP server structure tests
│   └── fixtures/            # VCR.py test fixtures (auto-generated)
├── scripts/                 # Development and utility scripts
│   └── dev.py               # Development server script
├── deploy/                  # Deployment configurations
│   ├── kubernetes.yaml      # Kubernetes deployment
│   ├── cloud-run.yaml       # Google Cloud Run config
│   └── digitalocean.yaml    # DigitalOcean App Platform
├── schemas/                 # Schema definitions
├── .github/                 # GitHub Actions CI/CD
├── mcp_server.py           # MCP server implementation
├── mcp_server_standalone.py # Standalone MCP server (no backend)
├── mcp_config.json         # MCP configuration for Claude Desktop
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── Makefile                # Build and deployment commands
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Dependency lock file
├── ruff.toml               # Ruff linter configuration
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── .gitignore              # Git ignore patterns
├── README.md               # Project documentation
├── CLAUDE.md               # Claude Code instructions
├── DEVELOPMENT.md          # Development planning document
├── DEPLOYMENT.md           # Deployment guide
├── MCP_SERVER_IMPLEMENTATION.md # MCP server details
├── PROJECT_STRUCTURE.md    # This file
├── example.py              # Example usage script
└── run_example.py          # Example runner script
```

## Key Components

### MCP Server (`mcp_server.py`, `mcp_server_standalone.py`)
- **`mcp_server.py`**: Main MCP server that wraps the FastAPI backend
  - Exposes three tools: `get_readme`, `get_file`, `list_directory`
  - Requires backend service to be running at `http://localhost:8000`
- **`mcp_server_standalone.py`**: Standalone version with mock responses
  - Same tools but returns mock data for testing
  - No backend dependency

### Source Code (`src/readme_mcp/`)
- **`main.py`**: FastAPI application setup and configuration
- **`api.py`**: API endpoint handlers for `/readme`, `/file`, and `/ls`
- **`github_client.py`**: GitHub API client with request handling and validation
- **`models.py`**: Pydantic request and response models with validation
- **`__init__.py`**: Package initialization with version information

### Tests (`tests/`)
- **`test_readme.py`**: Comprehensive unit tests for API endpoints
- **`test_mcp_server.py`**: MCP server tool discovery and invocation tests
- **`test_mcp_simple.py`**: Basic MCP functionality verification
- **`test_mcp_protocol.py`**: MCP protocol compliance tests
- **`test_mcp_structure.py`**: Tests for MCP server structure without backend
- **`fixtures/`**: Auto-generated VCR.py cassettes for HTTP request recording

### Scripts (`scripts/`)
- **`dev.py`**: Development server with auto-reload functionality
  - Usage: `python scripts/dev.py` or `uv run python scripts/dev.py`

### Deployment (`deploy/`)
- **`kubernetes.yaml`**: Kubernetes deployment with 3 replicas, health checks
- **`cloud-run.yaml`**: Google Cloud Run serverless deployment
- **`digitalocean.yaml`**: DigitalOcean App Platform configuration
- **`docker-compose.yml`**: Local development with Redis cache

### Configuration Files
- **`pyproject.toml`**: Project metadata, dependencies, build system, and tool configurations
- **`mcp_config.json`**: MCP configuration for Claude Desktop integration
- **`ruff.toml`**: Ruff linter settings
- **`.pre-commit-config.yaml`**: Ruff linting/formatting and pytest execution hooks
- **`uv.lock`**: Pinned dependency versions for reproducible environments

## Development Workflow

1. **Install dependencies**: `uv sync --group dev`
2. **Run backend service**: `uv run python scripts/dev.py`
3. **Run MCP server**: `uv run python mcp_server.py`
4. **Run tests**: `uv run pytest tests/`
5. **Test with MCP Inspector**: `mcp dev mcp_server.py`
6. **Install in Claude Desktop**: `mcp install mcp_server.py`
7. **Format code**: `uv run ruff format .`
8. **Lint code**: `uv run ruff check --fix .`
9. **Pre-commit hooks**: `pre-commit run --all-files`

## Build System

The project uses Hatchling as the build backend with the source code located in `src/readme_mcp/`. This provides:
- Clean separation of source and test code
- Proper package installation and imports
- Editable development installations
- Standard Python packaging structure

## MCP Integration

The project implements the Model Context Protocol (MCP) to provide AI assistants with tools for accessing GitHub repository documentation. The MCP server can be used with:
- Claude Desktop (via `mcp install`)
- MCP Inspector (via `mcp dev`)
- Any MCP-compatible client