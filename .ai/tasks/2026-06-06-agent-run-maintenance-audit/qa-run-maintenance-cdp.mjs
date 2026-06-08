import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9396)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-maintenance-audit/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const activeRunId = 'run-maintenance-active'
const archivedRunId = 'run-maintenance-archive'
const initialTitle = 'Maintenance Active Run'
const renamedTitle = 'Renamed Maintenance Run'
const archiveTitle = 'Archive Candidate Run'
let activeTitle = initialTitle
let archiveStatus = 'ready'

const makeRunListResponse = () => ({
  items: [
    {
      id: activeRunId,
      title: activeTitle,
      status: 'ready',
      createdAt: '2026-06-06T04:00:00Z',
      updatedAt: '2026-06-06T04:04:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Maintain saved backend runs.',
      activeBranchId: 'branch-maintenance',
      counts: { branches: 1, episodes: 1, tools: 1, gates: 1, artifacts: 0, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 0, events: 2 }
    },
    {
      id: archivedRunId,
      title: archiveTitle,
      status: archiveStatus,
      createdAt: '2026-06-06T04:05:00Z',
      updatedAt: '2026-06-06T04:09:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Archive a saved run.',
      activeBranchId: 'branch-archive',
      counts: { branches: 1, episodes: 0, tools: 0, gates: 0, artifacts: 0, evidence: 0, wiki: 0, graph: 0, timeline: 0, skills: 0, events: archiveStatus === 'archived' ? 2 : 1 }
    }
  ],
  total: 2,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
})

const makeActiveRunResponse = (latestEvent = null) => ({
  id: activeRunId,
  title: activeTitle,
  goal: 'Maintain saved backend runs.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T04:00:00Z',
  updatedAt: '2026-06-06T04:04:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Maintain saved backend runs.',
  activeBranchId: 'branch-maintenance',
  selectedNodeId: 'branch-maintenance',
  branches: [{ id: 'branch-maintenance', title: 'Maintenance Branch', branchType: 'governance', status: 'ready', evidenceIds: ['ev-maintenance'] }],
  episodes: [{ id: 'episode-maintenance', runId: activeRunId, branchId: 'branch-maintenance', actor: 'agent', toolCalls: ['tool-maintenance'], gateResults: ['gate-maintenance'], artifactIds: [] }],
  toolTraces: [{ id: 'tool-maintenance', branchId: 'branch-maintenance', name: 'worldline.rename_run', status: 'completed', permission: 'worldline:write', summary: 'Rename active run.' }],
  gateResults: [{ id: 'gate-maintenance', label: 'Maintenance audit', status: 'passed', value: 'recorded', threshold: 'latest event' }],
  evidenceRefs: [{ id: 'ev-maintenance', evidenceId: 'ev-maintenance', title: 'Maintenance evidence', sourceUri: 'qa/maintenance.md' }],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [],
  artifacts: [],
  events: [
    { id: 'evt-maintenance-created', runId: activeRunId, branchId: '', eventType: 'run.created', actor: 'qa-admin', summary: {} },
    { id: 'evt-maintenance-loaded', runId: activeRunId, branchId: 'branch-maintenance', eventType: 'run.loaded', actor: 'qa-admin', summary: {} }
  ],
  ...(latestEvent ? { latestEvent } : {})
})

const artifactListResponse = { run_id: activeRunId, items: [], total: 0, limit: 100, offset: 0 }

const makeArchiveResponse = () => ({
  id: archivedRunId,
  title: archiveTitle,
  status: 'archived',
  archivedAt: '2026-06-06T04:12:00Z',
  archivedBy: 'qa-admin',
  latestEvent: {
    id: 'evt-archive-candidate',
    runId: archivedRunId,
    eventType: 'run.archived',
    actor: 'qa-admin',
    summary: { previousStatus: 'ready', status: 'archived', reason: 'operator archive from Agent Workbench selector' }
  }
})

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
    } else if (url.endsWith(`/api/worldline/runs/${activeRunId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, makeActiveRunResponse())
    } else if (url.endsWith(`/api/worldline/runs/${activeRunId}/artifacts`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactListResponse)
    } else if (url.endsWith(`/api/worldline/runs/${activeRunId}/rename`) && method === 'POST') {
      activeTitle = renamedTitle
      await fulfillJson(client, event.requestId, makeActiveRunResponse({
        id: 'evt-run-renamed',
        runId: activeRunId,
        eventType: 'run.renamed',
        actor: 'qa-admin',
        summary: { oldTitle: initialTitle, newTitle: renamedTitle, reason: 'operator rename from Agent Workbench selector' }
      }))
    } else if (url.endsWith(`/api/worldline/runs/${archivedRunId}/archive`) && method === 'POST') {
      archiveStatus = 'archived'
      await fulfillJson(client, event.requestId, makeArchiveResponse())
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
  await waitFor(client, "Boolean(document.querySelector('[data-run-maintenance=\"true\"]'))", 'run maintenance form')

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
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(archiveTitle)})`, 'archive candidate listed')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${activeRunId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      return true
    }
  )()`)
  await waitFor(client, `document.querySelector('.ledger-status')?.innerText.includes(${JSON.stringify(activeRunId)})`, 'active run loaded')

  await evaluate(client, `(
    async () => {
      const input = document.querySelector('[data-run-rename-title="true"]')
      input.value = ${JSON.stringify(renamedTitle)}
      input.dispatchEvent(new Event('input', { bubbles: true }))
      document.querySelector('[data-run-rename-active="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      return true
    }
  )()`)
  await waitFor(client, `document.querySelector('.run-card h2')?.innerText.includes(${JSON.stringify(renamedTitle)})`, 'active run renamed')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-archive="${archivedRunId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      return true
    }
  )()`)
  await waitFor(client, `document.body.innerText.includes('Archived run ${archiveTitle}.')`, 'archive message')

  const state = await evaluate(client, `(() => ({
    title: document.querySelector('.run-card h2')?.innerText || '',
    ledger: document.querySelector('.ledger-status')?.innerText || '',
    selector: document.querySelector('[data-run-selector="true"]')?.innerText || '',
    maintenance: document.querySelector('[data-run-maintenance="true"]')?.innerText || '',
    archiveButtonDisabled: document.querySelector('[data-run-selector-archive="${archivedRunId}"]')?.disabled || false
  }))()`)
  if (!state.title.includes(renamedTitle)) throw new Error(`Run title did not update: ${state.title}`)
  if (!state.ledger.includes(activeRunId)) throw new Error(`Active ledger run changed unexpectedly: ${state.ledger}`)
  if (!state.selector.includes('archived')) throw new Error(`Archived status not visible in selector: ${state.selector}`)
  if (!state.selector.includes(`Archived run ${archiveTitle}.`)) throw new Error(`Archive message missing: ${state.selector}`)
  if (!state.archiveButtonDisabled) throw new Error('Archived row archive button should be disabled')

  for (const expected of [
    `/api/worldline/runs/${activeRunId}/rename`,
    `/api/worldline/runs/${archivedRunId}/archive`
  ]) {
    if (!capturedRequests.some((item) => item.includes(expected))) {
      throw new Error(`Missing request ${expected}: ${capturedRequests.join('\n')}`)
    }
  }

  const image = await screenshot(client, 'run-maintenance-audit.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
