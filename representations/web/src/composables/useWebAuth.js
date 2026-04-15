import { ref, computed } from 'vue'

const TOKEN_KEY = 'web_token'
const token = ref(sessionStorage.getItem(TOKEN_KEY) || '')

export function useWebAuth() {
    const isAuthenticated = computed(() => !!token.value)

    function getToken() {
        return token.value
    }

    function getAuthHeader() {
        return token.value ? `Bearer ${token.value}` : ''
    }

    async function login(masterPassword) {
        const res = await fetch('/pas-manager/v1/web/auth/unlock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ master_password: masterPassword }),
        })
        if (!res.ok) {
            const data = await res.json().catch(() => ({}))
            throw new Error(data.detail || 'Неверный пароль')
        }
        const data = await res.json()
        token.value = data.token
        sessionStorage.setItem(TOKEN_KEY, data.token)
    }

    async function logout() {
        try {
            await fetch('/pas-manager/v1/web/auth/logout', {
                method: 'POST',
                headers: { Authorization: getAuthHeader() },
            })
        } finally {
            token.value = ''
            sessionStorage.removeItem(TOKEN_KEY)
        }
    }

    async function checkStatus() {
        if (!token.value) return false
        try {
            const res = await fetch('/pas-manager/v1/web/auth/status', {
                headers: { Authorization: getAuthHeader() },
            })
            if (!res.ok) {
                token.value = ''
                sessionStorage.removeItem(TOKEN_KEY)
                return false
            }
            const data = await res.json()
            return data.is_unlocked
        } catch {
            return false
        }
    }

    return { isAuthenticated, getToken, getAuthHeader, login, logout, checkStatus }
}
