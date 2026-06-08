const fs = require('fs')
const path = require('path')
const { chromium } = require('playwright')

const baseUrl = process.env.WORLDLINE_BASE_URL || 'http://127.0.0.1:5173'
const outDir = path.resolve(__dirname, 'screenshots')

const viewports = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1440x900', width: 1440, height: 900 },
  { name: '390x844', width: 390, height: 844 }
]

const liveTheme = {
  id: 'live-kb',
  name: 'Live Knowledge',
  subtitle: 'Evidence-backed live bridge',
  description: 'Live knowledge base wired to evidence, wiki, graph, timeline, workflow, MCP, and gate APIs.',
  featured: true,
  knowledge_db_id: 'kb_live',
  tags: ['Evidence', 'Wiki', 'Graph'],
  context: {
    theme: 'live-kb',
    module: 'live-kb',
    scene: 'worldline',
    version: 'worldline-context-v1',
    db_id: 'kb_live',
    knowledge_db_id: 'kb_live'
  }
}

const counts = {
  source_assets: 1,
  document_versions: 1,
  evidence_anchors: 4,
  knowledge_files: 1,
  knowledge_chunks: 3,
  wiki_pages: 2,
  entities: 5,
  relationships: 4,
  temporal_facts: 2,
  golden_items: 1,
  quality_gate_runs: 1,
  workflow_runs: 1,
  mcp_audit_logs: 1
}

const overview = {
  db_id: 'kb_live',
  status: 'ready',
  counts,
  evidence: { items: [] },
  wiki: { pages: { items: [] }, stale: { stale_count: 0 } },
  graph: { entities: { items: [] }, relationships: { items: [] } },
  timeline: { items: [] },
  quality_gate: { latest: { gate_id: 'gate_live', status: 'passed' } },
  mcp: {
    manifest: {
      server: { name: 'worldline', version: '0.2.0' },
      tools: [
        { name: 'worldline.rebuild_wiki' },
        { name: 'worldline.update_graph' },
        { name: 'worldline.run_quality_gate' },
        { name: 'worldline.inspect_timeline' }
      ]
    },
    audit_logs: {
      items: [{ log_id: 'audit_live', tool_name: 'worldline.plan_workflow', status: 'success' }]
    }
  }
}

const generatedWorldline = {
  themeId: 'live-kb',
  moduleId: 'live-kb',
  knowledgeDbId: 'kb_live',
  knowledgeMode: 'llm_wiki_primary_rag_auxiliary',
  layers: ['evidence_ledger', 'llm_wiki', 'temporal_evidence_graph', 'quality_gate', 'agent_handoff'],
  rootQuestion: 'How should this live bridge be verified?',
  questionDraft: 'How should this live bridge be verified?',
  status: 'ready',
  sourceType: 'worldline-live-facade-v1',
  generationMode: 'base',
  generationRound: 1,
  branches: [
    {
      id: 'live-evidence',
      title: '证据优先世界线',
      subtitle: '先确认 EvidenceAnchor 再推进',
      summary: '当前分支来自后端 live facade，并保留 wiki、graph、timeline 和 quality gate 支撑。',
      choiceLabel: 'Evidence',
      riskLabel: '可验证',
      costLabel: '低扰动',
      confidenceLabel: '后端证据基线',
      routeTone: '先验证，再生成。',
      tone: 'calm',
      suitability: ['真实后端', '证据优先', '可回放'],
      focus: 'live-evidence',
      choiceReason: '该分支来自持久化知识对象。',
      switchHint: '当证据不足或质量门禁失败时切线。',
      evidenceRefs: [
        {
          id: 'ev_1',
          evidenceId: 'ev_1',
          title: 'live-notes.md',
          typeLabel: 'EvidenceAnchor',
          summary: 'Evidence anchors preserve the source path, page, line, and bbox.',
          sourceUri: 'live-notes.md',
          page: 1,
          lineStart: 10,
          lineEnd: 12,
          bbox: [1, 2, 3, 4]
        }
      ],
      wikiRefs: [{ id: 'wiki_1', title: 'Live Wiki', slug: 'live-wiki', status: 'current' }],
      entityRefs: [{ id: 'ent_1', name: 'Worldline', type: 'system', confidence: 0.98 }],
      timelineRefs: [{ id: 'tf_1', label: 'Live bridge verified', validFrom: '2026-06-04', validTo: '' }],
      quality: {
        status: 'inspectable',
        evidenceCount: 1,
        supportChannels: 4,
        citationCoverage: 1,
        graphSupport: true,
        temporalSupport: true
      },
      nextStepTitle: '继续验证此分支',
      nextStepSubtitle: '把当前分支带入 Agent、Graph 或 Quality Gate。',
      nextActions: [
        {
          id: 'go-chat',
          label: '带此分支去对话',
          description: '移交 Agent',
          targetType: 'chat',
          emphasis: 'primary'
        },
        {
          id: 'go-graph',
          label: '查看图谱支撑',
          description: '打开图谱页',
          targetType: 'graph',
          emphasis: 'secondary'
        }
      ],
      context: {
        theme: 'live-kb',
        module: 'live-kb',
        scene: 'evidence_first',
        entry: 'worldline-live',
        focus: 'live-evidence',
        branch: 'live-evidence',
        graph: 'worldline-live-graph',
        db_id: 'kb_live',
        knowledge_db_id: 'kb_live'
      }
    }
  ],
  activeBranchId: 'live-evidence',
  selectedNodeId: 'live-evidence',
  tree: {
    width: 1160,
    height: 560,
    nodes: [
      { id: 'root-question', type: 'root', title: '起始问题', subtitle: 'How should this live bridge be verified?', x: 120, y: 280 },
      { id: 'live-evidence', type: 'branch', title: '证据优先世界线', subtitle: 'Evidence', x: 420, y: 180, branchId: 'live-evidence' },
      { id: 'live-evidence-next', type: 'next-step', title: '继续验证', subtitle: 'Agent / Graph / Gate', x: 760, y: 180, branchId: 'live-evidence' }
    ],
    edges: [
      { id: 'edge-1', source: 'root-question', target: 'live-evidence', branchId: 'live-evidence', kind: 'primary' },
      { id: 'edge-2', source: 'live-evidence', target: 'live-evidence-next', branchId: 'live-evidence', kind: 'guide' }
    ]
  },
  viewState: {
    lastGeneratedFrom: 'live-generate',
    protocolVersion: 'worldline-live-v1'
  },
  displayMeta: {
    stageLabel: '真实知识库',
    stageTitle: '基于证据、Wiki、图谱和时间线生成世界线',
    stageSubtitle: '当前结果来自后端 Worldline facade。',
    branchCount: 1,
    themeName: 'Live Knowledge',
    generationLabel: '生成真实世界线',
    generationMode: 'base',
    workspaceHint: '先检查证据支撑，再进入下一层验证。'
  },
  snapshots: [
    { id: 'source', label: 'Source', title: '证据入账', metric: 4, summary: 'EvidenceAnchor ready.' },
    { id: 'wiki', label: 'Wiki', title: 'LLM Wiki', metric: 2, summary: 'Wiki ready.' },
    { id: 'graph', label: 'Graph', title: 'Graph', metric: 7, summary: 'Graph ready.' },
    { id: 'gate', label: 'Gate', title: 'Quality Gate', metric: 1, summary: 'Gate passed.' }
  ],
  quality: { status: 'passed', gateId: 'gate_live', branchCount: 1, citationCoverage: 1, latestGate: overview.quality_gate.latest },
  routeTrace: {
    db_id: 'kb_live',
    facade: 'WorldlineWorkbenchService',
    deterministic_baseline: true,
    counts,
    evidence_count: 1,
    wiki_page_count: 1,
    entity_count: 1,
    timeline_count: 1,
    quality_gate_status: 'passed'
  },
  overview: {
    status: 'ready',
    counts,
    quality_gate: overview.quality_gate
  }
}

const pages = [
  {
    id: 'worldline-hub-live',
    path: '/worldline',
    expect: async (page) => {
      const body = await page.textContent('body')
      if (!body.includes('Live Knowledge')) throw new Error('hub missing live module')
      if (!body.includes('生成世界线')) throw new Error('hub missing launch action')
    }
  },
  {
    id: 'worldline-workbench-live',
    path: '/worldline/live-kb?knowledge_db_id=kb_live&question=How%20should%20this%20live%20bridge%20be%20verified%3F',
    expect: async (page) => {
      await page.waitForSelector('[data-worldline-live-ops="true"]', { timeout: 8000 })
      const body = await page.textContent('body')
      if (!body.includes('后端联通')) throw new Error('workbench missing Live Ops panel')
      if (!body.includes('MCP Tools')) throw new Error('workbench missing MCP tool summary')
      if (!body.includes('证据优先世界线')) throw new Error('workbench missing live branch')
      if (!body.includes('kb_live')) throw new Error('workbench missing live db trace')
      await page.locator('[data-worldline-live-ops="true"] button[title="刷新 MCP manifest 和审计摘要"]').click()
      await page.waitForTimeout(300)
    }
  },
  {
    id: 'graph-live-db',
    path: '/graph?theme=live-kb&module=live-kb&scene=graph_timeline&db_id=kb_live&knowledge_db_id=kb_live',
    expect: async (page) => {
      await page.waitForSelector('.graph-container', { timeout: 8000 })
      const body = await page.textContent('body')
      if (!body.includes('Live Knowledge')) throw new Error('graph page did not preserve route db selection')
      if (!body.includes('已加载')) throw new Error('graph page did not load selected non-Neo4j stats')
    }
  }
]

async function installMocks(page) {
  await page.route('**/api/system/info', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: {
          organization: { name: 'Worldline', logo: '/favicon.svg', avatar: '/avatar.jpg' },
          branding: { name: 'Worldline', title: 'Worldline', subtitle: 'Live QA' },
          features: [],
          themes: [liveTheme],
          actions: [{ name: 'Docs', icon: 'docs', url: 'http://localhost:5174/' }],
          footer: { copyright: 'Worldline 2026' }
        }
      })
    })
  })
  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        username: 'Joy',
        user_id: 'Joy',
        role: 'superadmin',
        department_id: 1,
        department_name: '默认部门'
      })
    })
  })
  await page.route('**/api/knowledge/databases/kb_live/worldline/overview', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(overview) })
  })
  await page.route('**/api/knowledge/databases/kb_live/worldline/generate', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(generatedWorldline) })
  })
  await page.route('**/api/knowledge/databases/kb_live/worldline-mcp/manifest', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ db_id: 'kb_live', ...overview.mcp.manifest })
    })
  })
  await page.route('**/api/knowledge/databases/kb_live/worldline-mcp/audit-logs**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(overview.mcp.audit_logs) })
  })
  await page.route('**/api/graph/list', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: [{ id: 'kb_live', name: 'Live Knowledge', type: 'lightrag' }] })
    })
  })
  await page.route('**/api/graph/stats**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: { total_nodes: 5, total_edges: 4 } })
    })
  })
  await page.route('**/api/graph/subgraph**', async (route) => {
    const url = new URL(route.request().url())
    if (url.searchParams.get('db_id') !== 'kb_live') {
      await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'wrong db' }) })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: {
          nodes: [{ id: 'Worldline', label: 'Worldline', type: 'system' }],
          edges: []
        }
      })
    })
  })
  await page.route('**/api/graph/neo4j/info', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: { status: 'closed', entity_count: 0, relationship_count: 0 } })
    })
  })
}

async function assertNoHorizontalOverflow(page) {
  const overflow = await page.evaluate(() => {
    const root = document.documentElement
    return Math.max(0, root.scrollWidth - root.clientWidth)
  })
  if (overflow > 4) {
    throw new Error(`horizontal overflow: ${overflow}px`)
  }
}

async function run() {
  fs.mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch({ headless: true })
  const report = []
  const failures = []

  for (const viewport of viewports) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1
    })
    await context.addInitScript(() => {
      localStorage.clear()
      sessionStorage.clear()
      localStorage.setItem('user_token', 'mock-superadmin-token')
      localStorage.setItem('worldline_app_nav_expanded', '1')
    })

    for (const entry of pages) {
      const page = await context.newPage()
      await installMocks(page)
      const screenshot = path.join(outDir, `${entry.id}-${viewport.name}.png`)
      try {
        await page.goto(`${baseUrl}${entry.path}`, { waitUntil: 'domcontentloaded', timeout: 15000 })
        await page.waitForTimeout(1200)
        await entry.expect(page)
        await assertNoHorizontalOverflow(page)
        await page.evaluate(() => {
          window.scrollTo(0, 0)
          document.querySelectorAll('*').forEach((element) => {
            if (element.scrollTop) {
              element.scrollTop = 0
            }
          })
        })
        await page.waitForTimeout(150)
        await page.screenshot({ path: screenshot, fullPage: true })
        report.push({
          page: entry.id,
          route: entry.path,
          viewport: viewport.name,
          screenshot,
          url: page.url(),
          status: 'passed'
        })
      } catch (error) {
        failures.push({
          page: entry.id,
          route: entry.path,
          viewport: viewport.name,
          error: error.message,
          url: page.url()
        })
        try {
          await page.screenshot({ path: screenshot, fullPage: true })
        } catch (_) {
          // Keep primary failure visible in the report.
        }
      } finally {
        await page.close()
      }
    }

    await context.close()
  }

  await browser.close()

  const payload = {
    generatedAt: new Date().toISOString(),
    baseUrl,
    report,
    failures
  }
  fs.writeFileSync(path.join(outDir, 'live-ops-screenshot-report.json'), JSON.stringify(payload, null, 2))

  if (failures.length) {
    console.error(JSON.stringify(payload, null, 2))
    process.exit(1)
  }

  console.log(JSON.stringify(payload, null, 2))
}

run().catch((error) => {
  console.error(error)
  process.exit(1)
})
