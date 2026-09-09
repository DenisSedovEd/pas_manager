import { createApp, defineAsyncComponent } from 'vue'
import App from './App.vue'

const app = createApp(App)

app.config.errorHandler = (error) => {
  console.error('Mini app error:', error)
  const root = document.getElementById('app')
  if (root) {
    root.innerHTML = `
      <div style="padding:24px;font-family:sans-serif;text-align:center">
        <p style="font-size:32px;margin:0 0 12px">⚠️</p>
        <p style="margin:0 0 8px;font-weight:600">Ошибка загрузки</p>
        <p style="margin:0;color:#888;font-size:14px">${error?.message || error}</p>
      </div>
    `
  }
}

window.addEventListener('error', (event) => {
  app.config.errorHandler(event.error || new Error(event.message))
})

window.addEventListener('unhandledrejection', (event) => {
  app.config.errorHandler(event.reason || new Error('Unhandled promise rejection'))
})

app.mount('#app')
