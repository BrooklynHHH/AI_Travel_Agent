<template>
  <div class="chat-container">
    <!-- Product floating window -->
    <div v-if="showProductWindow" class="product-window" @click="closeProductWindow">
      <div 
        class="product-window-content" 
        :class="{ 'fullscreen': isFullscreen }" 
        :style="{ height: windowHeight + '%' }"
        @click.stop
      >
        <div class="product-window-header">
          <h3>{{ productPageTitle }}</h3>
          <div class="drag-handle" 
            @mousedown="startDrag" 
            @touchstart="startDrag"
          >
            <span class="drag-icon">≡</span>
          </div>
          <div class="header-buttons">
            <button class="expand-button" @click="toggleFullscreen">{{ isFullscreen ? '▼' : '▲' }}</button>
            <button class="close-button" @click="closeProductWindow">×</button>
          </div>
        </div>
        <div class="product-window-body">
          <iframe v-if="productUrl" :src="productUrl" class="product-iframe" frameborder="0"></iframe>
          <p v-else class="product-name">{{ productName }}</p>
        </div>
      </div>
    </div>
    <!-- Mobile header -->
    <div class="mobile-header">
      <div class="status-bar">
        <div class="time">{{ currentTime }}</div>
        <div class="status-icons">
          <span class="signal">●●●●</span>
          <span class="wifi">●</span>
          <span class="battery">●</span>
        </div>
      </div>
      <div class="chat-header">
        <div class="back-button" @click="goBack">
          <i class="back-icon">←</i>
        </div>
        <div class="spacer"></div>
        <div class="add-button">
          <i class="add-icon">+</i>
        </div>
      </div>
    </div>

    <!-- Chat content -->
    <div class="chat-content" ref="chatContent">
      <!-- Quick action buttons -->
      <div class="quick-actions">
        <button 
          v-for="(action, index) in quickActions" 
          :key="index"
          class="quick-action-button"
          @click="handleQuickAction(action)"
        >
          {{ action }}
        </button>
      </div>
      
      <!-- Messages -->
      <div v-for="(message, index) in messages" :key="index">
        <!-- User message -->
        <div v-if="message.role === 'user'" class="message-container user-message">
          <div class="message-bubble">
            {{ message.content }}
          </div>
        </div>

        <!-- Bot message -->
        <template v-else-if="message.role === 'assistant'">
          <!-- Main response -->
          <div class="message-container bot-message">
            <div class="mi-logo">
              <div class="mi-logo-text">MI</div>
            </div>
            <div class="message-bubble main-response">
              <div v-if="message.streaming" class="response-text">
                <div v-html="renderMarkdown(message.content)"></div><span class="cursor">|</span>
              </div>
              <div v-else class="response-text" v-html="renderMarkdown(message.content)"></div>
              
              <!-- Follow-up question section -->
              <div v-if="message.followUpQuestion" class="follow-up-question">
                <p class="question-text">{{ message.followUpQuestion.question }}</p>
                <div class="option-buttons">
                  <button 
                    v-for="(option, index) in message.followUpQuestion.options" 
                    :key="index" 
                    class="option-button"
                    @click="sendFollowUpResponse(option)"
                  >
                    {{ option }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Progress bar (visible when loading or streaming) -->
      <div v-if="isLoading || isStreaming" class="progress-container">
        <div class="progress-bar"></div>
      </div>
      
      <!-- Small padding at bottom to ensure some space after last message -->
      <div style="height: 20px"></div>
    </div>

    <!-- Input area -->
    <div class="chat-input">
      <div class="input-container">
        <div class="plus-button">
          <i class="plus-icon">+</i>
        </div>
        <input 
          type="text" 
          placeholder="输入你想问的问题" 
          v-model="userInput"
          @keyup.enter="sendMessage"
        />
        <div class="voice-button" @click="sendMessage">
          <i class="send-icon">↑</i>
        </div>
      </div>
      
      <div class="bottom-toolbar">
        <div class="toolbar-item">
          <i class="depth-icon">🔍</i>
          <span>深度思考</span>
        </div>
        <div class="toolbar-item">
          <i class="web-icon">🌐</i>
          <span>联网搜索</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import { handleStreamingResponse, safeJsonParse } from '../utils/streamUtils';

import appConfig from '../config/app.config';

// Quick action buttons - loaded from config
const quickActions = ref(appConfig.quickActionButtons);

// Handler for quick action buttons
const handleQuickAction = (actionText) => {
  // Set the input value to the action text
  userInput.value = actionText;
  // Send the message
  sendMessage();
};

// Product window state
const showProductWindow = ref(false);
const productName = ref('');
const productUrl = ref('');
const isFullscreen = ref(false);
const windowHeight = ref(50); // Default height is 50%
const isDragging = ref(false);
const dragStartY = ref(0);
const dragStartHeight = ref(0);

// Computed property for the product window title
const productPageTitle = computed(() => {
  if (productUrl.value) {
    // Extract domain name for URLs
    try {
      const url = new URL(productUrl.value);
      return url.hostname.replace('www.', '') || '外部链接';
    } catch (e) {
      // If it's not a proper URL, show the URL as is or default text
      return productName.value || '页面内容';
    }
  }
  return productName.value || '页面内容';
});

// Drag functionality
const startDrag = (event) => {
  event.preventDefault();
  isDragging.value = true;
  
  // Get starting position
  if (event.type === 'mousedown') {
    dragStartY.value = event.clientY;
  } else if (event.type === 'touchstart') {
    dragStartY.value = event.touches[0].clientY;
  }
  
  // Store current height
  dragStartHeight.value = windowHeight.value;
  
  // Add event listeners for move and end
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('touchmove', handleDrag, { passive: false });
  document.addEventListener('mouseup', endDrag);
  document.addEventListener('touchend', endDrag);
};

const handleDrag = (event) => {
  if (!isDragging.value) return;
  
  // Prevent default touch behavior
  if (event.type === 'touchmove') {
    event.preventDefault();
  }
  
  // Calculate movement
  let currentY;
  if (event.type === 'mousemove') {
    currentY = event.clientY;
  } else if (event.type === 'touchmove') {
    currentY = event.touches[0].clientY;
  }
  
  // Calculate new height based on drag direction
  // Moving up = increase height, moving down = decrease height
  const deltaY = dragStartY.value - currentY;
  
  // Use window height for precise calculation
  const windowHeight_px = document.documentElement.clientHeight;
  
  // Increase sensitivity for downward movement (negative deltaY)
  const sensitivityFactor = deltaY < 0 ? 1.5 : 1.0; // Increase sensitivity for downward movement
  const adjustedDeltaY = deltaY * sensitivityFactor;
  
  // Convert to percentage of viewport height
  const deltaPercent = (adjustedDeltaY / windowHeight_px) * 100;
  const newHeight = dragStartHeight.value + deltaPercent;
  
  // Set limits - minimum 30%, maximum 100%
  windowHeight.value = Math.min(Math.max(newHeight, 30), 100);
  
  // Update fullscreen state based on window height
  isFullscreen.value = windowHeight.value >= 95;
  
  // Immediate update to make dragging feel more responsive
  nextTick(() => {
    // Force browser to repaint, making the drag feel more responsive
    window.requestAnimationFrame(() => {});
  });
};

const endDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('touchmove', handleDrag);
  document.removeEventListener('mouseup', endDrag);
  document.removeEventListener('touchend', endDrag);
};

// Function to close product window
const closeProductWindow = () => {
  showProductWindow.value = false;
  productUrl.value = '';
  isFullscreen.value = false;
};

// Function to toggle fullscreen mode
const toggleFullscreen = (event) => {
  event.stopPropagation();
  isFullscreen.value = !isFullscreen.value;
  
  // Also update window height to match fullscreen state
  if (isFullscreen.value) {
    windowHeight.value = 100; // Full height when fullscreen
  } else {
    windowHeight.value = 50; // Default height when not fullscreen
  }
};

// Initialize markdown-it renderer with custom link rendering
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
});

// Process custom product format before rendering markdown
const processCustomProductFormat = (content) => {
  // Find patterns like <小米15>(aisearch://product/{原有链接})
  const regex = /<([^>]+)>\(aisearch:\/\/product\/([^)]+)\)/g;
  
  // Replace with markdown link syntax [小米15](aisearch://product/{原有链接})
  return content.replace(regex, '[$1](aisearch://product/$2)');
};

// Add a custom attribute to links to identify them
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx];
  const href = token.attrGet('href');
  
  // Check if link starts with aisearch://
  if (href && href.startsWith('aisearch://')) {
    // Add styling class for all aisearch links
    token.attrPush(['class', 'special-link']);
    
    // Check if it's a product link
    if (href.startsWith('aisearch://product/')) {
      const productPath = href.substring('aisearch://product/'.length);
      token.attrPush(['data-product-url', productPath]);
      token.attrPush(['data-product', productPath]);
    } 
    // Check if it's a jump link (to external URL)
    else if (href.startsWith('aisearch://jump/')) {
      const jumpUrl = href.substring('aisearch://jump/'.length);
      token.attrPush(['data-jump-url', jumpUrl]);
    }
    else {
      token.attrPush(['data-product', href.substring('aisearch://'.length)]);
    }
  } else {
    // For regular links, open in new tab
    token.attrPush(['target', '_blank']);
    token.attrPush(['rel', 'noopener noreferrer']);
  }
  
  return self.renderToken(tokens, idx, options);
};

// Function to handle click on rendered content
const handleContentClick = (event) => {
  // Check if clicked element is an aisearch link (with the special-link class)
  if (event.target.tagName === 'A' && event.target.classList.contains('special-link')) {
    event.preventDefault();
    
    // Check if it's a jump link (to external URL)
    const jumpUrl = event.target.getAttribute('data-jump-url');
    if (jumpUrl) {
      // Extract the URL and use it in the floating window
      productName.value = '外部链接';  // Set a generic title for the header
      productUrl.value = jumpUrl;
      showProductWindow.value = true;
    }
    // Check if it has a product URL
    else if (event.target.hasAttribute('data-product-url')) {
      const productUrlAttr = event.target.getAttribute('data-product-url');
      productName.value = productUrlAttr;
      productUrl.value = productUrlAttr;
      showProductWindow.value = true;
    } else {
      // Handle regular aisearch links
      const product = event.target.getAttribute('data-product');
      if (product) {
        productName.value = product;
        productUrl.value = '';
        showProductWindow.value = true;
      }
    }
  }
};

// Data
const currentTime = ref('');
const userInput = ref('');
const chatContent = ref(null);
const isLoading = ref(false);
const streamingMessage = ref('');
const streamingMessageFollowUp = ref(null);
const conversationId = ref('');
const isStreaming = ref(false);

// Store messages
const messages = ref([]);

// Markdown renderer function
const renderMarkdown = (content) => {
  if (!content) return '';
  // Process the custom product format before rendering markdown
  const processedContent = processCustomProductFormat(content);
  return md.render(processedContent);
};

// Methods
const updateTime = () => {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  currentTime.value = `${hours}:${minutes}`;
};

const goBack = () => {
  // Handle back navigation
  console.log('Back button clicked');
};

const scrollToBottom = () => {
  if (chatContent.value) {
    chatContent.value.scrollTop = chatContent.value.scrollHeight;
  }
};

// Function to handle sending follow-up responses
const sendFollowUpResponse = (optionText) => {
  // Create Baidu search URL with the option text
  const searchUrl = `https://www.baidu.com/s?wd=${encodeURIComponent(optionText)}`;
  
  // Open product window with the search URL
  productName.value = optionText;
  productUrl.value = searchUrl;
  showProductWindow.value = true;
};

// Using safeJsonParse from streamUtils.js

// Flag to track if this is the first message
const isFirstMessage = ref(true);

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  const userMessage = userInput.value;
  console.log('Message sent:', userMessage);
  
  // Add user message to messages array
  messages.value.push({
    role: 'user',
    content: userMessage
  });
  
  // If this is the first message, update the page title
  if (isFirstMessage.value) {
    // Update document title with the user's query
    document.title = `${userMessage} - ${appConfig.defaultPageTitle}`;
    isFirstMessage.value = false;
  }
  
  // Clear input field
  userInput.value = '';
  
  // Scroll to bottom
  nextTick(() => {
    scrollToBottom();
  });
  
  // Set loading state
  isLoading.value = true;
  streamingMessage.value = '';
  
  try {
    // Create placeholder for assistant response
    const lastIndex = messages.value.push({
      role: 'assistant',
      content: '',
      streaming: true
    }) - 1;
    
    // Set streaming state to true
    isStreaming.value = true;
    
    // Call Xiaomi API
    const url = 'https://mify-be.pt.xiaomi.com/api/v1/chat-messages';
    
    const headers = {
      'Authorization': 'Bearer app-u456N01sF3Us7rg7QBpcOI2R',
      'Content-Type': 'application/json'
    };
    
    const body = {
      inputs: {},
      query: userMessage,
      response_mode: "streaming",
      conversation_id: conversationId.value,
      user: "taoliang",
      files: []
    };
    
    // Since we need to use headers and POST with streaming, we use fetch
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body)
    });
    
    // Use our streamingUtils to handle the streaming response
    await handleStreamingResponse(response, {
      debug: true,
      onStart: () => {
        console.log('Streaming response started');
      },
      onData: (data) => {
        // Handle conversation ID
        if (data.conversation_id) {
          conversationId.value = data.conversation_id;
        }
        
        // Handle message event (contains answer content)
        if (data.event === "message" && data.answer) {
          // Append new content to streaming message
          streamingMessage.value += data.answer;
          
          // Update the message content
          messages.value[lastIndex].content = streamingMessage.value;
          
          // Scroll to bottom with new content
          nextTick(() => {
            scrollToBottom();
          });
        }
        
        // Handle more_question event
        if (data.event === "node_finished" && data.data && data.data.title === "more_question") {
          console.log('More question detected:', data.data);
          
          if (data.data.outputs && data.data.outputs.text) {
            const rawText = data.data.outputs.text;
            console.log('Raw text from more_question:', rawText);
            
            const { data: parsedData, error } = safeJsonParse(rawText);
            if (!error && parsedData) {
              console.log('Successfully parsed text data:', parsedData);
              
              // Check if it has question and option property
              if (parsedData.question && Array.isArray(parsedData.option)) {
                console.log('Valid question and options found');
                
                // Cache the follow-up question data, but don't show it until streaming is complete
                streamingMessageFollowUp.value = {
                  question: parsedData.question,
                  options: parsedData.option
                };
                
                console.log('Cached follow-up question, will show after streaming completes');
              }
            }
          }
        }
      },
      onComplete: () => {
        console.log('Streaming response completed');
        
        // Mark streaming as complete
        messages.value[lastIndex].streaming = false;
        
        // Add the follow-up question to the message if available
        if (streamingMessageFollowUp.value) {
          console.log('Adding follow-up question to message:', streamingMessageFollowUp.value);
          messages.value[lastIndex].followUpQuestion = streamingMessageFollowUp.value;
          // Reset the follow-up cache
          streamingMessageFollowUp.value = null;
        }
        
        // Set streaming state to false
        isStreaming.value = false;
      },
      onError: (error) => {
        console.error('Streaming error:', error);
      },
      // Define custom handlers for specific events
      eventHandlers: {
        workflow_finished: (data) => {
          console.log('Workflow finished event received:', data);
        },
        message_end: (data) => {
          console.log('Message end event received:', data);
        }
      },
      // Define events that should end the stream
      endEvents: ['workflow_finished']
    });
    
  } catch (error) {
    console.error('Error calling chat API:', error);
    
    // Remove the streaming message placeholder
    if (messages.value.length > 0 && messages.value[messages.value.length - 1].streaming) {
      messages.value.pop();
    }
    
    // Add error message
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，无法回答您的问题。',
      error: true
    });
    
  } finally {
    // Reset loading and streaming states
    isLoading.value = false;
    isStreaming.value = false;
    
    // Scroll to bottom
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// Lifecycle hooks
onMounted(() => {
  updateTime();
  setInterval(updateTime, 60000);
  
  // Scroll to bottom initially
  nextTick(() => {
    scrollToBottom();
  });
  
  // Add event listener for clicks on chat content
  const chatContentEl = document.querySelector('.chat-content');
  if (chatContentEl) {
    chatContentEl.addEventListener('click', handleContentClick);
  }
});

// Add blinking cursor effect for streaming messages
setInterval(() => {
  const streamingElements = document.querySelectorAll('.cursor');
  streamingElements.forEach(el => {
    el.style.opacity = el.style.opacity === '0' ? '1' : '0';
  });
}, 500);
</script>

<style scoped>
</style>

<!-- Non-scoped styles for dynamically injected HTML content -->
<style>
/* Reset and global styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Main container */
.chat-container {
  position: fixed;
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
  width: 100vw;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevent scrolling on container level */
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Mobile header styling - fixed at top */
.mobile-header {
  background-color: #f7f8fc;
  padding-top: env(safe-area-inset-top, 10px);
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  width: 100%;
  display: none; /* Hide the mobile header */
}

.status-bar {
  display: flex;
  justify-content: space-between;
  padding: 4px 16px;
  font-size: 12px;
  color: #333;
}

.status-icons {
  display: flex;
  gap: 4px;
}

.chat-header {
  display: none; /* Hide the chat header */
}

.back-button, .add-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  cursor: pointer;
}

.back-icon, .add-icon {
  font-size: 20px;
}

.spacer {
  flex: 1;
}

/* Chat content - scrollable area between header and input */
.chat-content {
  grid-row: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  padding-bottom: 100px; /* Increase bottom padding to create more space above input area */
  -webkit-overflow-scrolling: touch;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.message-container {
  display: flex;
  margin-bottom: 16px;
  position: relative;
  width: 100%;
  min-width: 0;
  flex-shrink: 0;
}

.user-message {
  justify-content: flex-end;
}

.bot-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 90%;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  line-height: 1.4;
  overflow-wrap: break-word;
}

.user-message .message-bubble {
  background-color: #d8e8ff;
  color: #333;
  border-top-right-radius: 4px;
}

.bot-message .message-bubble {
  background-color: white;
  color: #333;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.mi-logo, .spacer-logo {
  width: 32px;
  height: 32px;
  margin-right: 8px;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ff6700;
}

.mi-logo-text {
  color: white;
  font-weight: bold;
  font-size: 14px;
  letter-spacing: -1px;
}

.spacer-logo {
  background-color: transparent;
}

.related-content {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 14px;
}

.check-icon {
  color: #ff6700;
  margin-right: 6px;
}

.chevron-right {
  margin-left: auto;
  font-size: 18px;
}

.with-chevron {
  padding: 10px 14px;
  cursor: pointer;
}

.main-response {
  padding: 16px;
  font-size: 15px;
}

.response-text {
  line-height: 1.5;
}

/* Markdown styles */
.response-text h1, 
.response-text h2, 
.response-text h3, 
.response-text h4, 
.response-text h5, 
.response-text h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.25;
}

.response-text h1 {
  font-size: 1.5em;
}

.response-text h2 {
  font-size: 1.3em;
}

.response-text h3 {
  font-size: 1.2em;
}

.response-text p {
  margin: 8px 0;
}

.response-text a {
  color: #ff6700;
  text-decoration: none;
}

.response-text a:hover {
  text-decoration: underline;
}

.response-text code {
  font-family: monospace;
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

.response-text pre {
  background-color: #f1f1f1;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
  margin: 12px 0;
}

.response-text pre code {
  background-color: transparent;
  padding: 0;
}

.response-text ul, 
.response-text ol {
  margin: 8px 0;
  padding-left: 24px;
}

.response-text li {
  margin: 4px 0;
}

.response-text blockquote {
  border-left: 4px solid #ddd;
  padding-left: 12px;
  color: #666;
  margin: 12px 0;
}

.response-text table {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
  border: 1px solid #ddd;
}

.response-text table th,
.response-text table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.response-text table th {
  background-color: #f1f1f1;
  font-weight: 600;
}

/* Ensure table borders are visible */
.response-text table tr {
  border-bottom: 1px solid #ddd;
}

.cursor {
  display: inline-block;
  font-weight: bold;
  transition: opacity 0.3s;
}

/* Progress bar */
.progress-container {
  width: 100%;
  height: 4px;
  margin: 12px 0;
  background-color: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  width: 30%;
  background-color: #ff6700;
  border-radius: 2px;
  animation: progress-animation 1.5s infinite ease-in-out;
}

@keyframes progress-animation {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

/* Input area - fixed at bottom */
.chat-input {
  grid-row: 2;
  width: 100%;
  background-color: #f7f8fc;
  padding: 8px 16px;
  padding-bottom: env(safe-area-inset-bottom, 16px);
  border-top: 1px solid #eee;
  z-index: 100;
}

.input-container {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 24px;
  padding: 4px 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.plus-button, .voice-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  cursor: pointer;
}

.voice-button {
  color: #ff6700;
  background-color: #f0f0f0;
  border-radius: 50%;
}

.send-icon {
  font-size: 18px;
  font-weight: bold;
}

input {
  flex: 1;
  border: none;
  padding: 8px 12px;
  font-size: 15px;
  outline: none;
  background: transparent;
}

.bottom-toolbar {
  display: flex;
  margin-top: 8px;
  justify-content: space-between;
  padding: 0 20px;
}

.toolbar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 16px;
}

.toolbar-item i {
  margin-right: 4px;
  font-size: 14px;
}

/* Quick action buttons */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.quick-action-button {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.quick-action-button:hover {
  background-color: #e9e9e9;
  border-color: #ccc;
}

.quick-action-button:active {
  background-color: #ff6700;
  color: white;
  border-color: #ff6700;
}

/* Product floating window */
.product-window {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.product-window-content {
  width: 100%;
  height: 50%;
  background-color: white;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slide-up 0.3s ease-out forwards;
  transition: height 0.3s ease-out;
}

.product-window-content.fullscreen {
  height: 100%;
  border-radius: 0;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.product-window-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.header-buttons {
  display: flex;
  align-items: center;
}

.product-window-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  text-align: left;
  margin-right: 50px; /* Make room for the drag handle */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drag-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  background-color: rgba(240, 240, 240, 0.9);
  border-radius: 16px;
  z-index: 10;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  touch-action: none; /* Improves touch handling */
}

.drag-handle:hover {
  background-color: rgba(230, 230, 230, 0.95);
}

.drag-handle:active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.05);
  background-color: rgba(224, 224, 224, 1);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.drag-icon {
  font-size: 22px;
  color: #555;
  user-select: none; /* Prevent text selection during drag */
}

.expand-button, .close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  margin-left: 10px;
}

.product-window-body {
  flex: 1;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.product-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.product-name {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 16px;
}

/* Style for special links (aisearch://) */
.special-link {
  color: black !important;
  font-weight: bold;
  font-style: italic;
  text-decoration: none; /* Remove underline */
  cursor: pointer;
  background-color: rgba(255, 103, 0, 0.1); /* Light orange background */
  padding: 2px 4px;
  border-radius: 3px;
}

/* Hover effect for special links */
.special-link:hover {
  background-color: rgba(255, 103, 0, 0.2);
}

/* Follow-up question styles */
.follow-up-question {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.question-text {
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.option-button {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.option-button:hover {
  background-color: #e9e9e9;
  border-color: #ccc;
}

.option-button:active {
  background-color: #ff6700;
  color: white;
  border-color: #ff6700;
}
</style>
