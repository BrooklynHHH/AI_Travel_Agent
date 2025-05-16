<template>
  <div class="chat-container">
    <!-- 浮层组件 -->
    <ImageViewer
      v-model:show="showImageViewer"
      :images="viewerImages"
      v-model:currentIndex="currentImageIndex"
      :keyword="currentImageKeyword"
    />
    <ProductWindow
      v-model:show="showProductWindow"
      :productName="productName"
      :productUrl="productUrl"
      v-model:isFullscreen="isFullscreen"
      v-model:windowHeight="windowHeight"
      :isLoading="isLoading"
      :iframeKey="iframeKey"
      @iframe-load="onIframeLoad"
    />
    <SettingsModal
      v-model:show="showSettingsModal"
      :apiKey="apiKeyInput"
      @save="saveApiKey"
    />
    <VideoPlayer
      v-model:show="showVideoPlayer"
      :videoUrl="videoUrl"
      :videoTitle="videoTitle"
      :videoAvatar="videoAvatar"
      :videoLikeCount="videoLikeCount"
      :videoCommentCount="videoCommentCount"
      :videoDescription="videoDescription"
    />

    <!-- Progress bar (visible when loading or streaming) -->
    <div v-if="isLoading || isStreaming" class="progress-container top-progress">
      <div class="progress-bar"></div>
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

    <!-- Settings Button -->
    <button class="settings-button" @click="openSettingsModal">
      <span class="settings-icon">⚙️</span>
    </button>
    
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
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper" style="width: 100%;">
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
              <!-- 相关图片展示区域 -->
              <div v-if="message.relatedImages && message.relatedImages.length > 0" class="related-images-container">
                <p class="related-images-title">相关图片</p>
                <div class="related-images-grid">
                  <div 
                    v-for="(image, imgIndex) in message.relatedImages" 
                    :key="imgIndex" 
                    class="related-image-item"
                    @click="openImageInProductWindow(image.url, image.keyword)"
                  >
                    <img :src="image.url" :alt="image.keyword" class="related-image" />
                  </div>
                </div>
              </div>
              
              <div v-if="message.streaming" class="response-text">
                <div v-html="renderMarkdown(message.content)"></div><span class="cursor">|</span>
              </div>
              <div v-else class="response-text" v-html="renderMarkdown(message.content)"></div>

              <div v-if="message.videoThumbnails" v-html="message.videoThumbnails"></div>
              
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
      
<div class="bottom-toolbar" style="display: none;">
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import ImageViewer from '../components/modals/ImageViewer.vue';
import ProductWindow from '../components/modals/ProductWindow.vue';
import SettingsModal from '../components/modals/SettingsModal.vue';
import VideoPlayer from '../components/modals/VideoPlayer.vue';
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

/** 视频播放器浮层状态 */
const showVideoPlayer = ref(false);
const videoUrl = ref('');
const videoTitle = ref('');
const videoAvatar = ref('');
const videoName = ref('');
const videoLikeCount = ref(0);
const videoCommentCount = ref(0);
const videoDescription = ref('');

// Product window state
const showProductWindow = ref(false);
const productName = ref('');
const productUrl = ref('');
const isFullscreen = ref(false);
const windowHeight = ref(50); // Default height is 50%
const iframeKey = ref(0); // 用于强制重新加载iframe
const isLoading = ref(false); // 加载状态

// iframe加载事件处理
const onIframeLoad = () => {
  console.log('Iframe加载完成');
  isLoading.value = false;
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
  let processedContent = content.replace(regex, '[$1](aisearch://product/$2)');
  
  // Also handle other aisearch protocols to ensure complete URLs are captured
  // For jump links
  const jumpRegex = /<([^>]+)>\(aisearch:\/\/jump\/([^)]+)\)/g;
  processedContent = processedContent.replace(jumpRegex, '[$1](aisearch://jump/$2)');
  
  // For image jump links
  const imgJumpRegex = /<([^>]+)>\(aisearch:\/\/imgjump\/([^)]+)\)/g;
  processedContent = processedContent.replace(imgJumpRegex, '[$1](aisearch://imgjump/$2)');
  
  return processedContent;
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
      console.log('Found jump URL:', jumpUrl);
      token.attrPush(['data-jump-url', jumpUrl]);
    }
    // Check if it's an image jump link
    else if (href.startsWith('aisearch://imgjump/')) {
      const imgJumpUrl = href.substring('aisearch://imgjump/'.length);
      console.log('Found image jump URL:', imgJumpUrl);
      token.attrPush(['data-imgjump-url', imgJumpUrl]);
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

// 监听iframe内部的消息，处理链接点击事件
const handleIframeMessages = (event) => {
  // 安全检查，确保消息来源是我们期望的
  if (event.data && event.data.type === 'linkClick') {
    console.log('收到iframe链接点击:', event.data.url);
    
    // 使用原生方式处理链接
    if (event.data.url) {
      const url = event.data.url;
      
      // 更新浮窗URL
      productName.value = '外部链接';
      productUrl.value = url.startsWith('/') ? url : (url.startsWith('http') ? url : `https://${url}`);
      
      // 刷新浮窗内容
      nextTick(() => {
        console.log('刷新浮窗内容为:', productUrl.value);
      });
    }
  }
};

// 添加全局事件监听
onMounted(() => {
  window.addEventListener('message', handleIframeMessages);
});

// 移除事件监听以防内存泄漏
onUnmounted(() => {
  window.removeEventListener('message', handleIframeMessages);
});

/** 浮层图片查看器状态 */
const showImageViewer = ref(false);
const viewerImages = ref([]);
const currentImageIndex = ref(0);
const currentImageKeyword = ref('');

/** 打开视频播放器，支持更多信息 */
const openVideoPlayer = (url, title = '视频播放', opts = {}) => {
  videoUrl.value = url;
  videoTitle.value = title;
  videoAvatar.value = opts.avatar || '';
  videoName.value = opts.name || '';
  videoLikeCount.value = opts.likeCount || 0;
  videoCommentCount.value = opts.commentCount || 0;
  videoDescription.value = opts.description || '';
  showVideoPlayer.value = true;
  document.body.style.overflow = 'hidden';
};

const openImageInProductWindow = (imageUrl, keyword) => {
  // 查找当前消息中的所有图片
  let currentImages = [];
  let imageIndex = 0;
  for (const message of messages.value) {
    if (message.relatedImages && message.relatedImages.length > 0) {
      const index = message.relatedImages.findIndex(img => img.url === imageUrl);
      if (index !== -1) {
        currentImages = message.relatedImages;
        imageIndex = index;
        break;
      }
    }
  }
  // 直接设置 viewerImages、currentImageIndex、currentImageKeyword，ImageViewer 组件通过 v-model 绑定
  viewerImages.value = currentImages;
  currentImageIndex.value = imageIndex;
  currentImageKeyword.value = keyword || '相关图片';
  showImageViewer.value = true;
};

const handleContentClick = (event) => {
  // Check if clicked element is a video thumbnail or one of its children
  const videoThumbnail = event.target.closest('.mi-video-thumbnail');
  if (videoThumbnail) {
    const dpLink = videoThumbnail.getAttribute('data-dp-link');
    const avatar = videoThumbnail.getAttribute('data-avatar') || '';
    const name = videoThumbnail.getAttribute('data-name') || '';
    const likeCount = Number(videoThumbnail.getAttribute('data-like-count')) || 0;
    const commentCount = Number(videoThumbnail.getAttribute('data-comment-count')) || 0;
    const description = videoThumbnail.getAttribute('data-description') || '';
    if (dpLink) {
      // 用浮层播放视频，带上更多信息
      openVideoPlayer(dpLink, '', {
        avatar,
        name,
        likeCount,
        commentCount,
        description
      });
    }
    return;
  }
  
  // Check if clicked element is an aisearch link (with the special-link class)
  if (event.target.tagName === 'A' && event.target.classList.contains('special-link')) {
    event.preventDefault();
    
    // Check if it's a jump link (to external URL)
    const jumpUrl = event.target.getAttribute('data-jump-url');
    if (jumpUrl) {
      console.log('处理跳转链接:', jumpUrl);
      
      // Extract the URL and use it in the floating window
      productName.value = '外部链接';  // Set a generic title for the header
      
      // 确保URL格式正确 - 处理完整的URL
      let actualUrl = jumpUrl;
      // 移除可能的引号或其他包装字符
      actualUrl = actualUrl.replace(/^["']+|["']+$/g, '');
      
      if (!actualUrl.startsWith('http://') && !actualUrl.startsWith('https://')) {
        actualUrl = 'https://' + actualUrl;
      }
      
      console.log('使用URL:', actualUrl);
      
      // 使用代理处理第一次访问，避免跨域问题
      if (actualUrl.includes('baidu.com')) {
        // 保持百度原始URL结构，仅更换域名部分为代理
        // 并添加一个特殊参数，标记这是通过我们的应用打开的
        const proxyUrl = actualUrl.replace(/https?:\/\/([^/]*\.)?baidu\.com/, '/baidu-proxy');
        console.log('使用百度代理URL:', proxyUrl);
        
        // 添加特殊参数，告知我们的代理这是一个百度搜索请求
        // 在vue.config.js中会根据这个参数特殊处理
        productUrl.value = `${proxyUrl}${proxyUrl.includes('?') ? '&' : '?'}_source=app`;
      } else {
        // 对于非百度域名，使用我们的通用外部代理
        const proxyUrl = `/external-proxy/${actualUrl}`;
        console.log('使用外部代理URL:', proxyUrl);
        productUrl.value = proxyUrl;
      }
      
      showProductWindow.value = true;
    }
    // Check if it's an image jump link
    else if (event.target.hasAttribute('data-imgjump-url')) {
      const imgJumpUrl = event.target.getAttribute('data-imgjump-url');
      console.log('处理图片跳转链接:', imgJumpUrl);
      
      // Extract the URL and use it in the floating window
      productName.value = '图片搜索';  // Set a title for the header
      
      // 确保URL格式正确 - 处理完整的URL
      let actualUrl = imgJumpUrl;
      // 移除可能的引号或其他包装字符
      actualUrl = actualUrl.replace(/^["']+|["']+$/g, '');
      
      if (!actualUrl.startsWith('http://') && !actualUrl.startsWith('https://')) {
        actualUrl = 'https://' + actualUrl;
      }
      
      console.log('使用图片搜索URL:', actualUrl);
      
      // 直接使用外部代理处理图片搜索请求，不使用baidu-proxy
      // 这样可以确保原始URL的完整性，包括移动版百度的域名和路径
      
      let proxyUrl;
      // 解析URL以正确处理中文参数
      try {
        const urlObj = new URL(actualUrl);
        // 保留原始查询参数，确保中文字符正确编码
        const searchParams = new URLSearchParams(urlObj.search);
        
        // 特别处理word参数，确保中文字符正确编码
        if (searchParams.has('word')) {
          const wordValue = searchParams.get('word');
          console.log('原始word参数值:', wordValue);
          // 重新设置word参数，确保正确编码
          searchParams.set('word', wordValue);
        }
        
        // 构建新的URL路径和查询字符串
        const newPath = urlObj.pathname;
        const newSearch = searchParams.toString();
        proxyUrl = `/external-proxy/${urlObj.origin}${newPath}?${newSearch}`;
        console.log('使用外部代理URL (图片搜索):', proxyUrl);
      } catch (e) {
        console.error('URL解析错误:', e);
        // 如果URL解析失败，回退到原始方法
        proxyUrl = `/external-proxy/${actualUrl}`;
        console.log('使用外部代理URL (图片搜索-回退):', proxyUrl);
      }
      
      // 清除当前浮窗内容并显示加载状态
      productUrl.value = '';
      isLoading.value = true;
      
      // 增加iframeKey使iframe强制重新加载
      iframeKey.value++;
      
      // 显示产品窗口
      showProductWindow.value = true;
      
      // 稍微延迟设置URL，确保浮窗完全初始化
      setTimeout(() => {
        productUrl.value = proxyUrl;
        console.log('浮窗URL已设置为:', productUrl.value);
        
        // 设置超时处理，如果30秒后仍未加载完成，重置加载状态
        setTimeout(() => {
          if (isLoading.value) {
            console.log('加载超时，重置状态');
            isLoading.value = false;
          }
        }, 30000);
      }, 300);
    }
    // Check if it has a product URL
    else if (event.target.hasAttribute('data-product-url')) {
      const productUrlAttr = event.target.getAttribute('data-product-url');
      // 使用链接的文本内容（产品名称）作为浮窗标题
      productName.value = event.target.textContent || '产品详情';
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
  const savedApiKey = getCookie('api_key');
  if (savedApiKey) {
    apiKeyInput.value = savedApiKey;
  }
  showSettingsModal.value = true;
};

const closeSettingsModal = () => {
  showSettingsModal.value = false;
};

// Cookie utility functions
const setCookie = (name, value, days = 365) => {
  const d = new Date();
  d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
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

const saveApiKey = () => {
  // Validate the API key format (app-xxxx)
  if (!apiKeyInput.value || !apiKeyInput.value.match(/^app-[a-zA-Z0-9]+$/)) {
    alert('请输入正确格式的API Key (app-xxxx)');
    return;
  }
  
  // Save to cookie
  setCookie('api_key', apiKeyInput.value);
  
  // Close the settings modal
  closeSettingsModal();
  
  // Provide feedback to user
  alert('API Key 已保存');
};

// Data
const currentTime = ref('');
const userInput = ref('');
const chatContent = ref(null);
// isLoading在前面已经声明，此处不再重复声明
const streamingMessage = ref('');
const streamingMessageFollowUp = ref(null);
const conversationId = ref('');
const isStreaming = ref(false);
// Store about_mi data during streaming
const aboutMiData = ref(null);

// 存储product_urls数据（缓存id不为null的项）
const cachedProductUrls = ref([]);

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
  console.log('处理跟进搜索:', optionText);
  
  // 端口可能变化，因此使用相对路径
  const searchUrl = `/baidu-proxy/s?wd=${encodeURIComponent(optionText)}`;
  console.log('生成的搜索URL:', searchUrl);
  
  // 清除当前浮窗内容并显示加载状态
  productUrl.value = '';
  isLoading.value = true;
  
  // 设置浮窗标题和显示状态
  productName.value = optionText;
  showProductWindow.value = true;
  
  // 增加iframeKey使iframe强制重新加载
  iframeKey.value++;
  
  // 使用较长的延迟确保DOM已更新
  setTimeout(() => {
    productUrl.value = searchUrl;
    console.log('浮窗URL已设置为:', productUrl.value);
    
    // 设置超时处理，如果30秒后仍未加载完成，重置加载状态
    setTimeout(() => {
      if (isLoading.value) {
        console.log('加载超时，重置状态');
        isLoading.value = false;
        // 显示错误信息
        productUrl.value = '';
        productName.value = '加载失败，请重试';
      }
    }, 30000);
  }, 300);
};

// Using safeJsonParse from streamUtils.js

// Flag to track if this is the first message
const isFirstMessage = ref(true);

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  const userMessage = userInput.value;
  console.log('Message sent:', userMessage);
  console.log('userInput.value:', userInput.value);
  
  // Add user message to messages array
  messages.value.push({
    role: 'user',
    content: userMessage
  });
  console.log('messages.value:', JSON.stringify(messages.value));
  
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
    
    // 从cookie中获取API key，如果不存在则使用默认值
    const savedApiKey = getCookie('api_key') || 'app-u456N01sF3Us7rg7QBpcOI2R';
    
    const headers = {
      'Authorization': `Bearer ${savedApiKey}`,
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
          let newContent = data.answer;
          
          // 添加处理后的内容
          streamingMessage.value += newContent;
          
          // 如果有缓存的产品数据，尝试匹配并替换streamingMessage.value中的产品名称为链接
          if (cachedProductUrls.value && cachedProductUrls.value.length > 0) {
            // 遍历所有缓存的产品
            cachedProductUrls.value.forEach(product => {
              if (product.name && product.id) {
                // 创建一个正则表达式来匹配产品名称
                // 使用 `\\b` 确保匹配整个单词，避免部分匹配
                const regex = new RegExp(product.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                
                // 创建一个正则表达式来匹配产品名称，但排除已经在链接中的产品名称
                // 使用否定前瞻（negative lookahead）确保不匹配已经是链接格式的文本
                const linkPattern = new RegExp(`\\[${product.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\]\\(aisearch://product/https://m.mi.com/commodity/detail/${product.id}\\)`, 'g');
                
                // 检查是否已经有替换过的链接
                if (!linkPattern.test(streamingMessage.value)) {
                  // 只替换那些不在链接中的产品名称
                  const oldContent = streamingMessage.value;
                  streamingMessage.value = streamingMessage.value.replace(regex, `[${product.name}](aisearch://product/https://m.mi.com/commodity/detail/${product.id})`);
                  
                  // 只有在内容确实被替换时才输出日志
                  if (oldContent !== streamingMessage.value) {
                    console.log('处理后的内容:', streamingMessage.value);
                  }
                }
              }
            });
          }
          
          // 更新消息内容
          messages.value[lastIndex].content = streamingMessage.value;
          
          // 检查是否包含aisearch://imgjump/格式的链接
          // 使用更宽松的正则表达式来捕获完整的URL，直到空格、括号结束或行尾
          const imgJumpRegex = /aisearch:\/\/imgjump\/([^\s)]+)/;
          const jumpRegex = /aisearch:\/\/jump\/([^\s)]+)/;
          
          // 先检查图片跳转链接
          const imgMatch = data.answer.match(imgJumpRegex);
          const jumpMatch = data.answer.match(jumpRegex);
          
          // 优先处理图片跳转链接
          const match = imgMatch || jumpMatch;
          
          if (match && match[1]) {
            const imgJumpUrl = match[1];
            console.log('检测到图片跳转链接，自动打开:', imgJumpUrl);
            
            // 确保URL格式正确 - 处理完整的URL
            let actualUrl = imgJumpUrl;
            // 移除可能的引号或其他包装字符
            actualUrl = actualUrl.replace(/^["']+|["']+$/g, '');
            
            if (!actualUrl.startsWith('http://') && !actualUrl.startsWith('https://')) {
              actualUrl = 'https://' + actualUrl;
            }
            
            // 使用外部代理处理图片搜索请求
            let proxyUrl;
            
            // 解析URL以正确处理中文参数
            try {
              const urlObj = new URL(actualUrl);
              // 保留原始查询参数，确保中文字符正确编码
              const searchParams = new URLSearchParams(urlObj.search);
              
              // 特别处理word参数，确保中文字符正确编码
              if (searchParams.has('word')) {
                const wordValue = searchParams.get('word');
                console.log('原始word参数值:', wordValue);
                // 重新设置word参数，确保正确编码
                searchParams.set('word', wordValue);
              }
              
              // 构建新的URL路径和查询字符串
              const newPath = urlObj.pathname;
              const newSearch = searchParams.toString();
              proxyUrl = `/external-proxy/${urlObj.origin}${newPath}?${newSearch}`;
              console.log('使用外部代理URL (图片搜索):', proxyUrl);
            } catch (e) {
              console.error('URL解析错误:', e);
              // 如果URL解析失败，回退到原始方法
              proxyUrl = `/external-proxy/${actualUrl}`;
              console.log('使用外部代理URL (图片搜索-回退):', proxyUrl);
            }
            
            // 设置浮窗标题和显示状态
            productName.value = '图片搜索';
            
            // 清除当前浮窗内容并显示加载状态
            productUrl.value = '';
            isLoading.value = true;
            
            // 增加iframeKey使iframe强制重新加载
            iframeKey.value++;
            
            // 显示产品窗口
            showProductWindow.value = true;
            
            // 稍微延迟设置URL，确保浮窗完全初始化
            setTimeout(() => {
              productUrl.value = proxyUrl;
              console.log('浮窗URL已设置为:', productUrl.value);
              
              // 设置超时处理，如果30秒后仍未加载完成，重置加载状态
              setTimeout(() => {
                if (isLoading.value) {
                  console.log('加载超时，重置状态');
                  isLoading.value = false;
                }
              }, 30000);
            }, 300);
          }
          
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
        
        // Handle about_mi event
        if (data.event === "node_finished" && data.data && data.data.title === "about_mi") {
          console.log('About MI content detected:', data.data);
          
          if (data.data.outputs) {
            // Store thumbnail, dp, and extra video info for later use
            aboutMiData.value = {
              thumbnail: data.data.outputs.thumbnail,
              dp: data.data.outputs.dp,
              avatar: data.data.outputs.avatar || '',
              name: data.data.outputs.name || '',
              likeCount: data.data.outputs.likeCount || 0,
              commentCount: data.data.outputs.commentCount || 0,
              description: data.data.outputs.title || ''
            };
            
            console.log('Stored about_mi data:', aboutMiData.value);
          }
        }
        
        // 处理product_urls节点
        if (data.event === "iteration_completed" && data.data && data.data.title === "product_urls") {
          console.log('Product URLs detected:', data.data);
          
          if (data.data.outputs && Array.isArray(data.data.outputs.output)) {
            console.log('Product URLs data received:', data.data.outputs.output);
            
            // 筛选出id不为null的项
            const validProducts = data.data.outputs.output.filter(item => item.id !== null);
            
            if (validProducts.length > 0) {
              // 缓存有效的产品数据
              cachedProductUrls.value = validProducts;
              console.log('缓存的产品数据:', cachedProductUrls.value);
              console.log('缓存的产品数量:', cachedProductUrls.value.length);
              console.log('缓存的产品详情:');
              cachedProductUrls.value.forEach((product, index) => {
                console.log(`  ${index + 1}. name: ${product.name}, id: ${product.id}`);
              });
            } else {
              console.log('没有找到id不为null的产品数据');
            }
          }
        }
        
        // 处理product_keyword节点
        if (data.event === "node_finished" && data.data && data.data.title === "product_keyword") {
          console.log('Product Keyword detected:', data.data);
          
          if (data.data.outputs) {
            try {
              // 解析outputs中的数据
              const outputData = typeof data.data.outputs === 'string' 
                ? JSON.parse(data.data.outputs) 
                : data.data.outputs;
              
              console.log('Product Keyword data parsed:', outputData);
              
              // 提取relate数组
              if (outputData.relate && Array.isArray(outputData.relate) && outputData.relate.length > 0) {
                console.log('Found relate keywords:', outputData.relate);
                
                // 遍历relate数组，调用API
                outputData.relate.forEach(async (relateKeyword) => {
                  console.log('Processing relate keyword:', relateKeyword);
                  
                  try {
                    // 调用API（使用blocking模式一次性获取结果）
                    const response = await fetch('https://mify-be.pt.xiaomi.com/api/v1/workflows/run', {
                      method: 'POST',
                      headers: {
                        'Authorization': 'Bearer app-WfbP069tyYjaP4VpUKS8M0EN',
                        'Content-Type': 'application/json'
                      },
                      body: JSON.stringify({
                        inputs: {
                          query: relateKeyword
                        },
                        response_mode: "blocking",
                        user: "abc-123"
                      })
                    });
                    
                    // 获取响应数据
                    const responseData = await response.json();
                    
                    // 处理响应数据
                    if (responseData.data && responseData.data.outputs && responseData.data.outputs.body) {
                      try {
                        // 第一次解析 - 解析body字段为JSON对象
                        const bodyData = typeof responseData.data.outputs.body === 'string' 
                          ? JSON.parse(responseData.data.outputs.body) 
                          : responseData.data.outputs.body;
                        
                        // 检查是否有answer字段
                        if (bodyData && bodyData.answer) {
                          // 第二次解析 - 因为answer是字符串形式的数组
                          let answerArray;
                          
                          try {
                            // 尝试将字符串answer解析为数组
                            if (typeof bodyData.answer === 'string') {
                              // 处理字符串数组表示
                              const answerStr = bodyData.answer.trim();
                              
                              // 检查是否是字符串形式的数组
                              if (answerStr.startsWith('[') && answerStr.endsWith(']')) {
                                // 解析为JavaScript数组
                                // 使用正则表达式匹配所有URL
                                const urlRegex = /'(http[^']+)'/g;
                                const urls = [];
                                let match;
                                
                                while ((match = urlRegex.exec(answerStr)) !== null) {
                                  urls.push(match[1]); // 添加捕获组1（URL部分）
                                }
                                
                                answerArray = urls;
                              } else {
                                // 不是数组形式，可能是单个URL
                                answerArray = [answerStr];
                              }
                            } else if (Array.isArray(bodyData.answer)) {
                              // 已经是数组，直接使用
                              answerArray = bodyData.answer;
                            } else {
                              // 不是期望的格式
                              console.log('Unexpected answer format:', bodyData.answer);
                              return;
                            }
                            
                            // 检查解析出的数组
                            if (answerArray && answerArray.length > 0) {
                              console.log('Found answer array for keyword:', relateKeyword, 'length:', answerArray.length);
                              
                              // 遍历answer数组，打印图片URL
                              // 创建一个存储关键词和图片链接的对象
                              const imageUrls = [];
                              
                              answerArray.forEach((item, index) => {
                                if (item && typeof item === 'string' && item.startsWith('http')) {
                                  console.log(`Image URL ${index + 1} for "${relateKeyword}":`, item);
                                  // 存储图片链接
                                  imageUrls.push({
                                    url: item,
                                    keyword: relateKeyword
                                  });
                                }
                              });
                              
                              // 如果找到了图片，存储到与当前关键词相关的图片数组中
                              if (imageUrls.length > 0) {
                                // 将图片链接与当前消息关联
                                if (!messages.value[lastIndex].relatedImages) {
                                  messages.value[lastIndex].relatedImages = [];
                                }
                                messages.value[lastIndex].relatedImages = 
                                  messages.value[lastIndex].relatedImages.concat(imageUrls);
                                  
                                console.log('已添加相关图片:', imageUrls.length);
                              }
                            }
                          } catch (parseAnswerError) {
                            console.error('Error parsing answer field:', parseAnswerError);
                          }
                        }
                      } catch (parseBodyError) {
                        console.error('Error parsing body field:', parseBodyError);
                      }
                    }
                  } catch (apiError) {
                    console.error('Error calling API for keyword:', relateKeyword, apiError);
                  }
                });
              } else {
                console.log('No relate keywords found in the response');
              }
            } catch (error) {
              console.error('Error processing product_keyword data:', error);
            }
          }
        }
      },
      onComplete: () => {
        console.log('Streaming response completed');
        
        // Add the about_mi thumbnail HTML to the message content if available
        if (aboutMiData.value && aboutMiData.value.thumbnail && aboutMiData.value.dp) {
          console.log('Adding about_mi thumbnail to message');
          
          // Create HTML for the thumbnail with play button overlay
          let thumbnailHtml = '';
          
          // Handle single thumbnail or multiple thumbnails
          const thumbnails = Array.isArray(aboutMiData.value.thumbnail) 
            ? aboutMiData.value.thumbnail 
            : [aboutMiData.value.thumbnail];
          
          thumbnails.forEach(imgUrl => {
            thumbnailHtml += `
              <div class="mi-video-thumbnail" data-dp-link="${aboutMiData.value.dp}"
                data-avatar="${aboutMiData.value.avatar || ''}"
                data-name="${aboutMiData.value.name || ''}"
                data-like-count="${aboutMiData.value.likeCount || 0}"
                data-comment-count="${aboutMiData.value.commentCount || 0}"
                data-description="${aboutMiData.value.description || ''}"
              >
                <img src="${imgUrl}" alt="Xiaomi Video" class="thumbnail-image">
                <div class="play-button-overlay">
                  <div class="play-button-icon">▶</div>
                </div>
              </div>
            `;
          });

          // 不再拼接到 streamingMessage.value，而是单独存储
          messages.value[lastIndex].videoThumbnails = thumbnailHtml;

          // Reset the about_mi data
          aboutMiData.value = null;

          // Scroll to bottom with new content
          nextTick(() => {
            scrollToBottom();
          });
        }
        
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
/* 视频信息区右侧绝对定位，垂直居中 */
.video-info-bar-custom-abs {
  position: absolute;
  top: 50%;
  right: 32px;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 10;
  pointer-events: none;
}
.video-info-right-custom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  pointer-events: auto;
}
.video-avatar-custom-abs {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  border: 2px solid #fff;
  background: #fff;
}
.video-like-comment-group-abs {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.video-like-custom-abs, .video-comment-custom-abs {
  color: #fff;
  font-size: 18px;
  background: rgba(0,0,0,0.45);
  border-radius: 16px;
  padding: 6px 18px;
  margin: 0;
  min-width: 60px;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
/* 视频标题底部绝对定位，距底20px */
.video-title-bottom-abs {
  position: absolute;
  left: 30px;
  right: 0;
  bottom: 20px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: left;
  text-shadow: 0 2px 8px rgba(0,0,0,0.25);
  z-index: 10;
  pointer-events: none;
  padding: 0 24px 0 0;
  line-height: 1.4;
}
.video-description-bottom-abs {
  position: absolute;
  left: 30px;
  right: 30px;
  bottom: 30px;
  color: #fff;
  font-size: 15px;
  font-weight: 400;
  text-align: left;
  text-shadow: 0 2px 8px rgba(0,0,0,0.25);
  z-index: 11;
  pointer-events: none;
  line-height: 1.6;
  background: rgba(0,0,0,0.32);
  border-radius: 8px;
  padding: 8px 16px;
  max-width: calc(100vw - 60px);
  word-break: break-word;
}
</style>

<!-- Non-scoped styles for dynamically injected HTML content -->
<style>
/* 视频播放器浮层样式 */
.video-player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #000;
  z-index: 300;
  display: flex;
  flex-direction: column;
}
.video-player-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.video-player-header {
  padding: 16px;
  display: flex;
  align-items: center;
  color: white;
}
.video-player-header .back-button {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}
.video-title {
  margin-left: 16px;
  font-size: 16px;
  flex: 1;
}
.header-spacer {
  width: 32px;
}
.video-player-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-iframe {
  width: 100%;
  height: 100%;
  background-color: #000;
}
.video-player-footer {
  display: none;
}
.fullscreen-button {
  display: none;
}
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

/* 确保用户消息容器正确对齐 */
.message-container.user-message {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.user-message {
  justify-content: flex-end;
  width: 100%;
  display: flex;
}

.bot-message {
  justify-content: flex-start;
  align-items: flex-start;
  width: 100%;
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
  max-width: 80%;
  margin-left: auto;
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
  margin-left: 0;
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

/* Top progress bar */
.top-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  height: 3px;
  background-color: transparent;
  border-radius: 0;
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
  padding-bottom: calc(env(safe-area-inset-bottom, 16px) + 20px); /* 增加20像素的底部间距 */
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

/* 加载状态样式 */
.iframe-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f7f8fc;
}

.iframe-loading p {
  margin-top: 16px;
  color: #666;
  font-size: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid rgba(255, 103, 0, 0.1);
  border-top-color: #ff6700;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

/* Video thumbnail styles */
.mi-video-thumbnail {
  position: relative;
  display: inline-block;
  margin: 10px 0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  max-width: 100%;
}

.mi-video-thumbnail:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.thumbnail-image {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
}

.play-button-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.3);
  transition: background-color 0.2s ease;
}

.mi-video-thumbnail:hover .play-button-overlay {
  background-color: rgba(0, 0, 0, 0.4);
}

.play-button-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 103, 0, 0.9);
  border-radius: 50%;
  color: white;
  font-size: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.mi-video-thumbnail:hover .play-button-icon {
  transform: scale(1.1);
  background-color: #ff6700;
}

/* 相关图片样式 */
.related-images-container {
  margin: 0 0 16px 0;
  background-color: #f8f8f8;
  border-radius: 12px;
  padding: 12px;
}

.related-images-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.related-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.related-image-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  aspect-ratio: 1;
}

.related-image-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.related-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 全屏图片查看器样式 */
.image-viewer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  animation: fade-in 0.2s ease-out;
}

.image-viewer-header {
  width: 100%;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  z-index: 10;
}

.image-viewer-title {
  font-size: 18px;
  font-weight: 500;
  max-width: 80%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-viewer-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-slider-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.image-slider {
  display: flex;
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.image-slide {
  min-width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.viewer-image {
  max-width: 100%;
  max-height: 95vh;
  object-fit: contain;
}

.slider-nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  transition: background-color 0.2s ease;
}

.slider-nav-button:hover {
  background-color: rgba(0, 0, 0, 0.6);
}

.prev-button {
  left: 16px;
}

.next-button {
  right: 16px;
}

.image-viewer-counter {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
}
</style>
