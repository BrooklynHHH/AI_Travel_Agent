<template>
  <div class="baidu-wenku-container">
    <!-- 返回按钮 -->
    <div class="back-button" @click="goBack">
      <i class="back-icon">&lt;</i>
    </div>
    
    <!-- 页面标题 -->
    <div class="header">
      <h1 class="title">百度文库</h1>
      <p class="subtitle">海量文档资源，智能搜索体验</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载百度文库...</p>
    </div>

    <!-- iframe容器 -->
    <div class="iframe-container" :class="{ 'loading': isLoading }">
      <div id="baidu-wenku-embed" class="embed-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoading = ref(true);

// 返回按钮功能
const goBack = () => {
  router.push('/advanced');
};

// 加载百度文库SDK
const loadBaiduWenKuSDK = () => {
  // 检查是否已经加载过SDK
  if (window.EmbedWebSDK) {
    initializeBaiduWenKu();
    return;
  }

  // 创建script标签加载SDK
  const script = document.createElement('script');
  script.src = 'https://agi-dev-platform-web.bj.bcebos.com/ai_apaas/embed/output/embedFullSDK.js?responseExpires=0';
  script.onload = () => {
    console.log('百度文库SDK加载成功');
    initializeBaiduWenKu();
  };
  script.onerror = () => {
    console.error('百度文库SDK加载失败');
    isLoading.value = false;
  };
  
  document.head.appendChild(script);
};

// 初始化百度文库
const initializeBaiduWenKu = () => {
  try {
    if (window.EmbedWebSDK) {
      new window.EmbedWebSDK({
        appId: 'b5353ed8-1672-4127-9c07-b8bee049a420',
        code: 'embedtDnrw9xsBm7TiSMmjrlx',
        renderConfig: {
          width: '100%',
          height: '100%'
        }
      });
      
      // 延迟隐藏加载状态，确保内容已渲染
      setTimeout(() => {
        isLoading.value = false;
      }, 2000);
    } else {
      console.error('EmbedWebSDK 未找到');
      isLoading.value = false;
    }
  } catch (error) {
    console.error('初始化百度文库失败:', error);
    isLoading.value = false;
  }
};

onMounted(() => {
  document.title = '百度文库 - 小米AI搜索';
  loadBaiduWenKuSDK();
});

onUnmounted(() => {
  // 清理可能的全局变量或事件监听器
  document.title = '小米AI搜索';
});
</script>

<style scoped>
.baidu-wenku-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 返回按钮样式 */
.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  cursor: pointer;
  z-index: 1000;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 1);
  transform: scale(1.05);
}

.back-icon {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 页面标题 */
.header {
  text-align: center;
  padding: 60px 20px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* iframe容器 */
.iframe-container {
  flex: 1;
  position: relative;
  background-color: white;
  margin: 0;
  overflow: hidden;
}

.iframe-container.loading {
  display: none;
}

.embed-container {
  width: 100%;
  height: 100%;
  border: none;
  background-color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 50px 16px 16px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .back-button {
    width: 36px;
    height: 36px;
    top: 12px;
    left: 12px;
  }
  
  .back-icon {
    font-size: 16px;
  }
}

/* 确保iframe内容正确显示 */
:deep(.embed-container iframe) {
  width: 100% !important;
  height: 100% !important;
  border: none !important;
}
</style>
