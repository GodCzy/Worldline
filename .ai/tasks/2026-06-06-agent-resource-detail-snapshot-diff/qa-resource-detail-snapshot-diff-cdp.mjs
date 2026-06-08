import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'

const port = Number(process.env.CDP_PORT || 9406)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-resource-detail-snapshot-diff/screenshots'
)
const profileDir = path.resolve(
  process.env.CHROME_PROFILE_DIR || '.ai/tasks/2026-06-06-agent-resource-detail-snapshot-diff/chrome-profile-cdp'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const resolveChromePath = () => {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
  ].filter(Boolean)
  const found = candidates.find((candidate) => fs.existsSync(candidate))
  if (!found) throw new Error(`Chrome executable not found. Tried: ${candidates.join(', ')}`)
  return found
}

const isCdpReady = async () => {
  try {
    const targets = await getJson(`http://127.0.0.1:${port}/json/list`)
    return targets.some((target) => target.type === 'page' && target.webSocketDebuggerUrl)
  } catch {
    return false
  }
}

const startChrome = async () => {
  if (await isCdpReady()) return null
  fs.rmSync(profileDir, { recursive: true, force: true })
  fs.mkdirSync(profileDir, { recursive: true })
  const chrome = spawn(resolveChromePath(), [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    '--disable-extensions',
    '--disable-sync',
    '--window-size=1440,900',
    'about:blank'
  ], {
    detached: false,
    stdio: 'ignore',
    windowsHide: true
  })
  chrome.on('error', (error) => {
    throw error
  })
  return chrome
}

const runId = 'run-resource-detail-diff'
const branchId = 'branch-resource-detail-diff'
const sourceArtifactId = 'source-001'
const savedArtifactId = 'resource-detail-run-resource-detail-diff-source-001'

const sourceArtifact = {
  id: sourceArtifactId,
  runId,
  branchId,
  eventId: 'evt-002-source-artifact',
  kind: 'qa-evidence',
  label: 'Current Source Detail',
  summary: 'Current source artifact for Resource Detail diff.',
  uri: `worldline-run-ledger://${runId}/artifacts/${sourceArtifactId}`,
  has_content: true
}

const savedArtifact = {
  id: savedArtifactId,
  runId,
  branchId,
  eventId: 'evt-003-saved-snapshot',
  kind: 'resource_detail_snapshot',
  format: 'json+markdown',
  label: 'Resource Detail: Saved Source Detail',
  summary: 'Saved baseline Resource Detail snapshot.',
  uri: `worldline-run-ledger://${runId}/artifacts/${savedArtifactId}`,
  has_content: true,
  has_markdown: true
}

const currentInspectResponse = {
  tool: 'worldline.inspect_run_artifacts',
  run_id: runId,
  selected: {
    id: sourceArtifactId,
    label: 'Current Source Detail',
    type: 'qa-evidence',
    content: 'Current detail content changed.',
    status: 'current'
  },
  meta: {
    risk: 'high',
    newOnly: 'current-only'
  },
  items: [{ id: sourceArtifactId, label: 'Current Source Detail', type: 'qa-evidence' }],
  total: 1
}

const savedSnapshot = {
  schema: 'worldline.resource_detail_snapshot.v0.1',
  exportedAt: '2026-06-06T14:00:00.000Z',
  run: { id: runId, title: 'Resource Detail Diff Run' },
  resource: {
    id: sourceArtifactId,
    key: `event-token:artifact:${sourceArtifactId}`,
    section: 'Event Artifact',
    sectionKey: 'artifacts',
    uri: `worldline-run-ledger://${runId}/artifact/${sourceArtifactId}`,
    tool: 'worldline.inspect_run_artifacts',
    args: { run_id: runId, artifact_id: sourceArtifactId }
  },
  selected: {
    id: sourceArtifactId,
    label: 'Saved Source Detail',
    type: 'qa-evidence',
    content: 'Saved baseline content.',
    status: 'saved'
  },
  response: {
    tool: 'worldline.inspect_run_artifacts',
    run_id: runId,
    selected: {
      id: sourceArtifactId,
      label: 'Saved Source Detail',
      type: 'qa-evidence',
      content: 'Saved baseline content.',
      status: 'saved'
    },
    meta: {
      risk: 'low',
      oldOnly: 'saved-only'
    },
    items: [{ id: sourceArtifactId, label: 'Saved Source Detail', type: 'qa-evidence' }],
    total: 1
  }
}

const events = [
  {
    id: 'evt-002-source-artifact',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'artifact-registry',
    summary: {
      artifactIds: [sourceArtifactId],
      artifactDetails: [sourceArtifact]
    },
    createdAt: '2026-06-06T14:01:00Z'
  },
  {
    id: 'evt-003-saved-snapshot',
    runId,
    branchId,
    eventType: 'artifact.registered',
    actor: 'qa-admin',
    summary: {
      artifactIds: [savedArtifactId],
      artifactDetails: [savedArtifact]
    },
    createdAt: '2026-06-06T14:02:00Z'
  },
  {
    id: 'evt-001-run-created',
    runId,
    branchId: '',
    eventType: 'run.created',
    actor: 'qa-admin',
    summary: { status: 'ready', title: 'Resource Detail Diff Run' },
    createdAt: '2026-06-06T14:00:00Z'
  }
]

const runListResponse = {
  items: [
    {
      id: runId,
      title: 'Resource Detail Diff Run',
      status: 'ready',
      createdAt: '2026-06-06T14:00:00Z',
      updatedAt: '2026-06-06T14:02:00Z',
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Diff current Resource Detail against saved snapshot.',
      activeBranchId: branchId,
      counts: { branches: 1, episodes: 1, tools: 1, gates: 0, artifacts: 2, evidence: 0, wiki: 0, graph: 0, timeline: 0, skills: 0, events: 3 }
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
  title: 'Resource Detail Diff Run',
  goal: 'Diff current Resource Detail against saved snapshot.',
  status: 'ready',
  createdBy: 'qa-admin',
  createdAt: '2026-06-06T14:00:00Z',
  updatedAt: '2026-06-06T14:02:00Z',
  protocolVersion: 'worldline-run-ledger-v0.1',
  themeId: 'agent-workbench',
  moduleId: 'agent-workbench',
  rootQuestion: 'Diff current Resource Detail against saved snapshot.',
  activeBranchId: branchId,
  selectedNodeId: branchId,
  branches: [{ id: branchId, title: 'Detail Diff Branch', branchType: 'evidence', status: 'approved', artifactIds: [sourceArtifactId, savedArtifactId] }],
  episodes: [{ id: 'episode-resource-detail-diff', runId, branchId, actor: 'agent', toolCalls: [], gateResults: [], artifactIds: [sourceArtifactId, savedArtifactId] }],
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

const artifactListResponse = { run_id: runId, items: [savedArtifact], total: 1, limit: 100, offset: 0 }
const currentArtifactReadResponse = {
  status: 'ok',
  tool: 'worldline.inspect_run_artifacts',
  run_id: runId,
  artifact_id: sourceArtifactId,
  selected: {
    ...sourceArtifact,
    content: currentInspectResponse.selected.content
  },
  ...currentInspectResponse,
  content_included: true,
  storage: { type: 'worldline_run_ledger', read_only: true }
}
const savedArtifactReadResponse = {
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

const eventPageResponse = (url) => {
  const parsed = new URL(url)
  const limit = Number(parsed.searchParams.get('limit') || 6)
  const offset = Number(parsed.searchParams.get('offset') || 0)
  return { run_id: runId, items: events.slice(offset, offset + limit), total: events.length, limit, offset }
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

const chromeProcess = await startChrome()
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
      const parsed = new URL(url)
      const artifactId = parsed.searchParams.get('artifact_id')
      await fulfillJson(
        client,
        event.requestId,
        artifactId === savedArtifactId ? savedArtifactReadResponse : currentArtifactReadResponse
      )
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
  await waitFor(client, `Array.from(document.querySelectorAll('.event-item')).some((item) => item.innerText.includes('ArtifactIds: ["${sourceArtifactId}"]'))`, 'source artifact event visible')
  await evaluate(client, `(
    async () => {
      const eventItem = Array.from(document.querySelectorAll('.event-item'))
        .find((item) => item.innerText.includes('ArtifactIds: ["${sourceArtifactId}"]'))
      eventItem?.click()
      await new Promise((resolve) => setTimeout(resolve, 600))
      return true
    }
  )()`)
  await waitFor(client, `Boolean(document.querySelector('[data-event-detail-token="artifact:${sourceArtifactId}"]'))`, 'source artifact token')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-event-detail-token="artifact:${sourceArtifactId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelector('[data-run-resource-drilldown=\"true\"]')?.innerText.includes('Current detail content changed.')", 'current detail loaded')
  await waitFor(client, `Boolean(document.querySelector('[data-resource-detail-diff="${savedArtifactId}"]:not(:disabled)'))`, 'diff detail button enabled')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-resource-detail-diff="${savedArtifactId}"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.body.innerText.includes('Compared current Resource Detail with Saved Source Detail')", 'diff message')
  await waitFor(client, "document.querySelector('[data-resource-detail-diff-panel=\"true\"]')?.innerText.includes('response.selected.content')", 'changed path visible')

  if (!capturedRequests.some((item) =>
    item.includes(`/api/worldline/runs/${runId}/artifacts/read`) &&
    item.includes(`artifact_id=${savedArtifactId}`) &&
    item.includes('include_content=true')
  )) {
    throw new Error(`Missing saved snapshot read request: ${capturedRequests.join('\n')}`)
  }

  const state = await evaluate(client, `(() => ({
    diff: document.querySelector('[data-resource-detail-diff-panel="true"]')?.innerText || '',
    lastMcp: document.querySelector('[data-last-mcp-call="true"]')?.innerText || '',
    resource: document.querySelector('[data-run-resource-drilldown="true"]')?.innerText || ''
  }))()`)
  if (!state.diff.includes('ADDED') || !state.diff.includes('REMOVED') || !state.diff.includes('CHANGED')) {
    throw new Error(`Diff counts missing: ${JSON.stringify(state)}`)
  }
  if (!state.lastMcp.includes('Registry Diff') || !state.lastMcp.includes('include_content')) {
    throw new Error(`Last MCP diff call missing: ${JSON.stringify(state)}`)
  }

  await evaluate(client, `(() => {
    document.querySelector('[data-resource-detail-diff-panel="true"]')?.scrollIntoView({ block: 'center', inline: 'nearest' })
    return true
  })()`)
  await sleep(500)
  const image = await screenshot(client, 'resource-detail-snapshot-diff.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
  if (chromeProcess) {
    chromeProcess.kill()
    await sleep(500)
    fs.rmSync(profileDir, { recursive: true, force: true })
  }
}
