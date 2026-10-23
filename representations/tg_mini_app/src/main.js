import { createApp } from 'vue'
import { API_KEY } from '@pas/shared/composables/useApi.js'
import { PLATFORM_KEY } from '@pas/shared/platform/index.js'
import App from './App.vue'
import { api } from './api.js'
import { tgPlatform } from './platform.js'

const app = createApp(App)
app.provide(API_KEY, api)
app.provide(PLATFORM_KEY, tgPlatform)

// Экран ошибки имеет смысл только до того, как приложение отрисовалось.
// После монтирования единичная асинхронная ошибка не должна стирать рабочий UI
// (иначе, например, сбой биометрии уносит с собой и вход по паролю).
let isMounted = false

const showBootstrapError = (error) => {
    console.error('Mini app error:', error)
    if (isMounted) return

    const root = document.getElementById('app')
    if (!root) return

    root.replaceChildren()
    const box = document.createElement('div')
    box.style.cssText = 'padding:24px;font-family:sans-serif;text-align:center'

    const icon = document.createElement('p')
    icon.style.cssText = 'font-size:32px;margin:0 0 12px'
    icon.textContent = '⚠️'

    const title = document.createElement('p')
    title.style.cssText = 'margin:0 0 8px;font-weight:600'
    title.textContent = 'Ошибка загрузки'

    const detail = document.createElement('p')
    detail.style.cssText = 'margin:0;color:#888;font-size:14px'
    detail.textContent = error?.message || String(error)

    box.append(icon, title, detail)
    root.append(box)
}

app.config.errorHandler = showBootstrapError

window.addEventListener('error', (event) => {
    showBootstrapError(event.error || new Error(event.message))
})

window.addEventListener('unhandledrejection', (event) => {
    showBootstrapError(event.reason || new Error('Unhandled promise rejection'))
})

app.mount('#app')
isMounted = true
