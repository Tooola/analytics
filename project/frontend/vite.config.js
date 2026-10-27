import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    // `vite preview` (Web Service Render) bloque les Host inconnus :
    // autoriser le domaine Render du dashboard (+ tout sous-domaine
    // onrender.com pour les futurs redéploiements/renommages).
    allowedHosts: ['analytics-1-ygzl.onrender.com', '.onrender.com'],
  },
})
