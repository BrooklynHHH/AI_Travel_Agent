import { ref, computed, onMounted, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import { API_CONFIG } from '@/config/api.config.js'

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export function useTravelChat() {
  // 核心状态
  const messages = ref([])
  const userInput = ref('')
  const isLoading = ref(false)
  const loadingText = ref('正在连接智能体系统...')
  const sessionId = ref(null)
  const isInputFocused = ref(false)
  const messagesContainer = ref(null)
  const inputField = ref(null)
  const chatContainer = ref(null)
  
  // 增强的加载状态
  const currentProcessingStatus = ref('准备中')
  const currentAgentStatus = ref('')
  const activeAgentInfo = ref(null)
  const processingSteps = ref([])
  const currentStepIndex = ref(0)

  // API 配置
  const API_BASE_URL = API_CONFIG.BASE_URL

  // 智能体配置
  const agentConfig = {
    'supervisor': { name: '制定策略', icon: '🎯' },
    'tour_search_agent': { name: '搜索景点', icon: '🔍' },
    'day_plan_agent': { name: '规划行程', icon: '📅' },
    'live_transport_agent': { name: '交通住宿', icon: '🚗' },
    'travel_butler_agent': { name: '整理建议', icon: '🎒' }
  }

  // 计算属性
  const hasStreamingMessage = computed(() => {
    return messages.value.some(msg => msg.isStreaming)
  })

  // 工具方法
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatMessageContent = (content) => {
    if (!content) return ''
    return md.render(content)
  }

  // 格式化搜索引用卡片
  const formatSearchRefCards = (datas) => {
    if (!datas || !Array.isArray(datas)) return ''
    
    let cardsHtml = '\n\n<div class="search-ref-cards">\n'
    cardsHtml += '<div class="search-ref-header">🔍 相关搜索结果</div>\n'
    
    datas.forEach((item, index) => {
      cardsHtml += `
<div class="search-ref-card">
  <div class="card-header">
    <div class="card-title">${item.title || '无标题'}</div>
    <div class="card-site">${item.siteName || '未知来源'}</div>
  </div>
  <div class="card-content">${item.content || '暂无内容'}</div>
  <div class="card-footer">
    <a href="${item.url || '#'}" target="_blank" class="card-link">
      <span class="link-icon">🔗</span>
      <span class="link-text">查看详情</span>
    </a>
  </div>
</div>`
    })
    
    cardsHtml += '\n</div>\n\n'
    return cardsHtml
  }

  const scrollToBottom = () => {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  }

  const autoResizeTextarea = () => {
    nextTick(() => {
      if (inputField.value) {
        inputField.value.style.height = 'auto'
        inputField.value.style.height = Math.min(inputField.value.scrollHeight, 120) + 'px'
      }
    })
  }

  // 打字机效果管理
  const typewriterState = ref({
    isTyping: false,
    targetContent: '',
    displayedContent: '',
    currentIndex: 0,
    messageId: null,
    typingSpeed: 30 // 毫秒
  })

  // 消息管理
  const addUserMessage = (content) => {
    const message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date()
    }
    messages.value.push(message)
    scrollToBottom()
    return message
  }

  const addAssistantMessage = () => {
    const message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      displayedContent: '', // 用于打字机效果的显示内容
      fullContent: '', // 完整内容
      isStreaming: true,
      isTyping: false, // 是否正在打字
      progress: Object.keys(agentConfig).map(agentKey => ({
        name: agentConfig[agentKey].name,
        agent: agentKey,
        icon: agentConfig[agentKey].icon,
        status: 'waiting'
      })),
      timestamp: new Date()
    }
    messages.value.push(message)
    scrollToBottom()
    return message
  }

  const updateAssistantMessage = (messageId, updates) => {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      Object.assign(messages.value[messageIndex], updates)
      scrollToBottom()
    }
  }

  // 打字机效果函数
  const startTypewriterEffect = (messageId, newContent) => {
    const message = messages.value.find(msg => msg.id === messageId)
    if (!message) return

    // 如果新内容比当前显示的内容短或相等，直接更新
    const currentDisplayed = message.displayedContent || ''
    if (newContent.length <= currentDisplayed.length) {
      message.displayedContent = newContent
      message.fullContent = newContent
      return
    }

    // 更新完整内容
    message.fullContent = newContent
    message.isTyping = true

    // 如果已经在打字，更新目标内容
    if (typewriterState.value.isTyping && typewriterState.value.messageId === messageId) {
      typewriterState.value.targetContent = newContent
      return
    }

    // 开始新的打字机效果
    typewriterState.value = {
      isTyping: true,
      targetContent: newContent,
      displayedContent: currentDisplayed,
      currentIndex: currentDisplayed.length,
      messageId: messageId,
      typingSpeed: 30
    }

    // 启动打字机动画
    typeNextCharacter()
  }

  const typeNextCharacter = () => {
    if (!typewriterState.value.isTyping) return

    const { targetContent, currentIndex, messageId } = typewriterState.value
    const message = messages.value.find(msg => msg.id === messageId)
    
    if (!message || currentIndex >= targetContent.length) {
      // 打字完成
      if (message) {
        message.displayedContent = targetContent
        message.isTyping = false
      }
      typewriterState.value.isTyping = false
      return
    }

    // 添加下一个字符
    const nextChar = targetContent[currentIndex]
    typewriterState.value.displayedContent += nextChar
    typewriterState.value.currentIndex++

    // 更新消息显示内容
    message.displayedContent = typewriterState.value.displayedContent

    // 滚动到底部
    scrollToBottom()

    // 继续下一个字符
    setTimeout(typeNextCharacter, typewriterState.value.typingSpeed)
  }

  const updateProgress = (messageId, agentKey, status) => {
    const message = messages.value.find(msg => msg.id === messageId)
    if (message && message.progress) {
      const step = message.progress.find(p => p.agent === agentKey)
      if (step) {
        step.status = status
      }
    }
  }

  // 流式数据处理
  const processStreamData = (data, currentMessage) => {
    console.log('📥 [流式数据]:', data)

    switch (data.type) {
      case 'start':
        console.log('🎬 [开始处理]')
        if (data.session_id) {
          sessionId.value = data.session_id
        }
        loadingText.value = '开始处理您的请求...'
        break

      case 'agent_start':
        console.log('🤖 [智能体启动]:', data.agent)
        updateProgress(currentMessage.id, data.agent, 'processing')
        loadingText.value = `正在调用 ${agentConfig[data.agent]?.name || data.agent}...`
        break

      case 'content_update':
        console.log('📝 [内容更新]:', data.agent, '长度:', data.content?.length || 0)
        if (data.content) {
          // 使用打字机效果显示累积内容
          startTypewriterEffect(currentMessage.id, data.content)
        }
        break

      case 'done':
        console.log('✅ [处理完成]')
        updateAssistantMessage(currentMessage.id, {
          isStreaming: false,
          content: data.final_response || data.content || currentMessage.content
        })
        // 标记所有步骤为完成
        if (currentMessage.progress) {
          currentMessage.progress.forEach(step => {
            if (step.status === 'processing') {
              step.status = 'completed'
            }
          })
        }
        break

      case 'error':
        console.error('❌ [处理错误]:', data.message)
        updateAssistantMessage(currentMessage.id, {
          isStreaming: false,
          content: `处理请求时出现错误：${data.message}`
        })
        break

      case 'raw_chunk': {
        // 处理原始数据块 - 修复重复字符问题
        // console.log('🔍 [原始数据块]:', data.data)
        
        let newToken = ''
        
        // 方法1: 从 chunk 数组中提取增量内容
        if (data.data && data.data.chunk && Array.isArray(data.data.chunk)) {
          data.data.chunk.forEach(item => {
            if (item && item.content) {
              // 这里应该是增量内容，不是累积内容
              newToken = item.content
            }
          })
        }
        
        // 方法2: 从 output_messages 中提取增量token
        if (data.data && data.data.output_messages && Array.isArray(data.data.output_messages)) {
          data.data.output_messages.forEach(msg => {
            if (msg.type === 'token_stream' && msg.content && msg.content.token) {
              // 这里是单个token，不需要累积
              newToken = msg.content.token
            }
          })
        }
        
        if (newToken) {
          console.log('📝 [新增token]:', newToken.length, '字符:', JSON.stringify(newToken))
          
          // 检查是否是 search_ref 格式的数据
          try {
            const parsedToken = JSON.parse(newToken)
            if (parsedToken.type === 'search_ref' && parsedToken.datas && Array.isArray(parsedToken.datas)) {
              console.log('🔍 [搜索引用数据]:', parsedToken)
              
              // 处理搜索引用数据，转换为卡片格式
              const searchCards = formatSearchRefCards(parsedToken.datas)
              const currentContent = currentMessage.content || ''
              const newContent = currentContent + searchCards
              
              updateAssistantMessage(currentMessage.id, {
                content: newContent
              })
              break
            }
          } catch (e) {
            // 不是JSON格式，按普通文本处理
          }
          
          // 累积更新消息内容 - 只添加新的token
          const currentContent = currentMessage.content || ''
          const newContent = currentContent + newToken
          
          updateAssistantMessage(currentMessage.id, {
            content: newContent
          })
        }
        break
      }

      default:
        console.warn('⚠️ [未知数据类型]:', data.type)
    }
  }

  // API 调用
  const callStreamAPI = async (userMessage) => {
    const requestData = {
      user_input: userMessage,
      session_id: sessionId.value
    }

    console.log('🚀 [API调用] 发送请求:', requestData)

    return new Promise((resolve, reject) => {
      // 使用 fetch 进行流式请求
      fetch(`${API_BASE_URL}/agent-api/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        // 创建助手消息
        const assistantMessage = addAssistantMessage()

        function readStream() {
          return reader.read().then(({ done, value }) => {
            if (done) {
              console.log('📥 [流式完成] 数据接收完毕')
              resolve('流式处理完成')
              return
            }

            // 解码数据块
            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')

            for (const line of lines) {
              const trimmedLine = line.trim()
              if (trimmedLine.startsWith('data: ')) {
                try {
                  const jsonStr = trimmedLine.slice(6).trim()
                  if (jsonStr && jsonStr !== '[DONE]') {
                    const data = JSON.parse(jsonStr)
                    processStreamData(data, assistantMessage)
                  }
                } catch (e) {
                  console.warn('⚠️ [解析警告] 解析流式数据失败:', e, '原始数据:', trimmedLine)
                }
              }
            }

            return readStream()
          })
        }

        return readStream()
      })
      .catch(error => {
        console.error('❌ [API错误] 流式请求失败:', error)
        reject(error)
      })
    })
  }

  // 核心方法
  const sendMessage = async () => {
    if (!userInput.value.trim() || isLoading.value) return

    const userMessage = userInput.value.trim()
    console.log('🚀 [发送消息] 用户输入:', userMessage)

    // 添加用户消息
    addUserMessage(userMessage)
    
    // 清空输入框
    userInput.value = ''
    autoResizeTextarea()

    // 设置加载状态
    isLoading.value = true
    loadingText.value = '正在连接智能体系统...'

    try {
      // 调用流式 API
      await callStreamAPI(userMessage)
      console.log('✅ [发送消息] 处理完成')
    } catch (error) {
      console.error('❌ [发送消息] 处理失败:', error)
      
      // 添加错误消息
      const errorMessage = {
        id: generateId(),
        role: 'assistant',
        content: `抱歉，处理您的请求时出现了错误：${error.message}`,
        isStreaming: false,
        progress: [],
        timestamp: new Date()
      }
      messages.value.push(errorMessage)
      scrollToBottom()
    } finally {
      isLoading.value = false
      loadingText.value = '正在连接智能体系统...'
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
    
    // 自动调整文本框高度
    autoResizeTextarea()
  }

  const quickStart = (message) => {
    userInput.value = message
    sendMessage()
  }

  const resetConversation = async () => {
    try {
      // 如果有会话ID，尝试清空服务器端会话
      if (sessionId.value) {
        await fetch(`${API_BASE_URL}/api/sessions/${sessionId.value}/clear`, {
          method: 'POST'
        })
      }
    } catch (error) {
      console.warn('清空服务器端会话失败:', error)
    }

    // 重置本地状态
    messages.value = []
    sessionId.value = null
    userInput.value = ''
    isLoading.value = false
    
    console.log('🔄 [重置对话] 对话已重置')
  }

  // 监听输入变化，自动调整文本框高度
  watch(userInput, () => {
    autoResizeTextarea()
  })

  // 设置输入区域高度监听器
  const setupInputAreaHeightMonitor = () => {
    nextTick(() => {
      const inputContainer = document.querySelector('.input-container')
      const chatContainer = document.querySelector('.chat-container')
      
      if (inputContainer && chatContainer) {
        // 创建 ResizeObserver 监听输入区域高度变化
        const resizeObserver = new ResizeObserver(entries => {
          for (let entry of entries) {
            const height = entry.contentRect.height
            // 动态设置聊天容器的底部间距
            chatContainer.style.paddingBottom = `${height + 20}px`
          }
        })
        
        resizeObserver.observe(inputContainer)
        
        // 初始设置
        const initialHeight = inputContainer.offsetHeight
        chatContainer.style.paddingBottom = `${initialHeight + 20}px`
      }
    })
  }

  // 组件挂载时的初始化
  const initializeChat = () => {
    console.log('🎉 [组件挂载] NewMultiTurnChatView 已加载')
    
    // 添加欢迎消息
    const welcomeMessage = {
      id: generateId(),
      role: 'assistant',
      content: '您好！我是您的智能旅游规划助手。我会通过多轮对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！',
      isStreaming: false,
      progress: [],
      timestamp: new Date()
    }
    messages.value.push(welcomeMessage)
    scrollToBottom()
    
    // 设置输入区域高度监听
    setupInputAreaHeightMonitor()
  }

  // 返回所有需要在组件中使用的数据和方法
  return {
    // 数据
    messages,
    userInput,
    isLoading,
    loadingText,
    sessionId,
    isInputFocused,
    messagesContainer,
    inputField,
    chatContainer,
    hasStreamingMessage,
    currentProcessingStatus,
    currentAgentStatus,
    activeAgentInfo,
    processingSteps,
    currentStepIndex,
    
    // 方法
    formatTime,
    formatMessageContent,
    sendMessage,
    handleKeyDown,
    quickStart,
    resetConversation,
    scrollToBottom,
    initializeChat
  }
}
