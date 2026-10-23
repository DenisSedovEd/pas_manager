import { api } from './api.js'

/**
 * Авторизация Mini App: /main/auth/*.
 *
 * Эти ручки отвечают не только двумя сотнями: 403 на неверный пароль и на
 * непрошедший био-токен, 401 на невалидный initData. Поэтому возвращаем явный
 * результат { ok, status, detail, data }, а не голое тело: иначе отказ выглядит
 * как успех с пустыми полями, и вызывающий код молча ничего не делает.
 */
const call = async (path, options) => {
    const res = await api.client.raw(path, options)
    let data = {}
    try {
        data = (await res.json()) ?? {}
    } catch {
        // пустое или не-JSON тело
    }
    return { ok: res.ok, status: res.status, detail: data?.detail || null, data }
}

const get = (path) => call(path)
const post = (path, body) => call(path, { method: 'POST', body })

export const authApi = {
    getStatus: () => get('/main/auth/status'),

    getBioSettings: () => get('/main/auth/bio-settings'),

    unlockWithPassword: (masterPassword) =>
        post('/main/auth/unlock', { master_password: masterPassword }),

    unlockWithBiometric: (bioToken) =>
        post('/main/auth/unlock-biometric', { bio_token: bioToken }),

    enableBiometric: (bioToken) =>
        post('/main/auth/enable-biometric', { bio_token: bioToken }),
}
