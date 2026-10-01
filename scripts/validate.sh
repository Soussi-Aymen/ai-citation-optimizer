#!/usr/bin/env sh
# Lint + test via Docker Compose (no local Python/pnpm or root Node required).
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

lint_only=false
tests_only=false
related=false

for arg in "$@"; do
  case "$arg" in
    --lint-only) lint_only=true ;;
    --tests-only) tests_only=true ;;
    --related) related=true ;;
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

changed_files() {
  git diff --name-only --diff-filter=ACMR HEAD
  git ls-files --others --exclude-standard
}

run_related_tests() {
  backend_all=false
  frontend_all=false
  backend_tests=""
  frontend_sources=""
  frontend_tests=""

  while IFS= read -r file; do
    [ -n "$file" ] || continue
    case "$file" in
      backend/pyproject.toml|backend/requirements.txt|backend/requirements-dev.txt|backend/tests/conftest.py|backend/Dockerfile)
        backend_all=true
        ;;
      backend/tests/*.py)
        backend_tests="$backend_tests ${file#backend/}"
        ;;
      backend/app/agent.py)
        backend_tests="$backend_tests tests/test_agent.py tests/test_agent_fix.py"
        ;;
      backend/app/main.py)
        backend_tests="$backend_tests tests/test_api_integration.py"
        ;;
      backend/app/llms_txt_analyzer.py)
        backend_tests="$backend_tests tests/test_llms_txt.py"
        ;;
      backend/app/peec_client.py)
        backend_tests="$backend_tests tests/test_peec_client.py"
        ;;
      backend/app/sitemap_analyzer.py)
        backend_tests="$backend_tests tests/test_sitemap_analyzer.py"
        ;;
      backend/app/*.py)
        backend_all=true
        ;;
      frontend/package.json|frontend/vite.config.ts|frontend/src/test/*)
        frontend_all=true
        ;;
      frontend/src/*.test.ts|frontend/src/*.test.tsx|frontend/src/*/*.test.ts|frontend/src/*/*.test.tsx)
        frontend_tests="$frontend_tests ${file#frontend/}"
        ;;
      frontend/src/*)
        frontend_sources="$frontend_sources ${file#frontend/}"
        ;;
    esac
  done <<EOF
$(changed_files)
EOF

  if [ "$backend_all" = true ]; then
    docker_run 'Backend tests for touched files (pytest -n auto)' backend pytest
  elif [ -n "$(printf '%s' "$backend_tests" | tr -s ' ')" ]; then
    # shellcheck disable=SC2086
    docker_run 'Backend tests for touched files (pytest -n auto)' backend pytest $backend_tests
  else
    printf '\n▶ Backend tests for touched files: none\n'
  fi

  if [ "$frontend_all" = true ]; then
    docker_run 'Frontend tests for touched files (vitest)' frontend pnpm test:run
  elif [ -n "$(printf '%s' "$frontend_sources$frontend_tests" | tr -s ' ')" ]; then
    # shellcheck disable=SC2086
    docker_run 'Frontend tests for touched files (vitest)' frontend pnpm exec vitest related --run --maxWorkers=100% $frontend_sources $frontend_tests
  else
    printf '\n▶ Frontend tests for touched files: none\n'
  fi
}

printf 'Running checks via Docker Compose...\n'

if [ "$tests_only" = false ]; then
  docker_run 'Backend lint (ruff)' backend ruff check .
  docker_run 'Backend format (ruff)' backend ruff format --check .
  docker_run 'Frontend typecheck' frontend pnpm typecheck
  docker_run 'Frontend lint (oxlint)' frontend pnpm lint
  docker_run 'Frontend format (oxfmt)' frontend pnpm format:check
fi

if [ "$lint_only" = false ]; then
  if [ "$related" = true ]; then
    run_related_tests
  else
    docker_run 'Backend tests (pytest)' backend pytest
    docker_run 'Frontend tests (vitest)' frontend pnpm test:run
  fi
fi

printf '\n✓ All checks passed\n'
