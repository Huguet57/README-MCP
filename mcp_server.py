#!/usr/bin/env python3
"""MCP Server wrapper for README-MCP service."""

import httpx
from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("readme-mcp")
BASE_URL = "http://localhost:8000"


@mcp.tool()
async def get_readme(repo_url: str, ref: str = "main", token: str | None = None) -> str:
    """Get README content from a GitHub repository"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/readme",
                json={"repo_url": repo_url, "ref": ref, "token": token},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error: {str(e)}") from e


@mcp.tool()
async def get_file(
    repo_url: str, path: str, ref: str = "main", token: str | None = None
) -> str:
    """Get a specific file from a GitHub repository"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/file",
                json={"repo_url": repo_url, "path": path, "ref": ref, "token": token},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error: {str(e)}") from e


@mcp.tool()
async def list_directory(
    repo_url: str, dir: str = "", ref: str = "main", token: str | None = None
) -> str:
    """List contents of a directory in a GitHub repository"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/ls",
                json={"repo_url": repo_url, "dir": dir, "ref": ref, "token": token},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Format directory listing
            entries = data["entries"]
            formatted_entries = []
            for entry in entries:
                type_indicator = "📁" if entry["type"] == "dir" else "📄"
                size_info = (
                    f" ({entry.get('size', 0)} bytes)"
                    if entry["type"] == "file"
                    else ""
                )
                formatted_entries.append(f"{type_indicator} {entry['name']}{size_info}")

            result = f"Directory listing for {dir or 'root'} ({data['total_count']} entries):\n\n"
            result += "\n".join(formatted_entries)

            return result
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error: {str(e)}") from e


if __name__ == "__main__":
    mcp.run()
