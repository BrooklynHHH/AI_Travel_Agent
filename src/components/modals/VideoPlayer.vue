<template>
  <div v-if="show" class="video-player-overlay" @click="handleClose">
    <div class="video-player-content" @click.stop>
      <div class="video-player-header">
        <button class="back-button" @click="handleClose">
          <i class="back-icon">←</i>
        </button>
        <div class="video-title">{{ videoTitle }}</div>
        <div class="header-spacer"></div>
      </div>
      <div v-if="videoAvatar || videoLikeCount || videoCommentCount" class="video-info-bar-custom-abs">
        <div class="video-info-right-custom">
          <img v-if="videoAvatar" :src="videoAvatar" alt="avatar" class="video-avatar-custom-abs" />
          <div class="video-like-comment-group-abs">
            <div v-if="videoLikeCount" class="video-like-custom-abs">👍 {{ videoLikeCount }}</div>
            <div v-if="videoCommentCount !== undefined" class="video-comment-custom-abs">💬 {{ videoCommentCount }}</div>
          </div>
        </div>
      </div>
      <div v-if="videoTitle" class="video-title-bottom-abs" :style="{ textAlign: 'left', left: '30px', right: '0', paddingLeft: '0', paddingRight: '24px' }">{{ videoTitle || '' }}</div>
      <div v-if="videoDescription && videoDescription.trim() !== ''" class="video-description-bottom-abs">
        {{ videoDescription }}
      </div>
      <div class="video-player-body" :class="{ 'loading': isLoading }">
        <div v-if="isLoading" class="video-loading">加载中...</div>
        <!-- 使用 vue3-video-play 组件 -->
        <div 
          class="video-container"
          :style="{ 
            maxWidth: videoContainerStyle.maxWidth,
            maxHeight: videoContainerStyle.maxHeight,
            aspectRatio: videoContainerStyle.aspectRatio
          }"
        >
          <vue3VideoPlay
            v-if="videoUrl"
            width="100%"
            height="100%"
            :title="videoTitle || '生成的视频'"
            :src="videoUrl"
            poster=""
            autoPlay
            muted
            class="video-iframe"
            @play="onPlay"
            @pause="onPlay"
            @canplay="onVideoCanPlay"
            @loadedmetadata="onVideoMetadata"
            @error="onVideoError"
            ref="videoPlayer"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, reactive, onMounted, onUnmounted, watch } from 'vue';
import 'vue3-video-play/dist/style.css';

const props = defineProps({
  show: Boolean,
  videoUrl: String,
  videoTitle: String,
  videoAvatar: String,
  videoLikeCount: Number,
  videoCommentCount: Number,
  videoDescription: String
});
const emit = defineEmits(['update:show']);

// 视频状态
const isLoading = ref(true);
const hasError = ref(false);
const errorMessage = ref('');
const videoPlayer = ref(null);

// 视频尺寸信息
const videoMetadata = reactive({
  width: 0,
  height: 0,
  aspectRatio: 16/9, // 默认宽高比
  loaded: false
});

// 容器尺寸
const containerSize = reactive({
  width: 0,
  height: 0
});

// 计算最佳视频容器样式
const videoContainerStyle = reactive({
  maxWidth: '100%',
  maxHeight: '100%',
  aspectRatio: '16/9'
});

// 监听窗口大小变化
let resizeObserver = null;

// 视频播放事件处理函数
const onPlay = () => {
  console.log('视频播放事件', props.videoUrl);
};

// 视频可以播放时
const onVideoCanPlay = () => {
  isLoading.value = false;
  console.log('视频可以播放');
};

// 视频元数据加载完成时
const onVideoMetadata = (event) => {
  try {
    // 获取视频元素
    const videoElement = event.target || (videoPlayer.value?.$el?.querySelector('video'));
    
    if (videoElement) {
      // 获取视频原始尺寸
      videoMetadata.width = videoElement.videoWidth;
      videoMetadata.height = videoElement.videoHeight;
      
      if (videoMetadata.width && videoMetadata.height) {
        videoMetadata.aspectRatio = videoMetadata.width / videoMetadata.height;
        videoMetadata.loaded = true;
        
        // 更新容器样式
        updateVideoContainerStyle();
        console.log('视频元数据加载完成', videoMetadata);
      }
    }
  } catch (error) {
    console.error('获取视频元数据失败', error);
  }
};

// 视频加载错误
const onVideoError = (error) => {
  isLoading.value = false;
  hasError.value = true;
  errorMessage.value = '视频加载失败';
  console.error('视频加载错误', error);
};

// 更新视频容器样式
const updateVideoContainerStyle = () => {
  if (!videoMetadata.loaded) return;
  
  // 获取播放器容器尺寸
  const playerBody = document.querySelector('.video-player-body');
  if (playerBody) {
    containerSize.width = playerBody.clientWidth;
    containerSize.height = playerBody.clientHeight;
  }
  
  // 计算容器宽高比
  const containerRatio = containerSize.width / containerSize.height;
  
  // 根据视频和容器的宽高比决定如何调整尺寸
  if (videoMetadata.aspectRatio > containerRatio) {
    // 视频更宽，以宽度为基准
    videoContainerStyle.maxWidth = '100%';
    videoContainerStyle.maxHeight = `${(containerSize.width / videoMetadata.aspectRatio)}px`;
  } else {
    // 视频更高，以高度为基准
    videoContainerStyle.maxHeight = '100%';
    videoContainerStyle.maxWidth = `${(containerSize.height * videoMetadata.aspectRatio)}px`;
  }
  
  // 设置容器宽高比
  videoContainerStyle.aspectRatio = `${videoMetadata.aspectRatio}`;
  
  console.log('更新视频容器样式', videoContainerStyle);
};

// 监听窗口大小变化
const setupResizeObserver = () => {
  const playerBody = document.querySelector('.video-player-body');
  if (playerBody && window.ResizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      updateVideoContainerStyle();
    });
    resizeObserver.observe(playerBody);
  }
};

// 监听视频URL变化
watch(() => props.videoUrl, () => {
  if (props.videoUrl) {
    isLoading.value = true;
    hasError.value = false;
    errorMessage.value = '';
    videoMetadata.loaded = false;
  }
});

// 监听显示状态变化
watch(() => props.show, (newVal) => {
  if (newVal) {
    // 组件显示时，设置监听
    setTimeout(() => {
      setupResizeObserver();
    }, 100);
  } else {
    // 组件隐藏时，清理监听
    if (resizeObserver) {
      resizeObserver.disconnect();
    }
  }
});

onMounted(() => {
  if (props.show) {
    setupResizeObserver();
  }
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});

const handleClose = () => {
  emit('update:show', false);
  document.body.style.overflow = '';
};
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
  position: relative;
}
.video-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: auto;
  transition: all 0.3s ease;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
}
.video-iframe {
  width: 100%;
  height: 100%;
  background-color: #000;
  object-fit: contain;
}
.video-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 16px;
  background: rgba(0, 0, 0, 0.5);
  padding: 10px 20px;
  border-radius: 4px;
  z-index: 5;
}
.video-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ff4d4f;
  font-size: 16px;
  background: rgba(0, 0, 0, 0.7);
  padding: 15px 25px;
  border-radius: 8px;
  z-index: 5;
  text-align: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .video-container {
    width: 100%;
    height: auto;
  }
  .video-title-bottom-abs {
    font-size: 16px;
    bottom: 15px;
  }
  .video-description-bottom-abs {
    font-size: 14px;
    bottom: 20px;
    padding: 6px 12px;
  }
  .video-info-bar-custom-abs {
    right: 16px;
  }
  .video-avatar-custom-abs {
    width: 48px;
    height: 48px;
  }
  .video-like-custom-abs, .video-comment-custom-abs {
    font-size: 16px;
    padding: 4px 14px;
  }
}
</style>
