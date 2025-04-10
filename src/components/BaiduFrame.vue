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
    
    <!-- 半屏浮窗 -->
    <div v-if="showFloatingWindow" class="floating-window" :class="{ 'full-height': isFullHeight }">
      <div class="floating-window-header">
        <span>图片搜索结果</span>
        <div class="floating-window-controls">
          <button @click="toggleFullHeight" class="control-button">
            {{ isFullHeight ? '半屏' : '全屏' }}
          </button>
          <button @click="closeFloatingWindow" class="control-button close-button">
            ×
          </button>
        </div>
      </div>
      <iframe 
        ref="floatingFrame" 
        class="floating-frame" 
        :src="floatingUrl" 
        frameborder="0"
      ></iframe>
    </div>
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
      loading: true,
      showFloatingWindow: false,
      floatingUrl: '',
      isFullHeight: false
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
      this.handleAisearchLinks()
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
    },
    
    // 处理aisearch://jump/和aisearch://imgjump/协议的链接
    handleAisearchLinks() {
      try {
        const iframe = this.$refs.baiduFrame
        
        // 使用代理拦截方法, 避免跨域限制
        this.setupFrameEventProxy(iframe)
        
        console.log('成功设置aisearch链接处理器')
      } catch (e) {
        console.error('设置aisearch链接处理器时出错:', e)
      }
    },
    
    // 设置iframe事件代理
    setupFrameEventProxy(iframe) {
      // 保存原始的window.open方法
      const originalWindowOpen = window.open
      
      // 代理window.open方法以捕获aisearch链接
      window.open = (url, target, features) => {
        console.log('检测到window.open调用:', url)
        
        // 检查是否是aisearch链接
        if (url && typeof url === 'string') {
          // 处理aisearch://imgjump/协议（图片搜索）
          if (url.startsWith('aisearch://imgjump/')) {
            // 提取实际URL，移除aisearch://imgjump/前缀
            const actualUrl = url.substring('aisearch://imgjump/'.length)
            
            if (actualUrl.startsWith('https://') || actualUrl.startsWith('http://')) {
              // 解析URL并创建代理路径
              const urlObj = new URL(actualUrl)
              const proxyPath = urlObj.pathname + urlObj.search
              const proxyUrl = '/baidu-proxy' + proxyPath
              
              console.log('拦截到aisearch图片链接，在浮窗中打开:', proxyUrl)
              
              // 在浮窗中打开图片搜索结果
              this.openFloatingWindow(proxyUrl)
              return null // 阻止原始window.open
            }
          }
          // 处理aisearch://jump/协议（普通链接）
          else if (url.startsWith('aisearch://jump/')) {
            // 提取实际URL，移除aisearch://jump/前缀
            const actualUrl = url.substring('aisearch://jump/'.length)
            
            if (actualUrl.startsWith('https://') || actualUrl.startsWith('http://')) {
              // 如果是百度域的URL，通过baidu-proxy跳转
              if (actualUrl.includes('baidu.com')) {
                // 解析URL并创建代理路径
                const urlObj = new URL(actualUrl)
                const proxyPath = urlObj.pathname + urlObj.search
                const proxyUrl = '/baidu-proxy' + proxyPath
                
                console.log('拦截到aisearch链接，跳转到:', proxyUrl)
                iframe.src = proxyUrl
                return null // 阻止原始window.open
              }
            }
          }
        }
        
        // 对于非aisearch链接，使用原始的window.open
        return originalWindowOpen.call(window, url, target, features)
      }
      
      // 尝试直接在iframe中添加click事件监听器
      try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document
        
        // 监听iframe内的点击事件
        iframeDoc.addEventListener('click', event => {
          // 查找被点击的链接元素
          let target = event.target
          while (target && target.tagName !== 'A') {
            target = target.parentElement
          }
          
          // 如果找到了链接
          if (target && target.tagName === 'A') {
            const href = target.getAttribute('href')
            this.processAisearchUrl(href, iframe)
          }
        })
      } catch (e) {
        console.warn('无法直接监听iframe内部点击，将使用window.open代理:', e)
      }
      
      // 添加message事件监听器，用于接收从iframe内部发送的消息
      window.addEventListener('message', event => {
        // 安全检查，确保消息来源可信
        if (event.source === iframe.contentWindow) {
          const { type, url } = event.data || {}
          
          if (type === 'aisearch-link' && url) {
            this.processAisearchUrl(url, iframe)
          }
        }
      })
      
      // 监听iframe的load事件
      iframe.addEventListener('load', () => {
        try {
          // 尝试注入脚本到iframe中，以捕获链接点击
          const iframeDoc = iframe.contentDocument || iframe.contentWindow.document
          const script = iframeDoc.createElement('script')
          script.textContent = `
            // 监听所有点击事件
            document.addEventListener('click', function(event) {
              let target = event.target;
              while (target && target.tagName !== 'A') {
                target = target.parentElement;
              }
              
              if (target && target.tagName === 'A') {
                const href = target.getAttribute('href');
                if (href && (href.startsWith('aisearch://jump/') || href.startsWith('aisearch://imgjump/'))) {
                  event.preventDefault();
                  window.parent.postMessage({ type: 'aisearch-link', url: href }, '*');
                }
              }
            }, true);
            
            // 代理window.open方法以捕获aisearch链接
            const originalWindowOpen = window.open;
            window.open = function(url, target, features) {
              if (url && typeof url === 'string' && 
                  (url.startsWith('aisearch://jump/') || url.startsWith('aisearch://imgjump/'))) {
                window.parent.postMessage({ type: 'aisearch-link', url: url }, '*');
                return null;
              }
              return originalWindowOpen.call(window, url, target, features);
            };
          `;
          iframeDoc.head.appendChild(script)
        } catch (e) {
          console.warn('无法注入脚本到iframe:', e)
        }
      })
    },
    
    // 处理aisearch URL
    processAisearchUrl(url, iframe) {
      if (!url || typeof url !== 'string') return
      
      // 处理aisearch://imgjump/协议（图片搜索）
      if (url.startsWith('aisearch://imgjump/')) {
        // 提取实际URL，移除aisearch://imgjump/前缀
        const actualUrl = url.substring('aisearch://imgjump/'.length)
        
        if (actualUrl.startsWith('https://') || actualUrl.startsWith('http://')) {
          // 解析URL并创建代理路径
          const urlObj = new URL(actualUrl)
          const proxyPath = urlObj.pathname + urlObj.search
          const proxyUrl = '/baidu-proxy' + proxyPath
          
          console.log('拦截到aisearch图片链接，在浮窗中打开:', proxyUrl)
          
          // 在浮窗中打开图片搜索结果
          this.openFloatingWindow(proxyUrl)
        }
      }
      // 处理aisearch://jump/协议（普通链接）
      else if (url.startsWith('aisearch://jump/')) {
        // 提取实际URL，移除aisearch://jump/前缀
        const actualUrl = url.substring('aisearch://jump/'.length)
        
        if (actualUrl.startsWith('https://') || actualUrl.startsWith('http://')) {
          // 如果是百度域的URL，通过baidu-proxy跳转
          if (actualUrl.includes('baidu.com')) {
            // 解析URL并创建代理路径
            const urlObj = new URL(actualUrl)
            const proxyPath = urlObj.pathname + urlObj.search
            const proxyUrl = '/baidu-proxy' + proxyPath
            
            console.log('拦截到aisearch链接，跳转到:', proxyUrl)
            iframe.src = proxyUrl
          } else {
            // 非百度域的URL，在新标签页打开
            console.log('外部URL:', actualUrl)
            window.open(actualUrl, '_blank')
          }
        }
      }
    },
    
    // 在浮窗中打开URL
    openFloatingWindow(url) {
      this.floatingUrl = url
      this.showFloatingWindow = true
    },
    
    // 关闭浮窗
    closeFloatingWindow() {
      this.showFloatingWindow = false
      this.floatingUrl = ''
      this.isFullHeight = false
    },
    
    // 切换浮窗高度（全屏/半屏）
    toggleFullHeight() {
      this.isFullHeight = !this.isFullHeight
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

/* 浮窗样式 */
.floating-window {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 60%;
  height: 50%; /* 默认半屏 */
  background-color: white;
  border-radius: 8px 0 0 0;
  box-shadow: -2px -2px 10px rgba(0, 0, 0, 0.2);
  z-index: 100;
  display: flex;
  flex-direction: column;
  transition: height 0.3s ease;
}

.floating-window.full-height {
  height: 85%; /* 全屏模式 */
}

.floating-window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f5f5;
  border-radius: 8px 0 0 0;
  border-bottom: 1px solid #e0e0e0;
}

.floating-window-controls {
  display: flex;
  gap: 8px;
}

.control-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.control-button:hover {
  background-color: #e0e0e0;
}

.close-button {
  font-size: 18px;
  font-weight: bold;
}

.floating-frame {
  flex: 1;
  width: 100%;
  border: none;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
