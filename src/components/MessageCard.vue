<template>
  <div class="message-card-wrapper" :class="messageType">
    <div class="message-card" :class="[messageType, { 'is-streaming': isStreaming, 'is-collapsed': isCollapsed }]">
      <!-- 卡片头部 -->
      <div class="card-header" @click="toggleCollapse" :class="{ 'clickable': canCollapse }">
        <div class="header-left">
          <div class="avatar" :class="messageType">
            <span class="avatar-icon">{{ getAvatarIcon() }}</span>
          </div>
          <div class="header-info">
            <div class="message-title">{{ getMessageTitle() }}</div>
            <div class="message-subtitle" v-if="getMessageSubtitle()">{{ getMessageSubtitle() }}</div>
          </div>
          <div class="status-indicator" v-if="isStreaming">
            <div class="streaming-dot"></div>
            <span class="status-text">实时生成中</span>
          </div>
        </div>
        <div class="header-right">
          <div class="timestamp">{{ formatTime(timestamp) }}</div>
          <div class="collapse-btn" v-if="canCollapse" :class="{ 'collapsed': isCollapsed }">
            {{ isCollapsed ? '▶' : '▼' }}
          </div>
        </div>
      </div>

      <!-- 卡片内容 -->
      <div class="card-content" :class="{ 'collapsed': isCollapsed }">
        <!-- 用户输入内容 -->
        <div v-if="messageType === 'user'" class="user-content">
          <div class="content-text">{{ content }}</div>
        </div>

        <!-- Supervisor内容 -->
        <div v-else-if="messageType === 'supervisor'" class="supervisor-content">
          <div class="content-text" v-html="formatContent(content)"></div>
          
          <!-- 工具调用信息 -->
          <div v-if="toolCalls && toolCalls.length > 0" class="tool-calls-section">
            <div class="tool-calls-header">
              <span class="tool-icon">🔧</span>
              <span class="tool-title">智能体调用</span>
            </div>
            <div class="tool-calls-list">
              <div v-for="(call, index) in toolCalls" :key="index" class="tool-call-item">
                <div class="tool-name">{{ getToolDisplayName(call.name) }}</div>
                <div class="tool-target" v-if="call.targetAgent">→ {{ call.targetAgent }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 智能体内容 -->
        <div v-else class="agent-content">
          <div class="content-text" v-html="formatContent(content)"></div>
          
          <!-- 内容完成信息 -->
          <div v-if="!isStreaming && content" class="completion-info">
            <span class="completion-text">✨ 内容生成完成</span>
            <span class="content-length">{{ getContentLength() }}字</span>
          </div>
        </div>

        <!-- 流式更新进度 -->
        <div v-if="isStreaming" class="streaming-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: streamingProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ streamingProgress }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'MessageCard',
  props: {
    messageType: {
      type: String,
      required: true,
      validator: (value) => ['user', 'supervisor', 'tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent'].includes(value)
    },
    content: {
      type: String,
      default: ''
    },
    timestamp: {
      type: Date,
      default: () => new Date()
    },
    isStreaming: {
      type: Boolean,
      default: false
    },
    streamingProgress: {
      type: Number,
      default: 0
    },
    toolCalls: {
      type: Array,
      default: () => []
    },
    canCollapse: {
      type: Boolean,
      default: true
    }
  },
  emits: ['toggle-collapse'],
  setup(props, { emit }) {
    const isCollapsed = ref(false)

    const toggleCollapse = () => {
      if (props.canCollapse) {
        isCollapsed.value = !isCollapsed.value
        emit('toggle-collapse', isCollapsed.value)
      }
    }

    const getAvatarIcon = () => {
      const iconMap = {
        'user': '👤',
        'supervisor': '🎯',
        'tour_search_agent': '🔍',
        'day_plan_agent': '📅',
        'live_transport_agent': '🚗',
        'travel_butler_agent': '🎒'
      }
      return iconMap[props.messageType] || '🤖'
    }

    const getMessageTitle = () => {
      const titleMap = {
        'user': '用户输入',
        'supervisor': '总控智能体',
        'tour_search_agent': '景点搜索专家',
        'day_plan_agent': '行程规划师',
        'live_transport_agent': '交通住宿顾问',
        'travel_butler_agent': '旅行管家'
      }
      return titleMap[props.messageType] || '未知智能体'
    }

    const getMessageSubtitle = () => {
      const subtitleMap = {
        'user': '您的旅游需求',
        'supervisor': '协调和决策',
        'tour_search_agent': '景点信息查询',
        'day_plan_agent': '行程安排规划',
        'live_transport_agent': '交通住宿建议',
        'travel_butler_agent': '旅行服务管理'
      }
      return subtitleMap[props.messageType] || ''
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

    const getContentLength = () => {
      if (!props.content) return 0
      const textContent = props.content.replace(/<[^>]*>/g, '')
      return textContent.length
    }

    return {
      isCollapsed,
      toggleCollapse,
      getAvatarIcon,
      getMessageTitle,
      getMessageSubtitle,
      getToolDisplayName,
      formatTime,
      formatContent,
      getContentLength
    }
  }
}
</script>

<style scoped>
.message-card-wrapper {
  margin-bottom: 16px;
}

.message-card-wrapper.user {
  display: flex;
  justify-content: flex-end;
}

.message-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  overflow: hidden;
  transition: all 0.3s ease;
  max-width: 85%;
  min-width: 300px;
}

/* 用户消息卡片样式 */
.message-card.user {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
  color: white;
  border-color: rgba(66, 153, 225, 0.3);
  max-width: 70%;
}

.message-card.user .card-header {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.message-card.user .avatar {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.message-card.user .timestamp {
  color: rgba(255, 255, 255, 0.8);
}

/* Supervisor消息卡片样式 */
.message-card.supervisor {
  border-color: rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.message-card.supervisor .card-header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
}

.message-card.supervisor .avatar {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

/* 智能体消息卡片样式 */
.message-card.tour_search_agent {
  border-color: rgba(66, 153, 225, 0.3);
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.05) 0%, rgba(49, 130, 206, 0.05) 100%);
}

.message-card.tour_search_agent .card-header {
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(49, 130, 206, 0.1) 100%);
  border-bottom: 1px solid rgba(66, 153, 225, 0.2);
}

.message-card.tour_search_agent .avatar {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.message-card.day_plan_agent {
  border-color: rgba(72, 187, 120, 0.3);
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.05) 0%, rgba(56, 161, 105, 0.05) 100%);
}

.message-card.day_plan_agent .card-header {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(56, 161, 105, 0.1) 100%);
  border-bottom: 1px solid rgba(72, 187, 120, 0.2);
}

.message-card.day_plan_agent .avatar {
  background: linear-gradient(45deg, #48bb78, #38a169);
  color: white;
}

.message-card.live_transport_agent {
  border-color: rgba(237, 137, 54, 0.3);
  background: linear-gradient(135deg, rgba(237, 137, 54, 0.05) 0%, rgba(221, 107, 32, 0.05) 100%);
}

.message-card.live_transport_agent .card-header {
  background: linear-gradient(135deg, rgba(237, 137, 54, 0.1) 0%, rgba(221, 107, 32, 0.1) 100%);
  border-bottom: 1px solid rgba(237, 137, 54, 0.2);
}

.message-card.live_transport_agent .avatar {
  background: linear-gradient(45deg, #ed8936, #dd6b20);
  color: white;
}

.message-card.travel_butler_agent {
  border-color: rgba(159, 122, 234, 0.3);
  background: linear-gradient(135deg, rgba(159, 122, 234, 0.05) 0%, rgba(128, 90, 213, 0.05) 100%);
}

.message-card.travel_butler_agent .card-header {
  background: linear-gradient(135deg, rgba(159, 122, 234, 0.1) 0%, rgba(128, 90, 213, 0.1) 100%);
  border-bottom: 1px solid rgba(159, 122, 234, 0.2);
}

.message-card.travel_butler_agent .avatar {
  background: linear-gradient(45deg, #9f7aea, #805ad5);
  color: white;
}

/* 流式更新状态 */
.message-card.is-streaming {
  border-color: #4299e1;
  box-shadow: 0 0 20px rgba(66, 153, 225, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

/* 折叠状态 */
.message-card.is-collapsed .card-content {
  max-height: 0;
  overflow: hidden;
  padding: 0 20px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  transition: background-color 0.2s ease;
}

.card-header.clickable {
  cursor: pointer;
}

.card-header.clickable:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.avatar-icon {
  transition: transform 0.3s ease;
}

.header-info {
  flex: 1;
}

.message-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 2px;
}

.message-card.user .message-title {
  color: white;
}

.message-subtitle {
  font-size: 11px;
  color: #718096;
  font-weight: 400;
}

.message-card.user .message-subtitle {
  color: rgba(255, 255, 255, 0.8);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(66, 153, 225, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.streaming-dot {
  width: 8px;
  height: 8px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-text {
  font-size: 11px;
  color: #4299e1;
  font-weight: 500;
}

.timestamp {
  font-size: 11px;
  color: #a0aec0;
  font-weight: 500;
}

.collapse-btn {
  font-size: 12px;
  color: #718096;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #4a5568;
}

.collapse-btn.collapsed {
  transform: rotate(-90deg);
}

/* 卡片内容 */
.card-content {
  padding: 20px;
  transition: all 0.3s ease;
  max-height: none;
  overflow: visible;
}

.card-content.collapsed {
  max-height: 0;
  overflow: hidden;
  padding: 0 20px;
}

.content-text {
  line-height: 1.6;
  font-size: 14px;
  color: #4a5568;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-card.user .content-text {
  color: white;
  font-weight: 500;
}

/* 工具调用样式 */
.tool-calls-section {
  margin-top: 16px;
  padding: 12px;
  background: rgba(237, 137, 54, 0.05);
  border-radius: 8px;
  border-left: 3px solid #ed8936;
}

.tool-calls-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #c05621;
  font-size: 13px;
}

.tool-icon {
  font-size: 14px;
}

.tool-calls-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tool-call-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  font-size: 12px;
}

.tool-name {
  font-weight: 500;
  color: #2d3748;
}

.tool-target {
  color: #718096;
  font-style: italic;
}

/* 完成信息样式 */
.completion-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(72, 187, 120, 0.1);
  border-radius: 8px;
  border-left: 3px solid #48bb78;
}

.completion-text {
  font-size: 12px;
  color: #2f855a;
  font-weight: 500;
}

.content-length {
  font-size: 11px;
  color: #718096;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 流式进度样式 */
.streaming-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding: 8px 0;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  transition: width 0.3s ease;
  border-radius: 2px;
}

.progress-text {
  font-size: 11px;
  color: #718096;
  font-weight: 500;
  min-width: 35px;
}

/* Markdown 样式增强 */
.content-text h1,
.content-text h2,
.content-text h3,
.content-text h4,
.content-text h5,
.content-text h6 {
  color: #2d3748;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.content-text h1 {
  font-size: 18px;
  border-bottom: 2px solid #4299e1;
  padding-bottom: 4px;
}

.content-text h2 {
  font-size: 16px;
  color: #4a5568;
}

.content-text h3 {
  font-size: 15px;
  color: #718096;
}

.content-text h4 {
  font-size: 14px;
  color: #718096;
}

.content-text p {
  margin: 8px 0;
  line-height: 1.6;
}

.content-text ul,
.content-text ol {
  margin: 8px 0;
  padding-left: 20px;
}

.content-text li {
  margin: 4px 0;
  line-height: 1.5;
}

.content-text strong {
  color: #2d3748;
  font-weight: 600;
}

.content-text em {
  color: #4a5568;
  font-style: italic;
}

.content-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.content-text pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border-left: 3px solid #4299e1;
}

.content-text pre code {
  background: none;
  padding: 0;
}

.content-text blockquote {
  border-left: 4px solid #e2e8f0;
  padding-left: 16px;
  margin: 12px 0;
  color: #718096;
  font-style: italic;
}

.content-text table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.content-text th,
.content-text td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.content-text th {
  background: rgba(66, 153, 225, 0.1);
  font-weight: 600;
}

.content-text a {
  color: #4299e1;
  text-decoration: none;
}

.content-text a:hover {
  text-decoration: underline;
}

.content-text hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}

/* 用户消息的 Markdown 样式覆盖 */
.message-card.user .content-text h1,
.message-card.user .content-text h2,
.message-card.user .content-text h3,
.message-card.user .content-text h4,
.message-card.user .content-text h5,
.message-card.user .content-text h6 {
  color: white;
}

.message-card.user .content-text strong {
  color: white;
}

.message-card.user .content-text a {
  color: rgba(255, 255, 255, 0.9);
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
  .message-card {
    max-width: 95%;
    min-width: 250px;
  }
  
  .message-card.user {
    max-width: 85%;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .message-title {
    font-size: 13px;
  }
  
  .message-subtitle {
    font-size: 10px;
  }
  
  .content-text {
    font-size: 13px;
  }
}
</style>
