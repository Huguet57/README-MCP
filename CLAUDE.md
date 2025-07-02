# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

README-MCP is a minimal service that exposes three deterministic endpoints (`/readme`, `/file`, `/ls`) for agents to retrieve GitHub repository documentation and files. The service is designed to be stateless, cache-friendly, and provide ground-truth documentation to AI agents with zero LLM tokens.

## Architecture

The service follows a simple REST API pattern with these core components:
- **Router**: Validates requests and authentication, routes to handlers
- **GitHubClient**: Thin wrapper around GitHub REST `contents` and `trees` endpoints  
- **Cache**: Keyed by `repo@sha+path`, stores body + ETag
- **Limiter**: Mirrors GitHub rate-limit headers to caller

## Tech Stack

- **Runtime**: Python 3.12 + FastAPI + Uvicorn
- **HTTP client**: `httpx` with retry & timeout middleware
- **Cache**: Redis (optional Cloudflare KV when serverless)
- **Testing**: PyTest + VCR.py to record GitHub fixtures

## Development Status

This repository currently contains only planning documentation (DEVELOPMENT.md). The actual implementation has not yet been started - this is a greenfield project in the planning phase.

## Security Requirements

When implementing code for this project:
- Validate `repo_url` against regex `^https://github.com/{owner}/{repo}$`
- Strip `..` and symlink elements in `path` and `dir` parameters
- Enforce 100 kB max file size and 1,000 entry max per listing
- Forward GitHub `X-RateLimit-*` headers to client

## API Endpoints (Planned)

- `POST /readme` - Return decoded README at repo root
- `POST /file` - Return raw bytes of a single in-repo file  
- `POST /ls` - List immediate children of a directory

All endpoints accept: `{ repo_url, ref?, token? }` with additional path parameters as needed.

## Development Phases

The project is planned in 7 phases over 16 days:
- Phase 0: Repo bootstrap, lint, CI skeleton
- Phase 1-3: Individual endpoint handlers with tests
- Phase 4: Shared caching layer & ETag support
- Phase 5-6: Integration tests and deployment
- Phase 7: Production cut-over

## Testing Strategy (Planned)

- **Unit**: Mock GitHub responses with VCR.py
- **Integration**: Test against real public repos (e.g. `pallets/flask`)
- **Contract**: Dredd tests to verify OpenAPI schema
- **Load**: k6 script simulating 500 rps, ensure <200ms p95