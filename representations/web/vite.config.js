import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    base: '/web/',
    // @pas/shared — воркспейс-пакет; страхуемся от двух копий Vue при hoisting
    resolve: {
        dedupe: ['vue'],
    },
    server: {
        port: 5174,
        host: '0.0.0.0',
        proxy: {
            '/pas-manager': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            }
        }
    }
})
