<template>
  <div class="chat-container">
    <!-- 返回按钮 -->
    <div class="back-button" @click="goBack">
      <i class="back-icon">&lt;</i>
    </div>
    
    <VideoPlayer
      v-model:show="showVideoPlayer"
      :videoUrl="videoUrl"
      :videoTitle="videoTitle"
      :videoAvatar="videoAvatar"
      :videoLikeCount="videoLikeCount"
      :videoCommentCount="videoCommentCount"
      :videoDescription="videoDescription"
    />

    <!-- 进度条 -->
    <div v-if="isLoading || isStreaming" class="progress-container top-progress">
      <div class="progress-bar"></div>
    </div>

    <!-- Chat内容 -->
    <div class="chat-content" ref="chatContent">
      <!-- 消息内容 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper" style="width: 100%;">
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="message-container user-message">
          <div class="message-bubble">
            <div class="user-image-container card bg-base-100 shadow-sm theme-light" :data-task-id="message.taskId" style="max-width: 320px;">
              <figure>
                <div style="position: relative; display: inline-block;">
                  <img :src="message.image || require('@/assets/video-default.jpg')" style="max-width: 320px; max-height: 300px; object-fit: contain;" />
                  <!-- 视频播放按钮 -->
                  <div v-if="message.videoUrl" class="play-button-overlay" @click="playVideo(message.videoUrl)">
                    <div class="play-button-icon">▶</div>
                  </div>
                  <!-- 视频生成进度条 -->
                  <div v-if="message.isGenerating" class="progress-overlay">
                    <div class="spinner"></div>
                  </div>
                </div>
              </figure>
              <div class="card-body p-4">
                <div v-if="message.content">{{ message.content }}</div>
                <div class="card-actions justify-end mt-2">
                  <div class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">{{ selectedAspectRatio }}</div>
                  <div class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">{{ selectedDuration }}s</div>
                  <div class="badge badge-outline" style="display: inline-flex; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem; border: 1px solid #666; color: #666; margin: 0.125rem;">{{ selectedModel }}</div>
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
            
            <!-- 视频预览（如果有） -->
            <div v-if="message.videoUrl" class="video-preview-container" @click="playVideo(message.videoUrl)">
              <div class="video-thumbnail">
                <div class="play-button-overlay">
                  <div class="play-button-icon">▶</div>
                </div>
                <!-- 使用纯色背景代替图片 -->
                <div class="video-thumbnail-placeholder"></div>
              </div>
              <div class="video-preview-text">点击播放视频</div>
            </div>
            
            <!-- 使用 vue3-video-play 组件播放视频 -->
            <div v-if="message.videoUrl" class="core-player-container">
              <vue3VideoPlay
                width="100%"
                height="auto"
                :title="'生成的视频'"
                :src="message.videoUrl"
                poster=""
                autoPlay
                muted
                class="native-video-player"
                @play="onVideoPlay"
                @pause="onVideoPlay"
                @canplay="onVideoPlay"
              />
            </div>
          </div>
        </div>
      </div>
      <div style="height: 20px"></div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <!-- 缩略图显示区域 -->
      <div class="thumbnail-container" v-if="uploadedImage || selectedVideoType.value === 'frame2video' || selectedVideoType.value === 'multiimg2video'">
        <!-- 普通图生视频模式 -->
        <div v-if="selectedVideoType.value !== 'frame2video' && selectedVideoType.value !== 'multiimg2video' && uploadedImage" @click="showFullScreenImage" class="single-image-container">
          <img :src="uploadedImage" class="thumbnail-image" alt="上传的图片" />
          <div class="clear-thumbnail-btn" @click.stop="clearSelectedImage">×</div>
        </div>
        
        <!-- 首尾帧生视频模式 -->
        <div v-if="selectedVideoType.value === 'frame2video'" class="frame-images-container">
          <div class="frame-image-item">
            <div class="frame-label">首帧</div>
            <div v-if="startImageThumbnail" class="frame-image-wrapper" @click="showFullScreenImage('start')">
              <img :src="startImageThumbnail" class="thumbnail-image" alt="首帧图片" />
              <div class="clear-thumbnail-btn" @click.stop="clearStartImage">×</div>
            </div>
            <div v-else class="frame-placeholder" @click="selectStartImage">
              <span>选择首帧</span>
            </div>
          </div>
          
          <div class="frame-image-item">
            <div class="frame-label">尾帧</div>
            <div v-if="endImageThumbnail" class="frame-image-wrapper" @click="showFullScreenImage('end')">
              <img :src="endImageThumbnail" class="thumbnail-image" alt="尾帧图片" />
              <div class="clear-thumbnail-btn" @click.stop="clearEndImage">×</div>
            </div>
            <div v-else class="frame-placeholder" @click="selectEndImage">
              <span>选择尾帧</span>
            </div>
          </div>
        </div>

        <!-- 多图参考生视频模式 -->
        <div v-if="selectedVideoType.value === 'multiimg2video'" class="multi-images-container">
          <div v-for="(image, index) in multiImages" :key="index" class="frame-image-item">
            <div class="frame-label">图片{{ index + 1 }}</div>
            <div v-if="image" class="frame-image-wrapper" @click="showFullScreenImage('multi', index)">
              <img :src="image.thumbnail" class="thumbnail-image" :alt="`参考图片${index + 1}`" />
              <div class="clear-thumbnail-btn" @click.stop="removeMultiImage(index)">×</div>
            </div>
            <div v-else class="frame-placeholder" @click="selectMultiImage(index)">
              <span>选择图片</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration Buttons -->
      <div class="config-buttons-container">
        <!-- Video Type Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('videoType')" ref="videoTypeButtonEl">
            {{ selectedVideoType.name }}
          </button>
          <div v-if="activeMenu === 'videoType'" class="config-menu" ref="videoTypeMenuEl">
            <div v-for="option in videoTypes" :key="option.value" class="config-menu-item" @click="selectVideoTypeOption(option)">
              {{ option.name }}
            </div>
          </div>
        </div>

        <!-- Model Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('model')" ref="modelButtonEl">
            {{ selectedModel }}
          </button>
          <div v-if="activeMenu === 'model'" class="config-menu" ref="modelMenuEl">
            <div v-for="option in selectedVideoType.models" :key="option" class="config-menu-item" @click="selectModelOption(option)">
              {{ option }}
            </div>
          </div>
        </div>

        <!-- Aspect Ratio Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('aspectRatio')" ref="aspectRatioButtonEl">
            {{ selectedAspectRatio }}
          </button>
          <div v-if="activeMenu === 'aspectRatio'" class="config-menu" ref="aspectRatioMenuEl">
            <div v-for="option in aspectRatioOptions" :key="option" class="config-menu-item" @click="selectAspectRatioOption(option)">
              {{ option }}
            </div>
          </div>
        </div>

        <!-- Duration Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('duration')" ref="durationButtonEl">
            时长: {{ selectedDuration }}s
          </button>
          <div v-if="activeMenu === 'duration'" class="config-menu" ref="durationMenuEl">
            <div v-for="option in durationOptions" :key="option" class="config-menu-item" @click="selectDurationOption(option)">
              时长: {{ option }}s
            </div>
          </div>
        </div>

        <!-- Mode Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('mode')" ref="modeButtonEl">
            模式: {{ selectedMode }}
          </button>
          <div v-if="activeMenu === 'mode'" class="config-menu" ref="modeMenuEl">
            <div v-for="option in modeOptions" :key="option" class="config-menu-item" @click="selectModeOption(option)">
              模式: {{ option }}
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
          placeholder="输入视频生成提示词" 
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
  </div>

</template>

<script setup>
import { ref, nextTick, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import VideoPlayer from '../components/modals/VideoPlayer.vue';
import { generateVideoFromText, generateVideoFromImage, generateVideoFromStartEnd, generateVideoFromMultiImages, checkQianfanVideoStatus } from '../utils/qianfanVideoApi';
// 引入 vue3-video-play 样式
import 'vue3-video-play/dist/style.css';

// 本地存储键名
const STORAGE_KEY_MESSAGES = 'qianfan_video_generation_messages';
const STORAGE_KEY_VIDEOS = 'qianfan_video_generation_videos';

// 保存消息到本地存储
const saveMessagesToLocalStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages.value));
    console.log('消息已保存到本地存储');
  } catch (error) {
    console.error('保存消息到本地存储失败:', error);
  }
};

// 移除状态消息（处理中或排队中）
const removeStatusMessages = () => {
  const statusIndicesToRemove = [];
  messages.value.forEach((msg, index) => {
    if (msg.role === 'system' && 
        (msg.content.includes('视频生成处理中') || 
         msg.content.includes('视频生成排队中'))) {
      statusIndicesToRemove.push(index);
    }
  });
  
  // 从后往前删除，避免索引变化
  for (let i = statusIndicesToRemove.length - 1; i >= 0; i--) {
    messages.value.splice(statusIndicesToRemove[i], 1);
  }
};

// 从本地存储加载消息
const loadMessagesFromLocalStorage = () => {
  try {
    const storedMessages = localStorage.getItem(STORAGE_KEY_MESSAGES);
    if (storedMessages) {
      const parsedMessages = JSON.parse(storedMessages);
      if (parsedMessages && parsedMessages.length > 0) {
        // 过滤掉所有状态消息，确保初始状态下不显示
        const filteredMessages = parsedMessages.filter(msg => 
          !(msg.role === 'system' && 
            (msg.content.includes('视频生成处理中') || 
             msg.content.includes('视频生成排队中'))));
        
        messages.value = filteredMessages;
        console.log('从本地存储加载了消息');
        
        // 检查每个消息的状态
        messages.value.forEach(message => {
          if (message.role === 'user' && message.taskId) {
            checkMessageStatus(message);
          }
        });
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

// 检查消息状态并更新UI
const checkMessageStatus = async (message) => {
  if (!message.taskId) return;
  
  try {
    // 1. 从本地缓存中读取任务状态
    let videoCache = {};
    let cachedStatus = null;
    let cachedRemoteUrl = null;
    
    try {
      videoCache = JSON.parse(localStorage.getItem(STORAGE_KEY_VIDEOS) || '{}');
      if (videoCache[message.taskId]) {
        cachedStatus = videoCache[message.taskId].status;
        cachedRemoteUrl = videoCache[message.taskId].remoteUrl;
      }
    } catch (error) {
      console.error('读取缓存任务状态失败:', error);
    }
    
    // 2. 如果任务状态是succeed且remoteUrl已存在，则不需要调用API
    if (cachedStatus === 'succeed' && cachedRemoteUrl) {
      console.log(`任务 ${message.taskId} 已完成，使用缓存状态`);
      message.isGenerating = false;
      message.videoUrl = cachedRemoteUrl;
      return;
    }
    
    // 3. 如果任务状态不是succeed或remoteUrl不存在，则调用API检查状态
    const statusResult = await checkQianfanVideoStatus(message.taskId, message.model || selectedModel.value);
    console.log(`检查任务状态 ${message.taskId}:`, statusResult);
    
    // 更新缓存任务状态
    try {
      if (!videoCache[message.taskId]) {
        videoCache[message.taskId] = {};
      }
      videoCache[message.taskId].status = statusResult.data?.task_status;
      videoCache[message.taskId].timestamp = Date.now();
      localStorage.setItem(STORAGE_KEY_VIDEOS, JSON.stringify(videoCache));
    } catch (error) {
      console.error('缓存任务状态失败:', error);
    }
    
    if (statusResult.data?.task_status === 'succeed') {
      // 任务成功完成
      message.isGenerating = false;
      
      // 如果有视频URL，添加到消息中
      if (statusResult.data?.task_result?.videos && statusResult.data.task_result.videos.length > 0) {
        const videoUrlValue = statusResult.data.task_result.videos[0].url;
        
        // 直接使用原始URL
        message.videoUrl = videoUrlValue;
        
        // 存储视频URL到本地存储
        try {
          if (!videoCache[message.taskId]) {
            videoCache[message.taskId] = {};
          }
          videoCache[message.taskId].remoteUrl = videoUrlValue;
          videoCache[message.taskId].status = 'succeed';
          videoCache[message.taskId].timestamp = Date.now();
          localStorage.setItem(STORAGE_KEY_VIDEOS, JSON.stringify(videoCache));
        } catch (error) {
          console.error('存储视频URL失败:', error);
        }
        
        console.log('已将视频URL添加到用户消息:', message);
      }
    } else if (statusResult.data?.task_status === 'failed') {
      // 任务失败
      message.isGenerating = false;
      message.hasFailed = true; // 添加失败标记
    } else if (statusResult.data?.task_status === 'processing' || statusResult.data?.task_status === 'submitted') {
      // 任务仍在处理中，继续检查
      message.isGenerating = true;
      currentTaskId.value = message.taskId;
      startTaskStatusCheck();
    }
    
    // 保存更新后的消息到本地存储
    saveMessagesToLocalStorage();
  } catch (error) {
    console.error(`检查任务状态失败 ${message.taskId}:`, error);
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

// 首尾帧生视频相关变量
const startImage = ref(null); // 首帧图片
const endImage = ref(null); // 尾帧图片
const startImageThumbnail = ref(null); // 首帧缩略图
const endImageThumbnail = ref(null); // 尾帧缩略图

// 多图参考生视频相关变量
const multiImages = ref([null, null, null, null]); // 最多4张图片

// Configuration Button States
// 视频生成类型和对应的模型
const videoTypes = ref([
  {
    name: '文生视频',
    value: 'text2video',
    models: ['K1', 'K1.6', 'K2.0', 'K2.1-Master', 'VQ1', 'V1.5', 'MT-Director', 'MT-01']
  },
  {
    name: '图生视频', 
    value: 'img2video',
    models: ['K1.0', 'K1.5', 'K1.6', 'K2.0', 'K2.1', 'K2.1-Master', 'V2.0', 'VQ1', 'V1.5', 'MI-Director', 'MI-01-Live', 'MI-01']
  },
  {
    name: '首尾帧生视频',
    value: 'frame2video', 
    models: ['VQ1', 'V2.0', 'V1.5']
  },
  {
    name: '多图参考生视频',
    value: 'multiimg2video',
    models: ['V2.0', 'V1.5', 'K1.6', 'MS-01']
  },
  {
    name: '对口型',
    value: 'lipsync',
    models: ['K-Lip-Sync']
  }
]);

const selectedVideoType = ref(videoTypes.value[0]);
const selectedModel = ref(selectedVideoType.value.models[0]);

const aspectRatioOptions = ref(['16:9', '9:16', '1:1']);
const selectedAspectRatio = ref(aspectRatioOptions.value[0]);

const durationOptions = ref(['5', '10']);
const selectedDuration = ref(durationOptions.value[0]);

const modeOptions = ref(['std', 'fast']);
const selectedMode = ref(modeOptions.value[0]);

const activeMenu = ref(null); // null, 'videoType', 'model', 'aspectRatio', 'duration', 'mode'

// Template refs for buttons and menus for click outside detection
const videoTypeButtonEl = ref(null);
const videoTypeMenuEl = ref(null);
const modelButtonEl = ref(null);
const modelMenuEl = ref(null);
const aspectRatioButtonEl = ref(null);
const aspectRatioMenuEl = ref(null);
const durationButtonEl = ref(null);
const durationMenuEl = ref(null);
const modeButtonEl = ref(null);
const modeMenuEl = ref(null);

// 返回按钮功能
const goBack = () => {
  router.push('/advanced');
};

// 在组件加载时生成会话ID并加载本地存储的消息
onMounted(() => {
  const timestamp = new Date().getTime();
  conversationId.value = `qianfan_video_${timestamp}`;
  console.log('生成会话ID:', conversationId.value);
  
  // 从本地存储加载消息
  loadMessagesFromLocalStorage();
  
  // 检查是否有从图像生成页面传递过来的数据
  checkForImageData();
});

// 检查并处理从图像生成页面传递的数据
const checkForImageData = async () => {
  try {
    const imageDataStr = sessionStorage.getItem('qianfanVideoGenerationImageData');
    if (imageDataStr) {
      const imageData = JSON.parse(imageDataStr);
      console.log('接收到图像数据:', imageData);
      
      // 设置文本输入框的值
      userInput.value = imageData.prompt || '让图片中的人物动起来';
      
      // 将图像数据转换为File对象并设置
      if (imageData.imageUrl) {
        // 从Data URL创建Blob
        const fetchResponse = await fetch(imageData.imageUrl);
        const blob = await fetchResponse.blob();
        
        // 创建File对象
        const filename = `image_${Date.now()}.${blob.type.split('/')[1] || 'png'}`;
        const file = new File([blob], filename, { type: blob.type });
        
        // 模拟文件上传事件
        const mockEvent = {
          target: {
            files: [file]
          }
        };
        
        // 调用文件处理函数
        onFileChange(mockEvent);
      }
      
      // 清除sessionStorage中的数据，避免重复使用
      sessionStorage.removeItem('qianfanVideoGenerationImageData');
    }
  } catch (error) {
    console.error('处理图像数据失败:', error);
  }
};

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

const selectModelOption = (option) => {
  selectedModel.value = option;
  activeMenu.value = null;
};

const selectAspectRatioOption = (option) => {
  selectedAspectRatio.value = option;
  activeMenu.value = null;
};

const selectDurationOption = (option) => {
  selectedDuration.value = option;
  activeMenu.value = null;
};

const selectVideoTypeOption = (option) => {
  selectedVideoType.value = option;
  // 当视频类型改变时，重置模型选择为该类型的第一个模型
  selectedModel.value = option.models[0];
  activeMenu.value = null;
  
  // 如果选择了首尾帧生视频，立即显示图片选择浮窗
  if (option.value === 'frame2video') {
    // 清空之前的图片选择
    startImage.value = null;
    startImageThumbnail.value = null;
    endImage.value = null;
    endImageThumbnail.value = null;
    
    // 延迟一下确保界面更新完成后再触发选择
    nextTick(() => {
      selectStartImage();
    });
  }
  
  // 如果选择了多图参考生视频，清空之前的多图选择
  if (option.value === 'multiimg2video') {
    // 清空之前的多图选择
    multiImages.value = [null, null, null, null];
  }
};

const selectModeOption = (option) => {
  selectedMode.value = option;
  activeMenu.value = null;
};

// 显示全屏图片
const showFullScreenImage = (imageType = 'normal', index = 0) => {
  if (imageType === 'start' && startImage.value) {
    fullScreenImageUrl.value = startImage.value;
    isFullScreenImageVisible.value = true;
  } else if (imageType === 'end' && endImage.value) {
    fullScreenImageUrl.value = endImage.value;
    isFullScreenImageVisible.value = true;
  } else if (imageType === 'multi' && multiImages.value[index]) {
    fullScreenImageUrl.value = multiImages.value[index].original;
    isFullScreenImageVisible.value = true;
  } else if (originalImage.value) {
    fullScreenImageUrl.value = originalImage.value;
    isFullScreenImageVisible.value = true;
  }
};

// 播放视频
const playVideo = (videoUrlValue) => {
  if (videoUrlValue) {
    console.log('播放视频:', videoUrlValue);
    
    // 直接使用原始URL
    videoUrl.value = videoUrlValue;
    videoTitle.value = '生成的视频';
    showVideoPlayer.value = true;
  }
};

// 隐藏全屏图片
const hideFullScreenImage = () => {
  isFullScreenImageVisible.value = false;
  fullScreenImageUrl.value = '';
};

// 视频播放事件处理函数
const onVideoPlay = () => {
  console.log('视频播放事件');
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

// 首尾帧图片选择和处理方法
const selectStartImage = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFrameImage(file, 'start');
    }
  };
  input.click();
};

const selectEndImage = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFrameImage(file, 'end');
    }
  };
  input.click();
};

const processFrameImage = (file, frameType) => {
  const reader = new FileReader();
  
  reader.onload = (e) => {
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
      
      ctx.clearRect(0, 0, targetWidth, targetHeight);
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
      
      const thumbnailDataUrl = canvas.toDataURL('image/png');
      const originalDataUrl = e.target.result;
      
      if (frameType === 'start') {
        startImageThumbnail.value = thumbnailDataUrl;
        startImage.value = originalDataUrl;
        
        // 选择完首帧后，自动弹出选择尾帧的浮窗
        nextTick(() => {
          selectEndImage();
        });
      } else if (frameType === 'end') {
        endImageThumbnail.value = thumbnailDataUrl;
        endImage.value = originalDataUrl;
      }
    };
    
    img.src = e.target.result;
  };
  
  reader.readAsDataURL(file);
};

const clearStartImage = () => {
  const previousStartImage = startImage.value;
  startImageThumbnail.value = null;
  startImage.value = null;
  
  if (isFullScreenImageVisible.value && fullScreenImageUrl.value === previousStartImage) {
    hideFullScreenImage();
  }
};

const clearEndImage = () => {
  const previousEndImage = endImage.value;
  endImageThumbnail.value = null;
  endImage.value = null;
  
  if (isFullScreenImageVisible.value && fullScreenImageUrl.value === previousEndImage) {
    hideFullScreenImage();
  }
};

// 多图参考生视频相关方法
const selectMultiImage = (index) => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processMultiImage(file, index);
    }
  };
  input.click();
};

const processMultiImage = (file, index) => {
  const reader = new FileReader();
  
  reader.onload = (e) => {
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
      
      ctx.clearRect(0, 0, targetWidth, targetHeight);
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
      
      const thumbnailDataUrl = canvas.toDataURL('image/png');
      const originalDataUrl = e.target.result;
      
      // 更新对应索引的图片
      multiImages.value[index] = {
        thumbnail: thumbnailDataUrl,
        original: originalDataUrl
      };
    };
    
    img.src = e.target.result;
  };
  
  reader.readAsDataURL(file);
};

const removeMultiImage = (index) => {
  const previousImage = multiImages.value[index];
  multiImages.value[index] = null;
  
  // 如果全屏显示的正是这张被删除的图片，则关闭全屏视图
  if (isFullScreenImageVisible.value && previousImage && 
      fullScreenImageUrl.value === previousImage.original) {
    hideFullScreenImage();
  }
};


// 滚动到底部
const scrollToBottom = () => {
  const chatContentEl = document.querySelector('.chat-content');
  if (chatContentEl) {
    chatContentEl.scrollTop = chatContentEl.scrollHeight;
  }
};

// 其余状态和方法复用 ChatView
const isLoading = ref(false);
const showVideoPlayer = ref(false);
const videoUrl = ref('');
const videoTitle = ref('');
const videoAvatar = ref('');
const videoLikeCount = ref(0);
const videoCommentCount = ref(0);
const videoDescription = ref('');
const isStreaming = ref(false);
const currentTaskId = ref(''); // 存储当前任务ID
const taskCheckInterval = ref(null); // 存储任务状态检查的定时器ID

// 发送消息
const sendMessage = async () => {
  // 检查不同模式下的输入要求
  if (selectedVideoType.value.value === 'frame2video') {
    // 首尾帧生视频模式：需要首帧图片和提示词，尾帧图片可选
    if (!startImage.value || !userInput.value.trim()) {
      console.log('首尾帧生视频需要选择首帧图片和输入提示词');
      return;
    }
  } else if (selectedVideoType.value.value === 'multiimg2video') {
    // 多图参考生视频模式：需要至少一张图片和提示词
    const selectedImages = multiImages.value.filter(img => img);
    if (selectedImages.length === 0 || !userInput.value.trim()) {
      console.log('多图参考生视频需要至少选择一张图片和输入提示词');
      return;
    }
  } else {
    // 其他模式：需要图片或提示词
    if ((!userInput.value.trim() && !uploadedImage.value) || isLoading.value) return;
  }
  
  // 添加用户消息
  const message = {
    role: 'user',
    content: userInput.value,
    model: selectedModel.value,
    videoType: selectedVideoType.value.value
  };
  
  // 根据视频类型添加图片信息
  if (selectedVideoType.value.value === 'frame2video') {
    // 首尾帧生视频：显示首帧图片
    message.image = startImage.value;
    message.startImage = startImage.value;
    message.endImage = endImage.value;
  } else if (originalImage.value) {
    // 普通图生视频：使用 originalImage 以在聊天中显示原始比例图片
    message.image = originalImage.value;
  } else if (uploadedImage.value) {
    // Fallback or specific logic if only thumbnail was intended (should not happen with current flow)
    // For safety, ensure both are cleared if thumbnail was somehow present without original
    uploadedImage.value = null;
    originalImage.value = null;
  }
  
  messages.value.push(message);
  
  // 保存消息到本地存储
  saveMessagesToLocalStorage();
  
  // 调用千帆视频生成API
  try {
    isLoading.value = true;
    let result;
    
    if (selectedVideoType.value.value === 'frame2video') {
      // 首尾帧生视频
      const startFetchResponse = await fetch(startImage.value);
      const startBlob = await startFetchResponse.blob();
      const startFilename = `start_image_${Date.now()}.${startBlob.type.split('/')[1] || 'png'}`;
      const startImageFile = new File([startBlob], startFilename, { type: startBlob.type });
      
      let endImageFile = null;
      if (endImage.value) {
        const endFetchResponse = await fetch(endImage.value);
        const endBlob = await endFetchResponse.blob();
        const endFilename = `end_image_${Date.now()}.${endBlob.type.split('/')[1] || 'png'}`;
        endImageFile = new File([endBlob], endFilename, { type: endBlob.type });
      }
      
      result = await generateVideoFromStartEnd(
        message.content,
        startImageFile,
        endImageFile,
        selectedModel.value,
        selectedDuration.value
      );
      
      // 清空首尾帧图片
      startImage.value = null;
      startImageThumbnail.value = null;
      endImage.value = null;
      endImageThumbnail.value = null;
      
    } else if (selectedVideoType.value.value === 'multiimg2video') {
      // 多图参考生视频
      const selectedImages = multiImages.value.filter(img => img);
      const imageFiles = [];
      
      for (const imageData of selectedImages) {
        const fetchResponse = await fetch(imageData.original);
        const blob = await fetchResponse.blob();
        const filename = `multi_image_${Date.now()}_${Math.random().toString(36).substr(2, 9)}.${blob.type.split('/')[1] || 'png'}`;
        const imageFile = new File([blob], filename, { type: blob.type });
        imageFiles.push(imageFile);
      }
      
      result = await generateVideoFromMultiImages(
        message.content,
        imageFiles,
        selectedModel.value,
        { duration: selectedDuration.value }
      );
      
      // 清空多图选择
      multiImages.value = [null, null, null, null];
      
    } else if (message.image) {
      // 图生视频
      const fetchResponse = await fetch(message.image);
      const blob = await fetchResponse.blob();
      const filename = `image_${Date.now()}.${blob.type.split('/')[1] || 'png'}`;
      const imageFile = new File([blob], filename, { type: blob.type });
      
      result = await generateVideoFromImage(
        message.content || "让图片中的人物动起来",
        imageFile,
        selectedModel.value,
        selectedDuration.value
      );
      
      // 发送后清空缩略图和原始图
      uploadedImage.value = null;
      originalImage.value = null; 
      // 如果全屏预览是当前图片，也关闭它
      if (isFullScreenImageVisible.value && fullScreenImageUrl.value === message.image) {
        hideFullScreenImage();
      }
    } else {
      // 文生视频
      result = await generateVideoFromText(
        message.content,
        selectedModel.value,
        selectedDuration.value,
        selectedAspectRatio.value,
        selectedMode.value
      );
    }
    
    console.log('千帆视频生成API响应:', result);
    
    // 从响应中提取任务ID
    if (result && result.data && result.data.task_id) {
      currentTaskId.value = result.data.task_id;
      console.log('获取到任务ID:', currentTaskId.value);
      
      // 将任务ID与用户消息关联
      const userMessageIndex = messages.value.length - 1;
      if (userMessageIndex >= 0 && messages.value[userMessageIndex].role === 'user') {
        messages.value[userMessageIndex].taskId = currentTaskId.value;
        // 初始化为生成中状态
        messages.value[userMessageIndex].isGenerating = true;
      }
              
      // 开始定期检查任务状态
      startTaskStatusCheck();
    } else {
      console.error('API响应中没有任务ID');
    }
  } catch (error) {
    console.error('千帆视频生成失败:', error);
    // 可以添加错误处理逻辑，例如显示错误消息
    messages.value.push({
      role: 'system',
      content: `视频生成失败: ${error.message}`
    });
  } finally {
    // 清空输入框
    userInput.value = '';
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });
    
    // 注意：这里不设置isLoading.value = false，因为我们需要等待任务完成
    // isLoading状态将在任务完成或失败时更新
  }
};

// 开始定期检查任务状态
const startTaskStatusCheck = () => {
  // 清除可能存在的之前的定时器
  if (taskCheckInterval.value) {
    clearInterval(taskCheckInterval.value);
  }
  
  // 设置定时器，每2秒检查一次任务状态
  taskCheckInterval.value = setInterval(async () => {
    if (!currentTaskId.value) {
      clearInterval(taskCheckInterval.value);
      return;
    }
    
    // 检查本地缓存中的任务状态
    let shouldCheck = true;
    let cachedRemoteUrl = null;
    try {
      const videoCache = JSON.parse(localStorage.getItem(STORAGE_KEY_VIDEOS) || '{}');
      if (videoCache[currentTaskId.value]) {
        // 如果任务状态是succeed且remoteUrl存在，则不需要检查，直接更新UI
        if (videoCache[currentTaskId.value].status === 'succeed' && videoCache[currentTaskId.value].remoteUrl) {
          console.log('任务已完成，使用缓存视频URL:', currentTaskId.value);
          shouldCheck = false;
          cachedRemoteUrl = videoCache[currentTaskId.value].remoteUrl;
          
          // 更新UI显示视频
          isLoading.value = false;
          
          // 找到对应的用户消息
          const userMessage = messages.value.find(msg => 
            msg.role === 'user' && msg.taskId === currentTaskId.value);
          
          if (userMessage) {
            userMessage.isGenerating = false;
            userMessage.videoUrl = cachedRemoteUrl;
            
            // 保存消息到本地存储
            saveMessagesToLocalStorage();
          }
          
          // 清除定时器
          clearInterval(taskCheckInterval.value);
          return;
        }
        // 如果任务状态不是processing或submitted，则不需要检查
        else if (videoCache[currentTaskId.value].status !== 'processing' && 
            videoCache[currentTaskId.value].status !== 'submitted') {
          shouldCheck = false;
        }
      }
    } catch (error) {
      console.error('获取缓存任务状态失败:', error);
    }
    
    // 如果不需要检查，则清除定时器并返回
    if (!shouldCheck) {
      clearInterval(taskCheckInterval.value);
      return;
    }
    
    try {
      // 找到对应的用户消息以获取模型信息
      const userMessage = messages.value.find(msg => 
        msg.role === 'user' && msg.taskId === currentTaskId.value);
      
      const modelToUse = userMessage?.model || selectedModel.value;
      const statusResult = await checkQianfanVideoStatus(currentTaskId.value, modelToUse);
      console.log('任务状态:', statusResult);
      
      // 缓存任务状态
      try {
        const videoCache = JSON.parse(localStorage.getItem(STORAGE_KEY_VIDEOS) || '{}');
        if (!videoCache[currentTaskId.value]) {
          videoCache[currentTaskId.value] = {};
        }
        videoCache[currentTaskId.value].status = statusResult.data?.task_status;
        videoCache[currentTaskId.value].timestamp = Date.now();
        localStorage.setItem(STORAGE_KEY_VIDEOS, JSON.stringify(videoCache));
      } catch (error) {
        console.error('缓存任务状态失败:', error);
      }
      
      // 根据任务状态更新UI
      if (statusResult.data?.task_status === 'succeed') {
        // 任务成功完成，只处理一次
        clearInterval(taskCheckInterval.value);
        isLoading.value = false;
        
        // 移除生成中状态
        if (userMessage) {
          userMessage.isGenerating = false;
        }
        
        // 移除之前的状态消息
        removeStatusMessages();
        
        // 检查是否已经添加了成功消息，避免重复添加
        const hasSuccessMessage = messages.value.some(msg => 
          msg.role === 'system' && msg.content.includes('视频生成成功'));
        
        if (!hasSuccessMessage) {
          // 从data.task_result.videos中提取视频URL
          if (statusResult.data?.task_result?.videos && statusResult.data.task_result.videos.length > 0) {
            const videoUrlValue = statusResult.data.task_result.videos[0].url;
            
            // 直接使用原始URL
            const finalVideoUrl = videoUrlValue;
            
            // 存储视频URL到本地存储
            try {
              const videoCache = JSON.parse(localStorage.getItem(STORAGE_KEY_VIDEOS) || '{}');
              if (!videoCache[currentTaskId.value]) {
                videoCache[currentTaskId.value] = {};
              }
              videoCache[currentTaskId.value].remoteUrl = videoUrlValue;
              videoCache[currentTaskId.value].status = 'succeed';
              videoCache[currentTaskId.value].timestamp = Date.now();
              localStorage.setItem(STORAGE_KEY_VIDEOS, JSON.stringify(videoCache));
            } catch (error) {
              console.error('存储视频URL失败:', error);
            }
            
            // 存储视频URL，以便点击时播放
            videoUrl.value = finalVideoUrl;
            videoTitle.value = '生成的视频';
            
            // 找到对应的用户消息，添加视频URL
            if (userMessage) {
              userMessage.videoUrl = finalVideoUrl;
              console.log('已将视频URL添加到用户消息:', userMessage);
            }
            
            // 保存消息到本地存储
            saveMessagesToLocalStorage();
            
            // 添加成功消息，3秒后自动消失
            const successMessage = {
              role: 'system',
              content: '视频生成成功！',
              autoRemove: true
            };
            messages.value.push(successMessage);
            
            // 3秒后移除消息
            setTimeout(() => {
              const index = messages.value.indexOf(successMessage);
              if (index !== -1) {
                messages.value.splice(index, 1);
              }
            }, 3000);
            
            nextTick(() => {
              scrollToBottom();
            });
          } else {
            // 添加消息，3秒后自动消失
            const completeMessage = {
              role: 'system',
              content: '视频生成完成，但未返回视频URL',
              autoRemove: true
            };
            messages.value.push(completeMessage);
            
            // 3秒后移除消息
            setTimeout(() => {
              const index = messages.value.indexOf(completeMessage);
              if (index !== -1) {
                messages.value.splice(index, 1);
              }
            }, 3000);
            
            nextTick(() => {
              scrollToBottom();
            });
          }
        }
      } else if (statusResult.data?.task_status === 'failed') {
        // 任务失败
        clearInterval(taskCheckInterval.value);
        isLoading.value = false;
        
        // 移除生成中状态
        if (userMessage) {
          userMessage.isGenerating = false;
        }
        
        // 移除之前的状态消息
        removeStatusMessages();
        
        // 添加失败消息，3秒后自动消失
        const failedMessage = {
          role: 'system',
          content: `视频生成失败: ${statusResult.data?.task_status_msg || '未知错误'}`,
          autoRemove: true
        };
        messages.value.push(failedMessage);
        
        // 3秒后移除消息
        setTimeout(() => {
          const index = messages.value.indexOf(failedMessage);
          if (index !== -1) {
            messages.value.splice(index, 1);
          }
        }, 3000);
        
        // 保存消息到本地存储
        saveMessagesToLocalStorage();
      } else if (statusResult.data?.task_status === 'processing' || statusResult.data?.task_status === 'submitted') {
        // 任务仍在处理中或排队中
        
        // 设置生成中状态
        if (userMessage && statusResult.data?.task_status === 'processing') {
          userMessage.isGenerating = true;
        }
        
        // 避免重复添加状态消息，只在状态变化时添加
        const statusText = statusResult.data?.task_status === 'processing' ? '处理中' : '排队中';
        const lastMessage = messages.value[messages.value.length - 1];
        
        // 只有当最后一条消息不是相同状态的更新时，才添加新消息
        if (!lastMessage || lastMessage.role !== 'system' || 
            !lastMessage.content.includes(`视频生成${statusText}`)) {
          messages.value.push({
            role: 'system',
            content: `视频生成${statusText}，请耐心等待...`
          });
          
          // 滚动到底部以显示最新状态
          nextTick(() => {
            scrollToBottom();
          });
          
          // 保存消息到本地存储
          saveMessagesToLocalStorage();
        }
      }
      
      // 注意：移除这里的滚动，因为我们已经在各个状态处理中添加了滚动
    } catch (error) {
      console.error('检查任务状态时出错:', error);
      // 不要立即停止检查，可能是临时网络问题
    }
  }, 2000); // 每2秒检查一次
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

// 组件卸载时清除定时器
onBeforeUnmount(() => {
  if (taskCheckInterval.value) {
    clearInterval(taskCheckInterval.value);
  }
});

// Click outside handler for config menus
const handleClickOutside = (event) => {
  if (!activeMenu.value) return;

  const target = event.target;
  let activeMenuElement = null;
  let activeButtonElement = null;

  if (activeMenu.value === 'videoType') {
    activeMenuElement = videoTypeMenuEl.value;
    activeButtonElement = videoTypeButtonEl.value;
  } else if (activeMenu.value === 'model') {
    activeMenuElement = modelMenuEl.value;
    activeButtonElement = modelButtonEl.value;
  } else if (activeMenu.value === 'aspectRatio') {
    activeMenuElement = aspectRatioMenuEl.value;
    activeButtonElement = aspectRatioButtonEl.value;
  } else if (activeMenu.value === 'duration') {
    activeMenuElement = durationMenuEl.value;
    activeButtonElement = durationButtonEl.value;
  } else if (activeMenu.value === 'mode') {
    activeMenuElement = modeMenuEl.value;
    activeButtonElement = modeButtonEl.value;
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

/* 基础容器样式 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8f9fa;
}

/* 消息容器样式 */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-top: 53px; /* 为返回按钮留出空间 */
}

.message-wrapper {
  margin-bottom: 20px;
}

.message-container {
  display: flex;
  width: 100%;
}

.message-bubble {
  max-width: 80%;
}

/* 进度条样式 */
.progress-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  animation: progress 2s infinite;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 100%; }
}

/* 输入区样式 */
.chat-input {
  position: relative;
  padding: 10px 16px; /* 保持与input-container一致的内边距 */
  background-color: #fff; /* 确保背景颜色 */
  border-top: 1px solid #eee; /* 可选：添加边框 */
}

.input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 24px;
}

.input-container input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 8px 12px;
  font-size: 14px;
}

.voice-button {
  background-color: #007bff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.voice-button:hover {
  background-color: #0056b3;
}

.send-icon {
  color: white;
}

/* 缩略图样式 */
.thumbnail-container {
  display: flex;
  align-items: center;
  position: absolute;
  bottom: calc(100% + 10px); /* 悬浮在input-container上方，并留出10px间距 */
  left: 16px; /* 与input-container左对齐 */
  z-index: 10;
  background-color: #ffffff; /* 添加背景色 */
  border: 1px solid #e0e0e0; /* 添加边框 */
  border-radius: 8px; /* 添加圆角 */
  padding: 8px; /* 添加内边距 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 添加阴影 */
}

.thumbnail-image {
  width: 100px;
  height: 100px;
  object-fit: contain; /* 改为 contain 以保持原始比例 */
  border-radius: 4px;
  border: 1px solid #eee;
  background-color: #f0f0f0; /* 为图片空白区域添加背景色 */
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
  z-index: 1000; /* 确保在最顶层 */
  cursor: pointer;
}

.fullscreen-image-content {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px; /* 可选：为图片添加圆角 */
}

/* 清除缩略图按钮样式 */
.clear-thumbnail-btn {
  position: absolute;
  top: 2px; /* 微调以适应视觉效果 */
  right: 2px; /* 微调以适应视觉效果 */
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
  line-height: 20px; /* 确保 '×' 垂直居中 */
  z-index: 1; /* 确保在图片之上 */
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.clear-thumbnail-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

/* 用户消息气泡靠左对齐 */
.message-container.user-message {
  justify-content: flex-start; /* 覆盖默认的右对齐 */
}

/* 可选：如果气泡本身有例如 margin-left: auto 的样式，也需要重置 */
.message-container.user-message .message-bubble {
  margin-left: 0; /* 确保左边没有自动 margin */
  /* margin-right: auto; */ /* 如果需要推到最左边，可以考虑，但通常仅重置 margin-left 即可 */
}

/* Config Buttons Area */
.config-buttons-container {
  display: flex;
  justify-content: center; /* Center the group of buttons */
  gap: 10px; /* Add 10px gap between button wrappers */
  padding: 8px 0px; 
  border-bottom: 1px solid #f0f0f0; 
  margin-bottom: 8px; 
}

.config-button-wrapper {
  position: relative; /* For menu positioning */
}

.config-button {
  background-color: #f7f7f7;
  border: 1px solid #e0e0e0;
  border-radius: 16px; /* Increased border-radius for rounder corners */
  padding: 6px 12px; /* Adjusted padding slightly if needed */
  cursor: pointer;
  font-size: 13px;
  min-width: 80px; /* Adjust as needed */
  text-align: center; /* Center text */
  display: flex;
  justify-content: center; /* Center content (text) */
  align-items: center;
}

.config-button:hover {
  background-color: #efefef;
}

/* .dropdown-arrow class is no longer used */

.config-menu {
  position: absolute;
  bottom: calc(100% + 4px); /* Position above the button */
  left: 0;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 20; /* Ensure it's above other elements like thumbnail */
  min-width: 100%; /* At least as wide as the button */
  padding: 4px 0;
}

.config-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  text-align: center; /* Center text within menu item */
  position: relative; /* For pseudo-element positioning */
}

.config-menu-item:not(:last-child)::after {
  content: "";
  position: absolute;
  bottom: 0; /* Position at the bottom of the item */
  left: 25%; /* Start at 25% from the left to center a 50% width line */
  width: 50%;  /* Line width is 50% of the item's width */
  height: 1px;
  background-color: #eeeeee; /* Line color */
}

.config-menu-item:hover {
  background-color: #f0f0f0;
}

/* 视频预览样式 */
.video-preview-container {
  margin-top: 10px;
  cursor: pointer;
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.video-preview-container:hover {
  transform: scale(1.02);
}

.video-thumbnail {
  position: relative;
  width: 240px;
  height: 135px; /* 16:9 比例 */
  background-color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background-color: #2c3e50; /* 深蓝灰色背景 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-button-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-button-icon {
  width: 50px;
  height: 50px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #333;
}

.video-preview-text {
  padding: 8px;
  background-color: #f5f5f5;
  text-align: center;
  font-size: 14px;
  color: #333;
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
  /* back-button top: 16px, height: 32px. So bottom edge is at 16+32=48px.
     Add 5px spacing: 48px + 5px = 53px */
  padding-top: 53px; 
  /* 注意：如果 chat-content 已经有 overflow-y: scroll/auto，这个 padding 会在滚动区域内部 */
  /* 如果希望整个 chat-content 元素向下移动，而不是其内容，则应使用 margin-top。
     但通常对于滚动内容区域，padding-top 是合适的。*/
}

/* 这里使用 daisyUI 的原生样式，不需要自定义 */

/* 原生视频播放器样式 */
.core-player-container {
  margin-top: 15px;
  width: 100%;
  max-width: 640px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.native-video-player {
  width: 100%;
  height: auto;
  display: block;
  background-color: #000;
}

/* 首尾帧生视频样式 */
.frame-images-container {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.frame-image-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.frame-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.frame-image-wrapper {
  position: relative;
  cursor: pointer;
}

.frame-placeholder {
  width: 100px;
  height: 100px;
  border: 2px dashed #ccc;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: #f9f9f9;
  transition: all 0.2s ease;
}

.frame-placeholder:hover {
  border-color: #007bff;
  background-color: #f0f8ff;
}

.frame-placeholder span {
  font-size: 12px;
  color: #999;
  text-align: center;
}

.single-image-container {
  position: relative;
  cursor: pointer;
}

/* 多图参考生视频样式 */
.multi-images-container {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

/* 多图参考生视频浮窗样式 */
.multi-image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.multi-image-modal {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-upload-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.image-upload-slot {
  aspect-ratio: 1;
  border: 2px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s ease;
  background-color: #fafafa;
}

.image-upload-slot:hover {
  border-color: #007bff;
  background-color: #f0f8ff;
}

.image-upload-slot.has-image {
  border-style: solid;
  border-color: #007bff;
  background-color: white;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  width: 100%;
  height: 100%;
  justify-content: center;
}

.upload-icon {
  font-size: 32px;
  color: #999;
  font-weight: 300;
}

.upload-text {
  font-size: 14px;
  color: #666;
}

.uploaded-image-preview {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.uploaded-image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.remove-image-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.remove-image-btn:hover {
  background-color: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-cancel {
  background-color: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background-color: #e9e9e9;
  color: #333;
}

.btn-confirm {
  background-color: #007bff;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-confirm:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

</style>
