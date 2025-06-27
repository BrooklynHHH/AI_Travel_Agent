const BACKEND_URL = 'http://staging-llm.search.miui.srv/agent-fortune';

/**
 * 大師群聊 API
 * @param {Object} params - 請求參數
 * @param {string} params.query - 查詢內容
 * @param {string} params.response_mode - 響應模式 (blocking/streaming)
 * @param {string} params.conversation_id - 對話 ID
 * @param {string} params.user - 用戶標識
 * @param {Array} params.files - 文件列表
 * @returns {Promise} - API 響應
 */
export const mastersChat = async (params) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/masters-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    });
    
    return response; // 直接返回 Response 对象以支持流式读取
  } catch (error) {
    console.error('Error in masters chat API:', error);
    throw error;
  }
};

/**
 * 普通聊天 API
 * @param {Object} params - 請求參數
 * @param {string} params.query - 查詢內容
 * @param {string} params.response_mode - 響應模式 (blocking/streaming)
 * @param {string} params.conversation_id - 對話 ID
 * @param {string} params.user - 用戶標識
 * @param {Array} params.files - 文件列表
 * @returns {Promise} - API 響應
 */
export const chat = async (params) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    });
    
    return response; // 直接返回 Response 对象
  } catch (error) {
    console.error('Error in chat API:', error);
    throw error;
  }
};

/**
 * 算命 API (支持流式響應)
 * @param {Object} params - 請求參數
 * @param {string} params.query - 查詢內容
 * @param {string} params.response_mode - 響應模式 (blocking/streaming)
 * @param {string} params.conversation_id - 對話 ID
 * @param {string} params.user - 用戶標識
 * @param {Array} params.files - 文件列表
 * @returns {Promise} - API 響應
 */
export const fortune = async (params) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/fortune`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    });
    
    return response; // 直接返回 Response 对象
  } catch (error) {
    console.error('Error in fortune API:', error);
    throw error;
  }
};

/**
 * 流式響應處理器
 * @param {Response} response - fetch 響應對象
 * @param {Object} options - 處理選項
 * @returns {Promise} - 處理結果
 */
export const handleFortuneStream = async (response, options = {}) => {
  const {
    onStart = () => {},
    onData = () => {},
    onComplete = () => {},
    onError = () => {},
    debug = false
  } = options;

  try {
    onStart();
    
    if (debug) {
      console.log('Fortune streaming started');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        if (debug) {
          console.log('Fortune streaming completed');
        }
        onComplete();
        break;
      }

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.trim() === '') continue;
        
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          
          if (data === '[DONE]') {
            if (debug) {
              console.log('Fortune streaming done');
            }
            onComplete();
            return;
          }

          try {
            const parsedData = JSON.parse(data);
            onData(parsedData);
          } catch (error) {
            if (debug) {
              console.error('Error parsing stream data:', error);
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error in fortune stream handling:', error);
    onError(error);
  }
};
