<template>
  <div class="supervisor-agent-container">
    <!-- 头部标题 -->
    <div class="header">
      <h1 class="title">🧳 智能旅游规划助手 (完整版)</h1>
      <p class="subtitle">完全按照Python逻辑实现的智能对话流程</p>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages-wrapper">
        <!-- 消息列表 -->
        <div v-for="(message, index) in messages.filter(msg => msg.type !== 'planning_result')" :key="index" class="message-item">
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
              <!-- 需求收集阶段 -->
              <div v-if="message.type === 'need_collection'" class="need-collection-message">
                <div class="collection-header">
                  <span class="collection-icon">📝</span>
                  <span class="collection-title">需求收集阶段</span>
                  <span class="collection-status" :class="message.data.status.toLowerCase()">
                    {{ message.data.status === 'CONTINUE' ? '收集中' : '收集完成' }}
                  </span>
                </div>
                
                <!-- 已确认需求 -->
                <div v-if="message.data && message.data.confirm_need && message.data.confirm_need.length > 0" class="confirmed-needs">
                  <h4>✅ 已确认需求：</h4>
                  <ul>
                    <li v-for="need in message.data.confirm_need" :key="need" class="need-item confirmed">
                      {{ need }}
                    </li>
                  </ul>
                </div>

                <!-- 待确认需求 -->
                <div v-if="message.data && message.data.need && message.data.need.length > 0" class="pending-needs">
                  <h4>❓ 还需要了解：</h4>
                  <ul>
                    <li v-for="question in message.data.need" :key="question" class="need-item pending">
                      {{ question }}
                    </li>
                  </ul>
                </div>

              </div>


              <!-- 普通文本消息 -->
              <div v-else class="text-message">
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

        <!-- 草稿历史记录容器 - 显示所有草稿版本 -->
        <div v-if="draftHistory.length > 0" class="draft-history-container">
          <div v-for="(draft, index) in draftHistory" :key="draft.id" class="draft-item-wrapper">
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">🗺️</div>
              <div class="message-content">
                <div class="planning-result" :class="{ 'latest-draft': index === draftHistory.length - 1, 'collapsed-draft': draft.isCollapsed }">
                  <!-- 草稿头部 -->
                  <div class="planning-header" @click="toggleDraftCollapse(draft.id)">
                    <div class="planning-header-left">
                      <span class="planning-icon">🗺️</span>
                      <span class="planning-title">{{ getDraftTitle(draft) }}</span>
                      <span class="planning-round">第{{ draft.round }}轮</span>
                      <span v-if="index === draftHistory.length - 1" class="latest-badge">最新</span>
                    </div>
                    <div class="planning-header-right">
                      <span class="planning-time">{{ formatTime(draft.timestamp) }}</span>
                      <span class="collapse-indicator" :class="{ 'collapsed': draft.isCollapsed }" v-if="draftHistory.length > 1">
                        {{ draft.isCollapsed ? '▶' : '▼' }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- 草稿内容 -->
                  <div class="planning-content-wrapper" :class="{ 'collapsed': draft.isCollapsed }">
                    <div class="planning-content" v-html="formatPlanningContent(draft.content)"></div>
                    
                    <!-- 方案操作按钮 -->
                    <div class="planning-actions" v-if="!isLoading">
                      <button @click="provideFeedbackForDraft(draft)" class="action-btn primary">
                        💬 基于此版本反馈
                      </button>
                      <button @click="regeneratePlanFromDraft(draft)" class="action-btn secondary">
                        🔄 基于此版本重新生成
                      </button>
                      <button v-if="index === draftHistory.length - 1" @click="acceptPlan" class="action-btn success">
                        ✅ 接受最新方案
                      </button>
                    </div>
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

    <!-- 反馈输入区域 -->
    <div v-if="showFeedbackInput" class="feedback-overlay">
      <div class="feedback-modal">
        <div class="feedback-header">
          <h3>💬 请提供您的反馈</h3>
          <button @click="showFeedbackInput = false" class="close-btn">✕</button>
        </div>
        <div class="feedback-content">
          <textarea
            v-model="feedbackText"
            placeholder="请告诉我您希望如何调整这个方案..."
            class="feedback-textarea"
            rows="4"
          ></textarea>
          <div class="feedback-suggestions">
            <h4>💡 常见调整建议：</h4>
            <div class="suggestion-tags">
              <span @click="addSuggestion('行程太紧，希望放慢节奏')" class="suggestion-tag">放慢节奏</span>
              <span @click="addSuggestion('增加更多美食体验')" class="suggestion-tag">增加美食</span>
              <span @click="addSuggestion('预算需要控制在更低范围')" class="suggestion-tag">降低预算</span>
              <span @click="addSuggestion('增加购物时间')" class="suggestion-tag">增加购物</span>
              <span @click="addSuggestion('更换住宿地点')" class="suggestion-tag">更换住宿</span>
              <span @click="addSuggestion('调整交通方式')" class="suggestion-tag">调整交通</span>
            </div>
          </div>
        </div>
        <div class="feedback-actions">
          <button @click="showFeedbackInput = false" class="action-btn secondary">取消</button>
          <button @click="submitFeedback" :disabled="!feedbackText.trim()" class="action-btn primary">
            提交反馈
          </button>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-main-wrapper">
        <!-- 美化后的状态信息栏 -->
        <div class="status-info-bar">
          <div class="status-info-left">
            <div class="phase-indicator">
              <div class="phase-dot-wrapper">
                <span class="phase-dot" :class="currentPhase">
                  <span class="phase-dot-inner"></span>
                </span>
                <span class="phase-icon">{{ getPhaseIcon(currentPhase) }}</span>
              </div>
              <div class="phase-text-wrapper">
                <span class="phase-text">{{ getPhaseText(currentPhase) }}</span>
                <span class="phase-subtitle">{{ getPhaseSubtitle(currentPhase) }}</span>
              </div>
            </div>
            <div class="round-info">
              <div class="round-circle">
                <span class="round-number">{{ currentRound }}</span>
              </div>
              <span class="round-label">轮次</span>
            </div>
          </div>
          <div class="status-info-right" v-if="sessionId">
            <div class="session-info">
              <div class="session-icon">💬</div>
              <div class="session-details">
                <span class="session-label">会话ID</span>
                <span class="session-id">{{ sessionId.substring(0, 8) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 美化后的主输入框区域 -->
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
                :placeholder="getInputPlaceholder()"
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
                  <span class="send-text">{{ getSendButtonText() }}</span>
                </span>
                <span v-else class="loading-content">
                  <div class="loading-spinner-small"></div>
                  <span class="loading-label">处理中</span>
                </span>
              </button>
            </div>
          </div>

          <!-- 美化后的快捷操作区域 -->
          <div class="quick-actions-area" v-if="currentPhase === 'waiting' && userInputHistory.length === 0">
            <div class="quick-actions-header">
              <div class="quick-header-content">
                <span class="quick-icon">🚀</span>
                <div class="quick-header-text">
                  <span class="quick-title">快速开始</span>
                  <span class="quick-subtitle">选择一个热门目的地开始您的旅程</span>
                </div>
              </div>
            </div>
            <div class="quick-actions-grid">
              <button @click="quickStart('我想去北京三日游')" class="quick-action-card beijing">
                <div class="quick-card-background"></div>
                <div class="quick-card-content">
                  <div class="quick-card-icon">🏛️</div>
                  <div class="quick-card-text">北京三日游</div>
                  <div class="quick-card-desc">历史文化之旅</div>
                  <div class="quick-card-tags">
                    <span class="tag">故宫</span>
                    <span class="tag">长城</span>
                  </div>
                </div>
                <div class="quick-card-arrow">→</div>
              </button>
              <button @click="quickStart('计划上海周末游')" class="quick-action-card shanghai">
                <div class="quick-card-background"></div>
                <div class="quick-card-content">
                  <div class="quick-card-icon">🌃</div>
                  <div class="quick-card-text">上海周末游</div>
                  <div class="quick-card-desc">都市风情体验</div>
                  <div class="quick-card-tags">
                    <span class="tag">外滩</span>
                    <span class="tag">迪士尼</span>
                  </div>
                </div>
                <div class="quick-card-arrow">→</div>
              </button>
              <button @click="quickStart('西安历史文化之旅')" class="quick-action-card xian">
                <div class="quick-card-background"></div>
                <div class="quick-card-content">
                  <div class="quick-card-icon">🏺</div>
                  <div class="quick-card-text">西安文化游</div>
                  <div class="quick-card-desc">古都历史探索</div>
                  <div class="quick-card-tags">
                    <span class="tag">兵马俑</span>
                    <span class="tag">古城墙</span>
                  </div>
                </div>
                <div class="quick-card-arrow">→</div>
              </button>
              <button @click="quickStart('成都美食之旅')" class="quick-action-card chengdu">
                <div class="quick-card-background"></div>
                <div class="quick-card-content">
                  <div class="quick-card-icon">🌶️</div>
                  <div class="quick-card-text">成都美食游</div>
                  <div class="quick-card-desc">川菜美食之旅</div>
                  <div class="quick-card-tags">
                    <span class="tag">火锅</span>
                    <span class="tag">熊猫</span>
                  </div>
                </div>
                <div class="quick-card-arrow">→</div>
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
import travelPlanningAPI from '../utils/travelPlanningAPI.js'
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
  name: 'SupervisorAgentFixed',
  setup() {
    // 核心状态管理 - 严格按照Python逻辑
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const loadingText = ref('正在处理您的请求...')
    const loadingProgress = ref(0)
    const chatContainer = ref(null)
    
    // Python逻辑对应的状态变量
    const isFirstRound = ref(true)  // 对应 is_first_round = True
    const userInputHistory = ref([])  // 对应 user_input_history = []
    const draftHistory = ref([])  // 草稿历史记录数组
    const draftIdCounter = ref(0)  // 草稿ID计数器
    const currentPhase = ref('waiting')  // 当前阶段：waiting, need_collection, planning, adjustment
    const currentRound = ref(1)  // 当前轮次
    const sessionId = ref(null)  // 会话ID
    
    // 反馈相关状态
    const showFeedbackInput = ref(false)
    const feedbackText = ref('')
    const selectedDraftForFeedback = ref(null)  // 选中用于反馈的草稿
    
    // 需求收集状态
    const needCollectionData = ref(null)
    
    // 流式输出状态 - 改为卡片数组
    const streamingCards = ref([])
    const activeStreamingId = ref(null)
    const isStreaming = ref(false)
    const streamingCardIdCounter = ref(0)

    // 草稿管理方法
    const addDraft = (content, type = 'initial') => {
      const draftId = ++draftIdCounter.value
      const newDraft = {
        id: draftId,
        content: content,
        type: type, // 'initial' 或 'optimized'
        round: currentRound.value,
        timestamp: new Date(),
        isCollapsed: false
      }
      
      console.log('📄 [草稿管理] 添加新草稿:', {
        draftId,
        type,
        round: currentRound.value,
        contentLength: content.length,
        timestamp: newDraft.timestamp.toLocaleString('zh-CN')
      })
      
      // 如果不是第一个草稿，将之前的草稿设为折叠状态（但保持可见）
      if (draftHistory.value.length > 0) {
        draftHistory.value.forEach(draft => {
          draft.isCollapsed = true
        })
        console.log(`📁 [草稿管理] 将 ${draftHistory.value.length} 个历史草稿设为折叠状态`)
      }
      
      draftHistory.value.push(newDraft)
      console.log(`📋 [草稿管理] 当前草稿总数: ${draftHistory.value.length}`)
      scrollToBottom()
      return newDraft
    }

    const toggleDraftCollapse = (draftId) => {
      const draft = draftHistory.value.find(d => d.id === draftId)
      if (draft) {
        draft.isCollapsed = !draft.isCollapsed
        console.log('👆 [草稿管理] 切换草稿折叠状态:', {
          draftId,
          round: draft.round,
          newState: draft.isCollapsed ? '折叠' : '展开'
        })
      }
    }

    const getDraftTitle = (draft) => {
      if (draft.type === 'initial') {
        return '初始旅游方案'
      } else {
        return '优化后方案'
      }
    }

    const provideFeedbackForDraft = (draft) => {
      selectedDraftForFeedback.value = draft
      showFeedbackInput.value = true
      console.log('💬 [草稿管理] 选择草稿进行反馈:', {
        draftId: draft.id,
        round: draft.round,
        type: draft.type
      })
    }

    const regeneratePlanFromDraft = async (draft) => {
      console.log('🔄 [草稿管理] 基于草稿重新生成:', {
        draftId: draft.id,
        round: draft.round,
        type: draft.type
      })
      userInput.value = `请基于第${draft.round}轮的方案重新生成一个新的方案`
      await sendMessage()
    }

    // 工具方法
    const addMessage = (role, content, type = 'text', data = null) => {
      const message = {
        role,
        content,
        type,
        data,
        timestamp: new Date()
      }
      
      console.log('📝 [消息日志] 添加新消息:', {
        role,
        type,
        contentLength: content ? content.length : 0,
        hasData: !!data,
        timestamp: message.timestamp.toLocaleString('zh-CN')
      })
      
      if (data) {
        console.log('📊 [消息数据]:', data)
      }
      
      messages.value.push(message)
      console.log(`📋 [消息统计] 当前消息总数: ${messages.value.length}`)
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
        fullContent: content,  // 保存完整内容，避免被后续短消息覆盖
        timestamp: new Date(),
        isActive: true,
        isCollapsed: false,
        autoCollapseTimer: null
      }
      
      console.log('🆕 [流式卡片] 创建新卡片:', {
        cardId,
        agentKey,
        agentName: getAgentDisplayName(agentKey),
        contentLength: content.length,
        timestamp: newCard.timestamp.toLocaleString('zh-CN')
      })
      
      // 停用之前的活跃卡片，但不自动折叠，保持展开状态让用户查看
      let deactivatedCount = 0
      streamingCards.value.forEach(card => {
        if (card.isActive) {
          card.isActive = false
          deactivatedCount++
          console.log(`⏸️ [流式卡片] 停用卡片 ${card.id} (${card.agentKey})，保持展开状态`)
          
          // 清除之前的自动折叠定时器
          if (card.autoCollapseTimer) {
            clearTimeout(card.autoCollapseTimer)
            card.autoCollapseTimer = null
          }
          
          // 不再自动折叠，让用户自己决定是否折叠
          // card.isCollapsed = false // 保持展开状态
        }
      })
      
      if (deactivatedCount > 0) {
        console.log(`📊 [流式卡片] 共停用 ${deactivatedCount} 个活跃卡片，均保持展开状态`)
      }
      
      streamingCards.value.push(newCard)
      activeStreamingId.value = cardId
      console.log(`📋 [流式卡片] 当前卡片总数: ${streamingCards.value.length}, 活跃卡片ID: ${cardId}`)
      scrollToBottom()
      return cardId
    }

    const updateStreamingCard = (cardId, content) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card) {
        const oldLength = card.content.length
        card.content = content
        
        console.log('🔄 [流式卡片] 更新卡片内容:', {
          cardId,
          agentKey: card.agentKey,
          oldLength,
          newLength: content.length,
          contentDiff: content.length - oldLength,
          timestamp: new Date().toLocaleString('zh-CN')
        })
        
        scrollToBottom()
      } else {
        console.warn(`⚠️ [流式卡片] 未找到要更新的卡片: ${cardId}`)
      }
    }

    const finishStreamingCard = (cardId) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card) {
        console.log('✅ [流式卡片] 完成卡片:', {
          cardId,
          agentKey: card.agentKey,
          finalContentLength: card.content.length,
          wasActive: card.isActive,
          timestamp: new Date().toLocaleString('zh-CN')
        })
        
        card.isActive = false
        // 清除自动折叠定时器
        if (card.autoCollapseTimer) {
          clearTimeout(card.autoCollapseTimer)
          card.autoCollapseTimer = null
          console.log(`⏰ [流式卡片] 清除自动折叠定时器: ${cardId}`)
        }
        // 最后一个卡片保持展开状态，让用户查看完整内容
        card.isCollapsed = false
        console.log(`📖 [流式卡片] 保持展开状态: ${cardId}`)
      } else {
        console.warn(`⚠️ [流式卡片] 未找到要完成的卡片: ${cardId}`)
      }
      activeStreamingId.value = null
      console.log('🎯 [流式卡片] 清除活跃卡片ID')
    }

    const toggleCardCollapse = (cardId) => {
      const card = streamingCards.value.find(c => c.id === cardId)
      if (card && !card.isActive) {
        const oldState = card.isCollapsed
        
        // 清除自动折叠定时器，用户手动操作优先
        if (card.autoCollapseTimer) {
          clearTimeout(card.autoCollapseTimer)
          card.autoCollapseTimer = null
          console.log(`⏰ [流式卡片] 用户操作清除自动折叠定时器: ${cardId}`)
        }
        
        card.isCollapsed = !card.isCollapsed
        
        console.log('👆 [流式卡片] 用户切换折叠状态:', {
          cardId,
          agentKey: card.agentKey,
          oldState: oldState ? '折叠' : '展开',
          newState: card.isCollapsed ? '折叠' : '展开',
          timestamp: new Date().toLocaleString('zh-CN')
        })
      } else if (card && card.isActive) {
        console.log(`⚠️ [流式卡片] 无法切换活跃卡片状态: ${cardId}`)
      } else {
        console.warn(`⚠️ [流式卡片] 未找到要切换的卡片: ${cardId}`)
      }
    }

    const clearStreamingCards = () => {
      // 清除所有定时器
      streamingCards.value.forEach(card => {
        if (card.autoCollapseTimer) {
          clearTimeout(card.autoCollapseTimer)
        }
      })
      streamingCards.value = []
      activeStreamingId.value = null
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    const getPhaseText = (phase) => {
      const phaseMap = {
        'waiting': '等待输入',
        'need_collection': '需求收集',
        'planning': '行程规划',
        'adjustment': '方案调整'
      }
      return phaseMap[phase] || '未知'
    }

    const getInputPlaceholder = () => {
      switch (currentPhase.value) {
        case 'waiting':
          return '请告诉我您的旅游需求，比如：我想去北京三日游...'
        case 'need_collection':
          return '请回答上面的问题，帮助我更好地了解您的需求...'
        case 'planning':
          return '正在为您规划行程，请稍候...'
        case 'adjustment':
          return '请告诉我您希望如何调整方案...'
        default:
          return '请输入您的消息...'
      }
    }

    const getSendButtonText = () => {
      switch (currentPhase.value) {
        case 'need_collection':
          return '回答'
        case 'adjustment':
          return '提交反馈'
        default:
          return '发送'
      }
    }

    const getProgressPercentage = (data) => {
      if (!data) return 0
      const confirmedCount = data.confirm_need ? data.confirm_need.length : 0
      const totalNeeded = 6 // 基于需求收集智能体的逻辑，大约需要6个核心信息
      return Math.min(Math.round((confirmedCount / totalNeeded) * 100), 100)
    }

    // 核心逻辑：实现完整的main.py对话逻辑
    const sendMessage = async () => {
      if (!userInput.value.trim() || isLoading.value) return

      const userMessage = userInput.value
      userInputHistory.value.push(userMessage)
      
      // 添加用户消息
      addMessage('user', userMessage)
      
      // 清空输入
      userInput.value = ''
      
      // 设置加载状态
      isLoading.value = true
      loadingProgress.value = 0

      try {
        if (isFirstRound.value) {
          // 第一轮：需求收集 + 直接规划
          await handleFirstRound(userMessage)
        } else {
          // 后续轮次：基于反馈优化方案
          await handleSubsequentRounds(userMessage)
        }
      } catch (error) {
        console.error('处理消息时出现错误:', error)
        addMessage('assistant', `处理请求时出现错误：${error.message}`, 'text')
      } finally {
        isLoading.value = false
        loadingProgress.value = 0
        console.log("=====规划完成=====")
      }
    }

    // 第一轮处理逻辑：需求分析 + 第一轮计划生成
    const handleFirstRound = async (userMessage) => {
      try {
        // 第一步：需求收集（不管status状态）
        currentPhase.value = 'need_collection'
        loadingText.value = '正在分析您的需求...'
        loadingProgress.value = 20
        
        // 调用需求收集API
        const needResult = await travelPlanningAPI.collectNeeds(userMessage, userInputHistory.value)
        sessionId.value = needResult.session_id
        needCollectionData.value = needResult
        
        // 显示需求收集结果
        addMessage('assistant', '', 'need_collection', needResult)
        
        loadingProgress.value = 40
        
        // 第二步：直接生成规划（不管需求收集状态）
        // 构建查询字符串
        const query = `用户需求：${userMessage}\n已确认信息：${needResult.confirm_need.join(', ')}\n请帮我规划一下行程`
        
        currentPhase.value = 'planning'
        loadingText.value = '正在生成旅游方案...'
        loadingProgress.value = 60
        
        // 调用第一轮规划API（流式）
        const planningResult = await callTravelPlanningStream(query)
        
        // 添加第一个草稿到历史记录
        addDraft(planningResult, 'initial')
        isFirstRound.value = false
        currentRound.value = 2
        currentPhase.value = 'adjustment'
        
        loadingProgress.value = 100
        
      } catch (error) {
        console.error('第一轮处理失败:', error)
        addMessage('assistant', `规划阶段出错：${error.message}`, 'text')
      }
    }

    // 后续轮次处理逻辑：基于反馈优化方案
    const handleSubsequentRounds = async (userMessage) => {
      try {
        currentPhase.value = 'adjustment'
        loadingText.value = '正在根据您的反馈优化方案...'
        loadingProgress.value = 30
        
        // 获取最新草稿作为基础
        const latestDraft = draftHistory.value[draftHistory.value.length - 1]
        const baseDraft = latestDraft ? latestDraft.content : ''
        
        // 调用后续轮优化API（流式）
        const optimizedResult = await callTravelOptimizeStream(userMessage, baseDraft)
        
        // 添加新的优化草稿到历史记录
        addDraft(optimizedResult, 'optimized')
        currentRound.value += 1
        
        loadingProgress.value = 100
        
      } catch (error) {
        console.error('后续轮处理失败:', error)
        addMessage('assistant', `方案优化阶段出错：${error.message}`, 'text')
      }
    }

    // 调用第一轮规划API（流式）
    const callTravelPlanningStream = async (userRequest) => {
      return new Promise((resolve, reject) => {
        let fullResult = ''
        let currentAgent = ''
        
        // 初始化流式状态
        clearStreamingCards()
        isStreaming.value = true
        
        travelPlanningAPI.planTravelStream(
          userRequest,
          sessionId.value,
          // onUpdate
          (updateData) => {
            console.log('📥 收到第一轮规划流式更新:', updateData)
            
            // 处理不同类型的更新数据
            if (updateData) {
              // 检查是否是开始消息
              if (updateData.message) {
                // 创建初始卡片
                createStreamingCard('supervisor', updateData.message)
                loadingText.value = updateData.message
                return
              }
              
              // 检查supervisor数据结构
              if (updateData.supervisor && updateData.supervisor.messages) {
                const messages = updateData.supervisor.messages
                
                // 查找最新的有内容的消息（跳过工具调用返回消息）
                for (let i = messages.length - 1; i >= 0; i--) {
                  const message = messages[i]
                  if (message && message.content && message.content.length > 0 && 
                      !message.content.startsWith('Successfully transferred')) {
                    
                    // 更新当前智能体信息
                    if (message.name && message.name !== currentAgent) {
                      currentAgent = message.name
                      loadingText.value = `正在调用 ${getAgentDisplayName(currentAgent)}...`
                      console.log(`🔄 切换到智能体: ${currentAgent}`)
                      
                      // 创建新的流式卡片
                      const cardId = createStreamingCard(currentAgent, message.content)
                      activeStreamingId.value = cardId
                    } else if (activeStreamingId.value) {
                      // 更新当前活跃卡片的内容
                      updateStreamingCard(activeStreamingId.value, message.content)
                    }
                    
                    fullResult = message.content
                    loadingProgress.value = Math.min(loadingProgress.value + 3, 95)
                    break
                  }
                  
                  // 检查工具调用
                  if (message && message.tool_calls && message.tool_calls.length > 0) {
                    message.tool_calls.forEach(toolCall => {
                      console.log(`🔧 工具调用: ${toolCall.name}`)
                      loadingText.value = `正在执行 ${getToolDisplayName(toolCall.name)}...`
                    })
                  }
                }
              }
              
              // 检查其他智能体的数据结构
              const agentKeys = ['tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent']
              for (const agentKey of agentKeys) {
                if (updateData[agentKey] && updateData[agentKey].messages) {
                  const messages = updateData[agentKey].messages
                  
                  // 查找最新的有实际内容的消息（排除工具调用消息）
                  for (let i = messages.length - 1; i >= 0; i--) {
                    const message = messages[i]
                    
                    // 检查消息是否有有效内容
                    if (message && message.content && message.content.length > 50 && 
                        !message.content.startsWith('Successfully transferred') &&
                        !message.content.startsWith('Transferring back') &&
                        message.content !== 'Successfully transferred back to supervisor') {
                      
                      console.log(`🎯 找到有效内容 - ${agentKey}: ${message.content.length} 字符`)
                      console.log(`📄 内容预览 - ${agentKey}:`, message.content.substring(0, 200) + (message.content.length > 200 ? '...' : ''))
                      
                      // 检查是否已经为该智能体创建了卡片
                      let existingCard = streamingCards.value.find(card => card.agentKey === agentKey)
                      
                      if (!existingCard) {
                        // 如果没有该智能体的卡片，创建新卡片
                        currentAgent = agentKey
                        loadingText.value = `正在调用 ${getAgentDisplayName(agentKey)}...`
                        
                        const cardId = createStreamingCard(agentKey, message.content)
                        // 设置完整内容
                        const newCard = streamingCards.value.find(c => c.id === cardId)
                        if (newCard) {
                          newCard.fullContent = message.content
                        }
                        activeStreamingId.value = cardId
                        console.log(`🆕 为 ${agentKey} 创建新卡片: ${cardId}，保存完整内容 ${message.content.length} 字符`)
                      } else if (existingCard.isActive) {
                        // 如果该智能体的卡片是活跃的，更新内容
                        updateStreamingCard(existingCard.id, message.content)
                        // 如果新内容更长，更新完整内容
                        if (message.content.length > existingCard.fullContent.length) {
                          existingCard.fullContent = message.content
                          console.log(`📝 更新 ${agentKey} 完整内容: ${message.content.length} 字符`)
                        }
                        console.log(`🔄 更新 ${agentKey} 卡片内容: ${message.content.length} 字符`)
                      } else {
                        // 如果该智能体的卡片已经完成，重新激活它，但不折叠其他卡片
                        existingCard.isActive = true
                        existingCard.isCollapsed = false
                        existingCard.content = message.content
                        // 如果新内容更长，更新完整内容
                        if (message.content.length > existingCard.fullContent.length) {
                          existingCard.fullContent = message.content
                          console.log(`📝 重新激活时更新 ${agentKey} 完整内容: ${message.content.length} 字符`)
                        }
                        activeStreamingId.value = existingCard.id
                        console.log(`🔄 重新激活 ${agentKey} 卡片，保持其他卡片展开`)
                      }
                      
                      // 不要覆盖fullResult，保持最终结果
                      if (message.content.length > (fullResult?.length || 0)) {
                        fullResult = message.content
                      }
                      loadingProgress.value = Math.min(loadingProgress.value + 5, 95)
                      break
                    }
                  }
                  
                  // 如果找到了有效内容，跳出外层循环
                  if (fullResult && fullResult.length > 50) {
                    break
                  }
                }
              }
            }
          },
          // onComplete
          (completeData) => {
            console.log('✅ 第一轮规划完成:', completeData)
            
            // 从完成数据中提取最终结果
            if (completeData && completeData.data && completeData.data.draft) {
              fullResult = completeData.data.draft
            }
            
            // 完成最后一个活跃卡片
            if (activeStreamingId.value) {
              finishStreamingCard(activeStreamingId.value)
            }
            
            // 清理流式状态
            isStreaming.value = false
            resolve(fullResult || '规划完成，但未收到具体内容')
          },
          // onError
          (error) => {
            console.error('❌ 第一轮规划失败:', error)
            // 清理流式状态
            clearStreamingCards()
            isStreaming.value = false
            reject(error)
          }
        )
      })
    }

    // 调用后续轮优化API（流式）
    const callTravelOptimizeStream = async (userFeedback, draft) => {
      return new Promise((resolve, reject) => {
        let fullResult = ''
        let currentAgent = ''
        
        // 初始化流式状态
        clearStreamingCards()
        isStreaming.value = true
        
        travelPlanningAPI.optimizeTravelStream(
          userFeedback,
          draft,
          // onUpdate
          (updateData) => {
            console.log('📥 收到优化流式更新:', updateData)
            
            // 处理不同类型的更新数据
            if (updateData) {
              // 检查是否是开始消息
              if (updateData.message) {
                // 创建初始卡片
                createStreamingCard('supervisor', updateData.message)
                loadingText.value = updateData.message
                return
              }
              
              // 检查supervisor数据结构
              if (updateData.supervisor && updateData.supervisor.messages) {
                const messages = updateData.supervisor.messages
                
                // 查找最新的有内容的消息（跳过工具调用返回消息）- 与第一轮规划保持一致
                for (let i = messages.length - 1; i >= 0; i--) {
                  const message = messages[i]
                  if (message && message.content && message.content.length > 0 && 
                      !message.content.startsWith('Successfully transferred')) {
                    
                    // 更新当前智能体信息
                    if (message.name && message.name !== currentAgent) {
                      currentAgent = message.name
                      loadingText.value = `正在调用 ${getAgentDisplayName(currentAgent)}...`
                      console.log(`🔄 切换到智能体: ${currentAgent}`)
                      
                      // 创建新的流式卡片
                      const cardId = createStreamingCard(currentAgent, message.content)
                      activeStreamingId.value = cardId
                    } else if (activeStreamingId.value) {
                      // 更新当前活跃卡片的内容
                      updateStreamingCard(activeStreamingId.value, message.content)
                    }
                    
                    fullResult = message.content
                    loadingProgress.value = Math.min(loadingProgress.value + 3, 95)
                    break
                  }
                  
                  // 检查工具调用
                  if (message && message.tool_calls && message.tool_calls.length > 0) {
                    message.tool_calls.forEach(toolCall => {
                      console.log(`🔧 工具调用: ${toolCall.name}`)
                      loadingText.value = `正在执行 ${getToolDisplayName(toolCall.name)}...`
                    })
                  }
                }
              }
              
              // 检查其他智能体的数据结构 - 与第一轮规划保持一致的逻辑
              const agentKeys = ['tour_search_agent', 'day_plan_agent', 'live_transport_agent', 'travel_butler_agent']
              for (const agentKey of agentKeys) {
                if (updateData[agentKey] && updateData[agentKey].messages) {
                  const messages = updateData[agentKey].messages
                  
                  // 查找最新的有实际内容的消息（排除工具调用消息）
                  for (let i = messages.length - 1; i >= 0; i--) {
                    const message = messages[i]
                    
                    // 检查消息是否有有效内容 - 与第一轮规划保持一致的过滤条件
                    if (message && message.content && message.content.length > 50 && 
                        !message.content.startsWith('Successfully transferred') &&
                        !message.content.startsWith('Transferring back') &&
                        message.content !== 'Successfully transferred back to supervisor') {
                      
                      console.log(`🎯 找到有效内容 - ${agentKey}: ${message.content.length} 字符`)
                      console.log(`📄 内容预览 - ${agentKey}:`, message.content.substring(0, 200) + (message.content.length > 200 ? '...' : ''))
                      
                      // 检查是否已经为该智能体创建了卡片
                      let existingCard = streamingCards.value.find(card => card.agentKey === agentKey)
                      
                      if (!existingCard) {
                        // 如果没有该智能体的卡片，创建新卡片
                        currentAgent = agentKey
                        loadingText.value = `正在调用 ${getAgentDisplayName(agentKey)}...`
                        
                        const cardId = createStreamingCard(agentKey, message.content)
                        // 设置完整内容
                        const newCard = streamingCards.value.find(c => c.id === cardId)
                        if (newCard) {
                          newCard.fullContent = message.content
                        }
                        activeStreamingId.value = cardId
                        console.log(`🆕 为 ${agentKey} 创建新卡片: ${cardId}，保存完整内容 ${message.content.length} 字符`)
                      } else if (existingCard.isActive) {
                        // 如果该智能体的卡片是活跃的，更新内容
                        updateStreamingCard(existingCard.id, message.content)
                        // 如果新内容更长，更新完整内容
                        if (message.content.length > existingCard.fullContent.length) {
                          existingCard.fullContent = message.content
                          console.log(`📝 更新 ${agentKey} 完整内容: ${message.content.length} 字符`)
                        }
                        console.log(`🔄 更新 ${agentKey} 卡片内容: ${message.content.length} 字符`)
                      } else {
                        // 如果该智能体的卡片已经完成，重新激活它，但不折叠其他卡片
                        existingCard.isActive = true
                        existingCard.isCollapsed = false
                        existingCard.content = message.content
                        // 如果新内容更长，更新完整内容
                        if (message.content.length > existingCard.fullContent.length) {
                          existingCard.fullContent = message.content
                          console.log(`📝 重新激活时更新 ${agentKey} 完整内容: ${message.content.length} 字符`)
                        }
                        activeStreamingId.value = existingCard.id
                        console.log(`🔄 重新激活 ${agentKey} 卡片，保持其他卡片展开`)
                      }
                      
                      // 不要覆盖fullResult，保持最终结果
                      if (message.content.length > (fullResult?.length || 0)) {
                        fullResult = message.content
                      }
                      loadingProgress.value = Math.min(loadingProgress.value + 5, 95)
                      break
                    }
                  }
                  
                  // 如果找到了有效内容，跳出外层循环
                  if (fullResult && fullResult.length > 50) {
                    break
                  }
                }
              }
            }
          },
          // onComplete
          (completeData) => {
            console.log('✅ 方案优化完成:', completeData)
            
            // 从完成数据中提取最终结果
            if (completeData && completeData.data && completeData.data.new_draft) {
              fullResult = completeData.data.new_draft
            }
            
            // 完成最后一个活跃卡片
            if (activeStreamingId.value) {
              finishStreamingCard(activeStreamingId.value)
            }
            
            // 清理流式状态
            isStreaming.value = false
            resolve(fullResult || '优化完成，但未收到具体内容')
          },
          // onError
          (error) => {
            console.error('❌ 方案优化失败:', error)
            // 清理流式状态
            clearStreamingCards()
            isStreaming.value = false
            reject(error)
          }
        )
      })
    }

    // 反馈相关方法
    const addSuggestion = (suggestion) => {
      if (feedbackText.value) {
        feedbackText.value += '\n' + suggestion
      } else {
        feedbackText.value = suggestion
      }
    }

    const submitFeedback = async () => {
      if (!feedbackText.value.trim()) return
      
      const feedback = feedbackText.value
      feedbackText.value = ''
      showFeedbackInput.value = false
      
      // 将反馈作为用户输入处理
      userInput.value = feedback
      await sendMessage()
    }

    // 方案操作方法
    const regeneratePlan = async () => {
      userInput.value = '请重新生成一个方案'
      await sendMessage()
    }

    const acceptPlan = () => {
      addMessage('assistant', '🎉 太好了！您的旅游方案已确认。祝您旅途愉快！如果需要进一步调整，随时告诉我。', 'text')
      currentPhase.value = 'waiting'
    }

    // 快捷操作
    const quickStart = (message) => {
      userInput.value = message
      sendMessage()
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
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    }

    const formatPlanningContent = (content) => {
      if (!content) return ''
      return renderMarkdown(content)
    }

    // 格式化流式内容 - 使用 markdown 渲染
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

    // 获取智能体表情符号
    const getAgentEmoji = (agentKey) => {
      const emojiMap = {
        'supervisor': '🎯',
        'tour_search_agent': '🔍',
        'day_plan_agent': '📅',
        'live_transport_agent': '🚗',
        'travel_butler_agent': '🎒',
        'final_plan': '🌟'
      }
      return emojiMap[agentKey] || '🤖'
    }

    // 获取内容长度
    const getContentLength = (content) => {
      if (!content) return 0
      // 移除HTML标签计算纯文本长度
      const textContent = content.replace(/<[^>]*>/g, '')
      return textContent.length
    }

    // 新增UI状态
    const isInputFocused = ref(false)

    // 新增UI方法
    const getPhaseIcon = (phase) => {
      const iconMap = {
        'waiting': '⏳',
        'need_collection': '📝',
        'planning': '🎯',
        'adjustment': '🔧'
      }
      return iconMap[phase] || '❓'
    }

    const getPhaseSubtitle = (phase) => {
      const subtitleMap = {
        'waiting': '准备开始您的旅程',
        'need_collection': '了解您的具体需求',
        'planning': '智能规划行程方案',
        'adjustment': '根据反馈优化方案'
      }
      return subtitleMap[phase] || ''
    }

    // 生命周期
    onMounted(() => {
      addMessage('assistant', '您好！我是您的智能旅游规划助手。我会通过友好的对话了解您的需求，然后为您制定详细的个性化旅游方案。请告诉我您的旅游想法吧！', 'text')
      scrollToBottom()
    })

    return {
      // 数据
      messages,
      userInput,
      isLoading,
      loadingText,
      loadingProgress,
      chatContainer,
      isFirstRound,
      userInputHistory,
      draftHistory,
      draftIdCounter,
      currentPhase,
      currentRound,
      sessionId,
      showFeedbackInput,
      feedbackText,
      selectedDraftForFeedback,
      needCollectionData,
      streamingCards,
      activeStreamingId,
      isStreaming,
      isInputFocused,
      
      // 草稿管理方法
      addDraft,
      toggleDraftCollapse,
      getDraftTitle,
      provideFeedbackForDraft,
      regeneratePlanFromDraft,
      
      // 流式卡片方法
      toggleCardCollapse,
      createStreamingCard,
      updateStreamingCard,
      finishStreamingCard,
      clearStreamingCards,
      
      // 核心方法
      sendMessage,
      handleKeyDown,
      getPhaseText,
      getPhaseIcon,
      getPhaseSubtitle,
      getInputPlaceholder,
      getSendButtonText,
      getProgressPercentage,
      addSuggestion,
      submitFeedback,
      regeneratePlan,
      acceptPlan,
      quickStart,
      formatTime,
      formatMessageContent,
      formatPlanningContent,
      formatStreamingContent,
      getAgentDisplayName,
      getToolDisplayName,
      getAgentEmoji,
      getContentLength
    }
  }
}
</script>

<style scoped>
.supervisor-agent-container {
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
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
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
  padding-bottom: 80px;
  position: relative;
  z-index: 1;
  min-height: 0;
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

/* 需求收集样式 */
.need-collection-message {
  border-left: 4px solid #4299e1;
  padding-left: 20px;
}

.collection-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.collection-status {
  padding: 3px 10px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 500;
}

.collection-status.continue {
  background: #fed7d7;
  color: #c53030;
}

.collection-status.end {
  background: #c6f6d5;
  color: #2f855a;
}

.confirmed-needs, .pending-needs {
  margin-bottom: 20px;
}

.confirmed-needs h4, .pending-needs h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #4a5568;
}

.need-item {
  margin-bottom: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  list-style: none;
  font-size: 13px;
}

.need-item.confirmed {
  background: #c6f6d5;
  color: #2f855a;
}

.need-item.pending {
  background: #feebc8;
  color: #c05621;
}


/* 草稿历史记录样式 */
.draft-history-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.draft-item-wrapper {
  animation: fadeInUp 0.4s ease-out;
}

/* 规划结果样式 */
.planning-result {
  border-left: 4px solid #48bb78;
  padding-left: 20px;
  transition: all 0.3s ease;
}

.planning-result.latest-draft {
  border-left-color: #4299e1;
  background: rgba(66, 153, 225, 0.02);
}

.planning-result.collapsed-draft .planning-content-wrapper {
  max-height: 0;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.planning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 0;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.planning-header:hover {
  background-color: rgba(72, 187, 120, 0.05);
}

.planning-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.planning-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.planning-round {
  padding: 3px 10px;
  background: #e6fffa;
  color: #2f855a;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 500;
}

.latest-badge {
  padding: 2px 8px;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.planning-time {
  font-size: 11px;
  color: #a0aec0;
}

.planning-content-wrapper {
  max-height: none;
  overflow: visible;
  transition: all 0.3s ease;
}

.planning-content-wrapper.collapsed {
  max-height: 0;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.planning-content {
  line-height: 1.5;
  margin-bottom: 16px;
  font-size: 14px;
}

.planning-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.action-btn {
  padding: 8px 14px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn.primary {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
}

.action-btn.secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.action-btn.success {
  background: linear-gradient(45deg, #48bb78, #38a169);
  color: white;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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

.streaming-card-content.collapsed {
  max-height: 0;
  overflow: hidden;
  padding: 0;
}

.streaming-content {
  line-height: 1.5;
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

/* 旧的流式输出样式（保留兼容性） */
.streaming-message {
  margin-bottom: 20px;
  animation: fadeInUp 0.4s ease-out;
}

.streaming-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

/* 加载样式 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-progress {
  margin-top: 15px;
}

.loading-text {
  color: #718096;
  font-size: 13px;
}

/* 反馈模态框样式 */
.feedback-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.feedback-modal {
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.feedback-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #a0aec0;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f7fafc;
  color: #4a5568;
}

.feedback-textarea {
  width: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.feedback-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.feedback-suggestions {
  margin-top: 20px;
}

.feedback-suggestions h4 {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-size: 14px;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tag {
  padding: 5px 10px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 12px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-tag:hover {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
}

.feedback-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 25px;
}

/* 美化后的输入区域样式 */
.input-container {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
  backdrop-filter: blur(20px);
  padding: 12px 16px;
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.12);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 10;
}

.input-main-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 美化后的状态信息栏 */
.status-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.status-info-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-info-right {
  display: flex;
  align-items: center;
}

.phase-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.phase-dot-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phase-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.phase-dot.waiting {
  background: linear-gradient(45deg, #e2e8f0, #cbd5e0);
  animation: pulse 2s ease-in-out infinite;
}

.phase-dot.need_collection {
  background: linear-gradient(45deg, #fed7d7, #fbb6ce);
  animation: pulse 2s ease-in-out infinite;
}

.phase-dot.planning {
  background: linear-gradient(45deg, #bee3f8, #90cdf4);
  animation: pulse 2s ease-in-out infinite;
}

.phase-dot.adjustment {
  background: linear-gradient(45deg, #c6f6d5, #9ae6b4);
  animation: pulse 2s ease-in-out infinite;
}

.phase-dot-inner {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite alternate;
}

.phase-icon {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: 12px;
  background: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.phase-text-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.phase-text {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.phase-subtitle {
  font-size: 11px;
  color: #718096;
  font-weight: 400;
}

.round-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.round-circle {
  width: 32px;
  height: 32px;
  background: linear-gradient(45deg, #4299e1, #3182ce);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

.round-number {
  color: white;
  font-size: 14px;
  font-weight: 700;
}

.round-label {
  font-size: 12px;
  color: #718096;
  font-weight: 500;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.session-icon {
  font-size: 14px;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.session-label {
  font-size: 10px;
  color: #718096;
  font-weight: 500;
}

.session-id {
  font-size: 11px;
  color: #4a5568;
  font-weight: 600;
  font-family: monospace;
}

/* 美化后的主输入框区域 */
.input-main-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-box-container {
  position: relative;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-radius: 16px;
  padding: 8px 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.input-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.input-box.input-focused {
  border-color: #4299e1;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.2), 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-2px);
}

.input-box.input-focused::before {
  opacity: 1;
}

.input-box.input-loading {
  border-color: #48bb78;
  box-shadow: 0 8px 32px rgba(72, 187, 120, 0.2);
}

.input-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(45deg, #f7fafc, #edf2f7);
  border-radius: 50%;
  font-size: 16px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.input-box.input-focused .input-icon {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  transform: scale(1.1);
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
  max-height: 80px;
  font-family: inherit;
  padding: 4px 0;
}

.input-textarea::placeholder {
  color: #a0aec0;
  font-style: italic;
}

.send-button {
  background: linear-gradient(45deg, #cbd5e0, #a0aec0);
  color: #718096;
  border: none;
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
  min-height: 32px;
}

.send-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.send-button.send-ready {
  background: linear-gradient(45deg, #4299e1, #3182ce);
  color: white;
  box-shadow: 0 4px 16px rgba(66, 153, 225, 0.3);
  transform: scale(1.02);
}

.send-button.send-ready:hover:not(:disabled) {
  background: linear-gradient(45deg, #3182ce, #2c5aa0);
  transform: scale(1.05) translateY(-1px);
  box-shadow: 0 8px 24px rgba(66, 153, 225, 0.4);
}

.send-button.send-ready:hover::before {
  left: 100%;
}

.send-button:disabled {
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-icon {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.send-button.send-ready .send-icon {
  animation: bounce 2s ease-in-out infinite;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 压缩后的快捷操作区域 */
.quick-actions-area {
  animation: fadeInUp 0.6s ease-out;
}

.quick-actions-header {
  margin-bottom: 12px;
}

.quick-header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-icon {
  font-size: 18px;
  animation: bounce 2s ease-in-out infinite;
}

.quick-header-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.quick-title {
  font-size: 14px;
  font-weight: 700;
  color: #2d3748;
  background: linear-gradient(45deg, #4299e1, #48bb78);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.quick-subtitle {
  font-size: 11px;
  color: #718096;
  font-weight: 400;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.quick-action-card {
  position: relative;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.4s ease;
  overflow: hidden;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.quick-action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.quick-action-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: #4299e1;
}

.quick-action-card:hover::before {
  opacity: 1;
}

.quick-action-card.beijing:hover {
  border-color: #e53e3e;
  box-shadow: 0 12px 40px rgba(229, 62, 62, 0.2);
}

.quick-action-card.shanghai:hover {
  border-color: #3182ce;
  box-shadow: 0 12px 40px rgba(49, 130, 206, 0.2);
}

.quick-action-card.xian:hover {
  border-color: #d69e2e;
  box-shadow: 0 12px 40px rgba(214, 158, 46, 0.2);
}

.quick-action-card.chengdu:hover {
  border-color: #38a169;
  box-shadow: 0 12px 40px rgba(56, 161, 105, 0.2);
}

.quick-card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.quick-action-card.beijing .quick-card-background {
  background: linear-gradient(135deg, rgba(229, 62, 62, 0.1) 0%, rgba(245, 101, 101, 0.05) 100%);
}

.quick-action-card.shanghai .quick-card-background {
  background: linear-gradient(135deg, rgba(49, 130, 206, 0.1) 0%, rgba(66, 153, 225, 0.05) 100%);
}

.quick-action-card.xian .quick-card-background {
  background: linear-gradient(135deg, rgba(214, 158, 46, 0.1) 0%, rgba(236, 201, 75, 0.05) 100%);
}

.quick-action-card.chengdu .quick-card-background {
  background: linear-gradient(135deg, rgba(56, 161, 105, 0.1) 0%, rgba(72, 187, 120, 0.05) 100%);
}

.quick-action-card:hover .quick-card-background {
  opacity: 1;
}

.quick-card-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.quick-card-icon {
  font-size: 24px;
  margin-bottom: 4px;
  transition: transform 0.3s ease;
}

.quick-action-card:hover .quick-card-icon {
  transform: scale(1.1) rotate(5deg);
}

.quick-card-text {
  font-size: 14px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 2px;
}

.quick-card-desc {
  font-size: 11px;
  color: #718096;
  margin-bottom: 6px;
  line-height: 1.3;
}

.quick-card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  padding: 2px 6px;
  background: rgba(66, 153, 225, 0.1);
  color: #3182ce;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
  border: 1px solid rgba(66, 153, 225, 0.2);
  transition: all 0.3s ease;
}

.quick-action-card:hover .tag {
  background: rgba(66, 153, 225, 0.2);
  transform: translateY(-1px);
}

.quick-card-arrow {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 14px;
  color: #a0aec0;
  transition: all 0.3s ease;
  z-index: 3;
}

.quick-action-card:hover .quick-card-arrow {
  color: #4299e1;
  transform: translateX(2px);
}

/* 动画增强 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

/* 动画效果 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
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
    transform: scale(1.1);
  }
}

/* Markdown样式增强 - 针对 planning-content */
.planning-content h1,
.planning-content h2,
.planning-content h3,
.planning-content h4,
.planning-content h5,
.planning-content h6 {
  color: #2d3748;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.planning-content h1 {
  font-size: 18px;
  border-bottom: 2px solid #48bb78;
  padding-bottom: 4px;
}

.planning-content h2 {
  font-size: 16px;
  color: #4a5568;
}

.planning-content h3 {
  font-size: 15px;
  color: #718096;
}

.planning-content h4 {
  font-size: 14px;
  color: #718096;
}

.planning-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.planning-content ul,
.planning-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.planning-content li {
  margin: 4px 0;
  line-height: 1.5;
}

.planning-content strong {
  color: #2d3748;
  font-weight: 600;
}

.planning-content em {
  color: #4a5568;
  font-style: italic;
}

.planning-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.planning-content pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border-left: 3px solid #48bb78;
}

.planning-content pre code {
  background: none;
  padding: 0;
}

.planning-content blockquote {
  border-left: 4px solid #e2e8f0;
  padding-left: 16px;
  margin: 12px 0;
  color: #718096;
  font-style: italic;
}

.planning-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.planning-content th,
.planning-content td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.planning-content th {
  background: rgba(72, 187, 120, 0.1);
  font-weight: 600;
}

.planning-content a {
  color: #48bb78;
  text-decoration: none;
}

.planning-content a:hover {
  text-decoration: underline;
}

.planning-content hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 8px;
}

.chat-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
