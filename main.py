import base64
import re

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI(title="README-MCP", description="GitHub repository documentation service")


class ReadmeRequest(BaseModel):
    repo_url: str
    ref: str | None = "main"
    token: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GitHub repository URL format")
        return v


class FileRequest(BaseModel):
    repo_url: str
    path: str
    ref: str | None = "main"
    token: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GitHub repository URL format")
        return v

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        # Strip leading/trailing slashes and normalize
        v = v.strip("/")

        # Check for path traversal attempts
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid path: path traversal not allowed")

        # Basic path validation
        if not v or len(v) > 1000:
            raise ValueError("Path must be between 1 and 1000 characters")

        return v


class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"

    async def get_readme(
        self, owner: str, repo: str, ref: str = "main", token: str | None = None
    ) -> dict:
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


github_client = GitHubClient()


@app.post("/readme")
async def get_readme(request: ReadmeRequest):
    repo_parts = request.repo_url.replace("https://github.com/", "").split("/")
    if len(repo_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid repository URL")

    owner, repo = repo_parts

    try:
        readme_data = await github_client.get_readme(
            owner, repo, request.ref, request.token
        )

        content = base64.b64decode(readme_data["content"]).decode("utf-8")

        return {
            "content": content,
            "name": readme_data["name"],
            "path": readme_data["path"],
            "sha": readme_data["sha"],
            "size": readme_data["size"],
            "encoding": readme_data["encoding"],
            "download_url": readme_data["download_url"],
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.post("/file")
async def get_file(request: FileRequest):
    repo_parts = request.repo_url.replace("https://github.com/", "").split("/")
    if len(repo_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid repository URL")

    owner, repo = repo_parts

    try:
        file_data = await github_client.get_file(
            owner, repo, request.path, request.ref, request.token
        )

        # Decode content if it's base64 encoded
        content = file_data["content"]
        if file_data.get("encoding") == "base64":
            content = base64.b64decode(content).decode("utf-8")

        # Return content as string for JSON serialization

        return {
            "content": content,
            "name": file_data["name"],
            "path": file_data["path"],
            "sha": file_data["sha"],
            "size": file_data["size"],
            "encoding": file_data["encoding"],
            "download_url": file_data["download_url"],
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
