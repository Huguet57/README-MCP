# Makefile for README-MCP

.PHONY: help install dev test test-unit test-integration test-load test-mcp lint format clean build docker-build docker-run docker-push deploy-local deploy-k8s mcp-dev mcp-run mcp-install mcp-standalone

# Variables
PROJECT_NAME := readme-mcp
DOCKER_IMAGE := $(PROJECT_NAME)
DOCKER_TAG := latest
REGISTRY := gcr.io/your-project-id

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Run development server
	uv run python scripts/dev.py

mcp-dev: ## Run MCP server with inspector
	mcp dev mcp_server.py

mcp-run: ## Run MCP server
	uv run python mcp_server.py

mcp-standalone: ## Run standalone MCP server (no backend required)
	uv run python mcp_server_standalone.py

mcp-install: ## Install MCP server in Claude Desktop
	mcp install mcp_server.py --name "README-MCP"

test: ## Run all tests
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest tests/test_readme.py -v

test-mcp: ## Run MCP-specific tests
	uv run pytest tests/test_mcp_*.py -v

test-integration: ## Run integration tests only
	uv run pytest tests/test_integration.py -v -m integration

test-load: ## Run load tests (requires k6)
	k6 run --vus 50 --duration 30s tests/load/load_test.js

lint: ## Run linting
	uv run ruff check src/ tests/ scripts/ *.py

format: ## Format code
	uv run ruff format src/ tests/ scripts/ *.py

clean: ## Clean build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage

build: ## Build the package
	uv build

schema: ## Generate OpenAPI schema
	uv run python scripts/generate_openapi.py

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run Docker container locally
	docker run -p 8000:8000 $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-push: ## Push Docker image to registry
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)

deploy-local: ## Deploy locally with Docker Compose
	docker-compose up --build

deploy-k8s: ## Deploy to Kubernetes
	kubectl apply -f deploy/kubernetes.yaml

deploy-cloud-run: ## Deploy to Google Cloud Run
	gcloud run services replace deploy/cloud-run.yaml --region=us-central1

deploy-digitalocean: ## Deploy to DigitalOcean App Platform
	doctl apps create --spec deploy/digitalocean.yaml

# Quality checks
check: lint test ## Run all quality checks

# CI/CD helpers
ci-test: install test ## CI test target
ci-build: install build docker-build ## CI build target
ci-deploy: ci-build docker-push ## CI deploy target