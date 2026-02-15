import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// 不需要dev-tools的话将以下注释掉
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    // 不需要dev-tools的话将以下注释掉
    // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0', // 指定0.0.0.0，允许公网访问
    port: 24610,
    proxy: {
      '/api': {
        target: 'http://localhost:42611',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
