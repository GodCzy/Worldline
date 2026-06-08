import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9392)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-05-agent-run-resource-drilldown/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runId = 'run-agent-resource-drilldown'
const artifactId = 'replay-export-drilldown'

const runResponse = {
  id: runId,
  title: 'Agent Resource Drilldown Run',
  status: 'synced',
  protocolVersion: 'worldline-run-ledger-v0.1',
  events: [{ id: 'evt-run-created', eventType: 'run.created', label: 'Run Created', summary: {} }],
  artifacts: []
}

const manifestResponse = {
  status: 'ok',
  contractVersion: 'worldline-run-mcp-manifest-v0.1',
  run_id: runId,
  run: {
    id: runId,
    title: 'Agent Resource Drilldown Run',
    status: 'synced',
    uri: `worldline-run-ledger://${runId}`
  },
  sections: {
    artifacts: {
      id: 'artifacts',
      label: 'Replay Artifacts',
      tool: 'worldline.inspect_run_artifacts',
      count: 1,
      resources: [
        {
          id: artifactId,
          label: 'Replay Export Drilldown',
          kind: 'replay_export',
          uri: `worldline-run-ledger://${runId}/artifacts/${artifactId}`,
          tool: 'worldline.inspect_run_artifacts',
          args: {
            run_id: runId,
            artifact_id: artifactId,
            include_content: false,
            audit_db_id: ''
          }
        }
      ]
    },
    gates: { id: 'gates', label: 'Quality Gates', tool: 'worldline.inspect_run_gates', count: 0, resources: [] },
    evidence: { id: 'evidence', label: 'Evidence Anchors', tool: 'worldline.inspect_run_evidence', count: 0, resources: [] },
    sources: { id: 'sources', label: 'Source Assets', tool: 'worldline.inspect_run_evidence', count: 0, resources: [] },
    wiki: { id: 'wiki', label: 'Wiki Pages', tool: 'worldline.inspect_run_knowledge', count: 0, resources: [] },
    graph: { id: 'graph', label: 'Knowledge Entities', tool: 'worldline.inspect_run_knowledge', count: 0, resources: [] },
    timeline: { id: 'timeline', label: 'Temporal Facts', tool: 'worldline.inspect_run_knowledge', count: 0, resources: [] }
  },
  resourceCounts: { artifacts: 1, gates: 0, evidence: 0, sources: 0, wiki: 0, graph: 0, timeline: 0 },
  tools: [
    { name: 'worldline.inspect_run_manifest', write_scope: 'none', dispatch_backend: 'inline' },
    { name: 'worldline.inspect_run_artifacts', write_scope: 'none', dispatch_backend: 'inline' }
  ],
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const artifactDetailResponse = {
  status: 'ok',
  run_id: runId,
  artifact_id: artifactId,
  content_included: true,
  selected: {
    id: artifactId,
    label: 'Replay Export Drilldown',
    kind: 'replay_export',
    uri: `worldline-run-ledger://${runId}/artifacts/${artifactId}`,
    content_summary: {
      protocol: 'worldline-agent-workbench-v0.1',
      run_title: 'Agent Resource Drilldown Run',
      replay_steps: 2
    },
    content: {
      protocol: 'worldline-agent-workbench-v0.1',
      run: { title: 'Agent Resource Drilldown Run' },
      replayTimeline: [{ index: 1, label: 'Run Preview' }, { index: 2, label: 'Artifact Drilldown' }]
    }
  },
  items: [],
  total: 1,
  limit: 20,
  offset: 0,
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
    } else if (url.endsWith('/api/worldline/runs') && method === 'POST') {
      await fulfillJson(client, event.requestId, runResponse)
    } else if (url.includes(`/api/worldline/runs/${runId}/manifest`)) {
      await fulfillJson(client, event.requestId, manifestResponse)
    } else if (url.includes(`/api/worldline/runs/${runId}/artifacts/read`)) {
      await fulfillJson(client, event.requestId, artifactDetailResponse)
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
  await waitFor(client, "Boolean(document.querySelector('[data-run-manifest-api-inspector=\"true\"]'))", 'manifest API inspector')

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

  await waitFor(client, "Boolean(document.querySelector('.sync-action:not(.secondary):not(:disabled)'))", 'enabled run sync action')
  await evaluate(client, `(
    async () => {
      document.querySelector('.sync-action:not(.secondary)')?.click()
      await new Promise((resolve) => setTimeout(resolve, 500))
      return true
    }
  )()`)
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(runId)})`, 'synced mock run id')
  await waitFor(
    client,
    "Array.from(document.querySelectorAll('[data-run-mcp-manifest=\"true\"] button')).some((button) => button.textContent.includes('Load Backend Manifest') && !button.disabled)",
    'enabled backend manifest button'
  )

  await evaluate(client, `(
    async () => {
      const panel = document.querySelector('[data-run-mcp-manifest="true"]')
      const button = Array.from(panel.querySelectorAll('button'))
        .find((item) => item.textContent.includes('Load Backend Manifest'))
      button.click()
      await new Promise((resolve) => setTimeout(resolve, 500))
      return true
    }
  )()`)
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(`worldline-run-ledger://${runId}/artifacts/${artifactId}`)})`, 'manifest artifact resource')

  const result = await evaluate(client, `(
    async () => {
      const resource = Array.from(document.querySelectorAll('.run-manifest-api-resources li'))
        .find((item) => item.textContent.includes(${JSON.stringify(artifactId)}))
      if (!resource) return { error: 'resource_not_found' }
      resource.querySelector('button')?.click()
      await new Promise((resolve) => setTimeout(resolve, 650))
      const detail = document.querySelector('[data-run-resource-drilldown="true"]')
      detail?.scrollIntoView({ block: 'center' })
      await new Promise((resolve) => setTimeout(resolve, 250))
      return {
        resource: resource.innerText,
        detail: detail?.innerText || ''
      }
    }
  )()`)
  if (result.error) throw new Error(`Resource drilldown QA failed: ${result.error}`)
  for (const expected of ['Resource Detail', 'Loaded', 'Replay Export Drilldown', artifactId, 'worldline.inspect_run_artifacts']) {
    if (!result.detail.toLowerCase().includes(expected.toLowerCase())) {
      throw new Error(`Detail missing ${expected}: ${result.detail}`)
    }
  }
  if (!capturedRequests.some((item) => item.includes(`/api/worldline/runs/${runId}/artifacts/read`) && item.includes(`artifact_id=${artifactId}`))) {
    throw new Error(`Artifact drilldown API request was not captured: ${capturedRequests.join('\n')}`)
  }

  const image = await screenshot(client, 'run-resource-drilldown.png')
  console.log(JSON.stringify({
    status: 'ok',
    resource: result.resource,
    detail: result.detail,
    capturedRequests,
    screenshot: image
  }, null, 2))
} finally {
  client.close()
}
