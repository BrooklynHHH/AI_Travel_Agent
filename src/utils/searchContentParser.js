/**
 * 搜索内容解析器
 * 用于将搜索工具返回的字符串内容转换为结构化数据
 */

class SearchContentParser {
  /**
   * 解析搜索工具返回的内容
   * @param {string} content - 原始字符串内容
   * @returns {Object} 解析后的结构化数据
   */
  static parseSearchContent(content) {
    console.log('🔍 [SearchContentParser] 开始解析搜索内容')
    console.log('🔍 [SearchContentParser] 输入内容类型:', typeof content)
    console.log('🔍 [SearchContentParser] 输入内容长度:', content?.length || 0)
    
    if (!content || typeof content !== 'string') {
      console.warn('🔍 [SearchContentParser] 内容为空或不是字符串类型')
      return null
    }

    // 预处理：检查并处理多个连接的JSON对象
    console.log('🔍 [SearchContentParser] 开始预处理多个连接的JSON对象')
    const cleanedContent = this.preprocessMultipleJsonObjects(content)
    console.log('🔍 [SearchContentParser] 预处理完成，处理后内容长度:', cleanedContent.length)

    // 预检查：确保内容看起来像是搜索结果
    console.log('🔍 [SearchContentParser] 开始预检查内容格式')
    if (!this.isValidSearchContent(cleanedContent)) {
      console.warn('🔍 [SearchContentParser] 内容不是有效的搜索结果格式')
      console.log('🔍 [SearchContentParser] 内容预览:', cleanedContent.substring(0, 200) + '...')
      return null
    }
    
    console.log('🔍 [SearchContentParser] 预检查通过，开始解析')
    console.log('🔍 [SearchContentParser] 处理前数据预览:', cleanedContent.substring(0, 500) + '...')
    
    try {
      console.log('🔍 [SearchContentParser] 尝试JSON解析')
      const jsonResult = this.tryParseJSON(cleanedContent)
      console.log('🔍 [SearchContentParser] JSON解析成功')
      return jsonResult
    } catch (error) {
      console.warn('🔍 [SearchContentParser] JSON解析失败:', error.message)
      console.log('🔍 [SearchContentParser] JSON解析错误详情:', error)
      
      try {
        console.log('🔍 [SearchContentParser] 尝试Python字典解析')
        const pythonResult = this.parsePythonDict(cleanedContent)
        console.log('🔍 [SearchContentParser] Python字典解析成功')
        return pythonResult
      } catch (pythonError) {
        console.error('🔍 [SearchContentParser] Python字典解析也失败:', pythonError.message)
        console.log('🔍 [SearchContentParser] Python解析错误详情:', pythonError)
        console.warn('🔍 [SearchContentParser] 所有解析方法都失败，返回null')
        return null
      }
    }
  }

  /**
   * 预处理多个连接的JSON对象
   * @param {string} content - 原始内容
   * @returns {string} 处理后的内容
   */
  static preprocessMultipleJsonObjects(content) {
    console.log('🔍 [preprocessMultipleJsonObjects] 开始预处理多个JSON对象')
    console.log('🔍 [preprocessMultipleJsonObjects] 原始内容长度:', content.length)
    
    // 检查是否包含多个连接的JSON对象的模式
    // 常见模式：}]}{  或  }]}{'  等
    const multipleJsonPattern = /\}\]\}\s*[{['"]]/g
    const matches = content.match(multipleJsonPattern)
    
    if (matches && matches.length > 0) {
      console.log('🔍 [preprocessMultipleJsonObjects] 检测到多个连接的JSON对象')
      console.log('🔍 [preprocessMultipleJsonObjects] 匹配模式数量:', matches.length)
      console.log('🔍 [preprocessMultipleJsonObjects] 匹配内容:', matches)
      
      // 策略1：尝试提取第一个完整的JSON对象
      const firstJsonResult = this.extractFirstJsonObject(content)
      if (firstJsonResult) {
        console.log('🔍 [preprocessMultipleJsonObjects] 成功提取第一个JSON对象')
        return firstJsonResult
      }
      
      // 策略2：尝试提取最后一个完整的JSON对象
      const lastJsonResult = this.extractLastJsonObject(content)
      if (lastJsonResult) {
        console.log('🔍 [preprocessMultipleJsonObjects] 成功提取最后一个JSON对象')
        return lastJsonResult
      }
      
      // 策略3：尝试分割并选择最大的JSON对象
      const largestJsonResult = this.extractLargestJsonObject(content)
      if (largestJsonResult) {
        console.log('🔍 [preprocessMultipleJsonObjects] 成功提取最大的JSON对象')
        return largestJsonResult
      }
      
      console.warn('🔍 [preprocessMultipleJsonObjects] 所有提取策略都失败，返回原内容')
    } else {
      console.log('🔍 [preprocessMultipleJsonObjects] 未检测到多个连接的JSON对象')
    }
    
    return content
  }

  /**
   * 提取第一个完整的JSON对象
   * @param {string} content - 原始内容
   * @returns {string|null} 第一个JSON对象或null
   */
  static extractFirstJsonObject(content) {
    console.log('🔍 [extractFirstJsonObject] 尝试提取第一个JSON对象')
    
    try {
      // 寻找第一个 }]} 的位置
      const firstEndIndex = content.indexOf('}]}')
      if (firstEndIndex !== -1) {
        const firstJsonCandidate = content.substring(0, firstEndIndex + 3)
        console.log('🔍 [extractFirstJsonObject] 第一个JSON候选长度:', firstJsonCandidate.length)
        console.log('🔍 [extractFirstJsonObject] 第一个JSON预览:', firstJsonCandidate.substring(0, 200))
        
        // 验证是否是有效的JSON
        if (this.validateJsonCandidate(firstJsonCandidate)) {
          console.log('🔍 [extractFirstJsonObject] 第一个JSON对象验证成功')
          return firstJsonCandidate
        }
      }
    } catch (error) {
      console.warn('🔍 [extractFirstJsonObject] 提取第一个JSON对象失败:', error.message)
    }
    
    return null
  }

  /**
   * 提取最后一个完整的JSON对象
   * @param {string} content - 原始内容
   * @returns {string|null} 最后一个JSON对象或null
   */
  static extractLastJsonObject(content) {
    console.log('🔍 [extractLastJsonObject] 尝试提取最后一个JSON对象')
    
    try {
      // 寻找最后一个 {"type" 的位置
      const lastStartIndex = content.lastIndexOf('{"type"')
      if (lastStartIndex === -1) {
        // 如果没有找到双引号格式，尝试单引号格式
        const lastStartIndexSingle = content.lastIndexOf("{'type'")
        if (lastStartIndexSingle !== -1) {
          const lastJsonCandidate = content.substring(lastStartIndexSingle)
          console.log('🔍 [extractLastJsonObject] 最后一个JSON候选(单引号)长度:', lastJsonCandidate.length)
          
          if (this.validateJsonCandidate(lastJsonCandidate)) {
            console.log('🔍 [extractLastJsonObject] 最后一个JSON对象(单引号)验证成功')
            return lastJsonCandidate
          }
        }
      } else {
        const lastJsonCandidate = content.substring(lastStartIndex)
        console.log('🔍 [extractLastJsonObject] 最后一个JSON候选长度:', lastJsonCandidate.length)
        console.log('🔍 [extractLastJsonObject] 最后一个JSON预览:', lastJsonCandidate.substring(0, 200))
        
        if (this.validateJsonCandidate(lastJsonCandidate)) {
          console.log('🔍 [extractLastJsonObject] 最后一个JSON对象验证成功')
          return lastJsonCandidate
        }
      }
    } catch (error) {
      console.warn('🔍 [extractLastJsonObject] 提取最后一个JSON对象失败:', error.message)
    }
    
    return null
  }

  /**
   * 提取最大的JSON对象
   * @param {string} content - 原始内容
   * @returns {string|null} 最大的JSON对象或null
   */
  static extractLargestJsonObject(content) {
    console.log('🔍 [extractLargestJsonObject] 尝试提取最大的JSON对象')
    
    try {
      // 使用正则表达式分割多个JSON对象
      const jsonSeparatorPattern = /\}\]\}\s*[{['"]]/g
      const parts = content.split(jsonSeparatorPattern)
      
      console.log('🔍 [extractLargestJsonObject] 分割后的部分数量:', parts.length)
      
      let largestJson = null
      let maxLength = 0
      
      for (let i = 0; i < parts.length; i++) {
        let candidate = parts[i].trim()
        
        // 为非第一个部分添加可能缺失的结尾
        if (i > 0 && !candidate.endsWith('}]}')) {
          candidate += '}]}'
        }
        
        // 为非最后一个部分添加可能缺失的开头
        if (i < parts.length - 1 && !candidate.startsWith('{')) {
          candidate = '{' + candidate
        }
        
        console.log('🔍 [extractLargestJsonObject] 候选', i, '长度:', candidate.length)
        
        if (candidate.length > maxLength && this.validateJsonCandidate(candidate)) {
          largestJson = candidate
          maxLength = candidate.length
          console.log('🔍 [extractLargestJsonObject] 找到更大的有效JSON，长度:', maxLength)
        }
      }
      
      if (largestJson) {
        console.log('🔍 [extractLargestJsonObject] 最大JSON对象验证成功，长度:', maxLength)
        return largestJson
      }
    } catch (error) {
      console.warn('🔍 [extractLargestJsonObject] 提取最大JSON对象失败:', error.message)
    }
    
    return null
  }

  /**
   * 验证JSON候选是否有效
   * @param {string} candidate - JSON候选字符串
   * @returns {boolean} 是否有效
   */
  static validateJsonCandidate(candidate) {
    if (!candidate || typeof candidate !== 'string') {
      return false
    }
    
    try {
      // 尝试直接解析JSON
      JSON.parse(candidate)
      return true
    } catch (directError) {
      try {
        // 尝试Python字典格式转换后解析
        const normalized = candidate
          .replace(/'/g, '"')
          .replace(/None/g, 'null')
          .replace(/True/g, 'true')
          .replace(/False/g, 'false')
        
        JSON.parse(normalized)
        return true
      } catch (pythonError) {
        return false
      }
    }
  }

  /**
   * 检查内容是否是有效的搜索结果格式
   * @param {string} content - 内容字符串
   * @returns {boolean} 是否有效
   */
  static isValidSearchContent(content) {
    console.log('🔍 [isValidSearchContent] 开始检查内容格式')
    
    // 检查是否包含搜索结果的基本特征
    const hasSearchType = content.includes('"type"') || content.includes("'type'")
    const hasSearchData = content.includes('"datas"') || content.includes("'datas'")
    const hasSearchRef = content.includes('search_ref') || content.includes('search_tool')
    
    console.log('🔍 [isValidSearchContent] 特征检查结果:')
    console.log('  - hasSearchType:', hasSearchType)
    console.log('  - hasSearchData:', hasSearchData)
    console.log('  - hasSearchRef:', hasSearchRef)
    
    // 排除明显的Markdown内容
    const hasMarkdownHeaders = content.includes('**') || content.includes('##')
    const hasMarkdownLinks = content.includes('[') && content.includes('](')
    
    console.log('🔍 [isValidSearchContent] Markdown检查结果:')
    console.log('  - hasMarkdownHeaders:', hasMarkdownHeaders)
    console.log('  - hasMarkdownLinks:', hasMarkdownLinks)
    
    // 如果包含大量Markdown格式，可能不是搜索结果
    if (hasMarkdownHeaders || hasMarkdownLinks) {
      console.log('🔍 [isValidSearchContent] 检测到Markdown格式，需要同时满足搜索特征')
      const isValid = hasSearchType && hasSearchData && hasSearchRef
      console.log('🔍 [isValidSearchContent] Markdown内容验证结果:', isValid)
      return isValid
    }
    
    const isValid = hasSearchType && hasSearchData
    console.log('🔍 [isValidSearchContent] 普通内容验证结果:', isValid)
    return isValid
  }

  /**
   * 尝试解析标准JSON格式
   * @param {string} content - JSON字符串
   * @returns {Object} 解析结果
   */
  static tryParseJSON(content) {
    console.log('🔍 [tryParseJSON] 开始JSON解析')
    console.log('🔍 [tryParseJSON] 内容长度:', content.length)
    console.log('🔍 [tryParseJSON] 内容开头:', content.substring(0, 100))
    console.log('🔍 [tryParseJSON] 内容结尾:', content.substring(content.length - 100))
    
    try {
      const parsed = JSON.parse(content)
      console.log('🔍 [tryParseJSON] JSON.parse成功')
      console.log('🔍 [tryParseJSON] 解析结果类型:', typeof parsed)
      console.log('🔍 [tryParseJSON] 解析结果键:', Object.keys(parsed || {}))
      
      const normalized = this.normalizeSearchData(parsed)
      console.log('🔍 [tryParseJSON] 标准化完成')
      return normalized
    } catch (error) {
      console.error('🔍 [tryParseJSON] JSON.parse失败:', error.message)
      throw error
    }
  }

  /**
   * 解析Python字典格式的字符串
   * @param {string} content - Python字典格式字符串
   * @returns {Object} 解析结果
   */
  static parsePythonDict(content) {
    console.log('🔍 [parsePythonDict] 开始Python字典解析')
    console.log('🔍 [parsePythonDict] 原始内容长度:', content.length)
    console.log('🔍 [parsePythonDict] 原始内容预览:', content.substring(0, 200))
    
    // 清理和标准化Python字典格式
    let normalizedContent = content.trim()
    console.log('🔍 [parsePythonDict] trim后长度:', normalizedContent.length)
    
    // 移除可能的外层引号
    if ((normalizedContent.startsWith('"') && normalizedContent.endsWith('"')) ||
        (normalizedContent.startsWith("'") && normalizedContent.endsWith("'"))) {
      console.log('🔍 [parsePythonDict] 检测到外层引号，移除中...')
      normalizedContent = normalizedContent.slice(1, -1)
      console.log('🔍 [parsePythonDict] 移除外层引号后长度:', normalizedContent.length)
    }

    console.log('🔍 [parsePythonDict] 开始替换Python特有值')
    
    // 先处理字符串内容中的引号问题
    // 使用更精确的正则表达式来处理字符串值中的引号
    console.log('🔍 [parsePythonDict] 开始处理字符串值中的引号')
    
    // 替换Python特有的值
    normalizedContent = normalizedContent
      .replace(/None/g, 'null')     // None转null
      .replace(/True/g, 'true')     // True转true
      .replace(/False/g, 'false')   // False转false
    
    console.log('🔍 [parsePythonDict] Python值替换完成')
    
    // 更精确地处理单引号转双引号的问题
    // 需要避免转换字符串内容中的引号
    console.log('🔍 [parsePythonDict] 开始精确处理引号转换')
    
    try {
      // 尝试使用更安全的方法转换引号
      // 先找到所有的字符串值，然后逐个处理
      normalizedContent = this.safeConvertQuotes(normalizedContent)
      console.log('🔍 [parsePythonDict] 安全引号转换完成')
      console.log('🔍 [parsePythonDict] 转换后内容预览:', normalizedContent.substring(0, 300))
      
    } catch (quoteError) {
      console.warn('🔍 [parsePythonDict] 安全引号转换失败，使用简单替换:', quoteError.message)
      // 如果安全转换失败，回退到简单替换
      normalizedContent = normalizedContent.replace(/'/g, '"')
      console.log('🔍 [parsePythonDict] 简单引号替换完成')
    }
      
    console.log('🔍 [parsePythonDict] 开始处理转义字符')
    // 处理可能的转义字符
    normalizedContent = normalizedContent
      .replace(/\\'/g, "'")         // 处理转义的单引号
      .replace(/\\"/g, '"')         // 处理转义的双引号

    console.log('🔍 [parsePythonDict] 转义字符处理完成')
    console.log('🔍 [parsePythonDict] 最终标准化内容预览:', normalizedContent.substring(0, 300))

    try {
      console.log('🔍 [parsePythonDict] 尝试JSON.parse标准化内容')
      const parsed = JSON.parse(normalizedContent)
      console.log('🔍 [parsePythonDict] JSON.parse成功')
      console.log('🔍 [parsePythonDict] 解析结果类型:', typeof parsed)
      console.log('🔍 [parsePythonDict] 解析结果键:', Object.keys(parsed || {}))
      
      const normalized = this.normalizeSearchData(parsed)
      console.log('🔍 [parsePythonDict] 标准化完成')
      return normalized
    } catch (error) {
      console.error('🔍 [parsePythonDict] JSON.parse失败:', error.message)
      console.log('🔍 [parsePythonDict] 失败时的内容:', normalizedContent.substring(0, 500))
      
      // 尝试找到具体的错误位置
      const errorMatch = error.message.match(/position (\d+)/)
      if (errorMatch) {
        const errorPos = parseInt(errorMatch[1])
        console.log('🔍 [parsePythonDict] 错误位置周围的内容:', normalizedContent.substring(Math.max(0, errorPos - 50), errorPos + 50))
        console.log('🔍 [parsePythonDict] 错误位置字符:', JSON.stringify(normalizedContent.charAt(errorPos)))
      }
      
      throw error
    }
  }

  /**
   * 安全地转换Python字典中的单引号为双引号
   * @param {string} content - 原始内容
   * @returns {string} 转换后的内容
   */
  static safeConvertQuotes(content) {
    console.log('🔍 [safeConvertQuotes] 开始安全引号转换')
    
    // 使用更简单但更可靠的方法：
    // 1. 先标记所有字符串值的位置
    // 2. 然后安全地替换键名和结构中的单引号
    
    try {
      // 方法1: 使用正则表达式匹配字符串值，并保护其中的内容
      let result = content
      
      // 首先处理字符串值中的双引号，将其转义
      // 匹配单引号包围的字符串值
      result = result.replace(/'([^'\\]*(\\.[^'\\]*)*)'/g, (match, stringContent) => {
        // 在字符串内容中转义双引号
        const escapedContent = stringContent.replace(/"/g, '\\"')
        return `"${escapedContent}"`
      })
      
      // 然后处理剩余的单引号（主要是键名）
      // 匹配键名模式：'key':
      result = result.replace(/'([^']+)'(\s*:)/g, '"$1"$2')
      
      console.log('🔍 [safeConvertQuotes] 正则表达式方法完成')
      return result
      
    } catch (regexError) {
      console.warn('🔍 [safeConvertQuotes] 正则表达式方法失败，使用状态机方法:', regexError.message)
      
      // 方法2: 回退到状态机方法，但改进处理逻辑
      return this.safeConvertQuotesStateMachine(content)
    }
  }

  /**
   * 使用状态机安全地转换引号
   * @param {string} content - 原始内容
   * @returns {string} 转换后的内容
   */
  static safeConvertQuotesStateMachine(content) {
    console.log('🔍 [safeConvertQuotesStateMachine] 开始状态机引号转换')
    
    let result = ''
    let inString = false
    let stringChar = null
    let i = 0
    
    while (i < content.length) {
      const char = content[i]
      const nextChar = i + 1 < content.length ? content[i + 1] : null
      
      if (!inString) {
        // 不在字符串内部
        if (char === "'" || char === '"') {
          // 开始一个字符串
          inString = true
          stringChar = char
          result += '"' // 统一使用双引号
        } else {
          result += char
        }
      } else {
        // 在字符串内部
        if (char === stringChar) {
          // 检查是否是转义的引号
          let backslashCount = 0
          let j = i - 1
          while (j >= 0 && content[j] === '\\') {
            backslashCount++
            j--
          }
          const isEscaped = backslashCount % 2 === 1
          
          if (!isEscaped) {
            // 字符串结束
            inString = false
            stringChar = null
            result += '"' // 统一使用双引号
          } else {
            // 转义的引号，保持原样
            result += char
          }
        } else if (char === '"' && stringChar === "'") {
          // 在单引号字符串内部遇到双引号，需要转义
          result += '\\"'
        } else if (char === '\\' && nextChar === '"' && stringChar === "'") {
          // 处理已经转义的双引号
          result += '\\\\"'
          i++ // 跳过下一个字符
        } else {
          result += char
        }
      }
      
      i++
    }
    
    console.log('🔍 [safeConvertQuotesStateMachine] 状态机引号转换完成')
    return result
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
  static generateSummary(content, maxLength = 150) {
    if (!content || typeof content !== 'string') {
      return ''
    }

    const cleanContent = content.trim().replace(/\s+/g, ' ')
    
    if (cleanContent.length <= maxLength) {
      return cleanContent
    }

    // 尝试在句号处截断
    const sentences = cleanContent.split(/[。！？.!?]/)
    let summary = ''
    
    for (const sentence of sentences) {
      if ((summary + sentence).length > maxLength) {
        break
      }
      summary += sentence + '。'
    }

    if (summary.length === 0) {
      // 如果没有合适的句号，直接截断
      summary = cleanContent.substring(0, maxLength) + '...'
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
}

export default SearchContentParser
