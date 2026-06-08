import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9402)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-event-audit-filters/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-event-audit-filters'
const branchId = 'branch-event-audit-filters'

const events = [
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Audit Filters Run' },
    createdAt: '2026-06-06T10:00:00Z'
  },
  {
    id: 'evt-002-branch-approved',
    runId,
    branchId,
    eventType: 'branch.approved',
    actor: 'reviewer',
    summary: { branchId, decision: 'approved', reason: 'reviewer approved the evidence branch' },
    createdAt: '2026-06-06T10:01:00Z'
  },
  {
    id: 'evt-003-tool-called',
    runId,
    branchId,
    eventType: 'tool.called',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', permission: 'worldline:read' },
    createdAt: '2026-06-06T10:02:00Z'
  },
  {
    id: 'evt-004-skill-proposed',
    runId,
    branchId,
    eventType: 'skill.proposed',
    actor: 'agent',
    summary: { skillId: 'audit-filter-skill', status: 'candidate' },
    createdAt: '2026-06-06T10:03:00Z'
  },
  {
    id: 'evt-005-artifact-registered',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'artifact-registry',
    summary: { artifactId: 'artifact-audit-target', kind: 'qa-evidence' },
    createdAt: '2026-06-06T10:04:00Z'
  },
  {
    id: 'evt-006-tool-completed',
    runId,
    branchId,
    eventType: 'tool.completed',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', status: 'completed' },
    createdAt: '2026-06-06T10:05:00Z'
  }
]

const makeRunListResponse = () => ({
  items: [
    {
      id: runId,
      title: 'Audit Filters Run',
      status: 'ready',
      createdAt: '2026-06-06T10:00:00Z',
      updatedAt: '2026-06-06T10:05:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Filter and export loaded run events.',
      activeBranchId: branchId,
      counts: { branches: 1, episodes: 1, tools: 2, gates: 1, artifacts: 1, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 1, events: events.length }
    }
  ],
  total: 1,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
})

const runDetailResponse = {
  id: runId,
  title: 'Audit Filters Run',
  goal: 'Filter and export loaded run events.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T10:00:00Z',
  updatedAt: '2026-06-06T10:05:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Filter and export loaded run events.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [{ id: branchId, title: 'Audit Branch', branchType: 'evidence', status: 'approved', evidenceIds: ['ev-audit-filter'] }],
  episodes: [{ id: 'episode-audit-filter', runId, branchId, actor: 'agent', toolCalls: ['tool-audit-filter'], gateResults: ['gate-audit-filter'], artifactIds: ['artifact-audit-target'] }],
  toolTraces: [{ id: 'tool-audit-filter', branchId, name: 'worldline.query_evidence', status: 'completed', permission: 'worldline:read', summary: 'Query evidence for audit filters.' }],
  gateResults: [{ id: 'gate-audit-filter', label: 'Audit filter gate', status: 'passed', value: 'filtered', threshold: 'reviewable' }],
  evidenceRefs: [{ id: 'ev-audit-filter', evidenceId: 'ev-audit-filter', title: 'Audit filter evidence', sourceUri: 'qa/audit-filter.md' }],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [{ id: 'skill-audit-filter', title: 'Audit filter skill', status: 'candidate', branchId }],
  artifacts: [],
  events
}

const makeEventPageResponse = (url) => {
  const parsed = new URL(url)
  const limit = Number(parsed.searchParams.get('limit') || 6)
  const offset = Number(parsed.searchParams.get('offset') || 0)
  return {
    run_id: runId,
    items: events.slice(offset, offset + limit),
    total: events.length,
    limit,
    offset
  }
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
  const result = await client.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true })
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed')
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
  const result = await client.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, fromSurface: true })
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
      await fulfillJson(client, event.requestId, makeRunListResponse())
    } else if (url.match(/\/api\/worldline\/runs\/[^/]+\/events(?:\?|$)/) && method === 'GET') {
      await fulfillJson(client, event.requestId, makeEventPageResponse(url))
    } else if (url.endsWith(`/api/worldline/runs/${runId}/artifacts`) && method === 'GET') {
      await fulfillJson(client, event.requestId, { run_id: runId, items: [], total: 0, limit: 100, offset: 0 })
    } else if (url.endsWith(`/api/worldline/runs/${runId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, runDetailResponse)
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
  await client.send('Page.addScriptToEvaluateOnNewDocument', { source: "localStorage.removeItem('user_token')" })
  await client.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false })
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "Boolean(document.querySelector('[data-run-event-audit=\"true\"]'))", 'event audit toolbar')

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

  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-refresh=\"true\"]:not(:disabled)'))", 'enabled refresh')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-refresh="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 700))
      return true
    }
  )()`)
  await waitFor(client, `Boolean(document.querySelector('[data-run-selector-load="${runId}"]'))`, 'audit run visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${runId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-event-audit-status=\"true\"]')?.innerText.includes('6/6 matched')", 'initial audit count')

  await evaluate(client, `(
    async () => {
      const input = document.querySelector('[data-run-event-audit-search="true"]')
      input.value = 'artifact-audit-target'
      input.dispatchEvent(new Event('input', { bubbles: true }))
      await new Promise((resolve) => setTimeout(resolve, 400))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-event-audit-status=\"true\"]')?.innerText.includes('1/6 matched')", 'search filtered count')
  await waitFor(client, "document.querySelector('.event-list')?.innerText.includes('Artifact Registered')", 'artifact event visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-event-audit-export="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 500))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-event-audit-status=\"true\"]')?.innerText.includes('Event audit JSON prepared')", 'export message')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-event-audit-clear="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 300))
      const select = document.querySelector('[data-run-event-audit-actor="true"]')
      select.value = 'reviewer'
      select.dispatchEvent(new Event('change', { bubbles: true }))
      await new Promise((resolve) => setTimeout(resolve, 400))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-event-audit-status=\"true\"]')?.innerText.includes('1/6 matched')", 'actor filtered count')

  const state = await evaluate(client, `(() => ({
    status: document.querySelector('[data-run-event-audit-status="true"]')?.innerText || '',
    search: document.querySelector('[data-run-event-audit-search="true"]')?.value || '',
    actor: document.querySelector('[data-run-event-audit-actor="true"]')?.value || '',
    visibleEvents: Array.from(document.querySelectorAll('.event-item')).map((item) => item.innerText),
    exportDisabled: document.querySelector('[data-run-event-audit-export="true"]')?.disabled || false
  }))()`)
  if (state.actor !== 'reviewer') throw new Error(`Expected reviewer actor filter: ${JSON.stringify(state)}`)
  if (state.search) throw new Error(`Search should be cleared before actor filter: ${JSON.stringify(state)}`)
  if (state.visibleEvents.length !== 1 || !state.visibleEvents[0].includes('Branch Approved') || !state.visibleEvents[0].includes('reviewer')) {
    throw new Error(`Actor filter should show the reviewer branch event: ${JSON.stringify(state)}`)
  }
  if (state.exportDisabled) throw new Error('Export should remain enabled when one filtered event is visible')
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/events?limit=6&offset=0`))) {
    throw new Error(`Missing events request: ${capturedRequests.join('\n')}`)
  }

  const image = await screenshot(client, 'run-event-audit-filters.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
