import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9389)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-05-agent-knowledge-mcp-read-contract/screenshots'
)

fs.mkdirSync(screenshotDir, { recursive: true })

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

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

const copyRow = async (client, prefix, expectedSegment, expectedKind, name) => {
  const result = await evaluate(client, `(
    async () => {
      const row = Array.from(document.querySelectorAll('.focus-dossier-link-row'))
        .find((item) => item.textContent.includes(${JSON.stringify(prefix)}))
      if (!row) return { error: 'row_not_found' }
      row.scrollIntoView({ block: 'center' })
      row.querySelector('.focus-dossier-mcp-button')?.click()
      await new Promise((resolve) => setTimeout(resolve, 250))
      return {
        row: row.textContent.trim(),
        preview: document.querySelector('[data-focus-dossier-mcp-preview="true"]')?.innerText || '',
        last: document.querySelector('[data-last-mcp-call="true"]')?.innerText || ''
      }
    }
  )()`)
  if (result.error) throw new Error(`${prefix} ${result.error}`)
  if (!result.preview.includes(`/${expectedSegment}/`) || !result.preview.includes(`"kind": "${expectedKind}"`)) {
    throw new Error(`${prefix} MCP preview mismatch: ${result.preview}`)
  }
  if (!result.last.includes('worldline.inspect_run_knowledge')) {
    throw new Error(`${prefix} Last MCP panel missing knowledge tool: ${result.last}`)
  }
  const image = await screenshot(client, name)
  return { ...result, image }
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
  await waitFor(client, "Boolean(document.querySelector('.event-item'))", 'event list')

  const selectedBranch = await evaluate(client, `(
    async () => {
      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
      for (const event of Array.from(document.querySelectorAll('.event-item'))) {
        event.click()
        await sleep(150)
        const section = Array.from(document.querySelectorAll('.event-detail-section'))
          .find((item) => item.querySelector('strong')?.textContent.includes('Branches'))
        const token = section?.querySelector('.event-detail-token:not(:disabled)')
        if (token) {
          token.click()
          return token.textContent.trim()
        }
      }
      return ''
    }
  )()`)
  if (!selectedBranch) throw new Error('No clickable branch token found')

  await waitFor(client, "Boolean(document.querySelector('.focus-dossier'))", 'branch dossier')
  await waitFor(
    client,
    "['Wiki:', 'Graph:', 'Time:'].every((prefix) => Array.from(document.querySelectorAll('.focus-dossier-link-row')).some((row) => row.textContent.includes(prefix) && row.querySelector('.focus-dossier-mcp-button')))",
    'wiki graph timeline MCP rows'
  )

  const wiki = await copyRow(client, 'Wiki:', 'wiki', 'wiki', 'focus-dossier-wiki-mcp.png')
  const graph = await copyRow(client, 'Graph:', 'graph', 'graph', 'focus-dossier-graph-mcp.png')
  const timeline = await copyRow(client, 'Time:', 'timeline', 'timeline', 'focus-dossier-timeline-mcp.png')

  console.log(JSON.stringify({
    status: 'ok',
    selectedBranch,
    wiki,
    graph,
    timeline,
    screenshots: [wiki.image, graph.image, timeline.image]
  }, null, 2))
} finally {
  client.close()
}
