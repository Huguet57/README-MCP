"""Simple tests for MCP server functionality."""

import inspect

from mcp_server import get_file, get_readme, list_directory, mcp


class TestMCPSimple:
    """Simple tests for MCP setup verification."""

    def test_mcp_server_exists(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "run")

    def test_tool_functions_exist(self):
        """Test that all tool functions are defined."""
        assert callable(get_readme)
        assert callable(get_file)
        assert callable(list_directory)

    def test_tool_function_signatures(self):
        """Test that tool functions have correct signatures."""
        # Check get_readme signature
        readme_sig = inspect.signature(get_readme)
        readme_params = list(readme_sig.parameters.keys())
        assert "repo_url" in readme_params
        assert "ref" in readme_params
        assert "token" in readme_params

        # Check get_file signature
        file_sig = inspect.signature(get_file)
        file_params = list(file_sig.parameters.keys())
        assert "repo_url" in file_params
        assert "path" in file_params
        assert "ref" in file_params
        assert "token" in file_params

        # Check list_directory signature
        dir_sig = inspect.signature(list_directory)
        dir_params = list(dir_sig.parameters.keys())
        assert "repo_url" in dir_params
        assert "dir" in dir_params
        assert "ref" in dir_params
        assert "token" in dir_params

    def test_tool_function_defaults(self):
        """Test that tool functions have correct default values."""
        # Check get_readme defaults
        readme_sig = inspect.signature(get_readme)
        assert readme_sig.parameters["ref"].default == "main"
        assert readme_sig.parameters["token"].default is None

        # Check get_file defaults
        file_sig = inspect.signature(get_file)
        assert file_sig.parameters["ref"].default == "main"
        assert file_sig.parameters["token"].default is None

        # Check list_directory defaults
        dir_sig = inspect.signature(list_directory)
        assert dir_sig.parameters["dir"].default == ""
        assert dir_sig.parameters["ref"].default == "main"
        assert dir_sig.parameters["token"].default is None

    def test_tool_function_annotations(self):
        """Test that tool functions have correct type annotations."""
        # Check get_readme annotations
        readme_sig = inspect.signature(get_readme)
        assert readme_sig.return_annotation is str
        assert readme_sig.parameters["repo_url"].annotation is str
        assert readme_sig.parameters["ref"].annotation is str
        assert readme_sig.parameters["token"].annotation == str | None

        # Check get_file annotations
        file_sig = inspect.signature(get_file)
        assert file_sig.return_annotation is str
        assert file_sig.parameters["repo_url"].annotation is str
        assert file_sig.parameters["path"].annotation is str
        assert file_sig.parameters["ref"].annotation is str
        assert file_sig.parameters["token"].annotation == str | None

        # Check list_directory annotations
        dir_sig = inspect.signature(list_directory)
        assert dir_sig.return_annotation is str
        assert dir_sig.parameters["repo_url"].annotation is str
        assert dir_sig.parameters["dir"].annotation is str
        assert dir_sig.parameters["ref"].annotation is str
        assert dir_sig.parameters["token"].annotation == str | None

    def test_tool_decorators_applied(self):
        """Test that @mcp.tool() decorators are applied."""
        # Check if functions are properly decorated
        # FastMCP should add metadata to decorated functions
        assert hasattr(get_readme, "__annotations__")
        assert hasattr(get_file, "__annotations__")
        assert hasattr(list_directory, "__annotations__")

    def test_tool_docstrings(self):
        """Test that tool functions have docstrings."""
        assert get_readme.__doc__ is not None
        assert "README" in get_readme.__doc__

        assert get_file.__doc__ is not None
        assert "file" in get_file.__doc__

        assert list_directory.__doc__ is not None
        assert "directory" in list_directory.__doc__
