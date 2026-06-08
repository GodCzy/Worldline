const fs = require('node:fs/promises')
const path = require('node:path')

const port = Number(process.env.CDP_PORT || 9342)
const url = process.env.QA_URL || 'http://127.0.0.1:5173/worldline/agent'
const outDir = path.resolve(__dirname, 'screenshots')

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const getJson = async (targetUrl) => {
  const response = await fetch(targetUrl)
  if (!response.ok) throw new Error(`GET ${targetUrl} failed: ${response.status}`)
  return response.json()
}

const waitFor = async (fn, label, timeoutMs = 30000) => {
  const started = Date.now()
  let lastError
  while (Date.now() - started < timeoutMs) {
    try {
      const result = await fn()
      if (result) return result
    } catch (error) {
      lastError = error
    }
    await sleep(350)
  }
  throw new Error(`${label} timed out${lastError ? `: ${lastError.message}` : ''}`)
}

const connectPage = async () => {
  const targets = await waitFor(
    () => getJson(`http://127.0.0.1:${port}/json/list`),
    'CDP target list'
  )
  const page = targets.find((target) => target.type === 'page' && target.webSocketDebuggerUrl)
  if (!page) throw new Error('No debuggable Chrome page found')

  const socket = new WebSocket(page.webSocketDebuggerUrl)
  const callbacks = new Map()
  let commandId = 0

  socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data)
    if (!message.id || !callbacks.has(message.id)) return
    const { resolve, reject } = callbacks.get(message.id)
    callbacks.delete(message.id)
    if (message.error) reject(new Error(message.error.message))
    else resolve(message.result || {})
  })

  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true })
    socket.addEventListener('error', reject, { once: true })
  })

  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++commandId
    callbacks.set(id, { resolve, reject })
    socket.send(JSON.stringify({ id, method, params }))
  })

  return { send, close: () => socket.close() }
}

const evaluate = async (client, expression) => {
  const result = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true
  })
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed')
  }
  return result.result?.value
}

const waitForText = (client, text, label = text) =>
  waitFor(
    () => evaluate(client, `document.body.innerText.includes(${JSON.stringify(text)})`),
    label
  )

const clickByText = async (client, selector, text) => {
  const clicked = await evaluate(client, `
    (() => {
      const node = [...document.querySelectorAll(${JSON.stringify(selector)})]
        .find((item) => item.innerText.includes(${JSON.stringify(text)}))
      if (!node) return false
      node.click()
      return true
    })()
  `)
  if (!clicked) throw new Error(`Unable to click ${selector} containing ${text}`)
}

const screenshot = async (client, fileName) => {
  const shot = await client.send('Page.captureScreenshot', {
    format: 'png',
    captureBeyondViewport: false
  })
  await fs.mkdir(outDir, { recursive: true })
  const filePath = path.join(outDir, fileName)
  await fs.writeFile(filePath, Buffer.from(shot.data, 'base64'))
  return filePath
}

const scrollExportIntoView = async (client) => {
  await evaluate(client, `
    (() => {
      const panel = document.querySelector('[data-replay-export="true"]')
      if (!panel) return false
      panel.scrollIntoView({ block: 'center', inline: 'nearest' })
      return true
    })()
  `)
  await sleep(250)
}

const previewText = async (client) =>
  evaluate(client, 'document.querySelector(".replay-export-preview")?.innerText || ""')

const main = async () => {
  const client = await connectPage()
  try {
    await client.send('Runtime.enable')
    await client.send('Page.enable')
    await client.send('Emulation.setDeviceMetricsOverride', {
      width: 1600,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false
    })
    await client.send('Page.navigate', { url })
    await waitFor(
      () => evaluate(client, 'document.readyState === "complete" || document.readyState === "interactive"'),
      'page ready'
    )

    await waitForText(client, 'REPLAY EXPORT', 'replay export panel')
    await waitForText(client, 'Download JSON', 'download action')
    await waitForText(client, 'Copy Markdown', 'copy action')
    await waitForText(client, 'Preview Artifact', 'preview action')
    await waitForText(client, 'Run Preview', 'selected run event')
    await clickByText(client, '.manifest-action', 'Open Replay Manifest')
    await waitForText(client, 'Replay Manifest', 'focused replay manifest')

    await scrollExportIntoView(client)
    await clickByText(client, '.replay-export-action', 'Preview Artifact')
    await waitForText(client, '# Worldline Replay Export', 'export markdown title')

    const preview = await previewText(client)
    const required = [
      'Run: Agent Workbench Stage 1',
      'Selected Event: Run Preview',
      'Focused Dossier: Agent Workbench Stage 1',
      '## Replay Timeline',
      'Tool Pending'
    ]
    const missing = required.filter((text) => !preview.includes(text))
    if (missing.length) {
      throw new Error(`Export preview missing: ${missing.join(', ')}`)
    }

    const previewPath = await screenshot(client, 'replay-export-preview.png')

    await clickByText(client, '.replay-export-action', 'Copy Markdown')
    await waitFor(
      () => evaluate(client, `
        (() => {
          const message = document.querySelector('.replay-export-message')?.innerText || ''
          return message.includes('Markdown') || message.includes('Clipboard')
        })()
      `),
      'copy status'
    )
    const copyStatusPath = await screenshot(client, 'replay-export-copy-status.png')

    console.log(JSON.stringify({
      ok: true,
      previewPath,
      copyStatusPath
    }, null, 2))
  } finally {
    client.close()
  }
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
