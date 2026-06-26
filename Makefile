.PHONY: setup dev docker-up docker-down test test-integration

setup:
	node scripts/setup.mjs

dev:
	node scripts/dev.mjs

test:
	cd backend && python -m pytest
	cd frontend && pnpm test:run

test-integration:
	cd backend && python -m pytest -m integration

docker-up:
	docker compose up --build

docker-down:
	docker compose down
