import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'
import AdvancedView from '../views/AdvancedView.vue'
import AdvancedResultView from '../views/AdvancedResultView.vue'

const routes = [
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/SearchView.vue')
  },
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
    path: '/advanced',
    name: 'advanced',
    component: AdvancedView
  },
  {
    path: '/advanced-result',
    name: 'advanced-result',
    component: AdvancedResultView
  },
  {
    path: '/',
    redirect: '/mi'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
