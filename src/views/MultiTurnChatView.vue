<template>
  <div class="multi-turn-chat-container">
    <!-- 头部标题 -->
    <div class="header">
      <h1 class="title">🤖 智能多轮对话助手</h1>
      <p class="subtitle">基于多智能体系统的智能旅游规划对话</p>
    </div>

    <!-- Supervisor 监控面板 -->
    <SupervisorMonitor 
      :supervisorData="supervisorData" 
      :isActive="isLoading"
      @update:expanded="onSupervisorExpanded"
      v-if="showSupervisorMonitor"
    />

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
            <!-- 流式输出卡片列表 - 显示在助手消息之前 -->
            <div v-if="streamingCards.length > 0 && (index === messages.length - 1 || isLoading)" class="streaming-cards-container" :key="'streaming-' + forceUpdateKey">
              <div v-for="card in streamingCards" :key="`card-${card.id}-${card.timestamp.getTime()}`" class="streaming-card-wrapper">
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
                    
                    <!-- 卡片内容 - 累积式展示 -->
                    <div class="streaming-card-content" :class="{ 'collapsed': card.isCollapsed }">
                      <!-- 如果有内容区域，使用累积式展示 -->
                      <div v-if="card.contentSections && card.contentSections.length > 0" class="content-sections-container">
                        <div 
                          v-for="section in card.contentSections" 
                          :key="`section-${section.id}-${section.timestamp.getTime()}`"
                          class="content-section"
                          :class="{
                            'section-new': section.isNew,
                            'section-processing': section.status === 'processing',
                            'section-completed': section.status === 'completed'
                          }"
                        >
                          <!-- 区域头部信息 -->
                          <div class="section-header" v-if="card.contentSections.length > 1 || section.isNew">
                            <div class="section-info">
                              <span class="section-status-icon">
                                {{ section.status === 'processing' ? '⚡' : '✅' }}
                              </span>
                              <span class="section-label">
                                {{ section.isNew ? '新增内容' : '已生成内容' }}
                              </span>
                              <span class="section-time">{{ formatTime(section.timestamp) }}</span>
                            </div>
                            <div class="section-type-badge" :class="`type-${section.type}`">
                              {{ getContentTypeLabel(section.type) }}
                            </div>
                            <!-- 添加内容长度信息 -->
                            <div class="section-length-info">
                              {{ section.content.length }}字
                            </div>
                          </div>
                          
                          <!-- 区域内容 -->
                          <div class="section-content">
                            <div class="streaming-content" v-html="formatStreamingContent(section.content)"></div>
                          </div>
                        </div>
                      </div>
                      
                      <!-- 如果没有内容区域，使用传统展示方式 -->
                      <div v-else class="streaming-content" v-html="formatStreamingContent(card.fullContent || card.content)" :key="`content-${card.id}-${card.timestamp.getTime()}`"></div>
                      
                      <!-- 卡片完成状态 -->
                      <div v-if="!card.isActive && (card.fullContent || card.content)" class="card-completion-info">
                        <span class="completion-text">
                          {{ card.agentKey === 'final_plan' ? '🎯 最终方案已生成' : '✨ 内容生成完成' }}
                        </span>
                        <div class="completion-stats">
                          <span class="content-length">{{ getContentLength(card.fullContent || card.content) }}字</span>
                          <span v-if="card.contentSections && card.contentSections.length > 1" class="sections-count">
                            {{ card.contentSections.length }}个更新
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 助手消息 -->
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">🤖</div>
              <div class="message-content">
                <div class="text-message">
                  <div class="message-text" v-html="formatMessageContent(message.content)"></div>
                </div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 增强的加载指示器 -->
        <div v-if="isLoading" class="loading-message">
          <div class="message assistant-message">
            <div class="message-avatar assistant-avatar loading-avatar">
              <div class="avatar-spinner">🤖</div>
            </div>
            <div class="message-content loading-card">
              <!-- 主要加载状态 -->
              <div class="loading-header">
                <div class="loading-status-indicator">
                  <div class="status-pulse"></div>
                  <span class="status-text">{{ currentProcessingStatus }}</span>
                </div>
                <div class="loading-time">{{ formatTime(new Date()) }}</div>
              </div>
              
              <!-- 详细加载内容 -->
              <div class="loading-content-detailed">
                <div class="loading-main">
                  <div class="loading-spinner-enhanced"></div>
                  <div class="loading-text-container">
                    <div class="loading-primary-text">{{ loadingText }}</div>
                    <div class="loading-secondary-text" v-if="currentAgentStatus">
                      {{ currentAgentStatus }}
                    </div>
                  </div>
                </div>
                
                <!-- 处理步骤指示器 -->
                <div class="processing-steps" v-if="processingSteps.length > 0">
                  <div class="steps-header">
                    <span class="steps-title">处理进度</span>
                    <span class="steps-counter">{{ currentStepIndex + 1 }}/{{ processingSteps.length }}</span>
                  </div>
                  <div class="steps-list">
                    <div 
                      v-for="(step, index) in processingSteps" 
                      :key="index"
                      class="step-item"
                      :class="{ 
                        'step-completed': index < currentStepIndex,
                        'step-current': index === currentStepIndex,
                        'step-pending': index > currentStepIndex
                      }"
                    >
                      <div class="step-icon">
                        <span v-if="index < currentStepIndex">✅</span>
                        <span v-else-if="index === currentStepIndex" class="step-spinner">⚡</span>
                        <span v-else>⏳</span>
                      </div>
                      <span class="step-text">{{ step }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 智能体工作状态 -->
                <div class="agent-status-display" v-if="activeAgentInfo">
                  <div class="agent-status-header">
                    <div class="agent-info">
                      <span class="agent-emoji">{{ activeAgentInfo.emoji }}</span>
                      <span class="agent-name">{{ activeAgentInfo.name }}</span>
                    </div>
                    <div class="agent-activity">
                      <div class="activity-indicator"></div>
                      <span class="activity-text">工作中</span>
                    </div>
                  </div>
                  <div class="agent-description">{{ activeAgentInfo.description }}</div>
                </div>
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
import SupervisorMonitor from '@/components/SupervisorMonitor.vue'

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
  components: {
    SupervisorMonitor
  },
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
    const forceUpdateKey = ref(0) // 强制更新键
    
    // UI 状态
    const isInputFocused = ref(false)
    
    // 增强的加载状态
    const currentProcessingStatus = ref('准备中')
    const currentAgentStatus = ref('')
    const activeAgentInfo = ref(null)
    const processingSteps = ref([])
    const currentStepIndex = ref(0)
    const loadingStartTime = ref(null)

    // Supervisor 监控状态
    const supervisorData = ref({})
    const showSupervisorMonitor = ref(true)

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


    // 流式卡片管理方法 - 支持累积式内容展示
    const createStreamingCard = (agentKey, content = '') => {
      const cardId = ++streamingCardIdCounter.value
      const newCard = {
        id: cardId,
        agentKey: agentKey,
        agent: getAgentDisplayName(agentKey),
        content: content,
        fullContent: content,
        contentSections: [], // 新增：内容区域数组，用于累积式展示
        sectionIdCounter: 0, // 新增：区域ID计数器
        lastContentLength: 0, // 新增：记录上次内容长度，用于检测新增内容
        timestamp: new Date(),
        isActive: true,
        isCollapsed: false
      }
      
      // 如果有初始内容，创建第一个区域
      if (content && content.trim()) {
        const firstSection = {
          id: ++newCard.sectionIdCounter,
          content: content,
          timestamp: new Date(),
          type: detectContentType(content),
          status: 'processing', // processing, completed, new
          isNew: true // 标记为新内容
        }
        newCard.contentSections.push(firstSection)
        newCard.lastContentLength = content.length
      }
      
      console.log('🆕 [流式卡片] 创建新卡片:', {
        cardId,
        agentKey,
        agentName: getAgentDisplayName(agentKey),
        contentLength: content.length,
        sectionsCount: newCard.contentSections.length,
        timestamp: newCard.timestamp.toLocaleString('zh-CN')
      })
      
      // 优化：只停用同一智能体的之前卡片，保持其他智能体卡片可见
      streamingCards.value.forEach(card => {
        if (card.agentKey === agentKey && card.isActive) {
          card.isActive = false
          // 将之前卡片的所有区域标记为已完成
          card.contentSections.forEach(section => {
            section.status = 'completed'
            section.isNew = false
          })
          console.log('🔄 [停用同类卡片] 停用同一智能体的之前卡片:', card.id)
        }
      })
      
      streamingCards.value.push(newCard)
      activeStreamingId.value = cardId
      scrollToBottom()
      return cardId
    }

    const updateStreamingCard = (cardId, content) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (!card) return
      
      // 检查内容是否有实质性变化
      if (content.length <= card.lastContentLength) {
        return // 没有新内容，不更新
      }
      
      // 获取新增的内容
      const newContent = content.substring(card.lastContentLength)
      
      console.log('📝 [卡片更新] 检测到新内容:', {
        cardId,
        agentKey: card.agentKey,
        totalLength: content.length,
        lastLength: card.lastContentLength,
        newContentLength: newContent.length,
        newContentPreview: newContent.substring(0, 100) + (newContent.length > 100 ? '...' : ''),
        fullContentPreview: content.substring(0, 200) + (content.length > 200 ? '...' : '')
      })
      
      // 将之前的区域标记为非新内容
      card.contentSections.forEach(section => {
        section.isNew = false
        if (section.status === 'processing') {
          section.status = 'completed'
        }
      })
      
      // 去除最小新增内容长度限制，支持显示全部内容
      const minNewContentLength = 1 // 移除字数限制，允许显示任何长度的新增内容
      
      if (newContent.length < minNewContentLength && card.contentSections.length > 0) {
        // 如果新增内容很少，合并到最后一个区域
        const lastSection = card.contentSections[card.contentSections.length - 1]
        if (lastSection && lastSection.status === 'completed') {
          // 将新内容追加到最后一个区域
          lastSection.content += newContent
          lastSection.timestamp = new Date()
          lastSection.status = 'processing'
          lastSection.isNew = true
          
          console.log('🔄 [内容合并] 将新增内容合并到最后区域:', {
            sectionId: lastSection.id,
            appendedLength: newContent.length,
            totalSectionLength: lastSection.content.length
          })
        } else {
          // 创建新的内容区域
          const newSection = {
            id: ++card.sectionIdCounter,
            content: newContent,
            timestamp: new Date(),
            type: detectContentType(newContent),
            status: 'processing',
            isNew: true
          }
          card.contentSections.push(newSection)
        }
      } else {
        // 创建新的内容区域，去除字数限制，显示全部内容
        let contentToAdd = newContent
        // 移除最大区域长度限制，支持显示完整内容
        
        // 直接显示完整的新增内容，不进行任何截取
        console.log('✨ [完整显示] 显示全部新增内容，无字数限制')
        
        const newSection = {
          id: ++card.sectionIdCounter,
          content: contentToAdd,
          fullContent: newContent, // 保存完整的新增内容
          timestamp: new Date(),
          type: detectContentType(newContent),
          status: 'processing',
          isNew: true
        }
        
        card.contentSections.push(newSection)
        
        console.log('✨ [新增区域] 创建新内容区域:', {
          sectionId: newSection.id,
          contentLength: newContent.length,
          displayLength: contentToAdd.length,
          totalSections: card.contentSections.length
        })
      }
      
      // 更新卡片的完整内容和元数据
      card.content = content
      card.fullContent = content
      card.lastContentLength = content.length
      card.timestamp = new Date()
      
      // 强制触发全局重新渲染
      forceUpdateKey.value++
      
      // 强制触发响应式更新并滚动
      nextTick(() => {
        scrollToBottom()
      })
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
      
      // 设置增强的加载状态
      isLoading.value = true
      loadingStartTime.value = new Date()
      
      // 初始化处理步骤
      initializeProcessingSteps()
      updateLoadingStatus('正在启动', '系统正在准备处理您的请求...')
      loadingText.value = '正在连接智能体系统...'
      
      // 模拟初始化步骤
      setTimeout(() => {
        updateProcessingStep(1)
        updateLoadingStatus('系统启动中', '正在激活多智能体协作系统...')
        loadingText.value = '智能体系统已激活，开始分析需求...'
      }, 500)

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
        resetLoadingState()
        
        // 清理流式卡片状态
        if (activeStreamingId.value) {
          finishStreamingCard(activeStreamingId.value)
        }
      }
    }

    // 简化的数据处理器
    const normalizeStreamData = (rawData) => {
      // 直接处理标准SSE格式
      if (rawData.type && rawData.agent) {
        return {
          type: rawData.type,
          agent: rawData.agent,
          content: rawData.content || '',
          sessionId: rawData.session_id,
          timestamp: new Date(),
          content_length: rawData.content_length || 0,
          is_incremental: rawData.is_incremental || false
        }
      }
      
      // 简单的fallback处理
      return {
        type: 'content_update',
        agent: 'supervisor',
        content: typeof rawData === 'string' ? rawData : JSON.stringify(rawData),
        timestamp: new Date()
      }
    }

    // 移除复杂的数据处理逻辑，简化为直接处理

    // 统一的流式数据处理器
    const createUnifiedStreamProcessor = () => {
      let agentCardMap = new Map()
      let fullResponse = ''
      let currentAgent = ''

      const processData = async (rawData) => {
        try {
          // 数据标准化
          const normalizedData = normalizeStreamData(rawData)
          if (!normalizedData) return

          console.log('🔄 [统一处理器] 处理标准化数据:', normalizedData)

          // 路由到对应处理器
          switch(normalizedData.type) {
            case 'start':
              return await handleStart(normalizedData)
            case 'agent_start':
              return await handleAgentStart(normalizedData)
            case 'content_update':
              return await handleContentUpdate(normalizedData)
            case 'agent_complete':
              return await handleAgentComplete(normalizedData)
            case 'done':
              return await handleDone(normalizedData)
            case 'error':
              return await handleError(normalizedData)
            default:
              console.warn('⚠️ [统一处理器] 未知数据类型:', normalizedData.type)
          }
        } catch (error) {
          console.error('❌ [统一处理器] 处理数据时出错:', error)
          await handleError({ error: error.message })
        }
      }

      const handleStart = async (data) => {
        console.log('🎬 [开始处理] 流式处理开始')
        updateProcessingStep(1, '系统已启动')
        updateLoadingStatus('连接成功', '开始处理您的请求...')
        
        if (data.sessionId) {
          sessionId.value = data.sessionId
        }
        
        // 更新监控数据 - 开始处理
        updateSupervisorData({
          status: 'processing',
          sessionId: data.sessionId,
          startTime: new Date()
        })
        
        // 添加开始处理的监控消息
        addSupervisorMessage('开始处理用户请求...', 'system_start')
        
        // 创建初始supervisor卡片
        const cardId = createStreamingCard('supervisor', data.content || '正在制定处理策略...')
        agentCardMap.set('supervisor', cardId)
        loadingText.value = data.content || '正在制定处理策略...'
        scrollToBottom()
      }

      const handleAgentStart = async (data) => {
        console.log('🤖 [智能体启动]:', data.agent)
        
        // 更新监控数据 - 智能体启动
        setCurrentActiveAgent(data.agent)
        addSupervisorMessage(`${getAgentDisplayName(data.agent)} 开始工作`, 'agent_start')
        
        // 立即创建卡片，提升用户体验
        if (!agentCardMap.has(data.agent)) {
          updateProcessingStep(2, '智能体开始工作')
          setActiveAgent(data.agent)
          loadingText.value = `正在调用 ${getAgentDisplayName(data.agent)}...`
          
          // 立即创建卡片，显示占位内容
          const cardId = createStreamingCard(data.agent, '🔄 正在生成内容，请稍候...')
          agentCardMap.set(data.agent, cardId)
          activeStreamingId.value = cardId
          console.log('🆕 [立即创建卡片] 智能体启动时创建卡片:', data.agent, 'ID:', cardId)
          scrollToBottom()
        } else {
          // 重新激活现有卡片
          const existingCardId = agentCardMap.get(data.agent)
          const existingCard = streamingCards.value.find(c => c.id === existingCardId)
          if (existingCard) {
            existingCard.isActive = true
            existingCard.isCollapsed = false
            activeStreamingId.value = existingCardId
            console.log('🔄 [重新激活卡片] 重新激活智能体卡片:', data.agent)
          }
        }
      }

      const handleContentUpdate = async (data) => {
        console.log('📝 [内容更新]:', data.agent, '长度:', data.content?.length || 0)
        
        // 确保卡片存在
        if (!agentCardMap.has(data.agent)) {
          await handleAgentStart(data)
        }
        
        // 更新监控数据 - 内容更新
        addSupervisorMessage(`${getAgentDisplayName(data.agent)} 正在生成内容...`, 'content_update')
        
        // 更新卡片内容
        const cardId = agentCardMap.get(data.agent)
        if (data.content) {
          updateStreamingCard(cardId, data.content)
          
          // 更新完整内容
          const card = streamingCards.value.find(c => c.id === cardId)
          if (card) {
            card.fullContent = data.content
          }
          
          console.log('🔄 [实时更新] 立即更新卡片内容:', cardId, '新长度:', data.content.length)
          
          // 强制触发响应式更新
          nextTick(() => {
            scrollToBottom()
          })
        }
        
        // 更新完整响应
        if (data.content && data.content.length > (fullResponse?.length || 0)) {
          fullResponse = data.content
        }
        
        // 更新加载状态
        updateLoadingStatus('内容生成中', `${getAgentDisplayName(data.agent)}正在生成内容...`)
        updateProcessingStep(3, '内容实时生成中')
        
        // 更新当前智能体
        if (data.agent !== currentAgent) {
          currentAgent = data.agent
          setActiveAgent(data.agent)
          setCurrentActiveAgent(data.agent)
        }
      }

      const handleAgentComplete = async (data) => {
        console.log('✅ [智能体完成]:', data.agent)
        
        // 更新监控数据 - 智能体完成
        addSupervisorMessage(`${getAgentDisplayName(data.agent)} 工作完成`, 'agent_complete')
        
        if (agentCardMap.has(data.agent)) {
          const cardId = agentCardMap.get(data.agent)
          finishStreamingCard(cardId)
          console.log('✅ [完成卡片] 标记智能体卡片为完成:', data.agent, 'ID:', cardId)
        }
        updateProcessingStep(4, '智能体工作完成')
      }

      const handleDone = async (data) => {
        console.log('🏁 [处理完成] 流式处理结束')
        
        // 更新监控数据 - 处理完成
        addSupervisorMessage('所有智能体工作完成，生成最终方案', 'system_complete')
        updateSupervisorData({
          status: 'completed',
          endTime: new Date()
        })
        
        // 完成所有卡片
        agentCardMap.forEach(cardId => {
          finishStreamingCard(cardId)
        })
        
        // 更新最终状态
        updateProcessingStep(4, '处理完成')
        updateLoadingStatus('完成', '内容生成完毕')
        
        // 只使用supervisor生成的内容作为最终响应，不包含其他智能体的内容
        const supervisorCardId = agentCardMap.get('supervisor')
        let finalResponse = ''
        
        if (supervisorCardId) {
          const supervisorCard = streamingCards.value.find(c => c.id === supervisorCardId)
          if (supervisorCard && supervisorCard.fullContent) {
            finalResponse = supervisorCard.fullContent
            console.log('📋 [最终响应] 使用supervisor生成的内容作为最终响应')
          }
        }
        
        // 如果没有supervisor内容，使用传入的内容作为备选
        if (!finalResponse && (data.content || fullResponse)) {
          finalResponse = data.content || fullResponse
        }
        
        // 添加最终消息（只包含supervisor的内容）
        if (finalResponse && finalResponse.trim()) {
          addMessage('assistant', finalResponse.trim())
        }
        
        return { completed: true, response: finalResponse }
      }

      const handleError = async (data) => {
        console.error('❌ [处理错误]:', data.error)
        updateLoadingStatus('错误', data.error)
        throw new Error(data.error)
      }

      // 处理复杂流式数据的特殊逻辑
      const handleComplexStreamData = async (updateData) => {
        // 更新 supervisor 监控数据
        if (updateData.supervisor && updateData.supervisor.messages) {
          supervisorData.value = {
            messages: updateData.supervisor.messages,
            currentAgent: currentAgent,
            timestamp: new Date()
          }
        }

        // 检查工具调用
        const checkToolCalls = (messages) => {
          for (const message of messages) {
            if (message && message.tool_calls && message.tool_calls.length > 0) {
              message.tool_calls.forEach(toolCall => {
                console.log(`🔧 工具调用: ${toolCall.name}`)
                loadingText.value = `正在执行 ${getToolDisplayName(toolCall.name)}...`
              })
            }
          }
        }

        // 处理supervisor消息
        if (updateData.supervisor && updateData.supervisor.messages) {
          checkToolCalls(updateData.supervisor.messages)
        }

        // 处理其他智能体消息
        const agentKeys = ['tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent']
        for (const agentKey of agentKeys) {
          if (updateData[agentKey] && updateData[agentKey].messages) {
            checkToolCalls(updateData[agentKey].messages)
          }
        }
      }

      return {
        processData,
        handleComplexStreamData,
        getFullResponse: () => fullResponse,
        getCurrentAgent: () => currentAgent,
        getAgentCardMap: () => agentCardMap
      }
    }

    // 重构后的调用多轮对话流式 API
    const callMultiTurnChatStream = async (userMessage) => {
      return new Promise((resolve, reject) => {
        // 清理之前的流式卡片
        clearStreamingCards()
        
        const requestData = {
          message: userMessage,
          session_id: sessionId.value
        }

        console.log('🚀 [API调用] 开始统一流式处理:', requestData)

        // 创建统一处理器
        const processor = createUnifiedStreamProcessor()

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
          
          // 旧的处理函数已被统一处理器替代，保留此注释作为参考
          
          function readStream() {
            return reader.read().then(async ({ done, value }) => {
              if (done) {
                console.log('📥 [流式完成] 数据接收完毕')
                
                // 直接处理完成逻辑
                const finalResponse = processor.getFullResponse()
                
                // 完成所有卡片
                const agentCardMap = processor.getAgentCardMap()
                agentCardMap.forEach(cardId => {
                  finishStreamingCard(cardId)
                })
                
                // 添加最终消息
                if (finalResponse && finalResponse.trim()) {
                  addMessage('assistant', finalResponse.trim())
                }
                
                resolve(finalResponse || '对话完成')
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
                      
                      // 使用统一处理器处理所有数据
                      const result = await processor.processData(data)
                      
                      // 如果返回完成信号，停止处理
                      if (result && result.completed) {
                        resolve(result.response || '对话完成')
                        return
                      }
                      
                      // 处理复杂流式数据的特殊逻辑
                      if (!data.type) {
                        await processor.handleComplexStreamData(data)
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
          clearStreamingCards()
          reject(error)
        })
      })
    }

    // 获取工具显示名称
    const getToolDisplayName = (toolName) => {
      const toolMap = {
        'transfer_to_tour_search_agent': '调用景点搜索专家',
        'transfer_to_day_plan_agent': '调用行程规划师',
        'transfer_to_live_transport_agent': '调用交通住宿顾问',
        'transfer_to_travel_butler_agent': '调用旅行管家',
        'transfer_back_to_supervisor': '返回总控智能体'
      }
      return toolMap[toolName] || toolName
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

    // 智能内容格式化函数
    const detectContentType = (content) => {
      if (!content || typeof content !== 'string') return 'text'
      
      const trimmed = content.trim()
      
      // 检测JSON格式
      if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || 
          (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
        try {
          JSON.parse(trimmed)
          return 'json'
        } catch (e) {
          // 不是有效JSON，继续检测其他格式
        }
      }
      
      // 检测Markdown格式
      if (trimmed.includes('##') || trimmed.includes('**') || 
          trimmed.includes('- ') || trimmed.includes('1. ') ||
          trimmed.includes('```') || trimmed.includes('`')) {
        return 'markdown'
      }
      
      return 'text'
    }

    const formatJsonToMarkdown = (jsonString) => {
      try {
        const parsed = JSON.parse(jsonString)
        
        // 如果是智能体响应数据，进行特殊处理
        if (isAgentResponseData(parsed)) {
          return formatAgentResponseData(parsed)
        }
        
        // 如果是旅游规划相关的结构化数据，进行特殊处理
        if (isTravelPlanData(parsed)) {
          return formatTravelPlanData(parsed)
        }
        
        // 通用JSON格式化
        return formatGenericJson(parsed)
        
      } catch (e) {
        // 如果解析失败，返回原始内容
        return jsonString
      }
    }

    const isAgentResponseData = (data) => {
      if (typeof data !== 'object' || !data) return false
      const agentKeys = ['supervisor', 'tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent']
      return agentKeys.some(key => key in data)
    }

    const isTravelPlanData = (data) => {
      if (typeof data !== 'object' || !data) return false
      const travelKeys = ['destination', 'days', 'itinerary', 'attractions', 'hotels', 'transport', 'budget']
      return travelKeys.some(key => key in data)
    }

    const formatAgentResponseData = (data) => {
      let formatted = '# 🤖 智能体协作响应\n\n'
      
      const agentNames = {
        'supervisor': '🎯 总控智能体',
        'tour_search_agent': '🔍 景点搜索专家',
        'day_plan_agent': '📅 行程规划师',
        'live_transport_agent': '🚗 交通住宿顾问',
        'travel_butler_agent': '🎒 旅行管家'
      }
      
      Object.entries(data).forEach(([agentKey, agentData]) => {
        if (agentNames[agentKey] && agentData && typeof agentData === 'object') {
          formatted += `## ${agentNames[agentKey]}\n\n`
          
          if (agentData.messages && Array.isArray(agentData.messages)) {
            agentData.messages.forEach(message => {
              if (message && message.content) {
                formatted += `${message.content}\n\n`
              }
            })
          } else if (agentData.content) {
            formatted += `${agentData.content}\n\n`
          }
        }
      })
      
      return formatted
    }

    const formatTravelPlanData = (data) => {
      let formatted = '# 🎯 旅游规划方案\n\n'
      
      if (data.destination) {
        formatted += `## 📍 目的地\n${data.destination}\n\n`
      }
      
      if (data.days) {
        formatted += `## 📅 行程天数\n${data.days}天\n\n`
      }
      
      if (data.budget) {
        formatted += `## 💰 预算\n${data.budget}\n\n`
      }
      
      if (data.itinerary && Array.isArray(data.itinerary)) {
        formatted += '## 📋 详细行程\n\n'
        data.itinerary.forEach((day, dayIndex) => {
          formatted += `### 第${dayIndex + 1}天\n`
          if (typeof day === 'string') {
            formatted += `${day}\n\n`
          } else if (typeof day === 'object') {
            if (day.activities) {
              day.activities.forEach(activity => {
                formatted += `- ${activity}\n`
              })
            }
            formatted += '\n'
          }
        })
      }
      
      if (data.attractions && Array.isArray(data.attractions)) {
        formatted += '## 🏛️ 推荐景点\n\n'
        data.attractions.forEach(attraction => {
          if (typeof attraction === 'string') {
            formatted += `- ${attraction}\n`
          } else if (typeof attraction === 'object') {
            formatted += `- **${attraction.name || '景点'}**`
            if (attraction.description) {
              formatted += `: ${attraction.description}`
            }
            formatted += '\n'
          }
        })
        formatted += '\n'
      }
      
      return formatted
    }

    const formatGenericJson = (data) => {
      let formatted = '# 📋 结构化信息\n\n'
      
      const formatValue = (value, depth = 0) => {
        const indent = '  '.repeat(depth)
        
        if (value === null) return '`null`'
        if (typeof value === 'boolean') return value ? '✅ 是' : '❌ 否'
        if (typeof value === 'number') return `**${value}**`
        if (typeof value === 'string') return value
        
        if (Array.isArray(value)) {
          if (value.length === 0) return '*(空列表)*'
          let result = '\n'
          value.forEach((item) => {
            result += `${indent}- ${formatValue(item, depth + 1)}\n`
          })
          return result
        }
        
        if (typeof value === 'object') {
          if (Object.keys(value).length === 0) return '*(空对象)*'
          let result = '\n'
          Object.entries(value).forEach(([key, val]) => {
            result += `${indent}**${key}**: ${formatValue(val, depth + 1)}\n`
          })
          return result
        }
        
        return String(value)
      }
      
      if (typeof data === 'object' && data !== null) {
        Object.entries(data).forEach(([key, value]) => {
          formatted += `## ${key}\n${formatValue(value)}\n\n`
        })
      } else {
        formatted += formatValue(data)
      }
      
      return formatted
    }

    const formatMessageContent = (content) => {
      if (!content) return ''
      
      const contentType = detectContentType(content)
      
      switch (contentType) {
        case 'json': {
          const markdownContent = formatJsonToMarkdown(content)
          return renderMarkdown(markdownContent)
        }
        case 'markdown':
          return renderMarkdown(content)
        default:
          return renderMarkdown(content)
      }
    }

    const formatStreamingContent = (content) => {
      if (!content) return ''
      
      const contentType = detectContentType(content)
      
      switch (contentType) {
        case 'json': {
          const markdownContent = formatJsonToMarkdown(content)
          return renderMarkdown(markdownContent)
        }
        case 'markdown':
          return renderMarkdown(content)
        default:
          return renderMarkdown(content)
      }
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

    // 获取内容类型标签
    const getContentTypeLabel = (type) => {
      const typeMap = {
        'text': '文本',
        'markdown': 'Markdown',
        'json': 'JSON',
        'code': '代码'
      }
      return typeMap[type] || '文本'
    }

    // 增强的加载状态管理
    const initializeProcessingSteps = () => {
      processingSteps.value = [
        '接收用户请求',
        '启动智能体系统',
        '分析旅游需求',
        '搜索相关信息',
        '生成个性化方案'
      ]
      currentStepIndex.value = 0
    }

    const updateProcessingStep = (stepIndex, customStep = null) => {
      if (customStep) {
        processingSteps.value[stepIndex] = customStep
      }
      currentStepIndex.value = stepIndex
    }

    const setActiveAgent = (agentKey) => {
      const agentInfoMap = {
        'supervisor': {
          name: '总控智能体',
          emoji: '🎯',
          description: '正在协调各个专业智能体，制定处理策略...'
        },
        'tour_search_agent': {
          name: '景点搜索专家',
          emoji: '🔍',
          description: '正在搜索相关景点信息和用户评价...'
        },
        'day_plan_agent': {
          name: '行程规划师',
          emoji: '📅',
          description: '正在制定详细的每日行程安排...'
        },
        'live_transport_agent': {
          name: '交通住宿顾问',
          emoji: '🚗',
          description: '正在查询交通方式和住宿推荐...'
        },
        'travel_butler_agent': {
          name: '旅行管家',
          emoji: '🎒',
          description: '正在整理旅行建议和注意事项...'
        }
      }
      
      activeAgentInfo.value = agentInfoMap[agentKey] || null
      
      if (activeAgentInfo.value) {
        currentAgentStatus.value = `${activeAgentInfo.value.name}正在工作...`
        currentProcessingStatus.value = '智能体处理中'
      }
    }

    const updateLoadingStatus = (status, agentStatus = '') => {
      currentProcessingStatus.value = status
      if (agentStatus) {
        currentAgentStatus.value = agentStatus
      }
    }

    const resetLoadingState = () => {
      currentProcessingStatus.value = '准备中'
      currentAgentStatus.value = ''
      activeAgentInfo.value = null
      processingSteps.value = []
      currentStepIndex.value = 0
      loadingStartTime.value = null
    }

    // 生命周期
    onMounted(() => {
      addMessage('assistant', '您好！我是您的智能旅游规划助手。我会通过多轮对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！')
      scrollToBottom()
    })

    // Supervisor 监控相关方法
    const onSupervisorExpanded = (expanded) => {
      console.log('Supervisor 监控面板展开状态:', expanded)
      
      // 输出当前监控数据状态
      console.log('当前 supervisorData:', supervisorData.value)
      console.log('监控数据详情:', {
        hasMessages: !!(supervisorData.value.messages && supervisorData.value.messages.length > 0),
        messagesCount: supervisorData.value.messages ? supervisorData.value.messages.length : 0,
        currentAgent: supervisorData.value.currentAgent,
        timestamp: supervisorData.value.timestamp,
        dataKeys: Object.keys(supervisorData.value)
      })
    }

    // 更新 supervisor 监控数据的方法
    const updateSupervisorData = (newData) => {
      console.log('🔄 [监控数据更新] 更新 supervisor 监控数据:', newData)
      
      // 合并新数据到现有数据
      supervisorData.value = {
        ...supervisorData.value,
        ...newData,
        timestamp: new Date()
      }
      
      console.log('📊 [监控数据] 更新后的完整数据:', supervisorData.value)
    }

    // 添加监控消息的方法
    const addSupervisorMessage = (message, type = 'supervisor_response') => {
      console.log('📝 [监控消息] 添加新的监控消息:', { message, type })
      
      if (!supervisorData.value.messages) {
        supervisorData.value.messages = []
      }
      
      const newMessage = {
        content: message,
        type: type,
        timestamp: new Date(),
        role: 'assistant'
      }
      
      supervisorData.value.messages.push(newMessage)
      
      // 触发响应式更新
      supervisorData.value = { ...supervisorData.value }
      
      console.log('📊 [监控消息] 当前消息总数:', supervisorData.value.messages.length)
    }

    // 设置当前活跃智能体
    const setCurrentActiveAgent = (agentKey) => {
      console.log('🤖 [活跃智能体] 设置当前活跃智能体:', agentKey)
      
      updateSupervisorData({
        currentAgent: agentKey,
        activeAgentInfo: {
          key: agentKey,
          name: getAgentDisplayName(agentKey),
          emoji: getAgentEmoji(agentKey),
          status: '工作中',
          startTime: new Date()
        }
      })
    }

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
      currentProcessingStatus,
      currentAgentStatus,
      activeAgentInfo,
      processingSteps,
      currentStepIndex,
      supervisorData,
      showSupervisorMonitor,
      
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
      getContentLength,
      getContentTypeLabel,
      initializeProcessingSteps,
      updateProcessingStep,
      setActiveAgent,
      updateLoadingStatus,
      resetLoadingState,
      onSupervisorExpanded,
      updateSupervisorData,
      addSupervisorMessage,
      setCurrentActiveAgent
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
  padding-bottom: 250px;
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

.message-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

/* 累积式内容展示样式 */
.content-sections-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-section {
  border-radius: 8px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.4s ease-out;
}

.content-section.section-new {
  background: rgba(66, 153, 225, 0.08);
  border: 1px solid rgba(66, 153, 225, 0.2);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.15);
}

.content-section.section-processing {
  background: rgba(255, 193, 7, 0.05);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.content-section.section-completed {
  background: rgba(56, 161, 105, 0.05);
  border: 1px solid rgba(56, 161, 105, 0.15);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 12px;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-status-icon {
  font-size: 14px;
  animation: pulse 1.5s ease-in-out infinite;
}

.section-label {
  font-weight: 600;
  color: #2d3748;
}

.section-time {
  color: #718096;
  font-size: 11px;
}

.section-type-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.section-type-badge.type-text {
  background: #e2e8f0;
  color: #4a5568;
}

.section-type-badge.type-markdown {
  background: #e6fffa;
  color: #2f855a;
}

.section-type-badge.type-json {
  background: #fef5e7;
  color: #d69e2e;
}

.section-type-badge.type-code {
  background: #edf2f7;
  color: #2d3748;
}

.section-content {
  padding: 0;
}

.section-content .streaming-content {
  margin-bottom: 0;
  border-radius: 0 0 6px 6px;
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

.sections-count {
  color: #4299e1;
  font-weight: 500;
  background: rgba(66, 153, 225, 0.1);
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
}

.section-length-info {
  color: #718096;
  font-size: 10px;
  background: rgba(113, 128, 150, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 500;
}

/* 增强的加载状态样式 */
.loading-message {
  animation: fadeInUp 0.4s ease-out;
}

.loading-avatar {
  position: relative;
  overflow: hidden;
}

.avatar-spinner {
  animation: pulse 2s ease-in-out infinite;
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

/* 响应式设计 - 增强加载状态 */
@media (max-width: 768px) {
  .loading-card {
    padding: 16px;
  }
  
  .loading-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .loading-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .loading-spinner-enhanced {
    width: 24px;
    height: 24px;
    border-width: 2px;
  }
  
  .processing-steps {
    padding: 12px;
  }
  
  .agent-status-display {
    padding: 12px;
  }
  
  .agent-status-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
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
    padding-bottom: 280px;
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
