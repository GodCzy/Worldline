import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9393)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-selector/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-agent-selector-loaded'
const runTitle = 'Loaded Selector Run'

const runListResponse = {
  items: [
    {
      id: runId,
      title: runTitle,
      status: 'ready',
      createdAt: '2026-06-06T01:00:00Z',
      updatedAt: '2026-06-06T01:05:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Load an existing backend Worldline run.',
      activeBranchId: 'branch-selector',
      qualitySummary: { branchCount: 1 },
      counts: {
        branches: 1,
        episodes: 1,
        tools: 1,
        gates: 1,
        artifacts: 0,
        evidence: 1,
        wiki: 1,
        graph: 1,
        timeline: 1,
        skills: 1,
        events: 2
      }
    },
    {
      id: 'run-agent-selector-older',
      title: 'Older Selector Run',
      status: 'approved',
      createdAt: '2026-06-05T01:00:00Z',
      updatedAt: '2026-06-05T01:05:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Older saved run.',
      activeBranchId: 'branch-older',
      qualitySummary: {},
      counts: {
        branches: 1,
        episodes: 0,
        tools: 0,
        gates: 0,
        artifacts: 0,
        evidence: 0,
        wiki: 0,
        graph: 0,
        timeline: 0,
        skills: 0,
        events: 1
      }
    }
  ],
  total: 2,
  limit: 8,
  offset: 0,
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const runDetailResponse = {
  id: runId,
  title: runTitle,
  goal: 'Load an existing backend Worldline run.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T01:00:00Z',
  updatedAt: '2026-06-06T01:05:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  knowledgeDbId: 'neo4j',
  rootQuestion: 'Load an existing backend Worldline run.',
  activeBranchId: 'branch-selector',
  selectedNodeId: 'branch-selector',
  branches: [
    {
      id: 'branch-selector',
      title: 'Selector Loaded Branch',
      branchType: 'tool_action',
      status: 'ready',
      score: 0.91,
      evidenceIds: ['ev-selector'],
      toolCallIds: ['tool-selector'],
      gateResultIds: ['gate-selector']
    }
  ],
  episodes: [
    {
      id: 'episode-selector',
      runId,
      branchId: 'branch-selector',
      actor: 'agent',
      toolCalls: ['tool-selector'],
      gateResults: ['gate-selector'],
      artifactIds: []
    }
  ],
  toolTraces: [
    {
      id: 'tool-selector',
      branchId: 'branch-selector',
      name: 'worldline.inspect_run_manifest',
      status: 'completed',
      permission: 'worldline:read',
      summary: 'Inspect selected run manifest.'
    }
  ],
  gateResults: [
    {
      id: 'gate-selector',
      label: 'Selector contract',
      status: 'passed',
      value: 'loaded',
      threshold: 'run can hydrate'
    }
  ],
  evidenceRefs: [
    {
      id: 'ev-selector',
      evidenceId: 'ev-selector',
      title: 'Selector evidence',
      summary: 'The selector loads a saved backend run.',
      sourceUri: 'qa/run-selector.md'
    }
  ],
  wikiRefs: [
    {
      id: 'wiki-selector',
      title: 'Run Selector',
      slug: 'run-selector',
      status: 'draft',
      evidenceCoverage: 0.88,
      evidenceIds: ['ev-selector']
    }
  ],
  entityRefs: [
    {
      id: 'entity-selector',
      name: 'RunSelector',
      type: 'agent_runtime',
      confidence: 0.9,
      evidenceId: 'ev-selector'
    }
  ],
  timelineRefs: [
    {
      id: 'tf-selector',
      label: 'Selector run loaded',
      validFrom: '2026-06-06',
      status: 'observed',
      evidenceId: 'ev-selector'
    }
  ],
  skillProposals: [
    {
      id: 'skill-selector',
      name: 'Operate Run Selector',
      trigger: 'operator switches backend runs',
      steps: ['refresh runs', 'load selected run'],
      requiredPermissions: ['worldline:read'],
      evalScore: 0.84
    }
  ],
  artifacts: [],
  events: [
    { id: 'evt-selector-created', runId, branchId: '', eventType: 'run.created', actor: 'qa-admin', summary: {} },
    { id: 'evt-selector-loaded', runId, branchId: 'branch-selector', eventType: 'run.loaded', actor: 'qa-admin', summary: {} }
  ]
}

const artifactListResponse = {
  run_id: runId,
  items: [],
  total: 0,
  limit: 100,
  offset: 0
}

const getJson = async (url) => {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`GET ${url} failed: ${response.status}`)
  return response.json()
}

const waitForCdp = async () => {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const targets = await getJson(`http://127.0.0.1:${port}/json/list`)
      const page = targets.find((target) => target.type === 'page' && target.webSocketDebuggerUrl)
      if (page) return page.webSocketDebuggerUrl
    } catch {
      await sleep(500)
    }
  }
  throw new Error(`Chrome CDP port ${port} did not become ready`)
}

const createClient = async (webSocketUrl) => {
  const ws = new WebSocket(webSocketUrl)
  const pending = new Map()
  const handlers = new Map()
  let id = 0

  ws.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data)
    if (payload.id && pending.has(payload.id)) {
      const { resolve, reject } = pending.get(payload.id)
      pending.delete(payload.id)
      if (payload.error) reject(new Error(JSON.stringify(payload.error)))
      else resolve(payload.result || {})
      return
    }
    const callback = handlers.get(payload.method)
    if (callback) callback(payload.params || {})
  })

  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true })
    ws.addEventListener('error', reject, { once: true })
  })

  const send = (method, params = {}) => new Promise((resolve, reject) => {
    id += 1
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })

  return {
    send,
    on: (method, callback) => handlers.set(method, callback),
    close: () => ws.close()
  }
}

const fulfillJson = (client, requestId, body, status = 200) =>
  client.send('Fetch.fulfillRequest', {
    requestId,
    responseCode: status,
    responseHeaders: [{ name: 'Content-Type', value: 'application/json' }],
    body: Buffer.from(JSON.stringify(body), 'utf8').toString('base64')
  })

const evaluate = async (client, expression, awaitPromise = true) => {
  const result = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true
  })
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed')
  }
  return result.result?.value
}

const waitFor = async (client, expression, label, timeoutMs = 30000) => {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const value = await evaluate(client, expression)
    if (value) return value
    await sleep(500)
  }
  throw new Error(`Timed out waiting for ${label}`)
}

const screenshot = async (client, name) => {
  const result = await client.send('Page.captureScreenshot', {
    format: 'png',
    captureBeyondViewport: true,
    fromSurface: true
  })
  const filePath = path.join(screenshotDir, name)
  fs.writeFileSync(filePath, Buffer.from(result.data, 'base64'))
  return filePath
}

const webSocketUrl = await waitForCdp()
const client = await createClient(webSocketUrl)
const capturedRequests = []

client.on('Fetch.requestPaused', async (event) => {
  const url = event.request.url
  const method = event.request.method
  capturedRequests.push(`${method} ${url}`)
  try {
    if (url.endsWith('/api/system/info')) {
      await fulfillJson(client, event.requestId, { name: 'Worldline QA' })
    } else if (url.includes('/api/worldline/runs?') && method === 'GET') {
      await fulfillJson(client, event.requestId, runListResponse)
    } else if (url.endsWith(`/api/worldline/runs/${runId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, runDetailResponse)
    } else if (url.endsWith(`/api/worldline/runs/${runId}/artifacts`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactListResponse)
    } else {
      await client.send('Fetch.continueRequest', { requestId: event.requestId })
    }
  } catch {
    await client.send('Fetch.failRequest', { requestId: event.requestId, errorReason: 'Failed' })
  }
})

try {
  await client.send('Runtime.enable')
  await client.send('Page.enable')
  await client.send('Fetch.enable', {
    patterns: [{ urlPattern: '*://127.0.0.1:5173/api/*' }, { urlPattern: '*://localhost:5173/api/*' }]
  })
  await client.send('Page.addScriptToEvaluateOnNewDocument', {
    source: "localStorage.removeItem('user_token')"
  })
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 1100,
    deviceScaleFactor: 1,
    mobile: false
  })
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "Boolean(document.querySelector('[data-run-selector=\"true\"]'))", 'run selector panel')

  const adminState = await evaluate(client, `(() => {
    const pinia = document.querySelector('#app')?.__vue_app__?.config?.globalProperties?.$pinia
    const user = pinia?._s?.get('user')
    if (!user) return { error: 'user_store_not_found' }
    user.token = 'qa-token'
    user.userId = 'qa-admin'
    user.username = 'qa-admin'
    user.userRole = 'admin'
    return { isAdmin: user.isAdmin, role: user.userRole }
  })()`)
  if (adminState.error || adminState.isAdmin !== true) {
    throw new Error(`Could not inject admin user store: ${JSON.stringify(adminState)}`)
  }

  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-refresh=\"true\"]:not(:disabled)'))", 'enabled run selector refresh')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-refresh="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 650))
      return true
    }
  )()`)
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(runTitle)})`, 'listed selector run')

  const loaded = await evaluate(client, `(
    async () => {
      const button = document.querySelector('[data-run-selector-load="${runId}"]')
      if (!button) return { error: 'run_button_not_found' }
      button.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      const status = document.querySelector('.ledger-status')?.innerText || ''
      const title = document.querySelector('.run-card h2')?.innerText || ''
      const selector = document.querySelector('[data-run-selector="true"]')?.innerText || ''
      return { status, title, selector, body: document.body.innerText }
    }
  )()`)
  if (loaded.error) throw new Error(`Run selector load failed: ${loaded.error}`)
  if (!loaded.status.includes(runId)) throw new Error(`Ledger status did not show loaded run: ${loaded.status}`)
  if (!loaded.title.includes(runTitle)) throw new Error(`Run title did not hydrate: ${loaded.title}`)
  if (!loaded.selector.includes('Active backend run')) {
    throw new Error(`Selector message did not confirm active run: ${loaded.selector}`)
  }
  for (const expected of ['Selector Loaded Branch', 'worldline.inspect_run_manifest', 'Operate Run Selector']) {
    if (!loaded.body.includes(expected)) {
      throw new Error(`Loaded workbench missing ${expected}`)
    }
  }
  if (!capturedRequests.some((item) => item.includes('/api/worldline/runs?limit=8'))) {
    throw new Error(`Run list request was not captured: ${capturedRequests.join('\n')}`)
  }
  if (!capturedRequests.some((item) => item.endsWith(`/api/worldline/runs/${runId}`))) {
    throw new Error(`Run detail request was not captured: ${capturedRequests.join('\n')}`)
  }
  if (!capturedRequests.some((item) => item.endsWith(`/api/worldline/runs/${runId}/artifacts`))) {
    throw new Error(`Run artifact refresh request was not captured: ${capturedRequests.join('\n')}`)
  }

  const image = await screenshot(client, 'run-selector-loaded.png')
  console.log(JSON.stringify({
    status: 'ok',
    loaded,
    capturedRequests,
    screenshot: image
  }, null, 2))
} finally {
  client.close()
}
