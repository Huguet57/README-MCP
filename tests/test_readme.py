import pytest
import vcr
from fastapi.testclient import TestClient

from readme_mcp.main import app

client = TestClient(app)


@vcr.use_cassette("tests/fixtures/flask_readme.yaml", record_mode="once")
def test_get_readme_success():
    """Test successful README retrieval from Flask repository"""
    response = client.post(
        "/readme", json={"repo_url": "https://github.com/pallets/flask", "ref": "main"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "content" in data
    assert "name" in data
    assert "path" in data
    assert "sha" in data
    assert "size" in data
    assert data["name"].lower().startswith("readme")
    assert "Flask" in data["content"]


@vcr.use_cassette("tests/fixtures/nonexistent_repo.yaml", record_mode="once")
def test_get_readme_nonexistent_repo():
    """Test README retrieval from non-existent repository"""
    response = client.post(
        "/readme",
        json={"repo_url": "https://github.com/nonexistent/repo", "ref": "main"},
    )

    assert response.status_code == 404


def test_invalid_repo_url():
    """Test validation of repository URL format"""
    response = client.post(
        "/readme", json={"repo_url": "https://example.com/invalid/repo", "ref": "main"}
    )

    assert response.status_code == 422


def test_invalid_repo_url_format():
    """Test validation of GitHub URL with invalid characters"""
    response = client.post(
        "/readme", json={"repo_url": "https://github.com/owner/../repo", "ref": "main"}
    )

    assert response.status_code == 422


@vcr.use_cassette("tests/fixtures/react_readme.yaml", record_mode="once")
def test_get_readme_with_token():
    """Test README retrieval with authentication token (may fail with fake token)"""
    response = client.post(
        "/readme",
        json={
            "repo_url": "https://github.com/facebook/react",
            "ref": "main",
            "token": "fake_token_for_testing",
        },
    )

    # Accept both success and auth failure for this test
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "React" in data["content"]


@vcr.use_cassette("tests/fixtures/flask_specific_branch.yaml", record_mode="once")
def test_get_readme_specific_branch():
    """Test README retrieval from specific branch"""
    response = client.post(
        "/readme", json={"repo_url": "https://github.com/pallets/flask", "ref": "2.3.x"}
    )

    assert response.status_code in [200, 404]


@vcr.use_cassette("tests/fixtures/flask_pyproject_toml.yaml", record_mode="once")
def test_get_file_success():
    """Test successful file retrieval from Flask repository"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "pyproject.toml",
            "ref": "main",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "content" in data
    assert "name" in data
    assert "path" in data
    assert "sha" in data
    assert "size" in data
    assert data["name"] == "pyproject.toml"
    assert data["path"] == "pyproject.toml"
    assert "project" in data["content"] or "name" in data["content"]


@vcr.use_cassette("tests/fixtures/flask_license.yaml", record_mode="once")
def test_get_file_license():
    """Test file retrieval of LICENSE file from Flask repository"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "LICENSE.txt",
            "ref": "main",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "content" in data
    assert data["name"] == "LICENSE.txt"
    assert "Copyright" in data["content"] and "Redistribution" in data["content"]


@vcr.use_cassette("tests/fixtures/nonexistent_file.yaml", record_mode="once")
def test_get_file_nonexistent():
    """Test file retrieval for non-existent file"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "nonexistent_file.txt",
            "ref": "main",
        },
    )

    assert response.status_code == 404


def test_get_file_invalid_path():
    """Test file retrieval with path traversal attempt"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "../../../etc/passwd",
            "ref": "main",
        },
    )

    assert response.status_code == 422


def test_get_file_invalid_repo_url():
    """Test file retrieval with invalid repository URL"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://example.com/invalid/repo",
            "path": "setup.py",
            "ref": "main",
        },
    )

    assert response.status_code == 422


@vcr.use_cassette("tests/fixtures/flask_directory.yaml", record_mode="once")
def test_get_file_directory_path():
    """Test file retrieval when path points to directory"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "src",
            "ref": "main",
        },
    )

    assert response.status_code == 400


def test_get_file_empty_path():
    """Test file retrieval with empty path"""
    response = client.post(
        "/file",
        json={
            "repo_url": "https://github.com/pallets/flask",
            "path": "",
            "ref": "main",
        },
    )

    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
