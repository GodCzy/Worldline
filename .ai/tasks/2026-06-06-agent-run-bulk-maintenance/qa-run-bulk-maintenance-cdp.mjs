import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9398)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-06-agent-run-bulk-maintenance/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const runStates = {
  'run-bulk-ready-one': { title: 'Bulk Ready One', status: 'ready', events: 2 },
  'run-bulk-ready-two': { title: 'Bulk Ready Two', status: 'approved', events: 2 },
  'run-bulk-archived': { title: 'Bulk Archived', status: 'archived', events: 2 }
}

const makeRunListResponse = () => ({
  items: Object.entries(runStates).map(([id, state], index) => ({
    id,
    title: state.title,
    status: state.status,
    createdAt: `2026-06-06T06:0${index}:00Z`,
    updatedAt: `2026-06-06T06:1${index}:00Z`,
    createdBy: 'qa-admin',
    themeId: 'agent-workbench',
    rootQuestion: 'Bulk maintain saved backend runs.',
    activeBranchId: `branch-${id}`,
    counts: { branches: 1, episodes: 1, tools: 1, gates: 1, artifacts: 0, evidence: 1, wiki: 0, graph: 0, timeline: 0, skills: 0, events: state.events }
  })),
  total: 3,
  limit: 8,
  offset: 0,
  filters: { query: '', status: '', themeId: '', createdBy: '' },
  storage: { type: 'worldline_run_ledger', read_only: true }
})

const mutationResponse = (runId, eventType, nextStatus) => {
  const state = runStates[runId]
  state.status = nextStatus
  state.events += 1
  return {
    id: runId,
    title: state.title,
    status: state.status,
    latestEvent: {
      id: `evt-${eventType}-${runId}`,
      runId,
      eventType,
      actor: 'qa-admin',
      summary: {
        previousStatus: eventType === 'run.archived' ? 'ready' : 'archived',
        status: state.status,
        reason: eventType === 'run.archived'
          ? 'operator archive from Agent Workbench selector'
          : 'operator restore from Agent Workbench selector'
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
      await fulfillJson(client, event.requestId, makeRunListResponse())
    } else {
      const archiveMatch = url.match(/\/api\/worldline\/runs\/([^/]+)\/archive$/)
      const restoreMatch = url.match(/\/api\/worldline\/runs\/([^/]+)\/restore$/)
      if (archiveMatch && method === 'POST') {
        await fulfillJson(client, event.requestId, mutationResponse(archiveMatch[1], 'run.archived', 'archived'))
      } else if (restoreMatch && method === 'POST') {
        await fulfillJson(client, event.requestId, mutationResponse(restoreMatch[1], 'run.restored', 'ready'))
      } else {
        await client.send('Fetch.continueRequest', { requestId: event.requestId })
      }
    }
  } catch {
    await client.send('Fetch.failRequest', { requestId: event.requestId, errorReason: 'Failed' })
  }
})

const setChecked = async (client, runIds) => {
  await evaluate(client, `(
    async () => {
      for (const id of ${JSON.stringify(runIds)}) {
        const input = document.querySelector('[data-run-selector-select="' + id + '"]')
        if (input && !input.checked) {
          input.click()
          await new Promise((resolve) => setTimeout(resolve, 150))
        }
      }
      await new Promise((resolve) => setTimeout(resolve, 250))
      return true
    }
  )()`)
}

try {
  await client.send('Runtime.enable')
  await client.send('Page.enable')
  await client.send('Fetch.enable', {
    patterns: [{ urlPattern: '*://127.0.0.1:5173/api/*' }, { urlPattern: '*://localhost:5173/api/*' }]
  })
  await client.send('Page.addScriptToEvaluateOnNewDocument', { source: "localStorage.removeItem('user_token')" })
  await client.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false })
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "Boolean(document.querySelector('[data-run-selector-bulk=\"true\"]'))", 'bulk selector')

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
  await waitFor(client, "document.querySelectorAll('[data-run-selector-select]').length === 3", 'three selectable runs')

  await setChecked(client, ['run-bulk-ready-one', 'run-bulk-ready-two'])
  await waitFor(client, "document.querySelector('[data-run-bulk-archive=\"true\"]:not(:disabled)')", 'bulk archive enabled')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-bulk-archive="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1200))
      return true
    }
  )()`)
  await waitFor(client, "document.body.innerText.includes('Archived 2/2 selected runs.')", 'bulk archive message')
  await waitFor(client, "document.body.innerText.includes('run-bulk-ready-one / archived') && document.body.innerText.includes('run-bulk-ready-two / archived')", 'bulk archive statuses')

  await setChecked(client, ['run-bulk-ready-one', 'run-bulk-ready-two', 'run-bulk-archived'])
  await waitFor(client, "document.querySelector('[data-run-bulk-restore=\"true\"]:not(:disabled)')", 'bulk restore enabled')
  await evaluate(client, `(
    async () => {
      document.querySelector('[data-run-bulk-restore="true"]')?.click()
      await new Promise((resolve) => setTimeout(resolve, 1500))
      return true
    }
  )()`)
  await waitFor(client, "document.body.innerText.includes('Restored 3/3 selected runs.')", 'bulk restore message')

  const state = await evaluate(client, `(() => ({
    selector: document.querySelector('[data-run-selector="true"]')?.innerText || '',
    checkedCount: Array.from(document.querySelectorAll('[data-run-selector-select]')).filter((item) => item.checked).length,
    archiveButtons: document.querySelectorAll('[data-run-selector-archive]').length,
    restoreButtons: document.querySelectorAll('[data-run-selector-restore]').length
  }))()`)
  for (const id of Object.keys(runStates)) {
    if (!state.selector.includes(id + ' / ready')) {
      throw new Error(`Expected ${id} to be ready after restore: ${state.selector}`)
    }
  }
  if (state.checkedCount !== 0) throw new Error(`Selection should be cleared after bulk restore: ${state.checkedCount}`)
  if (state.archiveButtons !== 3 || state.restoreButtons !== 0) {
    throw new Error(`Expected 3 archive buttons and 0 restore buttons: ${JSON.stringify(state)}`)
  }

  for (const expected of [
    '/api/worldline/runs/run-bulk-ready-one/archive',
    '/api/worldline/runs/run-bulk-ready-two/archive',
    '/api/worldline/runs/run-bulk-ready-one/restore',
    '/api/worldline/runs/run-bulk-ready-two/restore',
    '/api/worldline/runs/run-bulk-archived/restore'
  ]) {
    if (!capturedRequests.some((item) => item.includes(expected))) {
      throw new Error(`Missing request ${expected}: ${capturedRequests.join('\n')}`)
    }
  }

  const image = await screenshot(client, 'run-bulk-maintenance.png')
  console.log(JSON.stringify({ status: 'ok', state, capturedRequests, screenshot: image }, null, 2))
} finally {
  client.close()
}
