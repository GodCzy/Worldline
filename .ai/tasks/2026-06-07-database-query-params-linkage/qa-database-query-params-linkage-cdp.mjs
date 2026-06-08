import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'

const port = Number(process.env.CDP_PORT || 9411)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/database/kb_query_params'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-07-database-query-params-linkage/screenshots'
)
const profileDir = path.resolve(
  process.env.CHROME_PROFILE_DIR || '.ai/tasks/2026-06-07-database-query-params-linkage/chrome-profile-cdp'
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

const clickCenter = async (client, elementExpression, label) => {
  const rect = await evaluate(client, `(() => {
    const element = ${elementExpression}
    if (!element) return null
    element.scrollIntoView({ block: 'center', inline: 'center' })
    const box = element.getBoundingClientRect()
    return {
      x: box.left + box.width / 2,
      y: box.top + box.height / 2
    }
  })()`)
  if (!rect) throw new Error(`Unable to find element for ${label}`)
  await client.send('Input.dispatchMouseEvent', {
    type: 'mousePressed',
    button: 'left',
    clickCount: 1,
    x: rect.x,
    y: rect.y
  })
  await client.send('Input.dispatchMouseEvent', {
    type: 'mouseReleased',
    button: 'left',
    clickCount: 1,
    x: rect.x,
    y: rect.y
  })
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

const milvusQueryParams = {
  params: {
    type: 'milvus',
    options: [
      {
        key: 'search_mode',
        label: '检索模式',
        type: 'select',
        default: 'hybrid',
        options: [
          { value: 'vector', label: '向量检索', description: '仅使用向量相似度检索' },
          { value: 'keyword', label: '关键词检索', description: '仅使用关键词匹配检索' },
          { value: 'hybrid', label: '混合检索', description: '向量检索与关键词检索融合' }
        ],
        description: '选择检索模式'
      },
      {
        key: 'final_top_k',
        label: '最终返回 Chunk 数',
        type: 'number',
        default: 10,
        min: 1,
        max: 100,
        description: '重排序后返回给前端的文档数量'
      },
      {
        key: 'similarity_threshold',
        label: '相似度阈值（0-1）',
        type: 'number',
        default: 0.2,
        min: 0,
        max: 1,
        step: 0.1,
        description: '过滤相似度低于此值的结果'
      },
      {
        key: 'keyword_top_k',
        label: '使用关键词召回的最大 Chunk 数',
        type: 'number',
        default: 50,
        min: 1,
        max: 200,
        description: '关键词/混合检索时的候选数量'
      },
      {
        key: 'include_distances',
        label: '显示相似度',
        type: 'boolean',
        default: true,
        description: '在结果中显示相似度分数'
      },
      {
        key: 'metric_type',
        label: '距离度量类型',
        type: 'select',
        default: 'COSINE',
        options: [
          { value: 'COSINE', label: '余弦相似度', description: '适合文本语义相似度' },
          { value: 'L2', label: '欧几里得距离', description: '适合数值型数据' }
        ],
        description: '向量相似度计算方法'
      },
      {
        key: 'use_reranker',
        label: '启用重排序',
        type: 'boolean',
        default: false,
        description: '是否使用精排模型对检索结果进行重排序'
      },
      {
        key: 'reranker_model',
        label: '重排序模型',
        type: 'select',
        default: '',
        options: [
          { value: 'siliconflow/BAAI/bge-reranker-v2-m3', label: 'BAAI/bge-reranker-v2-m3' },
          { value: 'jina/reranker-v2-base-multilingual', label: 'jina-reranker-v2-base' }
        ],
        description: '选择用于本次查询的重排序模型'
      },
      {
        key: 'recall_top_k',
        label: '召回数量',
        type: 'number',
        default: 50,
        min: 10,
        max: 200,
        description: '向量检索时保留的候选数量（启用重排序时有效）'
      }
    ]
  },
  message: 'success'
}

const databaseInfo = {
  db_id: 'kb_query_params',
  name: '世界线检索知识库',
  description: '用于验证 CommonRAG 检索参数与后端 query-params 契约联通。',
  kb_type: 'milvus',
  embed_info: { name: 'siliconflow/BAAI/bge-m3' },
  additional_params: {
    chunk_preset_id: 'general',
    auto_generate_questions: false
  },
  share_config: { is_shared: true, accessible_departments: [] },
  files: {
    doc_1: {
      file_id: 'doc_1',
      filename: 'worldline.md',
      is_folder: false,
      status: 'done',
      created_at: '2026-06-07T12:00:00Z'
    }
  }
}

const chromeProcess = await startChrome()
const webSocketUrl = await waitForCdp()
const client = await createClient(webSocketUrl)
const capturedRequests = []
const updatePayloads = []

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
    } else if (url.endsWith('/api/departments')) {
      await fulfillJson(client, event.requestId, { departments: [] })
    } else if (url.endsWith('/api/knowledge/databases/kb_query_params') && method === 'GET') {
      await fulfillJson(client, event.requestId, databaseInfo)
    } else if (url.endsWith('/api/knowledge/databases/kb_query_params/query-params') && method === 'GET') {
      await fulfillJson(client, event.requestId, milvusQueryParams)
    } else if (url.endsWith('/api/knowledge/databases/kb_query_params/query-params') && method === 'PUT') {
      const payload = JSON.parse(event.request.postData || '{}')
      updatePayloads.push(payload)
      await fulfillJson(client, event.requestId, { message: 'success', data: payload })
    } else if (url.endsWith('/api/knowledge/databases/kb_query_params/sample-questions')) {
      await fulfillJson(client, event.requestId, { questions: ['世界线如何使用证据驱动分支？'] })
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
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "document.body.innerText.includes('世界线检索知识库')", 'database detail title')
  await waitFor(client, "document.body.innerText.includes('检索测试')", 'query tab')

  await evaluate(client, `(() => {
    Array.from(document.querySelectorAll('button')).find((item) => item.innerText.includes('检索配置'))?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('后端联通')", 'contract strip')
  await waitFor(client, "document.body.innerText.includes('CommonRAG 检索参数')", 'kb type heading')
  await waitFor(client, "document.body.innerText.includes('检索范围')", 'retrieval group')
  await waitFor(client, "document.body.innerText.includes('重排序')", 'reranker group')
  await waitFor(client, "document.body.innerText.includes('启用重排序')", 'use reranker control')
  await waitFor(client, "document.body.innerText.includes('后端请求预览')", 'payload preview header')
  await evaluate(client, `(() => {
    const header = Array.from(document.querySelectorAll('.ant-collapse-header'))
      .find((node) => node.innerText.includes('后端请求预览'))
    header?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('/api/knowledge/databases/kb_query_params/query-params')", 'payload preview open')
  const shot = await screenshot(client, 'database-query-params-linkage.png')

  await clickCenter(
    client,
    `Array.from(document.querySelectorAll('button[role="switch"]'))
      .find((node) => node.closest('.ant-form-item')?.innerText.includes('启用重排序'))`,
    'use reranker switch'
  )
  await sleep(300)

  await clickCenter(
    client,
    `Array.from(document.querySelectorAll('.ant-form-item'))
      .find((node) => node.innerText.includes('重排序模型'))
      ?.querySelector('.ant-select-selector')`,
    'reranker model select'
  )
  await waitFor(client, "document.body.innerText.includes('BAAI/bge-reranker-v2-m3')", 'reranker option')
  await clickCenter(
    client,
    `Array.from(document.querySelectorAll('.ant-select-item-option'))
      .find((node) => node.innerText.includes('BAAI/bge-reranker-v2-m3'))`,
    'reranker option'
  )
  await waitFor(client, "document.body.innerText.includes('siliconflow/BAAI/bge-reranker-v2-m3')", 'payload selected reranker')

  await evaluate(client, `(() => {
    Array.from(document.querySelectorAll('.ant-modal-footer button'))
      .find((item) => item.innerText.includes('保存到后端'))?.click()
    return true
  })()`)
  for (let i = 0; i < 30 && updatePayloads.length === 0; i += 1) {
    await sleep(300)
  }
  if (updatePayloads.length === 0) {
    throw new Error('No query params update payload captured')
  }

  const payload = updatePayloads.at(-1)
  if (payload.use_reranker !== true) {
    const switchDebug = await evaluate(client, `(() => Array.from(document.querySelectorAll('button[role="switch"]')).map((node) => ({
      text: node.closest('.ant-form-item')?.innerText || '',
      ariaChecked: node.getAttribute('aria-checked'),
      className: node.className
    })))()`)
    throw new Error(`Expected use_reranker=true, got ${JSON.stringify(payload)}; switches=${JSON.stringify(switchDebug)}`)
  }
  if (payload.reranker_model !== 'siliconflow/BAAI/bge-reranker-v2-m3') {
    throw new Error(`Expected selected reranker model, got ${JSON.stringify(payload)}`)
  }
  if (payload.final_top_k !== 10 || payload.recall_top_k !== 50 || payload.include_distances !== true) {
    throw new Error(`Expected full backend payload, got ${JSON.stringify(payload)}`)
  }

  const errors = await evaluate(client, `(() => window.__qaConsoleErrors || [])()`)
  console.log(JSON.stringify({
    status: 'ok',
    screenshot: shot,
    payload,
    capturedRequests,
    errors
  }, null, 2))
} finally {
  client.close()
  if (chromeProcess) chromeProcess.kill()
}
