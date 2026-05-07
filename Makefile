.PHONY: test verify-ai pm-status pm-next pm-resume pm-branch-plan pm-summary verify help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run the test suite
	uv run python -m pytest tests/ -v

verify-ai: ## Check skill-pack integrity and role boundaries
	uv run harness verify-ai

pm-status: ## Show PM runtime health-check status
	uv run harness pm-status

pm-next: ## Print the deterministic next-action decision for the supervisor
	uv run harness pm-next

pm-resume: ## Summarize current resume context for an interrupted loop
	uv run harness pm-resume

pm-branch-plan: ## Print a read-only branch correction plan
	uv run harness pm-branch-plan

pm-summary: ## Print a concise audit summary of the supervisor loop run
	uv run harness pm-summary

verify: test verify-ai pm-status ## Run all verification checks (test + verify-ai + pm-status)
