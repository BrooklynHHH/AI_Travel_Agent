import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'

const routes = [
  {
    path: '/',
    name: 'chat',
    component: MovieView
  },
  {
    path: '/movie',
    name: 'movie',
    component: MovieView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
