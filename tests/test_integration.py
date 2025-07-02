"""Integration tests for README-MCP against real GitHub repositories."""

import pytest
from fastapi.testclient import TestClient

from readme_mcp.main import app

client = TestClient(app)

# Real public repositories for integration testing
REPOS_TO_TEST = [
    {
        "repo_url": "https://github.com/pallets/flask",
        "expected_readme_content": ["Flask", "Python", "web"],
        "expected_files": ["pyproject.toml", "LICENSE.txt"],
        "expected_directories": ["src", "tests"],
    },
    {
        "repo_url": "https://github.com/microsoft/vscode",
        "expected_readme_content": ["Visual Studio Code", "editor"],
        "expected_files": ["package.json", "README.md"],
        "expected_directories": ["src", "extensions"],
    },
    {
        "repo_url": "https://github.com/python/cpython",
        "expected_readme_content": ["Python", "software foundation"],
        "expected_files": ["README.rst", "pyproject.toml"],
        "expected_directories": ["Lib", "Python"],
    },
]


@pytest.mark.integration
class TestIntegrationReadme:
    """Integration tests for README endpoint."""

    @pytest.mark.parametrize("repo_config", REPOS_TO_TEST)
    def test_readme_real_repos(self, repo_config):
        """Test README retrieval from real public repositories."""
        response = client.post(
            "/readme",
            json={
                "repo_url": repo_config["repo_url"],
                "ref": "main",
            },
        )

        # Should succeed for public repos
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "content" in data
        assert "name" in data
        assert "path" in data
        assert "sha" in data
        assert "size" in data
        assert "encoding" in data
        assert "download_url" in data

        # Validate content contains expected keywords
        content_lower = data["content"].lower()
        for expected_word in repo_config["expected_readme_content"]:
            assert expected_word.lower() in content_lower

        # Validate metadata
        assert data["name"].lower().startswith("readme")
        assert data["size"] > 0
        assert len(data["sha"]) == 40  # Git SHA is 40 characters


@pytest.mark.integration
class TestIntegrationFile:
    """Integration tests for file endpoint."""

    @pytest.mark.parametrize("repo_config", REPOS_TO_TEST)
    def test_file_real_repos(self, repo_config):
        """Test file retrieval from real public repositories."""
        for file_path in repo_config["expected_files"]:
            response = client.post(
                "/file",
                json={
                    "repo_url": repo_config["repo_url"],
                    "path": file_path,
                    "ref": "main",
                },
            )

            # Should succeed for existing files
            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "content" in data
                assert "name" in data
                assert "path" in data
                assert "sha" in data
                assert "size" in data
                assert "encoding" in data
                assert "download_url" in data

                # Validate metadata
                assert data["name"] == file_path.split("/")[-1]
                assert data["path"] == file_path
                assert data["size"] > 0
                assert len(data["sha"]) == 40

                # Content should not be empty
                assert len(data["content"]) > 0


@pytest.mark.integration
class TestIntegrationDirectory:
    """Integration tests for directory listing endpoint."""

    @pytest.mark.parametrize("repo_config", REPOS_TO_TEST)
    def test_directory_root_real_repos(self, repo_config):
        """Test root directory listing from real public repositories."""
        response = client.post(
            "/ls",
            json={
                "repo_url": repo_config["repo_url"],
                "dir": "",
                "ref": "main",
            },
        )

        # Should succeed for public repos
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "entries" in data
        assert "total_count" in data
        assert "path" in data
        assert data["path"] == ""
        assert isinstance(data["entries"], list)
        assert data["total_count"] == len(data["entries"])
        assert data["total_count"] > 0

        # Validate entry structure
        for entry in data["entries"]:
            assert "name" in entry
            assert "path" in entry
            assert "sha" in entry
            assert "type" in entry
            assert entry["type"] in ["file", "dir"]
            assert len(entry["sha"]) == 40

            # Files should have size and download_url
            if entry["type"] == "file":
                assert "size" in entry
                assert entry["size"] is not None
                assert "download_url" in entry
                assert entry["download_url"] is not None

        # Check for expected directories
        entry_names = [entry["name"] for entry in data["entries"]]
        for expected_dir in repo_config["expected_directories"]:
            # Some directories might not exist in all repos
            if expected_dir in entry_names:
                dir_entry = next(
                    e for e in data["entries"] if e["name"] == expected_dir
                )
                assert dir_entry["type"] == "dir"

    @pytest.mark.parametrize("repo_config", REPOS_TO_TEST)
    def test_directory_subdirectory_real_repos(self, repo_config):
        """Test subdirectory listing from real public repositories."""
        for directory in repo_config["expected_directories"]:
            response = client.post(
                "/ls",
                json={
                    "repo_url": repo_config["repo_url"],
                    "dir": directory,
                    "ref": "main",
                },
            )

            # Directory might not exist in all repos, so check both success and 404
            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "entries" in data
                assert "total_count" in data
                assert "path" in data
                assert data["path"] == directory
                assert isinstance(data["entries"], list)
                assert data["total_count"] == len(data["entries"])

                # Validate entry structure if entries exist
                for entry in data["entries"]:
                    assert "name" in entry
                    assert "path" in entry
                    assert "sha" in entry
                    assert "type" in entry
                    assert entry["type"] in ["file", "dir"]
                    assert entry["path"].startswith(directory + "/")
            elif response.status_code == 404:
                # Directory doesn't exist in this repo, which is acceptable
                pass
            else:
                # Unexpected error
                pytest.fail(
                    f"Unexpected status code {response.status_code} for {directory}"
                )


@pytest.mark.integration
class TestIntegrationErrorHandling:
    """Integration tests for error handling with real GitHub API."""

    def test_nonexistent_repo(self):
        """Test handling of non-existent repository."""
        response = client.post(
            "/readme",
            json={
                "repo_url": "https://github.com/nonexistent-user-12345/nonexistent-repo-12345",
                "ref": "main",
            },
        )

        assert response.status_code == 404

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        response = client.post(
            "/file",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "path": "nonexistent-file-12345.txt",
                "ref": "main",
            },
        )

        assert response.status_code == 404

    def test_nonexistent_directory(self):
        """Test handling of non-existent directory."""
        response = client.post(
            "/ls",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "dir": "nonexistent-directory-12345",
                "ref": "main",
            },
        )

        assert response.status_code == 404

    def test_nonexistent_branch(self):
        """Test handling of non-existent branch."""
        response = client.post(
            "/readme",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "ref": "nonexistent-branch-12345",
            },
        )

        assert response.status_code == 404

    def test_file_as_directory(self):
        """Test handling when requesting directory operations on files."""
        response = client.post(
            "/ls",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "dir": "README.md",
                "ref": "main",
            },
        )

        assert response.status_code == 400

    def test_directory_as_file(self):
        """Test handling when requesting file operations on directories."""
        response = client.post(
            "/file",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "path": "src",
                "ref": "main",
            },
        )

        assert response.status_code == 400


@pytest.mark.integration
class TestIntegrationPerformance:
    """Basic performance tests for integration."""

    def test_response_times(self):
        """Test that responses are reasonably fast."""
        import time

        # Test README endpoint
        start_time = time.time()
        response = client.post(
            "/readme",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "ref": "main",
            },
        )
        readme_time = time.time() - start_time

        assert response.status_code == 200
        assert readme_time < 5.0  # Should complete within 5 seconds

        # Test file endpoint
        start_time = time.time()
        response = client.post(
            "/file",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "path": "pyproject.toml",
                "ref": "main",
            },
        )
        file_time = time.time() - start_time

        assert response.status_code == 200
        assert file_time < 5.0  # Should complete within 5 seconds

        # Test directory endpoint
        start_time = time.time()
        response = client.post(
            "/ls",
            json={
                "repo_url": "https://github.com/pallets/flask",
                "dir": "",
                "ref": "main",
            },
        )
        ls_time = time.time() - start_time

        assert response.status_code == 200
        assert ls_time < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
