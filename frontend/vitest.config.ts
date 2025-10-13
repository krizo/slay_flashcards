import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    css: true,
    setupFiles: './vitest.setup.ts',
    pool: 'forks',
    poolOptions: {
      forks: {
        isolate: true,
      },
    },
    reporters: [
      ['default', {
        summary: true,
        verbose: false,
      }]
    ],
    // Compact output settings
    hideSkippedTests: true,
    onConsoleLog: () => false, // Hide console logs during tests
  },
});
