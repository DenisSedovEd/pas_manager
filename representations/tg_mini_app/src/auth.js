import { api } from './api.js'

/**
 * Авторизация Mini App: /main/auth/*.
 *
 * Эти ручки намеренно идут через raw: бэкенд отвечает 403 на неверный пароль
 * и 401 на невалидный initData, а вызывающий код разбирает тело сам
 * (проверяет res.ok / res.is_unlocked), а не ловит исключение.
 */
const readJson = async (res) => {
    try {
        return await res.json()
    } catch {
        return {}
    }
}

const post = async (path, body) =>
    readJson(await api.client.raw(path, { method: 'POST', body }))

const get = async (path) => readJson(await api.client.raw(path))

export const authApi = {
    getStatus: () => get('/main/auth/status'),

    unlockWithPassword: (masterPassword) =>
        post('/main/auth/unlock', { master_password: masterPassword }),

    unlockWithBiometric: (bioToken) =>
        post('/main/auth/unlock-biometric', { bio_token: bioToken }),

    logout: () => post('/main/auth/logout'),

    getBioSettings: () => get('/main/auth/bio-settings'),

    enableBiometric: (payload) => post('/main/auth/enable-biometric', payload),
}
