export const MIFY_API_KEY = 'app-O7w2lF9yDCUjuEl3M6DJoUzm';
export const MIFY_API_URL = 'https://mify-be.pt.xiaomi.com/api/v1';
export const TAROT_APP_ID = 'app-LowxiZTrY0htW4CtKvh8PLFE';
export const FORTUNE_APP_ID = 'app-O7w2lF9yDCUjuEl3M6DJoUzm';

const updateCardPreviewsFromResults = (results) => {
  // 只要有 zongjie 或 fenxi 就顯示
  cardPreviews.zodiac = formatDetailContent(
    (results.xingzuo.fenxi || results.xingzuo.zongjie || '暂无内容').substring(0, 200) + '...'
  )
  cardPreviews.bazi = formatDetailContent(
    (results.bazi.fenxi || results.bazi.zongjie || '暂无内容').substring(0, 200) + '...'
  )
  cardPreviews.astro = formatDetailContent(
    (results.xingpan.fenxi || results.xingpan.zongjie || '暂无内容').substring(0, 200) + '...'
  )
}

const sendMessage = async () => {
  // ...原有代碼...
  try {
    const response = await fetch('/api/masters-chat', {})
    if (response.ok) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      let hasMasterMsg = false
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
              // 兼容 answer 字段
              if (data.answer) {
                addSystemMessage(data.answer)
                hasMasterMsg = true
              }
              // 兼容 master_messages
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
                      hasMasterMsg = true
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
      // 如果一條大師消息都沒有，給用戶提示
      if (!hasMasterMsg) {
        addSystemMessage('大师们暂时没有回复，请稍后再试。')
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    addSystemMessage('发送消息失败，请重试')
  }
} 