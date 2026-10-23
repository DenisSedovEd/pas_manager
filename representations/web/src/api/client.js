export const BASE_URL = '/pas-manager/v1'

let onSessionExpired = null

export function setSessionExpiredHandler(handler) {
    onSessionExpired = handler
}

export async function apiFetch(url, options = {}) {
    const res = await fetch(url, options)
    if (res.status === 401) {
        onSessionExpired?.()
    }
    return res
}
