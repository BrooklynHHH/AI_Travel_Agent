const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 9051,
    proxy: {
      '/baidu-proxy': {
        target: 'https://www.baidu.com',
        changeOrigin: true,
        pathRewrite: {
          '^/baidu-proxy': ''
        },
        headers: {
          Referer: 'https://www.baidu.com'
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
        }
      }
    }
  }
})
