"""GitHub API client for README-MCP."""

import httpx
from fastapi import HTTPException


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self):
        self.base_url = "https://api.github.com"

    async def get_readme(
        self, owner: str, repo: str, ref: str = "main", token: str | None = None
    ) -> dict:
        """Fetch README file from GitHub repository.

        Args:
            owner: Repository owner username
            repo: Repository name
            ref: Git reference (branch, tag, commit SHA)
            token: GitHub authentication token

        Returns:
            Dictionary containing README file data from GitHub API

        Raises:
            HTTPException: If README not found or API error occurs
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/readme"
            params = {"ref": ref}

            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="README not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="GitHub API error"
                )

            return response.json()

    async def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main",
        token: str | None = None,
    ) -> dict:
        """Fetch file from GitHub repository.

        Args:
            owner: Repository owner username
            repo: Repository name
            path: File path within repository
            ref: Git reference (branch, tag, commit SHA)
            token: GitHub authentication token

        Returns:
            Dictionary containing file data from GitHub API

        Raises:
            HTTPException: If file not found, is directory, too large, or API error occurs
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            params = {"ref": ref}

            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="File not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="GitHub API error"
                )

            file_data = response.json()

            # Check if response is a list (directory) or dict (file)
            if isinstance(file_data, list):
                raise HTTPException(
                    status_code=400, detail="Path is a directory, not a file"
                )

            # Ensure it's a file, not a directory
            if file_data.get("type") != "file":
                raise HTTPException(status_code=400, detail="Path is not a file")

            # Check file size limit (100kB = 102400 bytes)
            if file_data.get("size", 0) > 102400:
                raise HTTPException(
                    status_code=413, detail="File too large (max 100kB)"
                )

            return file_data

    async def list_directory(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str = "main",
        token: str | None = None,
    ) -> list[dict]:
        """List contents of a directory in GitHub repository.

        Args:
            owner: Repository owner username
            repo: Repository name
            path: Directory path within repository (empty for root)
            ref: Git reference (branch, tag, commit SHA)
            token: GitHub authentication token

        Returns:
            List of directory entries from GitHub API

        Raises:
            HTTPException: If directory not found, path is file, or API error occurs
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        async with httpx.AsyncClient() as client:
            # Use contents API for directory listing
            if path:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            else:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents"

            params = {"ref": ref}

            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Directory not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="GitHub API error"
                )

            directory_data = response.json()

            # Check if response is a single file (dict) instead of directory (list)
            if isinstance(directory_data, dict):
                raise HTTPException(
                    status_code=400, detail="Path is a file, not a directory"
                )

            # Enforce 1,000 entry limit per CLAUDE.md requirements
            if len(directory_data) > 1000:
                raise HTTPException(
                    status_code=413, detail="Directory too large (max 1,000 entries)"
                )

            return directory_data

    def parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse GitHub repository URL into owner and repo name.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Tuple of (owner, repo) strings

        Raises:
            HTTPException: If URL format is invalid
        """
        repo_parts = repo_url.replace("https://github.com/", "").split("/")
        if len(repo_parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid repository URL")

        return repo_parts[0], repo_parts[1]
