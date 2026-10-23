import { inject } from 'vue'

export const API_KEY = Symbol('pas:api')

/** Для общих компонентов: API приходит из приложения через app.provide(API_KEY, api). */
export function useApi() {
    const api = inject(API_KEY, null)
    if (!api) {
        throw new Error('API не предоставлен — нужен app.provide(API_KEY, createApi({...}))')
    }
    return api
}
