import { mkdir, rm, writeFile } from 'node:fs/promises'
import { request } from 'node:http'
import { spawn } from 'node:child_process'
import { resolve } from 'node:path'

const chromePath = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const root = resolve('.ai/tasks/2026-06-08-theme-module-closure')
const screenshotDir = resolve(root, 'screenshots')
const profileDir = resolve(root, 'chrome-profile-theme-qa')
const port = Number(process.env.CDP_PORT || 9339)
const token = process.env.QA_TOKEN || ''
const dbId = process.env.QA_DB_ID || ''
const themeId = process.env.QA_THEME_ID || ''

if (!token || !dbId || !themeId) {
  throw new Error('QA_TOKEN, QA_DB_ID, and QA_THEME_ID are required.')
}

await mkdir(screenshotDir, { recursive: true })
await rm(profileDir, { recursive: true, force: true })
await mkdir(profileDir, { recursive: true })

const chrome = spawn(
  chromePath,
  [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--hide-scrollbars',
    '--window-size=1440,900',
    'http://127.0.0.1:5173/'
  ],
  { stdio: 'ignore' }
)

const httpJson = (path) =>
  new Promise((resolveJson, reject) => {
    const req = request({ host: '127.0.0.1', port, path, method: 'GET' }, (res) => {
      let body = ''
      res.setEncoding('utf8')
      res.on('data', (chunk) => {
        body += chunk
      })
      res.on('end', () => {
        try {
          resolveJson(JSON.parse(body))
        } catch (error) {
          reject(error)
        }
      })
    })
    req.on('error', reject)
    req.end()
  })

const sleep = (ms) => new Promise((resolveSleep) => setTimeout(resolveSleep, ms))

const waitForTab = async () => {
  const deadline = Date.now() + 30000
  while (Date.now() < deadline) {
    try {
      const tabs = await httpJson('/json/list')
      const tab = tabs.find((item) => item.type === 'page' && item.webSocketDebuggerUrl)
      if (tab) return tab
    } catch {}
    await sleep(250)
  }
  throw new Error('Timed out waiting for Chrome CDP tab.')
}

const cdpTab = await waitForTab()
const ws = new WebSocket(cdpTab.webSocketDebuggerUrl)
await new Promise((resolveOpen, reject) => {
  ws.addEventListener('open', resolveOpen, { once: true })
  ws.addEventListener('error', reject, { once: true })
})

let seq = 0
const pending = new Map()
const eventWaiters = new Map()

ws.addEventListener('message', (event) => {
  const msg = JSON.parse(event.data)
  if (msg.id && pending.has(msg.id)) {
    const { resolve: resolvePending, reject } = pending.get(msg.id)
    pending.delete(msg.id)
    if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)))
    else resolvePending(msg.result || {})
    return
  }
  if (msg.method && eventWaiters.has(msg.method)) {
    const waiters = eventWaiters.get(msg.method)
    eventWaiters.delete(msg.method)
    waiters.forEach((resolveWaiter) => resolveWaiter(msg.params || {}))
  }
})

const send = (method, params = {}) =>
  new Promise((resolveSend, reject) => {
    const id = ++seq
    pending.set(id, { resolve: resolveSend, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })

const waitEvent = (method, timeout = 30000) =>
  new Promise((resolveWait, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timed out waiting for ${method}`)), timeout)
    const wrapped = (params) => {
      clearTimeout(timer)
      resolveWait(params)
    }
    const waiters = eventWaiters.get(method) || []
    waiters.push(wrapped)
    eventWaiters.set(method, waiters)
  })

const evaluate = async (expression) => {
  const result = await send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true
  })
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed')
  }
  return result.result?.value
}

const navigate = async (url) => {
  const loaded = waitEvent('Page.loadEventFired', 45000).catch(() => null)
  await send('Page.navigate', { url })
  await loaded
  await sleep(900)
}

const waitForText = async (text, timeout = 30000) => {
  const deadline = Date.now() + timeout
  while (Date.now() < deadline) {
    const found = await evaluate(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`)
    if (found) return true
    await sleep(350)
  }
  throw new Error(`Timed out waiting for text: ${text}`)
}

const capture = async (filename) => {
  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false })
  await writeFile(resolve(screenshotDir, filename), Buffer.from(shot.data, 'base64'))
}

const pageState = async () =>
  evaluate(`(() => ({
    url: location.href,
    width: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    text: document.body.innerText.slice(0, 5000)
  }))()`)

const newModuleUrl =
  `http://127.0.0.1:5173/themes?new_module=1&db_id=${encodeURIComponent(dbId)}` +
  `&knowledge_db_id=${encodeURIComponent(dbId)}` +
  '&knowledge_name=Codex%20Theme%20Browser%20QA%20KB' +
  '&knowledge_type=codex_test' +
  '&knowledge_description=Temporary%20KB%20for%20theme%20module%20browser%20QA.' +
  '&name=Codex%20Theme%20Browser%20QA%20Draft'
const detailUrl = `http://127.0.0.1:5173/themes/${themeId}`
const workbenchUrl = `http://127.0.0.1:5173/worldline/${themeId}?db_id=${encodeURIComponent(dbId)}&knowledge_db_id=${encodeURIComponent(dbId)}`

try {
  await send('Page.enable')
  await send('Runtime.enable')
  await navigate('http://127.0.0.1:5173/')
  await evaluate(`localStorage.setItem('user_token', ${JSON.stringify(token)})`)

  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false })
  await navigate(newModuleUrl)
  await waitForText('添加自定义模块')
  const createDesktop = await pageState()
  await capture('theme-create-modal-1440x900.png')

  await navigate(detailUrl)
  await waitForText('Codex Browser QA Module')
  const detailDesktop = await pageState()
  await capture('theme-detail-1440x900.png')

  await navigate(workbenchUrl)
  await waitForText('Codex Browser QA Module')
  const workbenchDesktop = await pageState()
  await capture('theme-workbench-1440x900.png')

  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true })
  await navigate(newModuleUrl)
  await waitForText('添加自定义模块')
  const createMobile = await pageState()
  await capture('theme-create-modal-390x844.png')

  await navigate(detailUrl)
  await waitForText('Codex Browser QA Module')
  const detailMobile = await pageState()
  await capture('theme-detail-390x844.png')

  await navigate(workbenchUrl)
  await waitForText('Codex Browser QA Module')
  const workbenchMobile = await pageState()
  await capture('theme-workbench-390x844.png')

  const checks = {
    createDesktop: {
      url: createDesktop.url,
      hasObjective: createDesktop.text.includes('模块目标'),
      hasEvidence: createDesktop.text.includes('证据来源'),
      hasConfigButton: createDesktop.text.includes('能力与生成配置'),
      hasKnowledge: createDesktop.text.includes('Codex Theme Browser QA KB'),
      overflow: createDesktop.overflow
    },
    detailDesktop: {
      url: detailDesktop.url,
      hasKnowledge: detailDesktop.text.includes('Codex Theme Browser QA KB'),
      hasObjective: detailDesktop.text.includes('Validate theme detail and worldline route binding.'),
      hasCapability: detailDesktop.text.includes('模块能力控制台'),
      hasWorkbench: detailDesktop.text.includes('进入世界线工作台'),
      overflow: detailDesktop.overflow
    },
    workbenchDesktop: {
      url: workbenchDesktop.url,
      hasGenerate: workbenchDesktop.text.includes('生成'),
      hasEmptyState:
        workbenchDesktop.text.includes('当前知识库还没有可生成的世界线') ||
        workbenchDesktop.text.includes('后端 facade 暂无可用分支') ||
        workbenchDesktop.text.includes('等待数据'),
      overflow: workbenchDesktop.overflow
    },
    createMobile: { url: createMobile.url, overflow: createMobile.overflow },
    detailMobile: { url: detailMobile.url, overflow: detailMobile.overflow },
    workbenchMobile: { url: workbenchMobile.url, overflow: workbenchMobile.overflow }
  }

  await writeFile(resolve(root, 'theme-module-closure-browser-checks.json'), JSON.stringify(checks, null, 2))
  console.log(JSON.stringify(checks, null, 2))
} finally {
  ws.close()
  chrome.kill()
  await sleep(500)
  await rm(profileDir, { recursive: true, force: true })
}
