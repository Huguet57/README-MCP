#!/usr/bin/env python3
"""
Direct test of the README endpoint without running a server
"""

import asyncio

from main import ReadmeRequest, github_client


async def demonstrate_flask_readme():
    """Demonstrate fetching Flask repository README"""

    print("🚀 README-MCP Service Demo")
    print("=" * 40)

    # Create request for Flask repository
    request = ReadmeRequest(repo_url="https://github.com/pallets/flask", ref="main")

    print(f"📍 Repository: {request.repo_url}")
    print(f"🌿 Branch: {request.ref}")
    print("\n🔍 Fetching README...")

    try:
        # Extract owner and repo from URL
        repo_parts = request.repo_url.replace("https://github.com/", "").split("/")
        owner, repo = repo_parts

        # Fetch README data
        readme_data = await github_client.get_readme(owner, repo, request.ref)

        # Decode content
        import base64

        content = base64.b64decode(readme_data["content"]).decode("utf-8")

        print("✅ Success!")
        print(f"📄 File: {readme_data['name']}")
        print(f"📏 Size: {readme_data['size']} bytes")
        print(f"🔗 SHA: {readme_data['sha'][:8]}...")
        print(f"🌐 Download URL: {readme_data['download_url']}")

        print("\n📖 Content preview (first 800 chars):")
        print("-" * 60)
        preview = content[:800] + "..." if len(content) > 800 else content
        print(preview)
        print("-" * 60)

        # Show some statistics
        lines = content.split("\n")
        print("\n📊 Statistics:")
        print(f"   • Total lines: {len(lines)}")
        print(f"   • Total characters: {len(content)}")
        print(f"   • Contains 'Flask': {'Yes' if 'Flask' in content else 'No'}")
        print(f"   • Contains 'Python': {'Yes' if 'Python' in content else 'No'}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(demonstrate_flask_readme())
