"""Tests for MCP server setup and tool functionality."""

import json
import subprocess
import sys
import time


class TestMCPServer:
    """Test MCP server tool discovery and invocation."""

    def test_mcp_tools_listed(self):
        """Test that MCP server properly lists all three tools."""
        # Start MCP server process
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            process.stdin.write(json.dumps(initialize_request) + "\n")
            process.stdin.flush()

            # Read initialize response
            response_line = process.stdout.readline()
            initialize_response = json.loads(response_line)

            assert initialize_response["jsonrpc"] == "2.0"
            assert initialize_response["id"] == 1
            assert "result" in initialize_response

            # Send list tools request
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            }

            process.stdin.write(json.dumps(list_tools_request) + "\n")
            process.stdin.flush()

            # Read list tools response
            response_line = process.stdout.readline()
            list_tools_response = json.loads(response_line)

            assert list_tools_response["jsonrpc"] == "2.0"
            assert list_tools_response["id"] == 2
            assert "result" in list_tools_response

            tools = list_tools_response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]

            # Verify all three tools are present
            expected_tools = ["get_readme", "get_file", "list_directory"]
            for expected_tool in expected_tools:
                assert expected_tool in tool_names

            # Verify tool schemas are properly defined
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
                assert tool["inputSchema"]["type"] == "object"
                assert "properties" in tool["inputSchema"]
                assert "required" in tool["inputSchema"]

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_mcp_tool_schemas(self):
        """Test that MCP tools have correct parameter schemas."""
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Initialize
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            process.stdin.write(json.dumps(initialize_request) + "\n")
            process.stdin.flush()
            process.stdout.readline()  # Consume initialize response

            # List tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            }

            process.stdin.write(json.dumps(list_tools_request) + "\n")
            process.stdin.flush()

            response_line = process.stdout.readline()
            list_tools_response = json.loads(response_line)
            tools = list_tools_response["result"]["tools"]

            # Check get_readme schema
            readme_tool = next(tool for tool in tools if tool["name"] == "get_readme")
            readme_props = readme_tool["inputSchema"]["properties"]
            assert "repo_url" in readme_props
            assert "ref" in readme_props
            assert "token" in readme_props
            assert readme_tool["inputSchema"]["required"] == ["repo_url"]

            # Check get_file schema
            file_tool = next(tool for tool in tools if tool["name"] == "get_file")
            file_props = file_tool["inputSchema"]["properties"]
            assert "repo_url" in file_props
            assert "path" in file_props
            assert "ref" in file_props
            assert "token" in file_props
            assert set(file_tool["inputSchema"]["required"]) == {"repo_url", "path"}

            # Check list_directory schema
            dir_tool = next(tool for tool in tools if tool["name"] == "list_directory")
            dir_props = dir_tool["inputSchema"]["properties"]
            assert "repo_url" in dir_props
            assert "dir" in dir_props
            assert "ref" in dir_props
            assert "token" in dir_props
            assert dir_tool["inputSchema"]["required"] == ["repo_url"]

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_mcp_tool_call_error_handling(self):
        """Test that MCP tools handle errors properly."""
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Initialize
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            process.stdin.write(json.dumps(initialize_request) + "\n")
            process.stdin.flush()
            process.stdout.readline()  # Consume initialize response

            # Call tool with invalid parameters (should fail gracefully)
            tool_call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_readme",
                    "arguments": {
                        "repo_url": "invalid-url"  # Invalid URL format
                    },
                },
            }

            process.stdin.write(json.dumps(tool_call_request) + "\n")
            process.stdin.flush()

            response_line = process.stdout.readline()
            tool_call_response = json.loads(response_line)

            # Should return an error response, not crash
            assert tool_call_response["jsonrpc"] == "2.0"
            assert tool_call_response["id"] == 3
            # Either success with error content or proper error response
            assert "result" in tool_call_response or "error" in tool_call_response

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_mcp_server_startup(self):
        """Test that MCP server starts up properly."""
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Give server a moment to start
            time.sleep(0.1)

            # Server should be running and responsive
            assert process.poll() is None, "MCP server should still be running"

            # Send a simple initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            process.stdin.write(json.dumps(initialize_request) + "\n")
            process.stdin.flush()

            # Should get a response within reasonable time
            response_line = process.stdout.readline()
            assert response_line.strip(), "Should receive a response from MCP server"

            response = json.loads(response_line)
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response

        finally:
            process.terminate()
            process.wait(timeout=5)
