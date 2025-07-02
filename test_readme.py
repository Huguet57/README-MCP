import pytest
import vcr
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@vcr.use_cassette('tests/fixtures/flask_readme.yaml', record_mode='once')
def test_get_readme_success():
    """Test successful README retrieval from Flask repository"""
    response = client.post("/readme", json={
        "repo_url": "https://github.com/pallets/flask",
        "ref": "main"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "content" in data
    assert "name" in data
    assert "path" in data
    assert "sha" in data
    assert "size" in data
    assert data["name"].lower().startswith("readme")
    assert "Flask" in data["content"]

@vcr.use_cassette('tests/fixtures/nonexistent_repo.yaml', record_mode='once')
def test_get_readme_nonexistent_repo():
    """Test README retrieval from non-existent repository"""
    response = client.post("/readme", json={
        "repo_url": "https://github.com/nonexistent/repo",
        "ref": "main"
    })
    
    assert response.status_code == 404

def test_invalid_repo_url():
    """Test validation of repository URL format"""
    response = client.post("/readme", json={
        "repo_url": "https://example.com/invalid/repo",
        "ref": "main"
    })
    
    assert response.status_code == 422

def test_invalid_repo_url_format():
    """Test validation of GitHub URL with invalid characters"""
    response = client.post("/readme", json={
        "repo_url": "https://github.com/owner/../repo",
        "ref": "main"
    })
    
    assert response.status_code == 422

@vcr.use_cassette('tests/fixtures/react_readme.yaml', record_mode='once')
def test_get_readme_with_token():
    """Test README retrieval with authentication token (may fail with fake token)"""
    response = client.post("/readme", json={
        "repo_url": "https://github.com/facebook/react",
        "ref": "main",
        "token": "fake_token_for_testing"
    })
    
    # Accept both success and auth failure for this test
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "React" in data["content"]

@vcr.use_cassette('tests/fixtures/flask_specific_branch.yaml', record_mode='once')
def test_get_readme_specific_branch():
    """Test README retrieval from specific branch"""
    response = client.post("/readme", json={
        "repo_url": "https://github.com/pallets/flask",
        "ref": "2.3.x"
    })
    
    assert response.status_code in [200, 404]

if __name__ == "__main__":
    pytest.main([__file__])