import { createRouter, createWebHistory } from 'vue-router'
import MiView from '../views/MiView.vue'

const routes = [
  {
    path: '/mi',
    name: 'mi',
    component: MiView
  },
  {
    path: '/',
    name: 'default',
    component: MiView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
