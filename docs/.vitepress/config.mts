import { defineConfig } from 'vitepress'
import markdownItTaskCheckbox from 'markdown-it-task-checkbox'

export default defineConfig({
  lang: 'zh-CN',
  title: 'Worldline Docs',
  description: 'Worldline reset baseline and current project facts.',
  base: '/',
  srcDir: './',
  markdown: {
    config: (md) => {
      md.use(markdownItTaskCheckbox)
    }
  },
  themeConfig: {
    logo: '/favicon.svg',
    nav: [
      { text: '首页', link: '/' },
      { text: '项目书', link: '/product/worldline-project-book' },
      { text: '架构', link: '/architecture/knowledge-compiler' }
    ],
    sidebar: [
      {
        text: 'Worldline',
        items: [
          { text: '当前事实源', link: '/' },
          { text: '项目书', link: '/product/worldline-project-book' }
        ]
      },
      {
        text: 'Architecture',
        items: [
          { text: 'Knowledge Compiler', link: '/architecture/knowledge-compiler' },
          { text: 'Worldline UI', link: '/architecture/worldline-ui' },
          { text: 'MCP And Skill Governance', link: '/architecture/mcp-skill-governance' },
          { text: 'Evaluation Gates', link: '/architecture/evaluation-gates' }
        ]
      }
    ],
    footer: {
      message: 'Worldline reset baseline.',
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
