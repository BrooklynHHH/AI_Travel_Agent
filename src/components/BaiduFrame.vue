<template>
  <div class="baidu-frame-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
    <iframe 
      ref="baiduFrame" 
      class="baidu-frame" 
      :src="baiduUrl" 
      frameborder="0"
      @load="onFrameLoad"
    ></iframe>
  </div>
</template>

<script>
export default {
  name: 'BaiduFrame',
  props: {
    // 可以传入搜索关键词
    query: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      loading: true
    }
  },
  computed: {
    // 构建百度URL，可选带搜索关键词
    baiduUrl() {
      const baseUrl = '/baidu-proxy/'
      if (this.query) {
        return `${baseUrl}s?wd=${encodeURIComponent(this.query)}`
      }
      return baseUrl
    }
  },
  methods: {
    // iframe加载完成时执行
    onFrameLoad() {
      this.loading = false
      this.injectStyles()
    },
    
    // 向iframe注入样式以隐藏头部
    injectStyles() {
      try {
        const iframe = this.$refs.baiduFrame
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document
        
        // 创建样式元素
        const styleEl = document.createElement('style')
        styleEl.textContent = `
          .head_wrapper { 
            display: none !important; 
          }
          /* 可以添加更多样式规则来隐藏或修改其他元素 */
        `
        
        // 将样式添加到iframe的head
        if (iframeDoc.head) {
          iframeDoc.head.appendChild(styleEl)
          console.log('成功注入样式以隐藏头部')
        } else {
          console.error('无法访问iframe的head元素')
        }
      } catch (e) {
        console.error('注入样式时出错:', e)
        // 如果出错，通常是由于跨域安全限制
        console.log('可能是跨域安全限制导致无法访问iframe内容')
      }
    }
  }
}
</script>

<style scoped>
.baidu-frame-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  overflow: hidden;
}

.baidu-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
