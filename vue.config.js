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
      }
    }
  }
})
