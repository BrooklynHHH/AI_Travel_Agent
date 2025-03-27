import { createApp } from 'vue'
import App from './App.vue'
import appConfig from './config/app.config'

// Set the initial document title from config
document.title = appConfig.defaultPageTitle

// Create and mount the app
const app = createApp(App)

// Make config available globally
app.config.globalProperties.$appConfig = appConfig

app.mount('#app')
