const fs = require('fs')
const path = require('path')
const { chromium } = require('/tmp/worldline-playwright-qa/node_modules/playwright')

const baseUrl = process.env.WORLDLINE_WEB_URL || 'http://127.0.0.1:5173'
const outputDir = '/mnt/d/dev/Worldline/.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots'

const viewports = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1440x900', width: 1440, height: 900 },
  { name: '390x844', width: 390, height: 844 }
]

const pages = [
  { key: 'worldline-hub', url: '/worldline', waitFor: '.worldline-hub-view' },
  { key: 'worldline-workbench', url: '/worldline/phase5-preview', waitFor: '[data-worldline-canvas="true"]' },
  {
    key: 'graph',
    url:
      '/graph?theme=phase5-preview&module=phase5-preview&scene=graph_timeline&version=worldline-phase5-preview&graph=phase5-graph-focus',
    waitFor: '.graph-container'
  }
]

const infoConfig = {
  organization: {
    name: 'Worldline',
    logo: '/favicon.svg',
    avatar: '/avatar.jpg'
  },
  branding: {
    name: 'Worldline',
    title: 'Worldline',
    subtitle: 'Living Knowledge OS',
    description: 'Phase 5 screenshot QA configuration.'
  },
  features: [],
  themes: [
    {
      id: 'phase5-preview',
      name: 'Phase 5 Preview',
      subtitle: '本地前端验收模块',
      description: '用于验证 Worldline UI 的当前阶段样本。',
      featured: true,
      tags: ['LLM Wiki', 'Temporal Graph', 'Evidence Gate'],
      highlights: ['证据轨', '时间 scrubber', '图谱聚焦', 'Agent handoff'],
      context: {
        theme: 'phase5-preview',
        module: 'phase5-preview',
        scene: 'worldline',
        version: 'worldline-phase5-preview'
      },
      worldline: {
        preview: true
      }
    }
  ],
  actions: [{ name: 'Docs', icon: 'docs', url: 'http://localhost:5174/' }],
  footer: {
    copyright: 'Worldline 2026'
  }
}

const graphNodes = [
  { id: 'Knowledge Compiler', name: 'Knowledge Compiler', type: 'system_layer' },
  { id: 'LLM Wiki', name: 'LLM Wiki', type: 'knowledge_surface' },
  { id: 'Temporal Evidence Graph', name: 'Temporal Evidence Graph', type: 'graph_layer' },
  { id: 'Quality Gate', name: 'Quality Gate', type: 'evaluation' }
]

const graphEdges = [
  { id: 'e1', source_id: 'Knowledge Compiler', target_id: 'LLM Wiki', type: 'feeds' },
  { id: 'e2', source_id: 'LLM Wiki', target_id: 'Temporal Evidence Graph', type: 'cites' },
  { id: 'e3', source_id: 'Temporal Evidence Graph', target_id: 'Quality Gate', type: 'validates' },
  { id: 'e4', source_id: 'Quality Gate', target_id: 'Knowledge Compiler', type: 'replays' }
]

const json = (data) => ({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify(data)
})

async function mockApi(page) {
  await page.route('**/api/**', async (route) => {
    const requestUrl = new URL(route.request().url())
    const pathname = requestUrl.pathname

    if (pathname === '/api/system/info') {
      await route.fulfill(json({ success: true, data: infoConfig }))
      return
    }

    if (pathname === '/api/auth/me') {
      await route.fulfill(
        json({
          id: 'qa-admin',
          username: 'phase5-admin',
          user_id: 'phase5-admin',
          user_id_login: 'phase5-admin',
          role: 'superadmin',
          avatar: ''
        })
      )
      return
    }

    if (pathname === '/api/chat/agent') {
      await route.fulfill(
        json({
          agents: [
            {
              id: 'phase5-agent',
              name: 'Phase 5 Agent',
              description: 'Screenshot QA agent for Worldline handoff.',
              examples: []
            }
          ]
        })
      )
      return
    }

    if (pathname === '/api/chat/default_agent') {
      await route.fulfill(json({ default_agent_id: 'phase5-agent' }))
      return
    }

    if (pathname === '/api/chat/agent/phase5-agent') {
      await route.fulfill(
        json({
          id: 'phase5-agent',
          name: 'Phase 5 Agent',
          description: 'Screenshot QA agent for Worldline handoff.',
          configurable_items: {
            tools: { options: [], default: [] }
          },
          available_tools: []
        })
      )
      return
    }

    if (pathname === '/api/chat/agent/phase5-agent/configs') {
      await route.fulfill(json({ configs: [{ id: 'phase5-default', name: 'Default', is_default: true }] }))
      return
    }

    if (pathname === '/api/chat/agent/phase5-agent/configs/phase5-default') {
      await route.fulfill(
        json({
          config: {
            id: 'phase5-default',
            name: 'Default',
            config_json: { context: {} }
          }
        })
      )
      return
    }

    if (pathname.includes('/accessible') || pathname.includes('/mcp') || pathname.includes('/skill')) {
      await route.fulfill(json({ data: [], databases: [], success: true }))
      return
    }

    if (pathname === '/api/graph/list') {
      await route.fulfill(json({ success: true, data: [{ id: 'neo4j', name: 'Neo4j', type: 'neo4j' }] }))
      return
    }

    if (pathname === '/api/graph/neo4j/info') {
      await route.fulfill(
        json({
          data: {
            status: 'open',
            entity_count: graphNodes.length,
            relationship_count: graphEdges.length,
            embed_model_name: '',
            embed_model_configurable: true,
            unindexed_node_count: 0
          }
        })
      )
      return
    }

    if (pathname === '/api/graph/subgraph') {
      await route.fulfill(json({ data: { nodes: graphNodes, edges: graphEdges } }))
      return
    }

    if (pathname === '/api/system/config') {
      await route.fulfill(json({ success: true, data: { embed_model: '' } }))
      return
    }

    await route.fulfill(json({ success: true, data: {} }))
  })
}

async function preparePage(page, pageSpec) {
  await page.goto(`${baseUrl}${pageSpec.url}`, { waitUntil: 'networkidle' })
  await page.waitForSelector(pageSpec.waitFor, { timeout: 30000 })

  if (pageSpec.key === 'worldline-workbench') {
    const graphButton = page.getByRole('button', { name: /Graph|图谱|打开图谱/ }).first()
    await page.getByText('时间图谱推理线').first().click({ timeout: 10000 }).catch(() => {})
    await page.mouse.move(510, 310)
    await graphButton.isVisible().catch(() => false)
  }

  if (pageSpec.key === 'graph') {
    await page.waitForTimeout(2600)
  } else {
    await page.waitForTimeout(600)
  }
}

async function collectChecks(page, pageSpec) {
  return page.evaluate((key) => {
    const doc = document.documentElement
    const body = document.body
    const text = body.innerText || ''
    const hasHorizontalOverflow = doc.scrollWidth > window.innerWidth + 2
    const canvas = document.querySelector('[data-worldline-canvas="true"] svg')
    const branchNodes = document.querySelectorAll('[data-worldline-canvas="true"] .branch-node').length
    const evidence = document.querySelector('[data-worldline-evidence="true"]')
    const scrubber = document.querySelector('[data-worldline-scrubber="true"]')
    const graphFocus = document.querySelector('[data-worldline-graph-focus="true"]')
    const graphBanner = document.querySelector('.theme-graph-banner')
    const graphCanvas = document.querySelector('.graph-canvas')
    return {
      page: key,
      url: location.href,
      title: document.title,
      bodyTextLength: text.length,
      hasHorizontalOverflow,
      canvasPresent: Boolean(canvas),
      branchNodes,
      evidenceRailPresent: Boolean(evidence),
      scrubberPresent: Boolean(scrubber),
      graphFocusPresent: Boolean(graphFocus),
      graphBannerPresent: Boolean(graphBanner),
      graphCanvasPresent: Boolean(graphCanvas),
      hasAgentHandoff: /Agent Handoff|进入 Agent|带此分支/.test(text),
      hasMojibake: /涓|鐢|鍥|鈥|�/.test(text)
    }
  }, pageSpec.key)
}

async function main() {
  fs.mkdirSync(outputDir, { recursive: true })

  const browser = await chromium.launch({ headless: true })
  const report = []

  for (const viewport of viewports) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1
    })
    await context.addInitScript(() => {
      localStorage.setItem('user_token', 'phase5-screenshot-token')
    })

    for (const pageSpec of pages) {
      const page = await context.newPage()
      await mockApi(page)
      await preparePage(page, pageSpec)
      const checks = await collectChecks(page, pageSpec)
      const fileName = `${pageSpec.key}-${viewport.name}.png`
      const filePath = path.join(outputDir, fileName)
      await page.screenshot({ path: filePath, fullPage: true })
      report.push({ ...checks, viewport: viewport.name, screenshot: filePath })
      await page.close()
    }

    await context.close()
  }

  await browser.close()

  const failures = report.filter((item) => {
    if (item.bodyTextLength < 120 || item.hasMojibake || item.hasHorizontalOverflow) return true
    if (item.page === 'worldline-workbench') {
      return !item.canvasPresent || item.branchNodes < 4 || !item.evidenceRailPresent || !item.scrubberPresent || !item.graphFocusPresent || !item.hasAgentHandoff
    }
    if (item.page === 'graph') {
      return !item.graphBannerPresent || !item.graphCanvasPresent
    }
    return false
  })

  const reportPath = path.join(outputDir, 'phase5-screenshot-report.json')
  fs.writeFileSync(reportPath, JSON.stringify({ baseUrl, report, failures }, null, 2))

  console.log(JSON.stringify({ reportPath, screenshotCount: report.length, failureCount: failures.length }, null, 2))

  if (failures.length) {
    console.error(JSON.stringify(failures, null, 2))
    process.exit(1)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
