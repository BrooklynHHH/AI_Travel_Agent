import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'
import AdvancedView from '../views/AdvancedView.vue'
import AdvancedResultView from '../views/AdvancedResultView.vue'
import MultiAgentView from '../views/MultiAgentView.vue'
import OcrView from '../views/OcrView.vue'

import TravelView from '../views/TravelView.vue'
import MultiAgentMixExpertView from '../views/MultiAgentMixExpertView.vue'

export const routes = [ // Add export here
  {
    path: '/multi-turn-chat',
    name: '多轮对话',
    component: () => import('../views/MultiTurnChatView.vue')
  },
  {
    path: '/multi-turn-chat-simple',
    name: '多轮对话-simple',
    component: () => import('../views/NewMultiTurnChatView_V1_2.vue')
  },
  {
    path: '/multi-turn-chat_v0',
    name: '多轮对话_v0',
    component: () => import('../views/MultiTurnChatView_v0.vue')
  },
  {
    path: '/supervisor-agent-fixed',
    name: 'SupervisorAgentFixed',
    component: () => import('../views/SupervisorAgentFixed.vue')
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
    name: '高级搜索结果', // Translated
    component: AdvancedResultView
  },
  {
    path: '/multi-agent',
    name: '多智能体', // Translated
    component: MultiAgentView
  },
  {
    path: '/route-links',
    name: 'RouteLinks',
    component: () => import('../views/RouteLinksView.vue')
  },
  {
    path: '/',
    redirect: '/route-links' // Change redirect to the new page
  },
  {
    path: '/multi-agent-experts',
    name: 'multi-agent-experts',
    component: MultiAgentMixExpertView
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
