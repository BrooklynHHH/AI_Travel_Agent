import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import MovieView from '../views/MovieView.vue'
import BaiduView from '../views/BaiduView.vue'
import AdvancedView from '../views/AdvancedView.vue'
import AdvancedResultView from '../views/AdvancedResultView.vue'
import OcrView from '../views/OcrView.vue'
import PodcastView from '../views/PodcastView.vue'
import AiNewsPodcastView from '../views/AiNewsPodcastView.vue'
import FortuneView from '../views/FortuneView.vue'

import MultiAgentMixExpertView from '../views/MultiAgentMixExpertView.vue'
import VideoGenerationView from '@/views/VideoGenerationView.vue'
import ImageGenerationView from '@/views/ImageGenerationView.vue'

export const routes = [ // Add export here
  {
    path: '/travel',
    name: '旅游',
    component: () => import('../views/TravelPlanning.vue')
  },
  {
    path: '/podcast',
    name: '播客',
    component: PodcastView
  },
  {
    path: '/ai-news-podcast',
    name: 'AI日报',
    component: AiNewsPodcastView
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
    path: '/video',
    name: '视频生成', // Translated
    component: VideoGenerationView
  },
  {
    path: '/image',
    name: '图像生成',
    component: ImageGenerationView
  },
  {
    path: '/ocr',
    name: 'ocr', // Translated
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
    path: '/fortune',
    name: '算命',
    component: FortuneView
  },
  {
    path: '/route-links',
    name: 'RouteLinks',
    component: () => import('../views/RouteLinksView.vue')
  },
  {
    path: '/',
    redirect: '/advanced' // Change redirect to the new page
  },
  {
    path: '/podcast-detail',
    name: 'PodcastDetail',
    component: () => import('../views/PodcastDetailView.vue')
  },
  {
    path: '/aliyun-mcp-delivery',
    name: '全国快递物流查询MCP',
    component: () => import('../views/DeliveryMcpView.vue')
  },
  {
    path: '/aliyun-mcp-stocks',
    name: '股票实时行情查询MCP',
    component: () => import('../views/StocksMcpView.vue')
  },
  {
    path: '/aliyun-mcp-weather',
    name: '天气预报MCP',
    component: () => import('../views/WeatherMcpView.vue')
  },
  {
    path: '/aliyun-mcp-quark-search',
    name: '夸克搜索MCP',
    component: () => import('../views/QuarkSearchMcpView.vue')
  },
  {
    path: '/aliyun-mcp-vin',
    name: 'VIN码车架号查询MCP',
    component: () => import('../views/VinMcpView.vue')
  },
  {
    path: '/aliyun-mcp-company-info',
    name: '企业基本工商信息查询MCP',
    component: () => import('../views/CompanyInfoMcpView.vue')
  },
  {
    path: '/aliyun-mcp-exchange-rate',
    name: '汇率查询转换MCP',
    component: () => import('../views/ExchangeRateMcpView.vue')
  },
  {
    path: '/aliyun-mcp-barcode',
    name: '商品条码查询MCP',
    component: () => import('../views/BarCodeMcpView.vue')
  },
  {
    path: '/aliyun-mcp-moji-weather',
    name: '墨迹天气MCP',
    component: () => import('../views/MojiWeatherMcpView.vue')
  },
  {
    path: '/aliyun-mcp-invoice-checker',
    name: '发票真伪查询MCP',
    component: () => import('../views/InvoiceCheckerMcpView.vue')
  },
  {
    path: '/aliyun-mcp-isbn',
    name: 'ISBN书号查询MCP',
    component: () => import('../views/IsbnMcpView.vue')
  },
  {
    path: '/pic-translate',
    name: '图片翻译',
    component: () => import('../views/PicTranslateView.vue')
  },
  {
    path: '/text-recognition',
    name: '识文字',
    component: () => import('@/views/TextRecognizeView.vue')
  },
  {
    path: '/baidu-faxingbao',
    name: '法行宝',
    component: () => import('../views/BaiduFaXingBaoView.vue')
  },
  {
    path: '/qianfan',
    name: '千帆',
    component: () => import('../views/QianfanVideoGenerate.vue')
  },
  {
    path: '/baidu-wenku',
    name: '百度文库',
    component: () => import('../views/BaiduWenKuView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
