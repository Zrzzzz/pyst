// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // 源代码映射配置
  sourcemap: {
    server: true,
    client: true
  },

  // Vite 配置
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000',
          changeOrigin: true,
          rewrite: (path) => path
        }
      }
    },
    build: {
      sourcemap: true
    }
  },

  // 开发服务器配置
  devServer: {
    port: 3000,
    host: '127.0.0.1'
  }
})
