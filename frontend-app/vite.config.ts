import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const OFFICE_BACKEND = (process.env.OFFICE_BACKEND_URL || 'http://127.0.0.1:19800').replace(/\/$/, '')

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
    // Local dev: keep `VITE_API_BASE_URL` empty and let Vite proxy API calls to the Flask backend.
    proxy: {
      '/health': { target: OFFICE_BACKEND, changeOrigin: true },
      '/status': { target: OFFICE_BACKEND, changeOrigin: true },
      '/live': { target: OFFICE_BACKEND, changeOrigin: true },
      '/tasks': { target: OFFICE_BACKEND, changeOrigin: true },
      '/ollama': { target: OFFICE_BACKEND, changeOrigin: true },
      '/logs': { target: OFFICE_BACKEND, changeOrigin: true },
      '/news': { target: OFFICE_BACKEND, changeOrigin: true },
      '/api': { target: OFFICE_BACKEND, changeOrigin: true },
    },
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
