module.exports = {
  transpileDependencies: [],
  devServer: {
    port: 9051,
    proxy: {
      '/baidu-proxy': {
        target: 'https://www.baidu.com',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/baidu-proxy': ''
        },
        // 最简单的请求头设置
        onProxyReq: function(proxyReq, req, res) {
          proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');
          proxyReq.setHeader('Referer', 'https://www.baidu.com/');
          
          // 移除_source=app参数防止干扰
          if (req.url.includes('_source=app')) {
            proxyReq.path = req.url.replace(/[?&]_source=app/, '');
          }
        },
        // 极简响应处理 - 只移除安全头
        onProxyRes: function(proxyRes, req, res) {
          // 仅删除会阻止iframe加载的安全头
          delete proxyRes.headers['x-frame-options'];
          delete proxyRes.headers['content-security-policy'];
          
          // 更改响应类型的日志
          console.log('收到响应:', proxyRes.statusCode, proxyRes.statusMessage);
          console.log('内容类型:', proxyRes.headers['content-type']);
        }
      },
      '/external-proxy': {
        target: 'http://example.com', // 这个仅仅是一个占位符
        changeOrigin: true,
        router: function(req) {
          // 从请求URL中提取目标URL
          // URL格式为: /external-proxy/http://example.com
          const targetUrl = req.url.replace(/^\/external-proxy\//, '');
          return targetUrl;
        },
        pathRewrite: function(path, req) {
          // 移除/external-proxy/前缀
          return path.replace(/^\/external-proxy\/https?:\/\/[^\/]+/, '');
        },
        headers: function(req) {
          // 从原始URL中提取域名，作为Referer
          const match = req.url.match(/^\/external-proxy\/(https?:\/\/[^\/]+)/);
          if (match && match[1]) {
            const originalDomain = match[1]; // 例如 https://example.com
            return {
              Referer: originalDomain
            };
          }
          return {};
        }
      }
    }
  }
}
