import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, lazyPlugins } from 'vite-plus'

// https://vite.dev/config/
export default defineConfig({
  fmt: {
    semi: false,
    singleQuote: true,
    trailingComma: 'all',
    printWidth: 100,
    sortPackageJson: false,
    sortTailwindcss: {},
    ignorePatterns: ['.agents', 'dist', 'node_modules'],
  },
  lint: {
    plugins: ['typescript', 'unicorn', 'oxc', 'react', 'vitest'],
    categories: {
      correctness: 'error',
    },
    rules: {
      'typescript/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
        },
      ],
      'vite-plus/prefer-vite-plus-imports': 'error',
    },
    env: {
      builtin: true,
      browser: true,
    },
    ignorePatterns: ['dist', '.agents', 'node_modules'],
    options: {
      typeAware: true,
      typeCheck: true,
    },
    jsPlugins: [
      {
        name: 'vite-plus',
        specifier: 'vite-plus/oxlint-plugin',
      },
    ],
  },
  plugins: lazyPlugins(() => [tailwindcss(), react({ jsxRuntime: 'automatic' })]),
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    fileParallelism: true,
    maxWorkers: '100%',
  },
})
