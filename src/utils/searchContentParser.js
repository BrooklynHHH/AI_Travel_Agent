/**
 * 搜索内容解析器
 * 用于处理搜索工具返回的结构化数据并进行渲染
 */

class SearchContentParser {
  /**
   * 处理搜索工具返回的结构化数据
   * @param {Object|string} data - 结构化数据对象或字符串
   * @returns {Object} 标准化后的搜索数据
   */
  static processStructuredData(data) {
    console.log('🔍 [SearchContentParser] 开始处理搜索数据')
    console.log('🔍 [SearchContentParser] 输入数据类型:', typeof data)
    
    // 如果是字符串，尝试解析为JSON（兼容旧格式）
    if (typeof data === 'string') {
      console.log('🔍 [SearchContentParser] 检测到字符串格式，尝试解析')
      try {
        data = JSON.parse(data)
        console.log('🔍 [SearchContentParser] 字符串解析成功')
      } catch (error) {
        console.warn('🔍 [SearchContentParser] 字符串解析失败:', error.message)
        return null
      }
    }
    
    // 验证数据格式
    if (!data || typeof data !== 'object') {
      console.warn('🔍 [SearchContentParser] 数据格式无效')
      return null
    }
    
    // 检查是否是搜索结果类型
    if (data.type !== 'search_ref' && data.type !== 'search_tool') {
      console.warn('🔍 [SearchContentParser] 不是搜索结果类型:', data.type)
      return null
    }
    
    console.log('🔍 [SearchContentParser] 开始标准化数据')
    const normalized = this.normalizeSearchData(data)
    console.log('🔍 [SearchContentParser] 数据处理完成，结果数量:', normalized?.results?.length || 0)
    
    return normalized
  }

  /**
   * 解析搜索工具返回的内容（兼容旧版本）
   * @param {string|Object} content - 原始字符串内容或结构化数据
   * @returns {Object} 解析后的结构化数据
   */
  static parseSearchContent(content) {
    console.log('🔍 [SearchContentParser] 使用兼容模式解析内容')
    return this.processStructuredData(content)
  }

  /**
   * 标准化搜索数据结构
   * @param {Object} data - 原始数据
   * @returns {Object} 标准化后的数据
   */
  static normalizeSearchData(data) {
    if (!data || typeof data !== 'object') {
      return null
    }

    // 检查是否是搜索结果类型
    if (data.type !== 'search_ref' && data.type !== 'search_tool') {
      return data // 非搜索类型，直接返回
    }

    // 标准化搜索结果数据
    const normalized = {
      type: data.type,
      metadata: {
        totalResults: 0,
        searchTime: Date.now(),
        source: 'search_tool'
      },
      results: []
    }

    // 处理搜索结果数组
    if (data.datas && Array.isArray(data.datas)) {
      normalized.results = data.datas
        .filter(item => item && typeof item === 'object')
        .map((item, index) => this.normalizeSearchItem(item, index))
        .filter(item => item !== null)
      
      normalized.metadata.totalResults = normalized.results.length
    }

    return normalized
  }

  /**
   * 标准化单个搜索结果项
   * @param {Object} item - 原始搜索结果项
   * @param {number} index - 索引
   * @returns {Object} 标准化后的搜索结果项
   */
  static normalizeSearchItem(item, index) {
    if (!item.title && !item.url && !item.content) {
      return null // 无效项
    }

    return {
      id: `search_result_${index}_${Date.now()}`,
      title: item.title || '无标题',
      url: item.url || '',
      content: item.content || '',
      summary: this.generateSummary(item.content || ''),
      siteName: item.siteName || this.extractSiteName(item.url || ''),
      thumbnail: item.pic || null,
      relevanceScore: this.calculateRelevanceScore(item),
      metadata: {
        contentLength: (item.content || '').length,
        hasImage: !!item.pic,
        domain: this.extractDomain(item.url || '')
      }
    }
  }

  /**
   * 生成内容摘要
   * @param {string} content - 原始内容
   * @param {number} maxLength - 最大长度
   * @returns {string} 摘要
   */
  static generateSummary(content, maxLength = 200) {
    if (!content || typeof content !== 'string') {
      return ''
    }

    // 清理内容：移除多余的空白字符和特殊符号
    let cleanContent = content.trim()
      .replace(/\s+/g, ' ')
      .replace(/^\d+\.\s*/, '') // 移除开头的数字编号
      .replace(/^[*•-]\s*/, '') // 移除开头的列表符号
    
    if (cleanContent.length <= maxLength) {
      return cleanContent
    }

    // 智能截断：优先在合适的标点符号处截断
    const punctuationMarks = /[。！？；：.!?;:]/
    const sentences = cleanContent.split(punctuationMarks)
    let summary = ''
    let currentLength = 0
    
    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i].trim()
      if (!sentence) continue
      
      const nextLength = currentLength + sentence.length + 1 // +1 for punctuation
      
      if (nextLength > maxLength && summary.length > 0) {
        break
      }
      
      if (summary.length > 0) {
        summary += '。' + sentence
        currentLength = nextLength
      } else {
        summary = sentence
        currentLength = sentence.length
      }
    }

    // 如果没有找到合适的句子边界，直接截断
    if (summary.length === 0 || summary.length < maxLength * 0.3) {
      summary = cleanContent.substring(0, maxLength)
      
      // 尝试在最后一个空格处截断，避免截断单词
      const lastSpaceIndex = summary.lastIndexOf(' ')
      if (lastSpaceIndex > maxLength * 0.7) {
        summary = summary.substring(0, lastSpaceIndex)
      }
    }

    // 确保摘要以合适的标点结尾
    if (summary.length < cleanContent.length) {
      if (!/[。！？.!?]$/.test(summary)) {
        summary += '...'
      }
    }

    return summary.trim()
  }

  /**
   * 从URL提取站点名称
   * @param {string} url - URL地址
   * @returns {string} 站点名称
   */
  static extractSiteName(url) {
    if (!url) return ''
    
    try {
      const urlObj = new URL(url)
      const hostname = urlObj.hostname
      
      // 移除www前缀
      const siteName = hostname.replace(/^www\./, '')
      
      // 提取主域名
      const parts = siteName.split('.')
      if (parts.length >= 2) {
        return parts[parts.length - 2]
      }
      
      return siteName
    } catch (error) {
      return ''
    }
  }

  /**
   * 从URL提取域名
   * @param {string} url - URL地址
   * @returns {string} 域名
   */
  static extractDomain(url) {
    if (!url) return ''
    
    try {
      const urlObj = new URL(url)
      return urlObj.hostname
    } catch (error) {
      return ''
    }
  }

  /**
   * 计算相关性分数
   * @param {Object} item - 搜索结果项
   * @returns {number} 相关性分数 (0-100)
   */
  static calculateRelevanceScore(item) {
    let score = 50 // 基础分数

    // 有标题加分
    if (item.title && item.title.trim()) {
      score += 20
    }

    // 有内容加分
    if (item.content && item.content.trim()) {
      score += 20
      
      // 内容长度适中加分
      const contentLength = item.content.length
      if (contentLength > 100 && contentLength < 2000) {
        score += 10
      }
    }

    // 有图片加分
    if (item.pic) {
      score += 5
    }

    // 有站点名称加分
    if (item.siteName && item.siteName.trim()) {
      score += 5
    }

    return Math.min(100, Math.max(0, score))
  }

  /**
   * 渲染搜索结果为HTML
   * @param {Object} data - 标准化后的搜索数据
   * @param {Object} options - 渲染选项
   * @returns {string} HTML字符串
   */
  static renderSearchResults(data, options = {}) {
    if (!data || !data.results || !Array.isArray(data.results)) {
      return ''
    }

    const {
      showSummary = true,
      showMetadata = false,
      maxResults = 10,
      cardStyle = true
    } = options

    const validResults = data.results
      .filter(item => item.title || item.content)
      .slice(0, maxResults)

    if (validResults.length === 0) {
      return '<div class="search-no-results">未找到相关结果</div>'
    }

    const resultsHtml = validResults
      .map(item => this.renderSearchItem(item, { showSummary, showMetadata, cardStyle }))
      .join('')

    const headerHtml = `
      <div class="search-results-header">
        <h4 class="search-results-title">🔍 搜索结果 (${validResults.length}条)</h4>
        ${showMetadata ? `<div class="search-metadata">搜索时间: ${new Date(data.metadata.searchTime).toLocaleString()}</div>` : ''}
      </div>
    `

    return `
      <div class="search-results-container">
        ${headerHtml}
        <div class="search-results-list">
          ${resultsHtml}
        </div>
      </div>
    `
  }

  /**
   * 渲染单个搜索结果项
   * @param {Object} item - 搜索结果项
   * @param {Object} options - 渲染选项
   * @returns {string} HTML字符串
   */
  static renderSearchItem(item, options = {}) {
    const { showSummary = true, showMetadata = false, cardStyle = true } = options

    // 标题：title字段的内容+url——>形成可跳转的超链接
    const titleHtml = item.url 
      ? `<a href="${item.url}" target="_blank" rel="noopener noreferrer" class="search-item-title" title="点击访问原文">${this.escapeHtml(item.title)}</a>`
      : `<span class="search-item-title">${this.escapeHtml(item.title)}</span>`

    // 内容：网页相应的内容content字段（过长可简略展示）
    let contentHtml = ''
    if (item.content && item.content.trim()) {
      // 对内容进行适当的简略处理
      const displayContent = this.formatContentForDisplay(item.content, 200)
      contentHtml = `<div class="search-item-content-text">${this.escapeHtml(displayContent)}</div>`
    }

    // 可选的摘要显示（如果没有content或需要额外摘要）
    const summaryHtml = showSummary && item.summary && !item.content
      ? `<div class="search-item-summary">${this.escapeHtml(item.summary)}</div>`
      : ''

    const metadataHtml = showMetadata 
      ? `
        <div class="search-item-metadata">
          <span class="search-item-domain">🌐 ${this.escapeHtml(item.metadata.domain)}</span>
          <span class="search-item-length">📄 ${item.metadata.contentLength}字符</span>
          <span class="search-item-score">⭐ ${item.relevanceScore}%</span>
        </div>
      `
      : ''

    const thumbnailHtml = item.thumbnail 
      ? `<div class="search-item-thumbnail"><img src="${item.thumbnail}" alt="缩略图" loading="lazy" /></div>`
      : ''

    const containerClass = cardStyle ? 'search-item-card' : 'search-item-simple'

    return `
      <div class="search-item ${containerClass}" data-id="${item.id}">
        ${thumbnailHtml}
        <div class="search-item-content">
          <div class="search-item-header">
            ${titleHtml}
            ${item.siteName ? `<span class="search-item-site">${this.escapeHtml(item.siteName)}</span>` : ''}
          </div>
          ${contentHtml}
          ${summaryHtml}
          ${metadataHtml}
        </div>
      </div>
    `
  }

  /**
   * 格式化内容用于显示（处理过长内容的简略展示）
   * @param {string} content - 原始内容
   * @param {number} maxLength - 最大显示长度
   * @returns {string} 格式化后的内容
   */
  static formatContentForDisplay(content, maxLength = 200) {
    if (!content || typeof content !== 'string') {
      return ''
    }

    // 清理内容：移除多余的空白字符
    const cleanContent = content.trim().replace(/\s+/g, ' ')
    
    if (cleanContent.length <= maxLength) {
      return cleanContent
    }

    // 尝试在合适的位置截断（优先在句号、感叹号、问号处）
    const sentences = cleanContent.split(/([。！？.!?])/g)
    let result = ''
    
    for (let i = 0; i < sentences.length; i += 2) {
      const sentence = sentences[i] || ''
      const punctuation = sentences[i + 1] || ''
      
      if ((result + sentence + punctuation).length > maxLength) {
        break
      }
      
      result += sentence + punctuation
    }

    // 如果没有找到合适的句子边界，直接截断
    if (result.length === 0) {
      result = cleanContent.substring(0, maxLength)
    }

    // 添加省略号（如果内容被截断）
    if (result.length < cleanContent.length) {
      result = result.trim() + '...'
    }

    return result
  }

  /**
   * 转义HTML特殊字符
   * @param {string} text - 原始文本
   * @returns {string} 转义后的文本
   */
  static escapeHtml(text) {
    if (!text || typeof text !== 'string') {
      return ''
    }
    
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  /**
   * 获取搜索结果的纯文本摘要
   * @param {Object} data - 标准化后的搜索数据
   * @param {number} maxItems - 最大项目数
   * @returns {string} 纯文本摘要
   */
  static getTextSummary(data, maxItems = 5) {
    if (!data || !data.results || !Array.isArray(data.results)) {
      return '未找到搜索结果'
    }

    const validResults = data.results
      .filter(item => item.title || item.content)
      .slice(0, maxItems)

    if (validResults.length === 0) {
      return '未找到有效的搜索结果'
    }

    const summaryLines = validResults.map((item, index) => {
      const title = item.title || '无标题'
      const summary = item.summary || '无摘要'
      return `${index + 1}. ${title}\n   ${summary}`
    })

    return `搜索到 ${validResults.length} 条相关结果：\n\n${summaryLines.join('\n\n')}`
  }

  /**
   * 格式化搜索结果为参考资料列表
   * @param {Object} data - 标准化后的搜索数据或原始search_ref数据
   * @param {number} maxItems - 最大项目数
   * @returns {string} 参考资料格式的字符串
   */
  static formatAsReferenceList(data, maxItems = 10) {
    // 如果是原始的search_ref数据，先进行标准化
    let normalizedData = data
    if (data && data.type === 'search_ref' && data.datas) {
      normalizedData = this.normalizeSearchData(data)
    }

    if (!normalizedData || !normalizedData.results || !Array.isArray(normalizedData.results)) {
      return '参考资料：\n暂无相关资料'
    }

    const validResults = normalizedData.results
      .filter(item => item.title || item.content)
      .slice(0, maxItems)

    if (validResults.length === 0) {
      return '参考资料：\n暂无有效资料'
    }

    const referenceLines = validResults.map((item, index) => {
      const title = item.title || '无标题'
      const url = item.url || ''
      const content = item.content || ''
      
      // 生成摘要，优先使用content，其次使用已有的summary
      let summary = ''
      if (content) {
        summary = this.generateSummary(content, 150)
      } else if (item.summary) {
        summary = item.summary
      } else {
        summary = '无内容摘要'
      }

      // 格式化标题和URL
      const titleWithUrl = url ? `${title}[${url}]` : title
      
      return `${index + 1}.${titleWithUrl}\n   摘要：${summary}`
    })

    return `参考资料：\n${referenceLines.join('\n')}`
  }

  /**
   * 渲染search_ref数据为参考资料的markdown格式
   * @param {Object} data - search_ref类型的数据
   * @param {number} maxItems - 最大项目数
   * @param {number} summaryLength - 摘要长度
   * @returns {string} markdown格式的参考资料
   */
  static renderSearchRefAsMarkdown(data, maxItems = 10, summaryLength = 150) {
    console.log('🔍 [SearchContentParser] 开始渲染search_ref为markdown格式')
    console.log('🔍 [SearchContentParser] 输入数据:', data)
    
    if (!data || data.type !== 'search_ref' || !data.datas || !Array.isArray(data.datas)) {
      console.warn('🔍 [SearchContentParser] 数据格式不正确或不是search_ref类型')
      return ''
    }

    const validResults = data.datas
      .filter(item => item && (item.title || item.content))
      .slice(0, maxItems)

    if (validResults.length === 0) {
      console.warn('🔍 [SearchContentParser] 没有有效的搜索结果')
      return ''
    }

    console.log(`🔍 [SearchContentParser] 处理 ${validResults.length} 条有效结果`)

    const referenceLines = validResults.map((item, index) => {
      const title = item.title || '无标题'
      const url = item.url || ''
      const content = item.content || ''
      
      // 生成摘要
      const summary = content ? this.generateSummary(content, summaryLength) : '无内容摘要'
      
      // 格式化为markdown超链接
      const titleLink = url ? `[${title}](${url})` : title
      
      return `${index + 1}.${titleLink}\n   摘要：${summary}`
    })

    const result = `参考资料：\n${referenceLines.join('\n')}`
    console.log('🔍 [SearchContentParser] markdown渲染完成')
    return result
  }

  /**
   * 渲染search_ref数据为HTML格式的参考资料
   * @param {Object} data - search_ref类型的数据
   * @param {Object} options - 渲染选项
   * @returns {string} HTML格式的参考资料
   */
  static renderSearchRefAsHTML(data, options = {}) {
    const {
      maxItems = 10,
      summaryLength = 150,
      showIndex = true,
      cardStyle = true
    } = options

    console.log('🔍 [SearchContentParser] 开始渲染search_ref为HTML格式')
    
    if (!data || data.type !== 'search_ref' || !data.datas || !Array.isArray(data.datas)) {
      console.warn('🔍 [SearchContentParser] 数据格式不正确或不是search_ref类型')
      return '<div class="search-ref-empty">暂无参考资料</div>'
    }

    const validResults = data.datas
      .filter(item => item && (item.title || item.content))
      .slice(0, maxItems)

    if (validResults.length === 0) {
      return '<div class="search-ref-empty">暂无有效的参考资料</div>'
    }

    const itemsHtml = validResults.map((item, index) => {
      const title = item.title || '无标题'
      const url = item.url || ''
      const content = item.content || ''
      
      // 生成摘要
      const summary = content ? this.generateSummary(content, summaryLength) : '无内容摘要'
      
      // 格式化标题
      const titleHtml = url 
        ? `<a href="${url}" target="_blank" rel="noopener noreferrer" class="search-ref-title-link" title="点击访问原文">${this.escapeHtml(title)}</a>`
        : `<span class="search-ref-title">${this.escapeHtml(title)}</span>`

      const indexHtml = showIndex ? `<span class="search-ref-index">${index + 1}.</span>` : ''

      return `
        <div class="search-ref-item ${cardStyle ? 'search-ref-card' : 'search-ref-simple'}">
          <div class="search-ref-header">
            ${indexHtml}
            ${titleHtml}
          </div>
          <div class="search-ref-summary">
            <span class="search-ref-summary-label">摘要：</span>
            <span class="search-ref-summary-text">${this.escapeHtml(summary)}</span>
            <br></br>
          </div>
        </div>
        ${index < validResults.length - 1 ? '<div class="search-ref-separator"></div>' : ''}
      `
    }).join('')

    return `
      <div class="search-ref-container">
        <div class="search-ref-header">
          <h4 class="search-ref-title">📚 参考资料 (${validResults.length}条)</h4>
        </div>
        <div class="search-ref-list">
          ${itemsHtml}
        </div>
        <hr>
      </div>
    `
  }
}

export default SearchContentParser
