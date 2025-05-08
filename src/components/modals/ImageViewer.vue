<template>
  <div v-if="show" class="image-viewer" @click="handleClose">
    <div class="image-viewer-header">
      <span class="image-viewer-title">{{ keyword }}</span>
      <button class="close-button" @click.stop="handleClose">×</button>
    </div>
    <div class="image-viewer-content" @click.stop>
      <div class="image-slider-container" ref="imageSlider">
        <div 
          class="image-slider" 
          :style="{ transform: `translateX(${-currentIndex * 100}%)` }"
        >
          <div 
            v-for="(image, index) in images" 
            :key="index"
            class="image-slide"
          >
            <img :src="image.url" :alt="image.keyword" class="viewer-image" />
          </div>
        </div>
      </div>
      <button v-if="currentIndex > 0" 
        class="slider-nav-button prev-button" 
        @click.stop="prevImage"
      >
        ◀
      </button>
      <button v-if="currentIndex < images.length - 1" 
        class="slider-nav-button next-button" 
        @click.stop="nextImage"
      >
        ▶
      </button>
      <div class="image-viewer-counter">
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
  show: Boolean,
  images: {
    type: Array,
    default: () => []
  },
  currentIndex: {
    type: Number,
    default: 0
  },
  keyword: {
    type: String,
    default: ''
  }
});
const emit = defineEmits(['update:show', 'update:currentIndex']);

const imageSlider = ref(null);
const initialTouchX = ref(0);
const isSwiping = ref(false);
const swipeThreshold = 50;

const handleClose = () => {
  emit('update:show', false);
  // 恢复背景滚动
  document.body.style.overflow = '';
  removeTouchListeners();
};

const prevImage = () => {
  if (props.currentIndex > 0) {
    emit('update:currentIndex', props.currentIndex - 1);
  }
};
const nextImage = () => {
  if (props.currentIndex < props.images.length - 1) {
    emit('update:currentIndex', props.currentIndex + 1);
  }
};

const handleTouchStart = (event) => {
  initialTouchX.value = event.touches[0].clientX;
  isSwiping.value = true;
};
const handleTouchMove = () => {
  if (!isSwiping.value) return;
};
const handleTouchEnd = (event) => {
  if (!isSwiping.value) return;
  const touchEndX = event.changedTouches[0].clientX;
  const diffX = touchEndX - initialTouchX.value;
  if (Math.abs(diffX) > swipeThreshold) {
    if (diffX < 0 && props.currentIndex < props.images.length - 1) {
      nextImage();
    } else if (diffX > 0 && props.currentIndex > 0) {
      prevImage();
    }
  }
  isSwiping.value = false;
};

function addTouchListeners() {
  if (imageSlider.value) {
    imageSlider.value.addEventListener('touchstart', handleTouchStart);
    imageSlider.value.addEventListener('touchmove', handleTouchMove);
    imageSlider.value.addEventListener('touchend', handleTouchEnd);
  }
}
function removeTouchListeners() {
  if (imageSlider.value) {
    imageSlider.value.removeEventListener('touchstart', handleTouchStart);
    imageSlider.value.removeEventListener('touchmove', handleTouchMove);
    imageSlider.value.removeEventListener('touchend', handleTouchEnd);
  }
}

watch(() => props.show, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden';
    nextTick(addTouchListeners);
  } else {
    document.body.style.overflow = '';
    removeTouchListeners();
  }
});

onMounted(() => {
  if (props.show) {
    document.body.style.overflow = 'hidden';
    nextTick(addTouchListeners);
  }
});
onBeforeUnmount(() => {
  document.body.style.overflow = '';
  removeTouchListeners();
});
</script>

<style scoped>
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
