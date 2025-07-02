"""Integration tests for MCP server with mocked HTTP responses."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_server import get_file, get_readme, list_directory


class TestMCPIntegration:
    """Test MCP server with actual tool calls using mocked responses."""

    @pytest.mark.asyncio
    async def test_get_readme_tool_direct(self):
        """Test get_readme tool function directly with mocked HTTP."""
        mock_response_data = {"content": "# Test README\nThis is a test repository."}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await get_readme("https://github.com/test/repo")

            assert result == "# Test README\nThis is a test repository."
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                "http://localhost:8000/readme",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "ref": "main",
                    "token": None,
                },
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_get_file_tool_direct(self):
        """Test get_file tool function directly with mocked HTTP."""
        mock_response_data = {"content": "print('Hello, World!')"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await get_file("https://github.com/test/repo", "main.py")

            assert result == "print('Hello, World!')"
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                "http://localhost:8000/file",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "path": "main.py",
                    "ref": "main",
                    "token": None,
                },
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_list_directory_tool_direct(self):
        """Test list_directory tool function directly with mocked HTTP."""
        mock_response_data = {
            "entries": [
                {"name": "README.md", "type": "file", "size": 1234},
                {"name": "src", "type": "dir"},
                {"name": "tests", "type": "dir"},
            ],
            "total_count": 3,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await list_directory("https://github.com/test/repo")

            expected_result = (
                "Directory listing for root (3 entries):\n\n"
                "📄 README.md (1234 bytes)\n"
                "📁 src\n"
                "📁 tests"
            )
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_error_handling_http_error(self):
        """Test error handling when HTTP request fails."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"

            http_error = httpx.HTTPStatusError(
                "404 Not Found", request=AsyncMock(), response=mock_response
            )
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                http_error
            )

            with pytest.raises(RuntimeError) as exc_info:
                await get_readme("https://github.com/nonexistent/repo")

            assert "HTTP 404: Not Found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_handling_network_error(self):
        """Test error handling when network request fails."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                httpx.ConnectError("Connection failed")
            )

            with pytest.raises(RuntimeError) as exc_info:
                await get_readme("https://github.com/test/repo")

            assert "Error: Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test that tools validate parameters correctly."""
        # Test missing required parameter
        with pytest.raises(TypeError):
            await get_file("https://github.com/test/repo")  # Missing 'path' parameter

        # Test with all parameters
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.json.return_value = {"content": "test content"}

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await get_file(
                "https://github.com/test/repo",
                "test.py",
                ref="develop",
                token="test-token",
            )

            assert result == "test content"
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                "http://localhost:8000/file",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "path": "test.py",
                    "ref": "develop",
                    "token": "test-token",
                },
                timeout=30,
            )
