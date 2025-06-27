<template>
  <div class="podcast-detail-bg">
    <div class="podcast-detail-container">
      <div class="podcast-header-row">
        <img 
          class="podcast-cover" 
          :src="coverImage" 
          alt="cover" 
          @error="handleImageError"
          @load="handleImageLoad"
        />
        <div class="podcast-meta">
          <div class="podcast-title">{{ title }}</div>
          <div class="podcast-time">{{ formatDuration(duration) }} ｜ {{ currentDate }}</div>
          <div class="podcast-desc">{{ summary }}</div>
          <div class="podcast-actions">
            <div class="action-buttons">
              <button class="action-btn" @click="sharePodcast">
                <img src="@/assets/share.svg" alt="分享" class="btn-icon" />
                分享
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="podcast-tabs">
        <button class="tab-btn active">播客腳本</button>
      </div>

      <div class="podcast-script-block">
        <div v-for="(block, idx) in parsedBlocks" :key="idx" class="script-block">
          <div class="role-row">
            <span class="role-avatar">{{ getAvatar(block.role) }}</span>
            <span class="role-name">{{ block.role }}</span>
          </div>
          <div class="role-content">{{ block.content }}</div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="audio-player-bottom-bar">
    <div class="control-left">
      <img src="@/assets/play-icon.svg" alt="播放" class="play-icon" />
    </div>
    <div class="audio-progress">
      <span class="current-time">00:00</span>
      <audio controls :src="audioFile" class="audio-player" @loadedmetadata="handleLoadedMetadata"></audio>
      <span class="total-time">{{ formatDuration(duration) }}</span>
    </div>
    <div class="control-right">
      <img src="@/assets/download-icon.svg" alt="下載" class="download-icon" @click="downloadAudio" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'PodcastDetailView',
  data() {
    return {
      title: '',
      audioFilename: '', // 從路由獲取的音頻文件名
      content: '', // 從路由獲取的 Dify 生成的文本內容
      summary: '', // 播客摘要
      parsedBlocks: [], // 解析後的腳本分段
      duration: 0, // 音頻時長
      coverImage: '', // 默認封面
      defaultCover: '' // 備用封面
    }
  },
  computed: {
    currentDate() {
      return new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    audioFile() {
      // 從 Flask 服務器獲取音頻文件
      return this.audioFilename ? `http://localhost:5001/audio/${this.audioFilename}` : ''
    }
  },
  async created() {
    // 從路由參數獲取數據
    const { title, audioFile, content } = this.$route.query
    this.title = decodeURIComponent(title || '生成的播客')
    this.audioFilename = audioFile || ''
    this.content = decodeURIComponent(content || '')

    // 嘗試自動提取摘要（前200字）
    this.summary = this.content.slice(0, 200) + (this.content.length > 200 ? '...' : '')
    // 解析角色分段
    this.parsedBlocks = this.parseScript(this.content)

    // 動態導入圖片
    try {
      const image = await import('@/assets/podcast.jpeg')
      this.coverImage = image.default
      this.defaultCover = image.default
    } catch (error) {
      console.error('圖片加載失敗:', error)
    }
  },
  methods: {
    handleLoadedMetadata(event) {
      this.duration = event.target.duration
    },
    formatDuration(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      const formattedSeconds = remainingSeconds < 10 ? `0${remainingSeconds}` : remainingSeconds
      return `${minutes}:${formattedSeconds}`
    },
    parseScript(text) {
      if (!text) return []
      // 替換 \n 為實際換行符，並處理可能的 \r
      const processedText = text.replace(/\\n/g, '\n').replace(/\\r/g, '')

      // 如果文本中沒有冒號，假設整個文本都是主持人的內容
      if (!processedText.includes(':')) {
        return [{
          role: '主持人',
          content: processedText.trim()
        }]
      }

      const lines = processedText.split(/\n|\r/).filter(l => l.trim())
      const blocks = []
      let lastRole = ''

      lines.forEach(line => {
        // 匹配 "角色名: 內容" 或 "角色名：內容"
        const match = line.match(/^([\u4e00-\u9fa5A-Za-z0-9_-]+)[:：]\s*(.*)$/)
        if (match) {
          blocks.push({ role: match[1], content: match[2].trim() })
          lastRole = match[1]
        } else if (lastRole && blocks.length > 0) {
          // 如果沒有匹配到新角色，將此行內容追加到上一個角色的內容中
          blocks[blocks.length - 1].content += '\n' + line.trim()
        } else {
          // 如果沒有匹配到角色且沒有上一個角色，創建一個默認角色
          blocks.push({ role: '主持人', content: line.trim() })
        }
      })
      return blocks
    },
    getAvatar(role) {
      // 根據角色名返回不同emoji
      if (/emily/i.test(role)) return '👩🏻'
      if (/michael/i.test(role)) return '👨🏻'
      if (/王涛/.test(role)) return '🧑‍💼'
      if (/李靜/.test(role)) return '🧑‍💼'
      return '🎙️'
    },
    handleImageError(e) {
      console.error('圖片加載失敗:', e.target.src)
      this.coverImage = this.defaultCover
    },
    handleImageLoad(e) {
      console.log('圖片加載成功:', e.target.src)
    },
    sharePodcast() {
      // 實現分享功能
      console.log('分享播客')
    },
    downloadAudio() {
      const link = document.createElement('a')
      link.href = this.audioFile
      link.download = this.audioFilename || 'podcast_audio.mp3'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
}
</script>

<style scoped>
.podcast-detail-bg {
  position: fixed;
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
  width: 100vw;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.podcast-detail-container {
  width: 100%;
  max-width: 900px; /* 保持與 PodcastView 一致的寬度 */
  margin: 0 auto; /* 居中 */
  padding: 40px 0 32px 0;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.podcast-header-row {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}
.podcast-cover {
  width: 220px;
  height: 220px;
  object-fit: cover;
  border-radius: 16px;
  background: #eee;
}
.podcast-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.podcast-title {
  font-size: 26px;
  font-weight: bold;
  color: #222;
}
.podcast-time {
  color: #888;
  font-size: 15px;
  margin-bottom: 6px;
}
.podcast-desc {
  color: #444;
  font-size: 16px;
  margin-bottom: 8px;
}
.podcast-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.action-btn {
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 15px;
  color: #444;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn:hover {
  background: #ffecdb;
}

.btn-icon {
  width: 18px;
  height: 18px;
}
.podcast-tabs {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}
.tab-btn {
  background: #fafbfc;
  border: none;
  border-radius: 8px 8px 0 0;
  padding: 8px 18px;
  font-size: 16px;
  color: #444;
  font-weight: bold;
  cursor: pointer;
  border-bottom: 2px solid #ff6700;
}
.tab-btn.active {
  background: #fff;
  color: #ff6700;
}
.podcast-script-block {
  background: #fafbfc;
  border-radius: 12px;
  padding: 24px 18px;
  margin-top: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  max-height: calc(100vh - 400px); /* 調整高度以適應內容 */
  overflow-y: auto;
  margin-bottom: 100px; /* 為底部播放器留出空間 */
}
.script-block {
  margin-bottom: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.role-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}
.role-avatar {
  font-size: 24px;
  background: #f5f5f5;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.role-name {
  font-weight: bold;
  color: #222;
  font-size: 16px;
}
.role-content {
  color: #333;
  font-size: 16px;
  line-height: 1.7;
  white-space: pre-line;
  padding: 0 8px;
}
.audio-player-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: center; /* 居中對齊 */
  gap: 20px; /* 元素間距 */
  z-index: 1000;
  box-sizing: border-box; /* 確保 padding 不增加寬度 */
}

.control-left,
.control-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.play-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
}

.audio-progress {
  flex-grow: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 600px; /* 限制播放器進度條的最大寬度 */
}

.audio-player {
  flex-grow: 1;
  height: 30px;
  width: 100%; /* 確保在 audio-progress 中佔滿可用空間 */
}

.current-time,
.total-time {
  font-size: 14px;
  color: #555;
  white-space: nowrap; /* 防止時間換行 */
}

.download-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
}

@media (max-width: 900px) {
  .audio-player-bottom-bar {
    padding: 10px 15px;
    gap: 10px;
  }
  .play-icon {
    width: 28px;
    height: 28px;
  }
  .download-icon {
    width: 20px;
    height: 20px;
  }
  .audio-player {
    height: 25px;
  }
  .current-time,
  .total-time {
    font-size: 12px;
  }
  .audio-progress {
    max-width: none; /* 在小屏幕上不限制最大寬度 */
  }
}

.gradient-text {
  background: linear-gradient(to right, #ff7e5f, #feb47b); /* 漸變顏色 */
  -webkit-background-clip: text; /* 讓背景裁剪到文字形狀 */
  background-clip: text;
  color: transparent; /* 讓文字本身透明，顯示背景 */
}
</style> 