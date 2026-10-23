export const BASE_URL = '/pas-manager/v1'

/** Бэкенд отдаёт ошибки как {"detail": "..."} — достаём, если получится. */
const readDetail = async (res) => {
    try {
        const body = await res.json()
        return body?.detail || null
    } catch {
        return null
    }
}

/**
 * Единый HTTP-клиент для всех представлений.
 *
 * Эндпоинты у web и mini app одни и те же — различается только транспорт
 * авторизации (см. backend/dependencies.py::get_current_user, который
 * принимает и cookie, и заголовок). Поэтому транспорт — параметр клиента,
 * а не аргумент каждого метода.
 *
 * @param auth              адаптер из ./auth.js
 * @param onSessionExpired  вызывается на любой 401
 */
export function createApiClient({ auth, onSessionExpired = null } = {}) {
    let sessionExpiredHandler = onSessionExpired

    const setSessionExpiredHandler = (handler) => {
        sessionExpiredHandler = handler
    }

    const buildUrl = (path) => `${BASE_URL}${path}`

    /** Сырой ответ — нужен там, где важен сам статус (например, /category/all). */
    async function raw(path, { method = 'GET', body, headers = {} } = {}) {
        const init = {
            method,
            ...auth.requestInit,
            headers: { ...auth.headers(), ...headers },
        }

        if (body instanceof FormData) {
            // Content-Type с boundary проставит браузер
            init.body = body
        } else if (body !== undefined) {
            init.headers['Content-Type'] = 'application/json'
            init.body = JSON.stringify(body)
        }

        const res = await fetch(buildUrl(path), init)
        if (res.status === 401) sessionExpiredHandler?.()
        return res
    }

    /** Разобранный JSON; на !ok бросает detail от бэкенда либо errorMessage. */
    async function request(path, { errorMessage = 'Ошибка запроса', ...options } = {}) {
        const res = await raw(path, options)
        if (!res.ok) throw new Error((await readDetail(res)) || errorMessage)
        return res.json()
    }

    return { BASE_URL, buildUrl, raw, request, setSessionExpiredHandler }
}
