const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://172.21.120.164:8000/',  // ← 백엔드 포트
        changeOrigin: true,
        secure: false
      }
    }
  }
})
