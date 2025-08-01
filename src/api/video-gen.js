import axios from 'axios'

const BASE_URL = 'http://staging-llm.search.miui.srv';
const DEV_URL = 'http://127.0.0.1:8080'

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL || DEV_URL,
  timeout: 300000, // 5分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`发起请求: ${config.method?.toUpperCase()} ${config.url}`, config.data)
    config.startTime = Date.now()
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const responseTime = Date.now() - response.config.startTime
    console.log(`请求完成: ${response.config.url} (${responseTime}ms)`, response.data)
    return response.data
  },
  error => {
    const responseTime = error.config ? Date.now() - error.config.startTime : 0
    console.error(`请求失败: ${error.config?.url} (${responseTime}ms)`, error.response?.data || error.message)
    
    // 统一错误处理
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error || 
                        error.message || 
                        '请求失败'
    
    return Promise.reject(new Error(errorMessage))
  }
)

/**
 * 获取火山平台可用模型列表
 */
export async function getVolcModels() {
  try {
    const response = await api.get('/video-gen/volc/models')
    return response || []
  } catch (error) {
    console.error('获取火山模型列表失败:', error)
    throw error
  }
}

/**
 * 获取可灵平台可用模型列表
 */
export async function getKlingModels() {
  try {
    const response = await api.get('/video-gen/kling/models')
    return response || []
  } catch (error) {
    console.error('获取可灵模型列表失败:', error)
    throw error
  }
}

/**
 * 生成火山视频
 * @param {Object} request - 请求参数
 * @param {File} imageFile - 可选的参考图片文件
 */
export async function generateVolcVideo(request, imageFile = null) {
  try {
    const formData = new FormData()
    
    // 添加基本参数
    formData.append('prompt', request.prompt)
    formData.append('resolution', request.resolution || '1080p')
    formData.append('model', request.model)
    formData.append('ratio', request.ratio || '16:9')
    formData.append('duration', request.duration || 5)
    formData.append('framepersecond', request.framepersecond || 24)
    formData.append('watermark', request.watermark || false)
    formData.append('seed', request.seed || -1)
    formData.append('camerafixed', request.camerafixed || false)
    
    // 添加图片文件（如果有）
    if (imageFile) {
      formData.append('image', imageFile)
    }
    
    const response = await api.post('/video-gen/volc/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response
  } catch (error) {
    console.error('火山视频生成失败:', error)
    throw error
  }
}

/**
 * 生成可灵视频
 * @param {Object} request - 请求参数
 * @param {File} imageFile - 可选的参考图片文件
 */
export async function generateKlingVideo(request, imageFile = null) {
  try {
    const formData = new FormData()
    
    // 添加基本参数
    formData.append('prompt', request.prompt)
    formData.append('model', request.model || '')
    formData.append('ratio', request.ratio || '16:9')
    formData.append('duration', request.duration || 5)
    formData.append('resolution', request.resolution || '1080p')
    formData.append('framepersecond', request.framepersecond || 24)
    formData.append('watermark', request.watermark !== undefined ? request.watermark : false)
    formData.append('seed', request.seed !== undefined ? request.seed : -1)
    formData.append('camerafixed', request.camerafixed !== undefined ? request.camerafixed : false)
    
    // 添加图片文件（如果有）
    if (imageFile) {
      // 确保使用正确的文件名和类型
      const fileName = imageFile.name || 'image.jpg';
      const fileType = imageFile.type || 'image/jpeg';
      console.log(`上传图片: ${fileName}, 类型: ${fileType}`);
      
      // 使用原始文件对象
      formData.append('image', imageFile, fileName);
    }
    
    console.log('可灵视频生成请求参数:', {
      prompt: request.prompt,
      model: request.model || '',
      ratio: request.ratio || '16:9',
      duration: request.duration || 5,
      resolution: request.resolution || '1080p',
      framepersecond: request.framepersecond || 24,
      watermark: request.watermark !== undefined ? request.watermark : false,
      seed: request.seed !== undefined ? request.seed : -1,
      camerafixed: request.camerafixed !== undefined ? request.camerafixed : false,
      hasImage: !!imageFile
    })
    
    const response = await api.post('/video-gen/kling/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response
  } catch (error) {
    console.error('可灵视频生成失败:', error)
    throw error
  }
}

/**
 * 查询火山任务状态
 * @param {string} taskId - 任务ID
 * @param {string} type - 任务类型（可选）
 */
export async function queryVolcTask(taskId, type = null) {
  try {
    const params = { task_id: taskId }
    if (type) {
      params.type = type
    }
    
    const response = await api.get('/video-gen/volc/query', { params })
    return response
  } catch (error) {
    console.error('查询火山任务状态失败:', error)
    throw error
  }
}

/**
 * 查询可灵任务状态
 * @param {string} taskId - 任务ID
 * @param {string} type - 任务类型
 */
export async function queryKlingTask(taskId, type = 'text2video') {
  try {
    const params = { 
      task_id: taskId,
      type: type
    }
    
    const response = await api.get('/video-gen/kling/query', { params })
    return response
  } catch (error) {
    console.error('查询可灵任务状态失败:', error)
    throw error
  }
}

/**
 * 取消火山任务
 * @param {string} taskId - 任务ID
 */
export async function cancelVolcTask(taskId) {
  try {
    const response = await api.get(`/video-gen/volc/cancel/${taskId}`)
    return response
  } catch (error) {
    console.error('取消火山任务失败:', error)
    throw error
  }
}

/**
 * 查询可灵资源包
 */
export async function queryKlingResource() {
  try {
    const response = await api.get('/video-gen/kling/resource')
    return response
  } catch (error) {
    console.error('查询可灵资源包失败:', error)
    throw error
  }
}

// 导出api实例，供其他地方使用
export default api