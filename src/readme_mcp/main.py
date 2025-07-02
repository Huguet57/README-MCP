"""Main FastAPI application for README-MCP."""

from fastapi import FastAPI

from .api import router

app = FastAPI(
    title="README-MCP",
    description="GitHub repository documentation service",
    version="0.1.0",
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "name": "README-MCP",
        "description": "GitHub repository documentation service",
        "version": "0.1.0",
        "endpoints": {
            "/readme": "Get README file from GitHub repository",
            "/file": "Get specific file from GitHub repository",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# For direct execution, use scripts/dev.py instead
