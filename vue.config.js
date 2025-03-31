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
        headers: function(req) {
          // 如果存在原始referer，使用它，否则默认使用百度域名
          const originalReferer = req.headers.referer;
          // 尝试从referer中提取域名
          let refererDomain = 'https://www.baidu.com';
          if (originalReferer) {
            try {
              const url = new URL(originalReferer);
              refererDomain = `${url.protocol}//${url.host}`;
            } catch (e) {
              // 如果解析失败，使用默认值
            }
          }
          return {
            Referer: refererDomain,
            // 添加Host头，确保百度认为请求来自百度域名
            Host: 'www.baidu.com'
          };
        },
        // 添加响应处理器，修复百度返回中的本地IP链接
        onProxyRes: function(proxyRes, req, res) {
          // 检查是否是来自应用的特殊标记请求
          const isAppRequest = req.url.includes('_source=app');
          
          // 如果不是HTML响应或非应用请求，不处理
          const contentType = proxyRes.headers['content-type'] || '';
          if (!isAppRequest || !contentType.includes('text/html')) {
            return;
          }
          
          // 获取本地服务器的地址
          const localAddress = req.headers.host || 'localhost:9051';
          
          // 设置响应编码处理
          const _write = res.write;
          const _end = res.end;
          
          // 重写响应流，替换本地IP为百度域名
          let responseBody = '';
          
          // 监听数据块
          proxyRes.on('data', (data) => {
            responseBody += data.toString('utf8');
          });
          
          // 在响应结束时处理内容
          proxyRes.on('end', () => {
            // 替换所有形如 http://192.168.31.223:9051/s?... 的链接为 https://www.baidu.com/s?...
            const modifiedBody = responseBody.replace(
              new RegExp(`http:\\/\\/${localAddress.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\/`, 'g'), 
              'https://www.baidu.com/'
            );
            
            // 更新Content-Length头
            const bodyBuffer = Buffer.from(modifiedBody, 'utf8');
            res.setHeader('Content-Length', bodyBuffer.length);
            
            // 发送修改后的响应
            res.end(bodyBuffer);
          });
          
          // 禁用原始的写入和结束方法
          res.write = function() { return true; };
          res.end = function() { return true; };
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
})
