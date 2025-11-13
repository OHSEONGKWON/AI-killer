const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 로컬 FastAPI 백엔드
        changeOrigin: true,
        secure: false
      }
    }
  }
})
