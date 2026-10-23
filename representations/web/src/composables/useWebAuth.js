import { ref, computed } from 'vue'
import { api } from '../api.js'

const authenticated = ref(false)

api.setSessionExpiredHandler(() => {
    authenticated.value = false
})

export function useWebAuth() {
    const isAuthenticated = computed(() => authenticated.value)

    async function login(masterPassword) {
        await api.client.request('/web/auth/unlock', {
            method: 'POST',
            body: { master_password: masterPassword },
            errorMessage: 'Неверный пароль',
        })
        authenticated.value = true
    }

    async function logout() {
        try {
            await api.client.raw('/web/auth/logout', { method: 'POST' })
        } finally {
            authenticated.value = false
        }
    }

    // До входа ручка отвечает 401 — это нормальный путь, а не ошибка
    async function checkStatus() {
        try {
            const res = await api.client.raw('/web/auth/status')
            if (!res.ok) {
                authenticated.value = false
                return false
            }
            const data = await res.json()
            authenticated.value = data.is_unlocked
            return data.is_unlocked
        } catch {
            authenticated.value = false
            return false
        }
    }

    return { isAuthenticated, login, logout, checkStatus }
}
