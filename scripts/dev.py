#!/usr/bin/env python3
"""Development server script for README-MCP."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "readme_mcp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
    )
