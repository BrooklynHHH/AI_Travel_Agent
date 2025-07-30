<template>
  <div class="chat-container">
    <!-- 返回按钮 -->
    <div class="back-button" @click="goBack">
      <i class="back-icon">&lt;</i>
    </div>

    <!-- 进度条 -->
    <div v-if="isLoading" class="progress-container top-progress">
      <div class="progress-bar"></div>
    </div>

    <!-- Chat内容 -->
    <div class="chat-content" ref="chatContent">
      <!-- 消息内容 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper" style="width: 100%;">
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="message-container user-message">
          <div class="message-bubble">
            <div class="user-image-container card bg-base-100 shadow-sm theme-light" style="max-width: 320px;">
              <figure>
                <div style="position: relative; display: inline-block;">
                  <img :src="message.image || require('@/assets/video-default.jpg')" style="max-width: 320px; max-height: 300px; object-fit: contain;" />
                  <!-- 生成的图像显示 -->
                  <div v-if="message.generatedImage" class="generated-image-overlay" @click="showFullScreenImage(message.generatedImage)">
                    <img :src="message.generatedImage" class="generated-image" alt="生成的图像" />
                  </div>
                  <!-- 图像生成进度条 -->
                  <div v-if="message.isGenerating" class="progress-overlay">
                    <div class="spinner"></div>
                  </div>
                </div>
              </figure>
              <div class="card-body p-4">
                <div v-if="message.content">{{ message.content }}</div>
                <div class="card-actions justify-end mt-2">
                  <div class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">{{ selectedSize }}</div>
                  <div v-if="selectedGuidanceScale" class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">引导: {{ selectedGuidanceScale }}</div>
                  <div class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">水印: {{ selectedWatermark.text }}</div>
                  <!-- 动一动按钮 -->
                  <button v-if="message.generatedImage" class="animate-button" @click="goToVideoGeneration(message.generatedImage)" title="生成视频">
                    动一动
                  </button>
                  <!-- P一下按钮 -->
                  <button v-if="message.generatedImage" class="p-button" @click="addToThumbnail(message.generatedImage)" title="添加到缩略图">
                    P一下
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 系统消息 -->
        <div v-else-if="message.role === 'system'" class="message-container system-message">
          <div role="alert" :class="getAlertClass(message.content)">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ message.content }}</span>
            
            <!-- 生成的图像预览 -->
            <div v-if="message.imageUrl" class="image-preview-container" @click="showFullScreenImage(message.imageUrl)">
              <img :src="message.imageUrl" class="generated-image-preview" alt="生成的图像" />
            </div>
          </div>
        </div>
      </div>
      <div style="height: 20px"></div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <!-- 缩略图显示区域 -->
      <div class="thumbnail-container" v-if="uploadedImage" @click="showFullScreenImage(originalImage)">
        <img :src="uploadedImage" class="thumbnail-image" alt="上传的图片" />
        <div class="clear-thumbnail-btn" @click.stop="clearSelectedImage">×</div>
      </div>

      <!-- Configuration Buttons -->
      <div class="config-buttons-container">
        <!-- Size Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('size')" ref="sizeButtonEl">
            {{ selectedSize }}
          </button>
          <div v-if="activeMenu === 'size'" class="config-menu" ref="sizeMenuEl">
            <div v-for="option in sizeOptions" :key="option" class="config-menu-item" @click="selectSizeOption(option)">
              {{ option }}
            </div>
          </div>
        </div>

        <!-- Guidance Scale Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('guidanceScale')" ref="guidanceScaleButtonEl">
            引导: {{ selectedGuidanceScale || '默认' }}
          </button>
          <div v-if="activeMenu === 'guidanceScale'" class="config-menu" ref="guidanceScaleMenuEl">
            <div v-for="option in guidanceScaleOptions" :key="option" class="config-menu-item" @click="selectGuidanceScaleOption(option)">
              引导: {{ option || '默认' }}
            </div>
          </div>
        </div>

        <!-- Watermark Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('watermark')" ref="watermarkButtonEl">
            水印: {{ selectedWatermark.text }}
          </button>
          <div v-if="activeMenu === 'watermark'" class="config-menu" ref="watermarkMenuEl">
            <div v-for="option in watermarkOptions" :key="option.value" class="config-menu-item" @click="selectWatermarkOption(option)">
              水印: {{ option.text }}
            </div>
          </div>
        </div>
      </div>

      <div class="input-container">
        <!-- 上传图片按钮 -->
        <label class="upload-btn" style="margin-right: 8px;">
          <input type="file" accept="image/*" @change="onFileChange" style="display: none;" />
          <svg class="plus-icon" width="24" height="24" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M44 24C44 22.8954 43.1046 22 42 22C40.8954 22 40 22.8954 40 24H44ZM24 8C25.1046 8 26 7.10457 26 6C26 4.89543 25.1046 4 24 4V8ZM39 40H9V44H39V40ZM8 39V9H4V39H8ZM40 24V39H44V24H40ZM9 8H24V4H9V8ZM9 40C8.44772 40 8 39.5523 8 39H4C4 41.7614 6.23857 44 9 44V40ZM39 44C41.7614 44 44 41.7614 44 39H40C40 39.5523 39.5523 40 39 40V44ZM8 9C8 8.44772 8.44771 8 9 8V4C6.23858 4 4 6.23857 4 9H8Z" fill="#333"/>
            <path d="M6 35L16.6931 25.198C17.4389 24.5143 18.5779 24.4953 19.3461 25.1538L32 36" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M28 31L32.7735 26.2265C33.4772 25.5228 34.5914 25.4436 35.3877 26.0408L42 31" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M37 18L37 6" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M32 11L37 6L42 11" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </label>
        <input 
          type="text" 
          placeholder="输入图像生成提示词" 
          v-model="userInput"
          @keyup.enter="sendMessage"
        />
        <div class="voice-button" @click="sendMessage">
          <svg class="send-icon" width="24" height="24" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M43 5L29.7 43L22.1 25.9L5 18.3L43 5Z" stroke="white" stroke-width="4" stroke-linejoin="round"/>
            <path d="M43.0001 5L22.1001 25.9" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>
  </div>

  <!-- 全屏图片查看器 -->
  <div v-if="isFullScreenImageVisible" class="fullscreen-image-overlay" @click="hideFullScreenImage">
    <img :src="fullScreenImageUrl" alt="Full screen image" class="fullscreen-image-content" />
    <!-- 下载按钮 -->
    <div class="download-button" @click.stop="downloadImage" title="下载图片">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7,10 12,15 17,10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { generateImageFromText, generateImageFromImage } from '../utils/imageGenerationApi';

// 本地存储键名
const STORAGE_KEY_MESSAGES = 'image_generation_messages';

// 保存消息到本地存储
const saveMessagesToLocalStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages.value));
    console.log('消息已保存到本地存储');
  } catch (error) {
    console.error('保存消息到本地存储失败:', error);
  }
};

// 从本地存储加载消息
const loadMessagesFromLocalStorage = () => {
  try {
    const storedMessages = localStorage.getItem(STORAGE_KEY_MESSAGES);
    if (storedMessages) {
      const parsedMessages = JSON.parse(storedMessages);
      if (parsedMessages && parsedMessages.length > 0) {
        messages.value = parsedMessages;
        console.log('从本地存储加载了消息');
      } else {
        console.log('本地存储中没有有效的消息');
      }
    } else {
      console.log('本地存储中没有消息');
    }
  } catch (error) {
    console.error('从本地存储加载消息失败:', error);
  }
};

const router = useRouter();
const userInput = ref('');
const messages = ref([]);
const conversationId = ref('');
const uploadedImage = ref(null); // Thumbnail
const originalImage = ref(null); // Original image DataURL for fullscreen
const isFullScreenImageVisible = ref(false);
const fullScreenImageUrl = ref('');

// Configuration Button States
const sizeOptions = ref(['512x512', '768x768', '1024x1024', '1024x1792', '1792x1024']);
const selectedSize = ref(sizeOptions.value[2]); // 默认选择 1024x1024

const guidanceScaleOptions = ref([null, 3.5, 5.0, 7.5, 10.0, 15.0]);
const selectedGuidanceScale = ref(guidanceScaleOptions.value[0]); // 默认为 null

const watermarkOptions = ref([
  { text: '是', value: true },
  { text: '否', value: false },
]);
const selectedWatermark = ref(watermarkOptions.value[0]); // 默认添加水印

const activeMenu = ref(null); // null, 'size', 'guidanceScale', 'watermark'

// Template refs for buttons and menus for click outside detection
const sizeButtonEl = ref(null);
const sizeMenuEl = ref(null);
const guidanceScaleButtonEl = ref(null);
const guidanceScaleMenuEl = ref(null);
const watermarkButtonEl = ref(null);
const watermarkMenuEl = ref(null);

// 返回按钮功能
const goBack = () => {
  router.push('/advanced');
};

// 在组件加载时生成会话ID并加载本地存储的消息
onMounted(() => {
  const timestamp = new Date().getTime();
  conversationId.value = `image_gen_${timestamp}`;
  console.log('生成会话ID:', conversationId.value);
  
  // 从本地存储加载消息
  loadMessagesFromLocalStorage();
});

// 处理文件上传
const onFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 创建一个FileReader来读取文件
  const reader = new FileReader();
  
  reader.onload = (e) => {
    // 创建一个新的Image对象来处理图片
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const targetWidth = 100;
      const targetHeight = 100;

      canvas.width = targetWidth;
      canvas.height = targetHeight;

      const hRatio = targetWidth / img.width;
      const vRatio = targetHeight / img.height;
      const ratio = Math.min(hRatio, vRatio); // Use min to fit the image within the bounds

      const drawWidth = img.width * ratio;
      const drawHeight = img.height * ratio;

      const offsetX = (targetWidth - drawWidth) / 2;
      const offsetY = (targetHeight - drawHeight) / 2;
      
      // 清除canvas (重要，如果之前有内容或需要透明背景)
      ctx.clearRect(0, 0, targetWidth, targetHeight);
      
      // 绘制按比例缩放并居中的图片
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
      
      // 将canvas转换为DataURL并设置为缩略图 (PNG支持透明)
      uploadedImage.value = canvas.toDataURL('image/png');
      // 保存原始图片的DataURL
      originalImage.value = e.target.result; 
    };
    
    // 设置图片源为FileReader的结果
    img.src = e.target.result; // This is the original image DataURL
  };
  
  // 读取文件为DataURL
  reader.readAsDataURL(file);
  // 重置文件输入框，以便可以再次选择相同的文件
  if (event.target) {
    event.target.value = null;
  }
};

const toggleMenu = (menuName) => {
  if (activeMenu.value === menuName) {
    activeMenu.value = null;
  } else {
    activeMenu.value = menuName;
  }
};

const selectSizeOption = (option) => {
  selectedSize.value = option;
  activeMenu.value = null;
};

const selectGuidanceScaleOption = (option) => {
  selectedGuidanceScale.value = option;
  activeMenu.value = null;
};

const selectWatermarkOption = (option) => {
  selectedWatermark.value = option;
  activeMenu.value = null;
};

// 显示全屏图片
const showFullScreenImage = (imageUrl) => {
  if (imageUrl) {
    fullScreenImageUrl.value = imageUrl;
    isFullScreenImageVisible.value = true;
  }
};

// 隐藏全屏图片
const hideFullScreenImage = () => {
  isFullScreenImageVisible.value = false;
  fullScreenImageUrl.value = '';
};

// 清除选中的图片
const clearSelectedImage = () => {
  const previouslySelectedOriginalImage = originalImage.value; // Store before clearing
  uploadedImage.value = null;
  originalImage.value = null;

  // 如果全屏显示的正是这张被清除的图片，则关闭全屏视图
  if (isFullScreenImageVisible.value && fullScreenImageUrl.value === previouslySelectedOriginalImage) {
    hideFullScreenImage();
  }
};

// 下载图片
const downloadImage = () => {
  if (!fullScreenImageUrl.value) return;
  
  try {
    // 创建一个临时的 a 标签来触发下载
    const link = document.createElement('a');
    link.href = fullScreenImageUrl.value;
    
    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    link.download = `generated-image-${timestamp}.jpg`;
    
    // 触发下载
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('图片下载已触发');
  } catch (error) {
    console.error('下载图片失败:', error);
  }
};

// 跳转到视频生成页面
const goToVideoGeneration = async (imageUrl) => {
  try {
    // 将图像数据存储到 sessionStorage，以便在视频页面使用
    const imageData = {
      imageUrl: imageUrl,
      prompt: '动一动',
      timestamp: Date.now()
    };
    
    sessionStorage.setItem('videoGenerationImageData', JSON.stringify(imageData));
    
    // 跳转到视频生成页面
    router.push('/video');
  } catch (error) {
    console.error('跳转到视频生成页面失败:', error);
  }
};

// 添加图片到缩略图
const addToThumbnail = async (imageUrl) => {
  try {
    // 创建一个新的Image对象来处理图片
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const targetWidth = 100;
      const targetHeight = 100;

      canvas.width = targetWidth;
      canvas.height = targetHeight;

      const hRatio = targetWidth / img.width;
      const vRatio = targetHeight / img.height;
      const ratio = Math.min(hRatio, vRatio);

      const drawWidth = img.width * ratio;
      const drawHeight = img.height * ratio;

      const offsetX = (targetWidth - drawWidth) / 2;
      const offsetY = (targetHeight - drawHeight) / 2;
      
      // 清除canvas
      ctx.clearRect(0, 0, targetWidth, targetHeight);
      
      // 绘制按比例缩放并居中的图片
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
      
      // 将canvas转换为DataURL并设置为缩略图
      uploadedImage.value = canvas.toDataURL('image/png');
      // 保存原始图片的DataURL
      originalImage.value = imageUrl;
      
      console.log('图片已添加到缩略图');
    };
    
    // 设置图片源
    img.src = imageUrl;
  } catch (error) {
    console.error('添加图片到缩略图失败:', error);
  }
};

// 滚动到底部
const scrollToBottom = () => {
  const chatContentEl = document.querySelector('.chat-content');
  if (chatContentEl) {
    chatContentEl.scrollTop = chatContentEl.scrollHeight;
  }
};

// 其余状态和方法
const isLoading = ref(false);

// 发送消息
const sendMessage = async () => {
  if ((!userInput.value.trim() && !uploadedImage.value) || isLoading.value) return;
  
  // 添加用户消息
  const message = {
    role: 'user',
    content: userInput.value
  };
  
  // 如果有上传的图片，添加到消息中
  if (originalImage.value) {
    message.image = originalImage.value;
  }
  
  messages.value.push(message);
  
  // 保存消息到本地存储
  saveMessagesToLocalStorage();
  
  // 调用图像生成API
  try {
    isLoading.value = true;
    
    let result;
    
    // 如果有图片，需要将其转换为File对象
    let imageFile = null;
    if (message.image) {
      // 从Data URL创建Blob
      const fetchResponse = await fetch(message.image);
      const blob = await fetchResponse.blob();
      
      // 从Blob创建File对象
      const filename = `image_${Date.now()}.${blob.type.split('/')[1] || 'png'}`;
      imageFile = new File([blob], filename, { type: blob.type });
    }
    
    // 根据是否有图片选择不同的API
    if (imageFile) {
      // 图像到图像编辑
      result = await generateImageFromImage(
        message.content || '',
        imageFile,
        selectedSize.value === '1024x1024' ? 'adaptive' : selectedSize.value,
        selectedGuidanceScale.value,
        -1, // seed
        selectedWatermark.value.value
      );
    } else {
      // 文本到图像生成
      if (!message.content || !message.content.trim()) {
        throw new Error('请输入图像生成提示词');
      }
      
      result = await generateImageFromText(
        message.content,
        selectedSize.value,
        selectedGuidanceScale.value,
        -1, // seed
        selectedWatermark.value.value
      );
    }
    
    console.log('图像生成API响应:', result);
    
    // 处理API响应
    if (result && result.imageUrl) {
      // 使用处理后的 imageUrl (data URL 格式)
      const imageUrl = result.imageUrl;
      
      // 将生成的图像添加到用户消息中
      const userMessageIndex = messages.value.length - 1;
      if (userMessageIndex >= 0 && messages.value[userMessageIndex].role === 'user') {
        messages.value[userMessageIndex].generatedImage = imageUrl;
      }
      
      // 添加成功消息
      messages.value.push({
        role: 'system',
        content: '图像生成成功！',
        imageUrl: imageUrl
      });
    } else if (result && result.data && result.data.length > 0) {
      // 兼容旧格式：如果有 data 但没有 imageUrl
      const imageUrl = result.data[0].url || result.data[0].b64_json;
      
      if (imageUrl) {
        // 如果是 base64 数据，转换为 data URL
        const finalImageUrl = imageUrl.startsWith('data:') ? imageUrl : `data:image/jpeg;base64,${imageUrl}`;
        
        // 将生成的图像添加到用户消息中
        const userMessageIndex = messages.value.length - 1;
        if (userMessageIndex >= 0 && messages.value[userMessageIndex].role === 'user') {
          messages.value[userMessageIndex].generatedImage = finalImageUrl;
        }
        
        // 添加成功消息
        messages.value.push({
          role: 'system',
          content: '图像生成成功！',
          imageUrl: finalImageUrl
        });
      }
    } else if (result && result.id) {
      // 如果只有任务ID，显示处理中消息
      messages.value.push({
        role: 'system',
        content: '图像生成任务已提交，正在处理中...'
      });
    } else {
      // 处理其他响应格式
      messages.value.push({
        role: 'system',
        content: '图像生成完成，但响应格式异常'
      });
    }
    
    // 发送后清空缩略图和原始图
    uploadedImage.value = null;
    originalImage.value = null;
    
    // 如果全屏预览是当前图片，也关闭它
    if (isFullScreenImageVisible.value && fullScreenImageUrl.value === message.image) {
      hideFullScreenImage();
    }
    
  } catch (error) {
    console.error('图像生成失败:', error);
    messages.value.push({
      role: 'system',
      content: `图像生成失败: ${error.message}`
    });
  } finally {
    isLoading.value = false;
    
    // 清空输入框
    userInput.value = '';
    
    // 保存消息到本地存储
    saveMessagesToLocalStorage();
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// 根据消息内容选择alert类型
const getAlertClass = (content) => {
  // 默认样式
  let baseClass = 'alert flex items-center';
  
  // 根据消息内容判断状态
  if (content.includes('成功') || content.includes('完成')) {
    return `${baseClass} alert-success`;
  } else if (content.includes('失败') || content.includes('错误') || content.includes('取消')) {
    return `${baseClass} alert-error`;
  } else if (content.includes('处理中') || content.includes('排队中') || content.includes('等待')) {
    return `${baseClass} alert-warning`;
  }
  
  // 默认使用success
  return `${baseClass} alert-success`;
};

// Click outside handler for config menus
const handleClickOutside = (event) => {
  if (!activeMenu.value) return;

  const target = event.target;
  let activeMenuElement = null;
  let activeButtonElement = null;

  if (activeMenu.value === 'size') {
    activeMenuElement = sizeMenuEl.value;
    activeButtonElement = sizeButtonEl.value;
  } else if (activeMenu.value === 'guidanceScale') {
    activeMenuElement = guidanceScaleMenuEl.value;
    activeButtonElement = guidanceScaleButtonEl.value;
  } else if (activeMenu.value === 'watermark') {
    activeMenuElement = watermarkMenuEl.value;
    activeButtonElement = watermarkButtonEl.value;
  }

  // If click is not on the active button and not inside the active menu, close it
  if (activeButtonElement && !activeButtonElement.contains(target) &&
      activeMenuElement && !activeMenuElement.contains(target)) {
    activeMenu.value = null;
  }
};

watch(activeMenu, (newValue, oldValue) => {
  if (newValue) { // Menu opened
    // Needs nextTick because the menu element might not be in DOM yet when activeMenu changes
    nextTick(() => {
      document.addEventListener('mousedown', handleClickOutside);
    });
  } else if (oldValue) { // Menu closed
    document.removeEventListener('mousedown', handleClickOutside);
  }
});

onBeforeUnmount(() => {
  if (activeMenu.value) { // Ensure listener is removed if component unmounts with active menu
    document.removeEventListener('mousedown', handleClickOutside);
  }
});
</script>

<style scoped>
/* 输入区样式 */
.chat-input {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px 16px;
  background-color: #fff;
  border-top: 1px solid #eee;
  z-index: 50;
}

/* 缩略图样式 */
.thumbnail-container {
  display: flex;
  align-items: center;
  position: absolute;
  bottom: calc(100% + 10px);
  left: 16px;
  z-index: 10;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.thumbnail-image {
  width: 100px;
  height: 100px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid #eee;
  background-color: #f0f0f0;
}

/* 返回按钮样式 */
.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s ease;
}

.back-button:hover {
  opacity: 0.8;
}

.back-icon {
  font-size: 16px;
  font-weight: bold;
  color: #666;
}

.upload-btn {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.plus-icon {
  font-size: 20px;
}

/* 全屏图片查看器样式 */
.fullscreen-image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: pointer;
}

.fullscreen-image-content {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
}

/* 下载按钮样式 */
.download-button {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 48px;
  height: 48px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.download-button:hover {
  background-color: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.4);
}

.download-button svg {
  width: 24px;
  height: 24px;
}

/* 清除缩略图按钮样式 */
.clear-thumbnail-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 20px;
  height: 20px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  line-height: 20px;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.clear-thumbnail-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

/* 用户消息气泡靠左对齐 */
.message-container.user-message {
  justify-content: flex-start;
}

.message-container.user-message .message-bubble {
  margin-left: 0;
}

/* Config Buttons Area */
.config-buttons-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 8px 0px; 
  border-bottom: 1px solid #f0f0f0; 
  margin-bottom: 8px; 
}

.config-button-wrapper {
  position: relative;
}

.config-button {
  background-color: #f7f7f7;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 13px;
  min-width: 80px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.config-button:hover {
  background-color: #efefef;
}

.config-menu {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 0;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 20;
  min-width: 100%;
  padding: 4px 0;
}

.config-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  text-align: center;
  position: relative;
}

.config-menu-item:not(:last-child)::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 25%;
  width: 50%;
  height: 1px;
  background-color: #eeeeee;
}

.config-menu-item:hover {
  background-color: #f0f0f0;
}

/* 生成的图像样式 */
.generated-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.generated-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.image-preview-container {
  margin-top: 10px;
  cursor: pointer;
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.image-preview-container:hover {
  transform: scale(1.02);
}

.generated-image-preview {
  max-width: 240px;
  max-height: 240px;
  object-fit: contain;
  display: block;
}

/* 系统消息样式 */
.message-container.system-message {
  position: fixed;
  top: 16px;
  right: 16px;
  width: auto;
  max-width: 80%;
  z-index: 100;
}

/* DaisyUI alert样式覆盖 */
.alert {
  margin: 0 auto;
  max-width: 80%;
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
}

.alert svg {
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;
}

.alert-success {
  background-color: #36d399;
  color: white;
}

.alert-warning {
  background-color: #fbbd23;
  color: white;
}

.alert-error {
  background-color: #f87272;
  color: white;
}

/* 进度条样式 */
.progress-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

/* 圆形旋转进度条 */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid #4CAF50;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* chat-content 与 fixed back-button 间距调整 */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding-top: 53px;
  padding-bottom: 120px; /* 为固定在底部的输入区域留出空间 */
}

/* 进度条样式 */
.progress-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #f0f0f0;
  z-index: 1000;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  animation: progress-animation 2s ease-in-out infinite;
}

@keyframes progress-animation {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 通用样式 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: #fff;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
}

.input-container input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 12px;
  font-size: 14px;
}

.voice-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.voice-button:hover {
  background-color: #0056b3;
}

.send-icon {
  font-size: 16px;
  font-weight: bold;
}

/* 动一动按钮样式 */
.animate-button {
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 4px;
  font-weight: 500;
}

.animate-button:hover {
  background-color: #ff5252;
  transform: scale(1.05);
}

.animate-button:active {
  transform: scale(0.95);
}

/* P一下按钮样式 */
.p-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 4px;
  font-weight: 500;
}

.p-button:hover {
  background-color: #45a049;
  transform: scale(1.05);
}

.p-button:active {
  transform: scale(0.95);
}
</style>
