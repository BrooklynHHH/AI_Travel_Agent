import { createApp } from 'vue'
import App from './App.vue'
import './index.css' // Import Tailwind CSS
import appConfig from './config/app.config'
import router from './router'

// Set the initial document title from config
document.title = appConfig.defaultPageTitle

// Create and mount the app
const app = createApp(App)

// Make config available globally
app.config.globalProperties.$appConfig = appConfig

// Use router
app.use(router)

app.mount('#app')
