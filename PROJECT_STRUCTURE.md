# Project Structure

This document describes the organized file structure of the README-MCP project.

## Directory Layout

```
readme-mcp/
├── src/
│   └── readme_mcp/          # Main application package
│       ├── __init__.py      # Package initialization
│       └── main.py          # FastAPI application and endpoints
├── tests/                   # Test files
│   ├── __init__.py         # Test package init
│   ├── test_readme.py      # Unit tests for endpoints
│   └── fixtures/           # VCR.py test fixtures (auto-generated)
├── scripts/                # Development and utility scripts
│   └── dev.py              # Development server script
├── .github/                # GitHub Actions CI/CD
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Dependency lock file
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── .gitignore             # Git ignore patterns
├── CLAUDE.md              # Claude Code instructions
├── DEVELOPMENT.md         # Development planning document
└── PROJECT_STRUCTURE.md   # This file
```

## Key Components

### Source Code (`src/readme_mcp/`)
- **`main.py`**: FastAPI application setup and configuration
- **`api.py`**: API endpoint handlers for `/readme` and `/file`
- **`github_client.py`**: GitHub API client with request handling and validation
- **`models.py`**: Pydantic request and response models with validation
- **`__init__.py`**: Package initialization with version information

### Tests (`tests/`)
- **`test_readme.py`**: Comprehensive unit tests for both `/readme` and `/file` endpoints
- **`fixtures/`**: Auto-generated VCR.py cassettes for HTTP request recording

### Scripts (`scripts/`)
- **`dev.py`**: Development server with auto-reload functionality
  - Usage: `python scripts/dev.py` or `uv run python scripts/dev.py`

### Configuration Files
- **`pyproject.toml`**: Project metadata, dependencies, build system, and tool configurations
- **`.pre-commit-config.yaml`**: Ruff linting/formatting and pytest execution hooks
- **`uv.lock`**: Pinned dependency versions for reproducible environments

## Development Workflow

1. **Install dependencies**: `uv sync --group dev`
2. **Run tests**: `uv run pytest tests/`
3. **Start dev server**: `python scripts/dev.py`
4. **Format code**: `uv run ruff format .`
5. **Lint code**: `uv run ruff check --fix .`
6. **Pre-commit hooks**: `pre-commit run --all-files`

## Build System

The project uses Hatchling as the build backend with the source code located in `src/readme_mcp/`. This provides:
- Clean separation of source and test code
- Proper package installation and imports
- Editable development installations
- Standard Python packaging structure