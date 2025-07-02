#!/usr/bin/env python3
"""
Example usage of the README-MCP service with the Flask repository
"""

import asyncio

import httpx


async def test_readme_endpoint():
    """Test the /readme endpoint with Flask repository"""

    # Start the server first: uvicorn main:app --reload
    base_url = "http://localhost:8000"

    # Test data for Flask repository
    request_data = {"repo_url": "https://github.com/pallets/flask", "ref": "main"}

    async with httpx.AsyncClient() as client:
        try:
            print("🔍 Fetching README from Flask repository...")
            response = await client.post(f"{base_url}/readme", json=request_data)

            if response.status_code == 200:
                data = response.json()
                print("✅ Success!")
                print(f"📄 File: {data['name']}")
                print(f"📏 Size: {data['size']} bytes")
                print(f"🔗 SHA: {data['sha'][:8]}...")
                print("\n📖 Content preview (first 500 chars):")
                print("-" * 50)
                print(
                    data["content"][:500] + "..."
                    if len(data["content"]) > 500
                    else data["content"]
                )
                print("-" * 50)

            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the server is running: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(test_readme_endpoint())
