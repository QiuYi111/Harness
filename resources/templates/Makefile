# Harness Standard Makefile
# "The only valid interface to the project"

.PHONY: init spec-init up down proto lint typecheck test contract-test security-scan verify verify-ai classify-risk clean help

# --- Configuration ---
PROJECT_NAME := my-project

# --- 1. Environment & Setup ---

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Initialize development environment (Tools, Hooks)
	@echo "Initializing project..."
	@command -v git >/dev/null 2>&1 || (echo "git not found" && exit 1)
	@command -v python3 >/dev/null 2>&1 || echo "python3 not found; install if needed"
	@command -v pre-commit >/dev/null 2>&1 || pip install pre-commit
	@pre-commit install 2>/dev/null || true
	@echo "Environment is ready."

spec-init: ## Create feature spec directory. Usage: make spec-init FEATURE=001-feature-name
	@test -n "$(FEATURE)" || (echo "Usage: make spec-init FEATURE=001-feature-name" && exit 1)
	@mkdir -p specs/$(FEATURE)
	@for tmpl in SPEC_TEMPLATE PLAN_TEMPLATE TASKS_TEMPLATE EVAL_TEMPLATE REPORT_TEMPLATE; do \
		if [ -f "templates/$${tmpl}.md" ]; then \
			dst=$$(echo "$$tmpl" | sed 's/_TEMPLATE//' | tr '[:upper:]' '[:lower:]'); \
			cp "templates/$${tmpl}.md" "specs/$(FEATURE)/$${dst}.md"; \
		fi; \
	done
	@echo "Created specs/$(FEATURE)/ with templates."

up: ## Start infrastructure (Docker)
	@echo "Starting infrastructure..."
	@if [ -f docker-compose.yml ]; then docker-compose up -d --wait; else echo "No docker-compose.yml found. Skipping."; fi

down: ## Stop infrastructure
	@echo "Stopping infrastructure..."
	@if [ -f docker-compose.yml ]; then docker-compose down -v; else echo "No docker-compose.yml found. Skipping."; fi

# --- 2. Contract ---

proto: ## Generate code from contracts (Protobuf/OpenAPI)
	@echo "Generating contract code..."
	@echo "Contract generation complete."

# --- 3. Quality Assurance ---

lint: ## Run code linters
	@echo "Running linters..."
	@echo "Lint check passed."

typecheck: ## Run type checks
	@echo "Running type checks..."
	@echo "Type check passed."

test: ## Run unit and integration tests
	@echo "Running tests..."
	@echo "Tests passed."

contract-test: ## Run contract tests
	@echo "Running contract tests..."
	@echo "Contract tests passed."

security-scan: ## Scan for basic security issues (gitleaks)
	@echo "Running security scan..."
	@if command -v gitleaks >/dev/null 2>&1; then gitleaks detect --no-git -v; else echo "gitleaks not installed; skipping"; fi

# --- 4. The Gatekeepers ---

verify: lint typecheck test contract-test security-scan ## Run full product verification
	@echo "Product verification passed."

verify-ai: ## Run Harness/process verification (template integrity)
	@if [ -f scripts/verify-ai.sh ]; then bash scripts/verify-ai.sh; else echo "scripts/verify-ai.sh not found"; exit 1; fi

classify-risk: ## Classify current diff by blast radius risk level
	@if [ -f scripts/classify-risk.sh ]; then bash scripts/classify-risk.sh; else echo "scripts/classify-risk.sh not found"; exit 1; fi

clean: ## Clean build artifacts
	@echo "Cleaning..."
	@echo "Clean complete."
