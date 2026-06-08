const fs = require('fs')
const path = require('path')

const cdpBase = 'http://127.0.0.1:9227'
const pageUrl = 'http://127.0.0.1:5173/worldline/agent'
const outDir = 'D:/dev/Worldline/.ai/tasks/2026-06-05-agent-branch-decision-replay/screenshots'

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
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime evaluation failed')
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
    await waitFor(client, `document.body?.textContent.includes('拒绝并回滚')`, 'reject action')

    await evaluate(
      client,
      `Array.from(document.querySelectorAll('.branch-button')).find((button) => button.textContent.includes('工具执行分支'))?.click()`
    )
    await waitFor(
      client,
      `document.querySelector('[data-worldline-detail="true"]')?.textContent.includes('工具执行分支')`,
      'tool branch selection'
    )
    await waitFor(
      client,
      `Array.from(document.querySelectorAll('.action-button')).some((button) => button.textContent.includes('拒绝并回滚'))`,
      'reject button visible on tool branch'
    )

    const beforeText = await evaluate(client, `document.querySelector('.ledger-status')?.textContent.replace(/\\s+/g, ' ').trim()`)
    await evaluate(
      client,
      `Array.from(document.querySelectorAll('.action-button')).find((button) => button.textContent.includes('拒绝并回滚'))?.click()`
    )
    await waitFor(
      client,
      `document.querySelector('.ledger-status')?.textContent.includes('请先登录管理员账号') ||
        document.querySelector('.ledger-status')?.textContent.includes('当前账号不是管理员')`,
      'gated reject message'
    )
    await evaluate(client, `document.querySelector('[data-worldline-detail="true"]').scrollIntoView({ block: 'center', inline: 'nearest' })`)
    await delay(600)
    const afterText = await evaluate(client, `document.querySelector('.ledger-status')?.textContent.replace(/\\s+/g, ' ').trim()`)
    const actionText = await evaluate(
      client,
      `Array.from(document.querySelectorAll('.action-button')).map((button) => button.textContent.replace(/\\s+/g, ' ').trim())`
    )
    const screenshotPath = await screenshot(client, 'branch-reject-gated-message.png')

    console.log(JSON.stringify({
      ok: true,
      beforeText,
      afterText,
      actionText,
      screenshotPath
    }, null, 2))
  } finally {
    client.close()
  }
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
