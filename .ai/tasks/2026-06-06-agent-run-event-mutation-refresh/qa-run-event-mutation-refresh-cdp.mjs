import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9401)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-event-mutation-refresh/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-event-mutation-refresh'
const branchId = 'branch-event-mutation-refresh'
let renamed = false
let eventPageOffsetZeroCalls = 0

const baseEvents = [
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Mutation Refresh Run' },
    createdAt: '2026-06-06T09:00:00Z'
  },
  {
    id: 'evt-002-branch-approved',
    runId,
    branchId,
    eventType: 'branch.approved',
    actor: 'reviewer',
    summary: { branchId, decision: 'approved', reason: 'baseline branch approval' },
    createdAt: '2026-06-06T09:01:00Z'
  },
  {
    id: 'evt-003-tool-called',
    runId,
    branchId,
    eventType: 'tool.called',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', permission: 'worldline:read' },
    createdAt: '2026-06-06T09:02:00Z'
  },
  {
    id: 'evt-004-skill-proposed',
    runId,
    branchId,
    eventType: 'skill.proposed',
    actor: 'agent',
    summary: { skillId: 'mutation-refresh-skill', status: 'candidate' },
    createdAt: '2026-06-06T09:03:00Z'
  },
  {
    id: 'evt-005-artifact-registered',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'artifact-registry',
    summary: { artifactId: 'artifact-mutation-refresh', kind: 'qa-evidence' },
    createdAt: '2026-06-06T09:04:00Z'
  },
  {
    id: 'evt-006-tool-completed',
    runId,
    branchId,
    eventType: 'tool.completed',
    actor: 'agent',
    summary: { toolName: 'worldline.query_evidence', status: 'completed' },
    createdAt: '2026-06-06T09:05:00Z'
  }
]

const renameEvent = {
  id: 'evt-007-run-renamed',
  runId,
  branchId: '',
  eventType: 'run.renamed',
  actor: 'qa-admin',
  summary: { title: 'Mutation Refresh Run Renamed', reason: 'Renamed via QA refresh' },
  createdAt: '2026-06-06T09:06:00Z'
}

const currentEvents = () => (renamed ? [renameEvent, ...baseEvents] : baseEvents)

const makeRunListResponse = () => ({
  items: [
    {
      id: runId,
      title: renamed ? 'Mutation Refresh Run Renamed' : 'Mutation Refresh Run',
      status: 'ready',
      createdAt: '2026-06-06T09:00:00Z',
      updatedAt: renamed ? '2026-06-06T09:06:00Z' : '2026-06-06T09:05:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Refresh loaded run events after mutation.',
      activeBranchId: branchId,
      counts: { branches: 1, episodes: 1, tools: 2, gates: 1, artifacts: 1, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 1, events: currentEvents().length }
    }
  ],
  total: 1,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
})

const runDetailResponse = () => ({
  id: runId,
  title: renamed ? 'Mutation Refresh Run Renamed' : 'Mutation Refresh Run',
  goal: 'Refresh loaded run events after mutation.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T09:00:00Z',
  updatedAt: renamed ? '2026-06-06T09:06:00Z' : '2026-06-06T09:05:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Refresh loaded run events after mutation.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [{ id: branchId, title: 'Mutation Branch', branchType: 'evidence', status: 'approved', evidenceIds: ['ev-mutation-refresh'] }],
  episodes: [{ id: 'episode-mutation-refresh', runId, branchId, actor: 'agent', toolCalls: ['tool-mutation-refresh'], gateResults: ['gate-mutation-refresh'], artifactIds: ['artifact-mutation-refresh'] }],
  toolTraces: [{ id: 'tool-mutation-refresh', branchId, name: 'worldline.query_evidence', status: 'completed', permission: 'worldline:read', summary: 'Query evidence for mutation refresh.' }],
  gateResults: [{ id: 'gate-mutation-refresh', label: 'Mutation refresh gate', status: 'passed', value: 'events refresh', threshold: 'fresh' }],
  evidenceRefs: [{ id: 'ev-mutation-refresh', evidenceId: 'ev-mutation-refresh', title: 'Mutation refresh evidence', sourceUri: 'qa/mutation-refresh.md' }],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [{ id: 'skill-mutation-refresh', title: 'Mutation refresh skill', status: 'candidate', branchId }],
  artifacts: [],
  events: currentEvents()
})

const makeEventPageResponse = (url) => {
  const parsed = new URL(url)
  const limit = Number(parsed.searchParams.get('limit') || 6)
  const offset = Number(parsed.searchParams.get('offset') || 0)
  if (offset === 0) eventPageOffsetZeroCalls += 1
  const items = currentEvents().slice(offset, offset + limit)
  return {
    run_id: runId,
    items,
    total: currentEvents().length,
    limit,
    offset
  }
}

const makeRenameResponse = () => {
  renamed = true
  return {
    id: runId,
    title: 'Mutation Refresh Run Renamed',
    status: 'ready',
    latestEvent: renameEvent
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
    } else if (url.endsWith(`/api/worldline/runs/${runId}/rename`) && method === 'POST') {
      await fulfillJson(client, event.requestId, makeRenameResponse())
    } else if (url.endsWith(`/api/worldline/runs/${runId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, runDetailResponse())
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
  await waitFor(client, `Boolean(document.querySelector('[data-run-selector-load="${runId}"]'))`, 'mutation run visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${runId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-events-pagination=\"true\"]')?.innerText.includes('6/6 loaded')", 'initial event page')

  await evaluate(client, `(
    async () => {
      const input = document.querySelector('[data-run-rename-title="true"]')
      input.value = 'Mutation Refresh Run Renamed'
      input.dispatchEvent(new Event('input', { bubbles: true }))
      await new Promise((resolve) => setTimeout(resolve, 200))
      document.querySelector('[data-run-rename-active="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1400))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('.event-panel')?.innerText.includes('Mutation Refresh Run Renamed')", 'rename event visible')
  await waitFor(client, "document.querySelector('[data-run-events-pagination=\"true\"]')?.innerText.includes('6/7 loaded')", 'event window refreshed after rename')

  const eventPageRequests = capturedRequests.filter((item) =>
    item.includes(`/api/worldline/runs/${runId}/events?limit=6&offset=0`)
  )
  if (eventPageRequests.length < 2 || eventPageOffsetZeroCalls < 2) {
    throw new Error(`Expected two offset=0 event page requests: ${capturedRequests.join('\n')}`)
  }
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/rename`))) {
    throw new Error(`Missing rename request: ${capturedRequests.join('\n')}`)
  }

  const state = await evaluate(client, `(() => ({
    pagination: document.querySelector('[data-run-events-pagination="true"]')?.innerText || '',
    eventPanel: document.querySelector('.event-panel')?.innerText || '',
    ledger: document.querySelector('.ledger-status')?.innerText || '',
    titleInput: document.querySelector('[data-run-rename-title="true"]')?.value || ''
  }))()`)

  if (!state.eventPanel.includes('Run.Renamed')) {
    throw new Error(`Rename event type not visible: ${JSON.stringify(state)}`)
  }
  if (!state.eventPanel.includes('Mutation Refresh Run Renamed')) {
    throw new Error(`Rename event summary not visible: ${JSON.stringify(state)}`)
  }
  if (!state.pagination.includes('6/7 loaded')) {
    throw new Error(`Expected refreshed pagination to show 6/7: ${JSON.stringify(state)}`)
  }

  const image = await screenshot(client, 'run-event-mutation-refresh.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
