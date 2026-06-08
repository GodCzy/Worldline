const fs = require('fs')
const path = require('path')

const cdpBase = 'http://127.0.0.1:9226'
const outDir = 'D:/dev/Worldline/.ai/tasks/2026-06-05-agent-source-dossier/screenshots'
const pageUrl = 'http://127.0.0.1:5173/worldline/agent'

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const getJson = async (url) => {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`${url} -> ${response.status}`)
  return response.json()
}

const connectWs = async (url) => {
  const ws = new WebSocket(url)
  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true })
    ws.addEventListener('error', reject, { once: true })
  })

  let id = 0
  const callbacks = new Map()
  ws.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data)
    if (!payload.id || !callbacks.has(payload.id)) return
    const callback = callbacks.get(payload.id)
    callbacks.delete(payload.id)
    if (payload.error) callback.reject(new Error(payload.error.message || JSON.stringify(payload.error)))
    else callback.resolve(payload.result || {})
  })

  return {
    send(method, params = {}) {
      const messageId = ++id
      ws.send(JSON.stringify({ id: messageId, method, params }))
      return new Promise((resolve, reject) => callbacks.set(messageId, { resolve, reject }))
    },
    close() {
      ws.close()
    }
  }
}

const evaluate = async (client, expression) => {
  const result = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true
  })
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Runtime evaluation failed')
  }
  return result.result?.value
}

const waitFor = async (client, expression, label, timeoutMs = 15000) => {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const value = await evaluate(client, expression)
    if (value) return value
    await delay(250)
  }
  throw new Error(`Timed out waiting for ${label}`)
}

const screenshot = async (client, filename) => {
  const result = await client.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true
  })
  const filePath = path.join(outDir, filename)
  fs.writeFileSync(filePath, Buffer.from(result.data, 'base64'))
  return filePath
}

const focusDossierRect = (client) => evaluate(
  client,
  `(() => {
    const element = document.querySelector('.focus-dossier')
    element.scrollIntoView({ block: 'center', inline: 'nearest' })
    const rect = element.getBoundingClientRect()
    return { top: rect.top, left: rect.left, width: rect.width, height: rect.height, scrollY: window.scrollY }
  })()`
)

const main = async () => {
  fs.mkdirSync(outDir, { recursive: true })
  const pages = await getJson(`${cdpBase}/json/list`)
  const page = pages.find((item) => item.url.includes('/worldline/agent')) || pages[0]
  if (!page?.webSocketDebuggerUrl) throw new Error('No debuggable page found')
  const client = await connectWs(page.webSocketDebuggerUrl)

  try {
    await client.send('Page.enable')
    await client.send('Runtime.enable')
    await client.send('Emulation.setDeviceMetricsOverride', {
      width: 1600,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false
    })
    await client.send('Page.navigate', { url: pageUrl })
    await waitFor(client, `document.querySelector('[data-inspector-target="evidence:ev-agent-workflow"]')`, 'evidence item')

    const gateSupport = await evaluate(
      client,
      `Array.from(document.querySelectorAll('.gate-support-strip')).map((item) => item.textContent.replace(/\\s+/g, ' ').trim())`
    )
    if (!gateSupport.some((text) => /Source\s*\d+/.test(text))) {
      throw new Error(`Gate Source support strip not found: ${JSON.stringify(gateSupport)}`)
    }

    await evaluate(client, `document.querySelector('[data-inspector-target="evidence:ev-agent-workflow"]').click()`)
    await waitFor(
      client,
      `Array.from(document.querySelectorAll('.focus-dossier-link')).some((button) => button.textContent.includes('Source: src/services/worldline_agent_workflow_service.py'))`,
      'source link'
    )
    await evaluate(
      client,
      `Array.from(document.querySelectorAll('.focus-dossier-link')).find((button) => button.textContent.includes('Source: src/services/worldline_agent_workflow_service.py'))?.click()`
    )
    await waitFor(
      client,
      `(() => {
        const text = document.querySelector('.focus-dossier')?.textContent || ''
        return text.includes('Source Asset') &&
          text.includes('Document Node') &&
          text.includes('Controlled subagent lane manifest') &&
          text.includes('10-122') &&
          text.includes('Evidence: Controlled Agent workflow lanes')
      })()`,
      'source dossier'
    )
    const sourceRect = await focusDossierRect(client)
    await delay(600)
    const sourceShot = await screenshot(client, 'source-dossier-focus-viewport.png')

    await evaluate(
      client,
      `Array.from(document.querySelectorAll('.focus-dossier-link')).find((button) => button.textContent.includes('Evidence: Controlled Agent workflow lanes'))?.click()`
    )
    await waitFor(
      client,
      `document.querySelector('.focus-dossier')?.textContent.includes('Evidence ID') &&
        document.querySelector('.focus-dossier')?.textContent.includes('ev-agent-workflow')`,
      'evidence backlink'
    )
    const backlinkRect = await focusDossierRect(client)
    await delay(600)
    const backlinkShot = await screenshot(client, 'source-dossier-backlink-viewport.png')

    console.log(JSON.stringify({
      ok: true,
      gateSupport,
      sourceRect,
      backlinkRect,
      sourceShot,
      backlinkShot
    }, null, 2))
  } finally {
    client.close()
  }
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
