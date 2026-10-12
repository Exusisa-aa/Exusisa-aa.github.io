import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { vReveal } from './directives/reveal'
import './styles/index.css'

const app = createApp(App)

app.use(createPinia())
app.directive('reveal', vReveal)

app.mount('#app')
