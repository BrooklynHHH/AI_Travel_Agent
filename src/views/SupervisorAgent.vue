    // 主要发送消息逻辑
    const sendMessage = async () => {
      if (!userInput.value.trim() || isLoading.value) return

      const userMessage = userInput.value
      userInputHistory.value.push(userMessage)
      
      // 添加用户消息
      addMessage('user', userMessage)
      
      // 清空输入
      userInput.value = ''
      adjustTextareaHeight()
      
      // 设置加载状态
      isLoading.value = true

      try {
        if (isFirstRound.value) {
          // 第一轮：直接分析需求并生成方案
          loadingText.value = '正在分析需求并生成方案...'
          
          try {
            const planningResult = await callTravelPlanningDirect(userMessage)
            currentDraft.value = planningResult
            isFirstRound.value = false
          } catch (planningError) {
            console.error('第一轮规划阶段出错:', planningError)
            addMessage('assistant', `规划阶段遇到问题：${planningError.message}\n\n请检查网络连接或稍后重试。`, 'text')
          }
        } else {
          // 后续轮次：基于反馈优化方案
          loadingText.value = '正在根据您的反馈优化方案...'
          
          try {
            const optimizedResult = await callTravelPlanningFlexibleStream(userMessage, currentDraft.value)
            currentDraft.value = optimizedResult
          } catch (optimizeError) {
            console.error('方案优化阶段出错:', optimizeError)
            addMessage('assistant', `方案优化遇到问题：${optimizeError.message}\n\n当前方案仍然有效，您可以继续使用或稍后重试优化。`, 'text')
          }
        }
      } catch (error) {
        console.error('处理消息时出现未知错误:', error)
        addMessage('assistant', `处理请求时出现未知错误：${error.message}\n\n请稍后重试或联系技术支持。`, 'text')
      } finally {
        isLoading.value = false
      }
    }
