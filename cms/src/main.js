import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupHttp } from './api/http'
import './styles/theme.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

setupHttp(router)

app.mount('#app')
