<template>
  <div class="focus-agent-card" :class="[
    `agent-${agentInfo.key}`,
    `status-${currentStatus}`
  ]">
    <!-- 焦点区头部 -->
    <div class="focus-card-header">
      <div class="focus-agent-info">
        <div class="focus-agent-avatar">
          <span class="focus-agent-icon">{{ agentInfo.icon }}</span>
          <div v-if="currentStatus === 'streaming'" class="focus-streaming-pulse"></div>
        </div>
        <div class="focus-agent-details">
          <div class="focus-agent-name">{{ agentInfo.name }}</div>
          <div class="focus-agent-description">{{ agentInfo.description }}</div>
        </div>
      </div>
      
      <div class="focus-status-indicator">
        <div class="focus-status-content" :class="statusClass">
          <div class="focus-pulse-dot" :class="statusClass"></div>
          <span class="focus-status-text">{{ statusText }}</span>
        </div>
        <div class="focus-time">{{ formatTime(Date.now()) }}</div>
      </div>
    </div>

    <!-- 焦点区内容 -->
    <div class="focus-card-content">
      <div class="focus-streaming-content">
        <div 
          v-if="streamingContent" 
          class="focus-markdown-content" 
          v-html="formatContent(streamingContent)"
        ></div>
        <div v-else class="focus-streaming-placeholder">
          <div class="focus-streaming-indicator">
            <div class="focus-streaming-spinner"></div>
            <span class="focus-streaming-text">正在生成内容...</span>
          </div>
        </div>
        
        <!-- 流式输出光标 -->
        <div v-if="currentStatus === 'streaming'" class="focus-streaming-cursor">▋</div>
      </div>
    </div>

    <!-- 焦点区底部信息 -->
    <div class="focus-card-footer">
      <div class="focus-stats">
        <span class="focus-stat-item">
          📝 {{ streamingContent?.length || 0 }} 字符
        </span>
        <span class="focus-stat-item">
          ⚡ 实时输出
        </span>
      </div>
      <div class="focus-actions">
        <button @click="$emit('minimize')" class="focus-minimize-btn" title="最小化到网格">
          ⬇️ 最小化
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, watch, nextTick, ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'FocusAgentCard',
  props: {
    agentInfo: {
      type: Object,
      required: true
    },
    streamingContent: {
      type: String,
      default: ''
    },
    currentStatus: {
      type: String,
      default: 'streaming'
    }
  },
  emits: ['minimize'],
  setup(props) {
    const contentContainer = ref(null)
    const isUserScrolling = ref(false)
    const scrollTimeout = ref(null)

    // 动态状态文本
    const statusText = computed(() => {
      switch (props.currentStatus) {
        case 'streaming':
          return '正在工作中...'
        case 'completed':
          return '任务已完成'
        case 'waiting':
          return '等待中...'
        default:
          return '未知状态'
      }
    })

    // 动态状态样式类
    const statusClass = computed(() => {
      return `status-${props.currentStatus}`
    })

    // 滚动到底部
    const scrollToBottom = () => {
      if (!contentContainer.value || isUserScrolling.value) return
      
      try {
        contentContainer.value.scrollTo({
          top: contentContainer.value.scrollHeight,
          behavior: 'smooth'
        })
      } catch (e) {
        // 兼容性处理
        contentContainer.value.scrollTop = contentContainer.value.scrollHeight
      }
    }

    // 检测用户滚动行为
    const handleScroll = () => {
      if (!contentContainer.value) return
      
      const { scrollTop, scrollHeight, clientHeight } = contentContainer.value
      const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 50 // 增加容差到50px
      
      if (!isAtBottom) {
        isUserScrolling.value = true
        
        // 清除之前的定时器
        if (scrollTimeout.value) {
          clearTimeout(scrollTimeout.value)
        }
        
        // 5秒后重新启用自动滚动（延长时间）
        scrollTimeout.value = setTimeout(() => {
          isUserScrolling.value = false
        }, 5000)
      } else {
        isUserScrolling.value = false
      }
    }

    // 监听内容变化，自动滚动到底部
    watch(() => props.streamingContent, (newContent, oldContent) => {
      if (newContent && newContent !== oldContent) {
        nextTick(() => {
          scrollToBottom()
        })
      }
    }, { flush: 'post' })

    // 监听状态变化
    watch(() => props.currentStatus, (newStatus) => {
      console.log(`🎯 [焦点区状态] ${props.agentInfo.name}: ${newStatus}`)
    })

    // 组件挂载后设置滚动监听
    onMounted(() => {
      nextTick(() => {
        // 使用 ref 获取当前组件内的元素，避免全局选择器冲突
        const cardElement = document.querySelector('.focus-agent-card')
        if (cardElement) {
          const contentElement = cardElement.querySelector('.focus-card-content')
          if (contentElement) {
            contentContainer.value = contentElement
            contentElement.addEventListener('scroll', handleScroll, { passive: true })
          }
        }
      })
    })

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const formatContent = (content) => {
      if (!content) return ''
      
      // 处理工具调用的JSON输出
      const processedContent = processJsonContent(content)
      
      // 渲染markdown
      return md.render(processedContent)
    }

    const processJsonContent = (content) => {
      try {
        // 处理工具调用的JSON输出，转换为markdown链接
        const jsonRegex = /\{[^{}]*['"]type['"]:\s*['"]search_ref['"][^{}]*['"]datas['"]:\s*\[[^\]]*\][^{}]*\}/g
        
        return content.replace(jsonRegex, (match) => {
          try {
            // 将单引号替换为双引号以便JSON.parse正确解析
            let normalizedJson = match
              .replace(/'/g, '"')
              .replace(/(\w+):/g, '"$1":') // 确保属性名有双引号
            
            const data = JSON.parse(normalizedJson)
            
            if (data.type === 'search_ref' && data.datas && Array.isArray(data.datas)) {
              const markdownLinks = data.datas
                .filter(item => item.title && item.url)
                .map(item => `- [${item.title}](${item.url})`)
                .join('\n')
              
              return markdownLinks ? `\n\n**🔍 相关参考资料：**\n${markdownLinks}\n` : ''
            }
          } catch (e) {
            console.warn('解析工具调用结果失败:', e)
            
            // 备用解析方案
            try {
              const titleRegex = /['"]title['"]:\s*['"]([^'"]+)['"]/g
              const urlRegex = /['"]url['"]:\s*['"]([^'"]+)['"]/g
              
              const titles = []
              const urls = []
              
              let titleMatch
              while ((titleMatch = titleRegex.exec(match)) !== null) {
                titles.push(titleMatch[1])
              }
              
              let urlMatch
              while ((urlMatch = urlRegex.exec(match)) !== null) {
                urls.push(urlMatch[1])
              }
              
              if (titles.length > 0 && urls.length > 0 && titles.length === urls.length) {
                const markdownLinks = titles
                  .map((title, index) => `- [${title}](${urls[index]})`)
                  .join('\n')
                
                return markdownLinks ? `\n\n**🔍 相关参考资料：**\n${markdownLinks}\n` : ''
              }
            } catch (regexError) {
              console.warn('正则表达式提取失败:', regexError)
            }
          }
          return match
        })
      } catch (e) {
        console.warn('处理内容格式化失败:', e)
        return content
      }
    }

    return {
      formatTime,
      formatContent,
      statusText,
      statusClass,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
.focus-agent-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 12px;
  border: 2px solid #4299e1;
  box-shadow: 0 8px 24px rgba(66, 153, 225, 0.3);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  backdrop-filter: blur(20px);
  height: 100%; /* 使用父容器的完整高度 */
  width: 100%; /* 使用父容器的完整宽度 */
  display: flex;
  flex-direction: column;
}

.focus-agent-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4299e1, #3182ce, #2563eb);
  animation: focusShimmer 2s ease-in-out infinite;
}

.focus-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
  border-bottom: 1px solid rgba(66, 153, 225, 0.2);
  flex-shrink: 0;
}

.focus-agent-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.focus-agent-avatar {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.focus-agent-icon {
  font-size: 18px;
  color: white;
}

.focus-streaming-pulse {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 10px;
  height: 10px;
  background: #48bb78;
  border-radius: 50%;
  border: 2px solid white;
  animation: focusPulse 1.5s ease-in-out infinite;
}

.focus-agent-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.focus-agent-name {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.focus-agent-description {
  font-size: 11px;
  color: #4a5568;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.focus-status-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.focus-status-content {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  background: rgba(66, 153, 225, 0.15);
  border: 1px solid rgba(66, 153, 225, 0.3);
  color: #2563eb;
  white-space: nowrap;
}

.focus-pulse-dot {
  width: 6px;
  height: 6px;
  background: #4299e1;
  border-radius: 50%;
  animation: focusPulse 1.5s ease-in-out infinite;
}

.focus-time {
  font-size: 10px;
  color: #718096;
  font-family: monospace;
  background: rgba(113, 128, 150, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

.focus-card-content {
  padding: 12px 16px;
  flex: 1;
  overflow-y: scroll; /* 强制显示滚动条 */
  overflow-x: hidden;
  min-height: 0;
  max-height: calc(85vh - 120px); /* 减去头部和底部的高度 */
  scroll-behavior: smooth; /* 平滑滚动 */
  word-wrap: break-word; /* 长单词换行 */
  hyphens: auto; /* 自动断字 */
  position: relative;
}

.focus-streaming-content {
  position: relative;
  line-height: 1.6;
  font-size: 13px;
  color: #2d3748;
}

.focus-markdown-content {
  line-height: 1.6;
  font-size: 13px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
}

.focus-streaming-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(66, 153, 225, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(66, 153, 225, 0.3);
}

.focus-streaming-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4299e1;
}

.focus-streaming-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(66, 153, 225, 0.3);
  border-top: 2px solid #4299e1;
  border-radius: 50%;
  animation: focusSpin 1s linear infinite;
}

.focus-streaming-text {
  font-size: 12px;
  font-weight: 500;
}

.focus-streaming-cursor {
  display: inline-block;
  color: #4299e1;
  font-size: 14px;
  font-weight: bold;
  animation: focusBlink 1s ease-in-out infinite;
  margin-left: 2px;
}

.focus-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(247, 250, 252, 0.8);
  border-top: 1px solid rgba(66, 153, 225, 0.2);
  flex-shrink: 0;
}

.focus-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.focus-stat-item {
  font-size: 10px;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.focus-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.focus-minimize-btn {
  padding: 4px 8px;
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  border: 1px solid rgba(66, 153, 225, 0.3);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.focus-minimize-btn:hover {
  background: rgba(66, 153, 225, 0.2);
  border-color: #4299e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
}

/* 不同智能体的主题色 */
.focus-agent-card.agent-supervisor .focus-agent-avatar {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.focus-agent-card.agent-tour_search_agent .focus-agent-avatar {
  background: linear-gradient(135deg, #059669, #047857);
}

.focus-agent-card.agent-day_plan_agent .focus-agent-avatar {
  background: linear-gradient(135deg, #ea580c, #dc2626);
}

.focus-agent-card.agent-live_transport_agent .focus-agent-avatar {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
}

.focus-agent-card.agent-travel_butler_agent .focus-agent-avatar {
  background: linear-gradient(135deg, #db2777, #be185d);
}

/* Markdown 内容样式优化 */
.focus-markdown-content h1,
.focus-markdown-content h2,
.focus-markdown-content h3,
.focus-markdown-content h4,
.focus-markdown-content h5,
.focus-markdown-content h6 {
  color: #2d3748;
  margin: 20px 0 12px 0;
  font-weight: 600;
}

.focus-markdown-content h1 {
  font-size: 22px;
  border-bottom: 3px solid #4299e1;
  padding-bottom: 8px;
}

.focus-markdown-content h2 {
  font-size: 20px;
  color: #4a5568;
}

.focus-markdown-content h3 {
  font-size: 18px;
  color: #718096;
}

.focus-markdown-content p {
  margin: 12px 0;
  line-height: 1.8;
}

.focus-markdown-content ul,
.focus-markdown-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.focus-markdown-content li {
  margin: 6px 0;
  line-height: 1.6;
}

.focus-markdown-content strong {
  color: #2d3748;
  font-weight: 600;
}

.focus-markdown-content em {
  color: #4a5568;
  font-style: italic;
}

.focus-markdown-content code {
  background: rgba(66, 153, 225, 0.1);
  padding: 3px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 15px;
  color: #2563eb;
}

.focus-markdown-content pre {
  background: rgba(66, 153, 225, 0.05);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  border-left: 4px solid #4299e1;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.focus-markdown-content pre code {
  background: none;
  padding: 0;
  color: #2d3748;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.focus-markdown-content blockquote {
  border-left: 4px solid #4299e1;
  padding-left: 20px;
  margin: 16px 0;
  color: #4a5568;
  font-style: italic;
  background: rgba(66, 153, 225, 0.05);
  padding: 12px 20px;
  border-radius: 8px;
}

.focus-markdown-content a {
  color: #4299e1;
  text-decoration: none;
  border-bottom: 1px dotted rgba(66, 153, 225, 0.5);
}

.focus-markdown-content a:hover {
  text-decoration: none;
  border-bottom-style: solid;
  color: #2563eb;
}

.focus-markdown-content hr {
  border: none;
  border-top: 2px solid rgba(66, 153, 225, 0.2);
  margin: 24px 0;
}

/* 滚动条样式 */
.focus-card-content::-webkit-scrollbar {
  width: 8px;
}

.focus-card-content::-webkit-scrollbar-track {
  background: rgba(156, 163, 175, 0.2);
  border-radius: 4px;
}

.focus-card-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.focus-card-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #4f46e5, #7c3aed);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3);
}

/* 不同状态的样式 */
/* 完成状态 */
.focus-status-content.status-completed {
  background: rgba(72, 187, 120, 0.15);
  border: 1px solid rgba(72, 187, 120, 0.3);
  color: #2f855a;
}

.focus-pulse-dot.status-completed {
  background: #48bb78;
  animation: none; /* 停止脉冲动画 */
}

.focus-agent-card.status-completed::before {
  background: linear-gradient(90deg, #48bb78, #38a169, #2f855a);
}

/* 等待状态 */
.focus-status-content.status-waiting {
  background: rgba(237, 137, 54, 0.15);
  border: 1px solid rgba(237, 137, 54, 0.3);
  color: #c05621;
}

.focus-pulse-dot.status-waiting {
  background: #ed8936;
  animation: focusPulse 2s ease-in-out infinite; /* 慢一点的脉冲 */
}

.focus-agent-card.status-waiting::before {
  background: linear-gradient(90deg, #ed8936, #dd6b20, #c05621);
}

/* 流式状态（默认） */
.focus-status-content.status-streaming {
  background: rgba(66, 153, 225, 0.15);
  border: 1px solid rgba(66, 153, 225, 0.3);
  color: #2563eb;
}

.focus-pulse-dot.status-streaming {
  background: #4299e1;
  animation: focusPulse 1.5s ease-in-out infinite;
}

.focus-agent-card.status-streaming::before {
  background: linear-gradient(90deg, #4299e1, #3182ce, #2563eb);
  animation: focusShimmer 2s ease-in-out infinite;
}

/* 动画效果 */
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

@keyframes focusSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes focusBlink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .focus-card-header {
    padding: 16px 20px;
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .focus-agent-info {
    gap: 16px;
  }
  
  .focus-agent-avatar {
    width: 48px;
    height: 48px;
  }
  
  .focus-agent-icon {
    font-size: 24px;
  }
  
  .focus-agent-name {
    font-size: 20px;
  }
  
  .focus-agent-description {
    font-size: 14px;
  }
  
  .focus-agent-card {
    height: 80vh; /* 移动端高度 */
    max-height: 80vh;
  }
  
  .focus-card-content {
    padding: 20px;
    max-height: calc(80vh - 140px); /* 移动端减去头部和底部高度 */
    overflow-y: scroll; /* 确保移动端也强制显示滚动条 */
  }
  
  .focus-card-footer {
    padding: 12px 20px;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .focus-stats {
    gap: 16px;
  }
}
</style>
