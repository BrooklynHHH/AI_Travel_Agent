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
            <div v-if="message.image" class="user-image-container" :data-task-id="message.taskId">
              <div style="position: relative; display: inline-block;">
                <img :src="message.image" :ref="el => { if(message.hasOcr) ocrImage = el }" style="max-width: 320px; max-height: 300px; border: 1px solid #eee; object-fit: contain;" />
                <canvas
                  v-if="message.hasOcr"
                  width="320"
                  height="240"
                  ref="ocrCanvas"
                  style="position: absolute; left: 0; top: 0; pointer-events: none;"
                ></canvas>
                <!-- 视频播放按钮 -->
                <div v-if="message.videoUrl" class="play-button-overlay" @click="openVideoInNewTab(message.videoUrl)">
                  <div class="play-button-icon">▶</div>
                </div>
                <!-- 视频生成进度条 -->
                <div v-if="message.isGenerating" class="progress-overlay">
                  <div class="spinner"></div>
                </div>
              </div>
            </div>
            <div v-if="message.content">{{ message.content }}</div>
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
          </div>
        </div>
      </div>
      <div style="height: 20px"></div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <!-- 缩略图显示区域 -->
      <div class="thumbnail-container" v-if="uploadedImage" @click="showFullScreenImage">
        <img :src="uploadedImage" class="thumbnail-image" alt="上传的图片" />
        <div class="clear-thumbnail-btn" @click.stop="clearSelectedImage">×</div>
      </div>

      <!-- Configuration Buttons -->
      <div class="config-buttons-container">
        <!-- Resolution Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('resolution')" ref="resolutionButtonEl">
            {{ selectedResolution }}
          </button>
          <div v-if="activeMenu === 'resolution'" class="config-menu" ref="resolutionMenuEl">
            <div v-for="option in resolutionOptions" :key="option" class="config-menu-item" @click="selectResolutionOption(option)">
              {{ option }}
            </div>
          </div>
        </div>

        <!-- Duration Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('duration')" ref="durationButtonEl">
            时长: {{ selectedDuration }}
          </button>
          <div v-if="activeMenu === 'duration'" class="config-menu" ref="durationMenuEl">
            <div v-for="option in durationOptions" :key="option" class="config-menu-item" @click="selectDurationOption(option)">
              时长: {{ option }}
            </div>
          </div>
        </div>

        <!-- Camera Fixed Button -->
        <div class="config-button-wrapper">
          <button class="config-button" @click="toggleMenu('cameraFixed')" ref="cameraFixedButtonEl">
            镜头: {{ selectedCameraFixed.text }}
          </button>
          <div v-if="activeMenu === 'cameraFixed'" class="config-menu" ref="cameraFixedMenuEl">
            <div v-for="option in cameraFixedOptions" :key="option.value" class="config-menu-item" @click="selectCameraFixedOption(option)">
              镜头: {{ option.text }}
            </div>
          </div>
        </div>
      </div>

      <div class="input-container">
        <!-- 上传图片按钮 -->
        <label class="upload-btn" style="margin-right: 8px;">
          <input type="file" accept="image/*" @change="onFileChange" style="display: none;" />
          <i class="plus-icon">📷</i>
        </label>
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
    </div>
  </div>

  <!-- 全屏图片查看器 -->
  <div v-if="isFullScreenImageVisible" class="fullscreen-image-overlay" @click="hideFullScreenImage">
    <img :src="fullScreenImageUrl" alt="Full screen image" class="fullscreen-image-content" />
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, onBeforeUnmount } from 'vue'; // Added watch, onBeforeUnmount
import { useRouter } from 'vue-router';
import VideoPlayer from '../components/modals/VideoPlayer.vue';
import { generateVideo, checkVideoGenerationStatus } from '../utils/videoGenerationApi';

const router = useRouter();
const userInput = ref('');
const messages = ref([]);
const conversationId = ref('');
const uploadedImage = ref(null); // Thumbnail
const originalImage = ref(null); // Original image DataURL for fullscreen
const ocrImage = ref(null);
const isFullScreenImageVisible = ref(false);
const fullScreenImageUrl = ref('');

// Configuration Button States
const resolutionOptions = ref(['480p', '720p', '1080p']);
const selectedResolution = ref(resolutionOptions.value[0]);

const durationOptions = ref(['5s', '10s']);
const selectedDuration = ref(durationOptions.value[0]);

const cameraFixedOptions = ref([
  { text: '固定', value: true },
  { text: '不固定', value: false },
]);
const selectedCameraFixed = ref(cameraFixedOptions.value[0]); // Stores the selected object {text, value}

const activeMenu = ref(null); // null, 'resolution', 'duration', 'cameraFixed'

// Template refs for buttons and menus for click outside detection
const resolutionButtonEl = ref(null);
const resolutionMenuEl = ref(null);
const durationButtonEl = ref(null);
const durationMenuEl = ref(null);
const cameraFixedButtonEl = ref(null);
const cameraFixedMenuEl = ref(null);


// 返回按钮功能
const goBack = () => {
  router.push('/advanced');
};

// 在组件加载时生成会话ID
onMounted(() => {
  const timestamp = new Date().getTime();
  conversationId.value = `ocr_${timestamp}`;
  console.log('生成会话ID:', conversationId.value);
});

// 将DataURL转换为Blob
// const dataURLtoBlob = (dataURL) => {
//   const arr = dataURL.split(',');
//   const mime = arr[0].match(/:(.*?);/)[1];
//   const bstr = atob(arr[1]);
//   let n = bstr.length;
//   const u8arr = new Uint8Array(n);
  
//   while (n--) {
//     u8arr[n] = bstr.charCodeAt(n);
//   }
  
//   return new Blob([u8arr], { type: mime });
// };

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

const selectResolutionOption = (option) => {
  selectedResolution.value = option;
  activeMenu.value = null;
};

const selectDurationOption = (option) => {
  selectedDuration.value = option;
  activeMenu.value = null;
};

const selectCameraFixedOption = (option) => {
  selectedCameraFixed.value = option;
  activeMenu.value = null;
};

// 显示全屏图片
const showFullScreenImage = () => {
  if (originalImage.value) {
    fullScreenImageUrl.value = originalImage.value;
    isFullScreenImageVisible.value = true;
  }
};

// 播放视频
const playVideo = (videoUrlValue) => {
  if (videoUrlValue) {
    videoUrl.value = videoUrlValue;
    videoTitle.value = '生成的视频';
    showVideoPlayer.value = true;
  }
};

// 在新标签页中打开视频
const openVideoInNewTab = (url) => {
  if (url) {
    window.open(url, '_blank');
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
  if ((!userInput.value.trim() && !uploadedImage.value) || isLoading.value) return;
  
  // 添加用户消息
  const message = {
    role: 'user',
    content: userInput.value
  };
  
  // 如果有上传的图片，添加到消息中
  if (originalImage.value) { // 使用 originalImage 以在聊天中显示原始比例图片
    message.image = originalImage.value;
  } else if (uploadedImage.value) {
    // Fallback or specific logic if only thumbnail was intended (should not happen with current flow)
    // For safety, ensure both are cleared if thumbnail was somehow present without original
    uploadedImage.value = null;
    originalImage.value = null;
  }
  
  messages.value.push(message);
  
  // 调用视频生成API
  try {
    // 检查是否有图片和文本输入
    if (message.image || message.content) {
      isLoading.value = true;
      
      // 获取当前选择的分辨率（去掉"p"后缀）
      const resolution = selectedResolution.value;
      
      // 获取当前选择的时长（去掉"s"后缀并转换为数字）
      const duration = parseInt(selectedDuration.value.replace('s', ''));
      
      // 获取当前选择的相机固定设置
      const cameraFixed = selectedCameraFixed.value.value;
      
      // 如果有图片，需要将其转换为File对象
      let imageFile = null;
      if (message.image) {
        // 从Data URL创建Blob
        const fetchResponse = await fetch(message.image);
        const blob = await fetchResponse.blob();
        
        // 从Blob创建File对象
        const filename = `image_${Date.now()}.${blob.type.split('/')[1] || 'png'}`;
        imageFile = new File([blob], filename, { type: blob.type });
        
        // 发送后清空缩略图和原始图
        uploadedImage.value = null;
        originalImage.value = null; 
        // 如果全屏预览是当前图片，也关闭它
        if (isFullScreenImageVisible.value && fullScreenImageUrl.value === message.image) {
          hideFullScreenImage();
        }
      }
      
      // 调用generateVideo函数
      const result = await generateVideo(
        message.content || "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验", // 如果没有文本，使用默认文本
        resolution,
        duration,
        cameraFixed,
        imageFile
      );
      
      console.log('视频生成API响应:', result);
      
      // 从响应中提取任务ID
      if (result && result.id) {
        currentTaskId.value = result.id;
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
    }
  } catch (error) {
    console.error('视频生成失败:', error);
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
    
    try {
      const statusResult = await checkVideoGenerationStatus(currentTaskId.value);
      console.log('任务状态:', statusResult);
      
      // 找到对应的用户消息
      const userMessage = messages.value.find(msg => 
        msg.role === 'user' && msg.taskId === currentTaskId.value);
      
      // 根据任务状态更新UI
      if (statusResult.status === 'succeeded') {
        // 任务成功完成，只处理一次
        clearInterval(taskCheckInterval.value);
        isLoading.value = false;
        
        // 移除生成中状态
        if (userMessage) {
          userMessage.isGenerating = false;
        }
        
        // 检查是否已经添加了成功消息，避免重复添加
        const hasSuccessMessage = messages.value.some(msg => 
          msg.role === 'system' && msg.content.includes('视频生成成功'));
        
        if (!hasSuccessMessage) {
          // 从content.video_url中提取视频URL
          if (statusResult.content && statusResult.content.video_url) {
            const videoUrlValue = statusResult.content.video_url;
            
            // 更新消息，添加视频预览
            // const videoMessage = {
            //   role: 'system',
            //   content: '视频生成成功！点击预览查看视频',
            //   videoUrl: videoUrlValue
            // };
            
            // 存储视频URL，以便点击时播放
            videoUrl.value = videoUrlValue;
            videoTitle.value = '生成的视频';
            
            // 找到对应的用户消息，添加视频URL
            const userMessage = messages.value.find(msg => 
              msg.role === 'user' && msg.taskId === currentTaskId.value);
            
            if (userMessage) {
              userMessage.videoUrl = videoUrlValue;
              console.log('已将视频URL添加到用户消息:', userMessage);
            }
            
            // 添加消息并确保只在DOM更新后滚动一次
            // messages.value.push(videoMessage);
            nextTick(() => {
              scrollToBottom();
            });
          } else {
            messages.value.push({
              role: 'system',
              content: '视频生成完成，但未返回视频URL'
            });
            nextTick(() => {
              scrollToBottom();
            });
          }
        }
      } else if (statusResult.status === 'failed') {
        // 任务失败
        clearInterval(taskCheckInterval.value);
        isLoading.value = false;
        
        // 移除生成中状态
        if (userMessage) {
          userMessage.isGenerating = false;
        }
        
        messages.value.push({
          role: 'system',
          content: `视频生成失败: ${statusResult.error || '未知错误'}`
        });
      } else if (statusResult.status === 'running' || statusResult.status === 'queued') {
        // 任务仍在处理中或排队中
        
        // 设置生成中状态
        if (userMessage && statusResult.status === 'running') {
          userMessage.isGenerating = true;
        }
        
        // 避免重复添加状态消息，只在状态变化时添加
        const statusText = statusResult.status === 'running' ? '处理中' : '排队中';
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
        }
      } else if (statusResult.status === 'cancelled') {
        // 任务被取消
        clearInterval(taskCheckInterval.value);
        isLoading.value = false;
        
        // 移除生成中状态
        if (userMessage) {
          userMessage.isGenerating = false;
        }
        
        messages.value.push({
          role: 'system',
          content: '视频生成任务已被取消'
        });
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

  if (activeMenu.value === 'resolution') {
    activeMenuElement = resolutionMenuEl.value;
    activeButtonElement = resolutionButtonEl.value;
  } else if (activeMenu.value === 'duration') {
    activeMenuElement = durationMenuEl.value;
    activeButtonElement = durationButtonEl.value;
  } else if (activeMenu.value === 'cameraFixed') {
    activeMenuElement = cameraFixedMenuEl.value;
    activeButtonElement = cameraFixedButtonEl.value;
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
  position: relative;
  padding: 10px 16px; /* 保持与input-container一致的内边距 */
  background-color: #fff; /* 确保背景颜色 */
  border-top: 1px solid #eee; /* 可选：添加边框 */
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
  justify-content: center;
  margin: 8px 0;
  width: 100%;
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
</style>
