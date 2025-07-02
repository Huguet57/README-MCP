# Deployment Guide for README-MCP

This guide covers deploying README-MCP in various environments.

## Quick Start

### Local Development
```bash
# Install dependencies
uv sync

# Run development server
make dev
# or
uv run python scripts/dev.py
```

### Docker (Local)
```bash
# Build and run with Docker Compose
make deploy-local
# or
docker-compose up --build

# Or build and run manually
make docker-build
make docker-run
```

## Testing

### Unit Tests
```bash
# Run all unit tests (with VCR fixtures)
make test-unit
# or
uv run pytest tests/test_readme.py -v
```

### Integration Tests
```bash
# Run integration tests against real GitHub repos
make test-integration
# or
uv run pytest tests/test_integration.py -v -m integration
```

### Load Testing
```bash
# Requires k6 (https://k6.io/)
make test-load
# or
k6 run --vus 50 --duration 30s tests/load/load_test.js
```

## Production Deployment

### Google Cloud Run

1. Build and push Docker image:
```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id

# Build and push
docker build -t gcr.io/$PROJECT_ID/readme-mcp:latest .
docker push gcr.io/$PROJECT_ID/readme-mcp:latest
```

2. Deploy:
```bash
# Update PROJECT_ID in deploy/cloud-run.yaml
make deploy-cloud-run
```

### Kubernetes

1. Build and push Docker image to your registry
2. Update image reference in `deploy/kubernetes.yaml`
3. Deploy:
```bash
make deploy-k8s
```

### DigitalOcean App Platform

1. Install DigitalOcean CLI: https://docs.digitalocean.com/reference/doctl/how-to/install/
2. Authenticate and deploy:
```bash
doctl auth init
# Update GitHub repo in deploy/digitalocean.yaml
make deploy-digitalocean
```

## Configuration

### Environment Variables

- `PYTHONPATH`: Set to `/app/src` (handled automatically in containers)
- `PYTHONUNBUFFERED`: Set to `1` for proper logging
- `PORT`: Port to run on (default: 8000)

### Security

The service implements several security measures:
- Repository URL validation (`^https://github.com/{owner}/{repo}$`)
- Path traversal prevention (strips `..` and symlinks)
- File size limits (100kB max)
- Directory entry limits (1,000 max)
- Non-root Docker container execution

### Rate Limiting

The service forwards GitHub's rate limit headers to clients:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining` 
- `X-RateLimit-Reset`

Unauthenticated requests to GitHub API are limited to 60/hour per IP.
Authenticated requests (with token) allow 5,000/hour.

### Monitoring

Health check endpoint: `GET /health`

Returns:
```json
{"status": "healthy"}
```

## Performance

### Expected Performance
- Target: <200ms p95 latency at 500 RPS
- Memory usage: ~128-512MB per instance
- CPU: ~100-500m per instance

### Scaling

- **Kubernetes**: Horizontal Pod Autoscaler configured for 3-10 replicas
- **Cloud Run**: Auto-scales 1-100 instances based on concurrency
- **DigitalOcean**: Auto-scales 1-5 instances based on CPU/memory usage

### Caching

Future enhancement: Redis caching layer
- Cache key: `repo@sha+path`
- TTL based on GitHub ETag headers
- Optional Cloudflare KV for serverless deployments

## Troubleshooting

### Common Issues

1. **GitHub Rate Limiting**
   - Solution: Use authentication tokens
   - Monitor rate limit headers in responses

2. **File Size Limits**
   - Files >100kB return 413 error
   - This is by design for performance

3. **Directory Size Limits**
   - Directories >1,000 entries return 413 error
   - This prevents abuse and ensures performance

4. **Path Traversal Attempts**
   - Paths with `..` return 422 validation error
   - Security feature to prevent directory traversal

### Docker Issues

1. **Build Failures**
   ```bash
   # Clean build with no cache
   docker build --no-cache -t readme-mcp:latest .
   ```

2. **Permission Issues**
   - Container runs as non-root user (uid 1000)
   - Ensure proper file permissions in build

### Kubernetes Issues

1. **Pod Startup**
   - Check resource limits and requests
   - Verify health check endpoints

2. **Ingress**
   - Update hostname in ingress configuration
   - Ensure cert-manager is configured for TLS

## API Documentation

OpenAPI schema is available at:
- JSON: `/openapi.json` (generated via FastAPI)
- Static files in `schemas/` directory

Generate schema:
```bash
make schema
```

## Development Workflow

1. **Code Changes**
   ```bash
   # Format and lint
   make format
   make lint
   
   # Test
   make test
   ```

2. **Integration Testing**
   ```bash
   # Test against real repos
   make test-integration
   ```

3. **Load Testing**
   ```bash
   # Performance testing
   make test-load
   ```

4. **Deployment**
   ```bash
   # Build and test Docker
   make docker-build
   make docker-run
   
   # Deploy to staging/production
   make deploy-k8s  # or deploy-cloud-run, deploy-digitalocean
   ```

## Monitoring and Observability

### Metrics

The service exposes metrics compatible with Prometheus:
- Request count and duration
- Error rates by endpoint
- GitHub API call metrics

### Logging

Structured JSON logging includes:
- Request ID correlation
- GitHub API response times
- Error details and stack traces

### Alerting

Recommended alerts:
- Error rate >1%
- P95 latency >200ms
- GitHub rate limit approaching
- Pod/container restarts