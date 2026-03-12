import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'vue3-emoji-picker/css'

const app = createApp(App)
app.use(router)
app.mount('#app')