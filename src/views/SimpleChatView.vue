<template>
  <div class="simple-chat-container">
    <!-- 头部标题 -->
    <div class="header">
      <h1 class="title">🤖 简化多轮对话界面</h1>
      <p class="subtitle">专门处理 supervisor 消息流的展示界面</p>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages-wrapper">
        <!-- 用户消息 -->
        <div v-for="(message, index) in userMessages" :key="'user-' + index" class="message-item">
          <div class="message user-message">
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar">👤</div>
          </div>
        </div>

        <!-- 动态卡片列表 -->
        <div v-if="messageCards.length > 0" class="cards-container">
          <div v-for="card in messageCards" :key="card.id" class="card-wrapper">
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">🎯</div>
              <div class="message-content message-card" :class="{ 'active-card': card.isActive }">
                <!-- 卡片头部 -->
                <div class="card-header" @click="toggleCardCollapse(card.id)">
                  <div class="header-left">
                    <span class="card-icon" :class="{ 'active-icon': card.isActive }">
                      {{ card.isActive ? '⚡' : '✅' }}
                    </span>
                    <span class="card-title">
                      {{ card.isActive ? '实时生成中' : '已完成' }}
                    </span>
                    <span class="card-number">卡片 #{{ card.number }}</span>
                  </div>
                  <div class="header-right">
                    <span class="card-time">{{ formatTime(card.timestamp) }}</span>
                    <span class="collapse-indicator" :class="{ 'collapsed': card.isCollapsed }" v-if="!card.isActive">
                      {{ card.isCollapsed ? '▶' : '▼' }}
                    </span>
                  </div>
                </div>
                
                <!-- 卡片内容 -->
                <div class="card-content" :class="{ 'collapsed': card.isCollapsed }">
                  <div class="content-display" v-html="formatContent(card.content)"></div>
                  
                  <!-- 卡片完成状态 -->
                  <div v-if="!card.isActive" class="card-completion-info">
                    <span class="completion-text">✨ 内容生成完成</span>
                    <div class="completion-stats">
                      <span class="content-length">{{ getContentLength(card.content) }}字</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-if="isLoading" class="loading-message">
          <div class="message assistant-message">
            <div class="message-avatar assistant-avatar loading-avatar">
              <div class="avatar-spinner">🤖</div>
            </div>
            <div class="message-content loading-card">
              <div class="loading-header">
                <div class="loading-status-indicator">
                  <div class="status-pulse"></div>
                  <span class="status-text">{{ loadingStatus }}</span>
                </div>
                <div class="loading-time">{{ formatTime(new Date()) }}</div>
              </div>
              <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">{{ loadingText }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-wrapper">
        <!-- 状态栏 -->
        <div class="status-bar">
          <div class="status-left">
            <div class="cards-count">
              <div class="count-circle">
                <span class="count-number">{{ messageCards.length }}</span>
              </div>
              <span class="count-label">卡片数</span>
            </div>
          </div>
          <div class="status-right">
            <button @click="clearAll" class="clear-btn" :disabled="isLoading">
              🗑️ 清空
            </button>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <div class="input-box" :class="{ 'input-focused': isInputFocused, 'input-loading': isLoading }">
            <div class="input-icon">✍️</div>
            <textarea
              v-model="userInput"
              @keydown="handleKeyDown"
              @focus="isInputFocused = true"
              @blur="isInputFocused = false"
              placeholder="请输入消息..."
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

        <!-- 测试按钮区域 -->
        <div class="test-actions" v-if="messageCards.length === 0">
          <div class="test-header">
            <span class="test-icon">🧪</span>
            <span class="test-title">测试数据</span>
          </div>
          <div class="test-buttons">
            <button @click="simulateChunk" class="test-btn" :disabled="isLoading">
              模拟数据流
            </button>
            <button @click="quickTest('北京周边有什么好玩的？')" class="test-btn" :disabled="isLoading">
              快速测试
            </button>
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

export default {
  name: 'SimpleChatView',
  setup() {
    // 核心状态
    const userMessages = ref([])
    const messageCards = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const loadingText = ref('正在处理...')
    const loadingStatus = ref('准备中')
    const chatContainer = ref(null)
    const cardIdCounter = ref(0)
    const isInputFocused = ref(false)

    // 工具方法
    const scrollToBottom = () => {
      nextTick(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
      })
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const formatContent = (content) => {
      if (!content) return ''
      return md.render(content)
    }

    const getContentLength = (content) => {
      if (!content) return 0
      const textContent = content.replace(/<[^>]*>/g, '')
      return textContent.length
    }

    // 卡片管理
    const createMessageCard = (content) => {
      const cardId = ++cardIdCounter.value
      const newCard = {
        id: cardId,
        number: cardId,
        content: content,
        timestamp: new Date(),
        isActive: true,
        isCollapsed: false
      }
      
      // 将之前的卡片标记为非活跃状态
      messageCards.value.forEach(card => {
        card.isActive = false
      })
      
      messageCards.value.push(newCard)
      
      console.log('🆕 [创建卡片] 新卡片:', {
        id: cardId,
        contentLength: content.length,
        timestamp: newCard.timestamp.toLocaleString('zh-CN')
      })
      
      scrollToBottom()
      return cardId
    }

    const toggleCardCollapse = (cardId) => {
      const card = messageCards.value.find(c => c.id === cardId)
      if (card && !card.isActive) {
        card.isCollapsed = !card.isCollapsed
      }
    }

    // 处理数据流
    const processChunk = (chunk) => {
      console.log('📥 [处理数据块]:', chunk)
      
      try {
        // 检查是否包含 supervisor 数据
        if (chunk.supervisor && chunk.supervisor.messages && chunk.supervisor.messages.length > 0) {
          const lastMessage = chunk.supervisor.messages[chunk.supervisor.messages.length - 1]
          
          if (lastMessage && lastMessage.content) {
            console.log('📝 [提取内容]:', lastMessage.content)
            
            // 为每个 chunk 创建新的卡片
            createMessageCard(lastMessage.content)
          }
        }
      } catch (error) {
        console.error('❌ [处理错误]:', error)
      }
    }

    // API 基础 URL
    const API_BASE_URL = 'http://localhost:5001'
    const sessionId = ref(null)

    // 发送消息
    const sendMessage = async () => {
      if (!userInput.value.trim() || isLoading.value) return

      const userMessage = userInput.value.trim()
      
      console.log('🚀 [发送消息] 开始处理用户消息:', userMessage)
      
      // 添加用户消息
      userMessages.value.push({
        content: userMessage,
        timestamp: new Date()
      })
      
      // 清空输入
      userInput.value = ''
      
      // 设置加载状态
      isLoading.value = true
      loadingStatus.value = '连接中'
      loadingText.value = '正在处理您的请求...'
      
      try {
        // 调用真实的流式 API
        await callMultiTurnChatStream(userMessage)
        console.log('✅ [发送消息] 流式处理完成')
      } catch (error) {
        console.error('❌ [发送失败]:', error)
        // 添加错误消息
        const errorCard = createMessageCard(`处理请求时出现错误：${error.message}`)
        messageCards.value.find(c => c.id === errorCard).isActive = false
      } finally {
        isLoading.value = false
        loadingStatus.value = '完成'
      }
    }

    // 调用多轮对话流式 API
    const callMultiTurnChatStream = async (userMessage) => {
      return new Promise((resolve, reject) => {
        const requestData = {
          message: userMessage,
          session_id: sessionId.value
        }

        console.log('🚀 [API调用] 开始流式处理:', requestData)

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
          let currentCardId = null
          
          function readStream() {
            return reader.read().then(async ({ done, value }) => {
              if (done) {
                console.log('📥 [流式完成] 数据接收完毕')
                
                // 完成当前活跃的卡片
                if (currentCardId) {
                  const card = messageCards.value.find(c => c.id === currentCardId)
                  if (card) {
                    card.isActive = false
                  }
                }
                
                resolve('对话完成')
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
                      
                      // 处理不同类型的流式数据
                      if (data.type === 'start') {
                        console.log('🎬 [开始处理] 流式处理开始')
                        loadingStatus.value = '连接成功'
                        loadingText.value = '开始处理您的请求...'
                        
                        if (data.sessionId) {
                          sessionId.value = data.sessionId
                        }
                      } else if (data.type === 'agent_start') {
                        console.log('🤖 [智能体启动]:', data.agent)
                        loadingText.value = `正在调用 ${getAgentDisplayName(data.agent)}...`
                      } else if (data.type === 'content_update') {
                        console.log('📝 [内容更新]:', data.agent, '长度:', data.content?.length || 0)
                        
                        // 如果没有当前卡片或者智能体不同，创建新卡片
                        if (!currentCardId || data.agent !== 'supervisor') {
                          currentCardId = createMessageCard(data.content || '')
                        } else {
                          // 更新现有卡片内容
                          const card = messageCards.value.find(c => c.id === currentCardId)
                          if (card && data.content) {
                            card.content = data.content
                          }
                        }
                        
                        loadingText.value = `${getAgentDisplayName(data.agent)}正在生成内容...`
                      } else if (data.type === 'agent_complete') {
                        console.log('✅ [智能体完成]:', data.agent)
                      } else if (data.type === 'done') {
                        console.log('🏁 [处理完成] 流式处理结束')
                        
                        // 完成当前卡片
                        if (currentCardId) {
                          const card = messageCards.value.find(c => c.id === currentCardId)
                          if (card) {
                            card.isActive = false
                          }
                        }
                        
                        loadingStatus.value = '完成'
                        loadingText.value = '内容生成完毕'
                        resolve('对话完成')
                        return
                      } else if (data.type === 'error') {
                        console.error('❌ [处理错误]:', data.error)
                        throw new Error(data.error)
                      } else {
                        // 处理复杂的supervisor数据结构
                        if (data.supervisor && data.supervisor.messages && data.supervisor.messages.length > 0) {
                          const lastMessage = data.supervisor.messages[data.supervisor.messages.length - 1]
                          
                          if (lastMessage && lastMessage.content) {
                            console.log('📝 [Supervisor内容]:', lastMessage.content)
                            
                            // 如果没有当前卡片，创建新卡片
                            if (!currentCardId) {
                              currentCardId = createMessageCard(lastMessage.content)
                            } else {
                              // 更新现有卡片内容
                              const card = messageCards.value.find(c => c.id === currentCardId)
                              if (card) {
                                card.content = lastMessage.content
                              }
                            }
                          }
                        }
                      }
                    }
                  } catch (e) {
                    console.warn('⚠️ [解析警告] 解析流式数据失败:', e, '原始数据:', trimmedLine)
                    // 继续处理，不中断流程
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

    // 模拟单个数据块（保留用于测试）
    const simulateChunk = () => {
      const mockChunk = {
        supervisor: {
          messages: [
            {
              content: `这是一个测试消息，时间戳：${new Date().toLocaleString('zh-CN')}\n\n包含一些**Markdown**格式的内容：\n- 列表项 1\n- 列表项 2\n\n\`\`\`json\n{\n  "test": "data",\n  "timestamp": "${Date.now()}"\n}\n\`\`\``,
              id: `test-${Date.now()}`
            }
          ]
        }
      }
      
      processChunk(mockChunk)
    }

    // 快速测试
    const quickTest = (message) => {
      userInput.value = message
      sendMessage()
    }

    // 清空所有
    const clearAll = () => {
      userMessages.value = []
      messageCards.value = []
      cardIdCounter.value = 0
      sessionId.value = null
    }

    // 键盘事件
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    // 生命周期
    onMounted(() => {
      console.log('🚀 [简化聊天界面] 组件已加载')
    })

    return {
      // 数据
      userMessages,
      messageCards,
      userInput,
      isLoading,
      loadingText,
      loadingStatus,
      chatContainer,
      isInputFocused,
      
      // 方法
      sendMessage,
      simulateChunk,
      quickTest,
      clearAll,
      toggleCardCollapse,
      handleKeyDown,
      formatTime,
      formatContent,
      getContentLength
    }
  }
}
</script>

<style scoped>
.simple-chat-container {
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
  padding: 16px 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 4px 0;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  padding-bottom: 200px;
  position: relative;
  z-index: 1;
  min-height: 0;
  scroll-behavior: smooth;
}

.messages-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
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

.loading-avatar {
  position: relative;
  overflow: hidden;
}

.avatar-spinner {
  animation: pulse 2s ease-in-out infinite;
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

/* 卡片样式 */
.cards-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-wrapper {
  animation: fadeInUp 0.4s ease-out;
}

.message-card {
  border: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.message-card.active-card {
  border-color: #4299e1;
  box-shadow: 0 0 20px rgba(66, 153, 225, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease;
}

.card-header:hover {
  background-color: rgba(66, 153, 225, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  font-size: 16px;
  transition: all 0.3s ease;
}

.card-icon.active-icon {
  animation: pulse 1.5s ease-in-out infinite;
  color: #4299e1;
}

.card-title {
  font-weight: 600;
  font-size: 14px;
  color: #2d3748;
}

.card-number {
  padding: 4px 10px;
  background: #e6fffa;
  color: #2f855a;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 500;
}

.card-time {
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

.card-content {
  max-height: none;
  overflow: visible;
  transition: all 0.3s ease;
  padding: 16px 0;
}

.card-content.collapsed {
  max-height: 0;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.content-display {
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

.completion-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content-length {
  color: #718096;
}

/* 加载状态样式 */
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

.loading-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

.loading-text {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
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

.input-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 12px 20px;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.cards-count {
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

.clear-btn {
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

.clear-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.3);
}

.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-area {
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

/* 测试按钮区域 */
.test-actions {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.test-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.test-icon {
  font-size: 16px;
}

.test-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.test-buttons {
  display: flex;
  gap: 12px;
}

.test-btn {
  padding: 8px 16px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
    padding: 12px 16px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .subtitle {
    font-size: 12px;
  }
  
  .chat-container {
    padding: 16px;
    padding-bottom: 220px;
  }
  
  .input-wrapper {
    padding: 12px 16px;
  }
  
  .message-content {
    width: 90%;
    max-width: 90%;
  }
  
  .test-buttons {
    flex-direction: column;
  }
  
  .status-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .status-left {
    width: 100%;
    justify-content: space-between;
  }
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
