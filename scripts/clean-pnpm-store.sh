#!/usr/bin/env sh
# Remove accidental host-side pnpm content store (Docker creates it as root).
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

printf 'Removing frontend/.pnpm-store via Docker (root-owned)...\n'
docker compose run --rm --no-deps -u root frontend rm -rf /app/.pnpm-store

if [ -d frontend/.pnpm-store ]; then
  printf 'Removing leftover host files...\n'
  rm -rf frontend/.pnpm-store
fi

printf 'Done. Reload the Cursor window if Source Control still shows old files.\n'
