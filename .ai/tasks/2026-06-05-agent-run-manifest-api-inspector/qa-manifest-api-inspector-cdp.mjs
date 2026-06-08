import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9391)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-05-agent-run-manifest-api-inspector/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const manifest = {
  status: 'ok',
  contractVersion: 'worldline-run-mcp-manifest-v0.1',
  run_id: 'run-agent-workbench-api',
  run: {
    id: 'run-agent-workbench-api',
    title: 'Agent Workbench API Run',
    status: 'synced',
    activeBranchId: 'branch-runtime',
    protocolVersion: 'worldline-run-ledger-v0.1',
    uri: 'worldline-run-ledger://run-agent-workbench-api'
  },
  sections: {
    artifacts: {
      id: 'artifacts',
      label: 'Replay Artifacts',
      tool: 'worldline.inspect_run_artifacts',
      count: 2,
      resources: [
        {
          id: 'replay-export',
          label: 'Replay Export',
          kind: 'replay_export',
          uri: 'worldline-run-ledger://run-agent-workbench-api/artifacts/replay-export',
          tool: 'worldline.inspect_run_artifacts',
          args: { run_id: 'run-agent-workbench-api', artifact_id: 'replay-export' }
        }
      ]
    },
    gates: {
      id: 'gates',
      label: 'Quality Gates',
      tool: 'worldline.inspect_run_gates',
      count: 4,
      resources: [
        {
          id: 'gate-evidence',
          label: 'Evidence coverage',
          kind: 'gate',
          uri: 'worldline-run-ledger://run-agent-workbench-api/gates/gate-evidence',
          tool: 'worldline.inspect_run_gates',
          args: { run_id: 'run-agent-workbench-api', gate_id: 'gate-evidence' }
        }
      ]
    },
    evidence: {
      id: 'evidence',
      label: 'Evidence Anchors',
      tool: 'worldline.inspect_run_evidence',
      count: 3,
      resources: [
        {
          id: 'ev-runtime',
          label: 'Runtime evidence',
          kind: 'evidence',
          uri: 'worldline-run-ledger://run-agent-workbench-api/evidence/ev-runtime',
          tool: 'worldline.inspect_run_evidence',
          args: { run_id: 'run-agent-workbench-api', evidence_id: 'ev-runtime' }
        }
      ]
    },
    sources: {
      id: 'sources',
      label: 'Source Assets',
      tool: 'worldline.inspect_run_evidence',
      count: 2,
      resources: [
        {
          id: 'source-runtime',
          label: 'Runtime source',
          kind: 'source',
          uri: 'worldline-run-ledger://run-agent-workbench-api/sources/source-runtime',
          tool: 'worldline.inspect_run_evidence',
          args: { run_id: 'run-agent-workbench-api', source_id: 'source-runtime' }
        }
      ]
    },
    wiki: {
      id: 'wiki',
      label: 'Wiki Pages',
      tool: 'worldline.inspect_run_knowledge',
      count: 2,
      resources: [
        {
          id: 'wiki-agent-os',
          label: 'Agent Worldline OS',
          kind: 'wiki',
          uri: 'worldline-run-ledger://run-agent-workbench-api/wiki/wiki-agent-os',
          tool: 'worldline.inspect_run_knowledge',
          args: { run_id: 'run-agent-workbench-api', kind: 'wiki', item_id: 'wiki-agent-os' }
        }
      ]
    },
    graph: {
      id: 'graph',
      label: 'Knowledge Entities',
      tool: 'worldline.inspect_run_knowledge',
      count: 3,
      resources: [
        {
          id: 'entity-runtime',
          label: 'Runtime Entity',
          kind: 'graph',
          uri: 'worldline-run-ledger://run-agent-workbench-api/graph/entity-runtime',
          tool: 'worldline.inspect_run_knowledge',
          args: { run_id: 'run-agent-workbench-api', kind: 'graph', item_id: 'entity-runtime' }
        }
      ]
    },
    timeline: {
      id: 'timeline',
      label: 'Temporal Facts',
      tool: 'worldline.inspect_run_knowledge',
      count: 2,
      resources: [
        {
          id: 'tf-runtime',
          label: 'Runtime fact',
          kind: 'timeline',
          uri: 'worldline-run-ledger://run-agent-workbench-api/timeline/tf-runtime',
          tool: 'worldline.inspect_run_knowledge',
          args: { run_id: 'run-agent-workbench-api', kind: 'timeline', item_id: 'tf-runtime' }
        }
      ]
    }
  },
  resourceCounts: {
    artifacts: 2,
    gates: 4,
    evidence: 3,
    sources: 2,
    wiki: 2,
    graph: 3,
    timeline: 2
  },
  tools: [
    { name: 'worldline.inspect_run_manifest', write_scope: 'none', dispatch_backend: 'inline' },
    { name: 'worldline.inspect_run_artifacts', write_scope: 'none', dispatch_backend: 'inline' },
    { name: 'worldline.inspect_run_gates', write_scope: 'none', dispatch_backend: 'inline' },
    { name: 'worldline.inspect_run_evidence', write_scope: 'none', dispatch_backend: 'inline' },
    { name: 'worldline.inspect_run_knowledge', write_scope: 'none', dispatch_backend: 'inline' }
  ],
  storage: { type: 'worldline_run_ledger', read_only: true }
}

const runResponse = {
  id: 'run-agent-workbench-api',
  title: 'Agent Workbench API Run',
  status: 'synced',
  protocolVersion: 'worldline-run-ledger-v0.1',
  events: [
    {
      id: 'evt-run-created',
      eventType: 'run.created',
      label: 'Run Created',
      summary: { evidenceIds: ['ev-runtime'] }
    }
  ],
  artifacts: []
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
    if (url.endsWith('/api/auth/me')) {
      await fulfillJson(client, event.requestId, {
        id: 'qa-admin',
        user_id: 'qa-admin',
        username: 'qa-admin',
        role: 'admin',
        avatar: '',
        department_id: null,
        department_name: ''
      })
    } else if (url.endsWith('/api/worldline/runs') && method === 'POST') {
      await fulfillJson(client, event.requestId, runResponse)
    } else if (url.includes('/api/worldline/runs/run-agent-workbench-api/manifest')) {
      await fulfillJson(client, event.requestId, manifest)
    } else if (url.includes('/api/worldline/runs/run-agent-workbench-api/events')) {
      await fulfillJson(client, event.requestId, { total: 1, items: runResponse.events })
    } else if (url.includes('/api/worldline/runs/run-agent-workbench-api/artifacts')) {
      await fulfillJson(client, event.requestId, { total: 0, items: [] })
    } else {
      await client.send('Fetch.continueRequest', { requestId: event.requestId })
    }
  } catch (error) {
    await client.send('Fetch.failRequest', { requestId: event.requestId, errorReason: 'Failed' })
    throw error
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
  await waitFor(client, "document.body.innerText.includes('run-agent-workbench-api')", 'synced mock run id')
  await waitFor(
    client,
    "Array.from(document.querySelectorAll('[data-run-mcp-manifest=\"true\"] button')).some((button) => button.textContent.includes('Load Backend Manifest') && !button.disabled)",
    'enabled backend manifest button'
  )

  const result = await evaluate(client, `(
    async () => {
      const panel = document.querySelector('[data-run-mcp-manifest="true"]')
      const button = Array.from(panel.querySelectorAll('button'))
        .find((item) => item.textContent.includes('Load Backend Manifest'))
      button.click()
      await new Promise((resolve) => setTimeout(resolve, 600))
      const inspector = document.querySelector('[data-run-manifest-api-inspector="true"]')
      return {
        panel: panel.innerText,
        inspector: inspector?.innerText || ''
      }
    }
  )()`)

  for (const expected of ['BACKEND MANIFEST', 'LOADED', 'worldline.inspect_run_manifest', 'worldline.inspect_run_artifacts', 'run-agent-workbench-api']) {
    if (!result.inspector.toUpperCase().includes(expected.toUpperCase())) {
      throw new Error(`Inspector missing ${expected}: ${result.inspector}`)
    }
  }
  if (!capturedRequests.some((item) => item.includes('/api/worldline/runs/run-agent-workbench-api/manifest'))) {
    throw new Error(`Manifest API request was not captured: ${capturedRequests.join('\n')}`)
  }

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-manifest-api-inspector="true"]')?.scrollIntoView({ block: 'center' })
      await new Promise((resolve) => setTimeout(resolve, 250))
      return true
    }
  )()`)
  const image = await screenshot(client, 'run-manifest-api-inspector.png')
  console.log(JSON.stringify({
    status: 'ok',
    inspector: result.inspector,
    capturedRequests,
    screenshot: image
  }, null, 2))
} finally {
  client.close()
}
