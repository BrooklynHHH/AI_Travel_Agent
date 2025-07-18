import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'
import AdvancedView from '../views/AdvancedView.vue'
import AdvancedResultView from '../views/AdvancedResultView.vue'
import OcrView from '../views/OcrView.vue'
import PodcastView from '../views/PodcastView.vue'

import TravelView from '../views/TravelView.vue'
import RouteLinksView from '../views/RouteLinksView.vue'
import MultiAgentMixExpertView from '../views/MultiAgentMixExpertView.vue'

export const routes = [ // Add export here
  {
    path: '/route-links',
    name: '页面索引', // Translated
    component: RouteLinksView
  },
  {
    path: '/podcast',
    name: '播客',
    component: PodcastView
  },
  {
    path: '/search',
    name: '搜索', // Translated
    component: () => import('../views/SearchView.vue')
  },
  {
    path: '/travel',
    name: '旅游',
    component: TravelView
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
    name: '高级搜索结果', // Keep Chinese name
    component: AdvancedResultView
  },
  {
    path: '/multi-agent-experts',
    name: '多专家',
    component: MultiAgentMixExpertView
  },
  {
    path: '/',
    redirect: '/route-links' // Change redirect to the new page
  },
  {
    path: '/podcast-detail',
    name: 'PodcastDetail',
    component: () => import('../views/PodcastDetailView.vue')
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
