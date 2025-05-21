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
    name: '页面索引', // Translated
    component: RouteLinksView
  },
  {
    path: '/search',
    name: '搜索', // Translated
    component: () => import('../views/SearchView.vue')
  },
  {
    path: '/mi',
    name: '小米垂域', // Translated
    component: ChatView
  },
  {
    path: '/ocr',
    name: '搜题', // Translated
    component: OcrView
  },
  {
    path: '/movie',
    name: '影视', // Translated
    component: MovieView
  },
  {
    path: '/baidu',
    name: '百度', // Translated
    component: BaiduView
  },
  {
    path: '/advanced',
    name: '高级版', // Translated
    component: AdvancedView
  },
  {
    path: '/advanced-result',
    name: '高级搜索结果', // Translated
    component: AdvancedResultView
  },
  {
    path: '/multi-agent',
    name: '多智能体', // Translated
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
