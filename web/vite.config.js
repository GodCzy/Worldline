import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const appDir = fileURLToPath(new URL('./', import.meta.url))
  const apiProxyTarget = env.VITE_API_URL || 'http://127.0.0.1:5050'

  const manualChunks = (id) => {
    if (!id.includes('node_modules')) {
      return
    }

    if (
      id.includes('/node_modules/vue/') ||
      id.includes('/node_modules/vue-router/') ||
      id.includes('/node_modules/pinia/') ||
      id.includes('/node_modules/@vueuse/')
    ) {
      return 'vendor-vue'
    }

    if (
      id.includes('/node_modules/ant-design-vue/') ||
      id.includes('/node_modules/@ant-design/cssinjs/') ||
      id.includes('/node_modules/@ant-design/colors/') ||
      id.includes('/node_modules/@ant-design/icons-vue/') ||
      id.includes('/node_modules/@ant-design/icons-svg/') ||
      id.includes('/node_modules/@rc-component/') ||
      id.includes('/node_modules/rc-') ||
      id.includes('/node_modules/async-validator/')
    ) {
      return 'vendor-antdv'
    }

    if (id.includes('/node_modules/lucide-vue-next/')) {
      return 'vendor-lucide'
    }


    if (id.includes('/node_modules/@antv/')) {
      return 'vendor-g6'
    }

    if (
      id.includes('/node_modules/d3/') ||
      id.includes('/node_modules/d3-') ||
      id.includes('/node_modules/graphology/') ||
      id.includes('/node_modules/graphology-generators/') ||
      id.includes('/node_modules/sigma/') ||
      id.includes('/node_modules/@sigma/')
    ) {
      return 'vendor-graph-core'
    }

    if (id.includes('/node_modules/echarts/')) {
      return 'vendor-echarts'
    }

    if (id.includes('/node_modules/zrender/')) {
      return 'vendor-zrender'
    }

    if (
      id.includes('/node_modules/md-editor-v3/') ||
      id.includes('/node_modules/marked/') ||
      id.includes('/node_modules/marked-highlight/') ||
      id.includes('/node_modules/highlight.js/')
    ) {
      return 'vendor-markdown'
    }

    if (id.includes('/node_modules/markmap-lib/')) {
      return 'vendor-mindmap'
    }

    if (id.includes('/node_modules/markmap-view/')) {
      return 'vendor-mindmap-view'
    }
  }

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      fs: {
        allow: [appDir]
      },
      proxy: {
        '^/api': {
          target: apiProxyTarget,
          changeOrigin: true
        }
      },
      watch: {
        usePolling: true,
        ignored: ['**/node_modules/**', '**/dist/**'],
      },
      host: '0.0.0.0',
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks
        }
      }
    }
  }
})
