<template>
  <div class="multi-turn-chat-container">
    <!-- 头部标题 -->
    <div class="header">
      <h1 class="title">🤖 智能多轮对话助手</h1>
      <p class="subtitle">基于多智能体系统的智能旅游规划对话</p>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages-wrapper">
        <!-- 消息列表 -->
        <div v-for="(message, index) in messages" :key="index" class="message-item">
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="message user-message">
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar">👤</div>
          </div>

          <!-- 助手消息 -->
          <div v-else class="message-group">
            <!-- 助手消息 -->
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">🤖</div>
              <div class="message-content">
                <!-- 消息头部 -->
                <div class="message-header" v-if="message.isStreaming">
                  <span class="assistant-label">助手</span>
                  <span class="streaming-indicator">
                    <span class="pulse-dot"></span>
                    正在生成中...
                  </span>
                </div>

                <!-- 进度指示器 (仅在流式生成时显示) -->
                <div v-if="message.isStreaming && message.progress.length > 0" class="progress-section">
                  <div class="progress-title">处理进度:</div>
                  <div class="progress-steps">
                    <div 
                      v-for="step in message.progress" 
                      :key="step.name" 
                      class="progress-step"
                      :class="step.status"
                    >
                      <span class="step-icon">{{ step.icon }}</span>
                      <span class="step-name">{{ step.name }}</span>
                      <span class="step-status">
                        <span v-if="step.status === 'completed'" class="status-completed">✅</span>
                        <span v-else-if="step.status === 'processing'" class="status-processing">⚡</span>
                        <span v-else class="status-waiting">⏳</span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 消息内容 -->
                <div class="text-message">
                  <!-- 如果正在打字或有显示内容，显示打字机效果的内容 -->
                  <div class="message-text" v-html="formatMessageContent(message.displayedContent || message.content)" v-if="message.displayedContent || message.content"></div>
                  <!-- 打字机光标效果 -->
                  <span v-if="message.isTyping" class="typing-cursor">|</span>
                </div>
                
                <!-- 消息时间 -->
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-main-wrapper">
        <!-- 状态信息栏 - 左侧固定宽度 -->
        <div class="status-info-bar">
          <div class="status-info-content">
            <div class="session-info">
              <div class="session-icon">💬</div>
              <div class="session-details">
                <span class="session-label">会话ID</span>
                <span class="session-id">{{ sessionId ? sessionId.substring(0, 8) : '新会话' }}</span>
              </div>
            </div>
            <div class="message-count">
              <div class="count-circle">
                <span class="count-number">{{ messages.length }}</span>
              </div>
              <span class="count-label">消息数</span>
            </div>
            <button @click="resetConversation" class="reset-btn" :disabled="isLoading">
              🔄 重置
            </button>
          </div>
        </div>

        <!-- 主输入框区域 - 右侧弹性宽度 -->
        <div class="input-main-area">
          <div class="input-box-container">
            <div class="input-box" :class="{ 'input-focused': isInputFocused, 'input-loading': isLoading }">
              <div class="input-icon">
                <span>✍️</span>
              </div>
              <textarea
                v-model="userInput"
                @keydown="handleKeyDown"
                @focus="isInputFocused = true"
                @blur="isInputFocused = false"
                placeholder="请输入您的旅游需求或问题..."
                class="input-textarea"
                :disabled="isLoading"
                rows="1"
                ref="inputField"
              ></textarea>
              <button
                @click="sendMessage"
                :disabled="!userInput.trim() || isLoading"
                class="send-button"
                :class="{ 'send-ready': userInput.trim() && !isLoading }"
              >
                <span v-if="!isLoading" class="send-content">
                  <span class="send-icon">🚀</span>
                  <span class="send-text">发送</span>
                </span>
                <span v-else class="loading-content">
                  <div class="loading-spinner-small"></div>
                  <span class="loading-label">处理中</span>
                </span>
              </button>
            </div>
          </div>

          <!-- 快捷操作区域 -->
          <div v-if="messages.length === 0" class="quick-actions-area">
            <div class="quick-actions-header">
              <div class="quick-header-content">
                <span class="quick-icon">🚀</span>
                <div class="quick-header-text">
                  <span class="quick-title">快速开始</span>
                  <span class="quick-subtitle">选择一个示例开始您的多轮对话</span>
                </div>
              </div>
            </div>
            <div class="quick-actions-grid">
              <button @click="quickStart('我想去北京三日游')" class="quick-action-card beijing">
                <div class="quick-card-content">
                  <div class="quick-card-icon">🏛️</div>
                  <div class="quick-card-text">北京三日游</div>
                  <div class="quick-card-desc">历史文化之旅</div>
                </div>
              </button>
              <button @click="quickStart('计划上海周末游')" class="quick-action-card shanghai">
                <div class="quick-card-content">
                  <div class="quick-card-icon">🌃</div>
                  <div class="quick-card-text">上海周末游</div>
                  <div class="quick-card-desc">都市风情体验</div>
                </div>
              </button>
              <button @click="quickStart('西安历史文化之旅')" class="quick-action-card xian">
                <div class="quick-card-content">
                  <div class="quick-card-icon">🏺</div>
                  <div class="quick-card-text">西安文化游</div>
                  <div class="quick-card-desc">古都历史探索</div>
                </div>
              </button>
              <button @click="quickStart('成都美食之旅')" class="quick-action-card chengdu">
                <div class="quick-card-content">
                  <div class="quick-card-icon">🌶️</div>
                  <div class="quick-card-text">成都美食游</div>
                  <div class="quick-card-desc">川菜美食之旅</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
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

export default {
  name: 'NewMultiTurnChatView',
  setup() {
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
          console.log('🔍 [原始数据块]:', data.data)
          
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
          await fetch(`${API_BASE_URL}/agent-api/sessions/${sessionId.value}/clear`, {
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
    onMounted(() => {
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
    })

    // 返回所有需要在模板中使用的数据和方法
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
      scrollToBottom
    }
  }
}
</script>

<style scoped>
.multi-turn-chat-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
  z-index: 1000;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.title {
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 4px 0;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 12px;
  color: #718096;
  margin: 0;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  padding-bottom: 200px; /* 初始值，将被JavaScript动态调整 */
  position: relative;
  z-index: 1;
  min-height: 0;
  scroll-behavior: smooth;
}

.messages-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 消息样式 */
.message-item {
  animation: fadeInUp 0.4s ease-out;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-avatar {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.assistant-message .message-avatar {
  background: linear-gradient(45deg, #48bb78, #38a169);
  color: white;
}

.loading-avatar {
  animation: pulse 2s ease-in-out infinite;
}

.message-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 16px 20px;
  max-width: 80%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-all;
}

.user-message .message-content {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

/* 消息头部 */
.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.assistant-label {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4299e1;
  font-weight: 500;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

/* 进度指示器 */
.progress-section {
  background: rgba(66, 153, 225, 0.05);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 16px;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.progress-title {
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.progress-step.waiting {
  background: rgba(160, 174, 192, 0.1);
  color: #718096;
}

.progress-step.processing {
  background: rgba(66, 153, 225, 0.15);
  color: #2d3748;
  border: 1px solid rgba(66, 153, 225, 0.3);
}

.progress-step.completed {
  background: rgba(56, 161, 105, 0.1);
  color: #2f855a;
}

.step-icon {
  font-size: 14px;
}

.step-name {
  font-size: 13px;
  font-weight: 500;
  flex: 1;
}

.step-status {
  font-size: 14px;
}

.status-processing {
  animation: pulse 1s ease-in-out infinite;
  color: #4299e1;
}

/* 消息内容 */
.message-text {
  line-height: 1.6;
  font-size: 14px;
  margin-bottom: 8px;
}

/* 打字机光标效果 */
.typing-cursor {
  display: inline-block;
  color: #4299e1;
  font-weight: bold;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

.message-time {
  font-size: 11px;
  color: #a0aec0;
  text-align: right;
  margin-top: 8px;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

/* 加载指示器 */
.loading-message {
  animation: fadeInUp 0.4s ease-out;
}

.loading-card {
  border: 2px solid #4299e1;
  box-shadow: 0 0 20px rgba(66, 153, 225, 0.3);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(66, 153, 225, 0.05) 100%);
}

.loading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(66, 153, 225, 0.2);
  margin-bottom: 16px;
}

.loading-status-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-pulse {
  width: 12px;
  height: 12px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-text {
  font-weight: 600;
  color: #2d3748;
  font-size: 16px;
}

.loading-time {
  font-size: 11px;
  color: #a0aec0;
}

.loading-content-detailed {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.loading-spinner-enhanced {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

.loading-text-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.loading-primary-text {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.loading-secondary-text {
  font-size: 14px;
  color: #718096;
}

.processing-steps {
  background: rgba(66, 153, 225, 0.05);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.steps-title {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.steps-counter {
  background: #4299e1;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.step-item.step-completed {
  background: rgba(56, 161, 105, 0.1);
  color: #2f855a;
}

.step-item.step-current {
  background: rgba(66, 153, 225, 0.15);
  color: #2d3748;
  border: 1px solid rgba(66, 153, 225, 0.3);
  transform: translateX(4px);
}

.step-item.step-pending {
  background: rgba(160, 174, 192, 0.1);
  color: #718096;
}

.step-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.step-spinner {
  animation: pulse 1s ease-in-out infinite;
  color: #4299e1;
}

.step-text {
  font-size: 14px;
  font-weight: 500;
}

.agent-status-display {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.agent-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-emoji {
  font-size: 18px;
}

.agent-name {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.agent-activity {
  display: flex;
  align-items: center;
  gap: 6px;
}

.activity-indicator {
  width: 8px;
  height: 8px;
  background: #48bb78;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.activity-text {
  font-size: 12px;
  color: #48bb78;
  font-weight: 500;
}

.agent-description {
  font-size: 13px;
  color: #718096;
  line-height: 1.4;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 14px;
  color: #718096;
}

/* 输入区域 */
.input-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.input-main-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 16px;
}

.status-info-bar {
  flex-shrink: 0;
  width: 320px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-info-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-info-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-icon {
  font-size: 16px;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-label {
  font-size: 10px;
  color: #718096;
  font-weight: 500;
}

.session-id {
  font-size: 12px;
  color: #2d3748;
  font-weight: 600;
  font-family: monospace;
}

.message-count {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-circle {
  width: 24px;
  height: 24px;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.count-number {
  color: white;
  font-size: 11px;
  font-weight: 600;
}

.count-label {
  font-size: 12px;
  color: #718096;
}

.reset-btn {
  padding: 8px 16px;
  background: linear-gradient(45deg, #f56565, #e53e3e);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.3);
}

.reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-box-container {
  width: 100%;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.input-box.input-focused {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.input-box.input-loading {
  opacity: 0.7;
}

.input-icon {
  font-size: 20px;
  color: #718096;
  margin-bottom: 8px;
}

.input-textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #2d3748;
  background: transparent;
  min-height: 20px;
  max-height: 120px;
  overflow-y: auto;
}

.input-textarea::placeholder {
  color: #a0aec0;
}

.input-textarea:disabled {
  color: #a0aec0;
}

.send-button {
  padding: 12px 20px;
  background: #e2e8f0;
  color: #a0aec0;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 80px;
  justify-content: center;
}

.send-button.send-ready {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
}

.send-button:disabled {
  cursor: not-allowed;
}

.send-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-icon {
  font-size: 16px;
}

.send-text {
  font-size: 14px;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-label {
  font-size: 12px;
}

/* 快捷操作区域 */
.quick-actions-area {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.quick-actions-header {
  margin-bottom: 16px;
}

.quick-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quick-icon {
  font-size: 20px;
}

.quick-header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.quick-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.quick-subtitle {
  font-size: 12px;
  color: #718096;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.quick-action-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.quick-action-card:hover {
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(66, 153, 225, 0.15);
}

.quick-card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-card-icon {
  font-size: 24px;
}

.quick-card-text {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.quick-card-desc {
  font-size: 12px;
  color: #718096;
}

/* 特定城市卡片颜色 */
.quick-action-card.beijing:hover {
  border-color: #f56565;
  box-shadow: 0 8px 25px rgba(245, 101, 101, 0.15);
}

.quick-action-card.shanghai:hover {
  border-color: #4299e1;
  box-shadow: 0 8px 25px rgba(66, 153, 225, 0.15);
}

.quick-action-card.xian:hover {
  border-color: #ed8936;
  box-shadow: 0 8px 25px rgba(237, 137, 54, 0.15);
}

.quick-action-card.chengdu:hover {
  border-color: #f56565;
  box-shadow: 0 8px 25px rgba(245, 101, 101, 0.15);
}

.session-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  max-width: 1000px;
  margin: 0 auto;
}

.session-details {
  display: flex;
  align-items: center;
  gap: 20px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.session-icon {
  font-size: 14px;
}

.session-label {
  color: #718096;
  font-weight: 500;
}

.session-value {
  color: #2d3748;
  font-weight: 600;
  font-family: monospace;
}

.reset-button {
  padding: 6px 12px;
  background: linear-gradient(45deg, #f56565, #e53e3e);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.3);
}

.reset-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 输入框区域 */
.input-area {
  padding: 16px 20px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.input-container {
  margin-bottom: 16px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-wrapper.input-focused {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.input-wrapper.input-disabled {
  opacity: 0.7;
  background: #f7fafc;
}

.input-icon {
  font-size: 18px;
  color: #718096;
  margin-bottom: 2px;
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #2d3748;
  background: transparent;
  min-height: 20px;
  max-height: 120px;
  overflow-y: auto;
}

.input-field::placeholder {
  color: #a0aec0;
}

.input-field:disabled {
  color: #a0aec0;
}

.send-button {
  padding: 8px 16px;
  background: #e2e8f0;
  color: #a0aec0;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
}

.send-button.send-ready {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
}

.send-button:disabled {
  cursor: not-allowed;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 快捷操作 */
.quick-actions {
  margin-top: 8px;
}

.quick-actions-title {
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.quick-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}

.quick-button {
  padding: 10px 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  color: #2d3748;
}

.quick-button:hover {
  border-color: #4299e1;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.quick-button.beijing:hover {
  border-color: #f56565;
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.15);
}

.quick-button.shanghai:hover {
  border-color: #4299e1;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.quick-button.xian:hover {
  border-color: #ed8936;
  box-shadow: 0 4px 12px rgba(237, 137, 54, 0.15);
}

.quick-button.chengdu:hover {
  border-color: #f56565;
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.15);
}

/* Markdown 内容样式 */
.message-text h1,
.message-text h2,
.message-text h3,
.message-text h4,
.message-text h5,
.message-text h6 {
  color: #2d3748;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.message-text h1 {
  font-size: 18px;
  border-bottom: 2px solid #4299e1;
  padding-bottom: 4px;
}

.message-text h2 {
  font-size: 16px;
  color: #4a5568;
}

.message-text h3 {
  font-size: 15px;
  color: #718096;
}

.message-text p {
  margin: 8px 0;
  line-height: 1.6;
}

.message-text ul,
.message-text ol {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text li {
  margin: 4px 0;
  line-height: 1.5;
}

.message-text strong {
  color: #2d3748;
  font-weight: 600;
}

.message-text em {
  color: #4a5568;
  font-style: italic;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.message-text pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border-left: 3px solid #4299e1;
}

.message-text pre code {
  background: none;
  padding: 0;
}

.message-text blockquote {
  border-left: 4px solid #e2e8f0;
  padding-left: 16px;
  margin: 12px 0;
  color: #718096;
  font-style: italic;
}

.message-text table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.message-text th,
.message-text td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.message-text th {
  background: rgba(66, 153, 225, 0.1);
  font-weight: 600;
}

.message-text a {
  color: #4299e1;
  text-decoration: none;
}

.message-text a:hover {
  text-decoration: underline;
}

.message-text hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.input-field::-webkit-scrollbar {
  width: 4px;
}

.input-field::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.input-field::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 2px;
}

.input-field::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .subtitle {
    font-size: 12px;
  }
  
  .messages-container {
    padding: 16px;
  }
  
  .message-content {
    max-width: 90%;
  }
  
  .input-area {
    padding: 12px 16px;
  }
  
  .session-info {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .session-details {
    width: 100%;
    justify-content: space-between;
  }
  
  .quick-buttons {
    grid-template-columns: 1fr;
  }
  
  .progress-section {
    padding: 8px 12px;
  }
  
  .progress-steps {
    gap: 4px;
  }
  
  .progress-step {
    padding: 4px 6px;
  }
  
  .step-name {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .input-wrapper {
    padding: 8px 12px;
  }
  
  .send-button {
    min-width: 50px;
    padding: 6px 12px;
  }
  
  .message-content {
    padding: 12px 16px;
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
}
</style>
