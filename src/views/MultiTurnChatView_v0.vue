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
          <div v-else class="message assistant-message">
            <div class="message-avatar assistant-avatar">🤖</div>
            <div class="message-content">
              <div class="text-message">
                <div class="message-text" v-html="formatMessageContent(message.content)"></div>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- 流式输出卡片列表 -->
        <div v-if="streamingCards.length > 0" class="streaming-cards-container">
          <div v-for="card in streamingCards" :key="card.id" class="streaming-card-wrapper">
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">
                {{ getAgentEmoji(card.agentKey) }}
              </div>
              <div class="message-content streaming-card" :class="{ 'active-card': card.isActive, 'collapsed-card': card.isCollapsed }">
                <!-- 卡片头部 -->
                <div class="streaming-card-header" @click="toggleCardCollapse(card.id)">
                  <div class="streaming-header-left">
                    <span class="streaming-icon" :class="{ 'active-icon': card.isActive }">
                      {{ card.isActive ? '⚡' : '✅' }}
                    </span>
                    <span class="streaming-title">
                      {{ card.isActive ? '实时生成中' : '已完成' }}
                    </span>
                    <span class="streaming-agent" :class="'agent-' + card.agentKey">
                      {{ card.agent }}
                    </span>
                  </div>
                  <div class="streaming-header-right">
                    <span class="streaming-time">{{ formatTime(card.timestamp) }}</span>
                    <span class="collapse-indicator" :class="{ 'collapsed': card.isCollapsed }" v-if="!card.isActive">
                      {{ card.isCollapsed ? '▶' : '▼' }}
                    </span>
                  </div>
                </div>
                
                <!-- 卡片内容 -->
                <div class="streaming-card-content" :class="{ 'collapsed': card.isCollapsed }">
                  <div class="streaming-content" v-html="formatStreamingContent(card.fullContent || card.content)"></div>
                  
                  <!-- 卡片完成状态 -->
                  <div v-if="!card.isActive && (card.fullContent || card.content)" class="card-completion-info">
                    <span class="completion-text">
                      {{ card.agentKey === 'final_plan' ? '🎯 最终方案已生成' : '✨ 内容生成完成' }}
                    </span>
                    <span class="content-length">{{ getContentLength(card.fullContent || card.content) }}字</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-if="isLoading && streamingCards.length === 0" class="loading-message">
          <div class="message assistant-message">
            <div class="message-avatar assistant-avatar">🤖</div>
            <div class="message-content">
              <div class="loading-content">
                <div class="loading-spinner"></div>
                <span class="loading-text">{{ loadingText }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-main-wrapper">
        <!-- 状态信息栏 -->
        <div class="status-info-bar">
          <div class="status-info-left">
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
          </div>
          <div class="status-info-right">
            <button @click="resetConversation" class="reset-btn" :disabled="isLoading">
              🔄 重置对话
            </button>
          </div>
        </div>

        <!-- 主输入框区域 -->
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
          <div class="quick-actions-area" v-if="messages.length === 0">
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
import { ref, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'

// Initialize markdown-it renderer
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// Markdown renderer function
const renderMarkdown = (content) => {
  if (!content) return '';
  return md.render(content);
};

export default {
  name: 'MultiTurnChatView',
  setup() {
    // 核心状态管理
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const loadingText = ref('正在处理您的请求...')
    const chatContainer = ref(null)
    const sessionId = ref(null)
    
    // 流式输出状态
    const streamingCards = ref([])
    const activeStreamingId = ref(null)
    const streamingCardIdCounter = ref(0)
    
    // UI 状态
    const isInputFocused = ref(false)

    // API 基础 URL
    const API_BASE_URL = 'http://localhost:5001'

    // 工具方法
    const addMessage = (role, content, type = 'text') => {
      const message = {
        role,
        content,
        type,
        timestamp: new Date()
      }
      
      console.log('📝 [消息日志] 添加新消息:', {
        role,
        type,
        contentLength: content ? content.length : 0,
        timestamp: message.timestamp.toLocaleString('zh-CN')
      })
      
      messages.value.push(message)
      scrollToBottom()
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
      })
    }

    // 流式卡片管理方法
    const createStreamingCard = (agentKey, content = '') => {
      const cardId = ++streamingCardIdCounter.value
      const newCard = {
        id: cardId,
        agentKey: agentKey,
        agent: getAgentDisplayName(agentKey),
        content: content,
        fullContent: content,
        timestamp: new Date(),
        isActive: true,
        isCollapsed: false
      }
      
      console.log('🆕 [流式卡片] 创建新卡片:', {
        cardId,
        agentKey,
        agentName: getAgentDisplayName(agentKey),
        contentLength: content.length,
        timestamp: newCard.timestamp.toLocaleString('zh-CN')
      })
      
      // 停用之前的活跃卡片
      streamingCards.value.forEach(card => {
        if (card.isActive) {
          card.isActive = false
        }
      })
      
      streamingCards.value.push(newCard)
      activeStreamingId.value = cardId
      scrollToBottom()
      return cardId
    }

    const updateStreamingCard = (cardId, content) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card) {
        card.content = content
        card.fullContent = content
        scrollToBottom()
      }
    }

    const finishStreamingCard = (cardId) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card) {
        card.isActive = false
      }
      activeStreamingId.value = null
    }

    const toggleCardCollapse = (cardId) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card && !card.isActive) {
        card.isCollapsed = !card.isCollapsed
      }
    }

    const clearStreamingCards = () => {
      streamingCards.value = []
      activeStreamingId.value = null
    }

    // 核心发送消息方法
    const sendMessage = async () => {
      if (!userInput.value.trim() || isLoading.value) return

      const userMessage = userInput.value
      
      console.log('🚀 [发送消息] 开始处理用户消息:', userMessage)
      
      // 添加用户消息
      addMessage('user', userMessage)
      
      // 清空输入
      userInput.value = ''
      
      // 设置加载状态
      isLoading.value = true
      loadingText.value = '正在处理您的请求...'

      try {
        // 调用流式 API
        const result = await callMultiTurnChatStream(userMessage)
        console.log('✅ [发送消息] 流式处理完成:', result)
      } catch (error) {
        console.error('❌ [发送消息] 处理消息时出现错误:', error)
        addMessage('assistant', `处理请求时出现错误：${error.message}`)
      } finally {
        // 确保重置加载状态
        console.log('🔄 [发送消息] 重置加载状态')
        isLoading.value = false
        loadingText.value = '正在处理您的请求...'
        
        // 清理流式卡片状态
        if (activeStreamingId.value) {
          finishStreamingCard(activeStreamingId.value)
        }
      }
    }

    // 调用多轮对话流式 API
    const callMultiTurnChatStream = async (userMessage) => {
      return new Promise((resolve, reject) => {
        // 清理之前的流式卡片
        clearStreamingCards()
        
        const requestData = {
          message: userMessage,
          session_id: sessionId.value
        }

        console.log('🚀 [API调用] 开始流式请求:', requestData)

        fetch(`${API_BASE_URL}/api/multi-turn-chat/stream`, {
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
          let fullResponse = ''
          let hasReceivedData = false
          
          function readStream() {
            return reader.read().then(({ done, value }) => {
              if (done) {
                console.log('📥 [流式完成] 数据接收完毕:', { 
                  hasReceivedData, 
                  fullResponseLength: fullResponse.length,
                  activeStreamingId: activeStreamingId.value 
                })
                
                // 完成最后一个活跃卡片
                if (activeStreamingId.value) {
                  finishStreamingCard(activeStreamingId.value)
                }
                
                // 添加最终响应到消息列表
                if (fullResponse.trim()) {
                  addMessage('assistant', fullResponse.trim())
                }
                
                // 确保设置会话ID
                if (!sessionId.value && hasReceivedData) {
                  sessionId.value = requestData.session_id || 'default-session'
                }
                
                console.log('✅ [流式完成] 解析完成，准备resolve')
                resolve(fullResponse || '对话完成')
                return
              }
              
              const chunk = decoder.decode(value)
              const lines = chunk.split('\n')
              
              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6))
                    hasReceivedData = true
                    
                    console.log('📦 [流式数据]:', Object.keys(data))
                    
                    if (data.type === 'done') {
                      console.log('🏁 [完成信号] 收到done信号:', data)
                      fullResponse = data.full_response || fullResponse
                      
                      // 更新会话ID
                      if (data.session_id) {
                        sessionId.value = data.session_id
                      }
                      
                      // 立即结束流式处理
                      if (activeStreamingId.value) {
                        finishStreamingCard(activeStreamingId.value)
                      }
                      
                      if (fullResponse.trim()) {
                        addMessage('assistant', fullResponse.trim())
                      }
                      
                      resolve(fullResponse || '对话完成')
                      return
                    }
                    
                    if (data.type === 'error') {
                      console.error('❌ [流式错误]:', data.error)
                      throw new Error(data.error)
                    }
                    
                    // 处理智能体数据
                    const agentKeys = ['supervisor', 'tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent']
                    for (const agentKey of agentKeys) {
                      if (data[agentKey] && data[agentKey].messages) {
                        const messages = data[agentKey].messages
                        
                        // 查找最新的有效消息
                        for (let i = messages.length - 1; i >= 0; i--) {
                          const message = messages[i]
                          if (message && message.content && message.content.length > 50 && 
                              !message.content.startsWith('Successfully transferred')) {
                            
                            console.log(`🎯 [智能体消息] ${agentKey}:`, message.content.substring(0, 100) + '...')
                            
                            // 检查是否已经为该智能体创建了卡片
                            let existingCard = streamingCards.value.find(card => card.agentKey === agentKey)
                            
                            if (!existingCard) {
                              // 创建新卡片
                              loadingText.value = `正在调用 ${getAgentDisplayName(agentKey)}...`
                              
                              const cardId = createStreamingCard(agentKey, message.content)
                              const newCard = streamingCards.value.find(c => c.id === cardId)
                              if (newCard) {
                                newCard.fullContent = message.content
                              }
                              activeStreamingId.value = cardId
                            } else if (existingCard.isActive) {
                              // 更新现有活跃卡片
                              updateStreamingCard(existingCard.id, message.content)
                              if (message.content.length > existingCard.fullContent.length) {
                                existingCard.fullContent = message.content
                              }
                            }
                            
                            fullResponse = message.content
                            break
                          }
                        }
                        break
                      }
                    }
                  } catch (e) {
                    console.warn('⚠️ [解析警告] 解析流式数据失败:', e, '原始数据:', line)
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
          clearStreamingCards()
          reject(error)
        })
      })
    }

    // 其他方法
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    const quickStart = (message) => {
      userInput.value = message
      sendMessage()
    }

    const resetConversation = async () => {
      if (sessionId.value) {
        try {
          await fetch(`${API_BASE_URL}/api/multi-turn-chat/reset/${sessionId.value}`, {
            method: 'POST'
          })
        } catch (error) {
          console.error('重置会话失败:', error)
        }
      }
      
      // 重置本地状态
      messages.value = []
      clearStreamingCards()
      sessionId.value = null
      
      // 添加欢迎消息
      addMessage('assistant', '您好！我是您的智能旅游规划助手。我会通过多轮对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！')
    }

    // 格式化方法
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatMessageContent = (content) => {
      if (!content) return ''
      // 使用完整的 Markdown 渲染，与流式卡片保持一致
      return renderMarkdown(content)
    }

    const formatStreamingContent = (content) => {
      if (!content) return ''
      return renderMarkdown(content)
    }

    // 获取智能体显示名称
    const getAgentDisplayName = (agentName) => {
      const agentMap = {
        'supervisor': '总控智能体',
        'tour_search_agent': '景点搜索专家',
        'day_plan_agent': '行程规划师',
        'live_transport_agent': '交通住宿顾问',
        'travel_butler_agent': '旅行管家'
      }
      return agentMap[agentName] || agentName
    }

    // 获取智能体表情符号
    const getAgentEmoji = (agentKey) => {
      const emojiMap = {
        'supervisor': '🎯',
        'tour_search_agent': '🔍',
        'day_plan_agent': '📅',
        'live_transport_agent': '🚗',
        'travel_butler_agent': '🎒'
      }
      return emojiMap[agentKey] || '🤖'
    }

    // 获取内容长度
    const getContentLength = (content) => {
      if (!content) return 0
      const textContent = content.replace(/<[^>]*>/g, '')
      return textContent.length
    }

    // 生命周期
    onMounted(() => {
      addMessage('assistant', '您好！我是您的智能旅游规划助手。我会通过多轮对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！')
      scrollToBottom()
    })

    return {
      // 数据
      messages,
      userInput,
      isLoading,
      loadingText,
      chatContainer,
      sessionId,
      streamingCards,
      activeStreamingId,
      isInputFocused,
      
      // 方法
      sendMessage,
      handleKeyDown,
      quickStart,
      resetConversation,
      toggleCardCollapse,
      formatTime,
      formatMessageContent,
      formatStreamingContent,
      getAgentDisplayName,
      getAgentEmoji,
      getContentLength
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
  padding-bottom: 140px;
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

.message-item {
  margin-bottom: 20px;
  animation: fadeInUp 0.4s ease-out;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.user-avatar {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.assistant-avatar {
  background: linear-gradient(45deg, #48bb78, #38a169);
  color: white;
}

.message-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 16px 20px;
  width: 85%;
  max-width: 85%;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 14px;
}

.user-message .message-content {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.message-text {
  line-height: 1.5;
  margin-bottom: 8px;
  font-size: 14px;
}

.message-time {
  font-size: 11px;
  color: #a0aec0;
  text-align: right;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

/* 流式输出卡片样式 */
.streaming-cards-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.streaming-card-wrapper {
  animation: fadeInUp 0.4s ease-out;
}

.streaming-card {
  border: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.streaming-card.active-card {
  border-color: #4299e1;
  box-shadow: 0 0 20px rgba(66, 153, 225, 0.3);
}

.streaming-card.collapsed-card .streaming-card-content {
  max-height: 0;
  overflow: hidden;
  padding: 0 20px;
  margin: 0;
}

.streaming-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease;
}

.streaming-card-header:hover {
  background-color: rgba(66, 153, 225, 0.05);
}

.streaming-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.streaming-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.streaming-icon {
  font-size: 16px;
  transition: all 0.3s ease;
}

.streaming-icon.active-icon {
  animation: pulse 1.5s ease-in-out infinite;
  color: #4299e1;
}

.streaming-title {
  font-weight: 600;
  font-size: 14px;
  color: #2d3748;
}

.streaming-agent {
  padding: 4px 10px;
  background: #e6fffa;
  color: #2f855a;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 500;
}

.streaming-time {
  font-size: 11px;
  color: #a0aec0;
}

.collapse-indicator {
  font-size: 12px;
  color: #718096;
  transition: transform 0.3s ease;
}

.collapse-indicator.collapsed {
  transform: rotate(-90deg);
}

.streaming-card-content {
  max-height: none;
  overflow: visible;
  transition: all 0.3s ease;
  padding: 16px 0;
}

.streaming-content {
  line-height: 1.6;
  font-size: 14px;
  border-left: 4px solid #4299e1;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 0 8px 8px 0;
  padding: 12px 16px;
  margin-bottom: 16px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

/* Markdown 样式增强 - 针对 streaming-content */
.streaming-content h1,
.streaming-content h2,
.streaming-content h3,
.streaming-content h4,
.streaming-content h5,
.streaming-content h6 {
  color: #2d3748;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.streaming-content h1 {
  font-size: 18px;
  border-bottom: 2px solid #4299e1;
  padding-bottom: 4px;
}

.streaming-content h2 {
  font-size: 16px;
  color: #4a5568;
}

.streaming-content h3 {
  font-size: 15px;
  color: #718096;
}

.streaming-content h4 {
  font-size: 14px;
  color: #718096;
}

.streaming-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.streaming-content ul,
.streaming-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.streaming-content li {
  margin: 4px 0;
  line-height: 1.5;
}

.streaming-content strong {
  color: #2d3748;
  font-weight: 600;
}

.streaming-content em {
  color: #4a5568;
  font-style: italic;
}

.streaming-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.streaming-content pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border-left: 3px solid #4299e1;
}

.streaming-content pre code {
  background: none;
  padding: 0;
}

.streaming-content blockquote {
  border-left: 4px solid #e2e8f0;
  padding-left: 16px;
  margin: 12px 0;
  color: #718096;
  font-style: italic;
}

.streaming-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.streaming-content th,
.streaming-content td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.streaming-content th {
  background: rgba(66, 153, 225, 0.1);
  font-weight: 600;
}

.streaming-content a {
  color: #4299e1;
  text-decoration: none;
}

.streaming-content a:hover {
  text-decoration: underline;
}

.streaming-content hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}

.card-completion-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
}

.completion-text {
  color: #38a169;
  font-weight: 500;
}

.content-length {
  color: #718096;
}

/* 加载状态样式 */
.loading-message {
  animation: fadeInUp 0.4s ease-out;
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
  color: #718096;
  font-size: 14px;
}

/* 输入区域样式 */
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
}

.status-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
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
    transform: scale(1.1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 16px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .subtitle {
    font-size: 12px;
  }
  
  .chat-container {
    padding: 16px;
  }
  
  .input-main-wrapper {
    padding: 16px;
  }
  
  .message-content {
    width: 90%;
    max-width: 90%;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .status-info-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .status-info-left {
    width: 100%;
    justify-content: space-between;
  }
}

/* 智能体特定样式 */
.agent-supervisor {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.agent-tour_search_agent {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.agent-day_plan_agent {
  background: linear-gradient(45deg, #48bb78, #38a169);
  color: white;
}

.agent-live_transport_agent {
  background: linear-gradient(45deg, #ed8936, #dd6b20);
  color: white;
}

.agent-travel_butler_agent {
  background: linear-gradient(45deg, #9f7aea, #805ad5);
  color: white;
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.input-textarea::-webkit-scrollbar {
  width: 4px;
}

.input-textarea::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.input-textarea::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 2px;
}

.input-textarea::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>
