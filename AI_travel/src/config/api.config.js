/**
 * API configuration
 * 统一管理API相关配置
 */

// 根据环境变量或开发/生产环境自动选择API地址
const getApiBaseUrl = () => {
 
  // 生产环境可以配置为实际的服务器地址
  return 'http://staging-llm.search.miui.srv'
}

export const API_CONFIG = {
  // API基础地址
  BASE_URL: getApiBaseUrl(),
  
  // API端点
  ENDPOINTS: {
    STREAM: '/agent-api/stream',
    HEALTH: '/agent-api/health',
    SESSIONS: '/agent-api/sessions',
    STATUS: '/agent-api/status'
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
