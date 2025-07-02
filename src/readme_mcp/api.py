"""API endpoints for README-MCP."""

import base64

from fastapi import APIRouter, HTTPException

from .github_client import GitHubClient
from .models import (
    DirectoryEntry,
    DirectoryRequest,
    DirectoryResponse,
    FileRequest,
    FileResponse,
    ReadmeRequest,
    ReadmeResponse,
)

router = APIRouter()
github_client = GitHubClient()


@router.post("/readme", response_model=ReadmeResponse)
async def get_readme(request: ReadmeRequest) -> ReadmeResponse:
    """Get README file from GitHub repository.

    Args:
        request: README request with repo URL, ref, and optional token

    Returns:
        README content and metadata

    Raises:
        HTTPException: If repository not found, README missing, or other errors
    """
    owner, repo = github_client.parse_repo_url(request.repo_url)

    try:
        readme_data = await github_client.get_readme(
            owner, repo, request.ref, request.token
        )

        content = base64.b64decode(readme_data["content"]).decode("utf-8")

        return ReadmeResponse(
            content=content,
            name=readme_data["name"],
            path=readme_data["path"],
            sha=readme_data["sha"],
            size=readme_data["size"],
            encoding=readme_data["encoding"],
            download_url=readme_data["download_url"],
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/file", response_model=FileResponse)
async def get_file(request: FileRequest) -> FileResponse:
    """Get file from GitHub repository.

    Args:
        request: File request with repo URL, path, ref, and optional token

    Returns:
        File content and metadata

    Raises:
        HTTPException: If repository/file not found, path invalid, or other errors
    """
    owner, repo = github_client.parse_repo_url(request.repo_url)

    try:
        file_data = await github_client.get_file(
            owner, repo, request.path, request.ref, request.token
        )

        # Decode content if it's base64 encoded
        content = file_data["content"]
        if file_data.get("encoding") == "base64":
            content = base64.b64decode(content).decode("utf-8")

        return FileResponse(
            content=content,
            name=file_data["name"],
            path=file_data["path"],
            sha=file_data["sha"],
            size=file_data["size"],
            encoding=file_data["encoding"],
            download_url=file_data["download_url"],
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/ls", response_model=DirectoryResponse)
async def list_directory(request: DirectoryRequest) -> DirectoryResponse:
    """List directory contents from GitHub repository.

    Args:
        request: Directory request with repo URL, directory path, ref, and optional token

    Returns:
        Directory listing with entries and metadata

    Raises:
        HTTPException: If repository/directory not found, path invalid, or other errors
    """
    owner, repo = github_client.parse_repo_url(request.repo_url)

    try:
        directory_data = await github_client.list_directory(
            owner, repo, request.dir, request.ref, request.token
        )

        # Convert GitHub API response to our DirectoryEntry model
        entries = []
        for item in directory_data:
            entry = DirectoryEntry(
                name=item["name"],
                path=item["path"],
                sha=item["sha"],
                size=item.get("size"),  # Directories don't have size
                type=item["type"],
                download_url=item.get(
                    "download_url"
                ),  # Directories don't have download_url
            )
            entries.append(entry)

        return DirectoryResponse(
            entries=entries,
            total_count=len(entries),
            path=request.dir,
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from None
