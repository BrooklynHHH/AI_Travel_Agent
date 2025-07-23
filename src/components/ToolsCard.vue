<template>
  <div class="tools-card" :class="[
    `tool-type-${toolType}`,
    `status-${currentStatus}`,
    { 'card-collapsed': isCollapsed },
    { 'has-error': hasError }
  ]">
    <!-- 卡片头部 -->
    <div class="tools-card-header" @click="toggleCard">
      <div class="tool-info">
        <div class="tool-avatar">
          <span class="tool-icon">🔧</span>
          <div v-if="currentStatus === 'processing'" class="processing-pulse"></div>
        </div>
        <div class="tool-details">
          <div class="tool-name">
            {{ getToolDisplayName() }}
            <span class="call-index">#{{ callIndex }}</span>
          </div>
          <div class="tool-description">{{ getToolDescription() }}</div>
        </div>
      </div>
      
      <div class="card-controls">
        <!-- 时间信息 -->
        <div v-if="timestamp" class="timestamp-info">
          <span class="timestamp">{{ formatTime(timestamp) }}</span>
        </div>
        
        <!-- 状态指示器 -->
        <div class="status-indicator" :class="`status-${currentStatus}`">
          <span v-if="currentStatus === 'processing'" class="status-text">
            <div class="pulse-dot"></div>
            处理中
          </span>
          <span v-else-if="currentStatus === 'completed'" class="status-text">
            ✅ 完成
          </span>
          <span v-else-if="currentStatus === 'error'" class="status-text">
            ❌ 错误
          </span>
          <span v-else class="status-text">
            ⏳ 等待
          </span>
        </div>
        
        <!-- 操作按钮 -->
        <div class="card-actions">
          <button 
            v-if="parsedContent && !hasError" 
            @click.stop="copyContent" 
            class="action-btn copy-btn" 
            title="复制内容"
          >
            <span class="action-icon">📋</span>
          </button>
          <button @click.stop="toggleCard" class="collapse-btn" :title="isCollapsed ? '展开' : '折叠'">
            <span class="collapse-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 卡片内容区域 -->
    <div v-if="!isCollapsed" class="tools-card-content">
      <!-- 错误显示 -->
      <div v-if="hasError" class="error-display">
        <div class="error-header">
          <span class="error-icon">⚠️</span>
          <span class="error-title">内容解析失败</span>
        </div>
        <div class="error-message">{{ errorMessage }}</div>
        <div class="error-actions">
          <button @click="showRawContent = !showRawContent" class="error-btn">
            {{ showRawContent ? '隐藏' : '查看' }}原始内容
          </button>
          <button @click="retryParsing" class="error-btn retry-btn">
            重试解析
          </button>
        </div>
        <div v-if="showRawContent" class="raw-content">
          <pre>{{ toolContent }}</pre>
        </div>
      </div>

      <!-- 正常内容显示 -->
      <div v-else-if="parsedContent" class="parsed-content">
        <!-- 搜索结果展示 -->
        <div v-if="contentType === 'search'" class="search-results-display">
          <div v-html="renderedContent"></div>
        </div>

        <!-- JSON数据展示 -->
        <div v-else-if="contentType === 'json'" class="json-data-display">
          <div class="json-header">
            <span class="json-icon">📊</span>
            <span class="json-title">结构化数据</span>
            <span class="json-count">({{ getJsonItemCount() }} 项)</span>
          </div>
          <div class="json-content">
            <pre><code>{{ formatJsonContent() }}</code></pre>
          </div>
        </div>

        <!-- 普通文本展示 -->
        <div v-else class="text-content-display">
          <div class="text-header">
            <span class="text-icon">📝</span>
            <span class="text-title">文本内容</span>
          </div>
          <div class="text-content" v-html="renderedContent"></div>
        </div>
      </div>

      <!-- 处理中状态 -->
      <div v-else-if="currentStatus === 'processing'" class="processing-display">
        <div class="processing-indicator">
          <div class="processing-spinner"></div>
          <span class="processing-text">正在处理工具调用...</span>
        </div>
      </div>

      <!-- 空内容 -->
      <div v-else class="empty-content">
        <div class="empty-indicator">
          <span class="empty-icon">📭</span>
          <span class="empty-text">暂无内容</span>
        </div>
      </div>
    </div>

    <!-- 卡片底部统计 -->
    <div v-if="!isCollapsed && parsedContent" class="tools-card-footer">
      <div class="content-stats">
        <span class="stat-item">
          📏 {{ getContentLength() }} 字符
        </span>
        <span v-if="contentType === 'search'" class="stat-item">
          🔍 {{ getSearchResultCount() }} 条结果
        </span>
        <span class="stat-item">
          🕒 {{ formatDuration(processingTime) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import ContentFormatter from '@/utils/contentFormatter.js'
import SearchContentParser from '@/utils/searchContentParser.js'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'ToolsCard',
  props: {
    toolContent: {
      type: String,
      default: ''
    },
    toolType: {
      type: String,
      default: 'unknown'
    },
    toolName: {
      type: String,
      default: 'unknown_tool'
    },
    callIndex: {
      type: Number,
      default: 1
    },
    timestamp: {
      type: Number,
      default: null
    },
    processingTime: {
      type: Number,
      default: 0
    },
    status: {
      type: String,
      default: 'waiting' // waiting, processing, completed, error
    }
  },
  emits: ['expand', 'collapse', 'error', 'copy'],
  setup(props, { emit }) {
    const isCollapsed = ref(false)
    const showRawContent = ref(false)
    const hasError = ref(false)
    const errorMessage = ref('')
    const parsedContent = ref(null)
    const contentType = ref('text')
    const renderedContent = ref('')

    const currentStatus = computed(() => props.status)

    // 解析内容
    const parseContent = async () => {
      if (!props.toolContent) {
        parsedContent.value = null
        contentType.value = 'text'
        hasError.value = false
        return
      }

      try {
        hasError.value = false
        errorMessage.value = ''

        // 直接使用传入的纯净内容，不需要提取
        const pureContent = props.toolContent
        
        // 🔑 关键改进：使用传入的工具类型，如果没有则自动检测
        let detectedType = props.toolType || 'unknown'
        
        // 如果工具类型未知，则使用内容检测
        if (detectedType === 'unknown') {
          detectedType = ContentFormatter.detectContentType(pureContent)
        }
        
        contentType.value = detectedType
        console.log(`🔧 [ToolsCard] 工具类型: ${detectedType}, 内容长度: ${pureContent.length}`)

        // 根据工具类型采用不同的解析策略
        switch (detectedType) {
          case 'search':
            await parseSearchContent(pureContent)
            break
            
          case 'json':
            await parseJsonContent(pureContent)
            break
            
          case 'api':
            await parseApiContent(pureContent)
            break
            
          case 'file':
            await parseFileContent(pureContent)
            break
            
          case 'database':
            await parseDatabaseContent(pureContent)
            break
            
          default:
            // 普通文本内容
            await parseTextContent(pureContent)
        }
      } catch (error) {
        console.error('工具内容解析失败:', error)
        hasError.value = true
        errorMessage.value = error.message || '未知解析错误'
        parsedContent.value = null
        emit('error', error)
      }
    }

    // 解析搜索内容
    const parseSearchContent = async (content) => {
      try {
        const searchData = await SearchContentParser.parseSearchContent(content)
        if (searchData) {
          parsedContent.value = searchData
          renderedContent.value = SearchContentParser.renderSearchResults(searchData, {
            showSummary: true,
            showMetadata: false,
            maxResults: 10,
            cardStyle: true
          })
          console.log(`✅ [ToolsCard] 搜索内容解析成功，结果数: ${searchData.results?.length || 0}`)
        } else {
          // 如果搜索内容解析失败，将其作为普通文本处理
          console.warn('🔧 [ToolsCard] 搜索内容解析失败，作为普通文本处理')
          await parseTextContent(content)
        }
      } catch (error) {
        console.warn('🔧 [ToolsCard] 搜索内容解析错误:', error)
        await parseTextContent(content)
      }
    }

    // 解析JSON内容
    const parseJsonContent = async (content) => {
      try {
        const jsonData = JSON.parse(content)
        parsedContent.value = jsonData
        renderedContent.value = ''
        console.log(`✅ [ToolsCard] JSON内容解析成功`)
      } catch (error) {
        console.warn('🔧 [ToolsCard] JSON解析失败，作为普通文本处理:', error)
        await parseTextContent(content)
      }
    }

    // 解析API响应内容
    const parseApiContent = async (content) => {
      try {
        // 尝试解析为JSON格式的API响应
        if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
          const apiData = JSON.parse(content)
          parsedContent.value = apiData
          renderedContent.value = ''
          console.log(`✅ [ToolsCard] API响应解析成功`)
        } else {
          // 普通文本格式的API响应
          parsedContent.value = content
          renderedContent.value = md.render(content)
          console.log(`✅ [ToolsCard] API文本响应解析成功`)
        }
      } catch (error) {
        console.warn('🔧 [ToolsCard] API内容解析失败，作为普通文本处理:', error)
        await parseTextContent(content)
      }
    }

    // 解析文件操作内容
    const parseFileContent = async (content) => {
      parsedContent.value = content
      // 对文件路径和操作进行特殊格式化
      const formattedContent = content
        .replace(/文件路径:/g, '**文件路径:**')
        .replace(/操作类型:/g, '**操作类型:**')
        .replace(/文件大小:/g, '**文件大小:**')
      renderedContent.value = md.render(formattedContent)
      console.log(`✅ [ToolsCard] 文件操作内容解析成功`)
    }

    // 解析数据库操作内容
    const parseDatabaseContent = async (content) => {
      parsedContent.value = content
      // 对SQL语句进行特殊格式化
      const formattedContent = content
        .replace(/(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN)/g, '**$1**')
        .replace(/查询结果:/g, '**查询结果:**')
        .replace(/影响行数:/g, '**影响行数:**')
      renderedContent.value = md.render(formattedContent)
      console.log(`✅ [ToolsCard] 数据库操作内容解析成功`)
    }

    // 解析普通文本内容
    const parseTextContent = async (content) => {
      parsedContent.value = content
      renderedContent.value = md.render(content)
      console.log(`✅ [ToolsCard] 文本内容解析成功`)
    }


    // 工具显示名称
    const getToolDisplayName = () => {
      const toolNames = {
        search: '🔍 搜索工具',
        search_ref: '🔍 搜索引用',
        search_tool: '🔍 搜索工具',
        api: '🌐 API调用',
        database: '🗄️ 数据库查询',
        file: '📁 文件操作',
        unknown: '🔧 工具调用'
      }
      return toolNames[props.toolType] || toolNames.unknown
    }

    // 工具描述
    const getToolDescription = () => {
      const descriptions = {
        search: '搜索相关信息和资料',
        search_ref: '获取搜索引用结果',
        search_tool: '执行搜索查询',
        api: '调用外部API接口',
        database: '查询数据库信息',
        file: '处理文件操作',
        unknown: '执行工具调用操作'
      }
      return descriptions[props.toolType] || descriptions.unknown
    }

    // 格式化时间
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    // 格式化持续时间
    const formatDuration = (duration) => {
      if (duration < 1000) return `${duration}ms`
      return `${(duration / 1000).toFixed(1)}s`
    }

    // 获取内容长度
    const getContentLength = () => {
      return props.toolContent?.length || 0
    }

    // 获取搜索结果数量
    const getSearchResultCount = () => {
      if (contentType.value === 'search' && parsedContent.value?.results) {
        return parsedContent.value.results.length
      }
      return 0
    }

    // 获取JSON项目数量
    const getJsonItemCount = () => {
      if (contentType.value === 'json' && parsedContent.value) {
        if (Array.isArray(parsedContent.value)) {
          return parsedContent.value.length
        }
        return Object.keys(parsedContent.value).length
      }
      return 0
    }

    // 格式化JSON内容
    const formatJsonContent = () => {
      if (parsedContent.value) {
        return JSON.stringify(parsedContent.value, null, 2)
      }
      return ''
    }

    // 切换卡片状态
    const toggleCard = () => {
      isCollapsed.value = !isCollapsed.value
      emit(isCollapsed.value ? 'collapse' : 'expand')
    }

    // 复制内容
    const copyContent = async () => {
      try {
        let textToCopy = ''
        
        if (contentType.value === 'search' && parsedContent.value) {
          textToCopy = SearchContentParser.getTextSummary(parsedContent.value)
        } else if (contentType.value === 'json') {
          textToCopy = formatJsonContent()
        } else {
          textToCopy = props.toolContent
        }

        await navigator.clipboard.writeText(textToCopy)
        emit('copy', textToCopy)
        
        // 简单的复制成功提示
        const copyBtn = document.querySelector('.copy-btn .action-icon')
        if (copyBtn) {
          const originalText = copyBtn.textContent
          copyBtn.textContent = '✅'
          setTimeout(() => {
            copyBtn.textContent = originalText
          }, 1000)
        }
      } catch (error) {
        console.error('复制失败:', error)
      }
    }

    // 重试解析
    const retryParsing = () => {
      parseContent()
    }

    // 监听内容变化
    watch(() => props.toolContent, () => {
      parseContent()
    }, { immediate: true })

    // 监听状态变化
    watch(() => props.status, (newStatus) => {
      if (newStatus === 'processing' && isCollapsed.value) {
        isCollapsed.value = false
      }
    })

    return {
      isCollapsed,
      showRawContent,
      hasError,
      errorMessage,
      parsedContent,
      contentType,
      renderedContent,
      currentStatus,
      getToolDisplayName,
      getToolDescription,
      formatTime,
      formatDuration,
      getContentLength,
      getSearchResultCount,
      getJsonItemCount,
      formatJsonContent,
      toggleCard,
      copyContent,
      retryParsing
    }
  }
}
</script>

<style scoped>
.tools-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  margin-bottom: 16px;
}

.tools-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  transition: all 0.3s ease;
}

.tools-card.status-processing {
  border-color: #f59e0b;
  box-shadow: 0 8px 32px rgba(245, 158, 11, 0.25);
  transform: translateY(-2px);
}

.tools-card.status-processing::before {
  background: linear-gradient(90deg, #f59e0b, #d97706);
  animation: shimmer 2s ease-in-out infinite;
}

.tools-card.status-completed {
  border-color: #48bb78;
  box-shadow: 0 8px 32px rgba(72, 187, 120, 0.2);
}

.tools-card.status-completed::before {
  background: linear-gradient(90deg, #48bb78, #38a169);
}

.tools-card.status-error {
  border-color: #f56565;
  box-shadow: 0 8px 32px rgba(245, 101, 101, 0.2);
}

.tools-card.status-error::before {
  background: linear-gradient(90deg, #f56565, #e53e3e);
}

.tools-card.card-collapsed {
  transform: scale(0.98);
  opacity: 0.8;
}

.tools-card.has-error {
  border-color: #f56565;
}

.tools-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: background 0.2s ease;
}

.tools-card-header:hover {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(247, 250, 252, 0.98) 100%);
}

.tool-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.tool-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  transition: all 0.3s ease;
}

.tool-icon {
  font-size: 20px;
}

.processing-pulse {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #f59e0b;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.tool-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.2;
}

.tool-description {
  font-size: 12px;
  color: #718096;
  font-weight: 500;
}

.call-index {
  font-size: 11px;
  color: #718096;
  font-weight: normal;
  margin-left: 8px;
  padding: 2px 6px;
  background: rgba(113, 128, 150, 0.1);
  border-radius: 4px;
  font-family: monospace;
}

.card-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timestamp-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 6px;
  font-size: 11px;
}

.timestamp {
  color: #f59e0b;
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

.status-indicator.status-processing {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.status-indicator.status-completed {
  color: #48bb78;
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.status-indicator.status-error {
  color: #f56565;
  background: rgba(245, 101, 101, 0.1);
  border: 1px solid rgba(245, 101, 101, 0.2);
}

.status-indicator.status-waiting {
  color: #a0aec0;
  background: rgba(160, 174, 192, 0.1);
  border: 1px solid rgba(160, 174, 192, 0.2);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #f59e0b;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn, .collapse-btn {
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

.action-btn:hover, .collapse-btn:hover {
  background: rgba(245, 158, 11, 0.1);
  transform: scale(1.05);
}

.copy-btn {
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.copy-btn:hover {
  background: rgba(72, 187, 120, 0.2);
  border-color: rgba(72, 187, 120, 0.4);
}

.collapse-icon {
  transition: transform 0.3s ease;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.tools-card-content {
  padding: 0;
}

/* 错误显示样式 */
.error-display {
  padding: 20px;
  background: rgba(245, 101, 101, 0.05);
  border: 1px solid rgba(245, 101, 101, 0.2);
  margin: 16px 20px;
  border-radius: 12px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.error-icon {
  font-size: 18px;
}

.error-title {
  font-size: 16px;
  font-weight: 600;
  color: #e53e3e;
}

.error-message {
  color: #c53030;
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.error-btn {
  padding: 8px 16px;
  border: 1px solid rgba(245, 101, 101, 0.3);
  background: rgba(245, 101, 101, 0.1);
  color: #c53030;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.error-btn:hover {
  background: rgba(245, 101, 101, 0.2);
  border-color: rgba(245, 101, 101, 0.5);
}

.retry-btn {
  background: rgba(72, 187, 120, 0.1);
  border-color: rgba(72, 187, 120, 0.3);
  color: #38a169;
}

.retry-btn:hover {
  background: rgba(72, 187, 120, 0.2);
  border-color: rgba(72, 187, 120, 0.5);
}

.raw-content {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.raw-content pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 内容显示样式 */
.parsed-content {
  padding: 16px 20px;
}

.search-results-display {
  /* 继承搜索结果的样式 */
}

.json-data-display {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.json-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(66, 153, 225, 0.1);
  border-bottom: 1px solid rgba(66, 153, 225, 0.2);
}

.json-icon {
  font-size: 16px;
}

.json-title {
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
}

.json-count {
  font-size: 12px;
  color: #718096;
}

.json-content {
  background: rgba(0, 0, 0, 0.02);
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.json-content pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
  color: #2d3748;
}

.text-content-display {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.text-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(107, 114, 128, 0.1);
  border-bottom: 1px solid rgba(107, 114, 128, 0.2);
}

.text-icon {
  font-size: 16px;
}

.text-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.text-content {
  padding: 16px;
  line-height: 1.6;
  color: #2d3748;
}

/* 处理中状态样式 */
.processing-display {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.processing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f59e0b;
}

.processing-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(245, 158, 11, 0.3);
  border-top: 2px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.processing-text {
  font-size: 14px;
  font-weight: 500;
}

/* 空内容样式 */
.empty-content {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #a0aec0;
}

.empty-icon {
  font-size: 24px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
}

/* 底部统计样式 */
.tools-card-footer {
  padding: 12px 20px;
  background: rgba(245, 158, 11, 0.05);
  border-top: 1px solid rgba(245, 158, 11, 0.1);
}

.content-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.stat-item {
  font-size: 11px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .tools-card-header {
    padding: 12px 16px;
  }
  
  .card-controls {
    gap: 8px;
  }
  
  .timestamp-info {
    display: none;
  }
  
  .parsed-content {
    padding: 12px 16px;
  }
  
  .error-display {
    margin: 12px 16px;
    padding: 16px;
  }
  
  .processing-display,
  .empty-content {
    padding: 30px 16px;
  }
  
  .tools-card-footer {
    padding: 10px 16px;
  }
  
  .content-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .json-content,
  .raw-content {
    max-height: 300px;
  }
}

/* 搜索结果样式继承和覆盖 */
.search-results-display .search-results-container {
  margin: 0;
  border: none;
  background: transparent;
}

.search-results-display .search-results-header {
  background: rgba(245, 158, 11, 0.1);
  border-bottom-color: rgba(245, 158, 11, 0.2);
}

.search-results-display .search-results-title {
  color: #d97706;
}

.search-results-display .search-item-card:hover {
  border-color: rgba(245, 158, 11, 0.3);
}

.search-results-display .search-item-title {
  color: #d97706;
}

.search-results-display .search-item-title:hover {
  color: #b45309;
}
</style>
