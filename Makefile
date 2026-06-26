.PHONY: setup dev docker-up docker-down

setup:
	node scripts/setup.mjs

dev:
	node scripts/dev.mjs

docker-up:
	docker compose up --build

docker-down:
	docker compose down
