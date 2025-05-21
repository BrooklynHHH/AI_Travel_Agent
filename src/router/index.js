import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'
import AdvancedView from '../views/AdvancedView.vue'
import AdvancedResultView from '../views/AdvancedResultView.vue'
import MultiAgentView from '../views/MultiAgentView.vue'
import OcrView from '../views/OcrView.vue'
import RouteLinksView from '../views/RouteLinksView.vue'


export const routes = [ // Add export here
  {
    path: '/route-links',
    name: 'RouteLinks',
    component: RouteLinksView
  },
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
    path: '/ocr',
    name: 'ocr',
    component: OcrView
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
    path: '/multi-agent',
    name: 'multi-agent',
    component: MultiAgentView
  },
  {
    path: '/',
    redirect: '/route-links' // Change redirect to the new page
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
