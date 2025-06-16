<template>
  <div class="chat-container">
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

    <!-- Settings Button -->
    <button class="settings-button" @click="openSettingsModal">
      <span class="settings-icon">⚙️</span>
    </button>

    <!-- Chat content -->
    <div class="chat-content" ref="chatContent">
      <div class="messages-container">
        <!-- Quick action buttons -->
        <div class="quick-actions">
          <button v-for="(action, index) in quickActions" :key="index" class="quick-action-button"
            @click="handleQuickAction(action)">
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
            <div class="message-container bot-message">
              <div class="mi-logo">
                <div class="mi-logo-text">MI</div>
              </div>
              <div class="message-bubble main-response multi-agent-response">
                <div v-if="message.searchPlan" class="search-plan-container response-text">
                  <div v-html="renderMarkdown(message.searchPlan)"></div>
                </div>
                <!-- analysis 流式展示 -->
                <div v-if="message.analysisText">
                  <div class="analysis-label-block">
                    <i class="analysis-label-icon">🔍</i>
                    <span class="analysis-label-text">问题分析</span>
                  </div>
                  <div class="analysis-block">
                    <div class="analysis-content">{{ message.analysisText }}</div>
                  </div>
                </div>
                <!-- 专家分配标识 -->
                <div v-if="message.roleCards && message.roleCards.length" class="experts-assign-label">
                  <i class="experts-assign-icon">👥</i>
                  <span class="experts-assign-title">专家观点</span>
                </div>
                <!-- 专家分配模块 -->
                <div v-if="message.roleCards && message.roleCards.length" class="experts-assign-block">
                  <div class="experts-desc" v-if="false">
                    专家队列：
                    <span class="experts-names">
                      {{message.roleCards.map(r => r.role).join('、')}}
                    </span>
                  </div>
                </div>
                <!-- 滑动区 -->
                <div v-if="message.roleCards && message.roleCards.length" class="expert-swiper-container">
                  <div class="expert-swiper" :ref="el => setExpertSwiper(el, index)">
                    <div class="expert-card expert-slide" v-for="(roleObj, idx) in message.roleCards" :key="idx">
                      <!-- 专家身份区 -->
                      <div class="expert-header">
                        <i class="expert-icon">👤</i>
                        <span class="expert-title">{{ roleObj.role }}</span>
                      </div>
                      <!-- 新增：引用资料折叠区 -->
                      <div v-if="roleObj.searchResults && roleObj.searchResults.length" class="expert-ref-toggle-block">
                        <div class="ref-toggle-header" @click="roleObj.showRefs = !roleObj.showRefs">
                          <span class="ref-toggle-text">引用{{roleObj.searchResults.reduce((sum, s) => sum +
                            (s.search_result ? s.search_result.length : 0), 0) }}篇资料</span>
                          <span class="ref-toggle-btn">{{ roleObj.showRefs ? '▼' : '▶' }}</span>
                        </div>
                        <div v-show="roleObj.showRefs" class="expert-ref-list">
                          <div v-for="(result, idx2) in roleObj.searchResults" :key="idx2" class="search-item">
                            <div class="search-query" v-if="result.search_item"
                              style="font-weight: bold; color: #1976d2; margin-bottom: 4px;">
                              {{ result.search_item }}
                            </div>
                            <div class="search-content">
                              <div v-for="(item, i) in result.search_result" :key="i" class="result-item">
                                <a class="result-link" :href="item.url">{{ item.title }}</a>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <!-- 专家回答区 -->
                      <div v-if="roleObj.expert_answer && roleObj.expert_answer.text" class="expert-answer-block">
                        <div class="answer-content expert-markdown"
                          v-html="renderMarkdownRaw(roleObj.expert_answer.text)"></div>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- 搜索结果 -->
                <div v-if="message.searchResults" v-show="!isSearchPlanCollapsed" class="search-results-container">
                  <div v-for="(result, idx) in message.searchResults" :key="idx" class="search-item">
                    <div class="search-title">
                      <div class="search-header" @click="toggleSearchResult(result)">
                        <span class="toggle-icon">{{ result.show ? '▼' : '▶' }}</span>
                        <span class="search-query">{{ result.search_item }}</span>
                      </div>
                      <div v-show="result.show" class="search-content">
                        <div v-for="(item, i) in result.search_result" :key="i" class="result-item">
                          <a class="result-link" :href="item.url">{{ item.title }}</a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="response-text">
                  <div v-html="renderMarkdown(message.answerText)"></div>
                </div>
                <!-- Follow-up question section -->
                <div v-if="message.followUpQuestion" class="follow-up-question">
                  <p class="question-text">{{ message.followUpQuestion.question }}</p>
                  <div class="option-buttons">
                    <button v-for="(option, index) in message.followUpQuestion.options" :key="index"
                      class="option-button" @click="sendFollowUpResponse(option)">
                      {{ option }}
                    </button>
                  </div>
                </div>
                <!-- 专家卡片下方渲染总结 -->
                <ThinkingView 
                  v-if="message.thinkingText || message.normalText"
                  :thinkingText="message.thinkingText"
                  :normalText="message.normalText"
                  :uniqueIdSuffix="index"
                />
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
    </div>

    <!-- Input area -->
    <div class="chat-input">
      <div class="input-container">
        <div class="plus-button">
          <i class="plus-icon">+</i>
        </div>
        <input type="text" placeholder="输入你想问的问题" v-model="userInput" @keyup.enter="sendMessage" />
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
import { ref, onMounted, nextTick, onUpdated } from 'vue';
import MarkdownIt from 'markdown-it';
import ThinkingView from '@/base/views/ThinkingView.vue';


// Quick action buttons - loaded from config
const quickActions = ref([
  '小米15Ultra怎么样',
  '无人机可怕的死亡尖啸，为何大多数士兵听到就有心理阴影？'
]);

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
// Initialize markdown-it renderer with custom link rendering
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
});

// Add CSS for movie container
const style = document.createElement('style');
style.textContent = `
  .movie-container {
    display: flex;
    flex-direction: column;
    margin: 16px 0;
    background: #f9f9f9;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    max-width: 100%;
  }
  
  .movie-top-section {
    display: flex;
    flex-direction: column;
    @media (min-width: 768px) {
      flex-direction: row;
    }
  }
  
  .movie-poster {
    flex: 0 0 auto;
    background: #eee;
    min-height: 200px;
    max-height: 300px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    @media (min-width: 768px) {
      flex: 0 0 150px;
    }
  }
  
  .movie-poster img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  
  .movie-details {
    flex: 1;
    padding: 16px;
    overflow: hidden;
  }
  
  .movie-detail-item {
    margin-bottom: 8px;
    line-height: 1.4;
    display: flex;
    flex-wrap: wrap;
  }
  
  .detail-label {
    color: #666;
    margin-right: 4px;
    flex: 0 0 80px;
  }
  
  .detail-value {
    color: #333;
    flex: 1;
    word-break: break-word;
  }
  
  .movie-plot {
    padding: 16px;
    border-top: 1px solid #eee;
    line-height: 1.6;
    word-break: break-word;
  }
`;
document.head.appendChild(style);

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

      // Check if this is a Baidu URL and use our proxy if it is
      if (jumpUrl.includes('baidu.com')) {
        // Replace the Baidu domain with our proxy
        const proxyUrl = jumpUrl.replace(/https?:\/\/([^/]*\.)?baidu\.com/, '/baidu-proxy');
        productUrl.value = proxyUrl;
      } else {
        productUrl.value = jumpUrl;
      }

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

// Settings state
const showSettingsModal = ref(false);
const apiKeyInput = ref('');

// Settings functions
const openSettingsModal = () => {
  // Load existing API key from cookie if available
  const savedApiKey = getCookie('movie_api_key');
  if (savedApiKey) {
    apiKeyInput.value = savedApiKey;
  }
  showSettingsModal.value = true;
};

const getCookie = (name) => {
  const cookieName = name + "=";
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');

  for (let i = 0; i < cookieArray.length; i++) {
    let cookie = cookieArray[i].trim();
    if (cookie.indexOf(cookieName) === 0) {
      return cookie.substring(cookieName.length, cookie.length);
    }
  }
  return "";
};

// Data
const currentTime = ref('');
const userInput = ref('');
const chatContent = ref(null);
const isLoading = ref(false);
const isStreaming = ref(false);

// Store messages
const messages = ref([]);

// Markdown renderer function
const renderMarkdownRaw = (content) => {
  if (!content) return '';
  return md.render(content);
};

// renderMarkdown function for content that is NOT part of ThinkingView
const renderMarkdown = (content) => {
  if (!content) return '';
  let html = md.render(content);
  // Add spacing between paragraphs and headings
  html = html.replace(/(<\/p>)(\s*)<p>/g, '$1<div style="height:1em"></div><p>');
  html = html.replace(/(<\/h[1-6]>)(\s*)<p>/g, '$1<div style="height:1em"></div><p>');
  html = html.replace(/(<\/p>)(\s*)<(h[1-6]>)/g, '$1<div style="height:1em"></div><$3');
  html = html.replace(/(<\/h[1-6]>)(\s*)<(h[1-6]>)/g, '$1<div style="height:1em"></div><$3');
  return html;
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
  // Create Baidu search URL with the option text using our proxy
  const searchUrl = `/baidu-proxy/s?wd=${encodeURIComponent(optionText)}`;

  // Open product window with the search URL
  productName.value = optionText;
  productUrl.value = searchUrl;
  showProductWindow.value = true;
};

// Using safeJsonParse from streamUtils.js
const toggleSearchResult = (result) => {
  result.show = !result.show;
};

const sendMessage = async () => {
  try {
    isStreaming.value = true;
    const newMessage = {
      role: 'user',
      content: userInput.value,
      searchResults: null,
      answerText: '',
      searchPlan: '',
      roleCards: []
    };
    messages.value.push(newMessage);
    const assistantMessage = {
      role: 'assistant',
      content: '',
      searchResults: null,
      answerText: '',
      searchPlan: '',
      roleCards: [],
      analysisText: '',
      thinkingText: '', // 专门存储思考过程的内容
      normalText: '',   // 存储非思考过程的内容
      inThinkingMode: false // 新增：标记是否正在思考过程中
    };
    messages.value.push(assistantMessage);

    // 1. 第一个API流式获取专家名和analysis
    console.log('[sendMessage] 开始请求第一个API获取专家名和analysis');
    const response = await fetch('http://10.18.4.170/v1/chat-messages', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer app-bCkBvqZL5WpDnEQqNjb0Buld',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inputs: {},
        query: userInput.value,
        response_mode: 'streaming',
        conversation_id: '',
        user: 'abc-123'
      })
    });

    const reader = response.body.getReader();
    let partialLine = '';
    let shouldContinue = true;
    let expertNames = [];
    let analysisText = '';
    while (shouldContinue) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      const lines = (partialLine + chunk).split('\n');
      partialLine = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const eventData = JSON.parse(line.slice(6));
          // 收集 analysis（不再以1开头）并流式渲染
          if (eventData.event === 'message' && typeof eventData.answer === 'string') {
            analysisText += eventData.answer;
            const lastAssistantIndex = messages.value.findLastIndex(m => m.role === 'assistant');
            if (lastAssistantIndex >= 0) {
              messages.value[lastAssistantIndex].analysisText = analysisText;
            }
            console.log('[sendMessage] 收到analysis片段:', eventData.answer);
          }
          // 结束 analysis，遇到专家角色输出，流式渲染专家卡片
          if (eventData.event === 'node_finished' && eventData.data.title && eventData.data.title.includes('专家角色')) {
            if (eventData.data.outputs && eventData.data.outputs.output_role) {
              const content = JSON.parse(eventData.data.outputs.output_role.message.content);
              if (Array.isArray(content.role)) {
                expertNames = content.role;
                // 立即渲染专家卡片（初始为"正在生成..."）
                const lastAssistantIndex = messages.value.findLastIndex(m => m.role === 'assistant');
                if (lastAssistantIndex >= 0) {
                  messages.value[lastAssistantIndex].roleCards = expertNames.map(role => ({
                    role,
                    expert_answer: { text: '正在生成...' },
                    searchResults: []
                  }));
                  console.log('[sendMessage] 收到专家名并渲染卡片:', expertNames);
                }
              }
            }
          }
        }
      }
    }
    console.log('[sendMessage] analysis 完整内容:', analysisText);
    // 2. 并发调用第二个API获取每个专家的独立回答，流式更新卡片内容
    console.log('[sendMessage] 开始并发请求每个专家的独立总结');
    await Promise.all(
      expertNames.map(async (expert, idx) => {
        console.log(`[sendMessage] 请求专家 ${expert} 的独立总结`);
        const res2 = await fetch('http://10.18.4.170/v1/chat-messages', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer app-fiDcyif946Bsa9u88xKvMR51',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            inputs: {
              role: expert,
              analysis: analysisText
            },
            query: userInput.value,
            response_mode: 'streaming',
            conversation_id: '',
            user: 'abc-123'
          })
        });
        // 解析流式返回，拼接专家总结，实时更新卡片内容
        const reader2 = res2.body.getReader();
        let partial2 = '';
        let expertSummary = '';
        let shouldContinue2 = true;
        let lastAssistantIndex2 = messages.value.findLastIndex(m => m.role === 'assistant');
        while (shouldContinue2) {
          const { done, value } = await reader2.read();
          if (done) break;
          const chunk2 = new TextDecoder().decode(value);
          const lines2 = (partial2 + chunk2).split('\n');
          partial2 = lines2.pop() || '';
          for (const line2 of lines2) {
            if (line2.startsWith('data: ')) {
              const eventData2 = JSON.parse(line2.slice(6));
              // 收集专家总结并流式渲染
              if (eventData2.event === 'message' && typeof eventData2.answer === 'string') {
                expertSummary += eventData2.answer;
                if (lastAssistantIndex2 >= 0 && messages.value[lastAssistantIndex2].roleCards && messages.value[lastAssistantIndex2].roleCards[idx]) {
                  const oldCard = messages.value[lastAssistantIndex2].roleCards[idx];
                  messages.value[lastAssistantIndex2].roleCards[idx] = {
                    ...oldCard,
                    expert_answer: {
                      ...oldCard.expert_answer,
                      text: expertSummary
                    }
                  };
                  messages.value[lastAssistantIndex2].roleCards = [
                    ...messages.value[lastAssistantIndex2].roleCards
                  ];
                  messages.value = [...messages.value];
                }
                console.log(`[sendMessage] 收到专家 ${expert} 总结片段:`, eventData2.answer);
              }
              // 新增：先处理 output_search_item
              if (
                eventData2.event === 'node_finished' &&
                eventData2.data &&
                eventData2.data.outputs &&
                eventData2.data.outputs.output_search_item
              ) {
                let searchItemObj = JSON.parse(eventData2.data.outputs.output_search_item.message.content);
                let searchItem = searchItemObj.search_item || '';
                // 先渲染 search_item
                if (
                  lastAssistantIndex2 >= 0 &&
                  messages.value[lastAssistantIndex2].roleCards &&
                  messages.value[lastAssistantIndex2].roleCards[idx]
                ) {
                  const oldCard = messages.value[lastAssistantIndex2].roleCards[idx];
                  messages.value[lastAssistantIndex2].roleCards[idx] = {
                    ...oldCard,
                    searchResults: [
                      ...(oldCard.searchResults || []),
                      {
                        search_item: searchItem, // 只渲染字符串
                        search_result: [],
                        search_summary: '',
                        show: false
                      }
                    ]
                  };
                  messages.value[lastAssistantIndex2].roleCards = [
                    ...messages.value[lastAssistantIndex2].roleCards
                  ];
                  messages.value = [...messages.value];
                }
              }
              // 收集专家搜索结果（补充 search_result 和 search_summary）
              if (
                eventData2.event === 'node_finished' &&
                eventData2.data &&
                eventData2.data.outputs &&
                eventData2.data.outputs.output_search_result
              ) {
                let searchResultData = JSON.parse(eventData2.data.outputs.output_search_result.message.content);
                if (
                  lastAssistantIndex2 >= 0 &&
                  messages.value[lastAssistantIndex2].roleCards &&
                  messages.value[lastAssistantIndex2].roleCards[idx]
                ) {
                  const oldCard = messages.value[lastAssistantIndex2].roleCards[idx];
                  const searchResults = [...(oldCard.searchResults || [])];
                  // 找到最后一个 search_result 为空的项
                  let targetIdx = -1;
                  for (let i = searchResults.length - 1; i >= 0; i--) {
                    if (Array.isArray(searchResults[i].search_result) && searchResults[i].search_result.length === 0) {
                      targetIdx = i;
                      break;
                    }
                  }
                  if (targetIdx !== -1 && searchResults[targetIdx]) {
                    searchResults[targetIdx].search_result = searchResultData.search_result || [];
                  } else {
                    // 没有空的项，直接 push 一个新的
                    searchResults.push({
                      search_result: searchResultData.search_result || []
                    });
                  }
                  messages.value[lastAssistantIndex2].roleCards[idx] = {
                    ...oldCard,
                    searchResults
                  };
                  messages.value[lastAssistantIndex2].roleCards = [
                    ...messages.value[lastAssistantIndex2].roleCards
                  ];
                  messages.value = [...messages.value];
                }
              }
            }
          }
        }
        console.log(`[sendMessage] 专家 ${expert} 总结完整:`, expertSummary);
      })
    );
    // 3. 渲染到roleCards已在流式过程中完成
    const lastAssistantIndex = messages.value.findLastIndex(m => m.role === 'assistant');
    if (lastAssistantIndex >= 0) {
      console.log('[sendMessage] 所有专家及回答已渲染:', messages.value[lastAssistantIndex].roleCards);
    }

    // === 新增：调用第三个API进行总结 ===
    // 1. 收集所有专家名和回答
    const lastAssistantIndex2 = messages.value.findLastIndex(m => m.role === 'assistant');
    const expertIdeas = expertNames.map((name, idx) => {
      const card = messages.value[lastAssistantIndex2].roleCards[idx];
      const answer = card && card.expert_answer && card.expert_answer.text ? card.expert_answer.text : '';
      return answer ? `${name}：${answer}` : '';
    }).filter(Boolean).join('\n\n');

    console.log('[sendMessage] 开始调用第三个API进行总结，expert_idea:', expertIdeas);
    // 2. 调用新版第三个API
    let summaryText = '';
    let collectingSummary = false;
    const summaryRes = await fetch('https://mify-be.pt.xiaomi.com/api/v1/chat-messages', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer app-QFLCZ51CgCHHIweJdSZHEPhx',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inputs: {
          expert_idea: expertIdeas
        },
        query: userInput.value,
        response_mode: 'streaming',
        conversation_id: '',
        user: 'abc-123'
      })
    });
    const summaryReader = summaryRes.body.getReader();
    let partialSummary = '';
    let shouldContinueSummary = true;
    while (shouldContinueSummary) {
      const { done, value } = await summaryReader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      const lines = (partialSummary + chunk).split('\n');
      partialSummary = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const eventData = JSON.parse(line.slice(6));
          if (eventData.event === 'message' && typeof eventData.answer === 'string') {
            const answer = eventData.answer;
            summaryText += answer;

            const lastAssistantIndex = messages.value.findLastIndex(m => m.role === 'assistant');
            if (lastAssistantIndex >= 0) {
              const assistantMsg = messages.value[lastAssistantIndex];

              // 检查当前片段是否包含<think>或</think>标签
              if (answer.includes('<think>')) {
                // 开始思考模式
                assistantMsg.inThinkingMode = true;

                // 处理<think>之前的普通内容
                const beforeThinkContent = answer.split('<think>')[0];
                if (beforeThinkContent.trim()) {
                  assistantMsg.normalText = (assistantMsg.normalText || '') + beforeThinkContent;
                }

                // 处理<think>之后的思考内容
                const afterThinkContent = answer.split('<think>')[1];
                // 如果同一个片段中也有</think>，则提取中间部分
                if (afterThinkContent.includes('</think>')) {
                  const thinkContent = afterThinkContent.split('</think>')[0];
                  assistantMsg.thinkingText = (assistantMsg.thinkingText || '') + thinkContent;

                  // 处理</think>之后的普通内容
                  const afterEndThinkContent = afterThinkContent.split('</think>')[1];
                  if (afterEndThinkContent.trim()) {
                    assistantMsg.normalText = (assistantMsg.normalText || '') + afterEndThinkContent;
                  }

                  // 结束思考模式
                  assistantMsg.inThinkingMode = false;
                } else {
                  // 只有<think>没有</think>，则所有后续内容都是思考内容
                  assistantMsg.thinkingText = (assistantMsg.thinkingText || '') + afterThinkContent;
                }
              } else if (answer.includes('</think>')) {
                // 结束思考模式
                if (assistantMsg.inThinkingMode) {
                  const beforeEndThinkContent = answer.split('</think>')[0];
                  assistantMsg.thinkingText = (assistantMsg.thinkingText || '') + beforeEndThinkContent;

                  const afterEndThinkContent = answer.split('</think>')[1];
                  if (afterEndThinkContent.trim()) {
                    assistantMsg.normalText = (assistantMsg.normalText || '') + afterEndThinkContent;
                  }

                  assistantMsg.inThinkingMode = false;
                } else {
                  // 异常情况：有</think>但没有前面的<think>
                  assistantMsg.normalText = (assistantMsg.normalText || '') + answer;
                }
              } else if (assistantMsg.inThinkingMode) {
                // 正在思考模式中，内容添加到思考文本
                assistantMsg.thinkingText = (assistantMsg.thinkingText || '') + answer;

                // 更新思考文本后，确保自动滚动到最新内容
                nextTick(() => {
                  // 找到最新的思考块
                  const thinkingBlocks = document.querySelectorAll('.thinking-block-wrapper');
                  thinkingBlocks.forEach(block => {
                    const blockId = block.getAttribute('data-thinking-id');
                    if (blockId) {
                      const contentElement = document.getElementById(blockId);
                      if (contentElement) {
                        const innerContent = contentElement.querySelector('.thinking-block-inner-content');
                        if (innerContent && innerContent.style.overflow === 'auto') {
                          // 只有在展开状态时才滚动到底部
                          innerContent.scrollTop = innerContent.scrollHeight;
                        }
                      }
                    }
                  });
                });
              } else {
                // 普通内容
                assistantMsg.normalText = (assistantMsg.normalText || '') + answer;
              }

              messages.value = [...messages.value];
            }
            console.log('[sendMessage] 总结流式片段(message):', eventData.answer);
          }
          if (eventData.event === 'text_chunk' && eventData.data && typeof eventData.data.text === 'string') {
            // 兼容旧的 text_chunk 事件
            if (collectingSummary) {
              summaryText += eventData.data.text;
              const lastAssistantIndex = messages.value.findLastIndex(m => m.role === 'assistant');
              if (lastAssistantIndex >= 0) {
                messages.value[lastAssistantIndex].summaryText = summaryText;
                messages.value = [...messages.value];
              }
              console.log('[sendMessage] 总结流式片段(text_chunk):', eventData.data.text);
            }
          }
        }
      }
    }
    const lastAssistantIndex3 = messages.value.findLastIndex(m => m.role === 'assistant');
    if (lastAssistantIndex3 >= 0) {
      const assistantMsg = messages.value[lastAssistantIndex3];
      console.log('[sendMessage] 总结完整内容:', summaryText);
      console.log('[sendMessage] 思考过程内容:', assistantMsg.thinkingText);
      console.log('[sendMessage] 非思考过程内容:', assistantMsg.normalText);
    }
    // === END 新增 ===
  } catch (error) {
    console.error('请求错误:', error);
    if (messages.value.length > 0 && messages.value[messages.value.length - 1].streaming) {
      messages.value.pop();
    }
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，无法回答您的问题。',
      error: true,
      showThinking: true
    });
  } finally {
    isLoading.value = false;
    isStreaming.value = false;
    nextTick(() => {
      scrollToBottom();

      // 思考过程显示完成后，确保只保留一个思考块，并设置为折叠状态但不隐藏
      setTimeout(() => {
        const thinkingBlocks = document.querySelectorAll('.thinking-block-wrapper');

        for (let i = 0; i < thinkingBlocks.length; i++) {
          const blockId = thinkingBlocks[i].getAttribute('data-thinking-id');
          if (blockId) {
            const contentElement = document.getElementById(blockId);
            if (contentElement) {
              const innerContent = contentElement.querySelector('.thinking-block-inner-content');
              if (innerContent) {
                // 获取 thinkingText
                const thinkingText = innerContent.textContent.trim();

                if (thinkingText === '') {
                  // 如果 thinkingText 为空，则隐藏 thinking-block-wrapper
                  thinkingBlocks[i].style.display = 'none';
                } else {
                  // 如果 thinkingText 不为空，则折叠 thinking-block-wrapper
                  thinkingBlocks[i].style.display = 'block'; // 确保思考块可见
                  contentElement.style.display = 'block'; // 确保内容容器可见
                  innerContent.style.maxHeight = '0px'; // 设置为0以完全折叠
                  innerContent.style.padding = '0 12px'; // 移除上下 padding
                  innerContent.style.overflow = 'hidden';

                  const headerElement = contentElement.previousElementSibling;
                  const iconElement = headerElement && headerElement.querySelector('.toggle-icon-think');
                  if (iconElement) iconElement.textContent = '▶';
                }
              }
            }
          }
        }
      }, 500); // 设置延迟，确保所有内容都已渲染完成
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

// === 新增：每条消息独立的专家 swiper 和分页 ===
const expertSwipers = ref({}); // { [msgIdx]: swiperEl }
const expertPageMap = ref({}); // { [msgIdx]: 当前页 }

// 绑定 swiper ref
function setExpertSwiper(el, msgIdx) {
  if (el) expertSwipers.value[msgIdx] = el;
}

// 滚动时动态高亮
function onExpertScroll(msgIdx) {
  const swiperEl = expertSwipers.value[msgIdx];
  if (!swiperEl) return;
  const cards = swiperEl.querySelectorAll('.expert-card');
  let minDiff = Infinity;
  let page = 0;
  for (let i = 0; i < cards.length; i++) {
    const diff = Math.abs((cards[i].offsetLeft - swiperEl.offsetLeft) - swiperEl.scrollLeft);
    if (diff < minDiff) {
      minDiff = diff;
      page = i;
    }
  }
  expertPageMap.value[msgIdx] = page;
}

// 监听每个 swiper 的 scroll 事件
onMounted(() => {
  nextTick(() => {
    messages.value.forEach((msg, msgIdx) => {
      const swiperEl = expertSwipers.value[msgIdx];
      if (swiperEl && typeof swiperEl.addEventListener === 'function') {
        swiperEl.addEventListener('scroll', () => onExpertScroll(msgIdx));
      }
    });
  });
});
onUpdated(() => {
  messages.value.forEach((msg, msgIdx) => {
    const swiperEl = expertSwipers.value[msgIdx];
    if (swiperEl && typeof swiperEl.removeEventListener === 'function') {
      swiperEl.removeEventListener('scroll', () => onExpertScroll(msgIdx));
    }
    if (swiperEl && typeof swiperEl.addEventListener === 'function') {
      swiperEl.addEventListener('scroll', () => onExpertScroll(msgIdx));
    }
  });
});

</script>

<style scoped>
/* 搜索结果卡片样式 */
.search-annotation {
  color: #666;
  margin-bottom: 12px;
  font-size: 0.9em;
}

.reference-card {
  border: 1px solid #eee;
  border-radius: 8px;
  margin: 10px 0;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.reference-card:hover {
  background-color: #f8f9fa;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.toggle-icon {
  font-size: 0.8em;
  color: #999;
}

.card-content {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.summary {
  color: #666;
  line-height: 1.6;
  font-size: 0.9em;
}

.ref-link {
  display: inline-block;
  margin-top: 8px;
  color: #007aff;
  font-size: 0.85em;
  text-decoration: none;
}

/* Thinking container styles */
.thinking-container {
  background-color: #f9f9f9;
  border-left: 3px solid #aaa;
  padding: 0;
  margin-bottom: 16px;
  border-radius: 0 6px 6px 0;
  color: #505050;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.thinking-container.collapsed {
  background-color: #f5f5f5;
}

.thinking-header {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background-color: #fcfcfc;
  border-bottom: 1px solid #eee;
  user-select: none;
}

.thinking-header:hover {
  background-color: #f5f5f5;
}

.thinking-title {
  font-size: 0.85em;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.thinking-toggle {
  font-size: 0.8em;
  color: #999;
  padding: 2px 8px;
  border-radius: 10px;
  background-color: #f0f0f0;
}

.thinking-content {
  padding: 12px 16px;
  white-space: pre-wrap;
  transition: opacity 0.3s ease;
  opacity: 1;
}

/* Add animation effects for content toggling */
.thinking-container .thinking-content[style*="display: none"] {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
}

.thinking-container p {
  margin: 8px 0;
  line-height: 1.5;
  font-size: 0.95em;
}

.thinking-container code {
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #e83e8c;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

.thinking-container pre {
  background-color: #222;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
  border: none;
  color: #fff;
}

.thinking-container pre code {
  background-color: transparent;
  padding: 0;
  color: #eee;
  text-shadow: 0 1px rgba(0, 0, 0, 0.3);
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  line-height: 1.5;
}

.search-plan-container {
  background-color: #f5f5f5;
  /* 浅灰色背景 */
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
}

.search-plan-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.search-plan-title {
  font-weight: 500;
  color: #333;
}

.search-result-title {
  font-weight: 500;
  color: #333;
}

.toggle-icon {
  font-size: 0.9em;
  color: #666;
}

.search-plan-content {
  margin-top: 8px;
  color: #666;
  /* 内容文字灰色 */
}

.role-card {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px 28px;
  margin-bottom: 28px;
  border: 1.5px solid #e4e7ed;
  line-height: 2.1;
  min-height: 80px;
  font-size: 18px;
}

.expert-icon {
  font-size: 20px;
  margin-right: 10px;
  font-style: normal;
}

.role-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-title {
  font-size: 12px;
  color: #909399;
}

.role-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 确保消息气泡宽度适应新卡片 */
.message-bubble {
  max-width: 85%;
  overflow: visible;
}

/* Add keyword highlighting */
.thinking-container pre code .keyword {
  color: #f92672;
}

.thinking-container pre code .string {
  color: #a6e22e;
}

.thinking-container pre code .function {
  color: #66d9ef;
}

.thinking-container pre code .comment {
  color: #75715e;
}

/* Re-add list styling */
.thinking-container ul,
.thinking-container ol {
  padding-left: 20px;
  margin: 8px 0;
}

.thinking-container li {
  margin: 4px 0;
  line-height: 1.5;
}

/* Enhance blockquote styling */
.thinking-container blockquote {
  border-left: 3px solid #aaa;
  padding: 10px 15px;
  margin: 10px 0;
  background-color: rgba(170, 170, 170, 0.05);
  color: #505050;
  font-style: italic;
  border-radius: 0 4px 4px 0;
}

.role-cards-row {
  display: flex;
  flex-direction: row;
  gap: 12px;
  /* 卡片间距 */
  margin-bottom: 12px;
  flex-wrap: wrap;
  /* 超出自动换行 */
}

.expert-answer {
  margin-top: 6px;
  color: #333;
  font-size: 13px;
  background: #f8f8f8;
  border-radius: 4px;
  padding: 6px 8px;
}

.answer-label {
  color: #888;
  font-size: 12px;
  margin-right: 4px;
}

.analysis-block {
  /* 移除蓝色背景和左侧色条 */
  background: none;
  border-left: none;
  border-radius: 0;
  padding: 0;
  font-size: 16px;
}

.analysis-label {
  color: #1976d2;
  font-weight: bold;
  margin-right: 8px;
}

.analysis-content {
  color: #333;
}

.expert-markdown ul,
.expert-markdown ol {
  padding-left: 0 !important;
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.expert-markdown li {
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.expert-swiper-container {
  width: 100%;
  overflow: visible;
  /* 不再需要横向滚动 */
  position: relative;
  margin-bottom: 16px;
}

.expert-swiper {
  display: flex;
  flex-wrap: wrap;
  column-gap: 16px;
  row-gap: 8px;
  width: 100%;
  overflow: visible;
}

.expert-slide {
  flex: 0 0 calc(50% - 8px);
  max-width: calc(50% - 8px);
  box-sizing: border-box;
  /* 移除 margin-bottom，避免与 row-gap 冲突 */
}

@media (max-width: 600px) {
  .expert-slide {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

.expert-pagination {
  display: none !important;
}

.expert-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1.5px solid #e4e7ed;
  margin-bottom: 24px;
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.expert-header {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  padding: 18px 24px 12px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.expert-icon {
  font-size: 22px;
  margin-right: 10px;
}

.expert-title {
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
}

.expert-search-block {
  padding: 12px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #f8f9fa;
}

.search-header {
  cursor: pointer;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.toggle-icon {
  font-size: 12px;
  color: #868e96;
  margin-right: 8px;
}

.search-summary {
  color: #666;
  font-size: 0.95em;
  margin-bottom: 6px;
}

.search-content {
  margin-left: 18px;
  margin-bottom: 8px;
}

.result-item {
  margin-bottom: 4px;
}

.result-link {
  color: #228be6;
  text-decoration: none;
  font-size: 14px;
}

.expert-answer-block {
  padding: 20px 24px 24px 24px;
}

.answer-title {
  font-size: 15px;
  font-weight: bold;
  color: #ff6700;
  margin-bottom: 10px;
}

.answer-content {
  color: #222;
  font-size: 15px;
  line-height: 1.7;
}

.expert-markdown {
  padding-left: 0 !important;
  margin-left: 0 !important;
  line-height: 1.9;
  border-radius: 4px;
  margin-top: 6px;
  font-size: 15px;
  color: #222;
}

.expert-markdown :deep(h1),
.expert-markdown :deep(h2),
.expert-markdown :deep(h3) {
  font-size: 15px;
}

.expert-ref-toggle-block {
  padding: 0 24px 0 24px;
  background: none;
  border: none;
  border-radius: 0;
  margin-top: 8px;
  margin-bottom: 0;
}

.ref-toggle-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-weight: 500;
  color: #333;
  margin-bottom: 0;
  padding: 10px 12px 6px 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: background 0.2s;
}

.ref-toggle-header:hover {
  background: #f0f4ff;
}

.ref-toggle-text {
  font-size: 14px;
  color: #1976d2;
  user-select: none;
}

.ref-toggle-btn {
  font-size: 15px;
  color: #1976d2;
  margin-left: 12px;
  user-select: none;
}

.expert-ref-list {
  padding: 0 0 8px 0;
  background: none;
  border: none;
  border-radius: 0;
}

.expert-opinion-label {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 8px;
  margin-left: 0;
  margin-top: 20px;
}

.expert-opinion-icon {
  font-size: 20px;
  margin-right: 6px;
}

.analysis-label-block {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  margin-top: 20px;
}

.analysis-label-icon {
  font-size: 18px;
  margin-right: 6px;
  color: #1976d2;
}

.analysis-label-text {
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
}

.summary-label-block {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  margin-top: 20px;
}

.summary-label-icon {
  font-size: 20px;
  margin-right: 6px;
  color: #1976d2;
  font-style: normal; /* Added to match ThinkingView */
}

.summary-label-text {
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
}

.all-experts-card {
  background: none !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 18px;
}

.all-experts-header {
  display: flex;
  align-items: center;
  font-size: 26px;
  font-weight: bold;
  color: #2176ff;
  margin-bottom: 10px;
  margin-left: 2px;
}

.all-experts-icon {
  font-size: 32px;
  margin-right: 8px;
  color: #2176ff;
}

.all-experts-title {
  font-size: 26px;
  font-weight: bold;
  color: #2176ff;
}

.all-experts-avatars {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
  margin-left: 2px;
}

.expert-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #f2f6fc;
  box-shadow: 0 2px 8px rgba(33, 118, 255, 0.08);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expert-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  display: block;
}

.all-experts-desc {
  font-size: 15px;
  color: #888;
  font-weight: 500;
  margin-left: 2px;
  margin-bottom: 0;
  margin-top: 8px;
}

.all-experts-names {
  color: #888;
  font-size: 15px;
  font-weight: 500;
}

.experts-assign-block {
  margin-bottom: 24px;
}

.experts-avatars {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
}

.expert-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #f2f6fc;
  box-shadow: 0 2px 8px rgba(33, 118, 255, 0.08);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expert-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  display: block;
}

.experts-desc {
  font-size: 15px;
  color: #888;
  font-weight: 500;
  margin-bottom: 0;
  margin-top: 8px;
}

.experts-names {
  color: #888;
  font-size: 15px;
  font-weight: 500;
}

.expert-avatar-icon {
  font-size: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.experts-assign-label {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 8px;
  margin-left: 0;
  margin-top: 20px;
}

.experts-assign-icon {
  font-size: 20px;
  margin-right: 6px;
  color: #1976d2;
}

.experts-assign-title {
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
}

.experts-assign-icon,
.expert-opinion-icon,
.analysis-label-icon {
/* .summary-label-icon removed as it's now in ThinkingView.vue */
  font-style: normal;
}

.expert-markdown p, /* .summary-content p removed */
.response-text p {
  margin: 0 0 16px 0;
}

/* Styles for thinking blocks are now in ThinkingView.vue */
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
  overflow: hidden;
  /* Prevent scrolling on container level */
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
  display: none;
  /* Hide the mobile header */
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
  display: none;
  /* Hide the chat header */
}

.back-button,
.add-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  cursor: pointer;
}

.back-icon,
.add-icon {
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
  padding-bottom: 100px;
  /* Increase bottom padding to create more space above input area */
  -webkit-overflow-scrolling: touch;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* Center content horizontally */
}

/* Container for each message to maintain consistent width */
.messages-container {
  width: 100%;
  max-width: 800px;
  /* Maximum width on large screens */
  min-width: 320px;
  /* Minimum width on small screens */
  margin: 0 auto;
  padding: 0 16px;
  /* Add some padding on the sides */
}

/* Media queries for responsive design */
@media (max-width: 768px) {
  .messages-container {
    width: 100%;
    padding: 0 12px;
  }

  .message-bubble {
    max-width: 90%;
    /* Allow bubbles to be wider on small screens */
  }
}

@media (min-width: 1200px) {
  .messages-container {
    max-width: 900px;
    /* Slightly wider on very large screens */
  }
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
  max-width: 85%;
  /* Slightly reduced max width for better proportions */
  min-width: 0;
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  line-height: 1.4;
  overflow-wrap: break-word;
}

.multi-agent-response {
  min-width: 70%;
  /* 初始固定最小宽度（可根据实际需求调整数值） */
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

.mi-logo,
.spacer-logo {
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

search-header {
  cursor: pointer;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;

  &:hover {
    background-color: #e8e8e8;
  }
}

.toggle-icon {
  margin-right: 8px;
  font-size: 0.8em;
  color: #666;
}

.search-content {
  margin-top: 8px;
  padding-left: 24px;
  border-left: 2px solid #eee;
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
  max-width: 800px;
  /* Match message container max width */
  margin: 12px auto;
  background-color: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
  height: 4px;
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
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chat-input .input-container,
.chat-input .bottom-toolbar {
  width: 100%;
  max-width: 800px;
}

@media (min-width: 1200px) {

  .chat-input .input-container,
  .chat-input .bottom-toolbar {
    max-width: 900px;
  }
}

.input-container {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 24px;
  padding: 4px 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.plus-button,
.voice-button {
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
  padding: 0;
  width: 100%;
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

.search-plan-title {
  display: inline-block;
  margin-bottom: 12px;
  padding: 6px 12px;
  background: #f0f8ff;
  border-radius: 6px;
  color: #1976d2;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

.search-results-container {
  margin: 12px 0;
  border-radius: 12px;
  background: #f8f9fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-item {
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.search-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-header:hover {
  background: #f1f3f5;
}

.toggle-icon {
  font-size: 12px;
  color: #868e96;
  margin-right: 10px;
  transition: transform 0.2s ease;
}

.search-query {
  font-weight: 500;
  color: #212529;
  font-size: 14px;
}

.search-content {
  margin-top: 8px;
  padding: 8px 0;
  border-top: 1px solid #e9ecef;
}

.result-item {
  padding: 8px 12px;
  margin: 4px 0;
  background: white;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.result-item:hover {
  transform: translateX(4px);
}

.result-link {
  color: #228be6;
  text-decoration: none;
  font-size: 14px;
  line-height: 1.4;
}

.result-link:hover {
  text-decoration: underline;
  color: #1971c2;
}

/* Quick action buttons */
.quick-actions {
  width: 100%;
  max-width: 800px;
  /* Match message container max width */
  margin: 0 auto 20px auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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
  margin-right: 50px;
  /* Make room for the drag handle */
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
  touch-action: none;
  /* Improves touch handling */
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
  user-select: none;
  /* Prevent text selection during drag */
}

.expand-button,
.close-button {
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
  text-decoration: none;
  /* Remove underline */
  cursor: pointer;
  background-color: rgba(255, 103, 0, 0.1);
  /* Light orange background */
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

/* Settings Button */
.settings-button {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  border: 1px solid #eee;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s ease;
}

.settings-button:hover {
  transform: scale(1.05);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.settings-icon {
  font-size: 20px;
}

/* Settings Modal */
.settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.settings-modal-content {
  width: 90%;
  max-width: 400px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-modal-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.settings-modal-body {
  padding: 20px;
}

.settings-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background-color: #f8f8f8;
}

.form-group input:focus {
  border-color: #ff6700;
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 103, 0, 0.1);
}

.form-text {
  font-size: 12px;
  color: #666;
  margin-top: 6px;
  display: block;
}

.save-button {
  background-color: #ff6700;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  align-self: flex-end;
}

.save-button:hover {
  background-color: #e65c00;
}

.save-button:active {
  transform: translateY(1px);
}

.title-link {
  color: #007bff;
  text-decoration: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin: 1rem 0;

  &:hover {
    text-decoration: underline;
  }
}

.preview-frame {
  width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-top: 8px;
  transition: height 0.3s ease;
}

.arrow-icon {
  margin-left: 8px;
  font-size: 0.8em;
  transition: transform 0.3s ease;

  &.rotate-180 {
    transform: rotate(180deg);
  }
}

/* 角色卡片 */
.role-card {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px 28px;
  margin-bottom: 28px;
  border: 1.5px solid #e4e7ed;
  line-height: 2.1;
  min-height: 80px;
  font-size: 18px;
}

.role-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 搜索结果 */
.search-results-container {
  margin: 1rem 0;
  border-radius: 8px;
}

.search-item {
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 10px;
}

.search-link {
  color: #333;
  text-decoration: none;
}

.search-title {
  font-weight: 500;
  color: #1890ff;
}

.search-content {
  color: #666;
  font-size: 0.9em;
  margin: 0.5rem 0;
}

.search-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8em;
  color: #999;
}

/* 文本回答 */
.answer-text {
  margin-top: 1rem;
  padding: 0.8rem;
  background: #f8f9fa;
  border-radius: 4px;
  line-height: 1.6;
}

/* 统一列表缩进，保证小圆点和正文内容左对齐且美观 */
.summary-content ul,
.summary-content ol,
.expert-markdown ul,
.expert-markdown ol {
  padding-left: 2em !important;
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.summary-content li,
.expert-markdown li {
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.all-experts-card {
  background: none !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 18px;
}

.all-experts-list {
  padding: 0 0 24px 0 !important;
}

/* 为思考过程中的引用块添加样式 */
.thinking-block-inner-content blockquote {
  border-left: 4px solid #007bff !important;
  background-color: #f8f9fa !important;
  padding: 10px 12px !important;
  margin: 8px 0 !important;
  color: #666 !important;
  font-size: 0.9em !important;
}

/* 确保思考过程中的段落样式 */
.thinking-block-inner-content blockquote p {
  margin-bottom: 0.5em !important;
  line-height: 1.5 !important;
}

/* 针对以 | 开头的段落添加特殊样式 */
.thinking-block-inner-content blockquote p::first-letter {
  margin-right: 3px !important;
  color: #999 !important;
}

/* Styles related to .summary-content > p etc. are removed as they are now in ThinkingView.vue */
</style>
