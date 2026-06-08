import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9395)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-cross-run-diff/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const leftRunId = 'run-cross-diff-left'
const rightRunId = 'run-cross-diff-right'
const leftTitle = 'Active Diff Run'
const rightTitle = 'Candidate Diff Run'

const runListResponse = {
  items: [
    {
      id: leftRunId,
      title: leftTitle,
      status: 'ready',
      createdAt: '2026-06-06T03:00:00Z',
      updatedAt: '2026-06-06T03:04:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Compare the active run against another saved run.',
      activeBranchId: 'branch-left',
      counts: { branches: 1, episodes: 1, tools: 1, gates: 1, artifacts: 1, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 0, events: 2 }
    },
    {
      id: rightRunId,
      title: rightTitle,
      status: 'ready',
      createdAt: '2026-06-06T03:05:00Z',
      updatedAt: '2026-06-06T03:08:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Candidate run with extra evidence.',
      activeBranchId: 'branch-right',
      counts: { branches: 2, episodes: 1, tools: 1, gates: 2, artifacts: 0, evidence: 2, wiki: 1, graph: 1, timeline: 1, skills: 1, events: 3 }
    }
  ],
  total: 2,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const leftRunResponse = {
  id: leftRunId,
  title: leftTitle,
  goal: 'Compare the active run against another saved run.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T03:00:00Z',
  updatedAt: '2026-06-06T03:04:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Compare the active run against another saved run.',
  activeBranchId: 'branch-left',
  selectedNodeId: 'branch-left',
  branches: [
    { id: 'branch-left', title: 'Current Evidence Branch', branchType: 'evidence', status: 'ready', evidenceIds: ['ev-left'] }
  ],
  episodes: [{ id: 'episode-left', runId: leftRunId, branchId: 'branch-left', actor: 'agent', toolCalls: ['tool-left'], gateResults: ['gate-left'], artifactIds: ['artifact-left'] }],
  toolTraces: [{ id: 'tool-left', branchId: 'branch-left', name: 'worldline.inspect_run_manifest', status: 'completed', permission: 'worldline:read', summary: 'Inspect current run.' }],
  gateResults: [{ id: 'gate-left', label: 'Current coverage', status: 'passed', value: '1', threshold: '>= 1' }],
  evidenceRefs: [{ id: 'ev-left', evidenceId: 'ev-left', title: 'Current evidence', sourceUri: 'qa/current.md' }],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [],
  artifacts: [{ id: 'artifact-left', label: 'Current Artifact', kind: 'replay_export' }],
  events: [
    { id: 'evt-left-created', runId: leftRunId, branchId: '', eventType: 'run.created', actor: 'qa-admin', summary: {} },
    { id: 'evt-left-loaded', runId: leftRunId, branchId: 'branch-left', eventType: 'run.loaded', actor: 'qa-admin', summary: {} }
  ]
}

const artifactListResponse = { run_id: leftRunId, items: [], total: 0, limit: 100, offset: 0 }

const compareResponse = {
  status: 'ok',
  contractVersion: 'worldline-run-compare-v0.1',
  left: { id: leftRunId, title: leftTitle, status: 'ready', counts: runListResponse.items[0].counts },
  right: { id: rightRunId, title: rightTitle, status: 'ready', counts: runListResponse.items[1].counts },
  summary: { added: 5, removed: 1, changed: 2, shared: 3, sectionsChanged: 5 },
  sections: {
    branches: {
      key: 'branches',
      label: 'Branches',
      counts: { added: 1, removed: 0, changed: 1, shared: 0 },
      added: [{ id: 'branch-right-extra', label: 'Candidate Extra Branch', status: 'ready', type: 'evidence' }],
      removed: [],
      changed: [{ id: 'branch-left', before: { label: 'Current Evidence Branch' }, after: { label: 'Current Evidence Branch Revised' } }],
      shared: []
    },
    gates: { key: 'gates', label: 'Gates', counts: { added: 1, removed: 0, changed: 1, shared: 0 }, added: [], removed: [], changed: [], shared: [] },
    artifacts: { key: 'artifacts', label: 'Artifacts', counts: { added: 0, removed: 1, changed: 0, shared: 0 }, added: [], removed: [{ id: 'artifact-left', label: 'Current Artifact' }], changed: [], shared: [] }
  },
  timeline: [
    { key: 'branches', label: 'Branches', added: 1, removed: 0, changed: 1, shared: 0, totalDelta: 2 },
    { key: 'gates', label: 'Gates', added: 1, removed: 0, changed: 1, shared: 0, totalDelta: 2 },
    { key: 'artifacts', label: 'Artifacts', added: 0, removed: 1, changed: 0, shared: 0, totalDelta: 1 }
  ],
  storage: { type: 'worldline_run_ledger', read_only: true }
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
      await fulfillJson(client, event.requestId, runListResponse)
    } else if (url.endsWith(`/api/worldline/runs/${leftRunId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, leftRunResponse)
    } else if (url.endsWith(`/api/worldline/runs/${leftRunId}/artifacts`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactListResponse)
    } else if (url.includes('/api/worldline/runs/compare') && method === 'GET') {
      await fulfillJson(client, event.requestId, compareResponse)
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
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(rightTitle)})`, 'candidate run listed')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${leftRunId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      return true
    }
  )()`)
  await waitFor(client, `document.querySelector('.ledger-status')?.innerText.includes(${JSON.stringify(leftRunId)})`, 'left run loaded')

  const compared = await evaluate(client, `(
    async () => {
      const compare = document.querySelector('[data-run-selector-compare="${rightRunId}"]')
      if (!compare) return { error: 'compare_button_missing' }
      compare.click()
      await new Promise((resolve) => setTimeout(resolve, 900))
      const panel = document.querySelector('[data-run-diff-panel="true"]')
      panel?.scrollIntoView({ block: 'center' })
      await new Promise((resolve) => setTimeout(resolve, 250))
      return {
        panel: panel?.innerText || '',
        activeTitle: document.querySelector('.run-card h2')?.innerText || '',
        ledger: document.querySelector('.ledger-status')?.innerText || ''
      }
    }
  )()`)
  if (compared.error) throw new Error(`Compare QA failed: ${compared.error}`)
  const panelText = compared.panel.toLowerCase()
  for (const expected of ['RUN DIFF', leftTitle, rightTitle, '8 deltas', 'Branches', 'Artifacts', '+1 / -0 / Δ1']) {
    if (!panelText.includes(expected.toLowerCase())) throw new Error(`Diff panel missing ${expected}: ${compared.panel}`)
  }
  if (!compared.activeTitle.includes(leftTitle)) {
    throw new Error(`Compare should not switch active run title: ${compared.activeTitle}`)
  }
  if (!compared.ledger.includes(leftRunId)) {
    throw new Error(`Compare should not switch active ledger run: ${compared.ledger}`)
  }
  const compareRequest = capturedRequests.find((item) => item.includes('/api/worldline/runs/compare'))
  if (!compareRequest) throw new Error(`Compare request was not captured: ${capturedRequests.join('\n')}`)
  for (const expected of [`left_run_id=${leftRunId}`, `right_run_id=${rightRunId}`]) {
    if (!compareRequest.includes(expected)) throw new Error(`Compare request missing ${expected}: ${compareRequest}`)
  }

  const image = await screenshot(client, 'cross-run-diff-panel.png')
  console.log(JSON.stringify({ status: 'ok', compared, compareRequest, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
