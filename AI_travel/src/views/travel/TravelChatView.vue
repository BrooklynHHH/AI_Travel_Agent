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
          <div v-else class="message-group">
            <!-- 助手消息 -->
            <div class="message assistant-message">
              <div class="message-avatar assistant-avatar">🤖</div>
              <div class="message-content">
                <!-- 消息头部 -->
                <div class="message-header" v-if="message.isStreaming">
                  <span class="assistant-label">助手</span>
                  <span class="streaming-indicator">
                    <span class="pulse-dot"></span>
                    正在生成中...
                  </span>
                </div>

                <!-- 进度指示器 (仅在流式生成时显示) -->
                <div v-if="message.isStreaming && message.progress.length > 0" class="progress-section">
                  <div class="progress-title">处理进度:</div>
                  <div class="progress-steps">
                    <div 
                      v-for="step in message.progress" 
                      :key="step.name" 
                      class="progress-step"
                      :class="step.status"
                    >
                      <span class="step-icon">{{ step.icon }}</span>
                      <span class="step-name">{{ step.name }}</span>
                      <span class="step-status">
                        <span v-if="step.status === 'completed'" class="status-completed">✅</span>
                        <span v-else-if="step.status === 'processing'" class="status-processing">⚡</span>
                        <span v-else class="status-waiting">⏳</span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 消息内容 -->
                <div class="text-message">
                  <!-- 如果正在打字或有显示内容，显示打字机效果的内容 -->
                  <div class="message-text" v-html="formatMessageContent(message.displayedContent || message.content)" v-if="message.displayedContent || message.content"></div>
                  <!-- 打字机光标效果 -->
                  <span v-if="message.isTyping" class="typing-cursor">|</span>
                </div>
                
                <!-- 消息时间 -->
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

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
import { onMounted } from 'vue'
import { useTravelChat } from './useTravelChat.js'

export default {
  name: 'TravelChatView',
  setup() {
    // 使用 composable 获取所有状态和方法
    const {
      // 数据
      messages,
      userInput,
      isLoading,
      loadingText,
      sessionId,
      isInputFocused,
      messagesContainer,
      inputField,
      chatContainer,
      hasStreamingMessage,
      currentProcessingStatus,
      currentAgentStatus,
      activeAgentInfo,
      processingSteps,
      currentStepIndex,
      
      // 方法
      formatTime,
      formatMessageContent,
      sendMessage,
      handleKeyDown,
      quickStart,
      resetConversation,
      scrollToBottom,
      initializeChat
    } = useTravelChat()

    // 组件挂载时初始化
    onMounted(() => {
      initializeChat()
    })

    // 返回模板需要的所有数据和方法
    return {
      // 数据
      messages,
      userInput,
      isLoading,
      loadingText,
      sessionId,
      isInputFocused,
      messagesContainer,
      inputField,
      chatContainer,
      hasStreamingMessage,
      currentProcessingStatus,
      currentAgentStatus,
      activeAgentInfo,
      processingSteps,
      currentStepIndex,
      
      // 方法
      formatTime,
      formatMessageContent,
      sendMessage,
      handleKeyDown,
      quickStart,
      resetConversation,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
@import './travel-chat-styles.css';
</style>
