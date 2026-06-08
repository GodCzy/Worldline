import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9400)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-event-pagination/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-event-pages'
const branchId = 'branch-event-pages'

const events = [
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Event Pagination Run' },
    createdAt: '2026-06-06T08:00:00Z'
  },
  {
    id: 'evt-002-branch-approved',
    runId,
    branchId,
    eventType: 'branch.approved',
    actor: 'reviewer',
    summary: { branchId, decision: 'approved', reason: 'first evidence branch accepted' },
    createdAt: '2026-06-06T08:01:00Z'
  },
  {
    id: 'evt-003-tool-called',
    runId,
    branchId,
    eventType: 'tool.called',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', permission: 'worldline:read' },
    createdAt: '2026-06-06T08:02:00Z'
  },
  {
    id: 'evt-004-skill-proposed',
    runId,
    branchId,
    eventType: 'skill.proposed',
    actor: 'agent',
    summary: { skillId: 'worldline-event-pager', status: 'candidate' },
    createdAt: '2026-06-06T08:03:00Z'
  },
  {
    id: 'evt-005-artifact-registered',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'artifact-registry',
    summary: { artifactId: 'artifact-event-page-001', kind: 'qa-evidence' },
    createdAt: '2026-06-06T08:04:00Z'
  },
  {
    id: 'evt-006-run-renamed',
    runId,
    branchId: '',
    eventType: 'run.renamed',
    actor: 'qa-admin',
    summary: { title: 'Event Pagination Run v2' },
    createdAt: '2026-06-06T08:05:00Z'
  },
  {
    id: 'evt-007-branch-rejected',
    runId,
    branchId: 'branch-event-rejected',
    eventType: 'branch.rejected',
    actor: 'reviewer',
    summary: { branchId: 'branch-event-rejected', decision: 'rejected', reason: 'missing source anchor' },
    createdAt: '2026-06-06T08:06:00Z'
  },
  {
    id: 'evt-008-tool-completed',
    runId,
    branchId,
    eventType: 'tool.completed',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', status: 'completed' },
    createdAt: '2026-06-06T08:07:00Z'
  },
  {
    id: 'evt-009-artifact-saved',
    runId,
    branchId,
    eventType: 'artifact.saved',
    actor: 'artifact-registry',
    summary: { artifactId: 'artifact-event-page-002', kind: 'screenshot' },
    createdAt: '2026-06-06T08:08:00Z'
  },
  {
    id: 'evt-010-run-archived',
    runId,
    branchId: '',
    eventType: 'run.archived',
    actor: 'qa-admin',
    summary: { status: 'archived', reason: 'pagination qa terminal event' },
    createdAt: '2026-06-06T08:09:00Z'
  }
]

const makeRunListResponse = () => ({
  items: [
    {
      id: runId,
      title: 'Event Pagination Run',
      status: 'ready',
      createdAt: '2026-06-06T08:00:00Z',
      updatedAt: '2026-06-06T08:10:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Page through backend run events.',
      activeBranchId: branchId,
      counts: { branches: 2, episodes: 1, tools: 2, gates: 1, artifacts: 2, evidence: 1, wiki: 1, graph: 1, timeline: 1, skills: 1, events: events.length }
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
  title: 'Event Pagination Run',
  goal: 'Page through backend run events.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T08:00:00Z',
  updatedAt: '2026-06-06T08:10:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Page through backend run events.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [
    { id: branchId, title: 'Evidence Branch', branchType: 'evidence', status: 'approved', evidenceIds: ['ev-event-page'] },
    { id: 'branch-event-rejected', title: 'Rejected Branch', branchType: 'audit', status: 'rejected', evidenceIds: [] }
  ],
  episodes: [
    {
      id: 'episode-event-page',
      runId,
      branchId,
      actor: 'agent',
      toolCalls: ['tool-query-evidence'],
      gateResults: ['gate-event-page'],
      artifactIds: ['artifact-event-page-001']
    }
  ],
  toolTraces: [
    {
      id: 'tool-query-evidence',
      branchId,
      name: 'worldline.query_evidence',
      status: 'completed',
      permission: 'worldline:read',
      summary: 'Query evidence for event pagination.'
    }
  ],
  gateResults: [{ id: 'gate-event-page', label: 'Event page gate', status: 'passed', value: '10 events', threshold: 'paginated' }],
  evidenceRefs: [{ id: 'ev-event-page', evidenceId: 'ev-event-page', title: 'Event pagination evidence', sourceUri: 'qa/event-pagination.md' }],
  wikiRefs: [{ id: 'wiki-event-page', title: 'Run Events Pagination', sourceIds: ['ev-event-page'] }],
  entityRefs: [{ id: 'entity-run-event', label: 'RunEvent', kind: 'schema' }],
  timelineRefs: [{ id: 'timeline-run-event', title: 'Run Event Timeline', temporalStatus: 'current' }],
  skillProposals: [{ id: 'skill-event-pager', title: 'Event pager skill', status: 'candidate', branchId }],
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
  await waitFor(client, "Boolean(document.querySelector('[data-run-selector=\"true\"]'))", 'run selector')

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
  await waitFor(client, `Boolean(document.querySelector('[data-run-selector-load="${runId}"]'))`, 'event run visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${runId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-events-pagination=\"true\"]')?.innerText.includes('6/10 loaded')", 'first event page')
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/events?limit=6&offset=0`))) {
    throw new Error(`Missing first event page request: ${capturedRequests.join('\n')}`)
  }

  await waitFor(client, "Boolean(document.querySelector('[data-run-events-load-more=\"true\"]:not(:disabled)'))", 'event load more enabled')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-events-load-more="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-events-pagination=\"true\"]')?.innerText.includes('10/10 loaded')", 'second event page')
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/events?limit=6&offset=6`))) {
    throw new Error(`Missing second event page request: ${capturedRequests.join('\n')}`)
  }

  await evaluate(client, `(
    async () => {
      const buttons = Array.from(document.querySelectorAll('.event-filter-button'))
      const branch = buttons.find((button) => button.innerText.includes('Branch'))
      branch?.click()
      await new Promise((resolve) => setTimeout(resolve, 400))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('.event-filter-button.active')?.innerText.includes('Branch')", 'branch filter active')

  const state = await evaluate(client, `(() => ({
    pagination: document.querySelector('[data-run-events-pagination="true"]')?.innerText || '',
    eventPanel: document.querySelector('.event-panel')?.innerText || '',
    visibleEvents: Array.from(document.querySelectorAll('.event-item')).map((item) => item.innerText),
    activeFilter: document.querySelector('.event-filter-button.active')?.innerText || '',
    loadMoreDisabled: document.querySelector('[data-run-events-load-more="true"]')?.disabled || false
  }))()`)

  if (!state.pagination.includes('10/10 loaded')) throw new Error(`Unexpected pagination state: ${JSON.stringify(state)}`)
  if (!state.loadMoreDisabled) throw new Error('Load More Events should be disabled after all events are loaded')
  if (!state.activeFilter.includes('Branch') || !state.activeFilter.includes('2')) {
    throw new Error(`Branch filter count should be 2: ${JSON.stringify(state)}`)
  }
  if (state.visibleEvents.length !== 2 || !state.visibleEvents.every((text) => text.includes('Branch'))) {
    throw new Error(`Branch filter should show only two branch events: ${JSON.stringify(state)}`)
  }

  const image = await screenshot(client, 'run-event-pagination.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
