import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9405)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-resource-detail-artifact-replay/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-resource-detail-replay'
const branchId = 'branch-resource-detail-replay'
const savedArtifactId = 'resource-detail-run-resource-detail-replay-source-001'
const selectedSourceId = 'source-001'
const savedSnapshot = {
  schema: 'worldline.resource_detail_snapshot.v0.1',
  exportedAt: '2026-06-06T13:30:00.000Z',
  run: { id: runId, title: 'Resource Detail Replay Run' },
  resource: {
    id: selectedSourceId,
    key: `event-token:artifact:${selectedSourceId}`,
    section: 'Event Artifact',
    sectionKey: 'artifacts',
    uri: `worldline-run-ledger://${runId}/artifact/${selectedSourceId}`,
    tool: 'worldline.inspect_run_artifacts',
    args: { run_id: runId, artifact_id: selectedSourceId }
  },
  selected: {
    id: selectedSourceId,
    label: 'Saved Source Detail',
    type: 'qa-evidence',
    content: 'Replay restored inspect content from saved snapshot.'
  },
  selectedEvent: {
    id: 'evt-002-resource-detail-saved',
    eventType: 'artifact.registered',
    branchId,
    actor: 'qa-admin'
  },
  focusedDossier: {
    type: 'artifact',
    title: 'Saved Source Detail',
    badge: 'qa-evidence',
    summary: 'Saved snapshot source detail.'
  },
  response: {
    tool: 'worldline.inspect_run_artifacts',
    run_id: runId,
    selected: {
      id: selectedSourceId,
      label: 'Saved Source Detail',
      type: 'qa-evidence',
      content: 'Replay restored inspect content from saved snapshot.'
    },
    total: 1
  }
}

const savedArtifact = {
  id: savedArtifactId,
  runId,
  branchId,
  eventId: 'evt-002-resource-detail-saved',
  kind: 'resource_detail_snapshot',
  format: 'json+markdown',
  label: 'Resource Detail: Saved Source Detail',
  summary: 'Saved resource detail snapshot for replay.',
  uri: `worldline-run-ledger://${runId}/artifacts/${savedArtifactId}`,
  has_content: true,
  has_markdown: true,
  content_summary: { schema: savedSnapshot.schema, selected: 'Saved Source Detail' }
}

const events = [
  {
    id: 'evt-002-resource-detail-saved',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'qa-admin',
    summary: {
      artifactIds: [savedArtifactId],
      artifactDetails: [savedArtifact]
    },
    createdAt: '2026-06-06T13:31:00Z'
  },
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Resource Detail Replay Run' },
    createdAt: '2026-06-06T13:30:00Z'
  }
]

const runListResponse = {
  items: [
    {
      id: runId,
      title: 'Resource Detail Replay Run',
      status: 'ready',
      createdAt: '2026-06-06T13:30:00Z',
      updatedAt: '2026-06-06T13:31:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Replay saved resource detail artifact.',
      activeBranchId: branchId,
      counts: { branches: 1, episodes: 1, tools: 1, gates: 0, artifacts: 1, evidence: 0, wiki: 0, graph: 0, timeline: 0, skills: 0, events: 2 }
    }
  ],
  total: 1,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const runDetailResponse = {
  id: runId,
  title: 'Resource Detail Replay Run',
  goal: 'Replay saved resource detail artifact.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T13:30:00Z',
  updatedAt: '2026-06-06T13:31:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Replay saved resource detail artifact.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [{ id: branchId, title: 'Replay Detail Branch', branchType: 'evidence', status: 'approved', artifactIds: [savedArtifactId] }],
  episodes: [{ id: 'episode-resource-detail-replay', runId, branchId, actor: 'agent', toolCalls: [], gateResults: [], artifactIds: [savedArtifactId] }],
  toolTraces: [],
  gateResults: [],
  evidenceRefs: [],
  wikiRefs: [],
  entityRefs: [],
  timelineRefs: [],
  skillProposals: [],
  artifacts: [savedArtifact],
  events
}

const eventPageResponse = (url) => {
  const parsed = new URL(url)
  const limit = Number(parsed.searchParams.get('limit') || 6)
  const offset = Number(parsed.searchParams.get('offset') || 0)
  return { run_id: runId, items: events.slice(offset, offset + limit), total: events.length, limit, offset }
}

const artifactListResponse = { run_id: runId, items: [savedArtifact], total: 1, limit: 100, offset: 0 }
const artifactReadResponse = {
  status: 'ok',
  tool: 'worldline.inspect_run_artifacts',
  run_id: runId,
  artifact_id: savedArtifactId,
  selected: {
    ...savedArtifact,
    content: savedSnapshot,
    markdown: '# Worldline Resource Detail Snapshot\n\nSaved Source Detail'
  },
  items: [{ ...savedArtifact, content: savedSnapshot }],
  total: 1,
  content_included: true,
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
    } else if (url.endsWith(`/api/worldline/runs/${runId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, runDetailResponse)
    } else if (url.match(/\/api\/worldline\/runs\/[^/]+\/events(?:\?|$)/) && method === 'GET') {
      await fulfillJson(client, event.requestId, eventPageResponse(url))
    } else if (url.endsWith(`/api/worldline/runs/${runId}/artifacts`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactListResponse)
    } else if (url.includes(`/api/worldline/runs/${runId}/artifacts/read`) && method === 'GET') {
      await fulfillJson(client, event.requestId, artifactReadResponse)
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
  await waitFor(client, `Boolean(document.querySelector('[data-run-selector-load="${runId}"]'))`, 'run visible')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load="${runId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, `Boolean(document.querySelector('[data-resource-detail-replay="${savedArtifactId}"]:not(:disabled)'))`, 'read detail button enabled')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-resource-detail-replay="${savedArtifactId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.body.innerText.includes('Replayed saved resource detail snapshot: Saved Source Detail.')", 'replay message')
  await waitFor(client, "document.querySelector('[data-run-resource-drilldown=\"true\"]')?.innerText.includes('Replay restored inspect content from saved snapshot.')", 'snapshot content restored')

  if (!capturedRequests.some((item) =>
    item.includes(`/api/worldline/runs/${runId}/artifacts/read`) &&
    item.includes(`artifact_id=${savedArtifactId}`) &&
    item.includes('include_content=true')
  )) {
    throw new Error(`Missing artifact read request: ${capturedRequests.join('\n')}`)
  }

  const state = await evaluate(client, `(() => ({
    resource: document.querySelector('[data-run-resource-drilldown="true"]')?.innerText || '',
    registry: document.querySelector('[data-artifact-registry="true"]')?.innerText || '',
    lastMcp: document.querySelector('[data-last-mcp-call="true"]')?.innerText || ''
  }))()`)
  if (!state.registry.includes('Resource Detail: Saved Source Detail')) {
    throw new Error(`Snapshot artifact missing from registry: ${JSON.stringify(state)}`)
  }
  if (!state.lastMcp.includes('include_content') || !state.lastMcp.includes('true')) {
    throw new Error(`Last MCP call did not expose include_content=true: ${JSON.stringify(state)}`)
  }

  await evaluate(client, `(() => {
    document.querySelector('[data-run-resource-drilldown="true"]')?.scrollIntoView({ block: 'center', inline: 'nearest' })
    return true
  })()`)
  await sleep(500)
  const image = await screenshot(client, 'resource-detail-artifact-replay.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
