<template>
  <div class="chat-container podcast-bg">
    <div class="podcast-content-container">
      <div class="main-header">
        <h1 class="main-title">AI 播客生成器</h1>
        <div class="main-desc">在幾秒鐘內將您的內容轉為可分享的播客節目</div>
      </div>
      <div class="input-card">
        <div class="input-row">
          <textarea v-model="podcastText" class="topic-input" placeholder="貼上URL到這裡" />
        </div>
        <div class="option-row">
          <select v-model="lang" class="option-select">
            <option value="zh-CN">簡體中文</option>
            <option value="zh-TW">繁體中文</option>
            <option value="en">English</option>
          </select>
          <div class="host-select">
            <span>主持人：</span>
            <span class="host-avatar">🧑‍💼 李靜</span>
            <span class="host-avatar">🧑‍💼 王濤</span>
            <button class="type-btn" :class="{active: selectedType==='single'}" @click="selectType('single')">單人</button>
            <button class="type-btn" :class="{active: selectedType==='double'}" @click="selectType('double')">雙人</button>
          </div>
        </div>
        <button class="main-generate-btn" :disabled="!podcastText.trim() || isGenerating" @click="handleGenerate">
          <span v-if="isGenerating">生成中...</span>
          <span v-else>立即生成</span>
        </button>
      </div>
      <div class="example-section">
        <div class="example-title">示例提示詞</div>
        <div class="example-list">
          <span class="example-item">斯坦福 AI 指數報告 2024</span>
          <span class="example-item">馬斯克的願景：構建明天</span>
          <span class="example-item">大語言模型中的知識蒸餾</span>
          <span class="example-item">5 個日常生產力小貼士</span>
        </div>
      </div>
      <div class="podcast-output" v-if="isGenerating">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <div class="loading-text">播客生成中，請稍候...</div>
        </div>
      </div>
      <div class="error-message" v-if="error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { generatePodcast } from '@/api/podcast'
import { ElMessage } from 'element-plus'

export default {
  name: 'PodcastView',
  data() {
    return {
      selectedType: 'single', // 默認單人
      podcastText: '', // 用戶輸入的播客主題
      difyGeneratedContent: '', // Dify 生成的文本內容
      lang: 'zh-CN',
      isGenerating: false,
      error: null,
      loadingDify: false, // 新增：Dify 生成中狀態
      loadingAudio: false, // 新增：音頻生成中狀態
      userId: 'podcast-user', // Dify 用戶 ID
      controller: null // 用於取消 Dify 請求
    }
  },
  methods: {
    selectType(type) {
      this.selectedType = type
    },
    async handleGenerate() {
      if (!this.podcastText.trim()) {
        this.error = '請輸入播客主題'
        return
      }

      this.isGenerating = true
      this.loadingDify = true
      this.error = null
      this.difyGeneratedContent = ''

      try {
        // 步驟 1: 呼叫 Dify API 生成播客文本
        const apiKey = this.selectedType === 'single' ? 'app-kGi6NkKSrDzQqJyizV1hKjxI' : 'app-b87p8SKFRgsvKjCVHfXGqokW'
        const url = 'http://10.18.4.170/v1/chat-messages'
        const headers = {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
        const body = {
          query: this.podcastText,
          inputs: {},
          response_mode: 'streaming',
          user: this.userId
        }

        this.controller = new AbortController()
        const response = await fetch(url, {
          method: 'POST',
          headers,
          body: JSON.stringify(body),
          signal: this.controller.signal
        })

        if (!response.body) throw new Error('無法獲取 Dify 流式數據')

        const reader = response.body.getReader()
        let buffer = ''
        let fullAnswer = ''
        let finishedDify = false

        while (!finishedDify) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += new TextDecoder().decode(value)
          const parts = buffer.split('\n\n')
          buffer = parts.pop()

          for (const part of parts) {
            if (!part.trim().startsWith('data:')) continue
            const jsonStr = part.replace(/^data:\s*/, '')
            if (!jsonStr) continue
            let data
            try {
              data = JSON.parse(jsonStr)
            } catch (e) { continue }

            if (data.event === 'message') {
              if (data.answer) {
                fullAnswer += data.answer
              }
            }
            if (data.event === 'message_end') {
              finishedDify = true
            }
          }
        }
        this.difyGeneratedContent = fullAnswer

        // 步驟 2: Dify 文本生成完成，開始生成音頻
        this.loadingDify = false
        this.loadingAudio = true

        const result = await generatePodcast(this.difyGeneratedContent, this.selectedType)
        if (result.success) {
          ElMessage.success('生成成功')
          this.$router.push({
            path: '/podcast-detail',
            query: {
              audioFile: result.audioUrl,
              title: this.podcastText,
              content: encodeURIComponent(this.difyGeneratedContent),
              type: this.selectedType
            }
          })
        } else {
          this.error = result.error || '生成播客音頻失敗'
          ElMessage.error(this.error)
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('Dify 請求被取消')
          this.error = '生成已被取消'
        } else {
          this.error = error.message || '生成播客時出錯'
        }
        ElMessage.error(this.error)
      } finally {
        this.isGenerating = false
        this.loadingDify = false
        this.loadingAudio = false
      }
    }
  }
}
</script>

<style scoped>
.chat-container.podcast-bg {
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
.podcast-content-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 0 32px 0;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.main-header {
  margin-bottom: 8px;
}
.main-title {
  font-size: 32px;
  font-weight: bold;
  color: #222;
  text-align: center;
}
.main-desc {
  color: #888;
  font-size: 17px;
  margin-top: 10px;
  text-align: center;
}
.input-card {
  background: #fafbfc;
  border-radius: 12px;
  padding: 28px 24px 18px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.input-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.topic-input {
  width: 100%;
  min-height: 70px;
  padding: 14px;
  border: 1px solid #eee;
  border-radius: 8px;
  font-size: 16px;
  background: #f5f5f5;
  resize: none;
}
.option-row {
  display: flex;
  align-items: center;
  gap: 18px;
  font-size: 16px;
  flex-wrap: wrap;
}
.option-select {
  padding: 8px 18px;
  border-radius: 8px;
  border: 1px solid #eee;
  background: #fff;
  font-size: 16px;
}
.host-select {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.host-avatar {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 4px 14px;
  font-size: 16px;
  margin-right: 6px;
}
.type-btn {
  padding: 6px 18px;
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fff;
  color: #888;
  font-size: 15px;
  margin-left: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.type-btn.active, .type-btn:hover {
  background: #ff6700;
  color: #fff;
  border-color: #ff6700;
}
.main-generate-btn {
  background: linear-gradient(90deg, #ff6700 0%, #ffb300 100%);
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 16px 0;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 12px;
  transition: background 0.2s;
}
.main-generate-btn:disabled {
  background: #eee;
  color: #bbb;
  cursor: not-allowed;
}
.example-section {
  margin-bottom: 12px;
}
.example-title {
  color: #888;
  font-size: 16px;
  margin-bottom: 8px;
}
.example-list {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}
.example-item {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 16px;
  color: #444;
  cursor: pointer;
  transition: background 0.2s;
}
.example-item:hover {
  background: #ffecdb;
}
.podcast-output {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 24px;
  margin-top: 12px;
}
.podcast-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message {
  padding: 12px 18px;
  border-radius: 8px;
  background: #f5f5f5;
  font-size: 16px;
  color: #333;
}
.message.system {
  color: #ff6700;
  font-style: italic;
  background: transparent;
  box-shadow: none;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff6700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
.loading-text {
  color: #666;
  font-size: 16px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@media (max-width: 900px) {
  .podcast-content-container {
    max-width: 100vw;
    padding: 16px 2px 12px 2px;
  }
  .input-card {
    padding: 10px 2px 8px 2px;
  }
}
.error-message {
  color: #ff6700;
  font-size: 16px;
  margin-top: 12px;
  text-align: center;
}
</style> 