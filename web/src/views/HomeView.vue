<template>
  <div class="home-container">
    <div v-if="isLoading" class="loading-container">
      <a-spin size="large" />
      <p>正在载入 Worldline 控制台</p>
    </div>

    <template v-else>
      <header class="topbar">
        <router-link to="/" class="brand-link" aria-label="Worldline Home">
          <img
            v-if="infoStore.organization.logo && !logoFailed"
            :src="infoStore.organization.logo"
            :alt="infoStore.organization.name"
            class="brand-logo"
            @error="logoFailed = true"
          />
          <span v-else class="brand-mark">W</span>
          <span class="brand-name">{{ infoStore.organization.name || 'Worldline' }}</span>
        </router-link>

        <nav class="nav-links" aria-label="Primary">
          <button type="button" class="nav-pill" @click="openWorldline">
            <Waypoints :size="17" />
            <span>世界线</span>
          </button>
          <button type="button" class="nav-pill" @click="openThemes">
            <LayoutGrid :size="17" />
            <span>主题分区</span>
          </button>
          <button type="button" class="nav-pill" :class="{ locked: !userStore.isLoggedIn }" @click="openAgent">
            <Bot :size="17" />
            <span>Agent</span>
            <LockKeyhole v-if="!userStore.isLoggedIn" class="mini-lock" :size="12" />
          </button>
          <button type="button" class="nav-pill" :class="{ locked: !userStore.isAdmin }" @click="openKnowledge">
            <Database :size="17" />
            <span>知识库</span>
            <LockKeyhole v-if="!userStore.isAdmin" class="mini-lock" :size="12" />
          </button>
          <button type="button" class="nav-pill" :class="{ locked: !userStore.isAdmin }" @click="openGraph">
            <Network :size="17" />
            <span>图谱</span>
            <LockKeyhole v-if="!userStore.isAdmin" class="mini-lock" :size="12" />
          </button>
        </nav>

        <div class="header-actions">
          <a
            v-if="githubUrl"
            class="icon-button"
            :href="githubUrl"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Repository"
          >
            <Github :size="19" />
          </a>
          <button v-if="userStore.isLoggedIn" type="button" class="session-button" @click="logout">
            <ShieldCheck :size="17" />
            <span>{{ userStore.username || userStore.userIdLogin }}</span>
          </button>
          <button v-else type="button" class="session-button" @click="focusLogin('/agent')">
            <KeyRound :size="17" />
            <span>登录</span>
          </button>
        </div>
      </header>

      <main class="home-main">
        <div v-if="backendStatus.state !== 'ready'" class="status-banner" role="status">
          <AlertTriangle :size="18" />
          <span>{{ backendStatus.message }}</span>
          <button type="button" @click="retryLoad">重试</button>
        </div>

        <section class="hero-section" aria-label="Worldline console">
          <div class="hero-copy">
            <p class="eyebrow">LIVING KNOWLEDGE OS</p>
            <h1>{{ infoStore.branding.title || 'Worldline' }}</h1>
            <p class="subtitle">{{ infoStore.branding.subtitle }}</p>
            <p v-if="brandingDescription" class="description">{{ brandingDescription }}</p>

            <div class="hero-actions">
              <button class="primary-button" type="button" @click="openWorldline">
                <Waypoints :size="18" />
                <span>进入世界线</span>
              </button>
              <button class="secondary-button" type="button" @click="openThemes">
                <Plus :size="18" />
                <span>自定义模块</span>
              </button>
              <a
                v-if="docsUrl"
                class="secondary-button"
                :href="docsUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                <BookOpen :size="18" />
                <span>文档</span>
              </a>
            </div>

            <div class="signal-grid" aria-label="Worldline surfaces">
              <article v-for="card in featureCards" :key="card.label" class="signal-item">
                <div class="signal-icon">
                  <component :is="card.icon" :size="22" />
                </div>
                <div>
                  <p class="signal-value">{{ card.value }}</p>
                  <h2>{{ card.label }}</h2>
                  <p>{{ card.description }}</p>
                </div>
              </article>
            </div>
          </div>

          <aside ref="loginPanelRef" class="access-panel" :class="{ highlighted: shouldHighlightLogin }">
            <div class="panel-header">
              <p class="eyebrow">ACCESS</p>
              <h2>{{ userStore.isLoggedIn ? '已进入管理会话' : isFirstRun ? '初始化最高权限账号' : '登录 Worldline' }}</h2>
              <p>
                {{
                  userStore.isLoggedIn
                    ? `${userStore.username || userStore.userIdLogin} · ${userStore.userRole || 'user'}`
                    : 'Agent 登录后打开；知识库、图谱和扩展管理需要管理员权限。'
                }}
              </p>
            </div>

            <div v-if="userStore.isLoggedIn" class="access-ready">
              <div class="ready-grid">
                <button type="button" @click="openAgent">
                  <Bot :size="18" />
                  <span>Agent</span>
                </button>
                <button type="button" @click="openKnowledge">
                  <Database :size="18" />
                  <span>知识库</span>
                </button>
                <button type="button" @click="openGraph">
                  <Network :size="18" />
                  <span>图谱</span>
                </button>
                <button type="button" @click="openExtensions">
                  <Blocks :size="18" />
                  <span>扩展</span>
                </button>
              </div>
              <button class="secondary-button full-width" type="button" @click="logout">退出当前会话</button>
            </div>

            <form v-else-if="isFirstRun" class="login-form" @submit.prevent="handleInitialize">
              <label>
                <span>用户 ID</span>
                <input v-model.trim="adminForm.userId" autocomplete="username" placeholder="Joy" />
              </label>
              <label>
                <span>密码</span>
                <input
                  v-model="adminForm.password"
                  type="password"
                  autocomplete="new-password"
                  placeholder="输入初始化密码"
                />
              </label>
              <button class="primary-button full-width" type="submit" :disabled="authLoading">
                <KeyRound :size="18" />
                <span>{{ authLoading ? '正在初始化' : '创建最高权限账号' }}</span>
              </button>
            </form>

            <form v-else class="login-form" @submit.prevent="handleLogin">
              <label>
                <span>用户 ID / 手机号</span>
                <input v-model.trim="loginForm.loginId" autocomplete="username" placeholder="Joy" />
              </label>
              <label>
                <span>密码</span>
                <input
                  v-model="loginForm.password"
                  type="password"
                  autocomplete="current-password"
                  placeholder="输入密码"
                />
              </label>
              <button class="primary-button full-width" type="submit" :disabled="authLoading">
                <LogIn :size="18" />
                <span>{{ authLoading ? '正在登录' : '登录并继续' }}</span>
              </button>
            </form>

            <p v-if="authError" class="auth-error">{{ authError }}</p>
          </aside>
        </section>

        <section class="module-section" aria-label="Module entry">
          <div class="section-header">
            <div>
              <p class="eyebrow">MODULES</p>
              <h2>主题分区</h2>
            </div>
            <span class="module-count">{{ moduleCountText }}</span>
          </div>

          <button class="add-module-card" type="button" @click="openAddModule">
            <span class="add-icon"><Plus :size="32" /></span>
            <span class="add-title">添加自定义模块</span>
            <span class="add-copy">暂不展示旧主题或演示模块，下一阶段接入真实知识库、Wiki、图谱和工作流。</span>
          </button>
        </section>
      </main>

      <footer class="footer">
        <span>{{ infoStore.footer?.copyright || 'Worldline 2026' }}</span>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { nextTick, ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'
import { useInfoStore } from '@/stores/info'
import { healthApi } from '@/apis/system_api'
import { consumeStoredRedirect, normalizeAuthRedirect, setStoredRedirect } from '@/router'
import {
  AlertTriangle,
  Blocks,
  BookOpen,
  Bot,
  Database,
  FileText,
  Github,
  KeyRound,
  LayoutGrid,
  LockKeyhole,
  LogIn,
  Network,
  Plus,
  Route,
  ShieldCheck,
  Sparkles,
  Waypoints
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const infoStore = useInfoStore()

const isLoading = ref(true)
const logoFailed = ref(false)
const isFirstRun = ref(false)
const authLoading = ref(false)
const authError = ref('')
const loginPanelRef = ref(null)
const shouldHighlightLogin = ref(false)
const backendStatus = ref({
  state: 'checking',
  message: '正在检查后端服务状态'
})

const loginForm = ref({
  loginId: '',
  password: ''
})

const adminForm = ref({
  userId: 'Joy',
  password: ''
})

const iconKey = (value) => (typeof value === 'string' ? value.toLowerCase() : '')

const featureIconMap = {
  docs: FileText,
  document: FileText,
  route: Route,
  graph: Network,
  shield: ShieldCheck,
  default: Sparkles
}

const withTimeout = (promise, timeoutMs, timeoutMessage) =>
  Promise.race([
    promise,
    new Promise((_, reject) => {
      window.setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
    })
  ])

const checkHealth = async () => {
  try {
    const response = await withTimeout(healthApi.checkHealth(), 3500, 'Backend health check timed out.')
    if (response.status !== 'ok') {
      throw new Error('Backend health response is not ok.')
    }
    backendStatus.value = {
      state: 'ready',
      message: '后端服务已连接'
    }
  } catch (error) {
    backendStatus.value = {
      state: 'offline',
      message: '后端暂不可用，当前使用本地配置渲染首页'
    }
    console.warn('Backend health check failed; homepage remains available.', error)
  }
}

const checkFirstRunStatus = async () => {
  if (userStore.isLoggedIn) {
    isFirstRun.value = false
    return
  }

  isFirstRun.value = await userStore.checkFirstRun()
}

const refreshRuntimeStatus = async () => {
  await Promise.allSettled([checkHealth(), infoStore.loadInfoConfig(true), checkFirstRunStatus()])
}

const loadData = () => {
  isLoading.value = false
  backendStatus.value = {
    state: 'checking',
    message: '正在检查后端服务状态'
  }
  refreshRuntimeStatus()
}

const retryLoad = () => {
  loadData()
}

const openWorldline = () => {
  router.push('/worldline')
}

const openThemes = () => {
  router.push('/themes')
}

const requestAdminAccess = async (redirectPath = '', label = '该能力') => {
  if (!userStore.isLoggedIn) {
    await focusLogin(redirectPath)
    return
  }
  message.info(`${label}需要管理员权限`)
}

const openKnowledge = () => {
  if (userStore.isAdmin) {
    router.push('/database')
    return
  }
  requestAdminAccess('/database', '知识库')
}

const openGraph = () => {
  if (userStore.isAdmin) {
    router.push('/graph')
    return
  }
  requestAdminAccess('/graph', '知识图谱')
}

const openExtensions = () => {
  if (userStore.isSuperAdmin) {
    router.push('/extensions')
    return
  }
  message.info('扩展管理需要最高权限账号')
}

const openAgent = () => {
  if (userStore.isLoggedIn) {
    router.push('/agent')
    return
  }
  focusLogin('/agent')
}

const openAddModule = () => {
  const moduleCreatePath = '/themes?new_module=1'
  if (userStore.isAdmin) {
    router.push(moduleCreatePath)
    return
  }
  if (!userStore.isLoggedIn) {
    focusLogin(moduleCreatePath)
    return
  }
  message.info('创建自定义模块需要管理员权限')
}

const focusLogin = async (redirectPath = '') => {
  const normalizedRedirect = normalizeAuthRedirect(redirectPath)
  if (normalizedRedirect) {
    setStoredRedirect(normalizedRedirect)
  }
  shouldHighlightLogin.value = true
  await router.replace({
    name: 'Home',
    query: {
      ...route.query,
      login: '1',
      ...(normalizedRedirect ? { redirect: normalizedRedirect } : {})
    }
  })
  await nextTick()
  loginPanelRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  window.setTimeout(() => {
    shouldHighlightLogin.value = false
  }, 1400)
}

const getRedirectAfterAuth = () => {
  return normalizeAuthRedirect(route.query.redirect) || consumeStoredRedirect()
}

const handleLogin = async () => {
  authError.value = ''
  if (!loginForm.value.loginId || !loginForm.value.password) {
    authError.value = '请输入用户 ID 和密码。'
    return
  }

  authLoading.value = true
  try {
    await userStore.login({
      loginId: loginForm.value.loginId,
      password: loginForm.value.password
    })
    message.success('登录成功')
    const redirectPath = getRedirectAfterAuth()
    await router.push(redirectPath || '/worldline')
  } catch (error) {
    authError.value = error?.message || '登录失败，请检查账号或密码。'
  } finally {
    authLoading.value = false
  }
}

const handleInitialize = async () => {
  authError.value = ''
  if (!adminForm.value.userId || !adminForm.value.password) {
    authError.value = '请输入初始化用户 ID 和密码。'
    return
  }

  authLoading.value = true
  try {
    await userStore.initialize({
      user_id: adminForm.value.userId,
      password: adminForm.value.password,
      phone_number: null
    })
    message.success('最高权限账号已初始化')
    const redirectPath = getRedirectAfterAuth()
    await router.push(redirectPath || '/worldline')
  } catch (error) {
    authError.value = error?.message || '初始化失败。'
  } finally {
    authLoading.value = false
  }
}

const logout = () => {
  userStore.logout()
  message.success('已退出登录')
  checkFirstRunStatus()
}

onMounted(async () => {
  loadData()
  if (route.query.login === '1') {
    await nextTick()
    focusLogin(normalizeAuthRedirect(route.query.redirect) || '')
  }
})

watch(
  () => route.query.login,
  (value) => {
    if (value === '1' && !userStore.isLoggedIn) {
      focusLogin(normalizeAuthRedirect(route.query.redirect) || '')
    }
  }
)

const featureCards = computed(() => {
  const list = Array.isArray(infoStore.features) ? infoStore.features : []
  return list
    .map((item) => {
      if (typeof item === 'string') {
        return {
          label: item,
          value: '',
          description: '',
          icon: featureIconMap.default
        }
      }

      const key = iconKey(item.icon || item.type)
      return {
        label: item.label || item.name || '',
        value: item.value || '',
        description: item.description || '',
        icon: featureIconMap[key] || featureIconMap.default
      }
    })
    .filter((item) => item.label || item.value || item.description)
})

const githubUrl = computed(() => infoStore.projectRepoUrl || '')
const docsUrl = computed(() => infoStore.docsUrl || '')
const brandingDescription = computed(() => infoStore.branding?.description || '')
const moduleCountText = computed(() => {
  const count = Array.isArray(infoStore.themes) ? infoStore.themes.length : 0
  return count ? `${count} 个模块` : '等待自定义接入'
})
</script>

<style lang="less" scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--wl-text);
  background: var(--wl-page-bg);
}

.loading-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: var(--wl-muted);
}

.topbar {
  position: relative;
  z-index: 20;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 14px 28px;
  border-bottom: 1px solid var(--wl-border);
  background: rgba(2, 5, 10, 0.78);
  backdrop-filter: blur(18px);
}

.brand-link,
.nav-pill,
.icon-button,
.session-button {
  color: inherit;
  text-decoration: none;
}

.brand-link,
.nav-pill,
.header-actions,
.session-button,
.hero-actions,
.ready-grid button {
  display: inline-flex;
  align-items: center;
}

.brand-link {
  gap: 10px;
  min-width: 0;
  font-weight: 900;
}

.brand-logo,
.brand-mark {
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
}

.brand-logo {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  object-fit: cover;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--wl-radius-sm);
  border: 1px solid var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: var(--wl-gold-soft);
  font-weight: 900;
}

.brand-name {
  color: var(--wl-text);
  white-space: nowrap;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.nav-pill,
.icon-button,
.session-button,
.primary-button,
.secondary-button,
.ready-grid button {
  min-height: 38px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-weight: 800;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease;
}

.nav-pill {
  gap: 7px;
  padding: 0 12px;
}

.nav-pill.locked {
  border-color: rgba(var(--wl-cyan-rgb), 0.08);
  color: rgba(148, 172, 184, 0.72);
}

.nav-pill.locked:hover {
  border-color: rgba(var(--wl-gold-rgb), 0.35);
  background: rgba(var(--wl-gold-rgb), 0.06);
  color: var(--wl-gold-soft);
}

.mini-lock {
  color: var(--wl-gold-soft);
}

.icon-button {
  width: 38px;
  justify-content: center;
}

.session-button {
  gap: 7px;
  max-width: 190px;
  padding: 0 11px;
}

.session-button span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-pill:hover,
.icon-button:hover,
.session-button:hover,
.secondary-button:hover,
.ready-grid button:hover {
  border-color: var(--wl-border-strong);
  background: rgba(var(--wl-cyan-rgb), 0.1);
  color: var(--wl-text);
}

.header-actions {
  gap: 8px;
  justify-content: flex-end;
  min-width: 0;
}

.home-main {
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 52px;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  padding: 12px 14px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.28);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold-soft);
}

.status-banner button {
  margin-left: auto;
  border: 1px solid var(--wl-border-gold);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: var(--wl-gold-soft);
  min-height: 30px;
  padding: 0 10px;
  cursor: pointer;
  font-weight: 800;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
  gap: 18px;
  align-items: stretch;
}

.hero-copy,
.access-panel {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
}

.hero-copy {
  min-height: 620px;
  display: flex;
  flex-direction: column;
  padding: 30px;
  overflow: hidden;
}

.hero-copy::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(rgba(var(--wl-cyan-rgb), 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(var(--wl-cyan-rgb), 0.035) 1px, transparent 1px);
  background-size: 46px 46px;
  opacity: 0.58;
  z-index: 0;
}

.hero-copy::after {
  content: '';
  position: absolute;
  left: 28px;
  right: 28px;
  top: 280px;
  height: 180px;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.78), rgba(var(--wl-gold-rgb), 0.92)),
    linear-gradient(90deg, transparent, rgba(var(--wl-cyan-rgb), 0.2), transparent);
  clip-path: polygon(0 49%, 18% 44%, 34% 18%, 50% 52%, 66% 36%, 82% 46%, 100% 49%, 100% 53%, 82% 55%, 66% 62%, 50% 57%, 34% 78%, 18% 56%, 0 53%);
  filter: drop-shadow(0 0 18px rgba(var(--wl-gold-rgb), 0.35)) drop-shadow(0 0 22px rgba(var(--wl-cyan-rgb), 0.25));
  opacity: 0.48;
  z-index: 0;
}

.hero-copy > * {
  z-index: 1;
}

.eyebrow {
  margin: 0 0 9px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

.hero-copy h1 {
  max-width: 780px;
  margin: 0;
  color: var(--wl-text);
  font-size: 64px;
  font-weight: 950;
  line-height: 1.02;
  letter-spacing: 0;
}

.subtitle {
  max-width: 780px;
  margin: 16px 0 0;
  color: var(--wl-text-soft);
  font-size: 20px;
  font-weight: 800;
  line-height: 1.45;
}

.description {
  max-width: 760px;
  margin: 12px 0 0;
  color: var(--wl-muted);
  line-height: 1.7;
}

.hero-actions {
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 26px;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 15px;
  text-decoration: none;
}

.primary-button {
  border-color: var(--wl-border-gold);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.72));
  color: var(--wl-ink);
}

.primary-button:hover {
  transform: translateY(-1px);
}

.primary-button:disabled,
.secondary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.signal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: auto;
  padding-top: 250px;
}

.signal-item {
  min-height: 148px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
}

.signal-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--wl-radius-sm);
  border: 1px solid var(--wl-border);
  color: var(--wl-cyan);
  background: rgba(var(--wl-cyan-rgb), 0.07);
}

.signal-item h2,
.signal-item p {
  margin: 0;
}

.signal-value {
  color: var(--wl-gold-soft);
  font-size: 12px;
  font-weight: 900;
}

.signal-item h2 {
  margin-top: 3px;
  color: var(--wl-text);
  font-size: 16px;
  font-weight: 900;
}

.signal-item p:last-child {
  margin-top: 6px;
  color: var(--wl-muted);
  line-height: 1.55;
}

.access-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 620px;
  padding: 24px;
}

.access-panel.highlighted {
  border-color: var(--wl-border-gold);
  box-shadow: var(--wl-shadow), 0 0 0 3px rgba(var(--wl-gold-rgb), 0.12);
}

.panel-header h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 25px;
  font-weight: 950;
}

.panel-header p {
  margin: 9px 0 0;
  color: var(--wl-muted);
  line-height: 1.65;
}

.login-form {
  display: grid;
  gap: 14px;
}

.login-form label {
  display: grid;
  gap: 7px;
  color: var(--wl-gold-soft);
  font-size: 13px;
  font-weight: 900;
}

.login-form input {
  width: 100%;
  height: 42px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(2, 5, 10, 0.76);
  color: var(--wl-text);
  padding: 0 12px;
  outline: none;
}

.login-form input:focus {
  border-color: var(--wl-border-gold);
  box-shadow: var(--wl-focus-ring);
}

.login-form input::placeholder {
  color: var(--wl-muted-soft);
}

.full-width {
  width: 100%;
}

.auth-error {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid rgba(255, 123, 123, 0.32);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 123, 123, 0.08);
  color: var(--wl-red);
}

.access-ready {
  display: grid;
  gap: 14px;
}

.ready-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.ready-grid button {
  justify-content: flex-start;
  gap: 8px;
  min-height: 54px;
  padding: 0 13px;
}

.module-section {
  margin-top: 18px;
  padding: 20px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.section-header h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 24px;
  font-weight: 950;
}

.module-count {
  border: 1px solid rgba(var(--wl-gold-rgb), 0.25);
  border-radius: 999px;
  padding: 7px 11px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold-soft);
  font-size: 13px;
  font-weight: 900;
}

.add-module-card {
  width: 100%;
  min-height: 162px;
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  grid-template-areas:
    'icon title'
    'icon copy';
  align-items: center;
  column-gap: 18px;
  padding: 20px;
  border: 1px dashed var(--wl-border-strong);
  border-radius: var(--wl-radius);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.06), transparent 28%),
    rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text);
  cursor: pointer;
  text-align: left;
}

.add-module-card:hover {
  border-color: var(--wl-border-gold);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.09), transparent 30%),
    rgba(var(--wl-cyan-rgb), 0.065);
}

.add-icon {
  grid-area: icon;
  width: 64px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--wl-border-gold);
  border-radius: var(--wl-radius);
  color: var(--wl-gold-soft);
  background: rgba(var(--wl-gold-rgb), 0.1);
}

.add-title {
  grid-area: title;
  color: var(--wl-text);
  font-size: 20px;
  font-weight: 950;
}

.add-copy {
  grid-area: copy;
  margin-top: 7px;
  color: var(--wl-muted);
  line-height: 1.65;
}

.footer {
  margin-top: auto;
  border-top: 1px solid var(--wl-border);
  background: rgba(2, 5, 10, 0.82);
  color: var(--wl-muted-soft);
}

.footer span {
  display: block;
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
  padding: 18px 0;
}

@media (max-width: 1060px) {
  .topbar {
    grid-template-columns: 1fr auto;
  }

  .nav-links {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .hero-section {
    grid-template-columns: 1fr;
  }

  .access-panel,
  .hero-copy {
    min-height: auto;
  }

  .signal-grid {
    padding-top: 230px;
  }
}

@media (max-width: 760px) {
  .topbar {
    padding: 12px 14px;
  }

  .home-main {
    width: min(100% - 24px, 1280px);
    padding-top: 18px;
  }

  .hero-copy,
  .access-panel,
  .module-section {
    padding: 18px;
  }

  .hero-copy h1 {
    font-size: 40px;
  }

  .subtitle {
    font-size: 17px;
  }

  .hero-copy::after {
    left: 16px;
    right: 16px;
    top: 410px;
    height: 120px;
  }

  .hero-actions,
  .status-banner {
    align-items: stretch;
    flex-direction: column;
  }

  .primary-button,
  .secondary-button {
    width: 100%;
  }

  .status-banner button {
    margin-left: 0;
  }

  .signal-grid {
    grid-template-columns: 1fr;
    padding-top: 190px;
  }

  .section-header,
  .add-module-card {
    align-items: flex-start;
  }

  .section-header {
    flex-direction: column;
  }

  .add-module-card {
    grid-template-columns: 1fr;
    grid-template-areas:
      'icon'
      'title'
      'copy';
  }
}
</style>
