module.exports = {
  devServer: {
    port: 1024,
    proxy: {
      '/api/baidu-search': {
        target: 'http://staging-llm.search.miui.srv/baidu-search/v3',
        changeOrigin: true,
        pathRewrite: { '^/api/baidu-search': '' }
      },
      '/api/doubao-chat': {
        target: 'https://open.feedcoopapi.com/agent_api/agent/chat/completion',
        changeOrigin: true,
        secure: false,
        pathRewrite: { '^/api/doubao-chat': '' },
        onProxyReq: (proxyReq, req, res) => {
          if (req.headers['authorization']) {
            proxyReq.setHeader('authorization', req.headers['authorization']);
          }
        }
      },
      '/api/doubao-search': {
        target: 'https://open.feedcoopapi.com/search_api/web_search',
        changeOrigin: true,
        secure: false,
        pathRewrite: { '^/api/doubao-search': '' },
        onProxyReq: (proxyReq, req, res) => {
          if (req.headers['authorization']) {
            proxyReq.setHeader('authorization', req.headers['authorization']);
          }
        }
      }
    }
  }
} 