import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9399)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-selector-pagination/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runStates = Array.from({ length: 10 }, (_, index) => {
  const number = index + 1
  return {
    id: `run-page-${String(number).padStart(2, '0')}`,
    title: `Paged Run ${number}`,
    status: number === 10 ? 'archived' : 'ready',
    events: 2
  }
})

const makeRunListResponse = (url) => {
  const parsed = new URL(url)
  const limit = Number(parsed.searchParams.get('limit') || 8)
  const offset = Number(parsed.searchParams.get('offset') || 0)
  return {
    items: runStates.slice(offset, offset + limit).map((state, index) => ({
      id: state.id,
      title: state.title,
      status: state.status,
      createdAt: `2026-06-06T07:${String(index).padStart(2, '0')}:00Z`,
      updatedAt: `2026-06-06T07:${String(index + offset).padStart(2, '0')}:30Z`,
      createdBy: 'qa-admin',
      themeId: 'agent-workbench',
      rootQuestion: 'Page through saved backend runs.',
      activeBranchId: `branch-${state.id}`,
      counts: { branches: 1, episodes: 1, tools: 1, gates: 1, artifacts: 0, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 0, events: state.events }
    })),
    total: runStates.length,
    limit,
    offset,
    filters: { query: '', status: '', themeId: '', createdBy: '' },
    storage: { type: 'worldline_run_ledger', read_only: true }
  }
}

const archiveRun = (runId) => {
  const state = runStates.find((item) => item.id === runId)
  if (!state) return null
  state.status = 'archived'
  state.events += 1
  return {
    id: runId,
    title: state.title,
    status: state.status,
    latestEvent: {
      id: `evt-archive-${runId}`,
      runId,
      eventType: 'run.archived',
      actor: 'qa-admin',
      summary: {
        previousStatus: 'ready',
        status: 'archived',
        reason: 'operator archive from Agent Workbench selector'
      }
    }
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
      await fulfillJson(client, event.requestId, makeRunListResponse(url))
    } else {
      const archiveMatch = url.match(/\/api\/worldline\/runs\/([^/]+)\/archive$/)
      if (archiveMatch && method === 'POST') {
        const result = archiveRun(archiveMatch[1])
        if (!result) await fulfillJson(client, event.requestId, { detail: 'missing' }, 404)
        else await fulfillJson(client, event.requestId, result)
      } else {
        await client.send('Fetch.continueRequest', { requestId: event.requestId })
      }
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
  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-pagination=\"true\"]') || document.querySelector('[data-run-selector-refresh=\"true\"]'))", 'run selector shell')

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
      await new Promise((resolve) => setTimeout(resolve, 800))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelectorAll('[data-run-selector-item]').length === 8", 'first page loaded')
  await waitFor(client, "document.querySelector('[data-run-selector-load-more=\"true\"]:not(:disabled)')", 'load more enabled')

  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-selector-load-more="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 800))
      return true
    }
  )()`)
  await waitFor(client, "document.querySelectorAll('[data-run-selector-item]').length === 10", 'second page appended')
  await waitFor(client, "document.body.innerText.includes('10/10 loaded')", 'loaded count')

  await evaluate(client, `(
    async () => {
      const input = document.querySelector('[data-run-selector-select="run-page-09"]')
      if (input && !input.checked) input.click()
      await new Promise((resolve) => setTimeout(resolve, 250))
      document.querySelector('[data-run-bulk-archive="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return true
    }
  )()`)
  await waitFor(client, "document.body.innerText.includes('Archived 1/1 selected runs.')", 'page two bulk archive message')
  await waitFor(client, "document.body.innerText.includes('run-page-09 / archived')", 'page two row archived')

  const state = await evaluate(client, `(() => ({
    selector: document.querySelector('[data-run-selector="true"]')?.innerText || '',
    itemCount: document.querySelectorAll('[data-run-selector-item]').length,
    checkedCount: Array.from(document.querySelectorAll('[data-run-selector-select]')).filter((item) => item.checked).length,
    loadMoreDisabled: document.querySelector('[data-run-selector-load-more="true"]')?.disabled || false
  }))()`)
  if (state.itemCount !== 10) throw new Error(`Expected 10 loaded rows: ${JSON.stringify(state)}`)
  if (state.checkedCount !== 0) throw new Error(`Selection should be cleared after archive: ${state.checkedCount}`)
  if (!state.loadMoreDisabled) throw new Error('Load More should be disabled after all rows are loaded')
  for (const expected of [
    '/api/worldline/runs?limit=8&offset=0',
    '/api/worldline/runs?limit=8&offset=8',
    '/api/worldline/runs/run-page-09/archive'
  ]) {
    if (!capturedRequests.some((item) => item.includes(expected))) {
      throw new Error(`Missing request ${expected}: ${capturedRequests.join('\n')}`)
    }
  }

  const image = await screenshot(client, 'run-selector-pagination.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
