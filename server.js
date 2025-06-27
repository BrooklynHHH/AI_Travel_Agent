const express = require('express');
const path = require('path');
const os = require('os');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');
const readline = require('readline');

const app = express();

// 解析命令行参数
const args = process.argv.slice(2);
let PORT = process.env.PORT || 3001;

// 查找--port参数
const portIndex = args.indexOf('--port');
if (portIndex !== -1 && portIndex + 1 < args.length) {
  const portValue = args[portIndex + 1];
  if (portValue && !isNaN(parseInt(portValue))) {
    PORT = parseInt(portValue);
    console.log(`使用命令行指定的端口: ${PORT}`);
  }
}

// Mify API配置
const MIFY_API_KEY = 'app-O7w2lF9yDCUjuEl3M6DJoUzm';
const MIFY_API_URL = 'https://mify-be.pt.xiaomi.com/api/v1';
// 不同工作流的应用ID
const TAROT_APP_ID = 'app-LowxiZTrY0htW4CtKvh8PLFE'; // 塔罗牌应用ID
const FORTUNE_APP_ID = 'app-O7w2lF9yDCUjuEl3M6DJoUzm'; // 命理分析应用ID

console.log('正在初始化服务器...');

app.use(cors());

// 解析JSON请求体
app.use(bodyParser.json());

// 请求日志中间件
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

console.log('中间件设置完成');

// 在中间件设置完成之后、路由定义之前插入通用工具函数
function processMifyStreamLine(line, res, sessionId = '') {
  // 忽略空行
  if (!line || !line.trim()) return;

  // 去掉可能存在的 "data: " 前缀
  let jsonStr = line.startsWith('data: ') ? line.slice(6).trim() : line.trim();

  // 跳过 SSE 的事件描述行，例如 "event: ping"
  if (jsonStr.startsWith('event:')) {
    return;
  }

  // 过滤 SSE 注释或结束标记
  if (jsonStr === '' || jsonStr === '[DONE]' || jsonStr.startsWith(':')) {
    if (jsonStr === '[DONE]') {
      res.write(`data: [DONE]\n\n`);
    }
    return;
  }

  try {
    const mifyData = JSON.parse(jsonStr);
    if (mifyData.event === 'ping') {
      return; // 心跳包，直接跳过
    }

    // 兼容多种字段名，取到文本片段
    const textSegment = mifyData.data || mifyData.answer || mifyData.text || mifyData.content || '';

    // 重新封装为前端期望的数据格式
    const responseData = {
      event: 'message',
      conversation_id: mifyData.conversation_id || sessionId,
      data: textSegment,
      answer: textSegment,
      metadata: mifyData.metadata || undefined
    };

    // 推送给前端
    res.write(`data: ${JSON.stringify(responseData)}\n\n`);
  } catch (err) {
    console.error('解析 Mify 行失败:', err, '原始行:', jsonStr);
  }
}

// 路由设置 - 注意：在Vue项目中，根路由由Vue Router处理
// app.get('/', (req, res) => {
//   console.log('收到首页请求');
//   res.sendFile(path.join(__dirname, 'public', 'index.html'));
// });

// 大师群聊API路由
app.post('/api/masters-chat', async (req, res) => {
  console.log('收到大师群聊请求，完整请求体:', JSON.stringify(req.body));
  const { query, knowledge_base, conversation_id, user: frontendUser, user_info, workflow_type } = req.body || {};
  if (!query) {
    if (!res.headersSent) {
      res.status(400).json({
        event: 'error',
        error: '参数错误',
        message: '缺少必要参数: query'
      });
    }
    return;
  }
  // 构建包含知识库的详细查询
  const detailedQuery = `
大师讨论：

    用户信息：
姓名：${knowledge_base?.user_info?.name || '未知'}
性别：${knowledge_base?.user_info?.gender || '未知'}
生日：${knowledge_base?.user_info?.birthday || '未知'}
出生地：${knowledge_base?.user_info?.birth_place || '未知'}

之前的分析结果：
星座分析：${JSON.stringify(knowledge_base?.analysis_results?.xingzuo || {})}
八字分析：${JSON.stringify(knowledge_base?.analysis_results?.bazi || {})}
星盘分析：${JSON.stringify(knowledge_base?.analysis_results?.xingpan || {})}
塔罗分析：${knowledge_base?.analysis_results?.tarot || ''}

请四位大师（星座大师、八字大师、星盘大师、塔罗大师）基于以上信息进行三轮讨论。

输出格式要求：
你必须以JSON格式输出，格式如下：
{
  "master_messages": [
    {"master_tag": "xzdashi", "content": "星座大师的发言内容"},
    {"master_tag": "bzdashi", "content": "八字大师的发言内容"},
    {"master_tag": "xpdashi", "content": "星盘大师的发言内容"},
    {"master_tag": "tldashi", "content": "塔罗大师的发言内容"}
  ]
}

每位大师必须发言，内容要专业、有深度，且与用户信息和分析结果相关。
不要输出任何其他内容，只输出上述JSON格式。

${query}
    `;
  const requestBody = {
    app_id: FORTUNE_APP_ID,
    inputs: {},
    query: detailedQuery,
    response_mode: "streaming",
    conversation_id: conversation_id || "",
    user: frontendUser || user_info?.id || "masters-user",
    files: []
  };
  console.log('发送到Mify的大师群聊请求体:', JSON.stringify(requestBody));
  res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  let textContent = '';
  try {
    const response = await axios({
      method: 'post',
      url: `${MIFY_API_URL}/chat-messages`,
      data: requestBody,
      headers: {
        'Authorization': `Bearer ${MIFY_API_KEY}`,
        'Content-Type': 'application/json'
      },
      responseType: 'stream',
      timeout: 200000
    });
    const rl = readline.createInterface({ input: response.data });
    rl.on('line', (line) => {
      if (!line || !line.trim()) return;
      let jsonStr = line.startsWith('data: ') ? line.slice(6).trim() : line.trim();
      if (jsonStr === '' || jsonStr === '[DONE]' || jsonStr.startsWith(':') || jsonStr.startsWith('event:')) return;
      try {
        const mifyData = JSON.parse(jsonStr);
        if (mifyData.event === 'ping') return;
        if (mifyData.answer) {
          textContent += mifyData.answer;
          // 实时推送：尝试解析 answer，推送 master_messages
          let masterMessages = null;
          try {
            const parsed = JSON.parse(mifyData.answer);
            if (parsed.master_messages && Array.isArray(parsed.master_messages)) {
              masterMessages = parsed.master_messages;
            }
          } catch (e) {}
          const streamData = {
            event: 'message',
            conversation_id: mifyData.conversation_id || conversation_id || '',
            data: '',
            answer: mifyData.answer,
            metadata: {}
          };
          if (masterMessages) {
            streamData.metadata.master_messages = masterMessages;
          }
          res.write(`data: ${JSON.stringify(streamData)}\n\n`);
        }
      } catch (err) {
        // 忽略解析失败
      }
    });
    rl.on('close', () => {
      // 结束时依然尝试提取 master_messages
      let masterMessages = null;
      try {
        const match = textContent.match(/\{[\s\S]*?"master_messages"[\s\S]*?\}/);
        if (match) {
          const parsed = JSON.parse(match[0]);
          if (parsed.master_messages && Array.isArray(parsed.master_messages)) {
            masterMessages = parsed.master_messages;
          }
        }
      } catch (e) {}
      const responseData = {
        event: 'message',
        conversation_id: conversation_id || '',
        data: '',
        answer: textContent,
        metadata: {}
      };
      if (masterMessages) {
        responseData.metadata.master_messages = masterMessages;
      }
      res.write(`data: ${JSON.stringify(responseData)}\n\n`);
      res.write(`data: [DONE]\n\n`);
      res.end();
    });
    response.data.on('error', (err) => {
      console.error('Mify响应流错误:', err.message);
      const errorData = {
        event: "error",
        error: "stream_error",
        message: err.message,
        details: "流数据处理错误"
      };
      res.write(`data: ${JSON.stringify(errorData)}\n\n`);
      res.end();
    });
    req.on('close', () => {
      rl.close();
      response.data.destroy();
    });
    // 处理 readline 错误，避免未捕获异常导致服务器崩溃
    rl.on('error', (err) => {
      console.error('readline error (masters-chat):', err.message);
      const errorData = {
        event: 'error',
        error: 'stream_error',
        message: err.message,
        details: 'readline_interface_error'
      };
      if (!res.headersSent) {
        res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
      }
      res.write(`data: ${JSON.stringify(errorData)}\n\n`);
      res.end();
    });
  } catch (error) {
    console.error('调用Mify API出错 (masters-chat):', error.message);
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    const errObj = {
      event: 'error',
      error: '调用AI服务失败',
      message: error.message || '服务器内部错误，请稍后再试',
      details: error.code || '未知错误'
    };
    res.write(`data: ${JSON.stringify(errObj)}\n\n`);
    res.end();
  }
});


// 命理分析API路由
app.post('/api/fortune', async (req, res) => {
  console.log('收到命理分析请求:', JSON.stringify(req.body));
  const { name, gender, birthday, birth_place, user_info } = req.body;
  if (!name || !gender || !birthday || !birth_place || !user_info) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const query = `请根据以下信息进行命理分析：\n姓名：${name}\n性别：${gender}\n出生年月：${birthday}\n出生地点：${birth_place}\n\n请分别提供以下内容，并使用明确的标记格式：\n1. 星座分析：\n【xingzuo-zongjie】(在这里提供星座分析的的分析，四句话，100字左右)\n【xingzuo-fenxi】(在这里提供星座分析的详细分析)\n2. 八字命理：\n【bazi-zongjie】(在这里提供八字命理的分析，四句话，100字左右)\n【bazi-fenxi】(在这里提供八字命理的详细分析)\n3. 星盘解析：\n【xingpan-zongjie】(在这里提供星盘解析的的分析，四句话，100字左右)\n【xingpan-fenxi】(在这里提供星盘解析的详细分析)\n请严格按照上述格式提供内容，确保每个标记部分都有内容，且标记格式为【标记名】。每个分析部分的"zongjie"和"fenxi"必须分开标记，不要合并。这对于前端正确显示结果至关重要。`;
  const requestBody = {
    app_id: FORTUNE_APP_ID,
    inputs: { name, gender, birthday, birth_place },
    query,
    response_mode: 'streaming',
    conversation_id: '',
    user: user_info.id,
    files: []
  };
  console.log('发送到Mify的命理分析请求体:', JSON.stringify(requestBody));
  res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  try {
    const response = await axios({
      method: 'post',
      url: `${MIFY_API_URL}/chat-messages`,
      data: requestBody,
      headers: {
        'Authorization': `Bearer ${MIFY_API_KEY}`,
        'Content-Type': 'application/json'
      },
      responseType: 'stream',
      timeout: 200000
    });
    const rl = readline.createInterface({ input: response.data });
    rl.on('line', (line) => {
      processMifyStreamLine(line, res, '');
    });
    rl.on('close', () => {
      res.end();
    });
    response.data.on('error', (err) => {
      console.error('Mify响应流错误:', err.message);
      const errorData = {
        event: "error",
        error: "stream_error",
        message: err.message,
        details: "流数据处理错误"
      };
      res.write(`data: ${JSON.stringify(errorData)}\n\n`);
      res.end();
    });
    req.on('close', () => {
      rl.close();
      response.data.destroy();
    });
    // 处理 readline 错误，避免未捕获异常导致服务器崩溃
    rl.on('error', (err) => {
      console.error('readline error (fortune):', err.message);
      const errorData = {
        event: 'error',
        error: 'stream_error',
        message: err.message,
        details: 'readline_interface_error'
      };
      if (!res.headersSent) {
        res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
      }
      res.write(`data: ${JSON.stringify(errorData)}\n\n`);
      res.end();
    });
  } catch (error) {
    console.error('调用Mify API出错 (fortune):', error.message);
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    const errObj = {
      event: 'error',
      error: '调用AI服务失败',
      message: error.message || '服务器内部错误，请稍后再试',
      details: error.code || '未知错误'
    };
    res.write(`data: ${JSON.stringify(errObj)}\n\n`);
    res.end();
  }
});

// 通用聊天API路由
app.post('/api/chat', async (req, res) => {
    console.log('收到通用聊天请求:', JSON.stringify(req.body));

    const { query, conversation_id, user_info, workflow_type } = req.body;

    if (!query) {
        return res.status(400).json({ error: 'Missing query' });
    }
    
    const requestBody = {
        query,
        response_mode: 'streaming',
        conversation_id: conversation_id || '',
        user: user_info?.id || 'fortune-user',
        files: []
    };
    
    if (workflow_type === 'tarot') {
      requestBody.app_id = TAROT_APP_ID;
    }

    console.log('发送到Mify的通用聊天请求体:', JSON.stringify(requestBody));

    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // 调用Mify API（流式请求）
    try {
        const response = await axios({
            method: 'post',
            url: `${MIFY_API_URL}/chat-messages`,
            data: requestBody,
            headers: {
                'Authorization': `Bearer ${MIFY_API_KEY}`,
                'Content-Type': 'application/json'
            },
            responseType: 'stream',
            timeout: 200000
        });

        const mifyStream = response.data;

        mifyStream.on('error', (streamError) => {
            console.error('Mify stream error (chat):', streamError);
            if (!res.headersSent) {
                res.status(500).json({ event: 'error', error: 'AI服务流错误', message: streamError.message });
            }
            res.end();
        });

        mifyStream.pipe(res);

    } catch (error) {
        console.error('调用Mify API出错 (chat):', error.message);
        if (!res.headersSent) {
            res.status(500).json({
                event: 'error',
                error: '调用AI服务失败',
                message: error.message
            });
        } else {
            res.end();
        }
    }
});


// 服务器启动
app.listen(PORT, '0.0.0.0', () => {
  const interfaces = os.networkInterfaces();
  console.log(`服务器正在运行在 http://localhost:${PORT}`);
  Object.keys(interfaces).forEach(key => {
    interfaces[key].forEach(details => {
      if (details.family === 'IPv4') {
        console.log(`也可以通过 http://${details.address}:${PORT} 访问`);
      }
    });
  });
}); 