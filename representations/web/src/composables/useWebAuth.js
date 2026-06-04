import { ref, computed } from 'vue'

const authenticated = ref(false)

export function useWebAuth() {
    const isAuthenticated = computed(() => authenticated.value)

    async function login(masterPassword) {
        const res = await fetch('/pas-manager/v1/web/auth/unlock', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ master_password: masterPassword }),
        })
        if (!res.ok) {
            const data = await res.json().catch(() => ({}))
            throw new Error(data.detail || 'Неверный пароль')
        }
        authenticated.value = true
    }

    async function logout() {
        try {
            await fetch('/pas-manager/v1/web/auth/logout', {
                method: 'POST',
                credentials: 'include',
            })
        } finally {
            authenticated.value = false
        }
    }

    async function checkStatus() {
        try {
            const res = await fetch('/pas-manager/v1/web/auth/status', {
                credentials: 'include',
            })
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
