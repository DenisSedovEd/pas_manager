import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')
    const apiProxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000'

    return {
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
                    target: apiProxyTarget,
                    changeOrigin: true,
                }
            }
        }
    }
})
