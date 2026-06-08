const fs = require('node:fs/promises')
const path = require('node:path')

const port = Number(process.env.CDP_PORT || 9347)
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

const waitForTextInsensitive = (client, text, label = text) =>
  waitFor(
    () => evaluate(client, `document.body.innerText.toLowerCase().includes(${JSON.stringify(text.toLowerCase())})`),
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

const scrollRegistryIntoView = async (client) => {
  const found = await evaluate(client, `
    (() => {
      const panel = document.querySelector('[data-artifact-registry="true"]')
      if (!panel) return false
      panel.scrollIntoView({ block: 'center', inline: 'nearest' })
      return true
    })()
  `)
  if (!found) throw new Error('Artifact registry panel not found')
  await sleep(250)
}

const registryText = (client) =>
  evaluate(client, `document.querySelector('[data-artifact-registry="true"]')?.innerText || ''`)

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

    await waitForTextInsensitive(client, 'Registry', 'artifact registry')
    await waitForText(client, 'Replay', 'replay filter')
    await waitForText(client, 'Handoff', 'handoff filter')
    await waitForText(client, 'Replay Export: Agent Workbench Stage 1', 'planned replay artifact')
    await waitForText(client, 'Agent Handoff: Run Preview', 'planned handoff artifact')
    await scrollRegistryIntoView(client)

    const allText = await registryText(client)
    for (const required of ['Replay / planned', 'Handoff / planned']) {
      if (!allText.includes(required)) throw new Error(`Registry missing ${required}`)
    }

    await clickByText(client, '.registry-filter-button', 'Handoff')
    await waitFor(
      async () => {
        const text = await registryText(client)
        return text.includes('Agent Handoff: Run Preview') && !text.includes('Replay Export: Agent Workbench Stage 1')
      },
      'handoff filter result'
    )
    const handoffPath = await screenshot(client, 'artifact-registry-handoff-filter.png')

    await clickByText(client, '.registry-filter-button', 'Replay')
    await waitFor(
      async () => {
        const text = await registryText(client)
        return text.includes('Replay Export: Agent Workbench Stage 1') && !text.includes('Agent Handoff: Run Preview')
      },
      'replay filter result'
    )
    const replayPath = await screenshot(client, 'artifact-registry-replay-filter.png')

    console.log(JSON.stringify({
      ok: true,
      handoffPath,
      replayPath
    }, null, 2))
  } finally {
    client.close()
  }
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
