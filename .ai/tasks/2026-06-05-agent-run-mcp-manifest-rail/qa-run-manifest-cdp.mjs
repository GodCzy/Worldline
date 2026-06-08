import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9390)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-05-agent-run-mcp-manifest-rail/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const getJson = async (url) => {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`GET ${url} failed: ${response.status}`)
  }
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
  let id = 0

  ws.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data)
    if (!payload.id || !pending.has(payload.id)) return
    const { resolve, reject } = pending.get(payload.id)
    pending.delete(payload.id)
    if (payload.error) reject(new Error(JSON.stringify(payload.error)))
    else resolve(payload.result || {})
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

  return { send, close: () => ws.close() }
}

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

try {
  await client.send('Runtime.enable')
  await client.send('Page.enable')
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 1100,
    deviceScaleFactor: 1,
    mobile: false
  })
  await client.send('Page.navigate', { url: targetUrl })
  await waitFor(client, "Boolean(document.querySelector('[data-run-mcp-manifest=\"true\"]'))", 'run MCP manifest rail')

  const result = await evaluate(client, `(
    async () => {
      const panel = document.querySelector('[data-run-mcp-manifest="true"]')
      if (!panel) return { error: 'panel_not_found' }
      panel.scrollIntoView({ block: 'center' })
      await new Promise((resolve) => setTimeout(resolve, 250))
      const button = Array.from(panel.querySelectorAll('button'))
        .find((item) => item.textContent.includes('Copy Run Manifest'))
      if (!button) return { error: 'button_not_found', panel: panel.innerText }
      button.click()
      await new Promise((resolve) => setTimeout(resolve, 350))
      const last = document.querySelector('[data-last-mcp-call="true"]')
      return {
        panel: panel.innerText,
        last: last?.innerText || '',
        tool: last?.querySelector('.last-mcp-call-meta dd')?.innerText || '',
        argsJson: last?.querySelector('pre')?.innerText || '',
        uri: Array.from(last?.querySelectorAll('.last-mcp-call-meta div') || [])
          .find((item) => item.querySelector('dt')?.innerText === 'URI')
          ?.querySelector('dd')?.innerText || ''
      }
    }
  )()`)

  if (result.error) {
    throw new Error(`Run MCP manifest QA failed: ${result.error} ${result.panel || ''}`)
  }
  const normalizedPanel = result.panel.toLowerCase()
  for (const label of ['Run MCP Manifest', 'Artifacts', 'Gates', 'Evidence', 'Sources', 'Wiki', 'Graph', 'Time']) {
    if (!normalizedPanel.includes(label.toLowerCase())) {
      throw new Error(`Run MCP manifest panel missing ${label}: ${result.panel}`)
    }
  }
  if (!result.last.includes('worldline.inspect_run_manifest')) {
    throw new Error(`Last MCP panel missing run manifest tool: ${result.last}`)
  }
  const args = JSON.parse(result.argsJson)
  if (args.run_id !== 'run-agent-workbench-preview') {
    throw new Error(`Unexpected run_id: ${args.run_id}`)
  }
  if (args.include_resources !== true || args.limit !== 50) {
    throw new Error(`Unexpected manifest args: ${result.argsJson}`)
  }
  if (!result.uri.includes('worldline-run-ledger://run-agent-workbench-preview/manifest')) {
    throw new Error(`Unexpected manifest URI: ${result.uri}`)
  }

  const image = await screenshot(client, 'run-mcp-manifest-rail.png')
  console.log(JSON.stringify({
    status: 'ok',
    runId: args.run_id,
    uri: result.uri,
    panel: result.panel,
    last: result.last,
    screenshot: image
  }, null, 2))
} finally {
  client.close()
}
