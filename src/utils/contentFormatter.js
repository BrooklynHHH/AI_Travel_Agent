/**
 * 内容格式化工具
 * 统一处理各种工具返回的内容格式
 */

import SearchContentParser from './searchContentParser.js'

class ContentFormatter {
  /**
   * 格式化工具返回的内容
   * @param {string|Object} content - 原始内容或结构化数据对象
   * @param {Object} options - 格式化选项
   * @returns {string} 格式化后的内容
   */
  static formatToolContent(content, options = {}) {
    if (!content) {
      return ''
    }

    // 如果是对象，直接处理
    if (typeof content === 'object') {
      try {
        const structuredData = this.parseStructuredContent(content)
        if (structuredData) {
          return this.renderStructuredContent(structuredData, options)
        }
        // 如果不是已知的结构化数据类型，返回JSON字符串
        return JSON.stringify(content, null, 2)
      } catch (error) {
        console.warn('对象内容格式化失败:', error)
        return JSON.stringify(content, null, 2)
      }
    }

    // 如果是字符串，按原逻辑处理
    if (typeof content !== 'string') {
      return String(content)
    }

    try {
      // 尝试解析为结构化数据
      const structuredData = this.parseStructuredContent(content)
      
      if (structuredData) {
        return this.renderStructuredContent(structuredData, options)
      }
      
      // 如果不是结构化数据，返回原内容
      return content
    } catch (error) {
      console.warn('内容格式化失败:', error)
      return content
    }
  }

  /**
   * 解析结构化内容
   * @param {string|Object} content - 原始内容或结构化数据对象
   * @returns {Object|null} 解析后的结构化数据
   */
  static parseStructuredContent(content) {
    // 如果已经是对象，直接使用SearchContentParser处理
    if (typeof content === 'object' && content !== null) {
      if (content.type === 'search_ref' || content.type === 'search_tool') {
        return SearchContentParser.processStructuredData(content)
      }
      return content // 其他类型的对象直接返回
    }
    
    // 如果是字符串，检测内容类型并使用相应的解析器
    if (typeof content === 'string' && this.isSearchContent(content)) {
      return SearchContentParser.parseSearchContent(content)
    }
    
    // 可以在这里添加其他类型的解析器
    // if (this.isOtherToolContent(content)) {
    //   return OtherToolParser.parseContent(content)
    // }
    
    return null
  }

  /**
   * 检测是否为搜索工具内容
   * @param {string} content - 内容字符串
   * @returns {boolean} 是否为搜索内容
   */
  static isSearchContent(content) {
    if (!content || typeof content !== 'string') {
      return false
    }

    // 使用SearchContentParser的验证方法
    try {
      // 导入时可能会有循环依赖问题，所以直接在这里实现检查逻辑
      const hasSearchType = content.includes('"type"') || content.includes("'type'")
      const hasSearchData = content.includes('"datas"') || content.includes("'datas'")
      const hasSearchRef = content.includes('search_ref') || content.includes('search_tool')
      
      // 排除明显的Markdown内容
      const hasMarkdownHeaders = content.includes('**') || content.includes('##')
      const hasMarkdownLinks = content.includes('[') && content.includes('](')
      
      // 如果包含大量Markdown格式，可能不是搜索结果
      if (hasMarkdownHeaders || hasMarkdownLinks) {
        // 但如果同时包含搜索特征，仍然尝试解析
        return hasSearchType && hasSearchData && hasSearchRef
      }
      
      return hasSearchType && hasSearchData
    } catch (error) {
      console.warn('搜索内容检测失败:', error)
      return false
    }
  }

  /**
   * 渲染结构化内容
   * @param {Object} data - 结构化数据
   * @param {Object} options - 渲染选项
   * @returns {string} 渲染后的HTML
   */
  static renderStructuredContent(data, options = {}) {
    if (!data || typeof data !== 'object') {
      return ''
    }

    // 根据数据类型选择渲染器
    switch (data.type) {
      case 'search_ref':
      case 'search_tool':
        return this.renderSearchContent(data, options)
      
      default:
        return this.renderGenericContent(data, options)
    }
  }

  /**
   * 渲染搜索内容
   * @param {Object} data - 搜索数据
   * @param {Object} options - 渲染选项
   * @returns {string} HTML字符串
   */
  static renderSearchContent(data, options = {}) {
    const renderOptions = {
      showSummary: true,
      showMetadata: false,
      maxResults: 10,
      cardStyle: true,
      ...options
    }

    return SearchContentParser.renderSearchResults(data, renderOptions)
  }

  /**
   * 渲染通用内容
   * @param {Object} data - 通用数据
   * @param {Object} options - 渲染选项
   * @returns {string} HTML字符串
   */
  static renderGenericContent(data, options = {}) {
    // 对于非特定类型的结构化数据，提供基础的JSON展示
    try {
      const jsonString = JSON.stringify(data, null, 2)
      const showMetadata = options.showMetadata || false
      
      let metadataHtml = ''
      if (showMetadata && data.metadata) {
        metadataHtml = `
          <div class="content-metadata">
            <small>元数据: ${JSON.stringify(data.metadata)}</small>
          </div>
        `
      }
      
      return `
        <div class="generic-content">
          <div class="content-type-label">结构化数据 (${data.type || '未知类型'})</div>
          ${metadataHtml}
          <pre class="json-content"><code>${this.escapeHtml(jsonString)}</code></pre>
        </div>
      `
    } catch (error) {
      return '<div class="error-content">数据格式错误</div>'
    }
  }

  /**
   * 转义HTML字符
   * @param {string} text - 原始文本
   * @returns {string} 转义后的文本
   */
  static escapeHtml(text) {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  /**
   * 提取内容摘要
   * @param {string} content - 原始内容
   * @param {number} maxLength - 最大长度
   * @returns {string} 摘要
   */
  static extractSummary(content, maxLength = 200) {
    if (!content || typeof content !== 'string') {
      return ''
    }

    // 尝试解析结构化内容
    const structuredData = this.parseStructuredContent(content)
    
    if (structuredData && structuredData.type === 'search_ref') {
      return SearchContentParser.formatAsReferenceList(structuredData, 5)
    }

    // 对于普通文本，直接截取
    const cleanContent = content.trim().replace(/\s+/g, ' ')
    
    if (cleanContent.length <= maxLength) {
      return cleanContent
    }

    return cleanContent.substring(0, maxLength) + '...'
  }

  /**
   * 检测内容类型
   * @param {string} content - 内容字符串
   * @returns {string} 内容类型
   */
  static detectContentType(content) {
    if (!content || typeof content !== 'string') {
      return 'unknown'
    }

    if (this.isSearchContent(content)) {
      return 'search'
    }

    // 检测JSON格式
    try {
      JSON.parse(content)
      return 'json'
    } catch (e) {
      // 不是JSON
    }

    // 检测Markdown格式
    if (content.includes('##') || content.includes('**') || content.includes('[') && content.includes('](')) {
      return 'markdown'
    }

    // 检测HTML格式
    if (content.includes('<') && content.includes('>')) {
      return 'html'
    }

    return 'text'
  }

  /**
   * 获取内容统计信息
   * @param {string} content - 内容字符串
   * @returns {Object} 统计信息
   */
  static getContentStats(content) {
    if (!content || typeof content !== 'string') {
      return {
        type: 'unknown',
        length: 0,
        words: 0,
        lines: 0,
        hasStructuredData: false
      }
    }

    const type = this.detectContentType(content)
    const length = content.length
    const words = content.trim().split(/\s+/).length
    const lines = content.split('\n').length
    const hasStructuredData = type !== 'text' && type !== 'unknown'

    let additionalStats = {}

    // 为搜索内容添加特殊统计
    if (type === 'search') {
      const structuredData = this.parseStructuredContent(content)
      if (structuredData && structuredData.results) {
        additionalStats.searchResults = structuredData.results.length
        additionalStats.totalResults = structuredData.metadata?.totalResults || 0
      }
    }

    return {
      type,
      length,
      words,
      lines,
      hasStructuredData,
      ...additionalStats
    }
  }

  /**
   * 批量处理内容
   * @param {Array} contents - 内容数组
   * @param {Object} options - 处理选项
   * @returns {Array} 处理后的内容数组
   */
  static batchFormatContent(contents, options = {}) {
    if (!Array.isArray(contents)) {
      return []
    }

    return contents.map(content => ({
      original: content,
      formatted: this.formatToolContent(content, options),
      stats: this.getContentStats(content),
      summary: this.extractSummary(content)
    }))
  }
}

export default ContentFormatter
