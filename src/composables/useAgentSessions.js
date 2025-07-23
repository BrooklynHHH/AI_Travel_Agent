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
  const getOrCreateAgentSession = (agentKey, turnId = null) => {
    const targetTurnId = turnId || currentTurnId.value
    
    if (!targetTurnId) {
      console.warn('⚠️ [会话管理] 没有活跃的轮次，创建新轮次')
      createNewTurn()
      return getOrCreateAgentSession(agentKey, currentTurnId.value)
    }
    
    const turn = conversationTurns[targetTurnId]
    if (!turn) {
      console.error(`❌ [会话管理] 轮次不存在: ${targetTurnId}`)
      return null
    }
    
    // 关键修复：使用轮次+智能体的组合键确保数据隔离
    const sessionKey = `${targetTurnId}_${agentKey}`
    if (!turn.agentSessions[sessionKey]) {
      // 深度克隆创建完全独立的会话对象
      turn.agentSessions[sessionKey] = {
        agentInfo: getAgentConfig(agentKey), // 已经是深拷贝
        conversations: [], // 新数组实例
        isCardCollapsed: false,
        currentStatus: 'waiting', // waiting, streaming, completed
        streamingContent: '', // 独立的字符串
        totalDuration: 0,
        lastUpdateTime: Date.now(),
        turnId: targetTurnId,
        agentKey: agentKey,
        uniqueKey: sessionKey, // 用于Vue的key
        // 添加会话创建时间戳，确保唯一性
        createdAt: Date.now(),
        sessionId: generateId()
      }
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
    session.lastUpdateTime = Date.now()
    
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
    
    const session = getOrCreateAgentSession(agentKey)
    
    // 如果当前没有活跃的对话轮次，创建一个新的
    const activeConversation = session.conversations.find(conv => conv.status === 'streaming')
    if (!activeConversation) {
      startNewConversation(agentKey)
    }
    
    session.currentStatus = 'streaming'
    
    // 简化的焦点区管理：只在没有焦点智能体时设置初始焦点
    // 后续的焦点切换将由 handleAgentContentUpdate 处理
    if (agentKey !== 'tools' && agentKey !== 'unified_stream') {
      if (!focusedAgent.value) {
        console.log(`🎯 [初始焦点] 设置初始焦点智能体: ${agentKey}`)
        setFocusedAgent(agentKey)
      }
    }
  }

  // 处理智能体内容更新
  const handleAgentContentUpdate = async (agentKey, content, isIncremental = true) => {
    console.log(`📝 [内容更新] ${agentKey}: ${content.length} 字符`)
    
    // 关键修复：确保内容更新只影响当前轮次
    const session = getOrCreateAgentSession(agentKey, currentTurnId.value)
    if (!session) {
      console.warn(`⚠️ [内容更新] 无法获取智能体会话: ${agentKey}`)
      return
    }
    
    // 新增：更新最新活跃智能体
    lastActiveAgent.value = agentKey
    lastActiveTime.value = Date.now()
    
    // 新增：焦点区动态切换逻辑 - 实时跟随最新活跃的智能体
    if (agentKey !== 'tools' && agentKey !== 'unified_stream') {
      // 如果当前智能体不在焦点区，立即切换
      if (!focusedAgent.value || focusedAgent.value.agentKey !== agentKey) {
        console.log(`🎯 [焦点切换] 从 ${focusedAgent.value?.agentKey || 'null'} 切换到 ${agentKey}`)
        setFocusedAgent(agentKey)
      }
    }
    
    await updateStreamingContent(agentKey, content, isIncremental)
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

  // 处理工具调用（轮次级别去重）
  const handleToolCall = async (toolName, content) => {
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
    
    // 创建工具调用的唯一标识符
    const toolCallHash = `${toolName}_${content.substring(0, 100)}_${content.length}`
    
    // 检查当前轮次是否已经处理过这个工具调用
    if (turn.processedToolCalls.has(toolCallHash)) {
      console.log(`⚠️ [工具调用去重] 跳过重复的工具调用: ${toolName}`)
      return
    }
    
    // 标记为已处理（仅在当前轮次）
    turn.processedToolCalls.add(toolCallHash)
    
    console.log(`🔧 [工具调用] ${toolName}: ${content.length} 字符`)
    
    // 为工具调用创建特殊的内容格式
    const timestamp = new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    const toolContent = `**[${timestamp}] 工具调用: ${toolName}**\n\n${content}\n\n---\n\n`
    
    const session = getOrCreateAgentSession(agentKey)
    
    // 检查是否有活跃的对话轮次
    let activeConversation = session.conversations.find(conv => conv.status === 'streaming')
    if (!activeConversation) {
      activeConversation = startNewConversation(agentKey)
    }
    
    await updateStreamingContent(agentKey, toolContent, true)
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

  // 获取按轮次分组的智能体会话（使用固定排序）
  const agentSessionsByTurn = computed(() => {
    const result = {}
    
    // 按时间顺序排序轮次（最早的在前，最新的在后）
    const sortedTurns = Object.values(conversationTurns)
      .sort((a, b) => a.timestamp - b.timestamp)
    
    sortedTurns.forEach(turn => {
      // 关键修改：使用固定的角色顺序排序，而不是lastUpdateTime
      const turnSessions = Object.values(turn.agentSessions)
        .filter(session => session.turnId === turn.turnId)
        .sort((a, b) => {
          // 按照预设的角色顺序排序
          const orderA = a.agentInfo.roleOrder || 999
          const orderB = b.agentInfo.roleOrder || 999
          return orderA - orderB
        })
      
      // 关键修改：即使没有智能体会话，也显示轮次容器
      result[turn.turnId] = {
        turnInfo: {
          turnId: turn.turnId,
          userMessage: turn.userMessage,
          timestamp: turn.timestamp,
          status: turn.status
        },
        sessions: turnSessions // 现在按固定顺序排列
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
