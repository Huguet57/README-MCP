#!/usr/bin/env python3
"""Tests for MCP server structure and tool definitions."""

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    return mock_response


def test_mcp_server_initialization():
    """Test that MCP server initializes correctly."""
    # Import the mcp instance from mcp_server
    import mcp_server
    
    assert isinstance(mcp_server.mcp, FastMCP)
    assert mcp_server.mcp.name == "readme-mcp"


def test_mcp_server_has_tools():
    """Test that MCP server has tools defined."""
    import mcp_server
    
    # Get all tools from the server
    tools = mcp_server.mcp._tool_manager.tools
    
    # Check that we have exactly 3 tools
    assert len(tools) == 3
    
    # Check tool names
    tool_names = {tool.name for tool in tools.values()}
    expected_tools = {"get_readme", "get_file", "list_directory"}
    assert tool_names == expected_tools


def test_tool_signatures():
    """Test that tools have correct signatures."""
    import mcp_server
    
    tools = mcp_server.mcp._tool_manager.tools
    
    # Test get_readme tool
    readme_tool = tools["get_readme"]
    assert readme_tool.name == "get_readme"
    assert readme_tool.description == "Get README content from a GitHub repository"
    
    # Check input schema
    input_schema = readme_tool.inputSchema
    assert input_schema["type"] == "object"
    assert "repo_url" in input_schema["properties"]
    assert "ref" in input_schema["properties"]
    assert "token" in input_schema["properties"]
    assert input_schema["required"] == ["repo_url"]
    
    # Test get_file tool
    file_tool = tools["get_file"]
    assert file_tool.name == "get_file"
    assert file_tool.description == "Get a specific file from a GitHub repository"
    assert "path" in file_tool.inputSchema["properties"]
    assert file_tool.inputSchema["required"] == ["repo_url", "path"]
    
    # Test list_directory tool
    ls_tool = tools["list_directory"]
    assert ls_tool.name == "list_directory"
    assert ls_tool.description == "List contents of a directory in a GitHub repository"
    assert "dir" in ls_tool.inputSchema["properties"]


@pytest.mark.asyncio
async def test_get_readme_tool_execution(mock_httpx_response):
    """Test get_readme tool execution with mocked HTTP client."""
    import mcp_server
    
    # Mock the response data
    mock_httpx_response.json.return_value = {
        "content": "# Test README\n\nThis is a test."
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        # Configure the mock client
        mock_context = AsyncMock()
        mock_context.post.return_value = mock_httpx_response
        mock_client.return_value.__aenter__.return_value = mock_context
        
        # Execute the tool
        result = await mcp_server.get_readme(
            repo_url="https://github.com/test/repo",
            ref="main"
        )
        
        # Verify the result
        assert result == "# Test README\n\nThis is a test."
        
        # Verify the HTTP call was made correctly
        mock_context.post.assert_called_once_with(
            "http://localhost:8000/readme",
            json={"repo_url": "https://github.com/test/repo", "ref": "main", "token": None},
            timeout=30,
        )


@pytest.mark.asyncio
async def test_get_file_tool_execution(mock_httpx_response):
    """Test get_file tool execution with mocked HTTP client."""
    import mcp_server
    
    # Mock the response data
    mock_httpx_response.json.return_value = {
        "content": "print('Hello, world!')"
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        # Configure the mock client
        mock_context = AsyncMock()
        mock_context.post.return_value = mock_httpx_response
        mock_client.return_value.__aenter__.return_value = mock_context
        
        # Execute the tool
        result = await mcp_server.get_file(
            repo_url="https://github.com/test/repo",
            path="main.py",
            ref="main"
        )
        
        # Verify the result
        assert result == "print('Hello, world!')"
        
        # Verify the HTTP call was made correctly
        mock_context.post.assert_called_once_with(
            "http://localhost:8000/file",
            json={
                "repo_url": "https://github.com/test/repo",
                "path": "main.py",
                "ref": "main",
                "token": None
            },
            timeout=30,
        )


@pytest.mark.asyncio
async def test_list_directory_tool_execution(mock_httpx_response):
    """Test list_directory tool execution with mocked HTTP client."""
    import mcp_server
    
    # Mock the response data
    mock_httpx_response.json.return_value = {
        "entries": [
            {"type": "file", "name": "README.md", "size": 1234},
            {"type": "dir", "name": "src"},
            {"type": "file", "name": "setup.py", "size": 567}
        ],
        "total_count": 3
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        # Configure the mock client
        mock_context = AsyncMock()
        mock_context.post.return_value = mock_httpx_response
        mock_client.return_value.__aenter__.return_value = mock_context
        
        # Execute the tool
        result = await mcp_server.list_directory(
            repo_url="https://github.com/test/repo",
            dir="",
            ref="main"
        )
        
        # Verify the result format
        assert "Directory listing for root (3 entries):" in result
        assert "📄 README.md (1234 bytes)" in result
        assert "📁 src" in result
        assert "📄 setup.py (567 bytes)" in result
        
        # Verify the HTTP call was made correctly
        mock_context.post.assert_called_once_with(
            "http://localhost:8000/ls",
            json={
                "repo_url": "https://github.com/test/repo",
                "dir": "",
                "ref": "main",
                "token": None
            },
            timeout=30,
        )


@pytest.mark.asyncio
async def test_error_handling(mock_httpx_response):
    """Test error handling in MCP tools."""
    import mcp_server
    
    # Mock a 404 error
    mock_httpx_response.status_code = 404
    mock_httpx_response.text = "Repository not found"
    mock_httpx_response.raise_for_status.side_effect = Exception("HTTP 404: Repository not found")
    
    with patch("httpx.AsyncClient") as mock_client:
        # Configure the mock client
        mock_context = AsyncMock()
        mock_context.post.return_value = mock_httpx_response
        mock_client.return_value.__aenter__.return_value = mock_context
        
        # Execute the tool and expect an error
        with pytest.raises(RuntimeError) as exc_info:
            await mcp_server.get_readme(
                repo_url="https://github.com/test/nonexistent"
            )
        
        assert "HTTP 404" in str(exc_info.value)


def test_mcp_server_can_run():
    """Test that MCP server can be run as a script."""
    import mcp_server
    
    # Check that __main__ block exists
    assert hasattr(mcp_server, "__name__")
    
    # The server should be runnable
    # This just checks the structure, not actual execution
    assert hasattr(mcp_server.mcp, "run")


if __name__ == "__main__":
    # Run a quick sanity check
    test_mcp_server_initialization()
    test_mcp_server_has_tools()
    test_tool_signatures()
    print("✅ Basic MCP server structure tests passed!")