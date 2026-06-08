import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'

const port = Number(process.env.CDP_PORT || 9412)
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-07-knowledge-graph-state-ux/screenshots'
)
const profileDir = path.resolve(
  process.env.CHROME_PROFILE_DIR || '.ai/tasks/2026-06-07-knowledge-graph-state-ux/chrome-profile-cdp'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const getJson = async (url) => {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  return await response.json()
}

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
  return spawn(resolveChromePath(), [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    '--disable-extensions',
    '--disable-sync',
    '--window-size=1440,920',
    'about:blank'
  ], {
    detached: false,
    stdio: 'ignore',
    windowsHide: true
  })
}

const waitForCdp = async () => {
  for (let i = 0; i < 40; i += 1) {
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
  const result = await client.send('Page.captureScreenshot', {
    format: 'png',
    captureBeyondViewport: true,
    fromSurface: true
  })
  const filePath = path.join(screenshotDir, name)
  fs.writeFileSync(filePath, Buffer.from(result.data, 'base64'))
  return filePath
}

const graphReason = 'Neo4j 暂不可用：请检查 docker logs api-dev 和 graph service 配置'
const dbId = 'kb_graph_state'

const databaseInfo = {
  db_id: dbId,
  name: '世界线图谱知识库',
  description: '用于验证 LightRAG 图谱空态与后端降级提示。',
  kb_type: 'lightrag',
  embed_info: { name: 'siliconflow/BAAI/bge-m3' },
  additional_params: {
    chunk_preset_id: 'general',
    auto_generate_questions: false
  },
  share_config: { is_shared: true, accessible_departments: [] },
  files: {
    doc_1: {
      file_id: 'doc_1',
      filename: 'worldline-graph.md',
      is_folder: false,
      status: 'done',
      created_at: '2026-06-07T12:00:00Z'
    }
  }
}

const graphListResponse = {
  success: true,
  data: [
    {
      id: 'neo4j',
      name: '默认图谱',
      type: 'upload',
      status: 'unavailable',
      available: false,
      degraded: true,
      degraded_reason: graphReason,
      node_count: 0,
      edge_count: 0,
      capabilities: { supports_embedding: true, supports_threshold: true }
    },
    {
      id: dbId,
      name: '世界线图谱知识库',
      type: 'lightrag',
      status: 'active',
      available: false,
      degraded: true,
      degraded_reason: graphReason,
      node_count: 0,
      edge_count: 0,
      capabilities: { supports_embedding: false, supports_threshold: false }
    }
  ]
}

const graphStatsResponse = {
  success: true,
  data: {
    total_nodes: 0,
    total_edges: 0,
    entity_types: [],
    available: false,
    degraded: true,
    degraded_reason: graphReason,
    database_id: dbId
  },
  degraded: true,
  message: graphReason
}

const graphSubgraphResponse = {
  success: true,
  data: {
    nodes: [],
    edges: [],
    available: false,
    degraded: true,
    degraded_reason: graphReason,
    database_id: dbId,
    graph_type: 'lightrag'
  },
  degraded: true,
  message: graphReason
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
    if (url.endsWith('/api/auth/me')) {
      await fulfillJson(client, event.requestId, {
        user_id: 'qa-admin',
        username: 'qa-admin',
        user_id_login: 'qa-admin',
        role: 'admin',
        department_id: null,
        department_name: ''
      })
    } else if (url.endsWith('/api/system/info')) {
      await fulfillJson(client, event.requestId, { name: 'Worldline QA', status: 'ok' })
    } else if (url.endsWith('/api/chat/agent')) {
      await fulfillJson(client, event.requestId, { agents: [] })
    } else if (url.endsWith('/api/departments')) {
      await fulfillJson(client, event.requestId, { departments: [] })
    } else if (url.endsWith('/api/knowledge/files/supported-types')) {
      await fulfillJson(client, event.requestId, { file_types: ['md', 'txt', 'pdf'] })
    } else if (url.endsWith('/api/knowledge/databases')) {
      await fulfillJson(client, event.requestId, { databases: [databaseInfo] })
    } else if (url.endsWith(`/api/knowledge/databases/${dbId}`) && method === 'GET') {
      await fulfillJson(client, event.requestId, databaseInfo)
    } else if (url.includes('/api/graph/list')) {
      await fulfillJson(client, event.requestId, graphListResponse)
    } else if (url.includes('/api/graph/stats')) {
      await fulfillJson(client, event.requestId, graphStatsResponse)
    } else if (url.includes('/api/graph/subgraph')) {
      await fulfillJson(client, event.requestId, graphSubgraphResponse)
    } else if (url.endsWith('/api/graph/neo4j/info')) {
      await fulfillJson(client, event.requestId, {
        success: true,
        data: {
          graph_name: 'neo4j',
          entity_count: 0,
          relationship_count: 0,
          status: 'unavailable',
          available: false,
          degraded: true,
          degraded_reason: graphReason,
          embed_model_configurable: false,
          unindexed_node_count: 0
        },
        degraded: true,
        message: graphReason
      })
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
  await client.send('Page.navigate', { url: 'http://127.0.0.1:5173/' })
  await waitFor(client, 'Boolean(document.querySelector("#app"))', 'app root')
  await evaluate(client, `(() => {
    window.__qaConsoleErrors = []
    const originalError = console.error
    console.error = (...args) => {
      window.__qaConsoleErrors.push(args.map(String).join(' '))
      originalError(...args)
    }
    localStorage.setItem('user_token', 'qa-token')
    return true
  })()`)

  await client.send('Page.navigate', { url: `http://127.0.0.1:5173/graph?db_id=${dbId}` })
  await waitFor(client, "document.body.innerText.includes('知识图谱')", 'global graph title')
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(graphReason)})`, 'global graph degraded reason')
  await waitFor(client, "document.body.innerText.includes('重新读取图谱')", 'global graph retry button')
  await waitFor(client, "document.body.innerText.includes('前往知识库页面')", 'global graph database action')
  const globalShot = await screenshot(client, 'knowledge-graph-global-state.png')

  await client.send('Page.navigate', { url: `http://127.0.0.1:5173/database/${dbId}` })
  await waitFor(client, "document.body.innerText.includes('世界线图谱知识库')", 'database graph title')
  await waitFor(client, "document.body.innerText.includes('来源：/api/graph/subgraph')", 'graph source summary')
  await waitFor(client, "document.body.innerText.includes('图谱服务暂不可用或处于降级状态')", 'database graph degraded card')
  await waitFor(client, `document.body.innerText.includes(${JSON.stringify(graphReason)})`, 'database graph reason')
  await waitFor(client, "document.body.innerText.includes('重新读取图谱')", 'database graph retry button')
  const databaseShot = await screenshot(client, 'knowledge-graph-database-state.png')

  const errors = await evaluate(client, `(() => window.__qaConsoleErrors || [])()`)
  console.log(JSON.stringify({
    status: 'ok',
    screenshots: {
      global: globalShot,
      database: databaseShot
    },
    capturedRequests,
    errors
  }, null, 2))
} finally {
  client.close()
  if (chromeProcess) chromeProcess.kill()
}
