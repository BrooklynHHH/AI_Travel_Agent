/**
 * 旅游规划 API 客户端
 * 处理与 FastAPI 后端的通信
 */

class TravelPlanningAPI {
  constructor(baseURL = 'http://staging-llm.search.miui.srv') {
    this.baseURL = baseURL
    this.sessionId = null
  }

  /**
   * 通用请求方法
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    }

    try {
      const response = await fetch(url, { ...defaultOptions, ...options })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error)
      throw error
    }
  }

  /**
   * 需求收集
   */
  async collectNeeds(userInput, inputHistory = []) {
    const response = await this.request('/api/need-collection', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        session_id: this.sessionId,
        input_history: inputHistory
      })
    })

    // 更新会话ID
    if (response.session_id) {
      this.sessionId = response.session_id
    }

    return response
  }

  /**
   * 增强需求收集 - 按照main.py逻辑实现
   */
  async collectNeedsEnhanced(userInput, inputHistory = []) {
    const response = await this.request('/api/need-collection-enhanced', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        session_id: this.sessionId,
        input_history: inputHistory
      })
    })

    // 更新会话ID
    if (response.session_id) {
      this.sessionId = response.session_id
    }

    return response
  }

  /**
   * 旅游规划（非流式）
   */
  async planTravel(userRequest, confirmedNeeds = []) {
    const response = await this.request('/api/travel-planning', {
      method: 'POST',
      body: JSON.stringify({
        user_request: userRequest,
        session_id: this.sessionId,
        confirmed_needs: confirmedNeeds
      })
    })

    // 更新会话ID
    if (response.session_id) {
      this.sessionId = response.session_id
    }

    return response
  }

  /**
   * 第一轮旅游规划（流式）- 对应 /api/travel-planning-stream
   */
  async planTravelStream(userRequest, sessionId, onUpdate, onComplete, onError) {
    try {
      const response = await fetch(`${this.baseURL}/api/travel-planning-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_request: userRequest,
          session_id: sessionId || this.sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      let reading = true
      while (reading) {
        const { done, value } = await reader.read()
        
        if (done) {
          reading = false
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // 处理完整的事件
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              // 详细输出中间过程
              console.log('🔄 [第一轮规划] 流式数据:', data)
              
              // 更新会话ID
              if (data.session_id) {
                this.sessionId = data.session_id
              }

              // 处理不同类型的事件 - 适配后端实际格式
              if (data.event === 'planning_step' || data.event === 'supervisor_output') {
                // 统一处理为supervisor_output格式
                const updateData = data.event === 'planning_step' ? data.data : data.data
                onUpdate && onUpdate(updateData)
              } else if (data.event === 'planning_complete') {
                onComplete && onComplete(data)
                break
              } else if (data.event === 'planning_start') {
                // 处理开始事件
                console.log('📍 规划开始:', data.data.message)
                onUpdate && onUpdate(data.data)
              } else if (data.event === 'error' || data.event === 'planning_error') {
                onError && onError(new Error(data.data.error))
                break
              } else {
                // 处理其他类型的事件
                console.log('📦 其他事件:', data.event, data.data)
                onUpdate && onUpdate(data.data)
              }
            } catch (e) {
              console.warn('解析流式数据失败:', e, line)
            }
          }
        }
      }
    } catch (error) {
      console.error('第一轮流式规划请求失败:', error)
      onError && onError(error)
    }
  }

  /**
   * 第一轮：直接旅游规划（流式）
   */
  async planTravelDirectStream(userRequest, onUpdate, onComplete, onError) {
    try {
      const response = await fetch(`${this.baseURL}/api/travel-planning-direct`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_request: userRequest,
          session_id: this.sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      let reading = true
      while (reading) {
        const { done, value } = await reader.read()
        
        if (done) {
          reading = false
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // 处理完整的事件
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              // 详细输出中间过程
              console.log('🔄 [第一轮规划] 流式数据:', data)
              
              // 检查supervisor数据结构
              if (data.supervisor && data.supervisor.messages) {
                const messages = data.supervisor.messages
                const lastMessage = messages[messages.length - 1]
                
                if (lastMessage) {
                  // 输出当前智能体信息
                  if (lastMessage.name) {
                    console.log(`📍 当前智能体: ${lastMessage.name}`)
                  }
                  
                  // 输出工具调用信息
                  if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
                    lastMessage.tool_calls.forEach(toolCall => {
                      console.log(`🔧 调用工具: ${toolCall.name} (${toolCall.function ? toolCall.function.name : 'N/A'})`)
                    })
                  }
                  
                  // 输出内容预览
                  if (lastMessage.content && lastMessage.content.length > 0) {
                    console.log(`💬 内容预览: ${lastMessage.content.substring(0, 150)}...`)
                  }
                }
                
                // 输出所有消息的概览
                console.log(`📊 消息历史: 共${messages.length}条消息`)
                messages.forEach((msg, index) => {
                  if (msg.name) {
                    console.log(`  ${index + 1}. ${msg.name}: ${msg.content ? msg.content.substring(0, 50) + '...' : '工具调用'}`)
                  }
                })
              }
              
              // 更新会话ID
              if (data.session_id) {
                this.sessionId = data.session_id
              }

              // 处理不同类型的事件
              if (data.event === 'supervisor_output') {
                onUpdate && onUpdate(data)
              } else if (data.event === 'planning_complete') {
                onComplete && onComplete(data)
                break
              } else if (data.event === 'error') {
                onError && onError(new Error(data.data.error))
                break
              } else {
                // 处理其他类型的数据
                onUpdate && onUpdate(data)
              }
            } catch (e) {
              console.warn('解析流式数据失败:', e, line)
            }
          }
        }
      }
    } catch (error) {
      console.error('第一轮流式规划请求失败:', error)
      onError && onError(error)
    }
  }

  /**
   * 后续轮：流式方案优化 - 对应 /api/travel-optimize-stream
   */
  async optimizeTravelStream(userFeedback, travelPlanDraft, onUpdate, onComplete, onError) {
    try {
      const response = await fetch(`${this.baseURL}/api/travel-optimize-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_feedback: userFeedback,
          travel_plan_draft: travelPlanDraft,
          session_id: this.sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      let reading = true
      while (reading) {
        const { done, value } = await reader.read()
        
        if (done) {
          reading = false
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // 处理完整的事件
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              // 详细输出中间过程
              console.log('🔄 [方案优化] 流式数据:', data)
              
              // 更新会话ID
              if (data.session_id) {
                this.sessionId = data.session_id
              }

              // 处理不同类型的事件 - 适配后端实际格式
              if (data.event === 'optimization_step' || data.event === 'supervisor_output') {
                // 统一处理为supervisor_output格式
                const updateData = data.event === 'optimization_step' ? data.data : data.data
                onUpdate && onUpdate(updateData)
              } else if (data.event === 'optimization_complete') {
                onComplete && onComplete(data)
                break
              } else if (data.event === 'optimization_start') {
                // 处理开始事件
                console.log('📍 优化开始:', data.data.message)
                onUpdate && onUpdate(data.data)
              } else if (data.event === 'error' || data.event === 'optimization_error') {
                onError && onError(new Error(data.data.error))
                break
              } else {
                // 处理其他类型的事件
                console.log('📦 其他优化事件:', data.event, data.data)
                onUpdate && onUpdate(data.data)
              }
            } catch (e) {
              console.warn('解析流式数据失败:', e, line)
            }
          }
        }
      }
    } catch (error) {
      console.error('流式优化请求失败:', error)
      onError && onError(error)
    }
  }

  /**
   * 方案优化
   */
  async optimizeTravel(userFeedback, travelPlanDraft) {
    const response = await this.request('/api/travel-optimize', {
      method: 'POST',
      body: JSON.stringify({
        user_feedback: userFeedback,
        travel_plan_draft: travelPlanDraft,
        session_id: this.sessionId
      })
    })

    // 更新会话ID
    if (response.session_id) {
      this.sessionId = response.session_id
    }

    return response
  }

  /**
   * 获取会话信息
   */
  async getSessionInfo(sessionId = null) {
    const id = sessionId || this.sessionId
    if (!id) {
      throw new Error('没有有效的会话ID')
    }

    return await this.request(`/api/sessions/${id}`)
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId = null) {
    const id = sessionId || this.sessionId
    if (!id) {
      throw new Error('没有有效的会话ID')
    }

    const response = await this.request(`/api/sessions/${id}`, {
      method: 'DELETE'
    })

    // 如果删除的是当前会话，清空会话ID
    if (id === this.sessionId) {
      this.sessionId = null
    }

    return response
  }

  /**
   * 列出所有会话
   */
  async listSessions() {
    return await this.request('/api/sessions')
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    return await this.request('/health')
  }

  /**
   * 重置会话
   */
  resetSession() {
    this.sessionId = null
  }

  /**
   * 获取当前会话ID
   */
  getSessionId() {
    return this.sessionId
  }

  /**
   * 设置会话ID
   */
  setSessionId(sessionId) {
    this.sessionId = sessionId
  }
}

// 创建默认实例
const travelPlanningAPI = new TravelPlanningAPI()

export default travelPlanningAPI
export { TravelPlanningAPI }
