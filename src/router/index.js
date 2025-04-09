import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'

const routes = [
  {
    path: '/mi',
    name: 'mi',
    component: ChatView
  },
  {
    path: '/movie',
    name: 'movie',
    component: MovieView
  },
  {
    path: '/baidu',
    name: 'baidu',
    component: BaiduView
  },
  {
    path: '/',
    redirect: '/baidu'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
