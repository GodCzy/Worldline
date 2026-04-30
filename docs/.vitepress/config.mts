import { defineConfig } from 'vitepress'
import markdownItTaskCheckbox from 'markdown-it-task-checkbox'

export default defineConfig({
  lang: 'zh-CN',
  title: 'Worldline',
  description: 'Worldline 文档中心：面向企业级知识平台的前后端结构、模块扩展、运维验证与历史归档。',
  base: '/',
  srcDir: './',
  srcExclude: ['context-cache/**', 'archive/context-cache/**'],
  ignoreDeadLinks: [/localhost/],
  markdown: {
    config: (md) => {
      md.use(markdownItTaskCheckbox)
    }
  },
  themeConfig: {
    logo: '/favicon.svg',
    nav: [
      { text: '首页', link: '/' },
      { text: '平台架构', link: '/platform-architecture' },
      { text: '前端结构', link: '/frontend-architecture' },
      { text: '后端结构', link: '/backend-architecture' },
      { text: '模块扩展', link: '/module-extension' },
      { text: '运维与验证', link: '/operations-and-validation' }
    ],
    sidebar: [
      {
        text: '当前产品文档',
        items: [
          { text: '首页', link: '/' },
          { text: '平台架构', link: '/platform-architecture' },
          { text: '前端结构', link: '/frontend-architecture' },
          { text: '后端结构', link: '/backend-architecture' },
          { text: '模块扩展', link: '/module-extension' },
          { text: '运维与验证', link: '/operations-and-validation' }
        ]
      }
    ],
    footer: {
      message: 'Worldline 文档站服务于当前产品结构、工程实施、运行验证与历史审计。',
      copyright: 'Copyright 2026 Worldline'
    },
    lastUpdated: {
      text: '最后更新',
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'medium'
      }
    },
    search: {
      provider: 'local'
    },
    docFooter: {
      prev: '上一页',
      next: '下一页'
    }
  }
})
