<template>
  <div v-if="show" class="product-window" @click="handleClose">
    <div
      class="product-window-content"
      :class="{ fullscreen: isFullscreen }"
      :style="{ height: windowHeight + '%' }"
      @click.stop
    >
      <div class="product-window-header">
        <h3>{{ productPageTitle }}</h3>
        <div
          class="drag-handle"
          @mousedown="startDrag"
          @touchstart="startDrag"
        >
          <span class="drag-icon">≡</span>
        </div>
        <div class="header-buttons">
          <button class="expand-button" @click="toggleFullscreen">{{ isFullscreen ? '▼' : '▲' }}</button>
          <button class="close-button" @click="handleClose">×</button>
        </div>
      </div>
      <div class="product-window-body">
        <iframe
          v-if="productUrl"
          :src="productUrl"
          :key="iframeKey"
          class="product-iframe"
          frameborder="0"
          allow="scripts"
          referrerpolicy="origin"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox allow-top-navigation allow-top-navigation-by-user-activation"
          @load="onIframeLoad"
        ></iframe>
        <div v-else-if="isLoading" class="iframe-loading">
          <div class="loading-spinner"></div>
          <p>正在加载内容...</p>
        </div>
        <p v-else class="product-name">{{ productName }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, computed, nextTick } from 'vue';

const props = defineProps({
  show: Boolean,
  productName: String,
  productUrl: String,
  isFullscreen: Boolean,
  windowHeight: Number,
  isLoading: Boolean,
  iframeKey: {
    type: [String, Number],
    default: 0
  }
});
const emit = defineEmits([
  'update:show',
  'update:isFullscreen',
  'update:windowHeight',
  'iframe-load'
]);

const handleClose = () => {
  emit('update:show', false);
  emit('update:isFullscreen', false);
};

const productPageTitle = computed(() => {
  if (props.productUrl) {
    try {
      const url = new URL(props.productUrl, window.location.origin);
      return url.hostname.replace('www.', '') || '外部链接';
    } catch (e) {
      return props.productName || '页面内容';
    }
  }
  return props.productName || '页面内容';
});

const startDrag = (event) => {
  event.preventDefault();
  isDragging.value = true;
  if (event.type === 'mousedown') {
    dragStartY.value = event.clientY;
  } else if (event.type === 'touchstart') {
    dragStartY.value = event.touches[0].clientY;
  }
  dragStartHeight.value = props.windowHeight;
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('touchmove', handleDrag, { passive: false });
  document.addEventListener('mouseup', endDrag);
  document.addEventListener('touchend', endDrag);
};

const isDragging = ref(false);
const dragStartY = ref(0);
const dragStartHeight = ref(0);

const handleDrag = (event) => {
  if (!isDragging.value) return;
  if (event.type === 'touchmove') event.preventDefault();
  let currentY;
  if (event.type === 'mousemove') {
    currentY = event.clientY;
  } else if (event.type === 'touchmove') {
    currentY = event.touches[0].clientY;
  }
  const deltaY = dragStartY.value - currentY;
  const windowHeight_px = document.documentElement.clientHeight;
  const sensitivityFactor = deltaY < 0 ? 1.5 : 1.0;
  const adjustedDeltaY = deltaY * sensitivityFactor;
  const deltaPercent = (adjustedDeltaY / windowHeight_px) * 100;
  let newHeight = dragStartHeight.value + deltaPercent;
  newHeight = Math.min(Math.max(newHeight, 30), 100);
  emit('update:windowHeight', newHeight);
  emit('update:isFullscreen', newHeight >= 95);
  nextTick(() => {
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

const toggleFullscreen = (event) => {
  event.stopPropagation();
  emit('update:isFullscreen', !props.isFullscreen);
  emit('update:windowHeight', !props.isFullscreen ? 100 : 50);
};

const onIframeLoad = () => {
  emit('iframe-load');
};
</script>

<style scoped>
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
</style>
