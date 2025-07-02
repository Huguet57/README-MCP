"""Request and response models for README-MCP."""

import re

from pydantic import BaseModel, field_validator


class ReadmeRequest(BaseModel):
    """Request model for README endpoint."""

    repo_url: str
    ref: str | None = "main"
    token: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        """Validate GitHub repository URL format."""
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GitHub repository URL format")
        return v


class FileRequest(BaseModel):
    """Request model for file endpoint."""

    repo_url: str
    path: str
    ref: str | None = "main"
    token: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        """Validate GitHub repository URL format."""
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GitHub repository URL format")
        return v

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        """Validate file path to prevent traversal attacks."""
        # Strip leading/trailing slashes and normalize
        v = v.strip("/")

        # Check for path traversal attempts
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid path: path traversal not allowed")

        # Basic path validation
        if not v or len(v) > 1000:
            raise ValueError("Path must be between 1 and 1000 characters")

        return v


class FileResponse(BaseModel):
    """Response model for file content."""

    content: str
    name: str
    path: str
    sha: str
    size: int
    encoding: str
    download_url: str


class DirectoryRequest(BaseModel):
    """Request model for directory listing endpoint."""

    repo_url: str
    dir: str = ""
    ref: str | None = "main"
    token: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        """Validate GitHub repository URL format."""
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GitHub repository URL format")
        return v

    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v):
        """Validate directory path to prevent traversal attacks."""
        # Strip leading/trailing slashes and normalize
        v = v.strip("/")

        # Empty string is valid (root directory)
        if not v:
            return v

        # Check for path traversal attempts
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid directory path: path traversal not allowed")

        # Basic path validation
        if len(v) > 1000:
            raise ValueError("Directory path must be less than 1000 characters")

        return v


class DirectoryEntry(BaseModel):
    """Model for a single directory entry."""

    name: str
    path: str
    sha: str
    size: int | None
    type: str  # "file" or "dir"
    download_url: str | None


class DirectoryResponse(BaseModel):
    """Response model for directory listing."""

    entries: list[DirectoryEntry]
    total_count: int
    path: str


class ReadmeResponse(BaseModel):
    """Response model for README content."""

    content: str
    name: str
    path: str
    sha: str
    size: int
    encoding: str
    download_url: str
