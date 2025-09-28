import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    allowedHosts: true,
    proxy: {
      '/api/ingestion': {
        target: 'http://ai_analyst_for_startups-ingestion-service-1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ingestion/, ''),
      },
    },
  }
})