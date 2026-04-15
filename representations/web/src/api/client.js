export const BASE_URL = '/pas-manager/v1'

export function bearer() {
    const t = sessionStorage.getItem('web_token')
    return t ? `Bearer ${t}` : ''
}
