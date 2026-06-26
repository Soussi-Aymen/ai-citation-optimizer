#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const isWin = platform() === 'win32'
const backendDir = join(root, 'backend')
const frontendDir = join(root, 'frontend')
const venvDir = join(backendDir, '.venv')
const venvPython = join(venvDir, isWin ? 'Scripts' : 'bin', isWin ? 'python.exe' : 'python')

function run(label, command, args, cwd = root) {
  console.log(`\n▶ ${label}`)
  const result = spawnSync(command, args, { cwd, stdio: 'inherit', shell: isWin, env: process.env })
  if (result.status !== 0) {
    console.error(`\n✗ ${label} failed`)
    process.exit(result.status ?? 1)
  }
}

function resolvePython() {
  const candidates = isWin
    ? [
        ['py', ['-3']],
        ['python', []],
      ]
    : [
        ['python3', []],
        ['python', []],
      ]

  for (const [cmd, prefix] of candidates) {
    const check = spawnSync(cmd, [...prefix, '--version'], { stdio: 'pipe', shell: isWin })
    if (check.status === 0) {
      return { cmd, prefix }
    }
  }
  return null
}

function resolveUv() {
  const check = spawnSync(isWin ? 'uv.cmd' : 'uv', ['--version'], { stdio: 'pipe', shell: isWin })
  return check.status === 0 ? (isWin ? 'uv.cmd' : 'uv') : null
}

console.log('AI Citation Optimizer — setup')
console.log(`Platform: ${platform()}`)

if (!existsSync(join(root, '.env')) && existsSync(join(root, '.env.example'))) {
  console.log('\nℹ Copy .env.example to .env and add your API keys before running the app.')
}

const python = resolvePython()
const uv = resolveUv()

if (!existsSync(venvDir)) {
  if (uv) {
    run('Create Python venv (uv)', uv, ['venv', venvDir], backendDir)
  } else if (python) {
    run('Create Python venv', python.cmd, [...python.prefix, '-m', 'venv', venvDir], backendDir)
  } else {
    console.error(
      '\n✗ Python not found. Install Python 3.10+ or uv:\n' +
        '  - macOS: brew install python@3.12\n' +
        '  - WSL/Ubuntu: sudo apt install python3 python3-venv python3-pip\n' +
        '  - Windows: https://www.python.org/downloads/\n' +
        '  - Any OS (uv): curl -LsSf https://astral.sh/uv/install.sh | sh',
    )
    process.exit(1)
  }
}

if (!existsSync(venvPython)) {
  console.error(`\n✗ Virtualenv python not found at ${venvPython}`)
  process.exit(1)
}

run('Install backend dependencies', venvPython, ['-m', 'pip', 'install', '--upgrade', 'pip'])
run('Install backend requirements', venvPython, ['-m', 'pip', 'install', '-r', 'requirements.txt'], backendDir)
run('Install Playwright Chromium', venvPython, ['-m', 'playwright', 'install', 'chromium'], backendDir)

if (!isWin) {
  const deps = spawnSync(venvPython, ['-m', 'playwright', 'install-deps', 'chromium'], {
    cwd: backendDir,
    stdio: 'inherit',
  })
  if (deps.status !== 0) {
    console.log(
      '\nℹ Playwright system libraries may need manual install (Linux/WSL):\n' +
        '  sudo $(dirname $(which python3))/playwright install-deps\n' +
        '  — or use Docker: npm run docker:up',
    )
  }
}

run('Enable corepack (pnpm)', isWin ? 'corepack.cmd' : 'corepack', ['enable'])
run('Install frontend dependencies', isWin ? 'pnpm.cmd' : 'pnpm', ['install'], frontendDir)

console.log('\n✓ Setup complete. Start the app with: npm run dev')
console.log('  Or with Docker (all platforms): npm run docker:up')
