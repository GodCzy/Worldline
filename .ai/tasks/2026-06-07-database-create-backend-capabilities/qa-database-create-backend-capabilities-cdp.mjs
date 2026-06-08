import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'

const port = Number(process.env.CDP_PORT || 9410)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/database'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-07-database-create-backend-capabilities/screenshots'
)
const profileDir = path.resolve(
  process.env.CHROME_PROFILE_DIR || '.ai/tasks/2026-06-07-database-create-backend-capabilities/chrome-profile-cdp'
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
    '--window-size=1440,900',
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
    } else if (url.endsWith('/api/knowledge/databases')) {
      await fulfillJson(client, event.requestId, { databases: [] })
    } else if (url.endsWith('/api/knowledge/types')) {
      await fulfillJson(client, event.requestId, {
        kb_types: {
          milvus: { description: '基于 Milvus 的生产级向量库', class_name: 'MilvusKB' },
          lightrag: { description: '基于 LightRAG 的知识图谱实现', class_name: 'LightRagKB' },
          dify: { description: '基于 Dify Dataset Retrieve API 的只读检索知识库实现', class_name: 'DifyKB' }
        }
      })
    } else if (url.endsWith('/api/knowledge/embedding-models/status')) {
      await fulfillJson(client, event.requestId, {
        status: {
          total: 1,
          available: 1,
          models: {
            'siliconflow/BAAI/bge-m3': { status: 'available', message: 'mock ok' }
          }
        }
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
    localStorage.setItem('user_token', 'qa-token')
    return true
  })()`)
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "document.body.innerText.includes('文档知识库')", 'database page')
  await waitFor(client, "document.body.innerText.includes('新建知识库')", 'create button')

  await evaluate(client, `(() => {
    Array.from(document.querySelectorAll('button')).find((item) => item.innerText.includes('新建知识库'))?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('高级后端配置')", 'advanced section header')
  await evaluate(client, `(() => {
    Array.from(document.querySelectorAll('.ant-collapse-header')).find((item) => item.innerText.includes('高级后端配置'))?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('覆盖分块解析参数')", 'advanced panel open')
  await evaluate(client, `(() => {
    const switches = Array.from(document.querySelectorAll('.backend-advanced-panel button[role=\"switch\"]'))
    switches[0]?.click()
    switches[1]?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('Chunk Token 数')", 'chunk override fields')

  await evaluate(client, `(() => {
    const inputs = Array.from(document.querySelectorAll('.chunk-override-grid input'))
    if (inputs[0]) {
      inputs[0].value = '768'
      inputs[0].dispatchEvent(new Event('input', { bubbles: true }))
      inputs[0].dispatchEvent(new Event('change', { bubbles: true }))
    }
    if (inputs[1]) {
      inputs[1].value = '12'
      inputs[1].dispatchEvent(new Event('input', { bubbles: true }))
      inputs[1].dispatchEvent(new Event('change', { bubbles: true }))
    }
    return true
  })()`)
  await evaluate(client, `(() => {
    Array.from(document.querySelectorAll('button')).find((item) => item.innerText.includes('预览后端请求'))?.click()
    return true
  })()`)
  await waitFor(client, "document.body.innerText.includes('后端创建请求预览')", 'payload preview panel')
  const preview = await evaluate(client, `(() => {
    const panel = document.querySelector('[data-backend-payload-preview="true"]')
    const scrollHost = panel?.closest('.ant-modal-body') || panel?.closest('.ant-modal-content')
    if (panel && scrollHost) {
      scrollHost.scrollTop = Math.max(0, panel.offsetTop - 120)
    }
    const modalWrap = document.querySelector('.ant-modal-wrap')
    if (modalWrap && panel) {
      modalWrap.scrollTop = Math.max(0, panel.getBoundingClientRect().top + modalWrap.scrollTop - 160)
    }
    panel?.scrollIntoView({ block: 'center' })
    return panel?.innerText || ''
  })()`)
  if (!preview.includes('"is_private": true')) {
    throw new Error(`Preview did not include private flag: ${preview}`)
  }
  if (!preview.includes('"chunk_parser_config"')) {
    throw new Error(`Preview did not include chunk_parser_config: ${preview}`)
  }
  if (!preview.includes('"use_raptor": true') || !preview.includes('"use_graphrag": true')) {
    throw new Error(`Preview did not include graph parser toggles: ${preview}`)
  }

  await sleep(500)
  const shot = await screenshot(client, 'database-create-backend-capabilities.png')
  const errors = await evaluate(client, `(() => window.__qaConsoleErrors || [])()`)
  console.log(JSON.stringify({
    status: 'ok',
    screenshot: shot,
    capturedRequests,
    previewExcerpt: preview.slice(0, 1000),
    errors
  }, null, 2))
} finally {
  client.close()
  if (chromeProcess) chromeProcess.kill()
}
