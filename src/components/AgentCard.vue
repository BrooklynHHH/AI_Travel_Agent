<template>
  <div class="agent-card" :class="[
    `agent-${agentInfo.key}`,
    `status-${currentStatus}`,
    { 'card-collapsed': isCollapsed },
    { 'in-focus': isInFocus }
  ]">
    <!-- 卡片头部 -->
     <!-- lizylizy12 -->
    <div class="agent-card-header" @click="toggleCard">
      <div class="agent-info">
        <div class="agent-avatar">
          <span class="agent-icon">{{ agentInfo.icon }}</span>
          <div v-if="currentStatus === 'streaming'" class="streaming-pulse"></div>
        </div>
        <div class="agent-details">
          <div class="agent-name">{{ agentInfo.name }}</div>
          <div class="agent-description">{{ agentInfo.description }}</div>
        </div>
      </div>
      
      <div class="card-controls">
        <!-- 对话信息 -->
        <div v-if="conversations.length > 0" class="conversation-info-header">
          <span class="conversation-time">{{ formatTime(conversations[0].timestamp) }}</span>
        </div>
        
        <div class="status-indicator" :class="`status-${currentStatus}`">
          <span v-if="currentStatus === 'streaming'" class="status-text">
            <div class="pulse-dot"></div>
            输出中
          </span>
          <span v-else-if="currentStatus === 'completed'" class="status-text">
            ✅ 完成
          </span>
          <span v-else class="status-text">
            ⏳ 等待
          </span>
        </div>
        
        <div class="card-actions">
          <button 
            v-if="!isInFocus && agentInfo.key !== 'tools' && agentInfo.key !== 'unified_stream'" 
            @click.stop="$emit('focus-agent', agentInfo.key)" 
            class="focus-btn" 
            title="展开到焦点区"
          >
            <span class="focus-icon">🎯</span>
          </button>
          <button @click.stop="toggleCard" class="collapse-btn" :title="isCollapsed ? '展开' : '折叠'">
            <span class="collapse-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 卡片内容区域 -->
    <div v-if="!isCollapsed" class="agent-card-content">
      <!-- 对话轮次列表 -->
      <div class="conversations-list">
        <div 
          v-for="conversation in conversations" 
          :key="conversation.id"
          class="conversation-item"
          :class="{ 'conversation-collapsed': conversation.isCollapsed }"
        >

          <!-- 对话内容 -->
          <div v-if="!conversation.isCollapsed" class="conversation-content">
            <div 
              v-if="conversation.content" 
              class="markdown-content" 
              v-html="formatContent(conversation.content)"
            ></div>
            <div v-else-if="conversation.status === 'streaming'" class="streaming-placeholder">
              <div class="streaming-indicator-detailed">
                <div class="streaming-spinner"></div>
                <span class="streaming-text">正在生成内容...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 当前流式输出区域 -->
      <div v-if="currentStatus === 'streaming'" class="current-streaming">
        <div class="streaming-header">
          <span class="streaming-label">实时输出</span>
          <div class="streaming-progress">
            <div class="progress-bar"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 卡片底部统计 -->
    <div v-if="!isCollapsed" class="agent-card-footer">
      <div class="stats-info">
        <span class="stat-item">
          ⏱️ {{ formatDuration(totalDuration) }}
        </span>
        <span class="stat-item">
          📊 {{ totalCharacters }} 字符
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'AgentCard',
  props: {
    agentInfo: {
      type: Object,
      required: true
    },
    conversations: {
      type: Array,
      default: () => []
    },
    currentStatus: {
      type: String,
      default: 'waiting'
    },
    streamingContent: {
      type: String,
      default: ''
    },
    isInFocus: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-card', 'toggle-conversation'],
  setup(props, { emit }) {
    const isCollapsed = ref(false)

    const totalDuration = computed(() => {
      return props.conversations.reduce((total, conv) => {
        if (conv.endTime && conv.startTime) {
          return total + (conv.endTime - conv.startTime)
        }
        return total
      }, 0)
    })

    const totalCharacters = computed(() => {
      return props.conversations.reduce((total, conv) => {
        return total + (conv.content?.length || 0)
      }, 0) + (props.streamingContent?.length || 0)
    })

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const formatDuration = (duration) => {
      if (duration < 1000) return `${duration}ms`
      return `${(duration / 1000).toFixed(1)}s`
    }

    const formatContent = (content) => {
      if (!content) return ''
      
      // 将内容按照不同的更新批次进行分割和处理
      const contentSegments = splitContentIntoSegments(content)
      
      // 为每个段落添加视觉区分
      const processedSegments = contentSegments.map((segment, index) => {
        let processedContent = segment.content
        
        // 处理工具调用的JSON输出
        processedContent = processJsonContent(processedContent)
        
        // 渲染markdown
        const renderedContent = md.render(processedContent)
        
        // 为每个段落添加容器和样式类
        const segmentClass = index % 2 === 0 ? 'content-segment-primary' : 'content-segment-secondary'
        const updateIndex = index + 1
        
        // <div class="segment-header">
        //       <span class="segment-label">更新 #${updateIndex}</span>
        //       <span class="segment-time">${formatSegmentTime(segment.timestamp)}</span>
        //     </div>
        return `
          <div class="content-segment ${segmentClass}" data-update="${updateIndex}">
            <div class="segment-content">
              ${renderedContent}
            </div>
          </div>
        `
      })
      
      return processedSegments.join('')
    }

    const splitContentIntoSegments = (content) => {
      // 根据内容特征分割成不同的更新段落
      // 这里可以根据实际的内容更新模式进行调整
      
      // 方法1: 按照JSON块分割
      const jsonBlocks = content.match(/\{[^{}]*['"]type['"]:\s*['"][^'"]*['"][^{}]*\}/g) || []
      const textBlocks = content.split(/\{[^{}]*['"]type['"]:\s*['"][^'"]*['"][^{}]*\}/)
      
      const segments = []
      let currentTimestamp = Date.now()
      
      for (let i = 0; i < Math.max(jsonBlocks.length, textBlocks.length); i++) {
        let segmentContent = ''
        
        if (textBlocks[i]) {
          segmentContent += textBlocks[i].trim()
        }
        
        if (jsonBlocks[i]) {
          if (segmentContent) segmentContent += '\n\n'
          segmentContent += jsonBlocks[i]
        }
        
        if (segmentContent.trim()) {
          segments.push({
            content: segmentContent.trim(),
            timestamp: currentTimestamp - (segments.length * 1000) // 模拟时间差
          })
        }
      }
      
      // 如果没有找到明显的分割点，按照长度分割
      if (segments.length <= 1 && content.length > 500) {
        const midPoint = Math.floor(content.length / 2)
        const splitPoint = content.indexOf('\n', midPoint) !== -1 ? 
          content.indexOf('\n', midPoint) : midPoint
        
        return [
          {
            content: content.substring(0, splitPoint).trim(),
            timestamp: currentTimestamp - 2000
          },
          {
            content: content.substring(splitPoint).trim(),
            timestamp: currentTimestamp
          }
        ]
      }
      
      return segments.length > 0 ? segments : [{
        content: content,
        timestamp: currentTimestamp
      }]
    }

    const processJsonContent = (content) => {
      try {
        let data
        
        // 尝试直接解析 JSON
        try {
          data = JSON.parse(content)
        } catch (e) {
          // 如果直接解析失败，尝试处理Python字典格式
          // 将单引号替换为双引号，处理None值
          const normalizedContent = content
            .replace(/'/g, '"')
            .replace(/None/g, 'null')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
          
          data = JSON.parse(normalizedContent)
        }
        
        // 检查是否是搜索工具类型
        if (data.type === 'search_ref' || data.type === 'search_tool') {
          return renderSearchReferences(data)
        }
        
        // 其他类型保持原样
        return content
      } catch (e) {
        // 如果都解析失败，保持原样
        return content
      }
    }

    // 搜索结果渲染器
    const renderSearchReferences = (data) => {
      if (!data.datas || !Array.isArray(data.datas)) return ''
      
      const validItems = data.datas.filter(item => item.title && item.url)
      if (validItems.length === 0) return ''
      
      const richContent = validItems
        .map(item => {
          let content = `### [${item.title}](${item.url})\n`
          
          // 添加内容摘要（前50字）
          if (item.content && item.content.trim()) {
            const summary = item.content.trim().length > 50 
              ? item.content.trim().substring(0, 50) + '...'
              : item.content.trim()
            content += `${summary}\n`
          }
          
          return content
        })
        .join('\n---\n\n')
      
      return `\n\n**🔍 相关参考资料：**\n\n${richContent}\n`
    }

    // const formatSegmentTime = (timestamp) => {
    //   return new Date(timestamp).toLocaleTimeString('zh-CN', {
    //     hour: '2-digit',
    //     minute: '2-digit',
    //     second: '2-digit'
    //   })
    // }

    const toggleCard = () => {
      isCollapsed.value = !isCollapsed.value
      emit('toggle-card', props.agentInfo.key, isCollapsed.value)
    }

    const toggleConversation = (conversationId) => {
      emit('toggle-conversation', props.agentInfo.key, conversationId)
    }


    watch(() => props.currentStatus, (newStatus) => {
      if (newStatus === 'streaming' && isCollapsed.value) {
        isCollapsed.value = false
      }
    })

    return {
      isCollapsed,
      totalDuration,
      totalCharacters,
      formatTime,
      formatDuration,
      formatContent,
      toggleCard,
      toggleConversation
    }
  }
}
</script>

<style scoped>
.agent-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  margin-bottom: 16px;
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

.agent-card.status-streaming {
  border-color: #4299e1;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.25);
  transform: translateY(-2px);
}

.agent-card.status-streaming::before {
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

.agent-card.card-collapsed {
  transform: scale(0.98);
  opacity: 0.8;
}

/* 焦点区工作中的特殊样式 */
.agent-card.in-focus {
  border-color: #f59e0b;
  box-shadow: 0 12px 40px rgba(245, 158, 11, 0.3);
  transform: translateY(-4px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(254, 243, 199, 0.95) 100%);
}

.agent-card.in-focus::before {
  background: linear-gradient(90deg, #f59e0b, #d97706, #b45309);
  animation: focusShimmer 1.5s ease-in-out infinite;
  height: 6px;
}

.agent-card.in-focus .agent-card-header {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(255, 255, 255, 0.95) 100%);
  border-bottom: 2px solid rgba(245, 158, 11, 0.3);
}

.agent-card.in-focus .agent-avatar {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
  animation: focusPulse 2s ease-in-out infinite;
}

.agent-card.in-focus .agent-name {
  color: #92400e;
  font-weight: 700;
}

.agent-card.in-focus .agent-description {
  color: #b45309;
}

.agent-card.in-focus .status-indicator {
  background: rgba(245, 158, 11, 0.2);
  border: 2px solid rgba(245, 158, 11, 0.4);
  color: #92400e;
  font-weight: 700;
}

.agent-card.in-focus .status-indicator .pulse-dot {
  background: #f59e0b;
  animation: focusPulse 1s ease-in-out infinite;
}

/* 焦点区工作指示器 */
.agent-card.in-focus::after {
  content: '🎯 焦点工作中';
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  animation: focusBounce 2s ease-in-out infinite;
  z-index: 10;
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: background 0.2s ease;
}

.agent-card-header:hover {
  background: linear-gradient(135deg, rgba(247, 250, 252, 0.98) 0%, rgba(237, 242, 247, 0.98) 100%);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.agent-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(66, 153, 225, 0.1);
  transition: all 0.3s ease;
}

.agent-icon {
  font-size: 20px;
}

.streaming-pulse {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.agent-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
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
  font-weight: 500;
}

.card-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.conversation-info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: rgba(66, 153, 225, 0.1);
  border-radius: 6px;
  font-size: 11px;
}

.conversation-info-header .conversation-time {
  color: #4299e1;
  font-weight: 600;
  font-family: monospace;
}


.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.05);
}

.status-indicator.status-streaming {
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  border: 1px solid rgba(66, 153, 225, 0.2);
}

.status-indicator.status-completed {
  color: #48bb78;
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.status-indicator.status-waiting {
  color: #a0aec0;
  background: rgba(160, 174, 192, 0.1);
  border: 1px solid rgba(160, 174, 192, 0.2);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-btn, .action-btn, .focus-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 14px;
}

.collapse-btn:hover, .action-btn:hover, .focus-btn:hover {
  background: rgba(66, 153, 225, 0.1);
  transform: scale(1.05);
}

.focus-btn {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.focus-btn:hover {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.4);
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.focus-icon {
  font-size: 14px;
}

.collapse-icon {
  transition: transform 0.3s ease;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.agent-card-content {
  padding: 0;
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.conversation-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.conversation-item:last-child {
  border-bottom: none;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(247, 250, 252, 0.5);
  cursor: pointer;
  transition: background 0.2s ease;
}

.conversation-header:hover {
  background: rgba(237, 242, 247, 0.8);
}

.conversation-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.conversation-index {
  font-size: 12px;
  font-weight: 600;
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.conversation-time {
  font-size: 11px;
  color: #718096;
  font-family: monospace;
}


.mini-pulse {
  width: 6px;
  height: 6px;
  background: #4299e1;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.conversation-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-length {
  font-size: 10px;
  color: #a0aec0;
}

.mini-collapse-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.mini-collapse-btn:hover {
  background: rgba(66, 153, 225, 0.1);
}

.mini-collapse-icon {
  font-size: 10px;
  transition: transform 0.3s ease;
}

.mini-collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.conversation-content {
  padding: 16px 20px;
  background: white;
}

.conversation-item.conversation-collapsed .conversation-content {
  display: none;
}

.markdown-content {
  line-height: 1.6;
  font-size: 14px;
  color: #2d3748;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
}

/* 内容段落分割样式 */
.content-segment {
  margin-bottom: 16px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid transparent;
}

.content-segment:last-child {
  margin-bottom: 0;
}

.content-segment-primary {
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.05) 0%, rgba(66, 153, 225, 0.02) 100%);
  border-color: rgba(66, 153, 225, 0.15);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.1);
}

.content-segment-secondary {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.05) 0%, rgba(72, 187, 120, 0.02) 100%);
  border-color: rgba(72, 187, 120, 0.15);
  box-shadow: 0 2px 8px rgba(72, 187, 120, 0.1);
}

.content-segment:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.segment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 11px;
}

.content-segment-primary .segment-header {
  background: rgba(66, 153, 225, 0.1);
  border-bottom-color: rgba(66, 153, 225, 0.2);
}

.content-segment-secondary .segment-header {
  background: rgba(72, 187, 120, 0.1);
  border-bottom-color: rgba(72, 187, 120, 0.2);
}

.segment-label {
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 4px;
}

.content-segment-primary .segment-label {
  color: #2563eb;
}

.content-segment-secondary .segment-label {
  color: #059669;
}

.segment-label::before {
  content: '📝';
  font-size: 10px;
}

.content-segment-primary .segment-label::before {
  content: '🔵';
}

.content-segment-secondary .segment-label::before {
  content: '🟢';
}

.segment-time {
  font-family: monospace;
  color: #718096;
  font-size: 10px;
}

.segment-content {
  padding: 12px;
}

.content-segment-primary .segment-content {
  background: rgba(255, 255, 255, 0.9);
}

.content-segment-secondary .segment-content {
  background: rgba(255, 255, 255, 0.9);
}

/* 为段落内的markdown内容添加特殊样式 */
.segment-content .markdown-content h1,
.segment-content .markdown-content h2,
.segment-content .markdown-content h3 {
  margin-top: 8px;
  margin-bottom: 6px;
}

.segment-content .markdown-content p:first-child {
  margin-top: 0;
}

.segment-content .markdown-content p:last-child {
  margin-bottom: 0;
}

/* 工具调用结果的特殊样式 */
.segment-content .markdown-content strong:contains("🔍 相关参考资料") {
  color: #4299e1;
  font-size: 13px;
}

.content-segment-primary .segment-content .markdown-content strong {
  color: #2563eb;
}

.content-segment-secondary .segment-content .markdown-content strong {
  color: #059669;
}

/* 链接样式优化 */
.content-segment-primary .segment-content .markdown-content a {
  color: #2563eb;
  border-bottom: 1px dotted rgba(37, 99, 235, 0.3);
}

.content-segment-secondary .segment-content .markdown-content a {
  color: #059669;
  border-bottom: 1px dotted rgba(5, 150, 105, 0.3);
}

.content-segment .segment-content .markdown-content a:hover {
  text-decoration: none;
  border-bottom-style: solid;
}

/* 代码块样式优化 */
.content-segment-primary .segment-content .markdown-content pre {
  border-left-color: #2563eb;
  background: rgba(37, 99, 235, 0.05);
}

.content-segment-secondary .segment-content .markdown-content pre {
  border-left-color: #059669;
  background: rgba(5, 150, 105, 0.05);
}

/* 列表样式优化 */
.content-segment-primary .segment-content .markdown-content ul li::marker {
  color: #2563eb;
}

.content-segment-secondary .segment-content .markdown-content ul li::marker {
  color: #059669;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .content-segment {
    margin-bottom: 12px;
  }
  
  .segment-header {
    padding: 6px 10px;
    font-size: 10px;
  }
  
  .segment-content {
    padding: 10px;
  }
}

.streaming-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(66, 153, 225, 0.3);
}

.streaming-indicator-detailed {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4299e1;
}

.streaming-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(66, 153, 225, 0.3);
  border-top: 2px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.streaming-text {
  font-size: 14px;
  font-weight: 500;
}

.current-streaming {
  margin: 16px 20px;
  padding: 16px;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 12px;
  border: 2px solid rgba(66, 153, 225, 0.2);
}

.streaming-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.streaming-label {
  font-size: 12px;
  font-weight: 600;
  color: #4299e1;
}

.streaming-progress {
  flex: 1;
  margin-left: 12px;
  height: 4px;
  background: rgba(66, 153, 225, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4299e1, #3182ce);
  animation: progress 2s ease-in-out infinite;
}

.streaming-content {
  line-height: 1.6;
  font-size: 14px;
  color: #2d3748;
}

.agent-card-footer {
  padding: 12px 20px;
  background: rgba(247, 250, 252, 0.5);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.stats-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  font-size: 11px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 4px;
}

.agent-card.agent-supervisor .agent-avatar {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}

.agent-card.agent-tour_search_agent .agent-avatar {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.agent-card.agent-day_plan_agent .agent-avatar {
  background: rgba(234, 88, 12, 0.1);
  color: #ea580c;
}

.agent-card.agent-live_transport_agent .agent-avatar {
  background: rgba(124, 58, 237, 0.1);
  color: #7c3aed;
}

.agent-card.agent-travel_butler_agent .agent-avatar {
  background: rgba(219, 39, 119, 0.1);
  color: #db2777;
}

.agent-card.agent-tools .agent-avatar {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.agent-card.agent-unified_stream .agent-avatar {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
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

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes progress {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
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

@keyframes focusPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes focusBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  color: #2d3748;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.markdown-content h1 {
  font-size: 18px;
  border-bottom: 2px solid #4299e1;
  padding-bottom: 4px;
}

.markdown-content h2 {
  font-size: 16px;
  color: #4a5568;
}

.markdown-content h3 {
  font-size: 15px;
  color: #718096;
}

.markdown-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content li {
  margin: 4px 0;
  line-height: 1.5;
}

.markdown-content strong {
  color: #2d3748;
  font-weight: 600;
}

.markdown-content em {
  color: #4a5568;
  font-style: italic;
}

.markdown-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.markdown-content pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border-left: 3px solid #4299e1;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.markdown-content pre code {
  background: none;
  padding: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.markdown-content blockquote {
  border-left: 4px solid #e2e8f0;
  padding-left: 16px;
  margin: 12px 0;
  color: #718096;
  font-style: italic;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background: rgba(66, 153, 225, 0.1);
  font-weight: 600;
}

.markdown-content a {
  color: #4299e1;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}

@media (max-width: 768px) {
  .agent-card-header {
    padding: 12px 16px;
  }
  
  .conversation-header {
    padding: 10px 16px;
  }
  
  .conversation-content {
    padding: 12px 16px;
  }
  
  .current-streaming {
    margin: 12px 16px;
    padding: 12px;
  }
  
  .agent-card-footer {
    padding: 10px 16px;
  }
  
  .stats-info {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>
