import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9403)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-event-resource-drilldown/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-event-resource-drilldown'
const branchId = 'branch-event-resource-drilldown'
const artifactId = 'artifact-drilldown-001'

const events = [
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Resource Drilldown Run' },
    createdAt: '2026-06-06T11:00:00Z'
  },
  {
    id: 'evt-002-artifact-registered',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'artifact-registry',
    summary: {
      artifactIds: [artifactId],
      artifactDetails: [
        {
          id: artifactId,
          label: 'Drilldown Artifact',
          kind: 'qa-evidence',
          path: `worldline-run-ledger://${runId}/artifacts/${artifactId}`,
          summary: 'Artifact referenced from a run event.'
        }
      ]
    },
    createdAt: '2026-06-06T11:01:00Z'
  }
]

const makeRunListResponse = () => ({
  items: [
    {
      id: runId,
      title: 'Resource Drilldown Run',
      status: 'ready',
      createdAt: '2026-06-06T11:00:00Z',
      updatedAt: '2026-06-06T11:01:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Inspect event resources from tokens.',
      activeBranchId: branchId,
      counts: { branches: 1, episodes: 1, tools: 1, gates: 0, artifacts: 1, evidence: 0, wiki: 0, graph: 0, timeline: 0, skills: 0, events: events.length }
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
  title: 'Resource Drilldown Run',
  goal: 'Inspect event resources from tokens.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T11:00:00Z',
  updatedAt: '2026-06-06T11:01:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Inspect event resources from tokens.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [{ id: branchId, title: 'Resource Branch', branchType: 'evidence', status: 'approved', artifactIds: [artifactId] }],
  episodes: [{ id: 'episode-resource-drilldown', runId, branchId, actor: 'agent', toolCalls: ['tool-resource-drilldown'], gateResults: [], artifactIds: [artifactId] }],
  toolTraces: [
    {
      id: 'tool-resource-drilldown',
      branchId,
      name: 'worldline.register_artifact',
      status: 'completed',
      permission: 'worldline:write',
      summary: 'Register artifact for resource drilldown.',
      artifactIds: [artifactId],
      artifacts: [
        {
          id: artifactId,
          label: 'Drilldown Artifact',
          kind: 'qa-evidence',
          path: `worldline-run-ledger://${runId}/artifacts/${artifactId}`,
          summary: 'Artifact referenced from a run event.'
        }
      ]
    }
  ],
  gateResults: [],
  evidenceRefs: [],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [],
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

const artifactReadResponse = {
  tool: 'worldline.inspect_run_artifacts',
  run_id: runId,
  selected: {
    id: artifactId,
    label: 'Drilldown Artifact',
    type: 'qa-evidence',
    path: `worldline-run-ledger://${runId}/artifacts/${artifactId}`,
    content: 'Artifact content loaded by resource drilldown.'
  },
  items: [
    {
      id: artifactId,
      label: 'Drilldown Artifact',
      type: 'qa-evidence'
    }
  ],
  total: 1
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
    } else if (url.includes(`/api/worldline/runs/${runId}/artifacts/read`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactReadResponse)
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
  await waitFor(client, `Boolean(document.querySelector('[data-run-selector-load="${runId}"]'))`, 'resource run visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${runId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, `Boolean(document.querySelector('[data-event-detail-token="artifact:${artifactId}"]'))`, 'artifact token visible')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-event-detail-token="artifact:${artifactId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-resource-drilldown=\"true\"]')?.innerText.includes('Loaded Event Artifact Drilldown Artifact')", 'resource detail loaded')

  const state = await evaluate(client, `(() => ({
    dossier: document.querySelector('[data-inspector-dossier="true"]')?.innerText || '',
    resource: document.querySelector('[data-run-resource-drilldown="true"]')?.innerText || '',
    focusMessage: document.querySelector('.event-focus-message')?.innerText || '',
    tokenFocused: document.querySelector('[data-event-detail-token="artifact:${artifactId}"]')?.classList.contains('focused') || false
  }))()`)
  if (!state.dossier.includes('Drilldown Artifact')) {
    throw new Error(`Expected artifact dossier: ${JSON.stringify(state)}`)
  }
  if (!state.resource.includes('worldline.inspect_run_artifacts')) {
    throw new Error(`Expected artifact inspect tool: ${JSON.stringify(state)}`)
  }
  if (!state.resource.includes('Artifact content loaded by resource drilldown.')) {
    throw new Error(`Expected inspect response content: ${JSON.stringify(state)}`)
  }
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/artifacts/read`) && item.includes(`artifact_id=${artifactId}`))) {
    throw new Error(`Missing artifact read request: ${capturedRequests.join('\n')}`)
  }

  await evaluate(client, `(() => {
    document.querySelector('[data-run-resource-drilldown="true"]')?.scrollIntoView({ block: 'center', inline: 'nearest' })
    return true
  })()`)
  await sleep(500)
  const image = await screenshot(client, 'run-event-resource-drilldown.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
