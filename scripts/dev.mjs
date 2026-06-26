#!/usr/bin/env node
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const isWin = platform() === 'win32'
const backendDir = join(root, 'backend')
const frontendDir = join(root, 'frontend')
const venvPython = join(backendDir, '.venv', isWin ? 'Scripts' : 'bin', isWin ? 'python.exe' : 'python')
const pnpm = isWin ? 'pnpm.cmd' : 'pnpm'

const children = []

function shutdown(code = 0) {
  for (const child of children) {
    if (!child.killed) {
      child.kill(isWin ? undefined : 'SIGTERM')
    }
  }
  process.exit(code)
}

process.on('SIGINT', () => shutdown(0))
process.on('SIGTERM', () => shutdown(0))

if (!existsSync(venvPython)) {
  console.error('Backend not set up. Run: npm run setup')
  process.exit(1)
}

if (!existsSync(join(frontendDir, 'node_modules'))) {
  console.error('Frontend not set up. Run: npm run setup')
  process.exit(1)
}

function start(name, command, args, cwd) {
  const child = spawn(command, args, {
    cwd,
    stdio: 'inherit',
    shell: isWin,
    env: { ...process.env, FORCE_COLOR: '1' },
  })
  child.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`\n${name} stopped (exit ${code})`)
      shutdown(code)
    }
  })
  children.push(child)
  return child
}

console.log('Starting AI Citation Optimizer...\n')

start('backend', venvPython, ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], backendDir)
start('frontend', pnpm, ['dev', '--host'], frontendDir)

console.log('\n  App:      http://localhost:5173')
console.log('  API docs: http://localhost:8000/docs')
console.log('\nPress Ctrl+C to stop both services.\n')
