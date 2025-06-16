import { createApp } from 'vue'
import App from './App.vue'
import './index.css' // Import Tailwind CSS
import appConfig from './config/app.config'
import router from './router'
import 'katex/dist/katex.min.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// Set the initial document title from config
document.title = appConfig.defaultPageTitle

// Create and mount the app
const app = createApp(App)

// Make config available globally
app.config.globalProperties.$appConfig = appConfig

// Use router
app.use(router)
app.use(ElementPlus)

app.mount('#app')
