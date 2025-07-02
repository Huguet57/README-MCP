"""Test MCP server structure and tool registration."""

import pytest
from mcp.server.fastmcp import FastMCP
import mcp_server


class TestMCPStructure:
    """Test MCP server structure without requiring backend service."""

    def test_mcp_server_instance(self):
        """Test that MCP server is properly instantiated."""
        assert isinstance(mcp_server.mcp, FastMCP)
        assert mcp_server.mcp.name == "readme-mcp"

    def test_tools_registered(self):
        """Test that tools are properly registered with FastMCP."""
        # Get the tools from the FastMCP instance
        tools = mcp_server.mcp._tool_handlers
        
        # Verify all three tools are registered
        assert len(tools) == 3
        assert "get_readme" in tools
        assert "get_file" in tools  
        assert "list_directory" in tools

    def test_tool_metadata(self):
        """Test that tools have proper metadata."""
        tools = mcp_server.mcp._tool_handlers
        
        # Check get_readme metadata
        readme_handler = tools["get_readme"]
        assert readme_handler.description == "Get README content from a GitHub repository"
        
        # Check get_file metadata
        file_handler = tools["get_file"]
        assert file_handler.description == "Get a specific file from a GitHub repository"
        
        # Check list_directory metadata
        dir_handler = tools["list_directory"]
        assert dir_handler.description == "List contents of a directory in a GitHub repository"

    def test_tool_schemas(self):
        """Test that tool schemas are properly generated."""
        # This will generate the schemas from the function signatures
        tool_infos = mcp_server.mcp.list_tools()
        
        # Convert to dict for easier testing
        tool_dict = {tool.name: tool for tool in tool_infos}
        
        # Verify get_readme schema
        readme_tool = tool_dict["get_readme"]
        assert readme_tool.inputSchema["type"] == "object"
        assert "repo_url" in readme_tool.inputSchema["properties"]
        assert "ref" in readme_tool.inputSchema["properties"]
        assert "token" in readme_tool.inputSchema["properties"]
        assert readme_tool.inputSchema["required"] == ["repo_url"]
        
        # Verify get_file schema  
        file_tool = tool_dict["get_file"]
        assert file_tool.inputSchema["type"] == "object"
        assert "repo_url" in file_tool.inputSchema["properties"]
        assert "path" in file_tool.inputSchema["properties"]
        assert "ref" in file_tool.inputSchema["properties"]
        assert "token" in file_tool.inputSchema["properties"]
        assert set(file_tool.inputSchema["required"]) == {"repo_url", "path"}
        
        # Verify list_directory schema
        dir_tool = tool_dict["list_directory"]
        assert dir_tool.inputSchema["type"] == "object"
        assert "repo_url" in dir_tool.inputSchema["properties"]
        assert "dir" in dir_tool.inputSchema["properties"]
        assert "ref" in dir_tool.inputSchema["properties"]
        assert "token" in dir_tool.inputSchema["properties"]
        assert dir_tool.inputSchema["required"] == ["repo_url"]

    def test_mcp_capabilities(self):
        """Test that MCP server reports correct capabilities."""
        capabilities = mcp_server.mcp.get_capabilities()
        
        # Should have tools capability
        assert hasattr(capabilities, "tools")
        assert capabilities.tools is not None
        
        # Should not have resources or prompts unless defined
        assert not hasattr(capabilities, "resources") or capabilities.resources is None
        assert not hasattr(capabilities, "prompts") or capabilities.prompts is None