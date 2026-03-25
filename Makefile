# =============================================================================
# RIO Protocol — Makefile
# =============================================================================
# Usage:
#   make install      Install Python dependencies
#   make init         Initialize RIO data, keys, and policy files
#   make admin        Create the first admin user
#   make run          Start API server and dashboard
#   make test         Run the full test harness (47 tests)
#   make docker-up    Start services via Docker Compose
#   make docker-down  Stop Docker Compose services
#   make clean        Remove generated data files (keeps keys)
#   make reset        Full reset: remove all generated files including keys
# =============================================================================

.PHONY: install init admin run test docker-up docker-down clean reset help

PYTHON ?= python3

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies from requirements.txt
	$(PYTHON) -m pip install -r requirements.txt

init: ## Initialize RIO: create directories, keys, policy/risk files
	$(PYTHON) scripts/init_rio.py

admin: ## Create the first admin user (interactive)
	$(PYTHON) scripts/create_admin_user.py

run: ## Start the RIO API server and audit dashboard
	$(PYTHON) scripts/run_all.py

test: ## Run the full test harness (47 tests)
	$(PYTHON) -m runtime.test_harness

docker-up: ## Start services via Docker Compose
	docker compose -f docker/docker-compose.yml up --build -d

docker-down: ## Stop Docker Compose services
	docker compose -f docker/docker-compose.yml down

clean: ## Remove generated data files (preserves keys and policy originals)
	rm -f runtime/data/ledger.jsonl
	rm -f runtime/data/governed_corpus.jsonl
	rm -f runtime/data/receipts.jsonl
	rm -f runtime/data/requests.jsonl
	rm -f runtime/data/approvals.jsonl
	rm -f runtime/data/sent_emails.log
	rm -f runtime/data/calendar_events.log
	rm -f runtime/data/http_requests.log
	rm -f runtime/governance/policy_change_log.jsonl
	rm -f runtime/governance/risk_change_log.jsonl
	@echo "Data files cleaned. Keys and policy originals preserved."

reset: clean ## Full reset: also remove keys and generated policy versions
	rm -f runtime/keys/private_key.pem
	rm -f runtime/keys/public_key.pem
	rm -f runtime/governance/policy_rules_v1_1.json
	rm -f runtime/governance/risk_rules_v1_0_1.json
	@echo "Full reset complete. Run 'make init' to reinitialize."
