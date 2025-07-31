<template>
  <div class="ai-news-container">
    <!-- 頂部導航 -->
    <div class="header">
      <div class="nav-bar">
        <div class="nav-left">
          <button class="back-btn" @click="$router.go(-1)">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <div class="nav-right">
          <button class="nav-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="nav-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="main-content">
      <!-- 統一的新聞卡片列表 -->
      <div class="news-container">
        <!-- AI 早報卡片 -->
        <div class="news-card ai-daily-card">
          <div class="card-header">
            <div class="header-left">
              <div class="ai-icon">
                <span class="ai-text">AI</span>
              </div>
              <span class="daily-text">{{ currentReportTitle }}</span>
            </div>
            <div class="header-actions">
              <button class="listen-btn" @click="togglePlayback" :class="{ 'playing': isPlaying, 'loading': isLoading }">
                <svg v-if="!isPlaying && !isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M8 5V19L19 12L8 5Z" fill="currentColor"/>
                </svg>
                <svg v-else-if="isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M6 4H10V20H6V4ZM14 4H18V20H14V4Z" fill="currentColor"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M6 4H10V20H6V4ZM14 4H18V20H14V4Z" fill="currentColor"/>
                </svg>
                <span class="btn-text">{{ getButtonText() }}</span>
              </button>
              <button class="settings-btn" @click="showModeSelector = true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2"/>
                  <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.257 9.77251 19.9887C9.5799 19.7204 9.31074 19.5199 9 19.41C8.69838 19.2769 8.36381 19.2372 8.03941 19.296C7.71502 19.3548 7.41568 19.5095 7.18 19.74L7.12 19.8C6.93425 19.986 6.71368 20.1335 6.47088 20.2341C6.22808 20.3348 5.96783 20.3866 5.705 20.3866C5.44217 20.3866 5.18192 20.2448 4.93912 20.2341C4.69632 20.1335 4.47575 19.986 4.29 19.8C4.10405 19.6143 3.95653 19.3937 3.85588 19.1509C3.75523 18.9081 3.70343 18.6478 3.70343 18.385C3.70343 18.1222 3.75523 17.8619 3.85588 17.6191C3.95653 17.3763 4.10405 17.1557 4.29 16.97L4.35 16.91C4.58054 16.6743 4.7352 16.375 4.794 16.0506C4.8528 15.7262 4.8131 15.3916 4.68 15.09C4.55324 14.7942 4.34276 14.542 4.07447 14.3643C3.80618 14.1866 3.49179 14.0913 3.17 14.09H3C2.46957 14.09 1.96086 13.8793 1.58579 13.5042C1.21071 13.1291 1 12.6204 1 12.09C1 11.5596 1.21071 11.0509 1.58579 10.6758C1.96086 10.3007 2.46957 10.09 3 10.09H3.09C3.42099 10.0823 3.743 9.97512 4.0113 9.78251C4.2796 9.5899 4.4801 9.32074 4.59 9.01C4.72312 8.69838 4.76281 8.36381 4.70401 8.03941C4.64521 7.71502 4.49054 7.41568 4.26 7.18L4.2 7.12C4.01405 6.93425 3.86653 6.71368 3.76588 6.47088C3.66523 6.22808 3.61343 5.96783 3.61343 5.705C3.61343 5.44217 3.66523 5.18192 3.76588 4.93912C3.86653 4.69632 4.01405 4.47575 4.2 4.29C4.38575 4.10405 4.60632 3.95653 4.84912 3.85588C5.09192 3.75523 5.35217 3.70343 5.615 3.70343C5.87783 3.70343 6.13808 3.75523 6.38088 3.85588C6.62368 3.95653 6.84425 4.10405 7.03 4.29L7.09 4.35C7.32568 4.58054 7.62502 4.7352 7.94941 4.794C8.27381 4.8528 8.60838 4.8131 8.91 4.68H9C9.29577 4.55324 9.54802 4.34276 9.72569 4.07447C9.90337 3.80618 9.99872 3.49179 10 3.17V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.47324 15 4.6C15.3016 4.73312 15.6362 4.77281 15.9606 4.71401C16.285 4.65521 16.5843 4.50054 16.82 4.27L16.88 4.21C17.0657 4.02405 17.2863 3.87653 17.5291 3.77588C17.7719 3.67523 18.0322 3.62343 18.295 3.62343C18.5578 3.62343 18.8181 3.67523 19.0609 3.77588C19.3037 3.87653 19.5243 4.02405 19.71 4.21C19.896 4.39575 20.0435 4.61632 20.1441 4.85912C20.2448 5.10192 20.2966 5.36217 20.2966 5.625C20.2966 5.88783 20.2448 6.14808 20.1441 6.39088C20.0435 6.63368 19.896 6.85425 19.71 7.04L19.65 7.1C19.4195 7.33568 19.2648 7.63502 19.206 7.95941C19.1472 8.28381 19.1869 8.61838 19.32 8.92V9C19.4468 9.29577 19.6572 9.54802 19.9255 9.72569C20.1938 9.90337 20.5082 9.99872 20.83 10H21C21.5304 10 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.5882 14.0013 20.2738 14.0966 20.0055 14.2743C19.7372 14.452 19.5268 14.7042 19.4 15Z" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 音頻播放進度條 -->
          <div v-if="isPlaying || audioUrl" class="audio-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: audioProgress + '%' }"></div>
            </div>
            <div class="audio-info">
              <span class="audio-status">{{ isPlaying ? '播放中' : '已暫停' }}</span>
              <span class="audio-duration" v-if="audioDuration">{{ Math.round(audioDuration) }}s</span>
            </div>
          </div>
        </div>

        <!-- 新聞卡片 -->
        <div class="news-card" v-for="(news, index) in newsList" :key="index" @click="handleNewsCardClick(news)">
          <div class="card-header">
            <div class="header-left">
              <span class="news-number">{{ String(index + 1).padStart(2, '0') }}</span>
              <h3 class="news-title">{{ news.title }}</h3>
            </div>
          </div>
          <div class="news-image">
            <img 
              v-if="news.coverUrl && news.coverUrl !== 'null' && news.coverUrl !== ''" 
              :src="news.coverUrl" 
              :alt="news.title"
              class="news-cover-image"
              @error="handleImageError"
            />
            <div v-else class="image-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="#ccc"/>
              </svg>
              <span class="placeholder-text">暂无图片</span>
            </div>
            <div class="play-overlay" v-if="news.video">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M8 5V19L19 12L8 5Z" fill="white"/>
              </svg>
            </div>
          </div>
          <div class="news-content">
            <p class="news-summary">{{ news.summary }}</p>
            <div class="news-question" v-if="news.question">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M21 21L16.65 16.65M11 6C13.7614 6 16 8.23858 16 11C16 13.7614 13.7614 16 11 16C8.23858 16 6 13.7614 6 11C6 8.23858 8.23858 6 11 6Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>{{ news.question }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 播報模式選擇彈窗 -->
    <div class="modal-overlay" v-if="showModeSelector" @click="showModeSelector = false">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">选择播报模式</h3>
        <div class="mode-options">
          <div 
            class="mode-option" 
            :class="{ active: selectedMode === 'dual' }"
            @click="selectMode('dual')"
          >
            <span class="mode-text">双人播客</span>
            <svg v-if="selectedMode === 'dual'" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div 
            class="mode-option" 
            :class="{ active: selectedMode === 'female' }"
            @click="selectMode('female')"
          >
            <span class="mode-text">甜美女声</span>
            <svg v-if="selectedMode === 'female'" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div 
            class="mode-option" 
            :class="{ active: selectedMode === 'male' }"
            @click="selectMode('male')"
          >
            <span class="mode-text">清爽男声</span>
            <svg v-if="selectedMode === 'male'" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AiNewsPodcastView',
  data() {
    return {
      isPlaying: false,
      isLoading: false,
      showModeSelector: false,
      selectedMode: 'dual', // 默認雙人播客
      newsList: [],
      backendUrl: 'http://localhost:8080', // 後端服務地址
      currentAudio: null,
      audioUrl: null,
      audioDuration: 0,
      audioProgress: 0
    }
  },
  computed: {
    currentReportTitle() {
      const now = new Date()
      const hour = now.getHours()
      let timeType = '早报'
      
      if (hour >= 11 && hour < 18) {
        timeType = '午报'
      } else if (hour >= 18) {
        timeType = '晚报'
      }
      
      const month = now.getMonth() + 1
      const day = now.getDate()
      
      return `${timeType} | ${month}.${day}`
    }
  },
  methods: {
    async fetchNews() {
      try {
        const response = await fetch(`${this.backendUrl}/api/news`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result = await response.json()
        if (result.success) {
          this.newsList = result.data
          console.log('成功獲取新聞:', this.newsList)
        } else {
          console.error('獲取新聞失敗:', result.error)
        }
      } catch (error) {
        console.error('獲取新聞時發生錯誤:', error)
      }
    },

    // 生成播客
    async generatePodcast() {
      if (this.isLoading) {
        this.isLoading = false
        return
      }
      
      this.isLoading = true
      this.isPlaying = false
      this.audioProgress = 0
      
      try {
        // 建立WebSocket連接
        const wsUrl = `ws://localhost:8080/ws`
        const ws = new WebSocket(wsUrl)
        
        ws.onopen = () => {
          console.log('WebSocket連接已建立')
          ws.send(JSON.stringify({
            voice_mode: this.selectedMode
          }))
        }
        
        ws.onmessage = async (event) => {
          const data = JSON.parse(event.data)
          console.log('收到WebSocket消息:', data)
          
          if (data.type === 'start') {
            console.log('開始生成音頻:', data.message)
            // 立即開始嘗試播放音頻文件
            this.startStreamingAudio()
          } else if (data.type === 'success') {
            console.log('音頻生成成功:', data.data)
            
            // 播放音頻
            const audioUrl = `${this.backendUrl}${data.data.audio_url}`
            console.log('音頻URL:', audioUrl)
            
            // 停止當前播放的音頻
            if (this.currentAudio) {
              this.currentAudio.pause()
              this.currentAudio = null
            }
            
            // 創建新的音頻元素
            const audio = new Audio(audioUrl)
            this.currentAudio = audio
            this.audioUrl = audioUrl
            
            // 音頻事件處理
            audio.onloadstart = () => {
              console.log('開始加載音頻...')
            }
            
            audio.oncanplay = () => {
              console.log('音頻可以播放')
              this.isLoading = false
              this.isPlaying = true
              this.audioDuration = audio.duration || data.data.duration
              audio.play()
            }
            
            audio.onended = () => {
              console.log('音頻播放結束')
              this.isPlaying = false
              this.audioProgress = 0
            }
            
            audio.onerror = (error) => {
              console.error('音頻播放錯誤:', error)
              this.isLoading = false
              alert('音頻播放失敗，請檢查音頻文件')
            }
            
            // 更新播放進度
            audio.ontimeupdate = () => {
              if (audio.duration) {
                this.audioProgress = (audio.currentTime / audio.duration) * 100
              }
            }
            
            // 設置音頻加載超時
            setTimeout(() => {
              if (this.isLoading) {
                console.log('音頻加載超時，嘗試直接播放')
                this.isLoading = false
                this.isPlaying = true
                audio.play()
              }
            }, 5000)
            
            // 關閉WebSocket連接
            ws.close()
            
          } else if (data.type === 'error') {
            console.error('音頻生成失敗:', data.message)
            this.isLoading = false
            alert(`音頻生成失敗: ${data.message}`)
            ws.close()
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket錯誤:', error)
          this.isLoading = false
          alert('WebSocket連接失敗')
        }
        
        ws.onclose = () => {
          console.log('WebSocket連接已關閉')
        }
        
      } catch (error) {
        console.error('生成播客失敗:', error)
        this.isLoading = false
        alert('生成播客失敗')
      }
    },
    
    // 流式音頻播放
    startStreamingAudio() {
      console.log('開始流式音頻播放')
      
      // 停止當前播放的音頻
      if (this.currentAudio) {
        this.currentAudio.pause()
        this.currentAudio = null
      }
      
      // 創建音頻元素
      const audio = new Audio()
      this.currentAudio = audio
      
      // 設置音頻事件
      audio.onloadstart = () => {
        console.log('開始加載流式音頻...')
      }
      
      audio.oncanplay = () => {
        console.log('流式音頻可以播放')
        this.isLoading = false
        this.isPlaying = true
        audio.play()
      }
      
      audio.onended = () => {
        console.log('音頻播放結束')
        this.isPlaying = false
        this.audioProgress = 0
      }
      
      audio.onerror = (error) => {
        console.error('流式音頻播放錯誤:', error)
        // 不顯示錯誤，因為文件可能還在生成中
      }
      
      // 更新播放進度
      audio.ontimeupdate = () => {
        if (audio.duration) {
          this.audioProgress = (audio.currentTime / audio.duration) * 100
        }
      }
      
      // 開始輪詢音頻文件
      this.pollAudioFile(audio)
    },
    
    // 輪詢音頻文件
    pollAudioFile(audio) {
      const audioUrl = `${this.backendUrl}/audio/stream_${Date.now()}.mp3`
      console.log('輪詢音頻文件:', audioUrl)
      
      let pollCount = 0
      const maxPolls = 60 // 最多輪詢60次（30秒）
      
      const poll = () => {
        if (pollCount >= maxPolls) {
          console.log('音頻文件輪詢超時')
          return
        }
        
        pollCount++
        
        // 嘗試加載音頻文件
        audio.src = audioUrl
        
        // 檢查音頻是否可以播放
        audio.oncanplay = () => {
          console.log('音頻文件可以播放')
          this.isLoading = false
          this.isPlaying = true
          audio.play()
        }
        
        audio.onerror = () => {
          // 文件不存在或還未生成完成，繼續輪詢
          console.log(`音頻文件還未準備好，繼續輪詢... (${pollCount}/${maxPolls})`)
          setTimeout(poll, 500) // 每500ms輪詢一次
        }
      }
      
      poll()
    },

    togglePlayback() {
      console.log('按鈕被點擊', { isLoading: this.isLoading, isPlaying: this.isPlaying })
      
      if (this.isLoading) {
        // 如果正在加載，取消加載
        this.isLoading = false
        return
      }
      
      if (!this.isPlaying) {
        // 開始生成播客
        console.log('開始生成播客')
        this.generatePodcast()
      } else {
        // 暫停播放
        console.log('暫停播放')
        if (this.currentAudio) {
          this.currentAudio.pause()
        }
        this.isPlaying = false
      }
    },
    
    getButtonText() {
      if (this.isLoading) return '生成中...'
      if (this.isPlaying) return '播放中'
      return '听一听'
    },
    
    selectMode(mode) {
      this.selectedMode = mode
      this.showModeSelector = false
      // 這裡可以保存用戶選擇到本地存儲
      localStorage.setItem('ai-news-mode', mode)
    },

    handleImageError(event) {
      console.warn('圖片加載失敗，使用預設圖片:', event.target.src);
      // 隱藏失敗的圖片，顯示占位符
      event.target.style.display = 'none';
      const placeholder = event.target.parentElement.querySelector('.image-placeholder');
      if (placeholder) {
        placeholder.style.display = 'flex';
      }
    },

    handleNewsCardClick(news) {
      if (news.contentUrl && news.contentUrl.trim() !== '') {
        // 在新標籤頁中打開外部URL
        window.open(news.contentUrl, '_blank')
      } else {
        console.warn('新闻没有contentUrl，无法跳转:', news)
      }
    }
  },
  
  mounted() {
    // 從本地存儲恢復用戶選擇的模式
    const savedMode = localStorage.getItem('ai-news-mode')
    if (savedMode) {
      this.selectedMode = savedMode
    }
    
    // 頁面加載時獲取新聞
    this.fetchNews()
  }
}
</script>

<style scoped>
.ai-news-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 頂部導航 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 0 16px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn, .nav-btn {
  background: none;
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  color: #333;
  transition: all 0.2s;
}

.back-btn:hover, .nav-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

/* 主要內容 */
.main-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  overflow-x: hidden;
}

.news-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 20px;
  position: relative;
}

/* 添加時間線背景 */
.news-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 1px;
  z-index: 0;
}

/* 新聞卡片通用樣式 */
.news-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

/* 非AI早報卡片添加點擊樣式 */
.news-card:not(.ai-daily-card) {
  cursor: pointer;
}

.news-card:not(.ai-daily-card):hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
}

.news-card:not(.ai-daily-card):active {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
}

/* 添加連接線效果 */
.news-card:not(.ai-daily-card)::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 6px;
  background: linear-gradient(to bottom, rgba(102, 126, 234, 0.3), transparent);
  border-radius: 1px;
}

.news-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* AI 早報卡片特殊樣式 */
.ai-daily-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
  margin-bottom: 4px;
}

.ai-daily-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  position: relative;
}

.ai-icon::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  padding: 2px;
  background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
}

.ai-text {
  color: #fff;
  font-weight: 800;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.daily-text {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.listen-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  position: relative;
  z-index: 200;
  pointer-events: auto;
}

.listen-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.listen-btn.playing {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  box-shadow: 0 4px 16px rgba(76, 175, 80, 0.4);
}

.listen-btn.loading {
  background: linear-gradient(135deg, #FF9800, #F57C00);
  box-shadow: 0 4px 16px rgba(255, 152, 0, 0.4);
}

.btn-text {
  font-size: 14px;
  font-weight: 600;
}

.settings-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.2);
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  color: #667eea;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.settings-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

/* 新聞編號和標題 */
.news-number {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.news-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0;
  flex: 1;
  line-height: 1.4;
}

/* 圖片區域 */
.news-image {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.5);
}

.news-cover-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-cover-image:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 16px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
  color: #999;
  font-size: 14px;
  gap: 8px;
}

.placeholder-text {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
}

.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

/* 新聞內容 */
.news-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-summary {
  font-size: 15px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.news-question {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.2);
  backdrop-filter: blur(10px);
}

.news-question:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  transform: translateY(-1px);
}

/* 彈窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  width: 90%;
  max-width: 360px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0 0 24px 0;
  text-align: center;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mode-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.mode-option:hover {
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.mode-option.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-color: #667eea;
  color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.mode-text {
  font-size: 16px;
  font-weight: 600;
}

/* 音頻播放進度條 */
.audio-progress {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.audio-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.audio-status {
  font-weight: 600;
}

.audio-duration {
  opacity: 0.7;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .main-content {
    padding: 12px;
  }
  
  .news-card {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .daily-text {
    font-size: 18px;
  }
}
</style> 