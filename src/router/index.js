import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieChatView from '../views/MovieChatView.vue'

const routes = [
  {
    path: '/',
    name: 'chat',
    component: ChatView
  },
  {
    path: '/movieChat',
    name: 'movieChat',
    component: MovieChatView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
