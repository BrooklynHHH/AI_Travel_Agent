/**
 * API configuration
 * 统一管理API相关配置
 */

// 根据环境变量或开发/生产环境自动选择API地址
const getApiBaseUrl = () => {
  // 如果有环境变量，优先使用环境变量
  // if (process.env.VUE_APP_API_BASE_URL) {
  //   return process.env.VUE_APP_API_BASE_URL
  // }
  
  // 开发环境默认使用localhost
  if (process.env.NODE_ENV === 'development') {
    // return 'http://10.225.167.204:5000'
    return "http://localhost:5000"
  }
  
  // 生产环境可以配置为实际的服务器地址
  // return 'http://10.225.167.204:5000'
  return "http://localhost:5000"
}

export const API_CONFIG = {
  // API基础地址
  BASE_URL: getApiBaseUrl(),
  
  // API端点
  ENDPOINTS: {
    STREAM: '/api/stream',
    HEALTH: '/api/health',
    SESSIONS: '/api/sessions',
    STATUS: '/api/status'
  },
  
  // 请求超时时间（毫秒）
  TIMEOUT: 30000,
  
  // 重试配置
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000
  }
}

export default API_CONFIG
