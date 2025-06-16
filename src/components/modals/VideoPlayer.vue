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
      <div class="video-player-body">
        <!-- 使用 vue3-video-play 组件 -->
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
          @canplay="onPlay"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
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

// 视频播放事件处理函数
const onPlay = () => {
  console.log('视频播放事件', props.videoUrl);
};

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
}
.video-iframe {
  width: 100%;
  height: 100%;
  background-color: #000;
}
</style>
