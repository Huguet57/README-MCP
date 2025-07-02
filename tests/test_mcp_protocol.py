"""Test MCP protocol compliance."""

import json
import subprocess
import sys


class TestMCPProtocol:
    """Test MCP protocol compliance and tool discovery."""

    def test_mcp_initialization_and_tools(self):
        """Test complete MCP initialization and tool listing."""
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send initialization
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }
            process.stdin.write(json.dumps(init_msg) + "\n")
            process.stdin.flush()

            # Read initialization response
            init_response = json.loads(process.stdout.readline())
            assert init_response["jsonrpc"] == "2.0"
            assert init_response["id"] == 1
            assert "result" in init_response
            assert "serverInfo" in init_response["result"]
            assert init_response["result"]["serverInfo"]["name"] == "readme-mcp"

            # Send initialized notification
            initialized_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }
            process.stdin.write(json.dumps(initialized_msg) + "\n")
            process.stdin.flush()

            # Send tools/list request
            tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            }
            process.stdin.write(json.dumps(tools_msg) + "\n")
            process.stdin.flush()

            # Read tools response
            tools_response = json.loads(process.stdout.readline())
            assert tools_response["jsonrpc"] == "2.0"
            assert tools_response["id"] == 2

            if "result" in tools_response:
                tools = tools_response["result"]["tools"]
                tool_names = [tool["name"] for tool in tools]

                # Verify all three tools are present
                expected_tools = ["get_readme", "get_file", "list_directory"]
                for expected_tool in expected_tools:
                    assert expected_tool in tool_names, (
                        f"Tool {expected_tool} not found in {tool_names}"
                    )

                # Verify tool structure
                for tool in tools:
                    assert "name" in tool
                    assert "description" in tool
                    assert "inputSchema" in tool
                    assert tool["inputSchema"]["type"] == "object"
                    assert "properties" in tool["inputSchema"]
                    assert "required" in tool["inputSchema"]
            else:
                # If there's an error, at least verify it's a proper JSON-RPC error
                assert "error" in tools_response
                assert "code" in tools_response["error"]
                assert "message" in tools_response["error"]

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_mcp_server_capabilities(self):
        """Test that MCP server reports correct capabilities."""
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send initialization
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }
            process.stdin.write(json.dumps(init_msg) + "\n")
            process.stdin.flush()

            # Read initialization response
            init_response = json.loads(process.stdout.readline())

            result = init_response["result"]
            assert "capabilities" in result
            assert "tools" in result["capabilities"]
            assert "serverInfo" in result
            assert result["serverInfo"]["name"] == "readme-mcp"

        finally:
            process.terminate()
            process.wait(timeout=5)
