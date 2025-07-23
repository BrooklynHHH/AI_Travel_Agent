<template>
  <div class="multi-turn-chat-container">
    <!-- 头部标题 -->
    <div class="header">
      <h1 class="title">🤖 智能多轮对话助手</h1>
      <p class="subtitle">基于多智能体系统的智能旅游规划对话</p>
    </div>
<!-- lizy12 -->
    <!-- 焦点区 -->
    <div v-if="showFocusArea && !isMinimized" class="focus-area">
      <FocusAgentCard
        :agent-info="focusedAgentInfo.agentInfo"
        :streaming-content="focusedAgentInfo.streamingContent"
        :current-status="focusedAgentInfo.currentStatus"
        @minimize="handleMinimizeFocus"
      />
    </div>

    <!-- 最小化后的焦点区恢复按钮 -->
    <div v-if="showFocusArea && isMinimized" class="minimized-focus-indicator">
      <button @click="handleRestoreFocus" class="restore-focus-btn">
        <div class="restore-btn-content">
          <div class="restore-agent-info">
            <span class="restore-agent-icon">{{ focusedAgentInfo.agentInfo.icon }}</span>
            <span class="restore-agent-name">{{ focusedAgentInfo.agentInfo.name }}</span>
          </div>
          <span class="restore-text">展开焦点区</span>
        </div>
      </button>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages-wrapper" :class="{ 'with-focus-area': showFocusArea && !isMinimized }">
        <!-- 欢迎消息 -->
        <div v-if="Object.keys(agentSessionsByTurn).length === 0" class="welcome-message">
          <div class="welcome-content">
            <div class="welcome-avatar">🤖</div>
            <div class="welcome-text">
              <div class="welcome-title">您好！我是您的智能旅游规划助手</div>
              <div class="welcome-subtitle">我会通过多轮对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！</div>
            </div>
          </div>
        </div>

        <!-- 按时间顺序交替显示用户消息和轮次容器 -->
        <template v-for="(turnData, turnId) in agentSessionsByTurn" :key="turnId">
          <!-- 用户消息 -->
          <div class="message-item">
            <div class="user-message-standalone">
              <div class="user-message-container">
                <div class="user-avatar">👤</div>
                <div class="user-message-content">
                  <div class="user-message-text">{{ turnData.turnInfo.userMessage }}</div>
                </div>
              </div>
              <div class="message-time">{{ formatTime(turnData.turnInfo.timestamp) }}</div>
            </div>
          </div>

          <!-- 对应的轮次容器 -->
          <div class="conversation-turn">
            <!-- 轮次标题栏 -->
            <div class="turn-header">
            <div class="turn-info">
              <div class="turn-label">轮次 #{{ getTurnNumber(turnId) }}</div>
              <div class="turn-time">{{ formatTime(turnData.turnInfo.timestamp) }}</div>
            </div>
            <div class="turn-status">
            <div class="turn-agents-info">
              <span class="agents-icon">📤</span>
              <span class="agents-text">智能体响应 ({{ getAgentCount(turnData.sessions) }}个)</span>
            </div>
              <div class="turn-duration" v-if="turnData.turnInfo.status === 'completed'">
                <span class="duration-icon">⏱️</span>
                <span class="duration-text">{{ calculateTurnDuration(turnData) }}</span>
              </div>
              <div v-else class="streaming-status">
                <span class="pulse-dot"></span>
                <span class="streaming-text">处理中...</span>
              </div>
            </div>
          </div>

          <!-- 智能体响应区域 -->
          <div class="turn-agents-response">
            <div class="agents-grid" :class="{ 'with-focus-area': showFocusArea && !isMinimized }">
              <!-- 智能体卡片 -->
              <AgentCard
                v-for="session in turnData.sessions.filter(s => s.agentInfo.key !== 'tools')"
                :key="session.uniqueKey"
                :agent-info="session.agentInfo"
                :conversations="session.conversations"
                :current-status="session.currentStatus"
                :streaming-content="session.streamingContent"
                :is-in-focus="focusedAgentInfo && focusedAgentInfo.agentInfo.key === session.agentInfo.key"
                @toggle-card="handleToggleCard"
                @toggle-conversation="handleToggleConversation"
                @focus-agent="handleFocusAgent"
                class="agent-response-card"
              />
              
              <!-- 工具调用卡片 - 每个工具调用对话都创建一个独立的卡片 -->
              <template v-for="session in turnData.sessions.filter(s => s.agentInfo.key === 'tools')" :key="session.uniqueKey">
                <ToolsCard
                  v-for="conversation in session.conversations.filter(conv => conv.isToolCall)"
                  :key="`${session.uniqueKey}_${conversation.id}`"
                  :tool-content="conversation.content"
                  :tool-type="conversation.toolCallMetadata?.toolType || 'unknown'"
                  :tool-name="conversation.toolCallMetadata?.toolName || 'unknown_tool'"
                  :call-index="conversation.toolCallMetadata?.callIndex || 1"
                  :timestamp="conversation.timestamp"
                  :processing-time="conversation.endTime - conversation.startTime"
                  :status="conversation.status"
                  @expand="handleToolExpand"
                  @collapse="handleToolCollapse"
                  @error="handleToolError"
                  @copy="handleToolCopy"
                  class="tool-response-card"
                />
              </template>
            </div>
          </div>
          </div>
        </template>
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
import { ref, onMounted, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import { API_CONFIG } from '@/config/api.config.js'
import AgentCard from '@/components/AgentCard.vue'
import FocusAgentCard from '@/components/FocusAgentCard.vue'
import ToolsCard from '@/components/ToolsCard.vue'
import { useAgentSessions } from '@/composables/useAgentSessions.js'

// 智能工具类型检测函数
const detectToolType = (toolName, content) => {
  if (!content || typeof content !== 'string') {
    return 'unknown'
  }

  const trimmedContent = content.trim()
  
  // JSON工具检测
  if (trimmedContent.startsWith('{') || trimmedContent.startsWith('[')) {
    try {
      JSON.parse(trimmedContent)
      return 'json'
    } catch (e) {
      // 可能是格式不完整的JSON，继续其他检测
    }
  }
  
  // 搜索工具检测
  if (toolName.toLowerCase().includes('search') || 
      trimmedContent.includes('search_ref') || 
      trimmedContent.includes('search_tool') ||
      trimmedContent.includes('"type":"search') ||
      trimmedContent.includes("'type':'search")) {
    return 'search'
  }
  
  // API工具检测
  if (toolName.toLowerCase().includes('api') || 
      trimmedContent.includes('http://') || 
      trimmedContent.includes('https://') ||
      trimmedContent.includes('status_code') ||
      trimmedContent.includes('response')) {
    return 'api'
  }
  
  // 文件工具检测
  if (toolName.toLowerCase().includes('file') || 
      trimmedContent.includes('file_path') || 
      trimmedContent.includes('directory') ||
      trimmedContent.includes('path:')) {
    return 'file'
  }

  // 数据库工具检测
  if (toolName.toLowerCase().includes('db') || 
      toolName.toLowerCase().includes('sql') || 
      trimmedContent.includes('SELECT') || 
      trimmedContent.includes('INSERT') ||
      trimmedContent.includes('UPDATE')) {
    return 'database'
  }
  
  // 默认文本类型
  return 'text'
}

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// 智能体配置
const agentConfig = {
  'supervisor': { 
    name: '总指挥官', 
    icon: '🎯', 
    color: '#2563eb',
    description: '分析需求，制定策略'
  },
  'tour_search_agent': { 
    name: '景点搜索专家', 
    icon: '🔍', 
    color: '#059669',
    description: '搜索景点和活动'
  },
  'day_plan_agent': { 
    name: '行程规划师', 
    icon: '📅', 
    color: '#ea580c',
    description: '制定详细行程'
  },
  'live_transport_agent': { 
    name: '交通住宿专家', 
    icon: '🚗', 
    color: '#7c3aed',
    description: '规划交通和住宿'
  },
  'travel_butler_agent': { 
    name: '贴心旅行管家', 
    icon: '🎒', 
    color: '#db2777',
    description: '提供贴心建议'
  },
  'tools': { 
    name: '工具调用', 
    icon: '🔧', 
    color: '#6b7280',
    description: '执行API调用'
  }
}

export default {
  name: 'NewMultiTurnChatView',
  components: {
    AgentCard,
    FocusAgentCard,
    ToolsCard
  },
  setup() {
    // 使用智能体会话管理（新的轮次系统）
    const {
      agentSessions,
      activeAgentSessions,
      streamingAgentsCount,
      totalConversationsCount,
      agentSessionsByTurn,
      showFocusArea,
      focusedAgentInfo,
      createNewTurn,
      completeTurn,
      handleAgentStart,
      handleAgentContentUpdate,
      handleAgentComplete,
      handleToolCall,
      toggleCardCollapse,
      toggleConversationCollapse,
      handleCopyContent,
      resetAllSessions,
      setFocusedAgent
    } = useAgentSessions()

    // 核心状态
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const sessionId = ref(null)
    const isInputFocused = ref(false)
    const inputField = ref(null)
    const chatContainer = ref(null)

    // API 配置
    const API_BASE_URL = API_CONFIG.BASE_URL


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


    // 格式化持续时间
    const formatDuration = (startTime, endTime) => {
      if (!startTime) return ''
      const duration = (endTime || Date.now()) - startTime
      if (duration < 1000) return `${duration}ms`
      return `${(duration / 1000).toFixed(1)}s`
    }

    // 获取轮次编号
    const getTurnNumber = (turnId) => {
      const match = turnId.match(/turn_(\d+)_/)
      return match ? match[1] : '1'
    }

    // 计算轮次处理时长
    const calculateTurnDuration = (turnData) => {
      if (!turnData.sessions.length) return '0s'
      
      let totalDuration = 0
      let hasValidDuration = false
      
      turnData.sessions.forEach(session => {
        session.conversations.forEach(conv => {
          if (conv.startTime && conv.endTime) {
            totalDuration += (conv.endTime - conv.startTime)
            hasValidDuration = true
          }
        })
      })
      
      if (!hasValidDuration) return '0s'
      
      if (totalDuration < 1000) return `${totalDuration}ms`
      return `${(totalDuration / 1000).toFixed(1)}s`
    }

    // 复制用户消息
    const copyUserMessage = async (message) => {
      try {
        await navigator.clipboard.writeText(message)
        console.log('📋 用户消息已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
      }
    }

    // 计算智能体数量（排除工具调用）
    const getAgentCount = (sessions) => {
      return sessions.filter(session => 
        session.agentInfo.key !== 'tools' && 
        session.agentInfo.key !== 'unified_stream'
      ).length
    }


    // 优化后的DOM更新函数
    const updateDOM = async () => {
      await nextTick()
      scrollToBottom()
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
        isStreaming: true,
        agentOutputs: [], // 存储各个agent的输出
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


    // 流式数据处理 - 使用新的智能体会话管理系统
    const processStreamData = async (data) => {
      console.log('📥 [流式数据]:', data)

      switch (data.type) {
        case 'start':
          console.log('🎬 [开始处理]')
          if (data.session_id) {
            sessionId.value = data.session_id
          }
          break

        case 'agent_start':
          console.log('🤖 [智能体启动]:', data.agent)
          if (data.agent && data.agent !== 'tools') {
            handleAgentStart(data.agent)
          }
          break

        case 'content_update':
          console.log('📝 [内容更新]:', data.agent, '长度:', data.content?.length || 0)
          if (data.content && data.agent) {
            await handleAgentContentUpdate(data.agent, data.content, false)
          }
          break

        case 'done':
          console.log('✅ [处理完成]')
          // 完成所有活跃的智能体会话
          Object.keys(agentSessions).forEach(agentKey => {
            const session = agentSessions[agentKey]
            if (session.currentStatus === 'streaming') {
              handleAgentComplete(agentKey)
            }
          })
          break

        case 'error':
          console.error('❌ [处理错误]:', data.message)
          // 处理错误，完成所有活跃会话
          Object.keys(agentSessions).forEach(agentKey => {
            const session = agentSessions[agentKey]
            if (session.currentStatus === 'streaming') {
              handleAgentComplete(agentKey, `错误：${data.message}`)
            }
          })
          break

        case 'raw_chunk': {
          // console.log('🔍 [原始数据块]:', JSON.stringify(data.data, null, 2))
          
          // 处理supervisor流式输出
          if (data.data && data.data.chunk && Array.isArray(data.data.chunk) && data.data.chunk.length >= 2) {
            const chunk = data.data.chunk
            const content = chunk[0]?.content || ''
            const metadata = chunk[1] || {}
            const langgraph_node = metadata.langgraph_node || ''
            const checkpoint_ns = metadata.checkpoint_ns || ''
            
            console.log(`📊 [数据解析] langgraph_node: "${langgraph_node}", checkpoint_ns: "${checkpoint_ns}"`)
            console.log(`📝 [内容] content: "${content}"`)
            
            // 处理工具调用 - 使用新的替换模式和工具类型检测
            if (langgraph_node === "tools" || langgraph_node === "tour_search_agent") {
              const toolName = chunk[0]?.name || 'unknown_tool'
              let content = chunk[0]?.content || ''
              
              console.log(`🔧 [工具调用] 工具名称：${toolName}`)
              console.log(`� [工具调用] 原始内容长度：${content.length}`)
              console.log(`� [工具调用] 原始内容预览：${content.substring(0, 200)}...`)
              
              if (content) {
                // 🔑 关键改进：使用智能工具类型检测
                const toolType = detectToolType(toolName, content)
                console.log(`🔧 [工具调用] 检测到工具类型：${toolType}`)
                
                // 🔑 关键改进：使用新卡片模式处理工具调用
                console.log(`🔧 [工具调用] 使用新卡片模式处理工具调用`)
                await handleToolCall(toolName, content, { 
                  mode: 'new_card',  // 每次创建新卡片
                  toolType: toolType
                })
                
                console.log(`🔧 [工具调用] 工具调用处理完成`)
              }
            }
            
            // 处理智能体输出
            if (langgraph_node === "agent" || langgraph_node === "supervisor") {
              console.log(`🤖 [智能体] 检测到智能体节点: ${langgraph_node}`)
              console.log(`🤖 [智能体] checkpoint_ns: ${checkpoint_ns}`)
              
              // 解析智能体名称
              const pattern = /(\w+):([\w-]+)/
              const match = checkpoint_ns.match(pattern)
              
              if (match) {
                const agentName = match[1]
                console.log(`🎯 [智能体识别] 智能体名称: ${agentName}`)
                
                // 确保智能体已启动
                handleAgentStart(agentName)
                
                if (content) {
                  console.log(`📝 [智能体内容] 更新内容，长度: ${content.length}`)
                  await handleAgentContentUpdate(agentName, content, true)
                } else {
                  console.log(`⚠️ [智能体内容] 内容为空`)
                }
              } else {
                console.log(`⚠️ [智能体解析] 无法解析 checkpoint_ns: ${checkpoint_ns}`)
                
                // 如果无法解析，尝试直接使用 langgraph_node 作为智能体名称
                if (langgraph_node === "supervisor") {
                  console.log(`🎯 [智能体识别] 使用默认名称: supervisor`)
                  handleAgentStart('supervisor')
                  if (content) {
                    await handleAgentContentUpdate('supervisor', content, true)
                  }
                }
              }
            }
            
            console.log('---')
          }
          
          // 处理其他可能的数据格式
          let newToken = ''
          
          if (data.data && data.data.chunk && Array.isArray(data.data.chunk) && !data.data.chunk[1]) {
            data.data.chunk.forEach(item => {
              if (item && item.content) {
                newToken = item.content
              }
            })
          }
          
          if (data.data && data.data.output_messages && Array.isArray(data.data.output_messages)) {
            data.data.output_messages.forEach(msg => {
              if (msg.type === 'token_stream' && msg.content && msg.content.token) {
                newToken = msg.content.token
              }
            })
          }
          
          if (data.data && typeof data.data === 'string') {
            newToken = data.data
          }
          
          if (data.data && data.data.content && typeof data.data.content === 'string') {
            newToken = data.data.content
          }
          
          if (newToken) {
            console.log('📝 [新增token]:', newToken.length, '字符:', JSON.stringify(newToken.substring(0, 100)))
            await handleAgentContentUpdate('unified_stream', newToken, true)
          }
          break
        }

        default:
          console.warn('⚠️ [未知数据类型]:', data.type)
      }

      if (data.data != null && Object.hasOwn(data.data, 'stream_mode')){
        console.log('type : stream_mode', data)
      }
    }

    // 提取完整SSE消息的辅助函数
    const extractCompleteMessages = (buffer) => {
      const messages = []
      let remaining = buffer
      
      // SSE消息以\n\n分隔，但需要考虑data:行内的\n
      const parts = buffer.split('\n\n')
      
      // 最后一部分可能是不完整的，保留在buffer中
      for (let i = 0; i < parts.length - 1; i++) {
        if (parts[i].trim()) {
          messages.push(parts[i] + '\n\n')
        }
      }
      
      // 最后一部分作为剩余数据
      remaining = parts[parts.length - 1]
      
      return {
        complete: messages,
        remaining: remaining
      }
    }

    // 处理单个完整SSE消息的函数
    const processSSEMessage = async (message, assistantMessage) => {
      const lines = message.split('\n')
      
      for (const line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine.startsWith('data: ')) {
          try {
            const jsonStr = trimmedLine.slice(6).trim()
            if (jsonStr && jsonStr !== '[DONE]') {
              const data = JSON.parse(jsonStr)
              await processStreamData(data, assistantMessage)
              // 优化：使用轻量级DOM更新
              await updateDOM()
            } else if (jsonStr === '[DONE]') {
              console.log('📥 [流式结束标记] 收到 [DONE] 标记')
              // 确保消息状态正确更新为完成
              updateAssistantMessage(assistantMessage.id, {
                isStreaming: false
              })
              // 标记所有agent输出为完成
              if (assistantMessage.agentOutputs) {
                assistantMessage.agentOutputs.forEach(output => {
                  if (output.status === 'processing') {
                    output.status = 'completed'
                    output.endTime = Date.now()
                    output.isActive = false
                  }
                })
              }
              // 最终DOM更新
              await updateDOM()
            }
          } catch (e) {
            console.warn('⚠️ [解析警告] 解析流式数据失败:', e, '原始数据:', trimmedLine)
          }
        }
      }
    }

    // 处理buffer中剩余数据的函数
    const processBufferData = async (buffer, assistantMessage) => {
      if (!buffer.trim()) return
      
      console.log('📦 [处理剩余数据] 长度:', buffer.length)
      
      // 尝试处理剩余数据，可能是不完整的SSE消息
      const lines = buffer.split('\n')
      for (const line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine.startsWith('data: ')) {
          try {
            const jsonStr = trimmedLine.slice(6).trim()
            if (jsonStr && jsonStr !== '[DONE]') {
              const data = JSON.parse(jsonStr)
              await processStreamData(data, assistantMessage)
              await updateDOM()
            }
          } catch (e) {
            console.warn('⚠️ [剩余数据解析警告] 可能是不完整的数据:', e, '原始数据:', trimmedLine)
          }
        }
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
        fetch(`${API_BASE_URL}${API_CONFIG.ENDPOINTS.STREAM}`, {
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

          // 数据缓冲区，用于处理跨chunk的SSE消息
          let buffer = ''

          async function readStream() {
            try {
              const { done, value } = await reader.read()
              
              if (done) {
                console.log('📥 [流式完成] 数据接收完毕')
                
                // 处理buffer中剩余的数据
                if (buffer.trim()) {
                  await processBufferData(buffer, assistantMessage)
                }
                
                // 确保消息状态正确更新为完成
                updateAssistantMessage(assistantMessage.id, {
                  isStreaming: false
                })
                // 标记所有agent输出为完成
                if (assistantMessage.agentOutputs) {
                  assistantMessage.agentOutputs.forEach(output => {
                    if (output.status === 'processing') {
                      output.status = 'completed'
                      output.endTime = Date.now()
                      output.isActive = false
                    }
                  })
                }
                resolve('流式处理完成')
                return
              }

              // 解码数据块并拼接到buffer
              const chunk = decoder.decode(value, { stream: true })
              buffer += chunk
              
              console.log('📦 [数据块] 长度:', chunk.length, 'Buffer总长度:', buffer.length)

              // 提取完整的SSE消息
              const messageResult = extractCompleteMessages(buffer)
              
              // 处理每个完整消息
              for (const message of messageResult.complete) {
                await processSSEMessage(message, assistantMessage)
              }
              
              // 更新buffer为剩余的不完整数据
              buffer = messageResult.remaining
              
              if (messageResult.remaining) {
                console.log('📦 [剩余数据] 长度:', messageResult.remaining.length, '内容预览:', messageResult.remaining.substring(0, 100))
              }

              return readStream()
            } catch (error) {
              console.error('❌ [流式读取错误]:', error)
              reject(error)
            }
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

      // 创建新的对话轮次
      const turnId = createNewTurn(userMessage)
      console.log(`🆕 [新轮次] 创建轮次: ${turnId}`)

      // 添加用户消息
      addUserMessage(userMessage)
      
      // 清空输入框
      userInput.value = ''
      autoResizeTextarea()

      // 立即滚动到底部，显示用户消息
      await nextTick()
      scrollToBottom()

      // 设置加载状态
      isLoading.value = true

      try {
        // 调用流式 API
        await callStreamAPI(userMessage)
        console.log('✅ [发送消息] 处理完成')
        
        // 完成当前轮次
        completeTurn(turnId)
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
        
        // 完成当前轮次（即使出错）
        completeTurn(turnId)
      } finally {
        isLoading.value = false
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
          await fetch(`${API_BASE_URL}${API_CONFIG.ENDPOINTS.SESSIONS}/${sessionId.value}/clear`, {
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
      
      // 关键修复：重置智能体会话管理系统
      resetAllSessions()
      
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

    // 智能体卡片事件处理
    const handleToggleCard = (agentKey, isCollapsed) => {
      toggleCardCollapse(agentKey, isCollapsed)
    }

    const handleToggleConversation = (agentKey, conversationId) => {
      toggleConversationCollapse(agentKey, conversationId)
    }

    const handleCopyContentAction = (agentKey, content) => {
      handleCopyContent(agentKey, content)
      // 可以添加复制成功的提示
      console.log(`📋 已复制 ${agentKey} 的内容`)
    }

    // 焦点区处理方法
    const isMinimized = ref(false)
    
    const handleMinimizeFocus = () => {
      isMinimized.value = true
      console.log('🎯 [焦点区] 用户手动最小化焦点区')
    }
    
    const handleRestoreFocus = () => {
      isMinimized.value = false
      console.log('🎯 [焦点区] 用户恢复焦点区')
    }
    
    const handleFocusAgent = (agentKey) => {
      // 使用已经存在的智能体会话管理系统实例
      setFocusedAgent(agentKey)
      
      // 如果焦点区域被最小化，恢复显示
      if (isMinimized.value) {
        isMinimized.value = false
      }
      
      console.log(`🎯 [焦点切换] 用户手动切换焦点到: ${agentKey}`)
    }

    // 工具卡片相关方法
    const getLatestToolContent = (session) => {
      if (!session.conversations || session.conversations.length === 0) {
        return ''
      }
      
      const latestConversation = session.conversations[session.conversations.length - 1]
      return latestConversation.content || ''
    }

    const getToolType = (session) => {
      // 根据工具内容或会话信息判断工具类型
      const content = getLatestToolContent(session)
      
      if (content.includes('search_ref') || content.includes('search_tool')) {
        return 'search'
      }
      
      if (content.includes('api') || content.includes('http')) {
        return 'api'
      }
      
      if (content.includes('database') || content.includes('sql')) {
        return 'database'
      }
      
      if (content.includes('file') || content.includes('path')) {
        return 'file'
      }
      
      return 'unknown'
    }

    const getToolProcessingTime = (session) => {
      if (!session.conversations || session.conversations.length === 0) {
        return 0
      }
      
      const latestConversation = session.conversations[session.conversations.length - 1]
      if (latestConversation.startTime && latestConversation.endTime) {
        return latestConversation.endTime - latestConversation.startTime
      }
      
      if (latestConversation.startTime) {
        return Date.now() - latestConversation.startTime
      }
      
      return 0
    }

    const handleToolExpand = () => {
      console.log('🔧 [工具卡片] 用户展开工具卡片')
    }

    const handleToolCollapse = () => {
      console.log('🔧 [工具卡片] 用户折叠工具卡片')
    }

    const handleToolError = (error) => {
      console.error('🔧 [工具卡片] 工具解析错误:', error)
    }

    const handleToolCopy = (content) => {
      console.log('🔧 [工具卡片] 用户复制工具内容:', content.substring(0, 100) + '...')
    }

    // 返回所有需要在模板中使用的数据和方法
    return {
      // 数据
      messages,
      userInput,
      isLoading,
      sessionId,
      isInputFocused,
      inputField,
      chatContainer,
      
      // 智能体会话数据
      activeAgentSessions,
      streamingAgentsCount,
      totalConversationsCount,
      agentSessionsByTurn,
      
      // 焦点区数据
      showFocusArea,
      focusedAgentInfo,
      
      // 方法
      formatTime,
      formatMessageContent,
      formatDuration,
      getTurnNumber,
      calculateTurnDuration,
      copyUserMessage,
      getAgentCount,
      sendMessage,
      handleKeyDown,
      quickStart,
      resetConversation,
      scrollToBottom,
      
      // 智能体卡片事件处理
      handleToggleCard,
      handleToggleConversation,
      handleCopyContent: handleCopyContentAction,
      
      // 焦点区事件处理
      handleMinimizeFocus,
      handleRestoreFocus,
      handleFocusAgent,
      isMinimized,
      
      // 工具卡片事件处理
      getLatestToolContent,
      getToolType,
      getToolProcessingTime,
      handleToolExpand,
      handleToolCollapse,
      handleToolError,
      handleToolCopy
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  overflow: hidden;
  z-index: 1000;
}

.header {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  padding: 16px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 10;
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 6px 0;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 13px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

/* 焦点区样式 - 悬浮在右侧 */
.focus-area {
  position: fixed;
  top: 120px;
  right: 24px;
  bottom: 200px; /* 为底部输入区域留出足够空间 */
  width: 380px;
  z-index: 1000;
  animation: focusSlideIn 0.3s ease-out;
  overflow: hidden;
}

.focus-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4299e1, #3182ce, #2563eb);
  animation: focusShimmer 2s ease-in-out infinite;
}

@keyframes focusShimmer {
  0%, 100% { 
    opacity: 1; 
    transform: scaleX(1);
  }
  50% { 
    opacity: 0.8; 
    transform: scaleX(1.02);
  }
}

@keyframes focusSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 最小化后的焦点区恢复按钮样式 */
.minimized-focus-indicator {
  position: fixed;
  top: 120px;
  right: 24px;
  z-index: 1000;
  animation: minimizedSlideIn 0.3s ease-out;
}

.restore-focus-btn {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid #4299e1;
  border-radius: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(66, 153, 225, 0.3);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.restore-focus-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.4);
  border-color: #3182ce;
}

.restore-btn-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.restore-agent-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.restore-agent-icon {
  font-size: 18px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
}

.restore-agent-name {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.restore-text {
  font-size: 12px;
  color: #4299e1;
  font-weight: 600;
  background: rgba(66, 153, 225, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

@keyframes minimizedSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .minimized-focus-indicator {
    right: 16px;
  }
  
  .restore-focus-btn {
    min-width: 180px;
    padding: 10px 14px;
  }
}

@media (max-width: 768px) {
  .minimized-focus-indicator {
    top: 80px;
    left: 16px;
    right: 16px;
  }
  
  .restore-focus-btn {
    min-width: auto;
    width: 100%;
  }
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .focus-area {
    width: 320px;
    right: 16px;
  }
}

@media (max-width: 768px) {
  .focus-area {
    position: fixed;
    top: 80px;
    left: 16px;
    right: 16px;
    width: auto;
    max-height: 400px;
  }
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(255, 255, 255, 0.08);
  padding: 24px;
  padding-bottom: 200px; /* 初始值，将被JavaScript动态调整 */
  position: relative;
  z-index: 1;
  min-height: 0;
  scroll-behavior: smooth;
}

.messages-wrapper {
  max-width: 1600px; /* 从1400px增加到1600px */
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: margin-right 0.3s ease;
}

/* 当焦点区域显示时，为主内容区域预留空间 */
.messages-wrapper.with-focus-area {
  margin-right: 420px; /* 焦点区域宽度(380px) + 间距(40px) */
}

/* 欢迎消息样式 */
.welcome-message {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

.welcome-content {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.welcome-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(72, 187, 120, 0.3);
}

.welcome-text {
  flex: 1;
}

.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  color: #718096;
  line-height: 1.5;
}

/* 对话轮次容器样式 */
.conversation-turn {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
  margin-bottom: 24px;
}

/* 轮次标题栏 */
.turn-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(66, 153, 225, 0.1);
  margin-bottom: 20px;
}

.turn-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.turn-label {
  font-size: 14px;
  font-weight: 700;
  color: #2d3748;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
}

.turn-time {
  font-size: 12px;
  color: #718096;
  font-weight: 500;
  background: rgba(113, 128, 150, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.turn-status {
  display: flex;
  align-items: center;
  gap: 16px;
}

.turn-agents-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4a5568;
  font-weight: 500;
}

.agents-icon {
  font-size: 14px;
}

.turn-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #48bb78;
  font-weight: 600;
  background: rgba(72, 187, 120, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.streaming-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #4299e1;
  font-weight: 500;
}

.streaming-text {
  font-weight: 500;
}

/* 用户输入消息样式 */
.turn-user-input {
  margin-bottom: 20px;
}

.user-message-container {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  justify-content: flex-end;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(66, 153, 225, 0.3);
}

.user-message-content {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  border-radius: 16px;
  padding: 16px 20px;
  max-width: 70%;
  box-shadow: 0 4px 20px rgba(66, 153, 225, 0.25);
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-message-text {
  font-size: 14px;
  line-height: 1.5;
  flex: 1;
}

.user-message-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.action-icon {
  font-size: 12px;
}

/* 智能体响应区域 */
.turn-agents-response {
  margin-top: 16px;
}

.agents-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  transition: grid-template-columns 0.3s ease;
}

/* 当焦点区域显示时，保持单列布局 */
.agents-grid.with-focus-area {
  grid-template-columns: 1fr;
}

.agent-response-card {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.agent-response-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* 动态重排序动画效果 */
.agent-response-card.recently-active {
  animation: cardReorder 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #4299e1;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.25);
}

@keyframes cardReorder {
  0% {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 12px 40px rgba(66, 153, 225, 0.3);
  }
  50% {
    transform: translateY(0) scale(1.01);
    box-shadow: 0 8px 32px rgba(66, 153, 225, 0.25);
  }
  100% {
    transform: translateY(0) scale(1);
    box-shadow: 0 8px 32px rgba(66, 153, 225, 0.25);
  }
}

/* 新活跃智能体的高亮效果 */
.agent-response-card.newly-active::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #4299e1, #3182ce, #2563eb, #4299e1);
  background-size: 400% 400%;
  border-radius: 18px;
  z-index: -1;
  animation: gradientShift 2s ease-in-out;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
    opacity: 0.8;
  }
  50% {
    background-position: 100% 50%;
    opacity: 0.6;
  }
}

/* 工具卡片样式 */
.tool-response-card {
  transition: all 0.3s ease;
}

.tool-response-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* 消息样式 */
.message-item {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

/* 独立用户消息样式 */
.user-message-standalone {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 20px;
}

.user-message-standalone .user-message-container {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  justify-content: flex-end;
}

.user-message-standalone .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(66, 153, 225, 0.3);
}

.user-message-standalone .user-message-content {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  border-radius: 16px;
  padding: 16px 20px;
  max-width: 70%;
  box-shadow: 0 4px 20px rgba(66, 153, 225, 0.25);
  position: relative;
}

.user-message-standalone .user-message-text {
  font-size: 14px;
  line-height: 1.5;
}

.user-message-standalone .message-time {
  font-size: 11px;
  color: #a0aec0;
  text-align: right;
  margin-right: 48px; /* 对齐头像位置 */
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
}

.message-avatar::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3));
  z-index: -1;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
}

.assistant-message .message-avatar {
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
}

.loading-avatar {
  animation: pulse 2s ease-in-out infinite;
}

.message-content {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px 24px;
  max-width: 85%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  position: relative;
}

.message-content::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent);
  pointer-events: none;
}

.user-message .message-content {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.3);
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


/* Agent输出卡片样式 */
.agent-outputs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

/* 智能体卡片容器 */
.agent-cards-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 16px;
}

/* 轮次分组样式 */
.turn-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.turn-separator {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 8px;
}

.turn-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.turn-label {
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  background: rgba(66, 153, 225, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.turn-time {
  font-size: 11px;
  color: #718096;
  font-weight: 500;
}

.turn-status {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
}

.turn-status.status-active {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.turn-status.status-completed {
  background: rgba(72, 187, 120, 0.1);
  color: #48bb78;
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.turn-user-message {
  font-size: 12px;
  color: #4a5568;
  font-style: italic;
  background: rgba(0, 0, 0, 0.02);
  padding: 6px 10px;
  border-radius: 6px;
  border-left: 3px solid #4299e1;
}

.turn-agent-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.completed-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #48bb78;
  font-weight: 500;
}

.agent-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.agent-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #e2e8f0, #cbd5e0);
  transition: all 0.3s ease;
}

.agent-card.status-processing {
  border-color: #4299e1;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.25);
  transform: translateY(-2px);
}

.agent-card.status-processing::before {
  background: linear-gradient(90deg, #4299e1, #3182ce);
  animation: shimmer 2s ease-in-out infinite;
}

.agent-card.status-completed {
  border-color: #48bb78;
  box-shadow: 0 8px 32px rgba(72, 187, 120, 0.2);
}

.agent-card.status-completed::before {
  background: linear-gradient(90deg, #48bb78, #38a169);
}

.agent-card.status-waiting {
  border-color: #a0aec0;
  opacity: 0.8;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Agent卡片头部 */
.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.agent-icon {
  font-size: 22px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(66, 153, 225, 0.1);
  transition: all 0.3s ease;
}

.agent-name {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.2;
}

.agent-description {
  font-size: 12px;
  color: #718096;
  margin-left: 8px;
  font-weight: 500;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.05);
}

.status-processing {
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.status-completed {
  color: #48bb78;
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.status-waiting {
  color: #a0aec0;
  background: rgba(160, 174, 192, 0.1);
  border: 1px solid rgba(160, 174, 192, 0.2);
}

/* Agent内容区域 */
.agent-content {
  padding: 16px;
}

.markdown-content {
  line-height: 1.6;
  font-size: 14px;
}

/* 处理中占位符样式 */
.processing-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(66, 153, 225, 0.3);
}

.processing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4299e1;
}

.processing-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(66, 153, 225, 0.3);
  border-top: 2px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.processing-text {
  font-size: 14px;
  font-weight: 500;
}

/* Agent卡片底部 */
.agent-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(247, 250, 252, 0.5);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 11px;
  color: #718096;
}

.timing-info, .content-stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 不同agent的主题色 */
.agent-card.agent-supervisor .agent-icon {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}

.agent-card.agent-tour_search_agent .agent-icon {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.agent-card.agent-day_plan_agent .agent-icon {
  background: rgba(234, 88, 12, 0.1);
  color: #ea580c;
}

.agent-card.agent-live_transport_agent .agent-icon {
  background: rgba(124, 58, 237, 0.1);
  color: #7c3aed;
}

.agent-card.agent-travel_butler_agent .agent-icon {
  background: rgba(219, 39, 119, 0.1);
  color: #db2777;
}

.agent-card.agent-tools .agent-icon {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

/* 调用次数样式 */
.call-index {
  font-size: 11px;
  color: #718096;
  font-weight: normal;
  margin-left: 4px;
  padding: 2px 6px;
  background: rgba(113, 128, 150, 0.1);
  border-radius: 4px;
}

/* 消息内容 */
.message-text {
  line-height: 1.6;
  font-size: 14px;
  margin-bottom: 8px;
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
}

.step-item.step-completed {
  background: rgba(56, 161, 105, 0.1);
  color: #2f855a;
}

.step-item.step-current {
  background: rgba(66, 153, 225, 0.15);
  color: #2d3748;
  border: 1px solid rgba(66, 153, 225, 0.3);
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


/* 输入区域 */
.input-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.12);
  z-index: 100;
}

.input-main-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 12px 16px 24px; /* 左侧保持24px，右侧减少到12px */
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 16px; /* 减少间距，给input-main-area更多空间 */
}

.status-info-bar {
  flex-shrink: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  min-height: 72px; /* 与input-box对齐 */
}

.status-info-bar:hover {
  border-color: #4299e1;
  box-shadow: 0 6px 20px rgba(66, 153, 225, 0.15);
  transform: translateY(-1px);
}

.status-info-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 16px 20px;
  gap: 16px;
}

.status-info-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.session-icon {
  font-size: 20px;
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.session-label {
  font-size: 11px;
  color: #718096;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.session-id {
  font-size: 13px;
  color: #2d3748;
  font-weight: 700;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  background: rgba(66, 153, 225, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  max-width: fit-content;
}

.message-count {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
}

.count-circle {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
  transition: all 0.3s ease;
}

.count-circle:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
}

.count-number {
  color: white;
  font-size: 13px;
  font-weight: 700;
}

.count-label {
  font-size: 10px;
  color: #718096;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

.reset-btn {
  padding: 10px 16px;
  background: linear-gradient(135deg, #f56565, #e53e3e);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 101, 101, 0.3);
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.reset-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(245, 101, 101, 0.4);
  background: linear-gradient(135deg, #e53e3e, #c53030);
}

.reset-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(245, 101, 101, 0.3);
}

.reset-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(245, 101, 101, 0.2);
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
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  min-height: 72px; /* 与status-info-bar对齐 */
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
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.input-icon:hover {
  background: rgba(66, 153, 225, 0.15);
  transform: scale(1.05);
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
@media (max-width: 1400px) {
  /* 当焦点区域显示时，减少主内容区域的右边距 */
  .messages-wrapper.with-focus-area {
    margin-right: 360px; /* 减少到360px */
  }
  
  /* 保持单列布局 */
  .agents-grid.with-focus-area {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  /* 进一步减少边距和调整网格 */
  .messages-wrapper.with-focus-area {
    margin-right: 340px; /* 减少到340px */
  }
  
  /* 保持单列布局 */
  .agents-grid.with-focus-area {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  /* 移动端：取消焦点区域的边距影响，改为垂直布局 */
  .messages-wrapper.with-focus-area {
    margin-right: 0;
  }
  
  /* 保持单列布局 */
  .agents-grid.with-focus-area {
    grid-template-columns: 1fr;
  }
  
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
