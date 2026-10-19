.PHONY: setup kind-up kafka-up redpanda-up redpanda-down test lint

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

kind-up:
	kind create cluster --config infra/kind-config.yaml --name drift

kafka-up:
	@echo "Laptop-friendly: use 'make redpanda-up' (Phase A). kind+Kafka is Phase C (Week 4)."

redpanda-up:
	docker compose -f infra/docker-compose.yml up -d

redpanda-down:
	docker compose -f infra/docker-compose.yml down

test:
	pytest -q

lint:
	python -m py_compile generator/*.py streaming/*.py
