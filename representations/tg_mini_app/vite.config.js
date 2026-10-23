import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/tg/',
  // @pas/shared — воркспейс-пакет; страхуемся от двух копий Vue при hoisting
  resolve: {
    dedupe: ['vue'],
  },
  build: {
    target: ['es2020', 'safari14', 'chrome87'],
  },
  server: {
    port: 5173,
    // Разрешаем любые хосты для разработки через туннели
    allowedHosts: true,
    // Важно: заставляем сервер слушать внешний интерфейс
    host: '0.0.0.0',
    proxy: {
      '/pas-manager': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})