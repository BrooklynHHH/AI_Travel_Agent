import { createRouter, createWebHistory } from 'vue-router'
import MiView from '../views/MiView.vue'
import MovieView from '../views/MovieView.vue'

const routes = [
  {
    path: '/mi',
    name: 'mi',
    component: MiView
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
