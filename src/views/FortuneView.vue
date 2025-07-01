<template>
  <div class="fortune-bg">
    <div class="fortune-container">
      <header>
        <h1>命理分析系统</h1>
        <p>探索命运的奥秘，指引人生的方向</p>
      </header>

      <main>
        <section class="user-input-section" id="userInputSection" v-show="!showResults">
          <h2>个人信息</h2>
          <form id="fortuneForm" @submit.prevent="submitForm">
            <div class="form-group">
              <label for="name">姓名</label>
              <input type="text" id="name" name="name" v-model="formData.name">
            </div>
            <div class="form-group">
              <label for="gender">性别</label>
              <select id="gender" name="gender" v-model="formData.gender" required>
                <option value="">请选择</option>
                <option value="男">男</option>
                <option value="女">女</option>
                <option value="武直10">武直10</option>
                <option value="特朗普">特朗普</option>
              </select>
            </div>
            <div class="form-group">
              <label for="birthday">出生年月</label>
              <input type="date" id="birthday" name="birthday" v-model="formData.birthday" required>
            </div>
            <div class="form-group">
              <label for="birth_place">出生地点</label>
              <input type="text" id="birth_place" name="birth_place" v-model="formData.birth_place">
            </div>
            <button type="submit" class="btn-submit">开始分析</button>
          </form>
        </section>

        <section class="result-section" id="resultSection" v-show="showResults">
          <div class="analysis-cards" id="analysisCards">
            <div class="loading-spinner" id="loadingSpinner" v-show="loading">
              <img src="@/assets/wait.svg" class="wait-svg" alt="等待中" />
              <p class="loading-text">正在分析命盘，请稍候...</p>
            </div>

            <div class="cards-grid" id="cardsGrid" v-show="!loading">
              <div class="analysis-card" id="zodiacCard" data-type="zodiac" @click="showAnalysisDetail('zodiac')" :class="{ expanded: expandedCard === 'zodiac' }">
                <div class="card-header">
                  <i class="fas fa-star"></i>
                  <h3>星座运势</h3>
                </div>
                <div class="card-preview" v-html="cardPreviews.zodiac"></div>
              </div>

              <div class="analysis-card" id="baziCard" data-type="bazi" @click="showAnalysisDetail('bazi')" :class="{ expanded: expandedCard === 'bazi' }">
                <div class="card-header">
                  <i class="fas fa-yin-yang"></i>
                  <h3>八字命理</h3>
                </div>
                <div class="card-preview" v-html="cardPreviews.bazi"></div>
              </div>

              <div class="analysis-card" id="astroCard" data-type="astro" @click="showAnalysisDetail('astro')" :class="{ expanded: expandedCard === 'astro' }">
                <div class="card-header">
                  <i class="fas fa-sun"></i>
                  <h3>星盘解析</h3>
                </div>
                <div class="card-preview" v-html="cardPreviews.astro"></div>
              </div>

              <div class="analysis-card" id="tarotCard" data-type="tarot" @click="showAnalysisDetail('tarot')" :class="{ expanded: expandedCard === 'tarot' }">
                <div class="card-header">
                  <h3>塔罗占卜</h3>
                </div>
                <div class="card-preview" v-html="cardPreviews.tarot"></div>
              </div>
            </div>
          </div>

          <section class="wechat-chat-section" id="chatSection" v-show="showChat">
            <div class="wechat-chat-header">
              <h2>命理大师群</h2>
              <div class="group-info">
                <span class="group-members">5位成员</span>
              </div>
            </div>
            <div class="wechat-chat-container">
              <div class="wechat-chat-messages" id="chatMessages" ref="chatMessagesRef">
                <div v-for="(message, index) in chatMessages" :key="index" :class="['chat-message', message.type]">
                  <div class="message-avatar">
                    <span v-if="message.type === 'system'">💻</span>
                    <span v-else-if="message.type === 'zodiac'">⭐</span>
                    <span v-else-if="message.type === 'bazi'">☯️</span>
                    <span v-else-if="message.type === 'astro'">🌟</span>
                    <span v-else-if="message.type === 'tarot'">🎴</span>
                    <span v-else-if="message.type === 'user'">👤</span>
                  </div>
                  <div class="message-content">
                    <div class="message-header">
                      <span class="message-author">{{ message.author }}</span>
                      <span class="message-time">{{ message.time }}</span>
                    </div>
                    <div class="message-text" v-html="message.content"></div>
                  </div>
                </div>
              </div>
              <div class="wechat-chat-input-wrapper">
                <div class="wechat-chat-input">
                  <input type="text" id="chatInput" v-model="chatInput" @keyup.enter="sendMessage" placeholder="@大师名称 或直接提问...">
                  <div class="wechat-input-actions">
                    <button class="at-button" id="atButton" @click="showAtMenu"><i class="fas fa-at"></i></button>
                    <button id="sendMessage" @click="sendMessage"><i class="fas fa-paper-plane"></i></button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>

        <section class="analysis-detail" id="analysisDetail" v-show="showDetail">
          <div class="detail-header">
            <button class="back-to-cards" @click="backToCards"><i class="fas fa-arrow-left"></i></button>
            <h2 id="detailTitle">{{ detailTitle }}</h2>
          </div>
          <div class="detail-content" id="detailContent" v-html="detailContent"></div>
        </section>
      </main>

      <footer>
        <p>&copy; 2024 命理分析系统 | 仅供娱乐参考</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { fortune, mastersChat } from '@/api/fortune'
import { extractMarkedContent } from '@/utils/fortuneUtils'
import '@/assets/css/fortune/style.css'
import '@/assets/css/fortune/fortune-chat.css'
import '@/assets/css/fortune/tarot-animations.css'
import '@/assets/css/fortune/mystical-theme.css'
import '@/assets/css/fortune/fortune-animations.css'

// 響應式數據
const showResults = ref(false)
const showChat = ref(false)
const showDetail = ref(false)
const loading = ref(false)
const expandedCard = ref('')
const detailTitle = ref('')
const detailContent = ref('')
const chatInput = ref('')
const chatMessages = ref([])
const chatMessagesRef = ref(null)
// 是否已顯示過大師群歡迎信息
const masterWelcomeShown = ref(false)

// 表單數據
const formData = reactive({
  name: '',
  gender: '',
  birthday: '',
  birth_place: ''
})

// 卡片預覽內容
const cardPreviews = reactive({
  zodiac: '',
  bazi: '',
  astro: '',
  tarot: ''
})

// 分析結果
const fortuneResults = reactive({
  xingzuo: { zongjie: '', fenxi: '' },
  bazi: { zongjie: '', fenxi: '' },
  xingpan: { zongjie: '', fenxi: '' },
  tarot: ''
})

// 會話ID
let conversationId = ''

// 延遲顯示大師群計時器
let chatTimer = null

// 2. submitForm 改为调用本地 /api/fortune
const submitForm = async () => {
  loading.value = true
  showResults.value = true
  try {
    const userData = {
      name: formData.name,
      gender: formData.gender,
      birthday: formData.birthday,
      birth_place: formData.birth_place,
      user_info: {
        id: (() => {
          let userId = localStorage.getItem('user_id')
          if (!userId) {
            userId = `user_${Date.now()}`
            localStorage.setItem('user_id', userId)
          }
          return userId
        })()
      }
    }
    
    // 调用本地/api/fortune
    const response = await fortune(userData);

    if (!response.ok) {
        throw new Error(`API请求失败: ${response.status}`);
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let analysisText = ''

    // eslint-disable-next-line no-constant-condition
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.trim() === '') continue
        if (line.startsWith('data: ')) {
          const jsonStr = line.substring(6).trim()
          try {
            const data = JSON.parse(jsonStr)
            if (data.conversation_id) {
              conversationId = data.conversation_id
              localStorage.setItem('unified_conversation_id', conversationId)
            }
            // 兼容后端返回的多种字段名
            const segment = data.data || data.answer || data.text || data.content || ''
            if (segment && data.event !== 'ping') {
              analysisText += segment
              extractMarkedContent(analysisText, fortuneResults)
              updateCardPreviewsFromResults(fortuneResults)
            }
          } catch (err) {
            console.warn('解析API响应失败:', err)
          }
        }
      }
    }
    window.fortuneResults = fortuneResults

    if (fortuneResults.xingzuo.fenxi) {
      document.querySelector('#zodiacCard').dataset.detailContent = fortuneResults.xingzuo.fenxi;
    }
    if (fortuneResults.bazi.fenxi) {
      document.querySelector('#baziCard').dataset.detailContent = fortuneResults.bazi.fenxi;
    }
    if (fortuneResults.xingpan.fenxi) {
      document.querySelector('#astroCard').dataset.detailContent = fortuneResults.xingpan.fenxi;
    }
    
    cardPreviews.tarot = getTarotReadingHTML()
  } catch (error) {
    console.error('命理分析请求失败:', error)
    alert(`分析失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 顯示分析詳情
const showAnalysisDetail = (type) => {
  console.log('[showAnalysisDetail] 点击卡片:', type)
  // 每次點擊卡片先隱藏聊天、清計時器
  if (chatTimer) {
    clearTimeout(chatTimer)
    chatTimer = null
  }
  showChat.value = false

  expandedCard.value = type
  const typeNames = {
    zodiac: '星座运势',
    bazi: '八字命理',
    astro: '星盘解析',
    tarot: '塔罗占卜'
  }
  detailTitle.value = typeNames[type]
  if (type === 'tarot') {
    detailContent.value = getTarotReadingHTML()
    initTarotDeck()
    showDetail.value = true
    // 先清除可能存在的計時器
    if (chatTimer) {
      clearTimeout(chatTimer)
      chatTimer = null
    }
    chatTimer = setTimeout(() => {
      console.log('[showAnalysisDetail] showChat.value = true, startMasterChat()')
      showChat.value = true
      startMasterChat()
    }, 1000)
  } else {
    // 非塔羅卡片保持群聊隱藏
    showChat.value = false
    const keyMap = { zodiac: 'xingzuo', bazi: 'bazi', astro: 'xingpan' }
    const key = keyMap[type]
    let content = ''
    if (fortuneResults[key]) {
      content = fortuneResults[key].fenxi || fortuneResults[key].zongjie || '暂无详细分析内容'
    }
    detailContent.value = formatDetailContent(content)
    showDetail.value = true
  }
}

// 返回卡片
const backToCards = () => {
  showDetail.value = false
  expandedCard.value = ''
  // 返回卡片时，如非塔羅卡片則隱藏聊天
  if (expandedCard.value !== 'tarot') {
    showChat.value = false
  }
}

// 發送消息
const sendMessage = async () => {
  if (!Array.isArray(chatMessages.value)) chatMessages.value = [];
  const userMessage = chatInput.value.trim()
  console.log('[sendMessage] 用户输入:', userMessage)
  if (!userMessage) return
  
  addUserMessage(userMessage)
  chatInput.value = ''
  
  try {
    const knowledgeBase = {
      user_info: {
        name: formData.name,
        gender: formData.gender,
        birthday: formData.birthday,
        birth_place: formData.birth_place
      },
      analysis_results: fortuneResults
    }
    console.log('[sendMessage] 调用 mastersChat, knowledgeBase:', knowledgeBase)
    const response = await mastersChat({
        query: userMessage,
        knowledge_base: knowledgeBase,
        conversation_id: conversationId,
        user: localStorage.getItem('user_id') || 'fortune-user',
        workflow_type: 'masters_group'
    })
    console.log('[sendMessage] mastersChat response:', response)
    if (response.ok) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.trim() === '') continue
          if (line.startsWith('data: ')) {
            const jsonStr = line.substring(6).trim()
            try {
              const data = JSON.parse(jsonStr)
              console.log('[sendMessage] 收到流数据:', data)
              if (data.conversation_id) {
                conversationId = data.conversation_id;
              }
              if (data.metadata && data.metadata.master_messages) {
                data.metadata.master_messages.forEach((masterMsg, index) => {
                  if (masterMsg.master_tag && masterMsg.content) {
                    const masterType = {
                      'xzdashi': 'zodiac',
                      'bzdashi': 'bazi',
                      'xpdashi': 'astro',
                      'tldashi': 'tarot'
                    }[masterMsg.master_tag]
                    if (masterType) {
                      console.log('[sendMessage] 渲染大师消息:', masterType, masterMsg.content)
                      setTimeout(() => {
                        addMasterMessage(masterType, masterMsg.content.trim())
                      }, Math.random() * 1000 + 300 * index)
                    }
                  }
                })
              } else if (data.answer) {
                addSystemMessage(data.answer)
              }
            } catch (err) {
              console.warn('[sendMessage] 解析API响应失败:', err)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('[sendMessage] 发送消息失败:', error)
    addSystemMessage('发送消息失败，请重试')
  }
}

// 開始大師聊天
const startMasterChat = async () => {
  if (!Array.isArray(chatMessages.value)) chatMessages.value = [];
  // 僅首次進入顯示歡迎信息
  if (!masterWelcomeShown.value) {
    addSystemMessage('欢迎来到命理大师群，四位大师已准备好为您解答问题')
    masterWelcomeShown.value = true
  }
  
  const knowledgeBase = {
    user_info: {
      name: formData.name,
      gender: formData.gender,
      birthday: formData.birthday,
      birth_place: formData.birth_place
    },
    analysis_results: fortuneResults
  }
  
  try {
    const response = await mastersChat({
        query: '请四位大师基于之前的分析结果进行一轮讨论',
        knowledge_base: knowledgeBase,
        conversation_id: conversationId,
        user: localStorage.getItem('user_id') || 'fortune-user',
        workflow_type: 'masters_group'
    })
    
    if (response.ok) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      // eslint-disable-next-line no-constant-condition
      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.trim() === '') continue
          if (line.startsWith('data: ')) {
            const jsonStr = line.substring(6).trim()
            try {
              const data = JSON.parse(jsonStr)
              if (data.metadata && data.metadata.master_messages) {
                data.metadata.master_messages.forEach((masterMsg, index) => {
                  if (masterMsg.master_tag && masterMsg.content) {
                    const masterType = {
                      'xzdashi': 'zodiac',
                      'bzdashi': 'bazi',
                      'xpdashi': 'astro',
                      'tldashi': 'tarot'
                    }[masterMsg.master_tag]
                    
                    if (masterType) {
                      setTimeout(() => {
                        addMasterMessage(masterType, masterMsg.content.trim())
                      }, Math.random() * 1000 + 300 * index)
                    }
                  }
                })
              }
            } catch (err) {
              console.warn('解析API响应失败:', err)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('启动大师聊天失败:', error)
  }
}

// 添加用戶消息
const addUserMessage = (content) => {
  if (!Array.isArray(chatMessages.value)) chatMessages.value = [];
  console.log('[addUserMessage] 添加用户消息:', content)
  chatMessages.value.push({
    type: 'user',
    author: '您',
    content: content,
    time: getCurrentTime()
  })
  scrollToBottom()
}

// 添加大師消息
const addMasterMessage = (type, content) => {
  if (!Array.isArray(chatMessages.value)) chatMessages.value = [];
  console.log('[addMasterMessage] 添加大师消息:', type, content)
  const masterNames = {
    zodiac: '星座大师',
    bazi: '命理大师',
    astro: '星盘大师',
    tarot: '塔罗大师'
  }
  chatMessages.value.push({
    type: type,
    author: masterNames[type],
    content: content,
    time: getCurrentTime()
  })
  scrollToBottom()
}

// 添加系統消息
const addSystemMessage = (content) => {
  if (!Array.isArray(chatMessages.value)) chatMessages.value = [];
  console.log('[addSystemMessage] 添加系统消息:', content)
  chatMessages.value.push({
    type: 'system',
    author: '系统',
    content: content,
    time: getCurrentTime()
  })
  scrollToBottom()
}

// 滾動到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 獲取當前時間
const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 顯示@菜單
const showAtMenu = () => {
  // 實現@菜單功能
  console.log('顯示@菜單')
}

// 更新卡片預覽
const updateCardPreviewsFromResults = (results) => {
  if (results.xingzuo.zongjie) {
    cardPreviews.zodiac = formatDetailContent(results.xingzuo.zongjie)
  }
  if (results.bazi.zongjie) {
    cardPreviews.bazi = formatDetailContent(results.bazi.zongjie)
  }
  if (results.xingpan.zongjie) {
    cardPreviews.astro = formatDetailContent(results.xingpan.zongjie)
  }
}

// 格式化詳細內容
const formatDetailContent = (content) => {
  return content
    .split('\n')
    .filter(p => p.trim())
    .map(p => `<p>${p}</p>`)
    .join('')
}

// 獲取塔羅牌閱讀HTML
const getTarotReadingHTML = () => {
  return `
    <div class="tarot-reading">
      <p>请集中注意力，想着你的问题，然后点击下面的牌开始抽牌...</p>
      <p><small>点击牌面后，解读将直接显示在牌上</small></p>
      <div class="tarot-deck"></div>
    </div>
  `
}

// 初始化塔羅牌
const initTarotDeck = () => {
  nextTick(() => {
    const deckElement = document.querySelector('.tarot-deck')
    if (!deckElement) return
    // 先清空牌堆，保證只生成一張
    deckElement.innerHTML = ''
    const card = document.createElement('div')
    card.className = 'tarot-card'
    
    const cardInner = document.createElement('div')
    cardInner.className = 'tarot-card-inner'
    
    const cardFront = document.createElement('div')
    cardFront.className = 'tarot-card-front'
    cardFront.innerHTML = `<img src="/images/mystical-tarot-logo.svg" alt="塔罗牌背面">`
    
    const cardBack = document.createElement('div')
    cardBack.className = 'tarot-card-back'
    
    const colors = ['#9c27b0', '#673ab7', '#3f51b5', '#2196f3']
    const randomColor = colors[Math.floor(Math.random() * colors.length)]
    cardBack.style.backgroundColor = randomColor
    
    cardBack.innerHTML = `<div class="tarot-card-content"><p>点击翻牌</p></div>`
    
    cardInner.appendChild(cardFront)
    cardInner.appendChild(cardBack)
    card.appendChild(cardInner)
    deckElement.appendChild(card)
    
    // 添加點擊事件
    card.addEventListener('click', async function() {
      if (!this.classList.contains('flipped')) {
        this.classList.add('flipped')
        
        const cardBack = this.querySelector('.tarot-card-back')
        cardBack.innerHTML = `
          <div class="tarot-card-content">
            <h4>塔罗牌解读</h4>
            <div class="tarot-analysis">正在解读中...</div>
          </div>
        `
        
        try {
          const response = await mastersChat({
            query: '请解读我抽到的塔罗牌，我近期的运势如何？',
            conversation_id: conversationId,
            user: localStorage.getItem('user_id') || 'fortune-user',
            workflow_type: 'tarot'
          })
          
          if (response.ok) {
            const reader = response.body.getReader()
            const decoder = new TextDecoder('utf-8')
            let buffer = ''
            for (;;) {
              const { done, value } = await reader.read()
              if (done) break
              const chunk = decoder.decode(value, { stream: true })
              buffer += chunk
              const lines = buffer.split('\n')
              buffer = lines.pop() || ''
              for (const line of lines) {
                if (line.trim() === '') continue
                if (line.startsWith('data: ')) {
                  const jsonStr = line.substring(6).trim()
                  try {
                    const data = JSON.parse(jsonStr)
                    if (data.answer) {
                      fortuneResults.tarot = data.answer; // 保存塔罗分析结果
                      cardBack.innerHTML = `
                        <div class="tarot-card-content">
                          <h4>塔罗牌解读</h4>
                          <div class="tarot-analysis">${data.answer}</div>
                        </div>
                      `
                    }
                  } catch (err) {
                    console.warn('解析API响应失败:', err)
                  }
                }
              }
            }
          }
        } catch (error) {
          console.error('获取塔罗牌解读失败:', error)
          cardBack.innerHTML = `
            <div class="tarot-card-content error">
              <p>解读失败，请重试</p>
            </div>
          `
        }
      }
    })
  })
}

onMounted(() => {
  // 組件掛載後的初始化
})
</script>

<style>
.fortune-bg {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: none;
  overflow-y: auto;
}
.fortune-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
</style>
