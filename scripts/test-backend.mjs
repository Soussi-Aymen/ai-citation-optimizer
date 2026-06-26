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

const result = spawnSync(python, ['-m', 'pytest', ...process.argv.slice(2)], {
  cwd: backendDir,
  stdio: 'inherit',
  shell: isWin,
})
process.exit(result.status ?? 1)
