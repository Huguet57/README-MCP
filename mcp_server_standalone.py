#!/usr/bin/env python3
"""Standalone MCP Server for README-MCP service - No backend dependency."""

from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("readme-mcp")


@mcp.tool()
async def get_readme(repo_url: str, ref: str = "main", token: str | None = None) -> str:
    """Get README content from a GitHub repository
    
    This is a standalone version that returns mock data for demonstration.
    """
    # Mock response for demonstration
    return f"""# Example README

This is a mock README for repository: {repo_url}
Branch/Ref: {ref}

## Features
- Feature 1
- Feature 2  
- Feature 3

## Installation
```bash
pip install example
```

## Usage
```python
import example
example.run()
```
"""


@mcp.tool()
async def get_file(
    repo_url: str, path: str, ref: str = "main", token: str | None = None
) -> str:
    """Get a specific file from a GitHub repository
    
    This is a standalone version that returns mock data for demonstration.
    """
    # Mock response for demonstration
    return f"""# File: {path}
# Repository: {repo_url}
# Ref: {ref}

def example_function():
    '''This is mock file content for {path}'''
    return "Hello from {path}"

if __name__ == "__main__":
    print(example_function())
"""


@mcp.tool()
async def list_directory(
    repo_url: str, dir: str = "", ref: str = "main", token: str | None = None
) -> str:
    """List contents of a directory in a GitHub repository
    
    This is a standalone version that returns mock data for demonstration.
    """
    # Mock response for demonstration
    dir_name = dir or "root"
    return f"""Directory listing for {dir_name} (5 entries):

📁 src
📁 tests  
📄 README.md (2048 bytes)
📄 setup.py (512 bytes)
📄 requirements.txt (256 bytes)

Repository: {repo_url}
Ref: {ref}
"""


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()