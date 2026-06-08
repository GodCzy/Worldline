import fs from 'node:fs'
import path from 'node:path'

const port = Number(process.env.CDP_PORT || 9380)
const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:5173/worldline/agent'
const screenshotDir = path.resolve(
  process.env.SCREENSHOT_DIR || '.ai/tasks/2026-06-05-agent-evidence-mcp-read-contract/screenshots'
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
  await waitFor(client, "Boolean(document.querySelector('.event-item'))", 'event list')

  const selectedGate = await evaluate(client, `(
    async () => {
      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
      for (const event of Array.from(document.querySelectorAll('.event-item'))) {
        event.click()
        await sleep(150)
        const section = Array.from(document.querySelectorAll('.event-detail-section'))
          .find((item) => item.querySelector('strong')?.textContent.includes('Quality Gates'))
        const token = section?.querySelector('.event-detail-token:not(:disabled)')
        if (token) {
          token.click()
          return token.textContent.trim()
        }
      }
      return ''
    }
  )()`)
  if (!selectedGate) throw new Error('No clickable quality-gate token found')

  await waitFor(client, "Boolean(document.querySelector('.focus-dossier'))", 'gate dossier')
  await waitFor(
    client,
    "Array.from(document.querySelectorAll('.focus-dossier-link-row')).some((row) => row.textContent.includes('Evidence:') && row.querySelector('.focus-dossier-mcp-button'))",
    'evidence MCP row'
  )

  const evidenceResult = await evaluate(client, `(
    async () => {
      const row = Array.from(document.querySelectorAll('.focus-dossier-link-row'))
        .find((item) => item.textContent.includes('Evidence:'))
      row.scrollIntoView({ block: 'center' })
      row.querySelector('.focus-dossier-mcp-button').click()
      await new Promise((resolve) => setTimeout(resolve, 250))
      return {
        row: row.textContent.trim(),
        preview: document.querySelector('[data-focus-dossier-mcp-preview="true"]')?.innerText || '',
        last: document.querySelector('[data-last-mcp-call="true"]')?.innerText || ''
      }
    }
  )()`)
  if (!evidenceResult.preview.includes('/evidence/') || !evidenceResult.preview.includes('evidence_id')) {
    throw new Error(`Evidence MCP preview missing evidence args: ${evidenceResult.preview}`)
  }
  if (!evidenceResult.last.includes('worldline.inspect_run_evidence')) {
    throw new Error(`Last MCP panel missing evidence tool: ${evidenceResult.last}`)
  }
  const evidenceScreenshot = await screenshot(client, 'focus-dossier-evidence-mcp.png')

  await evaluate(client, `(
    async () => {
      const row = Array.from(document.querySelectorAll('.focus-dossier-link-row'))
        .find((item) => item.textContent.includes('Evidence:'))
      row.querySelector('.focus-dossier-link').click()
      await new Promise((resolve) => setTimeout(resolve, 300))
      return true
    }
  )()`)
  await waitFor(
    client,
    "Array.from(document.querySelectorAll('.focus-dossier-link-row')).some((row) => row.textContent.includes('Source:') && row.querySelector('.focus-dossier-mcp-button'))",
    'source MCP row'
  )

  const sourceResult = await evaluate(client, `(
    async () => {
      const row = Array.from(document.querySelectorAll('.focus-dossier-link-row'))
        .find((item) => item.textContent.includes('Source:'))
      row.scrollIntoView({ block: 'center' })
      row.querySelector('.focus-dossier-mcp-button').click()
      await new Promise((resolve) => setTimeout(resolve, 250))
      return {
        row: row.textContent.trim(),
        preview: document.querySelector('[data-focus-dossier-mcp-preview="true"]')?.innerText || '',
        last: document.querySelector('[data-last-mcp-call="true"]')?.innerText || ''
      }
    }
  )()`)
  if (!sourceResult.preview.includes('/sources/') || !sourceResult.preview.includes('source_id')) {
    throw new Error(`Source MCP preview missing source args: ${sourceResult.preview}`)
  }
  if (!sourceResult.last.includes('worldline.inspect_run_evidence')) {
    throw new Error(`Last MCP panel missing source tool: ${sourceResult.last}`)
  }
  const sourceScreenshot = await screenshot(client, 'focus-dossier-source-mcp.png')

  console.log(JSON.stringify({
    status: 'ok',
    selectedGate,
    evidence: evidenceResult,
    source: sourceResult,
    screenshots: [evidenceScreenshot, sourceScreenshot]
  }, null, 2))
} finally {
  client.close()
}
