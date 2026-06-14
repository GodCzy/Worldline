import { spawn } from 'node:child_process'
import { mkdir, rm, writeFile } from 'node:fs/promises'
import { get } from 'node:http'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const edgePath = process.env.EDGE_PATH || 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const baseUrl = process.env.QA_BASE_URL || 'http://127.0.0.1:5183'
const outDir = process.env.QA_OUT_DIR || path.dirname(fileURLToPath(import.meta.url))
const target = `${baseUrl}/seed?target=/worldline/p3-branch?question=P3%20Branch%20Canvas%20QA`

const viewports = [
  { name: '1440x900', width: 1440, height: 900, mobile: false },
  { name: '390x844', width: 390, height: 844, mobile: true }
]

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const fetchJson = (url) =>
  new Promise((resolve, reject) => {
    get(url, (response) => {
      let body = ''
      response.setEncoding('utf8')
      response.on('data', (chunk) => {
        body += chunk
      })
      response.on('end', () => {
        try {
          resolve(JSON.parse(body))
        } catch (error) {
          reject(error)
        }
      })
    }).on('error', reject)
  })

const waitForDebugger = async (port) => {
  const endpoint = `http://127.0.0.1:${port}/json/list`
  for (let index = 0; index < 50; index += 1) {
    try {
      const targets = await fetchJson(endpoint)
      const page = Array.isArray(targets) ? targets.find((item) => item.type === 'page') : null
      if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl
    } catch {
      await sleep(100)
    }
  }
  throw new Error(`CDP endpoint did not become ready on port ${port}`)
}

const connectCdp = (url) =>
  new Promise((resolve, reject) => {
    const socket = new WebSocket(url)
    let nextId = 1
    const pending = new Map()

    socket.addEventListener('open', () => {
      resolve({
        call(method, params = {}) {
          const id = nextId
          nextId += 1
          socket.send(JSON.stringify({ id, method, params }))
          return new Promise((callResolve, callReject) => {
            pending.set(id, { resolve: callResolve, reject: callReject })
          })
        },
        close() {
          socket.close()
        }
      })
    })

    socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data)
      if (!message.id || !pending.has(message.id)) return
      const item = pending.get(message.id)
      pending.delete(message.id)
      if (message.error) item.reject(new Error(message.error.message))
      else item.resolve(message.result)
    })

    socket.addEventListener('error', reject)
  })

const runViewport = async (viewport, index) => {
  const port = 9222 + index
  const profile = path.join(tmpdir(), `worldline-p3-cdp-${process.pid}-${viewport.name}`)
  await mkdir(profile, { recursive: true })
  const edge = spawn(edgePath, [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profile}`,
    `--window-size=${viewport.width},${viewport.height}`,
    'about:blank'
  ])
  const edgeExit = new Promise((resolve) => {
    edge.once('exit', resolve)
  })

  try {
    const cdpUrl = await waitForDebugger(port)
    const cdp = await connectCdp(cdpUrl)
    await cdp.call('Page.enable')
    await cdp.call('Runtime.enable')
    await cdp.call('Emulation.setDeviceMetricsOverride', {
      width: viewport.width,
      height: viewport.height,
      deviceScaleFactor: 1,
      mobile: viewport.mobile
    })
    await cdp.call('Page.navigate', { url: target })
    await sleep(5000)
    const metrics = await cdp.call('Runtime.evaluate', {
      returnByValue: true,
      expression: `(() => {
        const canvas = document.querySelector('[data-worldline-canvas="true"] svg');
        const detail = document.querySelector('[data-worldline-detail="true"]');
        const routeTrace = document.querySelector('[data-branch-route-trace="true"]');
        const gateRefs = document.querySelector('[data-branch-gate-refs="true"]');
        const support = document.querySelector('[data-branch-support-status="true"]');
        const canvasBox = canvas ? canvas.getBoundingClientRect() : null;
        const bodyText = document.body ? document.body.innerText : '';
        return {
          title: document.title,
          url: location.href,
          viewport: { width: innerWidth, height: innerHeight },
          hasCanvas: Boolean(canvas),
          hasInspector: Boolean(detail),
          hasRouteTrace: Boolean(routeTrace),
          hasGateRefs: Boolean(gateRefs),
          hasSupportStatus: Boolean(support),
          textSignals: {
            branchInspector: bodyText.includes('BRANCH INSPECTOR'),
            routePolicy: bodyText.includes('evidence_required'),
            gateId: bodyText.includes('gate-p3-3-qa'),
            evidenceRail: bodyText.includes('EVIDENCE RAIL')
          },
          pageOverflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          canvasBox: canvasBox ? {
            x: Math.round(canvasBox.x),
            y: Math.round(canvasBox.y),
            width: Math.round(canvasBox.width),
            height: Math.round(canvasBox.height)
          } : null
        };
      })()`
    })
    const screenshot = await cdp.call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false })
    const screenshotPath = path.join(outDir, `p3-3-worldline-branch-canvas-cdp-${viewport.name}.png`)
    await writeFile(screenshotPath, Buffer.from(screenshot.data, 'base64'))
    cdp.close()
    return { viewport: viewport.name, screenshotPath, ...metrics.result.value }
  } finally {
    edge.kill()
    await Promise.race([edgeExit, sleep(3000)])
    await rm(profile, { recursive: true, force: true })
  }
}

const report = []
for (const [index, viewport] of viewports.entries()) {
  report.push(await runViewport(viewport, index))
}

const reportPath = path.join(outDir, 'p3-3-branch-canvas-browser-qa.json')
await writeFile(reportPath, JSON.stringify(report, null, 2), 'utf8')
console.log(JSON.stringify({ reportPath, report }, null, 2))
