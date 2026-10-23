import { inject } from 'vue'

export const PLATFORM_KEY = Symbol('pas:platform')

/**
 * Чем представления расходятся помимо транспорта авторизации: диалоги и
 * тактильная отдача. Интерфейс один:
 *   alert(message)            → Promise<void>
 *   confirm(message)          → Promise<boolean>
 *   haptic(kind)              → void   ('success' | 'warning' | 'error' | 'light' | 'medium')
 */

/** Запасной вариант — нативные диалоги браузера. */
export const browserPlatform = {
    async alert(message) {
        window.alert(message)
    },
    async confirm(message) {
        return window.confirm(message)
    },
    haptic() {},
}

/**
 * Намеренно с запасным вариантом, а не с исключением: общий компонент не должен
 * падать из-за забытого provide — диалог важен, но не настолько.
 */
export function usePlatform() {
    return inject(PLATFORM_KEY, browserPlatform)
}
