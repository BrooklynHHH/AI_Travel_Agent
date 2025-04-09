module.exports = {
  transpileDependencies: [],
  devServer: {
    port: 80,
    proxy: {
      '/baidu-proxy': {
        target: 'https://www.baidu.com',
        changeOrigin: true,
        secure: false,
        selfHandleResponse: false, // 不自己处理响应
        pathRewrite: {
          '^/baidu-proxy': ''
        },
        // 简单的请求头设置
        onProxyReq: function(proxyReq, req, res) {
          // 明确告诉服务器不要发送压缩内容
          proxyReq.setHeader('Accept-Encoding', 'identity');
          proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');
          proxyReq.setHeader('Referer', 'https://www.baidu.com/');
        },
        onProxyRes: function(proxyRes, req, res) {
          // 移除安全头
          delete proxyRes.headers['x-frame-options'];
          delete proxyRes.headers['content-security-policy'];
          
          // 打印信息
          console.log('收到响应:', proxyRes.statusCode, proxyRes.statusMessage);
          console.log('内容类型:', proxyRes.headers['content-type']);
        }
      },
      '/external-proxy': {
        target: 'http://example.com',
        changeOrigin: true,
        router: function(req) {
          const targetUrl = req.url.replace(/^\/external-proxy\//, '');
          return targetUrl;
        },
        pathRewrite: function(path, req) {
          return path.replace(/^\/external-proxy\/https?:\/\/[^\/]+/, '');
        }
      }
    }
  }
}
