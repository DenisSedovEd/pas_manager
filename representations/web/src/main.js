import { createApp } from 'vue'
import { API_KEY } from '@pas/shared/composables/useApi.js'
import { PLATFORM_KEY } from '@pas/shared/platform/index.js'
import './style.css'
import App from './App.vue'
import { api } from './api.js'
import { webPlatform } from './platform.js'

createApp(App)
    .provide(API_KEY, api)
    .provide(PLATFORM_KEY, webPlatform)
    .mount('#app')
