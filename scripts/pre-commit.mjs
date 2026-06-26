#!/usr/bin/env node
/**
 * Git pre-commit hook: lint backend + frontend, then run unit tests.
 * Playwright integration tests are excluded (pytest default).
 */
import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const isWin = platform() === 'win32'
const backendDir = join(root, 'backend')
const frontendDir = join(root, 'frontend')
const venvPython = join(
  backendDir,
  '.venv',
  isWin ? 'Scripts' : 'bin',
  isWin ? 'python.exe' : 'python',
)
const python = existsSync(venvPython) ? venvPython : isWin ? 'python' : 'python3'
const pnpm = isWin ? 'pnpm.cmd' : 'pnpm'

function run(label, command, args, cwd = root) {
  console.log(`\n▶ ${label}`)
  const result = spawnSync(command, args, {
    cwd,
    stdio: 'inherit',
    shell: isWin,
    env: process.env,
  })
  if (result.status !== 0) {
    console.error(`\n✗ ${label} failed — commit aborted`)
    process.exit(result.status ?? 1)
  }
}

console.log('Running pre-commit checks...')

run('Backend lint (ruff)', python, ['-m', 'ruff', 'check', '.'], backendDir)
run('Backend format (ruff)', python, ['-m', 'ruff', 'format', '--check', '.'], backendDir)
run('Frontend typecheck', pnpm, ['typecheck'], frontendDir)
run('Frontend lint (eslint)', pnpm, ['lint'], frontendDir)
run('Backend tests (pytest)', python, ['-m', 'pytest'], backendDir)
run('Frontend tests (vitest)', pnpm, ['test:run'], frontendDir)

console.log('\n✓ Pre-commit checks passed')
