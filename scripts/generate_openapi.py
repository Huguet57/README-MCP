#!/usr/bin/env python3
"""Generate OpenAPI schema for README-MCP."""

import json
from pathlib import Path

from readme_mcp.main import app


def generate_openapi_schema():
    """Generate and save OpenAPI schema."""
    schema = app.openapi()

    # Ensure schemas directory exists
    schemas_dir = Path("schemas")
    schemas_dir.mkdir(exist_ok=True)

    # Save as JSON
    with open(schemas_dir / "openapi.json", "w") as f:
        json.dump(schema, f, indent=2)

    # Save as YAML (requires PyYAML)
    try:
        import yaml

        with open(schemas_dir / "openapi.yaml", "w") as f:
            yaml.dump(schema, f, default_flow_style=False)
    except ImportError:
        print("PyYAML not installed, skipping YAML output")

    print("OpenAPI schema generated:")
    print("  - schemas/openapi.json")
    if Path("schemas/openapi.yaml").exists():
        print("  - schemas/openapi.yaml")


if __name__ == "__main__":
    generate_openapi_schema()
