#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const isWin = platform() === 'win32'
const backendDir = join(root, 'backend')
const venvPython = join(
  backendDir,
  '.venv',
  isWin ? 'Scripts' : 'bin',
  isWin ? 'python.exe' : 'python',
)
const python = existsSync(venvPython) ? venvPython : isWin ? 'python' : 'python3'

function run(args) {
  const result = spawnSync(python, args, {
    cwd: backendDir,
    stdio: 'inherit',
    shell: isWin,
  })
  if (result.status !== 0) process.exit(result.status ?? 1)
}

run(['-m', 'ruff', 'check', '.'])
run(['-m', 'ruff', 'format', '--check', '.'])
