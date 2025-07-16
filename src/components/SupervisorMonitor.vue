<template>
  <div class="supervisor-monitor">
    <!-- 监控面板头部 -->
    <div class="monitor-header">
      <div class="header-left">
        <div class="supervisor-icon">🎯</div>
        <div class="header-info">
          <h3 class="monitor-title">智能体对话监控</h3>
          <p class="monitor-subtitle">实时显示对话流程和智能体协作</p>
        </div>
      </div>
      <div class="header-right">
        <div class="status-indicator" :class="currentStatus">
          <div class="status-dot"></div>
          <span class="status-text">{{ getStatusText() }}</span>
        </div>
        <button @click="toggleExpanded" class="expand-btn" :class="{ expanded: isExpanded }">
          {{ isExpanded ? '▼' : '▶' }}
        </button>
      </div>
    </div>

    <!-- 监控面板内容 -->
    <div class="monitor-content" :class="{ collapsed: !isExpanded }">
      <!-- 消息卡片列表 -->
      <div class="message-cards-container" v-if="messageCards.length > 0">
        <MessageCard
          v-for="card in messageCards"
          :key="card.id"
          :messageType="card.messageType"
          :content="card.content"
          :timestamp="card.timestamp"
          :isStreaming="card.isStreaming"
          :streamingProgress="card.streamingProgress"
          :toolCalls="card.toolCalls"
          :canCollapse="card.canCollapse"
          @toggle-collapse="handleCardCollapse(card.id, $event)"
        />
      </div>

      <!-- 空状态提示 -->
      <div v-else class="empty-state">
        <div class="empty-icon">💬</div>
        <div class="empty-text">暂无对话消息</div>
        <div class="empty-subtitle">开始对话后，这里将显示智能体的交互过程</div>
      </div>
      <!-- 当前执行状态 -->
      <div class="execution-status-section">
        <div class="section-header">
          <span class="section-icon">⚡</span>
          <span class="section-title">当前执行状态</span>
        </div>
        <div class="execution-status">
          <div class="current-agent-info" v-if="currentActiveAgent">
            <div class="agent-avatar" :class="`agent-${currentActiveAgent.key}`">
              {{ currentActiveAgent.emoji }}
            </div>
            <div class="agent-details">
              <div class="agent-name">{{ currentActiveAgent.name }}</div>
              <div class="agent-status">{{ currentActiveAgent.status }}</div>
            </div>
            <div class="agent-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: currentActiveAgent.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ currentActiveAgent.progress }}%</span>
            </div>
          </div>
          <div class="no-active-agent" v-else>
            <span class="idle-icon">💤</span>
            <span class="idle-text">系统空闲中</span>
          </div>
        </div>
      </div>

      <!-- 执行计划展示 -->
      <div class="execution-plan-section" v-if="executionPlan">
        <div class="section-header">
          <span class="section-icon">📋</span>
          <span class="section-title">执行计划</span>
          <span class="plan-timestamp">{{ formatTime(executionPlan.timestamp) }}</span>
        </div>
        <div class="execution-plan">
          <div class="plan-overview">
            <div class="plan-summary">{{ executionPlan.summary }}</div>
            <div class="plan-steps-count">共 {{ executionPlan.steps?.length || 0 }} 个步骤</div>
          </div>
          <div class="plan-steps" v-if="executionPlan.steps">
            <div 
              v-for="(step, index) in executionPlan.steps" 
              :key="index"
              class="plan-step"
              :class="{ 
                'step-completed': step.status === 'completed',
                'step-current': step.status === 'current',
                'step-pending': step.status === 'pending'
              }"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <div class="step-agent">{{ getAgentDisplayName(step.agent) }}</div>
                <div class="step-description">{{ step.description }}</div>
              </div>
              <div class="step-status-icon">
                <span v-if="step.status === 'completed'">✅</span>
                <span v-else-if="step.status === 'current'" class="current-spinner">⚡</span>
                <span v-else>⏳</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工具调用历史 -->
      <div class="tool-calls-section" v-if="toolCalls.length > 0">
        <div class="section-header">
          <span class="section-icon">🔧</span>
          <span class="section-title">工具调用历史</span>
          <span class="calls-count">{{ toolCalls.length }} 次调用</span>
        </div>
        <div class="tool-calls-list">
          <div 
            v-for="(call, index) in toolCalls" 
            :key="index"
            class="tool-call-item"
            :class="{ 'call-active': call.status === 'active' }"
          >
            <div class="call-timestamp">{{ formatTime(call.timestamp) }}</div>
            <div class="call-details">
              <div class="call-tool">{{ getToolDisplayName(call.toolName) }}</div>
              <div class="call-target" v-if="call.targetAgent">
                → {{ getAgentDisplayName(call.targetAgent) }}
              </div>
            </div>
            <div class="call-status" :class="`status-${call.status}`">
              <span v-if="call.status === 'completed'">✅</span>
              <span v-else-if="call.status === 'active'" class="active-spinner">⚡</span>
              <span v-else-if="call.status === 'failed'">❌</span>
              <span v-else>⏳</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent 切换时间线 -->
      <div class="agent-timeline-section" v-if="agentTransitions.length > 0">
        <div class="section-header">
          <span class="section-icon">🔄</span>
          <span class="section-title">Agent 切换时间线</span>
        </div>
        <div class="agent-timeline">
          <div 
            v-for="(transition, index) in agentTransitions" 
            :key="index"
            class="timeline-item"
          >
            <div class="timeline-time">{{ formatTime(transition.timestamp) }}</div>
            <div class="timeline-content">
              <div class="transition-from" v-if="transition.from">
                <span class="agent-badge" :class="`agent-${transition.from}`">
                  {{ getAgentDisplayName(transition.from) }}
                </span>
              </div>
              <div class="transition-arrow" v-if="transition.from">→</div>
              <div class="transition-to">
                <span class="agent-badge" :class="`agent-${transition.to}`">
                  {{ getAgentDisplayName(transition.to) }}
                </span>
              </div>
            </div>
            <div class="transition-reason">{{ transition.reason }}</div>
          </div>
        </div>
      </div>

      <!-- Supervisor 消息历史 -->
      <div class="supervisor-messages-section" v-if="supervisorMessages.length > 0">
        <div class="section-header">
          <span class="section-icon">💬</span>
          <span class="section-title">Supervisor 消息历史</span>
          <button @click="toggleMessagesExpanded" class="toggle-messages-btn">
            {{ isMessagesExpanded ? '收起' : '展开' }}
          </button>
        </div>
        <div class="supervisor-messages" :class="{ collapsed: !isMessagesExpanded }">
          <div 
            v-for="(message, index) in supervisorMessages" 
            :key="index"
            class="supervisor-message"
            :class="`message-${message.type}`"
          >
            <div class="message-header">
              <div class="message-type-icon">{{ getMessageTypeIcon(message.type) }}</div>
              <div class="message-info">
                <span class="message-type">{{ getMessageTypeLabel(message.type) }}</span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
            </div>
            <div class="message-content" v-if="message.content">
              <div class="content-preview" v-if="!message.expanded">
                {{ getContentPreview(message.content) }}
                <button @click="toggleMessageExpanded(index)" class="expand-content-btn" v-if="message.content.length > 100">
                  展开
                </button>
              </div>
              <div class="content-full" v-else>
                <div v-html="formatMessageContent(message.content)"></div>
                <button @click="toggleMessageExpanded(index)" class="collapse-content-btn">
                  收起
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import MessageCard from './MessageCard.vue'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'SupervisorMonitor',
  components: {
    MessageCard
  },
  props: {
    supervisorData: {
      type: Object,
      default: () => ({})
    },
    isActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:expanded'],
  setup(props, { emit }) {
    // 响应式状态
    const isExpanded = ref(true)
    const isMessagesExpanded = ref(false)
    const currentActiveAgent = ref(null)
    const executionPlan = ref(null)
    const toolCalls = ref([])
    const agentTransitions = ref([])
    const supervisorMessages = ref([])
    const messageCards = ref([])
    const cardIdCounter = ref(0)

    // 计算当前状态
    const currentStatus = computed(() => {
      if (!props.isActive) return 'idle'
      if (currentActiveAgent.value) return 'active'
      return 'waiting'
    })

    // 更新监控数据
    const updateMonitorData = (data) => {
      if (data.messages) {
        processSupervisorMessages(data.messages)
      }
      
      if (data.executionPlan) {
        executionPlan.value = {
          ...data.executionPlan,
          timestamp: new Date()
        }
      }
      
      if (data.currentAgent) {
        updateCurrentAgent(data.currentAgent)
      }
    }

    // 监听 supervisorData 变化
    watch(() => props.supervisorData, (newData) => {
      if (newData) {
        updateMonitorData(newData)
      }
    }, { deep: true, immediate: true })

    // 处理 supervisor 消息
    const processSupervisorMessages = (messages) => {
      const newMessages = []
      
      messages.forEach((message, index) => {
        const messageType = getMessageType(message)
        const processedMessage = {
          id: `msg-${index}`,
          type: messageType,
          content: message.content,
          timestamp: new Date(),
          expanded: false,
          raw: message
        }
        
        newMessages.push(processedMessage)
        
        // 处理工具调用
        if (message.tool_calls) {
          message.tool_calls.forEach(toolCall => {
            addToolCall(toolCall)
          })
        }
        
        // 检测 agent 切换
        if (messageType === 'tool_call' && message.tool_calls) {
          message.tool_calls.forEach(toolCall => {
            if (toolCall.name.startsWith('transfer_to_')) {
              const targetAgent = toolCall.name.replace('transfer_to_', '').replace('_agent', '')
              addAgentTransition(null, targetAgent, '工具调用切换')
            }
          })
        }
      })
      
      supervisorMessages.value = newMessages
    }

    // 获取消息类型
    const getMessageType = (message) => {
      if (message.content?.startsWith('Successfully transferred')) {
        return 'tool_result'
      }
      if (message.tool_calls?.length > 0) {
        return 'tool_call'
      }
      if (message.name === 'supervisor') {
        return 'supervisor_response'
      }
      return 'user_message'
    }

    // 提取目标 agent
    const extractTargetAgent = (toolName) => {
      if (toolName.startsWith('transfer_to_')) {
        return toolName.replace('transfer_to_', '').replace('_agent', '')
      }
      return null
    }

    // 更新当前活跃 agent
    const updateCurrentAgent = (agentKey) => {
      if (agentKey) {
        currentActiveAgent.value = {
          key: agentKey,
          name: getAgentDisplayName(agentKey),
          emoji: getAgentEmoji(agentKey),
          status: '工作中',
          progress: 75 // 可以根据实际情况动态计算
        }
      } else {
        currentActiveAgent.value = null
      }
    }

    // 添加工具调用记录
    const addToolCall = (toolCall) => {
      const existingCall = toolCalls.value.find(call => call.id === toolCall.id)
      if (!existingCall) {
        toolCalls.value.push({
          id: toolCall.id,
          toolName: toolCall.name,
          targetAgent: extractTargetAgent(toolCall.name),
          timestamp: new Date(),
          status: 'active'
        })
      }
    }

    // 添加 agent 切换记录
    const addAgentTransition = (from, to, reason) => {
      agentTransitions.value.push({
        from,
        to,
        reason,
        timestamp: new Date()
      })
      
      // 更新当前活跃 agent
      updateCurrentAgent(to)
    }

    // 工具方法
    const toggleExpanded = () => {
      isExpanded.value = !isExpanded.value
      emit('update:expanded', isExpanded.value)
    }

    const toggleMessagesExpanded = () => {
      isMessagesExpanded.value = !isMessagesExpanded.value
    }

    const toggleMessageExpanded = (index) => {
      supervisorMessages.value[index].expanded = !supervisorMessages.value[index].expanded
    }

    const getStatusText = () => {
      switch (currentStatus.value) {
        case 'active': return '工作中'
        case 'waiting': return '等待中'
        case 'idle': return '空闲'
        default: return '未知'
      }
    }

    const getAgentDisplayName = (agentKey) => {
      const agentMap = {
        'supervisor': '总控智能体',
        'tour_search_agent': '景点搜索专家',
        'day_plan_agent': '行程规划师',
        'live_transport_agent': '交通住宿顾问',
        'travel_butler_agent': '旅行管家'
      }
      return agentMap[agentKey] || agentKey
    }

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

    const getMessageTypeIcon = (type) => {
      const iconMap = {
        'user_message': '👤',
        'supervisor_response': '🎯',
        'tool_call': '🔧',
        'tool_result': '✅'
      }
      return iconMap[type] || '💬'
    }

    const getMessageTypeLabel = (type) => {
      const labelMap = {
        'user_message': '用户消息',
        'supervisor_response': 'Supervisor 回复',
        'tool_call': '工具调用',
        'tool_result': '工具结果'
      }
      return labelMap[type] || '未知类型'
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const formatMessageContent = (content) => {
      if (!content) return ''
      return md.render(content)
    }

    const getContentPreview = (content) => {
      if (!content) return ''
      return content.length > 100 ? content.substring(0, 100) + '...' : content
    }

    // 消息卡片管理方法
    const addMessageCard = (messageType, content, options = {}) => {
      const cardId = ++cardIdCounter.value
      const newCard = {
        id: cardId,
        messageType,
        content,
        timestamp: new Date(),
        isStreaming: options.isStreaming || false,
        streamingProgress: options.streamingProgress || 0,
        toolCalls: options.toolCalls || [],
        canCollapse: options.canCollapse !== false
      }
      
      messageCards.value.push(newCard)
      return cardId
    }

    const updateMessageCard = (cardId, updates) => {
      const card = messageCards.value.find(c => c.id === cardId)
      if (card) {
        Object.assign(card, updates)
      }
    }

    const handleCardCollapse = (cardId, isCollapsed) => {
      updateMessageCard(cardId, { isCollapsed })
    }

    const clearMessageCards = () => {
      messageCards.value = []
      cardIdCounter.value = 0
    }

    // 添加用户消息卡片
    const addUserMessage = (content) => {
      return addMessageCard('user', content, { canCollapse: false })
    }

    // 添加supervisor消息卡片
    const addSupervisorMessage = (content, toolCalls = []) => {
      return addMessageCard('supervisor', content, { toolCalls })
    }

    // 添加智能体消息卡片
    const addAgentMessage = (agentType, content, isStreaming = false) => {
      return addMessageCard(agentType, content, { isStreaming })
    }

    // 暴露给外部的方法
    const addMessage = (messageType, content, options = {}) => {
      return addMessageCard(messageType, content, options)
    }

    const updateMessage = (cardId, updates) => {
      updateMessageCard(cardId, updates)
    }

    return {
      // 响应式数据
      isExpanded,
      isMessagesExpanded,
      currentActiveAgent,
      executionPlan,
      toolCalls,
      agentTransitions,
      supervisorMessages,
      messageCards,
      currentStatus,
      
      // 方法
      toggleExpanded,
      toggleMessagesExpanded,
      toggleMessageExpanded,
      getStatusText,
      getAgentDisplayName,
      getAgentEmoji,
      getToolDisplayName,
      getMessageTypeIcon,
      getMessageTypeLabel,
      formatTime,
      formatMessageContent,
      getContentPreview,
      
      // 消息卡片方法
      addMessage,
      updateMessage,
      handleCardCollapse,
      clearMessageCards,
      addUserMessage,
      addSupervisorMessage,
      addAgentMessage
    }
  }
}
</script>

<style scoped>
.supervisor-monitor {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.supervisor-icon {
  font-size: 24px;
  animation: pulse 2s ease-in-out infinite;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.monitor-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.monitor-subtitle {
  font-size: 12px;
  opacity: 0.9;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-indicator.active .status-dot {
  background: #48bb78;
}

.status-indicator.waiting .status-dot {
  background: #ed8936;
}

.status-indicator.idle .status-dot {
  background: #a0aec0;
}

.expand-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.monitor-content {
  max-height: 600px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.monitor-content.collapsed {
  max-height: 0;
  overflow: hidden;
}

/* 消息卡片容器样式 */
.message-cards-container {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: #a0aec0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #718096;
}

.empty-subtitle {
  font-size: 14px;
  color: #a0aec0;
  line-height: 1.5;
}

.execution-status-section,
.execution-plan-section,
.tool-calls-section,
.agent-timeline-section,
.supervisor-messages-section {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #2d3748;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 14px;
}

.plan-timestamp,
.calls-count {
  margin-left: auto;
  font-size: 12px;
  color: #718096;
}

.current-agent-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.agent-details {
  flex: 1;
}

.agent-name {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.agent-status {
  font-size: 12px;
  color: #718096;
}

.agent-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 80px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(45deg, #48bb78, #38a169);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: #718096;
  font-weight: 500;
}

.no-active-agent {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #a0aec0;
  font-size: 14px;
}

.idle-icon {
  font-size: 20px;
}

.plan-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
}

.plan-summary {
  font-weight: 500;
  color: #2d3748;
}

.plan-steps-count {
  font-size: 12px;
  color: #718096;
}

.plan-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plan-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.plan-step.step-completed {
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.plan-step.step-current {
  background: rgba(66, 153, 225, 0.1);
  border: 1px solid rgba(66, 153, 225, 0.3);
  transform: translateX(4px);
}

.plan-step.step-pending {
  background: rgba(160, 174, 192, 0.05);
  border: 1px solid rgba(160, 174, 192, 0.1);
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #4a5568;
}

.step-current .step-number {
  background: #4299e1;
  color: white;
}

.step-completed .step-number {
  background: #48bb78;
  color: white;
}

.step-content {
  flex: 1;
}

.step-agent {
  font-weight: 500;
  color: #2d3748;
  font-size: 13px;
}

.step-description {
  font-size: 12px;
  color: #718096;
  margin-top: 2px;
}

.step-status-icon {
  font-size: 16px;
}

.current-spinner {
  animation: pulse 1s ease-in-out infinite;
  color: #4299e1;
}

.tool-calls-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-call-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(237, 137, 54, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(237, 137, 54, 0.1);
  transition: all 0.2s ease;
}

.tool-call-item.call-active {
  background: rgba(66, 153, 225, 0.1);
  border-color: rgba(66, 153, 225, 0.3);
}

.call-timestamp {
  font-size: 11px;
  color: #a0aec0;
  min-width: 60px;
}

.call-details {
  flex: 1;
}

.call-tool {
  font-weight: 500;
  color: #2d3748;
  font-size: 13px;
}

.call-target {
  font-size: 12px;
  color: #718096;
  margin-top: 2px;
}

.call-status {
  font-size: 14px;
}

.active-spinner {
  animation: pulse 1s ease-in-out infinite;
  color: #4299e1;
}

.agent-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(159, 122, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(159, 122, 234, 0.1);
}

.timeline-time {
  font-size: 11px;
  color: #a0aec0;
  min-width: 60px;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.agent-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background: #e2e8f0;
  color: #4a5568;
}

.agent-badge.agent-supervisor {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.agent-badge.agent-tour_search {
  background: rgba(66, 153, 225, 0.2);
  color: #4299e1;
}

.agent-badge.agent-day_plan {
  background: rgba(72, 187, 120, 0.2);
  color: #48bb78;
}

.agent-badge.agent-live_transport {
  background: rgba(237, 137, 54, 0.2);
  color: #ed8936;
}

.agent-badge.agent-travel_butler {
  background: rgba(159, 122, 234, 0.2);
  color: #9f7aea;
}

.transition-arrow {
  color: #718096;
  font-weight: bold;
}

.transition-reason {
  font-size: 12px;
  color: #718096;
  font-style: italic;
}

.supervisor-messages {
  max-height: 300px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.supervisor-messages.collapsed {
  max-height: 0;
  overflow: hidden;
}

.toggle-messages-btn {
  background: rgba(66, 153, 225, 0.1);
  border: 1px solid rgba(66, 153, 225, 0.2);
  color: #4299e1;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-messages-btn:hover {
  background: rgba(66, 153, 225, 0.2);
}

.supervisor-message {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.supervisor-message.message-user_message {
  background: rgba(66, 153, 225, 0.05);
  border-color: rgba(66, 153, 225, 0.2);
}

.supervisor-message.message-supervisor_response {
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.2);
}

.supervisor-message.message-tool_call {
  background: rgba(237, 137, 54, 0.05);
  border-color: rgba(237, 137, 54, 0.2);
}

.supervisor-message.message-tool_result {
  background: rgba(72, 187, 120, 0.05);
  border-color: rgba(72, 187, 120, 0.2);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.message-type-icon {
  font-size: 14px;
}

.message-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-type {
  font-weight: 500;
  font-size: 12px;
  color: #2d3748;
}

.message-time {
  font-size: 11px;
  color: #a0aec0;
}

.message-content {
  margin-top: 8px;
}

.content-preview {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
}

.content-full {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
}

.expand-content-btn,
.collapse-content-btn {
  background: rgba(66, 153, 225, 0.1);
  border: 1px solid rgba(66, 153, 225, 0.2);
  color: #4299e1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  cursor: pointer;
  margin-left: 8px;
  transition: all 0.2s ease;
}

.expand-content-btn:hover,
.collapse-content-btn:hover {
  background: rgba(66, 153, 225, 0.2);
}

/* 滚动条样式 */
.monitor-content::-webkit-scrollbar,
.supervisor-messages::-webkit-scrollbar {
  width: 4px;
}

.monitor-content::-webkit-scrollbar-track,
.supervisor-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.monitor-content::-webkit-scrollbar-thumb,
.supervisor-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 2px;
}

.monitor-content::-webkit-scrollbar-thumb:hover,
.supervisor-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 动画效果 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .monitor-header {
    padding: 12px 16px;
  }
  
  .header-left {
    gap: 8px;
  }
  
  .supervisor-icon {
    font-size: 20px;
  }
  
  .monitor-title {
    font-size: 14px;
  }
  
  .monitor-subtitle {
    font-size: 11px;
  }
  
  .header-right {
    gap: 12px;
  }
  
  .execution-status-section,
  .execution-plan-section,
  .tool-calls-section,
  .agent-timeline-section,
  .supervisor-messages-section {
    padding: 12px 16px;
  }
  
  .current-agent-info {
    gap: 12px;
    padding: 10px;
  }
  
  .agent-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .agent-name {
    font-size: 13px;
  }
  
  .agent-status {
    font-size: 11px;
  }
  
  .progress-bar {
    width: 60px;
  }
  
  .plan-step {
    padding: 10px;
    gap: 10px;
  }
  
  .step-number {
    width: 20px;
    height: 20px;
    font-size: 11px;
  }
  
  .tool-call-item {
    padding: 8px 10px;
    gap: 10px;
  }
  
  .timeline-item {
    padding: 10px;
    gap: 12px;
  }
  
  .supervisor-message {
    padding: 10px;
  }
}
</style>
