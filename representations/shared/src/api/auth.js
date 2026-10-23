/**
 * Транспорты авторизации — единственное, чем представления реально
 * отличаются на уровне API.
 */

/** Web SPA: сессия в httpOnly-cookie, браузер шлёт её сам. */
export const cookieAuth = {
    headers: () => ({}),
    requestInit: { credentials: 'include' },
}

/**
 * Telegram Mini App: initData в заголовке Authorization.
 * Геттер, а не значение, — initData читается на каждом запросе.
 */
export const initDataAuth = (getInitData) => ({
    headers: () => ({ Authorization: getInitData() || '' }),
    requestInit: {},
})
