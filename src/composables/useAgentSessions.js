import { reactive, computed, nextTick, ref } from 'vue'

// 智能体角色优先级配置（固定排序）
const AGENT_ROLE_ORDER = {
  'supervisor': 1,
  'tour_search_agent': 2,
  'day_plan_agent': 3,
  'live_transport_agent': 4,
  'travel_butler_agent': 5,
  'tools': 6,
  'unified_stream': 7
}

// 智能体配置
const AGENT_CONFIG = {
  'supervisor': { 
    key: 'supervisor',
    name: '总指挥官', 
    icon: '🎯', 
    color: '#2563eb',
    description: '分析需求，制定策略',
    roleOrder: AGENT_ROLE_ORDER.supervisor
  },
  'tour_search_agent': { 
    key: 'tour_search_agent',
    name: '景点搜索专家', 
    icon: '🔍', 
    color: '#059669',
    description: '搜索景点和活动',
    roleOrder: AGENT_ROLE_ORDER.tour_search_agent
  },
  'day_plan_agent': { 
    key: 'day_plan_agent',
    name: '行程规划师', 
    icon: '📅', 
    color: '#ea580c',
    description: '制定详细行程',
    roleOrder: AGENT_ROLE_ORDER.day_plan_agent
  },
  'live_transport_agent': { 
    key: 'live_transport_agent',
    name: '交通住宿专家', 
    icon: '🚗', 
    color: '#7c3aed',
    description: '规划交通和住宿',
    roleOrder: AGENT_ROLE_ORDER.live_transport_agent
  },
  'travel_butler_agent': { 
    key: 'travel_butler_agent',
    name: '贴心旅行管家', 
    icon: '🎒', 
    color: '#db2777',
    description: '提供贴心建议',
    roleOrder: AGENT_ROLE_ORDER.travel_butler_agent
  },
  'tools': { 
    key: 'tools',
    name: '工具调用', 
    icon: '🔧', 
    color: '#6b7280',
    description: '执行API调用',
    roleOrder: AGENT_ROLE_ORDER.tools
  },
  'unified_stream': {
    key: 'unified_stream',
    name: '流式输出',
    icon: '📡',
    color: '#4299e1',
    description: '统一流式输出显示',
    roleOrder: AGENT_ROLE_ORDER.unified_stream
  }
}

export function useAgentSessions() {
  // 对话轮次数据 - 新的核心数据结构
  const conversationTurns = reactive({})
  
  // 当前活跃的轮次ID
  const currentTurnId = ref(null)
  
  // 轮次计数器
  const turnCounter = ref(0)
  
  // 工具调用去重缓存（按轮次隔离）
  const processedToolCalls = reactive({})
  
  // 焦点区状态管理
  const focusedAgent = ref(null)
  const focusQueue = ref([]) // 等待进入焦点区的智能体队列
  const lastActiveAgent = ref(null) // 最新活跃的智能体
  const lastActiveTime = ref(null) // 最新活跃时间
  
  // 兼容性：保持原有的agentSessions引用（指向当前轮次）
  const agentSessions = computed(() => {
    if (!currentTurnId.value || !conversationTurns[currentTurnId.value]) {
      return {}
    }
    return conversationTurns[currentTurnId.value].agentSessions
  })
  
  // 生成唯一ID
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }


  // 获取智能体配置 - 深拷贝防止引用污染
  const getAgentConfig = (agentKey) => {
    const config = AGENT_CONFIG[agentKey] || { 
      key: agentKey,
      name: agentKey, 
      icon: '🤖', 
      color: '#6b7280',
      description: '未知智能体'
    }
    
    // 深拷贝配置对象，确保每个会话都有独立的配置实例
    return JSON.parse(JSON.stringify(config))
  }

  // 生成轮次ID
  const generateTurnId = () => {
    turnCounter.value++
    const timestamp = Date.now()
    return `turn_${turnCounter.value}_${timestamp}`
  }

  // 创建新的对话轮次
  const createNewTurn = (userMessage = '') => {
    const turnId = generateTurnId()
    
    conversationTurns[turnId] = {
      turnId,
      userMessage,
      timestamp: Date.now(),
      status: 'active', // active, completed
      agentSessions: {},
      processedToolCalls: new Set()
    }
    
    currentTurnId.value = turnId
    
    // 关键修复：新轮次开始时清除焦点区域，让第一个活跃智能体重新获得焦点
    console.log(`🆕 [新轮次] 创建轮次: ${turnId}，清除上一轮焦点`)
    focusedAgent.value = null
    focusQueue.value = []
    lastActiveAgent.value = null
    lastActiveTime.value = null
    
    return turnId
  }

  // 获取或创建当前轮次的智能体会话
  const getOrCreateAgentSession = (agentKey, turnId = null, forceNew = false) => {
    const targetTurnId = turnId || currentTurnId.value
    
    if (!targetTurnId) {
      console.warn('⚠️ [会话管理] 没有活跃的轮次，创建新轮次')
      createNewTurn()
      return getOrCreateAgentSession(agentKey, currentTurnId.value, forceNew)
    }
    
    const turn = conversationTurns[targetTurnId]
    if (!turn) {
      console.error(`❌ [会话管理] 轮次不存在: ${targetTurnId}`)
      return null
    }
    
    // 检查是否需要创建新会话实例
    if (forceNew) {
      // 为同一智能体创建新的会话实例
      const sessionIndex = Object.keys(turn.agentSessions)
        .filter(key => key.includes(`${targetTurnId}_${agentKey}`))
        .length + 1
      
      const sessionKey = `${targetTurnId}_${agentKey}_${sessionIndex}`
      console.log(`🆕 [新会话实例] 为 ${agentKey} 创建第 ${sessionIndex} 个会话实例`)
      
      turn.agentSessions[sessionKey] = {
        agentInfo: getAgentConfig(agentKey),
        conversations: [],
        isCardCollapsed: false,
        currentStatus: 'waiting',
        streamingContent: '',
        totalDuration: 0,
        lastUpdateTime: Date.now(),
        turnId: targetTurnId,
        agentKey: agentKey,
        uniqueKey: sessionKey,
        createdAt: Date.now(),
        sessionId: generateId(),
        sessionIndex: sessionIndex, // 会话实例序号
        // 新增：智能体完成状态跟踪
        emptyContentCount: 0,
        needNewSessionOnNextContent: false,
        lastContentTime: null
      }
      
      return turn.agentSessions[sessionKey]
    }
    
    // 查找该智能体的最新会话实例
    const existingSessions = Object.entries(turn.agentSessions)
      .filter(([, session]) => session.agentKey === agentKey)
      .sort(([, a], [, b]) => (b.sessionIndex || 1) - (a.sessionIndex || 1))
    
    if (existingSessions.length > 0) {
      const [, latestSession] = existingSessions[0]
      
      // 如果最新会话标记需要新会话，则创建新的
      if (latestSession.needNewSessionOnNextContent) {
        return getOrCreateAgentSession(agentKey, turnId, true)
      }
      
      return latestSession
    }
    
    // 首次创建会话
    const sessionKey = `${targetTurnId}_${agentKey}_1`
    turn.agentSessions[sessionKey] = {
      agentInfo: getAgentConfig(agentKey),
      conversations: [],
      isCardCollapsed: false,
      currentStatus: 'waiting',
      streamingContent: '',
      totalDuration: 0,
      lastUpdateTime: Date.now(),
      turnId: targetTurnId,
      agentKey: agentKey,
      uniqueKey: sessionKey,
      createdAt: Date.now(),
      sessionId: generateId(),
      sessionIndex: 1,
      // 新增：智能体完成状态跟踪
      emptyContentCount: 0,
      needNewSessionOnNextContent: false,
      lastContentTime: null
    }
    
    return turn.agentSessions[sessionKey]
  }

  // 开始新的对话轮次
  const startNewConversation = (agentKey) => {
    const session = getOrCreateAgentSession(agentKey)
    
    // 深度克隆创建完全独立的对话对象
    const conversation = {
      id: generateId(),
      timestamp: Date.now(),
      startTime: Date.now(),
      endTime: null,
      content: '', // 独立的字符串实例
      status: 'streaming',
      isCollapsed: false,
      // 添加对话级别的唯一标识
      conversationId: generateId(),
      turnId: session.turnId,
      agentKey: agentKey
    }
    
    // 确保conversations数组是独立的
    if (!Array.isArray(session.conversations)) {
      session.conversations = []
    }
    session.conversations.push(conversation)
    session.currentStatus = 'streaming'
    session.streamingContent = '' // 重置流式内容
    
    return conversation
  }

  // 更新流式内容 - 严格的轮次隔离
  const updateStreamingContent = async (agentKey, content, isIncremental = true) => {
    // 关键修复：强制使用当前轮次，防止跨轮次污染
    const session = getOrCreateAgentSession(agentKey, currentTurnId.value)
    
    if (!session) {
      console.error(`❌ [内容更新] 无法获取会话: ${agentKey} 在轮次 ${currentTurnId.value}`)
      return
    }
    
    // 验证会话归属，确保不会更新错误的轮次
    if (session.turnId !== currentTurnId.value) {
      console.error(`❌ [内容更新] 轮次不匹配: 期望 ${currentTurnId.value}, 实际 ${session.turnId}`)
      return
    }
    
    // 创建新的字符串实例，避免引用污染
    if (isIncremental) {
      // 增量更新：创建新字符串
      session.streamingContent = (session.streamingContent || '') + content
    } else {
      // 全量更新：创建新字符串
      session.streamingContent = String(content)
    }
    
    session.currentStatus = 'streaming'
    // 🔑 注意：这里的 lastUpdateTime 会被 handleAgentContentUpdate 中的时间戳覆盖
    // 所以我们不在这里更新，避免时间戳不一致
    // session.lastUpdateTime = Date.now()
    
    // 如果有活跃的对话轮次，也更新其内容（同样创建新字符串）
    const activeConversation = session.conversations.find(conv => 
      conv.status === 'streaming' && 
      conv.turnId === currentTurnId.value
    )
    
    if (activeConversation) {
      if (isIncremental) {
        activeConversation.content = (activeConversation.content || '') + content
      } else {
        activeConversation.content = String(content)
      }
    }
    
    await nextTick()
  }

  // 完成当前对话轮次
  const completeConversation = (agentKey, finalContent = null) => {
    const session = getOrCreateAgentSession(agentKey)
    
    // 找到当前活跃的对话轮次
    const activeConversation = session.conversations.find(conv => conv.status === 'streaming')
    
    if (activeConversation) {
      activeConversation.status = 'completed'
      activeConversation.endTime = Date.now()
      
      // 如果提供了最终内容，使用最终内容；否则使用流式内容
      if (finalContent !== null) {
        activeConversation.content = finalContent
        // 同时更新 streamingContent 以便焦点区显示
        session.streamingContent = finalContent
      } else if (session.streamingContent) {
        activeConversation.content = session.streamingContent
      }
    }
    
    // 更新会话状态
    session.currentStatus = 'completed'
    // 关键修改：不清空 streamingContent，保持内容供焦点区显示
    // session.streamingContent = ''
    session.lastUpdateTime = Date.now()
    
    // 计算总持续时间
    session.totalDuration = session.conversations.reduce((total, conv) => {
      if (conv.endTime && conv.startTime) {
        return total + (conv.endTime - conv.startTime)
      }
      return total
    }, 0)
  }

  // 焦点区管理方法
  const setFocusedAgent = (agentKey) => {
    if (agentKey && agentKey !== 'tools' && agentKey !== 'unified_stream') {
      const session = getOrCreateAgentSession(agentKey)
      if (session) {
        focusedAgent.value = session
        console.log(`🎯 [焦点区] 设置焦点智能体: ${agentKey}`)
      }
    }
  }

  const clearFocusedAgent = (agentKey = null) => {
    if (!agentKey || (focusedAgent.value && focusedAgent.value.agentKey === agentKey)) {
      console.log(`🎯 [焦点区] 清除焦点智能体: ${agentKey || 'all'}`)
      focusedAgent.value = null
      
      // 处理队列中的下一个智能体
      if (focusQueue.value.length > 0) {
        const nextAgent = focusQueue.value.shift()
        setFocusedAgent(nextAgent)
      }
    }
  }

  const addToFocusQueue = (agentKey) => {
    if (agentKey && agentKey !== 'tools' && agentKey !== 'unified_stream') {
      if (!focusQueue.value.includes(agentKey)) {
        focusQueue.value.push(agentKey)
        console.log(`📋 [焦点队列] 添加智能体: ${agentKey}`)
      }
    }
  }

  // 处理智能体开始工作
  const handleAgentStart = (agentKey) => {
    console.log(`🎯 [智能体启动] ${agentKey}`)
    
    // 🔑 关键修改：不在启动时立即创建会话，等到有实际内容时再创建
    // 这样可以避免创建空内容的卡片
    
    // 简化的焦点区管理：只在没有焦点智能体时设置初始焦点
    // 后续的焦点切换将由 handleAgentContentUpdate 处理
    if (agentKey !== 'tools' && agentKey !== 'unified_stream') {
      if (!focusedAgent.value) {
        console.log(`🎯 [初始焦点] 设置初始焦点智能体: ${agentKey}`)
        // 延迟设置焦点，等到有内容时再设置
        // setFocusedAgent(agentKey)
      }
    }
  }


  // 处理智能体内容更新
  const handleAgentContentUpdate = async (agentKey, content, isIncremental = true) => {
    console.log(`📝 [内容更新] ${agentKey}: ${content.length} 字符`)
    
    // 🔑 关键修改：如果内容为空，直接返回，不创建任何会话或卡片
    if (!content || content.trim() === '') {
      console.log(`🚫 [跳过空内容] ${agentKey} 内容为空，不创建卡片`)
      return
    }
    
    // 关键修复：确保内容更新只影响当前轮次
    const session = getOrCreateAgentSession(agentKey, currentTurnId.value)
    if (!session) {
      console.warn(`⚠️ [内容更新] 无法获取智能体会话: ${agentKey}`)
      return
    }
    
    // 检查是否需要创建新会话实例
    if (session.needNewSessionOnNextContent) {
      console.log(`🆕 [新会话] ${agentKey} 需要创建新会话实例`)
      
      // 创建新的会话实例
      getOrCreateAgentSession(agentKey, currentTurnId.value, true)
      
      // 重置标记
      session.needNewSessionOnNextContent = false
      
      console.log(`✨ [新卡片] ${agentKey} 已创建新的输出卡片`)
    }
    
    // 确保有活跃的对话
    const activeConversation = session.conversations.find(conv => conv.status === 'streaming')
    if (!activeConversation) {
      startNewConversation(agentKey)
    }
    
    // 🔑 关键修复：更新最新活跃智能体和时间戳
    const currentTime = Date.now()
    lastActiveAgent.value = agentKey
    lastActiveTime.value = currentTime
    
    // 🔑 关键修复：同步更新会话的lastUpdateTime，确保动态排序生效
    session.lastUpdateTime = currentTime
    
    // 新增：焦点区动态切换逻辑 - 实时跟随最新活跃的智能体
    if (agentKey !== 'tools' && agentKey !== 'unified_stream') {
      // 如果当前智能体不在焦点区，立即切换
      if (!focusedAgent.value || focusedAgent.value.agentKey !== agentKey) {
        console.log(`🎯 [焦点切换] 从 ${focusedAgent.value?.agentKey || 'null'} 切换到 ${agentKey}`)
        setFocusedAgent(agentKey)
      }
    }
    
    await updateStreamingContent(agentKey, content, isIncremental)
    
    console.log(`🔄 [动态排序] ${agentKey} 的 lastUpdateTime 已更新为: ${currentTime}`)
  }

  // 处理智能体完成
  const handleAgentComplete = (agentKey, finalContent = null) => {
    console.log(`✅ [智能体完成] ${agentKey}`)
    
    completeConversation(agentKey, finalContent)
    
    // 焦点区管理：智能体完成时的处理
    if (agentKey !== 'tools' && agentKey !== 'unified_stream') {
      // 检查是否还有其他正在工作的智能体
      const currentTurn = conversationTurns[currentTurnId.value]
      if (currentTurn) {
        const activeAgents = Object.values(currentTurn.agentSessions)
          .filter(session => 
            session.currentStatus === 'streaming' && 
            session.agentKey !== 'tools' && 
            session.agentKey !== 'unified_stream'
          )
        
        if (activeAgents.length > 0) {
          // 还有其他智能体在工作，不清除焦点区
          console.log(`🎯 [焦点保持] ${agentKey} 已完成，但还有 ${activeAgents.length} 个智能体在工作`)
        } else {
          // 没有其他智能体在工作了，保持当前焦点智能体显示完整内容
          if (focusedAgent.value && focusedAgent.value.agentKey === agentKey) {
            console.log(`🎯 [焦点保持] ${agentKey} 是最后完成的智能体，保持显示其完整内容`)
            // 不清除焦点，让用户看到最终结果
          }
        }
      }
    }
  }

  // 处理工具调用（支持多卡片创建）
  const handleToolCall = async (toolName, content, options = {}) => {
    const { mode = 'new_card', toolType = 'unknown' } = options
    const agentKey = 'tools'
    
    if (!currentTurnId.value) {
      console.warn('⚠️ [工具调用] 没有活跃轮次，创建新轮次')
      createNewTurn()
    }
    
    const turn = conversationTurns[currentTurnId.value]
    if (!turn) {
      console.error('❌ [工具调用] 当前轮次不存在')
      return
    }
    
    // 🔑 关键改进：每次工具调用都创建新的记录，不进行去重
    const toolCallHash = `${toolName}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 标记为已处理（仅在当前轮次）
    turn.processedToolCalls.add(toolCallHash)
    
    console.log(`🔧 [工具调用] ${toolName} (${mode}模式): ${content.length} 字符`)
    
    const session = getOrCreateAgentSession(agentKey)
    
    // 🔑 关键改进：每次工具调用都创建新的对话记录
    const timestamp = Date.now()
    const toolCallConversation = {
      id: generateId(),
      timestamp: timestamp,
      startTime: timestamp,
      endTime: timestamp, // 工具调用立即完成
      content: content, // 工具调用的完整内容
      status: 'completed', // 工具调用状态为已完成
      isCollapsed: false,
      // 工具调用特有的元数据
      toolCallMetadata: {
        toolName,
        toolType,
        timestamp,
        mode,
        callIndex: session.conversations.length + 1 // 调用序号
      },
      // 添加对话级别的唯一标识
      conversationId: generateId(),
      turnId: session.turnId,
      agentKey: agentKey,
      // 标记这是一个工具调用记录
      isToolCall: true
    }
    
    // 确保conversations数组是独立的
    if (!Array.isArray(session.conversations)) {
      session.conversations = []
    }
    
    // � 关键改进：直接添加新的工具调用记录，不替换现有内容
    session.conversations.push(toolCallConversation)
    
    // 更新会话状态
    session.currentStatus = 'completed' // 工具调用会话状态
    session.lastUpdateTime = timestamp
    
    // 🔑 关键改进：更新streamingContent为最新的工具调用内容（用于焦点区显示）
    session.streamingContent = content
    
    console.log(`✅ [工具调用] 创建新的工具调用卡片 #${toolCallConversation.toolCallMetadata.callIndex}`)
    
    return toolCallConversation
  }

  // 切换卡片折叠状态
  const toggleCardCollapse = (agentKey, isCollapsed) => {
    // 修复：使用 getOrCreateAgentSession 确保获取正确的会话
    const session = getOrCreateAgentSession(agentKey)
    if (session) {
      session.isCardCollapsed = isCollapsed
    }
  }

  // 切换对话轮次折叠状态
  const toggleConversationCollapse = (agentKey, conversationId) => {
    // 修复：使用 getOrCreateAgentSession 确保获取正确的会话
    const session = getOrCreateAgentSession(agentKey)
    if (session) {
      const conversation = session.conversations.find(conv => conv.id === conversationId)
      if (conversation) {
        conversation.isCollapsed = !conversation.isCollapsed
      }
    }
  }

  // 复制内容
  const handleCopyContent = (agentKey, content) => {
    console.log(`📋 [复制内容] ${agentKey}: ${content.length} 字符`)
    // 这里可以添加复制成功的提示
  }

  // 完成当前轮次
  const completeTurn = (turnId = null) => {
    const targetTurnId = turnId || currentTurnId.value
    if (!targetTurnId) return
    
    const turn = conversationTurns[targetTurnId]
    if (turn) {
      turn.status = 'completed'
      
      // 完成该轮次中所有活跃的智能体会话
      Object.values(turn.agentSessions).forEach(session => {
        if (session.currentStatus === 'streaming') {
          // 修复：使用 session.agentKey 而不是 session.agentInfo.key
          completeConversation(session.agentKey)
        }
      })
      
      console.log(`✅ [轮次完成] 轮次 ${targetTurnId} 已完成`)
    }
  }

  // 重置所有会话
  const resetAllSessions = () => {
    // 清空所有轮次数据
    Object.keys(conversationTurns).forEach(key => {
      delete conversationTurns[key]
    })
    
    // 重置状态
    currentTurnId.value = null
    turnCounter.value = 0
    
    // 清空工具调用缓存
    Object.keys(processedToolCalls).forEach(key => {
      delete processedToolCalls[key]
    })
    
    console.log('🔄 [重置会话] 所有轮次和智能体会话已重置')
  }

  // 获取所有轮次（按时间倒序）
  const allConversationTurns = computed(() => {
    return Object.values(conversationTurns)
      .sort((a, b) => b.timestamp - a.timestamp)
  })

  // 获取所有活跃的智能体会话（按最后更新时间排序）
  const activeAgentSessions = computed(() => {
    return Object.values(agentSessions.value)
      .filter(session => session.conversations.length > 0)
      .sort((a, b) => b.lastUpdateTime - a.lastUpdateTime)
  })

  // 获取当前正在流式输出的智能体数量
  const streamingAgentsCount = computed(() => {
    return Object.values(agentSessions.value)
      .filter(session => session.currentStatus === 'streaming').length
  })

  // 获取总对话轮次数
  const totalConversationsCount = computed(() => {
    return Object.values(agentSessions.value)
      .reduce((total, session) => total + session.conversations.length, 0)
  })

  // 获取按轮次分组的智能体会话（使用动态重排序）
  const agentSessionsByTurn = computed(() => {
    const result = {}
    
    // 按时间顺序排序轮次（最早的在前，最新的在后）
    const sortedTurns = Object.values(conversationTurns)
      .sort((a, b) => a.timestamp - b.timestamp)
    
    sortedTurns.forEach(turn => {
      // 🔑 关键修改：分别处理智能体和工具，然后合并
      const allSessions = Object.values(turn.agentSessions)
        .filter(session => session.turnId === turn.turnId)
      
      // 🔑 关键修改：过滤掉没有内容的会话（空内容的卡片不显示）
      const sessionsWithContent = allSessions.filter(session => {
        // 检查是否有实际内容
        const hasContent = session.streamingContent && session.streamingContent.trim() !== ''
        const hasValidConversations = session.conversations && session.conversations.some(conv => 
          conv.content && conv.content.trim() !== ''
        )
        
        return hasContent || hasValidConversations
      })
      
      // 分离智能体和工具会话
      const agentSessions = sessionsWithContent.filter(session => 
        session.agentKey !== 'tools' && session.agentKey !== 'unified_stream'
      )
      const toolSessions = sessionsWithContent.filter(session => 
        session.agentKey === 'tools' || session.agentKey === 'unified_stream'
      )
      
      // 🔑 对智能体会话进行动态排序 - 最新活跃的排在最后
      const sortedAgentSessions = agentSessions.sort((a, b) => {
        // 首先按照最后更新时间排序，最新的在后面
        const timeA = a.lastUpdateTime || a.createdAt || 0
        const timeB = b.lastUpdateTime || b.createdAt || 0
        
        console.log(`🔄 [排序调试] ${a.agentKey}: ${timeA}, ${b.agentKey}: ${timeB}`)
        
        // 如果时间相同，则按照角色顺序排序
        if (Math.abs(timeA - timeB) < 1000) { // 1秒内认为是相同时间
          const orderA = a.agentInfo.roleOrder || 999
          const orderB = b.agentInfo.roleOrder || 999
          console.log(`🔄 [排序调试] 时间相近，使用角色顺序: ${a.agentKey}(${orderA}) vs ${b.agentKey}(${orderB})`)
          return orderA - orderB
        }
        
        console.log(`🔄 [排序调试] 按时间排序: ${timeA < timeB ? a.agentKey + ' < ' + b.agentKey : a.agentKey + ' > ' + b.agentKey}`)
        return timeA - timeB
      })
      
      // 🔑 对工具会话按最后更新时间排序（最新的在后面）
      const sortedToolSessions = toolSessions.sort((a, b) => {
        const timeA = a.lastUpdateTime || a.createdAt || 0
        const timeB = b.lastUpdateTime || b.createdAt || 0
        return timeA - timeB
      })
      
      // 🔑 合并：智能体在前，工具在后，但都按最新更新时间排序（最新的在最后）
      const finalSessions = [...sortedAgentSessions, ...sortedToolSessions]
      
      console.log(`🔄 [最终排序] 轮次 ${turn.turnId} 的会话顺序:`, 
        finalSessions.map(s => `${s.agentKey}(${s.lastUpdateTime || s.createdAt})`))
      
      // 关键修改：只有当有实际会话时才显示轮次容器
      if (finalSessions.length > 0) {
        result[turn.turnId] = {
          turnInfo: {
            turnId: turn.turnId,
            userMessage: turn.userMessage,
            timestamp: turn.timestamp,
            status: turn.status
          },
          sessions: finalSessions // 现在按动态顺序排列，最新的在最后
        }
      }
    })
    
    return result
  })

  // 焦点区相关计算属性
  const showFocusArea = computed(() => !!focusedAgent.value)
  
  const focusedAgentInfo = computed(() => {
    return focusedAgent.value ? {
      agentKey: focusedAgent.value.agentKey,
      agentInfo: focusedAgent.value.agentInfo,
      streamingContent: focusedAgent.value.streamingContent,
      currentStatus: focusedAgent.value.currentStatus
    } : null
  })

  return {
    // 核心数据
    conversationTurns,
    currentTurnId,
    agentSessions,
    
    // 计算属性
    allConversationTurns,
    activeAgentSessions,
    streamingAgentsCount,
    totalConversationsCount,
    agentSessionsByTurn,
    
    // 焦点区状态
    focusedAgent,
    focusQueue,
    showFocusArea,
    focusedAgentInfo,
    
    // 轮次管理方法
    createNewTurn,
    completeTurn,
    
    // 智能体会话方法
    getAgentConfig,
    getOrCreateAgentSession,
    startNewConversation,
    updateStreamingContent,
    completeConversation,
    handleAgentStart,
    handleAgentContentUpdate,
    handleAgentComplete,
    handleToolCall,
    
    // 焦点区管理方法
    setFocusedAgent,
    clearFocusedAgent,
    addToFocusQueue,
    
    // 交互方法
    toggleCardCollapse,
    toggleConversationCollapse,
    handleCopyContent,
    resetAllSessions,
    
    // 工具方法
    generateId,
    generateTurnId
  }
}
