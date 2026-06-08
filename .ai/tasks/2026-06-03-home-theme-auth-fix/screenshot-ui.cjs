const fs = require('fs')
const path = require('path')
const { chromium } = require('playwright')

const baseUrl = process.env.WORLDLINE_BASE_URL || 'http://127.0.0.1:5173'
const outDir = path.resolve(__dirname, 'screenshots')
const oldPreviewNeedles = [
  ['phase', '5'].join(''),
  ['Phase', '5'].join(''),
  ['Phase', ' ', '5'].join('')
]
const viewports = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1440x900', width: 1440, height: 900 },
  { name: '390x844', width: 390, height: 844 }
]
const pages = [
  {
    id: 'home',
    path: '/',
    expect: async (page) => {
      const body = await page.textContent('body')
      if (!body.includes('Worldline')) throw new Error('home missing Worldline title')
      if (!body.includes('登录') && !body.includes('初始化') && !body.includes('已进入管理会话')) {
        throw new Error('home missing embedded access panel')
      }
    }
  },
  {
    id: 'themes',
    path: '/themes',
    expect: async (page) => {
      const body = await page.textContent('body')
      if (!body.includes('添加自定义模块')) throw new Error('themes missing custom add module entry')
      if (oldPreviewNeedles.some((needle) => body.includes(needle))) {
        throw new Error('themes still contains old stage copy')
      }
    }
  },
  {
    id: 'worldline-hub',
    path: '/worldline',
    expect: async (page) => {
      const body = await page.textContent('body')
      if (!body.includes('暂无可用 Worldline 模块')) throw new Error('worldline hub missing empty module state')
      if (oldPreviewNeedles.some((needle) => body.includes(needle))) {
        throw new Error('worldline hub still contains old stage copy')
      }
    }
  },
  {
    id: 'agent-login-redirect',
    path: '/agent',
    expect: async (page) => {
      await page.waitForURL(/\/\?login=1.*redirect=%2Fagent|\/\?login=1.*redirect=\/agent/, {
        timeout: 6000
      })
      const url = new URL(page.url())
      if (url.pathname !== '/' || url.searchParams.get('login') !== '1') {
        throw new Error(`agent did not redirect to home login panel: ${page.url()}`)
      }
      if ((url.searchParams.get('redirect') || '') !== '/agent') {
        throw new Error(`agent redirect query missing: ${page.url()}`)
      }
    }
  },
  {
    id: 'authenticated-sidebar',
    path: '/themes',
    authenticated: true,
    expect: async (page) => {
      const labels = await page.locator('.nav-label').allTextContents()
      const required = ['首页', '主题分区', '世界线', 'Agent', '知识图谱', '知识库', '扩展管理', '运营看板']
      const missing = required.filter((item) => !labels.includes(item))
      if (missing.length) throw new Error(`authenticated sidebar missing: ${missing.join(', ')}`)
    }
  }
]

async function run() {
  fs.mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch({ headless: true })
  const report = []
  const failures = []

  for (const viewport of viewports) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1
    })
    await context.addInitScript(() => {
      localStorage.clear()
      sessionStorage.clear()
    })

    for (const entry of pages) {
      const page = await context.newPage()
      if (entry.authenticated) {
        await page.route('**/api/auth/me', async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 1,
              username: 'Joy',
              user_id: 'Joy',
              phone_number: null,
              avatar: null,
              role: 'superadmin',
              department_id: 1,
              department_name: '默认部门',
              created_at: '2026-06-03T00:00:00',
              last_login: null
            })
          })
        })
        await page.addInitScript(() => {
          localStorage.setItem('user_token', 'mock-superadmin-token')
          localStorage.setItem('worldline_app_nav_expanded', '1')
        })
      }
      const screenshot = path.join(outDir, `${entry.id}-${viewport.name}.png`)
      try {
        await page.goto(`${baseUrl}${entry.path}`, { waitUntil: 'domcontentloaded', timeout: 15000 })
        await page.waitForTimeout(1600)
        await entry.expect(page)
        await page.screenshot({ path: screenshot, fullPage: true })
        report.push({
          page: entry.id,
          route: entry.path,
          viewport: viewport.name,
          screenshot,
          url: page.url(),
          status: 'passed'
        })
      } catch (error) {
        failures.push({
          page: entry.id,
          route: entry.path,
          viewport: viewport.name,
          error: error.message,
          url: page.url()
        })
        try {
          await page.screenshot({ path: screenshot, fullPage: true })
        } catch (_) {
          // Keep the primary failure visible.
        }
      } finally {
        await page.close()
      }
    }

    await context.close()
  }

  await browser.close()

  const payload = {
    generatedAt: new Date().toISOString(),
    baseUrl,
    report,
    failures
  }
  fs.writeFileSync(path.join(outDir, 'ui-screenshot-report.json'), JSON.stringify(payload, null, 2))

  if (failures.length) {
    console.error(JSON.stringify(payload, null, 2))
    process.exit(1)
  }

  console.log(JSON.stringify(payload, null, 2))
}

run().catch((error) => {
  console.error(error)
  process.exit(1)
})
