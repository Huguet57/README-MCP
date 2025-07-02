# README-MCP Service

A minimal FastAPI service that exposes the `/readme` endpoint for retrieving GitHub repository README files.

## Quick Start

```bash
# Install dependencies with uv
uv sync

# Run the development server
uv run uvicorn main:app --reload

# Test with Flask repository
uv run python run_example.py

# Run tests
uv run pytest test_readme.py -v
```

## API Usage

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

## Example

```bash
curl -X POST "http://localhost:8000/readme" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "ref": "main"
  }'
```

## Security Features

- URL validation against GitHub repository format
- Path traversal protection
- Input validation with Pydantic
- Optional authentication token support