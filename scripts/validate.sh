#!/usr/bin/env sh
# Lint + test via Docker Compose (no local Python/pnpm or root Node required).
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

lint_only=false
tests_only=false

for arg in "$@"; do
  case "$arg" in
    --lint-only) lint_only=true ;;
    --tests-only) tests_only=true ;;
  esac
done

docker_run() {
  label="$1"
  service="$2"
  shift 2
  printf '\n▶ %s\n' "$label"
  docker compose run --rm --no-deps "$service" "$@" || {
    printf '\n✗ %s failed\n' "$label" >&2
    exit 1
  }
}

printf 'Running checks via Docker Compose...\n'

if [ "$tests_only" = false ]; then
  docker_run 'Backend lint (ruff)' backend ruff check .
  docker_run 'Backend format (ruff)' backend ruff format --check .
  docker_run 'Frontend typecheck' frontend pnpm typecheck
  docker_run 'Frontend lint (eslint)' frontend pnpm lint
fi

if [ "$lint_only" = false ]; then
  docker_run 'Backend tests (pytest)' backend pytest
  docker_run 'Frontend tests (vitest)' frontend pnpm test:run
fi

printf '\n✓ All checks passed\n'
