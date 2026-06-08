import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9394)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-selector-filters/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-agent-selector-filtered'
const runTitle = 'Filtered Selector Run'

const runListResponse = {
  items: [
    {
      id: runId,
      title: runTitle,
      status: 'ready',
      createdAt: '2026-06-06T02:00:00Z',
      updatedAt: '2026-06-06T02:05:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Filter and load an existing backend Worldline run.',
      activeBranchId: 'branch-filtered',
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
    }
  ],
  total: 1,
  limit: 8,
  offset: 0,
  filters: {
    query: 'selector',
    status: 'ready',
    themeId: 'agent-workbench',
    createdBy: 'qa-admin'
  },
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const runDetailResponse = {
  id: runId,
  title: runTitle,
  goal: 'Filter and load an existing backend Worldline run.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T02:00:00Z',
  updatedAt: '2026-06-06T02:05:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  knowledgeDbId: 'neo4j',
  rootQuestion: 'Filter and load an existing backend Worldline run.',
  activeBranchId: 'branch-filtered',
  selectedNodeId: 'branch-filtered',
  branches: [
    {
      id: 'branch-filtered',
      title: 'Filtered Run Branch',
      branchType: 'tool_action',
      status: 'ready',
      score: 0.92,
      evidenceIds: ['ev-filtered'],
      toolCallIds: ['tool-filtered'],
      gateResultIds: ['gate-filtered']
    }
  ],
  episodes: [
    {
      id: 'episode-filtered',
      runId,
      branchId: 'branch-filtered',
      actor: 'agent',
      toolCalls: ['tool-filtered'],
      gateResults: ['gate-filtered'],
      artifactIds: []
    }
  ],
  toolTraces: [
    {
      id: 'tool-filtered',
      branchId: 'branch-filtered',
      name: 'worldline.list_runs',
      status: 'completed',
      permission: 'worldline:read',
      summary: 'Filter saved Worldline runs before loading.'
    }
  ],
  gateResults: [
    {
      id: 'gate-filtered',
      label: 'Filtered selector contract',
      status: 'passed',
      value: 'matched',
      threshold: 'filtered run can hydrate'
    }
  ],
  evidenceRefs: [
    {
      id: 'ev-filtered',
      evidenceId: 'ev-filtered',
      title: 'Filtered selector evidence',
      summary: 'The selector sends filters to the backend run list route.',
      sourceUri: 'qa/run-selector-filters.md'
    }
  ],
  wikiRefs: [
    {
      id: 'wiki-filtered-selector',
      title: 'Filtered Run Selector',
      slug: 'filtered-run-selector',
      status: 'draft',
      evidenceCoverage: 0.9,
      evidenceIds: ['ev-filtered']
    }
  ],
  entityRefs: [
    {
      id: 'entity-filtered-selector',
      name: 'FilteredRunSelector',
      type: 'agent_runtime',
      confidence: 0.91,
      evidenceId: 'ev-filtered'
    }
  ],
  timelineRefs: [
    {
      id: 'tf-filtered-selector',
      label: 'Filtered selector run loaded',
      validFrom: '2026-06-06',
      status: 'observed',
      evidenceId: 'ev-filtered'
    }
  ],
  skillProposals: [
    {
      id: 'skill-filtered-selector',
      name: 'Operate Filtered Selector',
      trigger: 'operator searches saved runs',
      steps: ['set filters', 'refresh runs', 'load selected run'],
      requiredPermissions: ['worldline:read'],
      evalScore: 0.86
    }
  ],
  artifacts: [],
  events: [
    { id: 'evt-filtered-created', runId, branchId: '', eventType: 'run.created', actor: 'qa-admin', summary: {} },
    { id: 'evt-filtered-loaded', runId, branchId: 'branch-filtered', eventType: 'run.loaded', actor: 'qa-admin', summary: {} }
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
  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-filters=\"true\"]'))", 'run selector filters')

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

  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-filters=\"true\"] button[type=\"submit\"]:not(:disabled)'))", 'enabled filter submit')
  await evaluate(client, `(
    async () => {
      const setValue = (selector, value) => {
        const element = document.querySelector(selector)
        element.value = value
        element.dispatchEvent(new Event('input', { bubbles: true }))
        element.dispatchEvent(new Event('change', { bubbles: true }))
      }
      setValue('[data-run-selector-query="true"]', 'selector')
      setValue('[data-run-selector-status="true"]', 'ready')
      setValue('[data-run-selector-theme="true"]', 'agent-workbench')
      setValue('[data-run-selector-created-by="true"]', 'qa-admin')
      document.querySelector('[data-run-selector-filters="true"] button[type="submit"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 800))
      return true
    }
  )()`)
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(runTitle)})`, 'filtered selector run')
  const selectorBeforeLoad = await evaluate(
    client,
    `document.querySelector('[data-run-selector="true"]')?.innerText || ''`
  )
  if (!selectorBeforeLoad.includes('Loaded 1/1 backend runs with filters')) {
    throw new Error(`Selector did not report filtered result before load: ${selectorBeforeLoad}`)
  }

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
  if (loaded.error) throw new Error(`Run selector filtered load failed: ${loaded.error}`)
  if (!loaded.status.includes(runId)) throw new Error(`Ledger status did not show loaded run: ${loaded.status}`)
  if (!loaded.title.includes(runTitle)) throw new Error(`Run title did not hydrate: ${loaded.title}`)
  if (!loaded.selector.includes('Active backend run')) {
    throw new Error(`Selector did not report active run after load: ${loaded.selector}`)
  }
  for (const expected of ['Filtered Run Branch', 'worldline.list_runs', 'Operate Filtered Selector']) {
    if (!loaded.body.includes(expected)) {
      throw new Error(`Loaded workbench missing ${expected}`)
    }
  }
  const filteredRequest = capturedRequests.find((item) => item.includes('/api/worldline/runs?'))
  if (!filteredRequest) {
    throw new Error(`Run list request was not captured: ${capturedRequests.join('\n')}`)
  }
  for (const expected of ['query=selector', 'status=ready', 'theme_id=agent-workbench', 'created_by=qa-admin']) {
    if (!filteredRequest.includes(expected)) {
      throw new Error(`Filtered request missing ${expected}: ${filteredRequest}`)
    }
  }
  if (!capturedRequests.some((item) => item.endsWith(`/api/worldline/runs/${runId}`))) {
    throw new Error(`Run detail request was not captured: ${capturedRequests.join('\n')}`)
  }
  if (!capturedRequests.some((item) => item.endsWith(`/api/worldline/runs/${runId}/artifacts`))) {
    throw new Error(`Run artifact refresh request was not captured: ${capturedRequests.join('\n')}`)
  }

  const image = await screenshot(client, 'run-selector-filters-loaded.png')
  console.log(JSON.stringify({
    status: 'ok',
    selectorBeforeLoad,
    loaded,
    filteredRequest,
    capturedRequests,
    screenshot: image
  }, null, 2))
} finally {
  client.close()
}
