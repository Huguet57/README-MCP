from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import httpx
import re
import base64
from typing import Optional

app = FastAPI(title="README-MCP", description="GitHub repository documentation service")

class ReadmeRequest(BaseModel):
    repo_url: str
    ref: Optional[str] = "main"
    token: Optional[str] = None
    
    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v):
        pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid GitHub repository URL format')
        return v

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        
    async def get_readme(self, owner: str, repo: str, ref: str = "main", token: Optional[str] = None) -> dict:
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
                raise HTTPException(status_code=response.status_code, detail="GitHub API error")
                
            return response.json()

github_client = GitHubClient()

@app.post("/readme")
async def get_readme(request: ReadmeRequest):
    repo_parts = request.repo_url.replace("https://github.com/", "").split("/")
    if len(repo_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid repository URL")
    
    owner, repo = repo_parts
    
    try:
        readme_data = await github_client.get_readme(owner, repo, request.ref, request.token)
        
        content = base64.b64decode(readme_data["content"]).decode("utf-8")
        
        return {
            "content": content,
            "name": readme_data["name"],
            "path": readme_data["path"],
            "sha": readme_data["sha"],
            "size": readme_data["size"],
            "encoding": readme_data["encoding"],
            "download_url": readme_data["download_url"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)